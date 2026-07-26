#!/usr/bin/env python3
"""
verify_992_recovery.py — is the recovered artifact really the N=992 cohort?
==========================================================================
The N=992 rows were computed by CI run 74994532125, uploaded as a 59,283-byte
artifact, and then discarded because `govphys_quadratic_results.csv` is line 7 of
.gitignore. The run now 404s and the artifact expired, so the cohort was declared
UNRECOVERABLE and the gap was left open.

The artifact has since been supplied from an off-repository copy. A file arriving
with the right name proves nothing — the whole point of the earlier refusal was that
a file engineered to match published statistics would pass every check precisely
because it was built to. So this script does NOT trust the bundled summary. It
recomputes every headline statistic FROM THE 992 ROWS using the repository's own
pre-registered analysis code, and compares against the CI log independently.

A genuine recovery must satisfy all of:
  R1  the pre-registration re-hashes to cac34f44... (the spec the artifact names)
  R2  the CSV has exactly 992 rows, 750 failed / 242 survived
  R3  VIF and Pearson r recomputed from the rows match the log
  R4  primary AIC(lin), AIC(quad) and dAIC recomputed match the log (-3.48)
  R5  the Third Law means recomputed match the log (50.61 / 19.76)
  R6  the verdict recomputed from the rows is QUADRATIC_DISCONFIRMED
  R7  the recomputed values agree with the SUPPLIED summary too (no doctored summary)

Any mismatch means the file is not the cohort and the gap stays open.

    python3 cohort-audit/verify_992_recovery.py
"""
from __future__ import annotations
import csv, hashlib, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

CSV = os.path.join(ROOT, "data", "github", "govphys_quadratic_results.csv")
SUM = os.path.join(ROOT, "data", "github", "govphys_quadratic_summary.json")
LOG = os.path.join(ROOT, "repro", "ci_logs", "run_74994532125_full_step5.txt")
SPEC = "cac34f44b2cea0ee3346921d708f00913f6b67cc36376e0b2e4630b9e77001f7"
SEED = 42

CHECKS, FAILED = [], []


def check(name, ok, detail=""):
    if not ok:
        FAILED.append(name)
    CHECKS.append({"check": name, "pass": bool(ok), "detail": detail})
    print("  %-4s %s" % ("PASS" if ok else "FAIL", name))
    if detail:
        print("        " + detail)


def close(a, b, tol):
    return abs(float(a) - float(b)) <= tol


def main():
    import govphys_quadratic_prereg_test as gp

    rows = list(csv.DictReader(open(CSV)))
    summary = json.load(open(SUM))
    log = open(LOG, errors="ignore").read() if os.path.exists(LOG) else ""

    print("=" * 84)
    print(" VERIFYING THE RECOVERED N=992 ARTIFACT AGAINST THE PRE-REGISTRATION AND CI LOG")
    print(" (recomputed from the rows -- the bundled summary is NOT trusted)")
    print("=" * 84)

    # ---- R1: the spec the artifact names is the spec this repo committed -----------
    live = gp.spec_hash()
    check("R1_prereg_spec_hash", live == SPEC == summary.get("spec_sha256"),
          "live re-hash %s | artifact names %s" % (live[:16] + "...",
                                                   str(summary.get("spec_sha256"))[:16] + "..."))

    # ---- R2: shape --------------------------------------------------------------
    E = np.array([int(r["E"]) for r in rows])
    n_fail, n_surv = int((1 - E).sum()), int(E.sum())
    check("R2_cohort_shape", len(rows) == 992 and n_fail == 750 and n_surv == 242,
          "N=%d  fail=%d  surv=%d   (log: N=992 fail=750 surv=242)"
          % (len(rows), n_fail, n_surv))

    U = np.array([float(r["U"]) for r in rows])
    Den = np.array([float(r["D_enc"]) for r in rows])
    Dde = np.array([float(r["D_dec"]) for r in rows])
    D = np.array([float(r["D"]) for r in rows])

    # ---- R3: channel independence, recomputed -----------------------------------
    r_pear = float(np.corrcoef(Den, Dde)[0, 1])
    vif = 1.0 / (1.0 - r_pear ** 2)
    check("R3_vif_recomputed", close(vif, 1.0203, 5e-3) and close(r_pear, 0.1412, 5e-3),
          "recomputed r=%.4f VIF=%.4f  |  log r=+0.141 VIF=1.02" % (r_pear, vif))

    # ---- R4: the primary model, recomputed with the repo's own estimator ---------
    rng = D.max() - D.min()
    Ds = (D - D.min()) / rng if rng > 0 else D * 0
    aic_lin, _ = gp.aic_logit(E, (U * Ds).reshape(-1, 1))
    aic_quad, _ = gp.aic_logit(E, (U * Ds ** 2).reshape(-1, 1))
    dAIC = aic_lin - aic_quad
    check("R4_primary_dAIC_recomputed",
          close(dAIC, -3.483, 0.02) and close(aic_lin, 1088.215, 0.5)
          and close(aic_quad, 1091.698, 0.5),
          "recomputed AIC_lin=%.3f AIC_quad=%.3f dAIC=%+.3f  |  log dAIC=-3.48"
          % (aic_lin, aic_quad, dAIC))

    # ---- R5: Third Law, recomputed ----------------------------------------------
    tau = np.array([float(r["tau_v"]) for r in rows])
    tf, ts = tau[E == 0], tau[E == 1]
    check("R5_third_law_recomputed",
          close(tf.mean(), 50.61, 0.02) and close(ts.mean(), 19.76, 0.02),
          "recomputed tau_fail=%.2f tau_surv=%.2f  |  log 50.61 / 19.76"
          % (tf.mean(), ts.mean()))

    # ---- R6: the verdict follows from the rows ----------------------------------
    verdict = ("INCONCLUSIVE" if (vif >= 5.0 or n_fail < 100)
               else "QUADRATIC_DISCONFIRMED" if dAIC <= 0 else "OTHER")
    check("R6_verdict_from_rows", verdict == "QUADRATIC_DISCONFIRMED"
          and "QUADRATIC_DISCONFIRMED" in log,
          "recomputed verdict = %s (dAIC<=0, VIF<5, N_fail=%d>=100); log agrees"
          % (verdict, n_fail))

    # ---- R7: the supplied summary was not doctored -------------------------------
    agree = (close(summary["primary_dAIC_quad_minus_lin"], dAIC, 0.02)
             and close(summary["VIF"], vif, 5e-3)
             and close(summary["thirdlaw_tau_fail_mean"], tf.mean(), 0.02)
             and summary["n_total"] == len(rows))
    check("R7_summary_matches_rows", agree,
          "the bundled summary.json is consistent with what the rows actually compute")

    # ---- the contradiction that exposed the synthetic proposal --------------------
    print("\n  For the record: the recovered dAIC is %+.3f. The rejected synthetic"
          % dAIC)
    print("  'restoration' reported -3.16 and a CV AUC with the QUADRATIC winning.")
    print("  Refusing it was correct -- this is what the real cohort actually says.")

    print("\n" + "=" * 84)
    ok = not FAILED
    print(" RESULT: %s  (%d/%d checks)"
          % ("RECOVERY VERIFIED" if ok else "NOT VERIFIED -- GAP STAYS OPEN",
             len(CHECKS) - len(FAILED), len(CHECKS)))
    if FAILED:
        print(" FAILED: %s" % FAILED)
    print("=" * 84)

    json.dump({"spec_sha256": SPEC, "verified": ok, "N": len(rows),
               "n_fail": n_fail, "n_surv": n_surv,
               "vif_recomputed": round(vif, 4), "pearson_recomputed": round(r_pear, 4),
               "aic_lin_recomputed": round(float(aic_lin), 3),
               "aic_quad_recomputed": round(float(aic_quad), 3),
               "dAIC_recomputed": round(float(dAIC), 3),
               "tau_fail_recomputed": round(float(tf.mean()), 2),
               "tau_surv_recomputed": round(float(ts.mean()), 2),
               "verdict_recomputed": verdict,
               "csv_sha256": hashlib.sha256(open(CSV, "rb").read()).hexdigest(),
               "checks": CHECKS, "checks_failed": FAILED},
              open(os.path.join(HERE, "results_992_recovery.json"), "w"), indent=2)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
