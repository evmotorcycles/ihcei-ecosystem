# SMI — the Synaptic Mesh Interface

**Nothing on the screen is positioned.** Every element is a node in a graph of
what depends on what. The distance between two of them is the effective
resistance between them on that graph, and the picture is whatever flat layout
best preserves those distances. Move a dependency and the layout rearranges
because the arithmetic changed — not because an animation was written.

```
python3 smi/run_smi.py     # the three phases, with terminal tables
python3 smi/render.py      # writes smi/smi.html and smi/frames/*.svg
python3 -m pytest -q smi/test_smi.py
```

Pure JAX + NumPy, on-device, offline, deterministic. No model, no weights, no
network. The whole layout for a hundred elements is one pseudo-inverse.

```
L⁺ = pinv(L)
R_ij = L⁺_ii + L⁺_jj − 2·L⁺_ij
d_ij = √R_ij
```

---

## What is being measured

**A dependency graph inside running software.** `J` is how strongly one element's
value determines another's; `d` is how far apart two elements should sit given
all of those dependencies. This is telemetry on an **information layer** — see
[`SCOPE.md`](SCOPE.md). Nothing here is a claim about matter or physical
distance, and the name is a name.

The claim, stated once, in the form it should be made:

> **A layout derived from a dependency graph cannot drift out of step with the
> dependencies.** Change what depends on what, and the picture changes, because
> the picture *is* the dependency structure rather than a drawing of it.

---

## Global tension is a zoom, by construction

For a scalar J > 0, `pinv(J·L₀) = J⁻¹·pinv(L₀)`. Therefore `R(J) = R(1)/J`, so
`d = √R ∝ J^(−1/2)` **exactly** — for every pair, on every graph, at every size.

| graph | slope | R² |
|---|---|---|
| ring N=100 *(as specified)* | −0.500000 | 1.000000 |
| ring N=7 (odd) | −0.500000 | 1.000000 |
| path N=40 | −0.500000 | 1.000000 |
| star N=50 | −0.500000 | 1.000000 |
| random p=0.05, N=80 | −0.500000 | 1.000000 |
| random p=0.50, N=30 | −0.500000 | 1.000000 |

**For an interface that is a guarantee worth having on purpose.** A global
tension control rescales the whole picture and changes nothing else: it cannot
reorder elements, cannot change what sits near what, and cannot alter a single
value. It is safe to hand to a user.

The same fact has a second edge. Because the slope comes out on *every* graph,
measuring it tells you nothing about *this* graph. So it is reported as
`INVARIANT (BY CONSTRUCTION)`, never as a pass, and kept for the other thing it
is genuinely good at: it breaks the moment `pinv`, the Laplacian construction or
the clipping breaks. A measurement that cannot come out otherwise is not a
verification — but it can still be a good smoke test, and a good design
guarantee, and this one is both.

**What carries information here is topology and *local* coupling** — which is
what H4 below measures, and H4 can fail.

Precision matters here. At float32 the N=100 ring reads **−0.500003**, and
reporting that as "exactly −0.5" would be reading noise as signal. The engine
turns on float64 at import.

---

## Two things the specification gets wrong

Both were predicted in `PREREG.md` before the harness ran, and both are
confirmed. Both would have shipped as visual bugs.

### 1. Broken links do not give infinite distance

> *"Low coupling or broken links yield infinite distance."*

They do not. Cut a ring into two arcs and the pseudo-inverse still returns a
finite number between the halves:

| pair | distance | |
|---|---|---|
| nodes 0 and 2 — **no path at all** | `1.118034` | finite, and meaningless |
| nodes 0 and 5 — same half | `1.732051` | finite, and correct |

The unrelated pair comes back *closer than the related one*. Unguarded, the
layout puts two elements with nothing to do with each other side by side, and
the wire between them draws taut. `mesh_metric()` detects components explicitly
and returns `inf` itself.

### 2. Zero coupling gives zero distance, not infinity

| uniform J | d(0,4) |
|---|---|
| 1e-2 | 1.41e+01 |
| 1e-4 | 1.41e+02 |
| 1e-8 | 1.41e+04 |
| **0** | **0.000000** |

At J = 0 the Laplacian is zero, its pseudo-inverse is zero, and every distance
collapses. **A completely dead mesh measures as perfectly contracted** —
pixel-identical to a perfectly coupled one. The limit is discontinuous, and the
engine special-cases it rather than trusting the metric.

---

## What actually varies, and can therefore fail

| prediction | result | why it matters |
|---|---|---|
| **H1** uniform J changes scale, never shape (`< 1e-4`) | **HOLDS** — 1.3e-14 | a screen can zoom without a single element changing neighbours |
| **H4** a local pull stays local (`≥ 90%` monotone) | **HOLDS** — 100% | dragging rearranges; global J only zooms. Without this, a gesture would be indistinguishable from a zoom |

H4 is the one that makes the interface interactive at all. Raising J on **one**
wire is not a global rescale, so the layout genuinely rearranges:

| hops from the pulled wire | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| mean shift | 0.286 | 0.152 | 0.111 | 0.089 | 0.075 | 0.065 |

---

## Three visual states, never two

| state | when | how it draws |
|---|---|---|
| `LIVE` | connected and resolved | full contrast, solid; **taut = thinner**, a hairline reads as tight |
| `HELD` | connected, no value yet | amber, still real — not pretending to a number |
| `ROTTED` | no path back to the anchor | `#475569` grey, dashed, parked |

`ROTTED` is not "very slack". An element cut off from its source has no distance
at all, and drawing it as merely distant puts something unrelated in the picture
looking slightly less important.

### Three rendering bugs found by looking at the output

- **A wire between two rotted elements drew LIVE.** Two cut-off nodes are still
  perfectly coupled *to each other*, so their own distance is small and the wire
  styled itself taut — inside a region of the screen that was entirely dead. A
  wire is live only if what it joins is still attached to the picture.
- **Two elements landed on exactly the same pixel.** VAT and Total are the same
  distance from everything by symmetry, so a flat projection stacks them. Nodes
  are boxes, not points: separation now clears the box, and collisions are
  reported in the frame.
- **Stranded nodes hung half off the edge**, and nodes drifted under the title
  band. Both were the same mistake — laying out points and then drawing boxes.

---

## Scope

The engine computes effective resistance on a dependency graph. **"Latency-Metric
Duality" is a name for that construction**, and the domain is software: which
live elements determine which others, and how strongly. `SCOPE.md` records the
one framing correction made after the first write-up, which changed no
prediction, no gate and no number — the pre-registration remains hash-locked and
unedited.

Files: `lmd.py` (metric + guards) · `mesh.py` (nodes, wires, MDS layout) ·
`compositor.py` (states, styles, the pull gesture) · `run_smi.py` (three phases)
· `render.py` (SVG) · `PREREG.md` + `prereg.lock.json` · `results_smi.json`.
