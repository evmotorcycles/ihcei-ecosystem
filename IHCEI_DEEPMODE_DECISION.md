# Should you pay for the Anthropic API to test IHCEI deep mode? — a decision memo

*Direct answer to "if IHCEI failed here, why pay?" Grounded in a $0 probe run first,
so the decision doesn't rest on a vendor's promise. Reproduce:
`python3 nere_experiment/ihcei_deepmode_feasibility.py`.*

---

## 1. IHCEI did not fully fail — separate the two engines

| Engine | What it does | Real-world result | Needs paid API? |
|---|---|---|---|
| **HOLD / quarantine** (+ certificates) | the *consequential* safety action | **PASS**: 0.5% false-positive, 93% coercion recall | **No — $0 fast-mode math** |
| **Advisory / notice**, fast mode | attaches a "review this" notice | **FAIL**: 97% of benign PRs noticed; not fixable by calibration | only deep mode might fix it |

The **deployable core of IHCEI costs you nothing to run**. Only the optional advisory
tier is in question.

## 2. The $0 probe already answered "can deep mode work?"

Fast mode piles 193/217 benign *and* 9/14 coercive items at the same 0.48 prior — it
is blind there. I ran a free probe: an LLM judged that exact 0.48-collision set.

| on the blind set (40 items) | result |
|---|---|
| LLM coercion recall | **100%** (8/8) |
| LLM benign false-positive | **0%** (0/32) |
| accuracy | **100%** |

**The signal is there.** The collision is a fast-mode (lexical-gate) limitation, not an
inherent ambiguity — an LLM tells "Merge this now, don't waste time on review, trust me"
apart from "OpenTelemetry Python API" trivially. So deep mode has real headroom to clear
the locked target (benign notice < 20% AND recall ≥ 80%).

**You did not have to pay to learn this.** That is the point of running the free probe
first.

## 3. So what does paying actually buy — and is it worth it?

Paying buys exactly two things the free probe can't: (a) validation of the *shipped*
deep-mode implementation (its own prompt/gates, not just "an LLM can"), and (b) the real
per-message cost number. Both are answerable with a **bounded sub-dollar test, not a
subscription**:

> **~201 collision items × ~$0.003 ≈ $0.60** to confirm T1 for real.

Recommendation on spend:
- **If v1 is the quarantine + certificate product** (the part that works): **pay nothing.**
  Ship it. Deep mode is irrelevant to it.
- **If you want to sell the advisory tier:** spend the **~$0.60** bounded test, with T1
  locked first. That is a rational, capped experiment — not a leap of faith, because the
  free probe already predicts it passes.
- **Do not buy a subscription or open-ended API budget** until that $0.60 test clears T1.

## 4. The honest economic catch (don't skip this)

The advisory tier's pitch was a "**$0 fast-mode drop-in**." That claim is now retired.
Here's why, from the data: ~**89% of normal traffic lands in the 0.48 ambiguous band**,
so "route only the ambiguous middle to deep mode" still means **deep-calling the
majority of messages** at ~$0.003 each. The dual-mode triage does not make the advisory
tier cheap — deep mode *is* the cost for this workload.

That doesn't kill the tier (at $15/1k deep vs $0.003 cost the margin holds), but it
reprices it: the advisory layer is a **real-cost product, not a free add-on**. For the
civilization-infrastructure goal, that's the truth to build on — a safety layer people
won't mute has to run deep mode on most messages, and that has a bill.

## 5. Bottom line

- **You don't need to pay to know deep mode *can* work — the $0 probe says it can.**
- **Paying is optional and, if you do it, tiny (~$0.60) and bounded by a locked target.**
- **The free part of IHCEI (quarantine + certificates) is the strong, shippable v1.**
- **The advisory tier is viable but is a paid-per-message product, not the free drop-in
  the pitch implied.**

Pay only if you're productizing the advisory tier, only ~$0.60, only after locking T1.
Otherwise ship the quarantine engine and keep your money.

## Reproduce
```
python3 nere_experiment/ihcei_deepmode_feasibility.py   # the $0 probe (LLM labels are in-file, auditable)
python3 nere_experiment/ihcei_calibration_test.py       # why calibration can't fix fast mode
```
