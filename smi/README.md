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

## Four visual states, never two

| state | when | how it draws |
|---|---|---|
| `LIVE` | connected and resolved | full contrast, solid; **taut = thinner**, a hairline reads as tight |
| `HELD` | connected, no value yet | amber, still real — not pretending to a number |
| `FADING` | connected, coupling below `FADE_BELOW = 0.01` | grey, `1 4` dash, no label; the readout prints `<0.01`, never `0.00` |
| `ROTTED` | no path back to the anchor | `#475569` grey, `4 5` dash, parked |

`ROTTED` is not "very slack". An element cut off from its source has no distance
at all, and drawing it as merely distant puts something unrelated in the picture
looking slightly less important.

`FADING` exists because the readout used to print `0.00` for a wire the legend
still called live — a fourth state the interface had without naming, the picture
saying *connected* while the arithmetic said *I move nothing*.

The moment a value loses its source gets a sentence, not a colour change:
`VAT 20% has no path back — now rotted.`

---

## The picture cannot show everything, and now it says so

This is the most important thing in SMI and it was wrong in this README until it
was measured.

Five elements generally need **four** dimensions to hold their distances. A
screen has two. Classical MDS keeps the best plane and drops the rest **in
silence**. On the invoice mesh SMI ships with:

| pair | drawn at | true distance | mesh diameter |
|---|---|---|---|
| `VAT 20%` / `Total` | `4.3e-16` of it | `0.5000` | `0.7071` |

VAT and Total hang off Net with identical couplings, so they are
interchangeable, and the axis that separates them is not in the top two. They
are drawn **on top of each other** while being 71% of the mesh's diameter apart.

An earlier version of this file listed that as a *rendering bug*, "fixed" by
pushing the two boxes apart until they cleared. **That fix was the bug.** The
gap you then see between them is manufactured by the overlap pass; it is the one
distance on screen that means nothing at all, and an interface whose entire
claim is *position means something* had been quietly inventing one.

So it is measured (`lmd.flatness`), named (`FLAT_WARN = 0.25`), and shown three
ways: a `flattest pair drawn` cell in the readout, a sentence naming the pair and
its real distance, and a dashed **`gap lost`** tie drawn between the two boxes.

`smi/test_smi.py::test_the_shipped_mesh_draws_two_elements_on_top_of_each_other`
exists so that the day someone separates them quietly, it fails.

---

## The second view: what to do when the picture cannot show it

Telling someone "these two are secretly 0.50 apart" and leaving them looking at
one box on top of another is a confession, not a fix. So there is a second
plane, one tap away.

Classical MDS spends its two dimensions minimising **strain** — error on the
double-centred Gram matrix. That is a *total*, and a total can be excellent
while one pair is destroyed. `lmd.best_axes` searches other eigenvector pairs
for the plane that maximises the **worst** pair instead:

| plane | worst pair | median pair | mean abs. distance error | strain |
|---|---|---|---|---|
| `(0, 1)` classical, the default | **0.0%** | 91.1% | 0.1235 | **0.1291** |
| `(0, 2)` the second view | **70.7%** | 70.7% | **0.1217** | 0.1953 |

The classical plane draws most pairs almost perfectly and one pair as a total
lie. The second view draws everything at about 71% and lies about nothing — and
it has the *lower mean distance error* of the two, because strain is measured on
the Gram matrix rather than on distances.

The button only appears when the alternative is at least 5 points better, says
by how much (`Show the lost gap (71%)`), and the header changes to *second view
— the gap the usual one loses* so nobody is unsure which picture they are
holding. Neither view invents anything; they answer different questions.

The default is still the classical plane, because that is what is
pre-registered and what "the MDS layout" means. That it is worse here on two of
four measures is a finding, not a licence to switch it quietly.

### Declared limit: on a symmetric mesh the second view is basis-dependent

`best_axes` searches pairs of eigenvector **indices**, so it searches inside
whichever basis the eigensolver returned. Where the spectrum is degenerate the
two engines hold different bases for the same subspace, range over different
sets of planes, and do not merely tie — on `star N=15` they found planes scoring
`0.0365` and `0.0274`. The alternative view is therefore well defined only where
the spectrum is: elsewhere it is *a* better plane, verified by the engine
drawing it, and not reproducible from the other. Recorded, not tuned away.

---

## A declared-unreliable quantity must not govern a reliable one

Found in a phone screenshot, not in the tests. A `FADING` element — coupled
below `FADE_BELOW`, labelled *moves nothing you can see* — is very weakly
coupled, so the metric puts it very far away, so it stretched the bounding box,
so everything else was drawn smaller:

| `net→vat` coupling | the four live boxes | share of canvas |
|---|---|---|
| `8.000` | 240 × 132 | 16.9% |
| `0.020` | 161 × 45 | 3.9% |
| `0.005` *(fading)* | 182 × 29 | 2.9% |
| `0.001` *(fading)* | 182 × 6 | **0.6%** |

At `J = 0.001` the four elements a person is actually auditing were a row of
slivers, because one the interface had already declared unreliable was setting
the zoom. The scale is now taken from the **solid sub-mesh**; faint elements
keep their true direction and are parked in the margin. `0.6% → 5.0%`.

---

## Making the layout hold still

The reviewer's complaint was that the map flips and jumps under a finger. Four
separate causes, each measured before and after rather than argued about:

| cause | before | after |
|---|---|---|
| MDS is fixed only up to rotation/reflection | worst drag move `0.7113` | `0.3268` (Procrustes onto the previous frame) |
| overlap resolved by shoving a node down a fixed step | **167 px** teleport on a 360×520 frame | separation by penetration depth, continuous |
| boxes too big to fit, so the relaxation fought every frame | steady 1.0 px before separation, **24 px** after | boxes given the room the metric asks for; pass goes quiet |
| stranded elements in a right-hand column | mesh drawn in ~⅓ of the canvas | bottom strip; `240×355` of `360×520` |

What is left is **one** frame of ~40 px at `J ≈ 3.97`, and it does not shrink
when the drag is sampled 32× finer — because it is not a rendering artefact.
That is where two nodes pass **through** each other in the projection: at the
crossing there is no direction to separate them along, so which side they come
out on flips. The interface announces the collapse rather than hiding the jump.

A centroid-and-max-radius fit was also tried, on the reasonable theory that a
bounding box is not rotation-invariant. It measured no better — `39.4 px`
against `39.8 px` — and wasted most of the canvas. Recorded because it is the
kind of plausible fix that gets adopted on reasoning alone.

### On a symmetric mesh the picture is not unique

`smi/test_parity.py` first asserted the two engines draw the same picture. On
`star N=15` that failed (gram distance `8.7e-01`), then a stress-matching version
failed too (`177.00` against `182.12`). Both engines are correct: fourteen
interchangeable leaves make thirteen eigenvalues exactly `1.0`, so any two of
those eigenvectors are a valid answer, and numpy and the browser's Jacobi sweep
pick different ones.

The second failure is the one worth keeping in view: **those equally-valid
pictures do not represent the distances equally well.** What classical MDS
equalises is *strain* — error on the double-centred Gram matrix — not *stress*.
That is what the parity test asserts now, plus identical pictures wherever the
eigenvalue gap makes the picture well posed.

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
