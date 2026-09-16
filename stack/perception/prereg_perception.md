# Pre-registration — perception-layer LMD, Patch 1

Written and hashed **before the repaired run**. 2026-09-16.

---

## Standing before this file: three defects in the supplied tests

These were **measured in a diagnostic pass before this file was written**, so
they are reported as findings about the supplied code, not as predictions. They
are recorded here because the patch's run order says "expect P1–P3 green", and
they are green for reasons that do not hold.

**D1 — P2's stated claim does not happen.** `build()` uses
`A = np.ones((n,n))/n`; symmetrized that is a complete graph with uniform weight
`2/n`, and for `K_n` at weight `w` the effective resistance is `2/(n·w)`. With
`w = 2/n` the `n` cancels and **`R_eff = 1.000000000000` for every pair at every
n** — measured at n = 16, 32, 64, spread `3.3e-16`. The assertion is written with
`>=`, so it passes; the docstring's "grows with context length" never occurs.
Diluting the mass by `1/n` exactly compensates for adding the nodes.

**D2 — P1's rank half cannot fail.** The ratio API divides the scale out by
construction, so `r1` and `r2` are bit-identical: measured `max|r1 − r2| = 0.0`.
Comparing their rank orders is a tautology. The *first* half of P1 (absolute
`d → d·c^(−1/2)`) is sound but is an **identity**, not a result:
`pinv(cL) = pinv(L)/c`, already locked in `smi/PREREG.md` as "IDENTITY, NOT A
RESULT".

**D3 — `DisconnectedSpaceError` is inert.** It fires only when the reference
distance is non-positive. On two disjoint 4-rings, bare `pinv` returns
`d(0,4) = 0.790569` across the components — finite, positive, and meaningless —
so the guard never fires. `smi/lmd.py:mesh_metric` already walks the adjacency
for exactly this reason: *"pinv does not know or care that a graph is in pieces.
This does."*

---

## The repaired predictions, locked before running

### P2R — lost-in-the-middle, operationalised so it can fail

`where`: the construction is mine. Attention is modelled as a **local window**
of fixed half-width `k = 2` — each token has conductance to its neighbours
within the window — plus a uniform background floor `b = 1e-4` so the graph
stays connected. Row mass is **not** renormalised by `n`, which is the step that
cancelled the effect in D1.

| # | Prediction | Value |
|---|---|---|
| P2R-a | `R_eff(premise, middle)` **strictly grows** with n over 16, 32, 64, 128 | strictly increasing |
| P2R-b | It grows **at least threefold** from n=16 to n=128 | ratio ≥ 3.0 |
| P2R-c | The supplied diluted-complete construction stays at **1.0** at every n | max spread < 1e-9 |

**P2R-b is the one I could be wrong about.** The background floor `b` provides a
route whose resistance falls as `n` grows (more parallel background edges), and
that works against the window path lengthening. Which term wins is not settled
by writing it down.

### P6 — the decoy, which is the padding attack in the perception layer

One injected high-conductance edge from premise to the middle token.

| # | Prediction | Value |
|---|---|---|
| P6-a | The decoy **reduces** `R_eff(premise, middle)` below the undecoyed value at the same n | falls |
| P6-b | It reduces it by more than half | ratio < 0.5 |

**This is not a bug to be fixed.** A declared edge is a declared edge; the
perception layer reads conductance it was given. It is the same result as
`agi-stack/`: adding edges clears the finding, and the remedy is to say so, not
to pretend the reading is robust.

### P4 — the disconnection guard, once it actually checks

| # | Prediction | Value |
|---|---|---|
| P4-a | With a components walk, a cross-component pair **refuses** instead of returning a number | raises |
| P4-b | Bare `pinv` on that same graph returns a finite positive number | finite |

### P1R / P3 — kept, with the vacuity removed

| # | Prediction | Value |
|---|---|---|
| P1R-a | `d → d·c^(−1/2)` under `C → cC` — **verification of an identity, not a result** | rel. err < 1e-9 |
| P1R-b | The ratio matrix is bit-identical under rescale, so the rank comparison is a tautology and is replaced by a **control**: a graph whose ranks genuinely differ | ranks differ |
| P3-a | An undeclared symmetrization raises | raises |
| P3-b | The pinned token runs and `d[ref] == 1.0` | 1.0 |

---

## Nulls, registered in advance

**NULL-P1.** Nothing here is a language model, an attention matrix from a real
model, or JEPA. The inputs are hand-built conductance graphs. No claim is made
about any model's behaviour, and "lost in the middle" is named as the phenomenon
the construction is *modelled on*, not as something measured in a transformer.

**NULL-P2.** The window construction is chosen. A different attention shape gives
a different exponent, and the background floor is a free parameter.

**NULL-P3.** `R_eff` is a reading of a drawn conductance graph. It does not know
what any token means.

**NULL-P4.** The ratio API removes the scale blindness from the *output*; it does
not remove it from the *reading*. Two graphs differing only by a global factor
are still indistinguishable, by design.

**NULL-P5 — the numerical one.** `np.linalg.pinv` uses a default `rcond` that
`lmd-scaling/RESULTS.md` measured flipping a published verdict on a dense graph
at n = 100. P2's supplied construction is a **complete** graph at n = 64, which
is that regime. The repaired construction is sparse, which avoids it rather than
solving it.

**NULL-P6.** n = 1 construction family, one seed-free deterministic build.

---

## What would falsify this

1. **P2R-a or P2R-b fails** — the background floor dominates, distance does not
   grow with context, and the construction does not model the phenomenon either.
2. **P6-a fails** — an injected edge does not shorten the reading, and the
   perception layer is not vulnerable the way the audit layer is.
3. **P4-a fails** — the components walk does not catch a disjoint graph.
