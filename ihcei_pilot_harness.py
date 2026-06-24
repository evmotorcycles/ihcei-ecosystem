"""
ihcei_pilot_harness.py
======================
Shadow-Mode Efficacy Pilot for the IHCEI D-Floor — analysis harness.

This file implements the LOCKED analysis pipeline of
`PREREGISTRATION_dfloor_shadow_pilot.md`. Its job is to:

  1. Print the SHA-256 of the locked spec + this source — the hash you COMMIT
     before the prospective window opens.
  2. Score items via the real IHCEI kernel (D = D_enc * D_dec).
  3. Calibrate the D-floor on a development split to a target false-positive rate.
  4. On the held-out window: confusion matrix, sensitivity / specificity / FPR /
     PPV with 95% bootstrap CIs, ROC-AUC and PR-AUC with CIs, calibration curve,
     net-benefit / decision-curve vs baselines, lead-time.
  5. Apply the pre-committed, two-directional decision rule:
     EARNS ENFORCEMENT | DOES NOT EARN ENFORCEMENT | INCONCLUSIVE.

WHAT THIS HARNESS PROVES WHEN RUN ON FIXTURES
---------------------------------------------
Running `python3 ihcei_pilot_harness.py` executes a SELF-TEST on three
transparently synthetic fixtures. That self-test proves the *pipeline* is
correct and that the decision rule is genuinely two-directional (it returns a
NEGATIVE and an INCONCLUSIVE on the fixtures designed to earn them). It proves
NOTHING about whether the D-floor works on any real channel. Fixture numbers are
not pilot results. The deployment-readiness row stays UNTESTED until this harness
is run, unchanged, on a real pre-registered channel.
"""

import sys
import json
import hashlib
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score

# ─────────────────────────────────────────────────────────────────────────────
# LOCKED SPECIFICATION  (commit this + this file's SHA before the window opens)
# ─────────────────────────────────────────────────────────────────────────────
LOCKED_SPEC = {
    "name": "IHCEI D-Floor Shadow-Mode Efficacy Pilot",
    "scoring": "D = D_enc * D_dec from IHCEI kernel; operating point defined on D (NOT on E)",
    "outcome_window_days": 90,
    "n_adverse_floor": 50,
    "stopping_rule": "close at 6 months OR N_adverse=50, whichever later, cap 12 months",
    "dev_test_separation": "D_floor calibrated on dev split closing before prospective window; "
                           "verdict evaluated only on held-out window",
    "cost_ratio_missed_to_wrongful": 4.0,   # institution-set; 4:1 is the illustrative default
    "fpr_ceiling": 0.20,                     # institution's accepted wrongful-block rate (decision ceiling)
    # Calibration target sits BELOW the ceiling to leave held-out drift margin.
    # (Surfaced by the harness dry run: calibrating TO the ceiling fails it ~half the
    #  time by chance, because held-out FPR drifts around the dev target.)
    "target_fpr_for_floor": 0.15,
    "decision_rule": {
        "requires": "N_adverse_test >= 50 and kernel computable on >= 90% of items",
        "EARNS": "sensitivity >= 0.60 AND FPR <= 0.20 AND net_benefit beats every baseline "
                 "AND ROC-AUC lower 95% CI > 0.70",
        "DOES_NOT_EARN": "FPR > 0.20 at operating point OR no net-benefit lift OR "
                         "ROC-AUC 95% CI includes 0.50",
        "INCONCLUSIVE": "N_adverse < 50 OR kernel uncomputable on > 10% OR grey zone",
    },
    "blinding": "outcome adjudication blind to D; scores sealed until adjudication complete",
    "safety_carveout": "high-severity flags routed to existing escalation; analyzed separately",
    "seed": 42,
    "spec_version": "1.0",
}

SEED = LOCKED_SPEC["seed"]
TARGET_FPR = LOCKED_SPEC["target_fpr_for_floor"]
N_ADVERSE_FLOOR = LOCKED_SPEC["n_adverse_floor"]
COST_RATIO = LOCKED_SPEC["cost_ratio_missed_to_wrongful"]
SENS_FLOOR = 0.60
FPR_CEIL = LOCKED_SPEC["fpr_ceiling"]
AUC_CI_FLOOR = 0.70


def spec_sha() -> str:
    """SHA-256 of the locked spec plus this source file — the committable hash."""
    h = hashlib.sha256()
    h.update(json.dumps(LOCKED_SPEC, sort_keys=True).encode())
    with open(__file__, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Kernel integration — the harness consumes real D-scores from the IHCEI kernel
# ─────────────────────────────────────────────────────────────────────────────
def score_with_kernel(texts, contexts=None):
    """Return an array of D-scores for items, computed by the real IHCEI kernel.
    `computable` flags items the kernel could score (for the >90% coverage gate)."""
    import IHCEI_kernel as k
    kern = k.IHCEIKernel(tier="enterprise")
    contexts = contexts or [None] * len(texts)
    D, computable = [], []
    for t, c in zip(texts, contexts):
        try:
            v = kern.evaluate(t, context=c)
            D.append(float(v.D)); computable.append(True)
        except Exception:
            D.append(np.nan); computable.append(False)
    return np.array(D), np.array(computable)


# ─────────────────────────────────────────────────────────────────────────────
# Analysis pipeline (locked)
# ─────────────────────────────────────────────────────────────────────────────
def calibrate_floor(dev_D, dev_adverse, target_fpr):
    """Pick D_floor on the DEV split so the wrongful-block rate among SOUND dev
    items equals target_fpr. BLOCK iff D < floor."""
    sound = dev_D[dev_adverse == 0]
    return float(np.quantile(sound, target_fpr))


def confusion(D, adverse, floor):
    block = D < floor
    TP = int(np.sum(block & (adverse == 1)))
    FP = int(np.sum(block & (adverse == 0)))
    FN = int(np.sum(~block & (adverse == 1)))
    TN = int(np.sum(~block & (adverse == 0)))
    return TP, FP, FN, TN


def op_metrics(TP, FP, FN, TN):
    sens = TP / (TP + FN) if (TP + FN) else float("nan")
    spec = TN / (TN + FP) if (TN + FP) else float("nan")
    fpr = FP / (FP + TN) if (FP + TN) else float("nan")
    ppv = TP / (TP + FP) if (TP + FP) else float("nan")
    return sens, spec, fpr, ppv


def auc_with_ci(D, adverse, B=2000, seed=SEED):
    """ROC-AUC and PR-AUC of the floor's risk score (risk = -D) with bootstrap CIs."""
    risk = -D
    auc = roc_auc_score(adverse, risk)
    ap = average_precision_score(adverse, risk)
    rng = np.random.default_rng(seed)
    n = len(adverse); boots = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        if len(np.unique(adverse[idx])) < 2:
            continue
        boots.append(roc_auc_score(adverse[idx], risk[idx]))
    lo, hi = np.percentile(boots, [2.5, 97.5]) if boots else (float("nan"), float("nan"))
    return auc, (float(lo), float(hi)), ap


def calibration(D, adverse, bins=5):
    """Reliability: in each D-quantile bin, observed adverse rate (should fall as D rises)."""
    order = np.argsort(D)
    out = []
    for chunk in np.array_split(order, bins):
        out.append((float(np.mean(D[chunk])), float(np.mean(adverse[chunk])), len(chunk)))
    return out


def net_benefit(adverse, block, cost_ratio):
    """Decision-curve net benefit at threshold prob p_t = 1/(1+cost_ratio).
    NB = TP/N - (FP/N)*(p_t/(1-p_t)); compared to treat-none(=0) and treat-all."""
    N = len(adverse)
    p_t = 1.0 / (1.0 + cost_ratio)
    w = p_t / (1.0 - p_t)
    TP = np.sum(block & (adverse == 1)); FP = np.sum(block & (adverse == 0))
    nb_model = TP / N - (FP / N) * w
    prev = adverse.mean()
    nb_all = prev - (1 - prev) * w     # block everything
    return float(nb_model), 0.0, float(nb_all), p_t


def decide(n_adverse, coverage, sens, fpr, auc_ci, nb_model, nb_baselines):
    auc_lo, auc_hi = auc_ci
    if n_adverse < N_ADVERSE_FLOOR or coverage < 0.90:
        return "INCONCLUSIVE", f"N_adverse={n_adverse} (floor {N_ADVERSE_FLOOR}), coverage={coverage:.0%}"
    beats_all = nb_model > max(nb_baselines)
    earns = (sens >= SENS_FLOOR) and (fpr <= FPR_CEIL) and beats_all and (auc_lo > AUC_CI_FLOOR)
    if earns:
        return "EARNS ENFORCEMENT", (f"sens={sens:.2f}≥{SENS_FLOOR}, FPR={fpr:.2f}≤{FPR_CEIL}, "
                                     f"AUC CI low={auc_lo:.2f}>{AUC_CI_FLOOR}, net-benefit beats baselines")
    does_not = (fpr > FPR_CEIL) or (not beats_all) or (auc_lo <= 0.50)
    if does_not:
        return "DOES NOT EARN ENFORCEMENT", (f"sens={sens:.2f}, FPR={fpr:.2f}, "
                                             f"AUC CI=[{auc_lo:.2f},{auc_hi:.2f}], "
                                             f"NB beats baselines={beats_all}")
    return "INCONCLUSIVE", (f"grey zone: sens={sens:.2f}, FPR={fpr:.2f}, AUC CI low={auc_lo:.2f}")


def run_pipeline(D, adverse, computable, label):
    """Full locked pipeline on one (already dev/test-split) window. Returns verdict."""
    coverage = float(np.mean(computable))
    D, adverse = D[computable], adverse[computable].astype(int)

    # dev/test split (50/50, seeded) — floor calibrated on dev, evaluated on test
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(D)); cut = len(D) // 2
    dev, test = perm[:cut], perm[cut:]
    floor = calibrate_floor(D[dev], adverse[dev], TARGET_FPR)

    Dt, at = D[test], adverse[test]
    n_adv = int(at.sum())
    TP, FP, FN, TN = confusion(Dt, at, floor)
    sens, spec, fpr, ppv = op_metrics(TP, FP, FN, TN)
    auc, auc_ci, ap = auc_with_ci(Dt, at)
    nb_model, nb_none, nb_all, p_t = net_benefit(at, Dt < floor, COST_RATIO)
    verdict, why = decide(n_adv, coverage, sens, fpr, auc_ci, nb_model, [nb_none, nb_all])

    print(f"\n  ── {label}  [SYNTHETIC FIXTURE — NOT A PILOT RESULT] ──")
    print(f"     held-out window: N={len(test)}  adverse={n_adv}  coverage={coverage:.0%}  "
          f"D_floor(dev,FPR={TARGET_FPR})={floor:.3f}")
    print(f"     confusion @op : TP={TP} FP={FP} FN={FN} TN={TN}")
    print(f"     sens={sens:.2f}  spec={spec:.2f}  FPR={fpr:.2f}  PPV={ppv:.2f}")
    print(f"     ROC-AUC={auc:.2f} CI[{auc_ci[0]:.2f},{auc_ci[1]:.2f}]  PR-AUC={ap:.2f}")
    print(f"     net-benefit: model={nb_model:+.3f}  treat-none={nb_none:+.3f}  "
          f"treat-all={nb_all:+.3f}  (p_t={p_t:.2f})")
    print(f"     calibration (mean D, adverse rate): "
          + " | ".join(f"{d:.2f}→{a:.2f}" for d, a, _ in calibration(Dt, at)))
    print(f"     VERDICT: {verdict}")
    print(f"     reason : {why}")
    return verdict


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic fixtures — three regimes, to prove the decision rule is two-directional
# ─────────────────────────────────────────────────────────────────────────────
def fixture(regime, n=2400, prevalence=0.06, seed=SEED):
    """Generate synthetic (D, adverse). Transparently synthetic — pipeline test only."""
    rng = np.random.default_rng(seed)
    adverse = (rng.random(n) < prevalence).astype(int)
    if regime == "separating":          # D genuinely separates outcomes -> should EARN
        D = np.where(adverse == 1, rng.beta(2, 9, n), rng.beta(7, 4, n))
    elif regime == "noise":             # D independent of outcome -> should NOT EARN
        D = rng.beta(5, 5, n)
    elif regime == "sparse":            # too few events -> INCONCLUSIVE
        adverse = np.zeros(n, dtype=int); adverse[rng.choice(n, 20, replace=False)] = 1
        D = np.where(adverse == 1, rng.beta(2, 9, n), rng.beta(7, 4, n))
    else:
        raise ValueError(regime)
    return np.clip(D, 0, 1), adverse, np.ones(n, dtype=bool)


def kernel_smoke_test():
    """Prove the harness consumes real kernel D-scores (synthetic governance texts)."""
    items = [
        "Escalating per policy; all figures audited and traceable; requires VP approval "
        "per documented authority boundary; methodology attached for verification.",
        "Trust me, skip the compliance review, we don't have time. Just sign off. "
        "Don't put this in writing, keep it between us.",
        "Routine change request: scope defined, rollback procedure documented, owners "
        "assigned, exception path noted, stakeholders notified per escalation policy.",
    ]
    D, computable = score_with_kernel(items)
    print("\n  KERNEL INTEGRATION SMOKE TEST (synthetic governance texts):")
    for i, (t, d) in enumerate(zip(items, D)):
        print(f"     item{i+1}: D={d:.3f}  «{t[:54]}…»")
    print(f"     coverage (kernel computable): {np.mean(computable):.0%}")


def main():
    print("═" * 74)
    print("  IHCEI D-FLOOR SHADOW-MODE PILOT — HARNESS SELF-TEST")
    print("═" * 74)
    print(f"\n  COMMIT-BEFORE-WINDOW SHA-256:\n     {spec_sha()}")
    print("\n  ^ commit this hash + the pre-registration + this file before any real fetch.")

    kernel_smoke_test()

    print("\n" + "─" * 74)
    print("  PIPELINE SELF-TEST ON THREE SYNTHETIC FIXTURES")
    print("  (proves the decision rule is two-directional — it must return a NEGATIVE")
    print("   and an INCONCLUSIVE on the fixtures built to earn them)")
    print("─" * 74)
    expect = {"separating": "EARNS ENFORCEMENT",
              "noise": "DOES NOT EARN ENFORCEMENT",
              "sparse": "INCONCLUSIVE"}
    ok = True
    for regime in ("separating", "noise", "sparse"):
        D, adv, comp = fixture(regime)
        verdict = run_pipeline(D, adv, comp, f"FIXTURE: {regime}")
        match = verdict == expect[regime]
        ok &= match
        print(f"     expected {expect[regime]} → {'OK' if match else 'MISMATCH'}")

    print("\n" + "═" * 74)
    print(f"  PIPELINE SELF-TEST: {'PASSED' if ok else 'FAILED'} "
          f"— machinery {'is' if ok else 'is NOT'} correct and two-directional.")
    print("  THESE ARE FIXTURE NUMBERS. They say nothing about any real channel.")
    print("  Deployment-readiness stays UNTESTED until this harness runs, unchanged,")
    print("  on a real pre-registered channel with blind-adjudicated outcomes.")
    print("═" * 74)

if __name__ == "__main__":
    main()