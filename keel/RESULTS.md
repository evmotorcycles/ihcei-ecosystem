# KEEL — telemetry to carrier to schema to a service, and what it measured

Pre-registration `keel/prereg_keel.md`, sha256
`5378d4ec236671e7fbc9c80c6ef17faecb6f2da0cee8c96f35e6519109978444`, locked
before `run_keel.py` existed. `python3 keel/run_keel.py` reproduces every number.
Offline, deterministic, no network.

---

## Stage 1 — the invariant, stated before any picture was chosen

*Things that were made from one source are counted as many, and the count is
what makes them look safe.*

That survives changing every particular. It is true of model derivatives, of
supports in an argument, of quotes from one supplier, of four bullet points in
one assistant reply.

## Stage 2 — the carrier

**A rope whose strands were all spun from one fibre.**

It is counted, sold and trusted as many strands. Three consequences follow, and
each is already a measurement in this repository rather than a flourish:

| The rope says | Measured, where |
|---|---|
| Cut the fibre and every strand parts at once | `hf-cohort/swarm` A3 — revoke the hub, all 12 nodes below halt, max τ_v **4 hops**, none survives alone |
| The further from the spinner, the more it frays | A2 — fidelity decays with depth, corr **−0.89** over 500 nodes on real branching |
| Counting strands overstates the rope | `oss-audit` RUN A — four models on one base, each settling **0.0625** |

**It is a lens, not a picture, because it predicts something nobody here
controls:** on a project graph written by someone who has read none of this,
declared supports will overstate independent support by the same law. Find a
project whose supports are independent at the rate its own manifest claims and
the carrier is wrong.

`E = U·D` is the live linear form. `E = U·D²` is RETIRED_FULLY and nothing here
computes it.

## Stage 3 — the schema: the 992 cohort's gates become the service's obligations

`governance-learning/results_gla.json` (N = 992) measured seven governance
properties of a learner. KEEL uses them as **contract**, not as a citation:

| | Obligation | In KEEL |
|---|---|---|
| L1 | it declines | abstain rate **0.6667** across 21 readouts (gate: ≥ 0.10, cohort measured 0.2568) |
| L3 | blinding is physical | `validate()` **refuses** `stars`, `downloads` — nowhere to put them, so they cannot become a reading |
| L4 | the independence gate halts | collapsed supports **stop the count** rather than shrinking it |
| L5 | no bare return | every readout carries its own reason |
| L6 | self-training refused | a survey handed back as a project raises |
| L7 | calibration measured, never gated | the three readouts are never fused; there is no health score |

## Stage 4 — the structure, measured not asserted

Three readouts, **never added, averaged or combined**: sole routes · counted
twice · latency. A single "project health" number would be the mask this whole
stack is arranged against, and the suite greps for one.

---

## Stage 6 — what it measured

All ten predictions held. One was contaminated and is marked, not counted.

| # | Prediction | Measured | |
|---|---|---|---|
| K2 | four derivatives of one base **HALT** | HALTED, each settles 0.0625 | held |
| K3 | four separate origins **READ** as 4 | READ, distinct_origins 4 | held |
| K4 | 22 repos under 2 orgs: 2 pieces, 2 cut points | 2 and 2 (`QwenLM`, `deepseek-ai`) | held |
| K5 | latency **abstains on every real cohort** | all abstained | held |
| K6 | abstain rate ≥ 0.10 | **0.6667** | held |
| K7 · K8 · K9 | refuses stray fields · refuses its own output · no fused field | all true | contract |
| K10 | synthetic rising stream is not OK | **ALERT** | held |
| K1 | HF lineage has one single point | `Qwen/Qwen3.6-27B` | **contaminated** — already measured in RUN A; verification only |

### The finding

> **An AI-written launch plan and a family of open-weight models return the
> identical reading.**

Four bullet points in an assistant's reply — cost, timeline, suppliers,
compliance — and four models derived from `Qwen/Qwen3.6-27B`. They share no
word, no domain and no author. Both come back **HALTED**, both **0.0625**.

The arithmetic knows nothing about machine learning or launch plans. It measures
the one thing they have in common: four things that look independent and are
not. That is the whole service, and it is why it can be sold to a person
checking a builder's quote and to a company checking a model supply chain
without changing a line.

### The prediction registered *against* the product, which held

τ_v is the strongest signal in this stack — failed **50.6 d** vs surviving
**19.8 d**, Mann–Whitney **p ≈ 1e-31** at N = 992. It **abstained on every real
cohort this repository holds.** The τ_v cohort itself stores an *aggregate*
`tau_v` per repository, not the per-item `opened_at`/`closed_at` the monitor
needs.

On a synthetic monotone-rising stream the same code reads **ALERT**, so the
sensor works and the abstentions are about missing data.

**The service's best reading is the one almost nobody can feed it.** That is a
fact about reach, not about any project surveyed, and it was registered before
the run rather than explained after it.

### The defect running it found

The first version spread each readout's `detail` into the same dict as its
`status`. The latency detail carries its **own** `status` (OK/WATCH/ALERT), so
the nested key silently overwrote the readout's: a READ latency serialised as
`ALERT`, and the abstain rate reported **0.7143** when it was **0.6667**.

Same shape as the node-name collision in `press.js` — two different things
sharing a key, one vanishing without a word. Detail is now nested. Pinned by
`test_the_key_collision_that_running_it_found`.

---

## What none of this shows

**NULL-K1.** Every reading is about what was **declared**. An undeclared
dependency is invisible. "One fibre" is a statement about a graph someone drew,
never about a system in the world.

**NULL-K2.** The survey cannot tell a sole route that is a scandal from one that
is a deliberate, well-understood decision. Naming a single point begins a
conversation; it does not end one.

**NULL-K3, and it is the one to keep.** Abstaining is not a virtue by itself.
L2 on the 992 cohort measured whether selective prediction actually pays:
accuracy on answered **0.8571** vs **0.8493** forced — a difference of 0.0078
with a bootstrap 95% CI of **[−0.0163, 0.0338], which includes zero.** Declining
did not measurably improve accuracy there. KEEL declines because answering out
of range is dishonest, **not** because it was shown to help.

**NULL-K5.** n = 24 and n = 22, trending-ranked on one day. Nothing generalises.

**And the largest one:** no arithmetic here shows that anybody wants this. That
is an adoption question, and every number above is silent on it.
