# Results — what the −0.5 coupling slope measures

Run 2026-09-15, offline, CPU, float64. No GPU, no network, no keys.
Predictions locked in `prereg_scaling.md`,
sha256 `c4714e7827ddb942749c90d323a00d729fd3bb4a6d9596ab50a1f435745029be`.

**Six predictions hit. Three missed.** The misses are in the suite by name.

## Read this first: most of this was already known here

`smi/PREREG.md` already states the −0.5 slope is **"IDENTITY, NOT A RESULT"** and
that it **"cannot fail"**. `smi/test_smi.py` already asserts it on a ring, path,
star and complete graph (`test_the_same_slope_appears_on_every_topology`,
docstring: *"This is the test that stops the sweep being read as a
discovery"*), already proves `pinv(J·L) == J⁻¹·pinv(L)` directly, already shows
raw `pinv` returning a finite distance across a broken mesh while the guarded
metric returns `inf`, and already pins float64 with the note *"At float32 the
N=100 ring reads −0.500003."*

**Arms 1, 3 and 4 below are therefore re-derivations, not findings.** They agree
with the existing work — independently, on different graphs, at n=100 rather
than n≤30 — and that agreement is worth having. It is not new.

**Two things here are new:**

1. **Arm 2** — fitting the exponent when the coupling is *not* global. `smi`
   shows a local pull changes the shape; it does not fit a slope. This does:
   **−0.0047**, R² **0.63**.
2. **Arm 6(d)** — the verdict flips on three implementation choices that are not
   physics: dtype, `pinv` library, and **how the Laplacian was assembled**. The
   last two only surface above roughly n=40, and `smi`'s complete graph is n=12.

---

## The headline

A GPU notebook sweeps a coupling `J` through a weighted ring Laplacian and
reports slope **−0.500000**, R² **1.000000**, verdict **PASS — space is emergent**.

Every number it printed is reproducible. The reading of them is not.

The sweep sets `L = J · L₀` — one scalar on **every** edge. The pseudo-inverse is
homogeneous of degree −1, so `R → R/J` and `d → d·J^(−1/2)` **by definition of
`pinv`**, before any graph is drawn. Measured here on four more graphs:

| graph | edges | slope | \|slope + 0.5\| |
|---|---|---|---|
| ring | 100 | −0.500000000 | 8.2e-15 |
| star | 99 | −0.500000000 | 0 |
| path | 99 | −0.500000000 | 5.5e-15 |
| Erdős–Rényi p=0.1 | 520 | −0.500000000 | 1.1e-16 |
| complete | 4950 | −0.499527072 | 4.7e-04 ← the miss |

A star has no ring, no lattice and no symmetry. It returns the same −0.5. **The
sweep does not discriminate topology**, so it is not evidence about lattices,
rings or space — in either direction.

The notebook's own plot labels the −0.5 line **"Theoretical LMD Null"**. Its
measured curve lands on that line, and it calls that PASS. Landing on a declared
null is normally the **inconclusive** outcome, not the win.

---

## The three that missed — S2, S3, S4

I predicted −0.5 for **all five** graphs. The complete graph broke all three
predictions at once, and the mechanism is not the mathematics.

`np.linalg.pinv` decides how many singular values count as zero by comparing
them to `rcond × largest`, with `rcond = 1e-15`. On K100 the true null
eigenvalue drifts across that line as the weights scale — **above it at 7 of the
15 couplings** — so the same graph is inverted at a different rank at different
`J`, and the null direction leaks into the answer. The error reaches **6.3e-3**,
four orders above float64 noise, with no indication that anything went wrong.

Fixing the rank to the known value `n − pieces` via `eigh` restores it:

| graph | slope, rank fixed |
|---|---|
| ring / star / path / complete / Erdős–Rényi | −0.500000000000 (worst err 3.1e-15) |

So the identity holds. **The prediction still missed**, because it said the sweep
would return −0.5 and the sweep did not. Those are different statements and this
project does not collapse them.

### The part worth keeping — three knobs that flip the verdict

On K100, at float64 throughout, with the notebook's own gate `atol=1e-4`:

| Laplacian assembled by | `pinv` from | slope | verdict |
|---|---|---|---|
| `L[i,i] += w` per edge | numpy | −0.499527072207 | **FAIL** |
| `L[i,i] += w` per edge | jax | −0.500000000000 | PASS |
| `diag(W.sum(1)) − W` | numpy | −0.500000000000 | PASS |
| `diag(W.sum(1)) − W` | jax | −0.500000000000 | PASS |

Same graph, same dtype, same gate. Accumulating the degree edge by edge sums 99
terms in sequence and rounds differently from summing the weight matrix once;
that alone lifts the null eigenvalue over numpy's `rcond` line. **Neither
assembly is wrong.** The analytic answer is −0.5 in all four rows.

So the published verdict is decidable by three choices that are not physics:
**dtype**, **which library's `pinv`**, and **how the matrix was built**. `smi`
already fixed the first by setting `jax_enable_x64`; it happens to avoid the
other two by using JAX and `diag(W.sum(1)) − W`, at n ≤ 30 where neither bites.

The exposure is in **re-implementations**. `smi/test_parity.py` checks the
browser engine against the JAX engine to <1e-9 over 14 graphs — a tolerance
these effects clear comfortably at small n. Whether they stay clear on a dense
graph at n=100 is **not tested**, and this run does not test it either.

---

## The version that can fail — S5, hit

Break the global scalar: ring at n=100, every edge weight 1 **except** edge (0,1),
swept over the same 15 couplings.

| | predicted | measured |
|---|---|---|
| S5 \|slope + 0.5\| | > 0.3 | **0.4953** |
| S5b \|slope\| | < 0.15 | **0.0047** |
| S5c R² | < 0.99 | **0.6286** |

A thousandfold change in one weight moves `d(0,50)` from 5.202 to 4.975 — under
5% — and the log–log relation is not a line at all. **The −0.5 is a property of
multiplying everything at once, not of the graph.**

---

## A number where there is no route — S6, S7, hit

Two disjoint rings of 50. Nodes 0 and 50 have **no path between them**, so the
effective resistance is undefined.

Bare `pinv` returns **2.886174** at J=1 — finite, unremarkable, sitting beside a
genuine within-component reading of 3.536. And it scales at **−0.500000000**,
exactly like a real distance. **Slope alone cannot tell a measured distance from
an unreachable one.**

This is already established here — `smi/test_smi.py` has
`test_raw_pinv_reports_a_finite_distance_across_a_broken_mesh` and
`test_the_guarded_metric_returns_infinity_where_there_is_no_path`. Reproduced at
n=100 rather than n=8.

This repository's own engine does not have that failure, and not by accident.
`smi/lmd.py` walks the adjacency separately and returns `inf` across components,
with the docstring naming the reason: *"pinv does not know or care that a graph
is in pieces. This does."* Measured: engine `inf`, bare sweep `2.886174`,
pieces seen `2`.

Any claim that a geometry was *reconstructed* has to say which pairs were
reachable. A bare sweep never asks.

---

## Precision — S8, S9, hit

The notebook printed `d(0,50) = 15.811394` at J=0.1. The exact value is
`5·√10 = 15.811388300842`.

| | value | rel. dev from exact |
|---|---|---|
| exact | 15.811388301 | — |
| notebook, published | 15.811394000 | **3.6e-07** |
| float64 here | 15.811388301 | 7.3e-14 |
| float32 here | 15.811586380 | 4.4e-05 |

The published figure is wrong in the 7th significant figure. JAX defaults to
float32 unless `jax_enable_x64` is set and the notebook does not set it. Its own
gate is `atol=1e-4`; **measured** float32 slope error is 3.4e-06, so the gate
absorbs the dtype error entirely and the run cannot notice its own precision.
No prediction was registered for that slope error — a least-squares fit can
average noise either way, and I did not know which.

`smi/lmd.py:60` sets `jax_enable_x64 = True`. This repository already made that
choice.

---

## The other half of the cancellation

The sweep measures the moving half of an identity this repository relies on.
Measured with `spar`, not hand-written:

| every weight × | weight | resistance | bearing (w·R) | total |
|---|---|---|---|---|
| 0.1 | 0.6 | 1.111111111 | 0.666666667 | 6.000000 |
| 1 | 6 | 0.111111111 | 0.666666667 | 6.000000 |
| 10 | 60 | 0.011111111 | 0.666666667 | 6.000000 |
| 1000 | 6000 | 0.000111111 | 0.666666667 | 6.000000 |

`spar.scaled()` carries the docstring *"Bearings must not move."* Resistance
falls by exactly the factor the weight rises by. The notebook sweeps `d = √R`
and finds it moves; the engine reports `w·R` and finds it does not. **Same
identity, opposite half.**

---

## What this run cannot do

- **It cannot say whether space is emergent.** An identity about `pinv` cannot
  confirm a physical thesis and cannot disprove one. If the sweep returns −0.5
  for a star, it is silent about physics. That is **inconclusive**, and recorded
  as such.
- **It cannot check the original.** I did not run it on a GPU and cannot verify
  its provenance. Float32 is inferred from published digits and that inference
  could be wrong for reasons a pasted transcript does not show.
- **It says nothing about heterogeneous graphs in general.** Arm 2 sweeps one
  chosen edge on one chosen topology.
- **The GPU is irrelevant to every result here.** These are 100×100
  pseudo-inverses. `jax.default_backend()` printing `gpu` is not evidence for
  anything the sweep concludes; it changes the runtime and the default dtype.
- **It is mostly not new.** Arms 1, 3 and 4 re-derive what `smi/` already
  established and pre-registered. Only Arm 2 and the three-knob flip are
  additional.
- **It does not test the browser engine.** The flip was measured between numpy
  and JAX in Python. Whether `smi/lmd.js` behaves the same on a dense graph at
  n=100 is untested, and naming the risk is not measuring it.
- **n = 1 notebook.** Nothing generalises.

## Reproduce

```
python3 lmd-scaling/run_scaling.py     # ~2.5s
python3 -m pytest lmd-scaling/test_scaling.py -q
```
