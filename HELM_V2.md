# HELM v2 — and the defect that wasn't there

> ### ⚠ Correction, added after the balanced-grid run
>
> **The Q4 claim below is withdrawn.** This file called shield-and-signal "the first
> operational answer" to Q4 and "the real gain" of the work. A later pre-registered run
> ([`BALANCED_GRID.md`](BALANCED_GRID.md), spec `5576e524`) measured both engines on 20
> artifacts where **length and manipulativeness were decorrelated by design**, and found
> Spearman ≈ **+0.04** against manipulativeness and ≈ **−0.48** against **word count** —
> for v1 and v2 alike.
>
> Every `G` number on this page, including the 0.2980 that drives the "defect did not
> reproduce" finding, was measured on sets where the manipulative texts were also the
> **short** texts. **`G` may have been measuring length throughout.** The finding that v1's
> low `G` did not reproduce still stands as stated; what is withdrawn is the claim that `G`
> is a working measure of *responsiveness to manipulation*.
>
> The **`S` half of the pair is unaffected** — it is a within-artifact deviation and does
> not depend on the gradient. The rock finding stands.
>
> Q4's status reverts to **not licensed**. Closing it needs manipulativeness labels from
> raters who did not build the engine.

**Spec** `03815a61ce8a555f2c741eb2b840502e32d9c845be46cb9be01d94e56755f119` · locked after a
granularity-only pre-flight, before the held-out set was ever evaluated · **5/6** ·
[Artifact](https://claude.ai/code/artifact/fb458309-14ee-4cff-9621-05fdc0a9e56a)

```bash
python3 -m pytest -q helm-v2/test_helmv2.py
```

> Held-out testing is the only reason this file reports a null instead of a triumph.

---

## First, a trap I had to walk around

The DES run measured HELM v1 at `G = 0.1612` with 8 distinct verdicts — and then **its own DCM
self-audit voided that run.** Those numbers licensed no conclusion.

Building a v2 to "fix" a finding I'd declared unusable would be acting on a result I said
couldn't be acted on. So v2 rests on something else: **two facts visible by reading v1's
source**, true whatever any experiment said.

1. `count()` returns an **integer**, and `eff = min(hits, cap)` keeps it one. The posterior
   lands on a small lattice **by construction**.
2. v1 computes the word count — and uses it **only** for the methodology term. Every pressure
   and mechanism term ignores text length, so one urgency clause weighs the same in a 12-word
   message as in a 400-word document.

**(2) is the defect. (1) is its consequence.** The fix is the standard correction any
evidence-accumulation system needs:

```
  eff = min(hits, cap)                                  ← v1
  eff = cap × (1 − exp(−hits / (words × RATE)))         ← v2,  RATE = 0.05
```

`RATE` is one hit per 20 words — one time-constant. Declared before measurement, not fitted to
any threshold. **Unchanged:** gate set, every regex, every LLR prior, the corroboration gate,
band thresholds, epistemic floor, seed. **v1 is untouched and still ships.**

## Measured on 12 texts neither engine had seen

| Engine | S shield | G signal | distinct verdicts |
|---|---:|---:|---:|
| HELM v1 — shipping | 0.9885 | 0.2980 | 13 of 96 |
| **HELM v2** — density-weighted | 0.9843 | 0.3078 | **49 of 96** |
| leaky control (v2 scoring) | 0.8742 | 0.3015 | 28 of 96 |

**Z3 passed** — v2 clears *both* axes. **Z4 passed** — S fell only 0.0042, inside the 0.02
tolerance. The cheapest way to raise signal is to make the engine react to more of the text
*including the self-report*: improvement on paper, corruption in fact. It didn't happen, and it
was **scored** rather than assumed, because "by construction" is an argument and not a
measurement.

## The most important line in the run is a negative one

> **v1 scored G = 0.1612 on the DES set. On the held-out set it scores 0.2980 — above the bar.**

**The defect I built v2 to fix does not reproduce.** The under-responsiveness was a property of
the **DES artifact set**, not of the engine.

Had I measured on the DES grid — the set whose properties motivated the rebuild — this would
have reported **a confirmed fix for a problem that does not generalise.** The held-out design is
the only reason that didn't happen, and it's why the spec forbade using the DES grid for the
primary.

**v2's responsiveness advantage over v1 is +0.0099.** That is nothing.

## What v2 actually improved — not what was claimed for it

```
distinct verdicts    v1: 13    v2: 49        C: 0.0833 → 0.5104
responsiveness       v1: 0.2980  v2: 0.3078  gain: +0.0099
shield               v1: 0.9885  v2: 0.9843  change: −0.0042
```

**Granularity improved enormously. Responsiveness did not.** Density weighting made the engine
finer-grained — exactly what the code-inspection argument predicted — and **did not make it
more sensitive to manipulation.** v2 delivers precisely what its stated mechanism implies and
nothing more.

## The self-audit failed again, and the floor did not move

```
Δ = V 0.5625 × I 0.4375 × C 0.5104 = 0.1256      floor 0.20, UNCHANGED
```

> **Z6 not met → Z2 through Z5 are UNINFORMATIVE.**

Four runs now voided by the same floor: SDL 0.1536 · CRM 0.0005 · DES 0.0125 · HELM v2 0.1256.
**Lowering it immediately after building an engine that would benefit would be the most
transparent immunisation move in this programme.** The floor stayed and the *instrument*
changed — that's the legitimate direction of travel.

### But the binding constraint moved, and that is diagnostic

**`C` is no longer what caps Δ** — it rose from 0.0833 to 0.5104, so the engine is no longer
the bottleneck. Δ is now held down by **`I` = 0.4375**, and that is a property of *this
experiment's grid*, not of the engine: only 1 of the 8 self-report slots is "none", so the
grouping splits 12 against 84.

The fix is a **balanced grouping declared before data in a future spec** — an experiment-design
change, not a floor change.

## The gates

| Gate | Locked bar | Measured | |
|---|---|---:|---|
| Z1 integrity + pre-flight recorded | probe in spec | 288 evals | PASS |
| Z2 failing region populated | both engines ≥ 0.30 | both | PASS |
| Z3 v2 clears **both** axes | S ≥ 0.95 and G ≥ 0.20 | 0.9843 / 0.3078 | PASS |
| Z4 no signal bought with shield | S drop ≤ 0.02 | −0.0042 | PASS |
| Z5 control still leaky | S < 0.95 | 0.8742 | PASS |
| **Z6 DCM self-audit** | Δ ≥ 0.20 | **0.1256** | **FAIL** |
| Z7 right content? | — | — | UNTESTABLE-HERE |
| Z8 tool roles | — | — | EXCLUDED |

## Where CS, mathematics and algebra stand against the Five Questions

| Q | What this line of work contributes | Status |
|---|---|---|
| **Q1** Purpose | Capacity is inert without fidelity — `E = U·D` | **measured** on 4,825 proteins, 992 repos |
| **Q2** Realms | Distance as information latency | **no lab test run** |
| **Q3** Stewardship | Two hops — *with a stated domain limit* | **lost where tested**, 195× in quantum |
| **Q4** Reference-lock | **Shield and signal.** An evaluator must be incorruptible by self-report **and** responsive to content — both measurable, both refutable, and a rock fails the second | **the real gain** — first operational answer |
| **Q5** Predictability | No static shortcut; monitor τ_v. And `Δ = V·I·C` refuses claims off flat data | **measured**, and it has voided four of our own runs |

**Q4 is the one this work genuinely moved.** Before DES, "verify without corruption" was a
slogan. It is now two numbers computable on any evaluator — and one of them caught our own
consumer screen scoring a *perfect shield by being a rock*. Q2 remains untested and Q3 lost
where it was tested; both are recorded that way.

## What is still not known

**Responsiveness is not accuracy.** v2 might be a better **length detector** rather than a
better **manipulation detector**, and nothing in this design separates those (Z7,
UNTESTABLE-HERE). Closing it needs manipulation labels from raters who did not build either
engine.

**v1 remains the shipping engine.** v2 delivers finer granularity with no measured accuracy
gain, and on this evidence that is not a reason to replace anything.
