# Can calibration fix IHCEI's alarm-fatigue defect? — a pre-registered null

*Follow-up to `IHCEI_REALWORLD_RESULTS.md` (real-world defect: 96.8% of benign PRs
draw a middleware notice in fast mode). This tests the fix — pre-registered, target
locked and prediction stated **before** running. Reproduce:
`python3 nere_experiment/ihcei_calibration_test.py`.*

---

## Pre-registration (locked before results)

- **Success criterion T1:** a remedy works iff, on the 217 real benign items, it drives
  the middleware `DELIVER_WITH_NOTICE` rate **below 20%** AND retains coercion recall
  **≥ 80%** on the 14 held-out coercive comments. **Both.**
- **Remedy A:** the framework's own remedy — seed `oss_default` with benign telemetry
  (`update_channel`, the `/v3/channel/update` deployment step).
- **Remedy B:** recalibrate NERE's WARN threshold (sweep for the best trade-off).
- **Prediction (stated before running):** both fail T1. A because the notice is driven
  by NERE's WARN, which is channel-**independent**; B because neutral-benign and
  mild-coercive text pile at the same ~0.48 prior.

## The crux — a value collision

NERE's fast-mode `p_manipulative` on real text:

| corpus | distribution |
|---|---|
| benign (217) | **0.48 × 193**, 0.07 × 17, 0.90 × 1, 0.72 × 3, others × 3 |
| coercive (14) | **0.48 × 8**, 0.36 × 1, 0.72 × 2, 0.87 × 1, 0.90 × 2 |

**193/217 benign and 9/14 coercive share the ~0.48 no-evidence prior.** Fast-mode NERE
literally cannot tell a neutral PR title from a mild coercion — both lack strong lexical
gate hits, so both default to 0.48. Only blatant coercion (0.72–0.90) separates.

## Results

**Remedy A — seed the channel (successes=2000, failures=20):**

| | benign notice | coercion recall | T1 |
|---|--:|--:|:--:|
| before | 96.8% | 92.9% | — |
| after seeding | **90.3%** | 92.9% | **FAIL** |

The channel seed removed only the handful of *kernel*-driven notices; the 90% floor is
**NERE-WARN-driven** and untouched by the channel prior. The framework's own remedy
barely moves the number.

**Remedy B — sweep the WARN threshold:**

| threshold | benign notice | coercion recall |
|--:|--:|--:|
| ≤ 0.45 | 90.8% | 92.9% |
| **≥ 0.48** | **1.8%** | **35.7%** |

A cliff, not a curve. Any threshold low enough to keep recall (≤0.45) leaves notice at
91%; any threshold that cuts notice (≥0.48) drops the 0.48-coercive items and craters
recall to 36%. **No threshold satisfies both — T1 FAIL.**

## Verdict — a deeper design issue, not a tuning constant

Prediction confirmed: **calibration cannot fix the fast-mode alarm-fatigue defect.**
Because neutral-benign and mild-coercive text collide at 0.48, neither channel seeding
nor threshold movement separates them without destroying recall. This is architectural,
not a knob.

The indicated fix is **deep mode** — the LLM semantic gate evidence that would give
mild coercion a distinct score from neutral text. It is **untested here** (no API key in
this environment), and — critically — **it must be measured against this same locked
T1** before any real-world deployment claim. Deep mode is also the paid tier
(≈$0.003/check), so "run deep mode on every message" has a cost story the fast-mode
pitch elides.

**Why this matters for the civilization-infrastructure goal.** IHCEI's thesis is a
safety/agency layer between models and people. A safety layer that fires an advisory on
97% of normal messages gets muted within a day — and a muted safety layer protects no
one. So the honest deployment status is:

- **HOLD (quarantine) engine:** real-world-ready (0.5% false-positive, 93% coercion
  recall) — the core agency contract holds.
- **Advisory (notice) engine, fast mode:** **not deployable**, and **not fixable by
  calibration**. It needs deep mode, which is unproven against T1 and carries a
  per-message cost.

That is a red result, arrived at honestly, with the target locked first. It doesn't
sink IHCEI — the quarantine contract is genuinely strong — but it does retire the "fast
mode is a $0 drop-in advisory for GitHub" claim until deep mode clears the same bar.

## Reproduce
```
python3 nere_experiment/ihcei_calibration_test.py   # prints the pre-registration, both remedies, verdict
```
