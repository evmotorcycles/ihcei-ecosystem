# Pre-registration — Patch 2, organization telemetry

Written and hashed **before the run**. 2026-09-17.

Cohort: `adg-tqg/fixtures/experiment_cohort.json`, n = 22, fetched 2026-07-17,
sha256 `020562667229a1c24e06b1a075786c2f86d700e5fbf1a4c0bb99a905b95f7a15`.
Labels: **16 survived, 6 failed**, by the fixture's own rule
`E = 0 iff archived or days_since_push > 365`.

---

## Three things found in the draft before anything ran

Measured in a diagnostic pass **before** this file was written, so recorded as
findings about the draft, not as predictions.

**R1 — the drafted score is not a rename.** `adg-tqg/experiment.py` computes
`C_dev = A_n · (a·t) / (eps + hbar)`, where `A_n` is the cosine of `(a, t, rsp)`
to the all-ones vector. The draft computes
`utility · (d_enc · d_dec) / (eps + noise)` = `a · (rsp·t) / (eps + hbar)`.
Those are different functions: **max absolute difference 5.21**, Spearman 0.936,
**rank orders differ**. A "bit-identical regression against the pre-rename
arithmetic" would have failed. The alignment factor `A_n` is dropped and
`utility` put in its place.

**R2 — `kappa` differs.** The original takes `sorted(A_n)[n//2]` = **0.861235**;
`np.median` on n = 22 averages the two middle values and gives **0.844392**.
Records between those two numbers render on opposite sides of the cutoff.

**R3 — the drafted `dissonance` leaks the label.** It is built from
`push_recency`, and `E` is defined as `days_since_push > 365`. The original says
so in its own header, line 35: *"push-date/archived are NOT inputs to A_n or
C_dev"*. The draft would introduce into the pipeline exactly the leakage the
pipeline was built to avoid.

---

## What ships, and the predictions

The module is a **true rename**: same arithmetic, engineering names, tradition
vocabulary reachable only through a display adapter.

| engineering name | original | definition |
|---|---|---|
| `utility` | `a` | minmax of `log1p(stargazers)` |
| `d_dec` | `t` | minmax of `log1p(n_closed)` |
| `d_enc` | `rsp` | minmax of `1/(1 + tau_v)` |
| `noise` | `hbar` | minmax of `tau_v` |
| `alignment` | `A_n` | cosine of `(utility, d_dec, d_enc)` to ones |
| `adg_score` | `C_dev` | `alignment · (utility · d_dec) / (eps + noise)` |

`where`: every mapping read from `adg-tqg/experiment.py` lines 55–86.

### Render labels

`aligned | misaligned | high_dissonance`.

**The two halves of the instruction conflict** — the first says
`high_dissonance` with the reason that the measured quantity is a top-quartile
say–do gap and "chaos" overstates it; the second says `chaos`. Taking the one
with the stated reason, because it is this repository's standing rule that a
label names what was measured — the same rule that demoted Foster from "health"
to an assembly check. **One constant to change if the other was meant.**

### Predictions

| # | Prediction | Value |
|---|---|---|
| R4 | The renamed module reproduces `experiment.py`'s `C_dev` and `A_n` **bit-identically** on all 22 records | max abs diff < 1e-12 |
| R5 | And its `kappa` equals `sorted(A_n)[n//2]`, not `np.median` | exact |
| P13-a | Dropping any single record changes the rank order of the remaining 21 for **at least one** record | ≥ 1 drop shifts ranks |
| P13-b | A typed cohort hash **cannot enter**: the constructor computes it from fixture bytes | constructor-only |
| P14-a | **Leaky** dissonance (push-based) separates survived from failed under an exact permutation null at **p < 0.01** — because the label is a function of it | p < 0.01 |
| P14-b | The **clean** `adg_score` (no push input) also separates, at **p < 0.05** | p < 0.05 |
| P14-c | The leaky p is **smaller** than the clean p, and the gap is the leakage | leaky < clean |
| P15-a | A zombie probe — fresh push, very high `tau_v` — renders `high_dissonance` | high_dissonance |
| P15-b | A healthy probe — fresh push, low `tau_v`, high adoption — renders `aligned` | aligned |
| P15-c | Appending any probe **changes the cohort hash**, so a probe reading can never be mistaken for a fixture reading | hash differs |

**P14-b is the one I could be wrong about.** 6 failures against 16 survivors is
thin, and an exact permutation test over C(22,6) = 74,613 assignments has a
floor of p ≈ 1.3e-5 but no power to spare. If it misses, the honest report is
that the cohort does not support the separation claim at n = 22, which is what
the ledger already says about uncorrected multiplicity.

---

## Nulls, registered in advance

**NULL-R1.** Every quantity here is **cohort-relative**. `utility`, `d_enc`,
`d_dec` and `noise` are min-max normalised within these 22 repositories, and
`kappa` and the quartile bound are order statistics of this cohort. A score is
not a property of a repository; it is a property of a repository *in this list*.

**NULL-R2 — correlational only.** Nothing here is causal. A high score does not
make a project survive, and the labels come from push dates, not from anything a
score influenced.

**NULL-R3.** n = 22, p-values uncorrected for multiplicity. A permutation null
tests one statistic; running several and reporting the best would be the thing
the ledger already forbids.

**NULL-R4.** The probes in P15 are **synthetic** records, constructed to have a
stated shape. They demonstrate what the renderer does with such a record. They
are not evidence that such repositories exist or are common.

**NULL-R5.** "Dissonance" is a say–do gap between two chosen columns. Another
pair of columns is another quantity with the same name.

**NULL-R6.** The rename is measured bit-identical to one prior implementation.
That makes it a faithful rename; it says nothing about whether the arithmetic
was a good idea.

---

## What would falsify this

1. **R4 fails** — the rename is not arithmetically faithful and must not ship.
2. **P14-b fails** — the clean score does not separate, and the ADG claim is
   unsupported on this cohort.
3. **P14-c fails** — the leaky and clean versions agree, and my account of the
   leakage is wrong.
