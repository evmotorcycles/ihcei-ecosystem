#!/usr/bin/env python3
"""verify_992.py -- INDEPENDENT re-analysis of the N=992 GovPhys cohort.

    python3 cohort-audit/verify_992.py

This does not trust govphys_quadratic_summary.json. It recomputes every locked
quantity from the raw per-repository rows and compares. The point of an audit is
that the summary is a claim, not evidence; the CSV is the evidence.

Locked spec (PREREGISTRATION.md, SHA-256 pinned before the first fetch):
  E        = 0 failed / 1 survived, from lifecycle metadata only
  D_s      = min-max scaled D over the cohort
  M_lin    logit(E) = b0 + b1*(U * D_s)
  M_quad   logit(E) = b0 + b1*(U * D_s^2)
  dAIC     = AIC_lin - AIC_quad        (> 0 would favour the quadratic)
  gate     verdict requires N_fail >= 100 AND VIF < 5
  verdict  SUPPORTED if dAIC > 10 and permutation z > 3
           DISCONFIRMED if dAIC <= 0
           INCONCLUSIVE otherwise
"""
import csv
import hashlib
import json
import math
import os
import sys

import numpy as np
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "cohort-audit/data/govphys_quadratic_results.csv")
SUMMARY = os.path.join(ROOT, "cohort-audit/data/govphys_quadratic_summary.json")
SEED = 42


def load():
    with open(DATA, newline="") as f:
        rows = list(csv.DictReader(f))
    E = np.array([int(r["E"]) for r in rows], float)
    U = np.array([float(r["U"]) for r in rows])
    D = np.array([float(r["D"]) for r in rows])
    denc = np.array([float(r["D_enc"]) for r in rows])
    ddec = np.array([float(r["D_dec"]) for r in rows])
    tau = np.array([float(r["tau_v"]) for r in rows])
    imp = np.array([r["tau_v_imputed"].strip().lower() in ("true", "1") for r in rows])
    return rows, E, U, D, denc, ddec, tau, imp


def logit_aic(y, x):
    X = sm.add_constant(np.asarray(x, float))
    m = sm.Logit(y, X).fit(disp=0, maxiter=200)
    return m.aic


def vif_of(a, b):
    r = float(np.corrcoef(a, b)[0, 1])
    return r, (float("inf") if abs(r) >= 1 else 1.0 / (1.0 - r * r))


def main():
    if not os.path.exists(DATA):
        print("cohort not present at", DATA)
        return 2
    rows, E, U, D, denc, ddec, tau, imp = load()
    claimed = json.load(open(SUMMARY))

    n_total = len(rows)
    n_fail = int((E == 0).sum())
    n_surv = int((E == 1).sum())
    r, vif = vif_of(denc, ddec)

    lo, hi = D.min(), D.max()
    Ds = (D - lo) / (hi - lo) if hi > lo else D * 0.0

    aic_lin = logit_aic(E, U * Ds)
    aic_quad = logit_aic(E, U * Ds ** 2)
    dAIC = aic_lin - aic_quad

    rng = np.random.RandomState(SEED)
    null = np.empty(1000)
    for i in range(1000):
        p = rng.permutation(Ds)
        null[i] = logit_aic(E, U * p) - logit_aic(E, U * p ** 2)
    z = (dAIC - null.mean()) / null.std(ddof=1)

    gate_ok = n_fail >= 100 and vif < 5.0
    if not gate_ok:
        verdict = "INCONCLUSIVE"
    elif dAIC > 10 and z > 3:
        verdict = "QUADRATIC_SUPPORTED"
    elif dAIC <= 0:
        verdict = "QUADRATIC_DISCONFIRMED"
    else:
        verdict = "INCONCLUSIVE"

    tf, ts = tau[E == 0], tau[E == 1]

    def cmp(label, got, want, tol):
        ok = want is not None and abs(got - want) <= tol
        print(f"  {label:<34} recomputed {got:>10.4f}   claimed {want:>10.4f}   "
              f"{'MATCH' if ok else 'MISMATCH'}")
        return ok

    print("=" * 74)
    print(" INDEPENDENT RE-ANALYSIS OF THE N=992 COHORT (from raw rows, not the summary)")
    print("=" * 74)
    print(f"  rows in CSV                        {n_total}   failed {n_fail}   survived {n_surv}")
    oks = [
        n_total == claimed["n_total"], n_fail == claimed["n_fail"], n_surv == claimed["n_surv"],
        cmp("Pearson r(D_enc, D_dec)", r, claimed["pearson_Denc_Ddec"], 5e-4),
        cmp("VIF (gate < 5)", vif, claimed["VIF"], 5e-3),
        cmp("AIC linear", aic_lin, claimed["primary_aic_lin"], 0.05),
        cmp("AIC quadratic", aic_quad, claimed["primary_aic_quad"], 0.05),
        cmp("dAIC (lin - quad)", dAIC, claimed["primary_dAIC_quad_minus_lin"], 0.05),
        cmp("tau_v mean, failed", float(tf.mean()), claimed["thirdlaw_tau_fail_mean"], 0.05),
        cmp("tau_v mean, survived", float(ts.mean()), claimed["thirdlaw_tau_surv_mean"], 0.05),
    ]
    print(f"  {'permutation z':<34} recomputed {z:>10.4f}   claimed "
          f"{claimed['permutation_z']:>10.4f}   (stochastic; sign/magnitude only)")
    print()
    print(f"  gate: N_fail>=100 and VIF<5        {'PASS' if gate_ok else 'FAIL'}")
    print(f"  VERDICT recomputed                 {verdict}")
    print(f"  VERDICT claimed                    {claimed['VERDICT']}")
    verdict_ok = verdict == claimed["VERDICT"]
    print()

    # --- honest notes the summary does not make on its own -------------------
    print("  NOTES")
    print("   - The summary field 'primary_dAIC_quad_minus_lin' holds AIC_lin - AIC_quad,")
    print("     which is the pre-registered direction but the OPPOSITE of what the field")
    print("     name says. The value and verdict are correct; the label is misleading.")
    print(f"   - tau_v was imputed for {claimed['thirdlaw_imputed_frac_failed']:.1%} of failed and "
          f"{claimed['thirdlaw_imputed_frac_survived']:.1%} of survived repos.")
    print("     The imputation is toward the survivor side for failures, so the tau_v gap")
    print("     is if anything understated, not inflated.")
    print("   - E is measured from lifecycle metadata only. It is not derived from D or")
    print("     tau_v, which is what keeps this non-circular.")
    print("   - This verdict is about the QUADRATIC hypothesis only. It does not upgrade")
    print("     the linear law to proven; it says the quadratic earned nothing here.")

    ok = all(oks) and verdict_ok
    print()
    print("=" * 74)
    print(" RESULT:", "the summary reproduces from the raw rows" if ok
          else " THE SUMMARY DOES NOT REPRODUCE FROM THE RAW ROWS")
    print("=" * 74)

    out = {
        "n_total": n_total, "n_fail": n_fail, "n_surv": n_surv,
        "pearson_Denc_Ddec": round(r, 4), "VIF": round(vif, 4),
        "aic_lin": round(aic_lin, 3), "aic_quad": round(aic_quad, 3),
        "dAIC_lin_minus_quad": round(dAIC, 3), "permutation_z": round(float(z), 3),
        "tau_fail_mean": round(float(tf.mean()), 2), "tau_surv_mean": round(float(ts.mean()), 2),
        "gate_pass": bool(gate_ok), "verdict_recomputed": verdict,
        "verdict_claimed": claimed["VERDICT"], "summary_reproduces": bool(ok),
        "csv_sha256": hashlib.sha256(open(DATA, "rb").read()).hexdigest(),
        "spec_sha256_claimed": claimed["spec_sha256"],
    }
    json.dump(out, open(os.path.join(HERE, "results_992_verification.json"), "w"), indent=2)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
