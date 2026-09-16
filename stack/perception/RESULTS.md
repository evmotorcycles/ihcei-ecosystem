# Results — Patch 1: registry lock and the perception module

Run 2026-09-16. Offline, deterministic, no network, no keys.
Predictions locked in `prereg_perception.md`, sha256
`4cee849de5c8fe786c7bb1e22967a429d65cf077339dd318c5cd597d4ea7c4f5`.
Cohort hash written into the ledger: `0205626672…` (n = 22, fetched 2026-07-17).

**P1–P6 green. But three of the supplied tests were green for reasons that do
not hold, and my own repair set the same sampling trap I fell into two commits
ago.**

---

## Three defects in the supplied P1–P3

Measured in a diagnostic pass **before** the pre-registration was written, so
they are reported as findings about the supplied code, not as predictions.

### D1 — P2's stated claim never happens

`A = np.ones((n,n))/n`, symmetrized, is `K_n` at uniform weight `2/n`. For a
complete graph at weight `w`, `R_eff = 2/(n·w)`, and with `w = 2/n` the `n`
cancels:

| n | 16 | 32 | 64 |
|---|---|---|---|
| `R_eff(premise, middle)` | **1.000000000000** | **1.000000000000** | **1.000000000000** |

Spread `3.3e-16`. The assertion is written with `>=`, so it passes; the
docstring's *"R_eff grows with context length"* does not occur. **Diluting the
row mass by `1/n` exactly compensates for adding the nodes.**

### D2 — P1's rank half cannot fail

The ratio API divides the scale out, so the two ratio matrices are bit-identical:
measured `max|r1 − r2| = 0.0`. Comparing their rank orders is a tautology. Kept
as `test_the_supplied_rank_comparison_could_not_fail`, with a **control** added
— a genuine chord, not a rescale — whose ranks do move.

P1's first half is sound but is an **identity, not a result**: `pinv(cL) =
pinv(L)/c`. `smi/PREREG.md` locked that as "IDENTITY, NOT A RESULT" before this
module existed.

### D3 — `DisconnectedSpaceError` was inert

It fired only on a non-positive reference distance. On two disjoint 4-rings bare
`pinv` returns `d(0,4) = 0.790569` — finite, positive, meaningless — so the
guard never fired. Fixed with a components walk before any reading, the way
`smi/lmd.py:mesh_metric` already does it. **P4 hits**: the pair now refuses, and
the module returns `inf` where there is no route.

---

## The repaired lost-in-the-middle test, and what it cost

Local-window attention (half-width 2), mass **not** renormalised by `n`, plus a
background floor `1e-4`:

| n | 16 | 32 | 64 | 128 |
|---|---|---|---|---|
| `R_eff` | 0.929948 | 1.677563 | 2.695681 | 2.894013 |
| step | — | ×1.804 | ×1.607 | ×1.074 |

**P2R-a and P2R-b both hit** — strictly increasing, and 16 → 128 grows
**3.112×** against a registered threshold of 3.0.

### And then it reverses

| n | 128 | 256 | 384 |
|---|---|---|---|
| `R_eff` | 2.894 | **2.171** | **1.784** |
| step | ×1.07 | **×0.75** | **×0.82** |

One doubling past the registered range the trend turns over. The background
floor is a parallel conductance whose **total** grows with `n`, so it eventually
beats the lengthening window path: the far token gets **closer**, not further.
Lost-in-the-middle reverses into found-by-the-crowd.

Remove the floor and the growth is clean — ×1.86, ×1.92, ×1.96 per doubling,
the path-graph behaviour — so the floor is doing all of the reversing and it is
a free parameter I chose.

**The registered predictions hit on the range I registered, and the claim they
were testing does not survive one extra sample.** That is the same trap as
`geometric-gate/`'s coarse leak sweep two commits ago, set again by me, and
caught only because I looked past my own range. Recorded as
`test_the_growth_reverses_one_sample_past_the_registered_range`.

## P6 — the decoy is the padding attack, in the perception layer

One injected edge of conductance 10, at n = 64:

| | `R_eff(premise, middle)` |
|---|---|
| plain | 2.695681 |
| with one decoy edge | **0.096424** |
| ratio | **0.0358** |

**P6-a and P6-b hit.** A single declared edge collapses the reading by 96%. This
is not a bug being tolerated — a declared edge is a declared edge, and the layer
reads the conductance it was given. It is `agi-stack/` again at a different
layer, and the remedy is to say so, not to claim the reading is robust.

---

## The ledger

`stack/governance/declarations.md` carries the **real** cohort hash
(`REPLACE_WITH…` is gone and `test_the_declarations_carry_the_real_cohort_hash`
recomputes it from the fixture), states Foster as a harness invariant that does
not gate health, and records both measured invariance groups for LINTEL
certificates (rewrites 27/27, omissions 18/27).

The CI grep for `un-gameable`, `thermodynamic` and a fused integrity score is in
place — and it **failed on first run against the ledger's own sentence** "not
thermodynamic entropy". The tenth time this session a check has matched the text
that forbids the thing it checks for — and the **eleventh** followed immediately,
when this very paragraph tripped it again. Four files are now exempt by explicit
allowlist, because saying those words is their job: the ledger, the grep, the
pre-registration and this write-up. The allowlist is asserted to be exactly four
long, so it cannot quietly grow.

## Blocked: the organization module

`stack/organization/adg_tqg.py` is **not built**, and not for engineering
reasons. The proposed signatures take religious-tradition vocabulary as public
parameter names. This repository's standing rule keeps that vocabulary in `ncu/`
and out of measurement code; a scoring function taking those arguments puts it
into every traceback, log line and API signature downstream.

The rebrand to Applied Governance / Cognitive Field Equivalence fixes the
acronyms, which was the smaller half. **The parameter names are the larger half
and need a decision before Patch 2.** The arithmetic is unaffected either way.

## What this cannot do

- **Nothing here is a language model, a real attention matrix, or JEPA.** The
  inputs are hand-built conductance graphs. "Lost in the middle" is the
  phenomenon the construction is *modelled on*, not something measured in a
  transformer.
- **The window construction and its floor are chosen.** A different shape gives
  a different exponent, and the reversal above shows how much the floor decides.
- **The ratio API removes scale blindness from the output, not the reading.**
  Two graphs differing by a global factor stay indistinguishable, by design.
- **`np.linalg.pinv` default `rcond`** flipped a published verdict on a dense
  graph at n = 100 in `lmd-scaling/`. The supplied P2 used a *complete* graph at
  n = 64, which is that regime; the repaired construction is sparse, which
  avoids the problem rather than solving it.
- **n = 1 construction family.**

## Reproduce

```
python3 -m pytest stack/perception -q
```
