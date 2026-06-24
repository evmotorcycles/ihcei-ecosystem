# Pre-Registration — Shadow-Mode Efficacy Pilot for the IHCEI D-Floor

**What is under test:** whether enforcing a governance-fidelity floor (the IHCEI D-floor) as a decision rule on a real institutional channel **catches genuine governance failures at a false-positive cost the institution would accept** — measured against observed downstream outcomes, blocking nothing.

**Status:** locked specification. Commit this file and the SHA-256 printed by the pilot harness **before** the prospective window opens. No definition, threshold, or operating point below may change after outcomes are seen. The design can return **earns-enforcement, does-not-earn-enforcement, or inconclusive**, and all three are reportable.

---

## What this test is — and is not

- **It tests the floor as a decision rule.** Does blocking low-D transmissions catch real failures without killing too many sound items? That is a classifier-validation question about error rates, answered against ground truth.
- **It does NOT test the coupling exponent.** The floor is exponent-agnostic at the boundary: D→0 collapses E under both `U·D` and `U·D²`. The operating point is defined on **D directly** (governance fidelity), not on E, so the deployed gate carries no commitment to the disconfirmed quadratic. The coupling question is the statutory pre-registration's job; this document does not reopen it.
- **It does NOT impose anything on the institution.** Shadow mode blocks nothing. The pilot's entire purpose is to produce the efficacy evidence that an institution would need to *independently verify before* choosing to adopt the floor — i.e., to raise the institution's D_dec rather than coerce it. Forcing adoption of an unvalidated constraint is the benevolent-tyranny signature the kernel is built to BLOCK; this pilot is the framework refusing to do to an institution what it forbids the institution from doing.

---

## Why this test exists

You may install a fail-safe *for your own system* without validation — a smoke detector needs no trial. But you need validation to **claim the fail-safe works** and to **ask anyone else to adopt it**. "Prescriptive" exempts the quadratic from being a descriptive *law*; it does not exempt the *constraint* from owing evidence of its **efficacy** — false-positive rate, cost, and whether it prevents the failures it targets — before deployment. The OQM companion says exactly this. This pilot supplies that evidence or withholds it.

---

## Setting & unit

- **Channel:** one decision channel at one institution that (a) carries **governance communications** (approval memos, change requests, disclosures, sign-offs — items with explicit scope, roles, rules, procedures, exceptions), and (b) has **observable downstream outcomes**. Recommended first instantiation: an internal **change-/release-approval pipeline** (change requests and design docs as items; production incident or rollback as the adverse outcome) — high volume, observable outcomes, willing-partner-tractable. Higher-stakes alternatives with more access friction: compliance-disclosure sign-off (outcome = restatement / enforcement action / audit finding) and clinical incident-report triage (outcome = recurrence / harm / mandated escalation).
- **Unit:** one submitted item passing through the channel during the prospective window.
- **Domain admission (pre-registered):** the channel must clear the same Explicit-Governance-Structure gate used in the statutory prereg (EGS ≥ 0.60 on a sample of its items), fixed before the window. This keeps "governance-communication channel" a measured property, not a post-hoc label.

---

## The instrument

- **Score:** the IHCEI kernel computes `D = D_enc × D_dec`, U, the manipulation flags, and a PASS/WARN/BLOCK verdict per item, emitting its existing SHA-256 certificate (the certificate is the pilot's audit substrate).
- **Operating point (pre-registered, defined on D):** the primary decision is **BLOCK if D < D_floor**, with `D_floor` **calibrated on a development split that closes before the prospective window opens**. The floor is calibrated to a target false-positive rate set **below** the decision ceiling (default: calibrate to FPR 0.15 against a 0.20 ceiling), leaving margin for held-out drift — calibrating *to* the ceiling fails it roughly half the time by chance, a defect the harness dry run surfaced. The kernel's legacy `E < 0.04` threshold was calibrated to the quadratic and to specific cases; it is **not** used as the operating point here — it is re-derived on D. The full WARN/BLOCK verdict is also logged for secondary analysis.
- **Reporting:** the full ROC and precision-recall curves are reported so the institution can choose its own deployment operating point afterward; the **go/no-go decision is evaluated at the single locked primary operating point**, on a held-out prospective window, not at a post-hoc-chosen point.

---

## Outcome (ground truth — measured, non-circular, blind-adjudicated)

- **E_adverse (positive class):** the item is linked to a downstream adverse event — incident, rollback, restatement, enforcement action, audit finding, or recurrence (domain-specific, locked) — within **W = 90 days** of the decision. Else the item is **sound**.
- **Independence:** the outcome is determined from downstream operational records, **never from D**. Adjudicators classifying outcomes are **blind to the D-scores** (scores are sealed until adjudication completes). This blinding is what prevents the efficacy estimate from being contaminated by the instrument it is testing.

---

## Shadow-mode integrity, blinding, and the safety carve-out

- **Block nothing.** The kernel runs alongside the live channel, logs verdicts and certificates, and takes **no consequential action** on any item. The channel operates exactly as it would without the pilot.
- **Sealed scores.** Item authors and outcome adjudicators do not see D-scores during the window. (If authors saw scores, behavior would change; if adjudicators saw them, outcome labels would be biased. Either contaminates the estimate.)
- **Safety carve-out (mandatory, especially clinical).** Shadow mode suppresses *measurement*, not *safety*. If the kernel flags a genuinely high-severity item (pre-defined severity criteria), it is routed to the institution's **existing** escalation channel — the pilot never withholds a real safety signal to protect a clean dataset. Carved-out items are recorded and analyzed separately; they do not enter the primary efficacy denominator if the escalation altered their outcome.

---

## Sampling & power

- **Event-count driven.** Confidence-interval width on sensitivity and false-positive rate is governed by the number of adverse events, not total volume. **Require N_adverse ≥ 50** in the held-out window (more for tight CIs; 50 is the floor below which the verdict is INCONCLUSIVE), mirroring the N_fail ≥ 100 discipline of the coupling test.
- **Stopping rule (locked):** the window closes at **6 months OR upon reaching N_adverse = 50, whichever is later, capped at 12 months.** Locked before opening; no peeking-and-stopping.
- **Development/test separation:** `D_floor` and any preprocessing are fixed on items from a development period that ends before the prospective window; the locked operating point is evaluated only on the held-out prospective items.

---

## Baselines (the floor must beat something)

Reported against the locked operating point:
1. **Chance** (prevalence-only).
2. **A trivial heuristic** — e.g., item length and an urgency-keyword count — to show the kernel adds value beyond surface features.
3. **The institution's existing review process**, if one exists (the relevant real-world comparator).

The synthesizing metric is **net benefit / decision-curve analysis** across a pre-specified range of cost ratios (cost of a missed failure : cost of a wrongful block). The floor "adds value" only if its net benefit exceeds every baseline across the institution's plausible cost-ratio range.

---

## Analysis

- **Confusion matrix** at the locked operating point: TP (BLOCK + adverse), FP (BLOCK + sound), FN (PASS + adverse), TN (PASS + sound).
- **Operating-characteristic estimates with 95% CIs:** sensitivity/recall, specificity, false-positive rate, precision/PPV, and the full **ROC-AUC and PR-AUC**.
- **Calibration:** reliability curve of D-implied failure probability vs observed failure rate (is a low D-score actually a high failure probability, or just a low score?).
- **Lead-time analysis:** for true positives, time between the BLOCK firing and the adverse event materializing — the early-warning value, paralleling the τ_v result.
- **Secondary:** performance of the three-way PASS/WARN/BLOCK verdict and of each manipulation flag, reported descriptively.

---

## Decision rule (pre-committed, both directions — locked)

A verdict requires `N_adverse ≥ 50`. The **FPR ceiling and sensitivity floor are set by the institution's cost ratio and locked before the window** (the values below are illustrative defaults for a setting where a missed failure costs ~4× a wrongful block):

| Verdict | Condition (at the locked operating point) |
|---|---|
| **EARNS ENFORCEMENT** | sensitivity ≥ 0.60 **and** FPR ≤ 0.20 **and** net benefit exceeds every baseline across the locked cost-ratio range **and** ROC-AUC lower 95% CI > 0.70 |
| **DOES NOT EARN ENFORCEMENT** | FPR > 0.20 at the required sensitivity, **or** no net-benefit lift over the best baseline, **or** ROC-AUC 95% CI includes 0.50 |
| **INCONCLUSIVE** | `N_adverse < 50`, or the kernel was uncomputable on > 10% of items, or the safety carve-out removed enough events to break power |

---

## What each outcome means for deployment

- **Earns enforcement** → the floor has a *demonstrated* operating point with a *known* false-positive cost, on real outcomes, beating real baselines. This licenses a **limited, monitored, human-in-the-loop** enforcement deployment — and, decisively, gives the institution evidence it verified itself, which is the only adoption that survives a regulator or a skeptic. A mandate built on this evidence holds at audit; a mandate built without it does not.
- **Does not earn enforcement** → the floor is not ready to gate anything in this channel. It remains a fail-safe the architect may run on their own system, never a standard to impose. Back to operationalizing D_enc/D_dec.
- **Inconclusive** → not enough events or coverage; extend the window or pick a higher-event channel. The deployment claim stays **unmade** — it is not filled by assumption.

---

## Provenance & honesty constraints

- The full spec — operating point, outcome definition, adjudication protocol, cost ratio, decision thresholds — is committed (SHA-256) **before** the prospective window. The harness, locked spec, sealed scores, and per-item outcome record are archived for reproducibility, exactly as for the two coupling cohorts.
- Outcome adjudication is **blind to D**; the operating point is **not** tuned after outcomes are seen.
- This is a **design, not a result.** No efficacy numbers exist yet; none may be reported, and no enforcement deployment may be described as validated, until the pre-registered pilot is executed. Absent execution, the deployment-readiness row stays **UNTESTED**.

---

### Relationship to the rest of the program

This pilot and the statutory pre-registration are twins under one rule. The statutory test answers a **descriptive** question — how governance viability couples to fidelity (prior: linear). This pilot answers a **prescriptive** question — whether *enforcing* a fidelity floor improves outcomes at acceptable cost. Both are pre-registered, two-directional, and non-circular; neither is allowed to launder the other's claim. Together they are the honest path to deployment: validate the law, then validate the gate, then let an institution adopt a floor it has checked for itself.