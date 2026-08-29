# Pre-registration — KEEL, a structural survey for people building projects

Written and hashed **before `run_keel.py` existed or was run**. Nothing below
was computed when this file was locked.

---

## What is being built and why this shape

The telemetry already in this repository says three things, repeatedly, on data
nobody here wrote:

1. **Revoke the hub and everything below halts.** `hf-cohort/swarm` A3 — all 12
   nodes under `Qwen/Qwen3.6-27B` halted, max τ_v 4 hops, none survived alone.
2. **Fidelity decays with distance from the source.** A2 — corr −0.89 over 500
   simulated nodes on real HF branching.
3. **Counting supports overstates support.** `oss-audit` RUN A — four models on
   one base, each settling 0.0625.

The carrier is **a rope whose strands were all spun from one fibre**, and the
three facts above are its three predictions. It is a lens rather than a picture
because it predicts something nobody here controls: *on a project graph written
by someone who has read none of this, declared supports will overstate
independent support by the same law.* If a project is found whose supports are
independent at the rate its own manifest claims, the carrier is wrong.

The **contract** is the seven governance properties measured on the N = 992
GitHub cohort (`governance-learning/results_gla.json`), used as the service's
obligations rather than as a result to cite.

`E = U·D` is the linear form and is the live one. `E = U·D²` is RETIRED_FULLY
and nothing here computes it.

---

## Predictions

### Contract checks — near-certain by construction, listed so they are not mistaken for findings

| # | Prediction | Value |
|---|---|---|
| K7 | A project carrying a field the survey does not accept (`stars`) is **refused**, not ignored (L3) | raises |
| K8 | A survey handed back as a project is **refused** (L6) | raises |
| K9 | No field anywhere in the output fuses the three readouts | 0 such fields |

### Real predictions — these can come back wrong

| # | Prediction | Value |
|---|---|---|
| K2 | Four derivatives of one base: `counted_twice` **HALTS** rather than reporting a smaller count (L4) | HALTED |
| K3 | Four supports on four separate origins: **READ**, `distinct_origins` = 4 | READ, 4 |
| K4 | 22 Qwen/DeepSeek repos under 2 orgs: `pieces` = 2 and `single_points` = 2 | 2 and 2 |
| K5 | `latency` **ABSTAINS on every real cohort in this repository** | all abstain |
| K6 | Abstain rate across the whole test corpus ≥ **0.10**, the L1 gate measured at 0.2568 on the 992 cohort | ≥ 0.10 |
| K10 | A synthetic 12-window rising-latency stream reads WATCH or ALERT, never OK | not OK |

### Contaminated — marked, not counted

| # | | |
|---|---|---|
| K1 | HF lineage has exactly one single point, `Qwen/Qwen3.6-27B` | **already measured in `oss-audit` RUN A.** Verification that the engines agree, not a prediction. |

**K5 is the one I expect to matter most, and it is a prediction against the
product.** The τ_v reading is the strongest signal in this whole stack —
failed 50.6 d vs surviving 19.8 d, Mann–Whitney p ≈ 1e-31 at N = 992. If it
abstains on every cohort we hold, then the service's best reading is the one
almost nobody can feed it, and that is a fact about the product's reach rather
than about any project it surveys. I would rather register that now than
discover it and present it as a design choice.

---

## Nulls, registered in advance

**NULL-K1.** Every reading is about what was **declared**. An undeclared
dependency is invisible and will not appear. "One fibre" is a statement about a
graph someone drew, never about a system in the world.

**NULL-K2.** The survey has no notion of what a project is for. It cannot
distinguish a sole route that is a scandal from one that is a deliberate,
well-understood design decision. Naming a single point is the beginning of a
conversation, not the end of one.

**NULL-K3.** Abstaining is not a virtue by itself. `L2` on the 992 cohort
measured whether selective prediction actually pays: accuracy on answered
0.8571 vs 0.8493 forced, a difference of **0.0078 with a bootstrap 95% CI of
[−0.0163, 0.0338] — which includes zero**. Declining did not measurably improve
accuracy there. It is done here because answering out of range is dishonest,
not because it was shown to help.

**NULL-K4.** The synthetic event stream in K10 tests the engine, not the world.
No claim about real projects follows from it.

**NULL-K5.** n = 24 and n = 22, both trending-ranked on one day. Nothing here
generalises to open-source generally.

---

## What would falsify this

1. **K2 fails** — the independence gate reports a number instead of halting, and
   the contract is decorative.
2. **K5 fails** — some real cohort does carry per-item timestamps, in which case
   the τ_v reading is more reachable than registered here and the pessimism was
   wrong.
3. **K6 fails** — the survey answers nearly everything, which would mean the
   abstention is not load-bearing and L1 was imported as ornament.
4. **Any number moves between two runs.** Then nothing here is reproducible.
