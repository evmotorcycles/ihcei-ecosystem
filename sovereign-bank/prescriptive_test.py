#!/usr/bin/env python3
"""
prescriptive_test.py — the Sovereign Risk-Sharing Engine, tested on N=992
========================================================================
Spec: sovereign-bank/prereg/prescriptive_prereg.json, canonical sha256 00d5d277...,
locked and committed BEFORE any gate below was computed.

The descriptive banking design failed twice (2/4 at N=27, 1/4 at N=44). The proposed
explanation is that raw capacity carries momentum in an unguided environment, masking
fidelity. That explanation is only worth anything if it can be wrong, so it is tested
here rather than assumed:

  P1  fidelity survives capacity stratification   MAKE-OR-BREAK   CAN FAIL
  P2  the D >= D_min floor actually binds                         CAN FAIL
  P3  the floored book has a better TAIL (not mean)               CAN FAIL
  P4  unearned capacity inflation predicts collapse               CAN FAIL
  P5  full-reserve invariant                     SPEC CHECK       CANNOT FAIL
  P6  decoupled evaluation changes the allocation  SUPPORTING     CAN FAIL

PRIMARY analysis uses MEASURED-ONLY tau_v (the cohort's imputation is asymmetric:
15.5% of failed vs 4.1% of performing, which could manufacture an effect by itself).
The full sample is reported as SECONDARY; if they disagree, measured-only governs.

    python3 sovereign-bank/prescriptive_test.py     # stdlib only, offline, $0
"""
from __future__ import annotations
import csv, hashlib, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "data", "github", "govphys_quadratic_results.csv")
LOCKED = open(os.path.join(HERE, "prereg", "PRESCRIPTIVE.sha256")).read().strip()
SEED = 42
RESULTS, FAILED = [], []


def gate(name, ok, detail="", falsifiable=True):
    if not ok and falsifiable:
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail,
                    "falsifiable": falsifiable})
    mark = "" if falsifiable else "   [spec check, not evidence]"
    print("\n  %-4s %s%s" % ("PASS" if ok else "FAIL", name, mark))
    print("        " + detail)


def auc(scores, labels):
    """P(a random defaulter scores above a random performer); ties = 0.5."""
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return float("nan")
    return sum(1.0 if a > b else 0.5 if a == b else 0.0
               for a in pos for b in neg) / (len(pos) * len(neg))


def quantile(v, q):
    v = sorted(v)
    if not v:
        return float("nan")
    i = q * (len(v) - 1)
    lo, hi = int(i), min(int(i) + 1, len(v) - 1)
    return v[lo] + (i - lo) * (v[hi] - v[lo])


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2.0 + 1
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def stratified_auc(rows):
    """P1: hold capacity constant, then ask whether tau_v still discriminates."""
    ordered = sorted(rows, key=lambda r: r["stars"])
    n = len(ordered)
    strata, per = [], []
    for k in range(5):
        chunk = ordered[k * n // 5:(k + 1) * n // 5]
        lab = [r["default"] for r in chunk]
        if len(set(lab)) < 2:
            per.append({"stratum": k + 1, "n": len(chunk), "auc": None,
                        "note": "single-outcome stratum, excluded"})
            continue
        a = auc([r["tau_v"] for r in chunk], lab)
        strata.append((len(chunk), a))
        per.append({"stratum": k + 1, "n": len(chunk), "defaults": sum(lab),
                    "auc": round(a, 4),
                    "median_stars": round(sorted(r["stars"] for r in chunk)[len(chunk) // 2])})
    if not strata:
        return float("nan"), 0, per
    w = sum(n_ * a for n_, a in strata) / sum(n_ for n_, _ in strata)
    return w, sum(1 for _, a in strata if a > 0.5), per


def bootstrap_p95(book, trials=2000):
    rnd = random.Random(SEED)
    rates = []
    for _ in range(trials):
        s = [book[rnd.randrange(len(book))] for _ in range(len(book))]
        rates.append(sum(s) / len(s))
    return quantile(rates, 0.95), sum(rates) / len(rates)


def main():
    raw = list(csv.DictReader(open(CSV)))
    rows = [{"repo": r["repo"], "stars": float(r["stars"]), "tau_v": float(r["tau_v"]),
             "D": float(r["D"]), "imputed": int(float(r["tau_v_imputed"])),
             "default": 1 - int(r["E"])} for r in raw]
    measured = [r for r in rows if not r["imputed"]]

    print("=" * 84)
    print(" THE SOVEREIGN RISK-SHARING ENGINE — prescriptive gates on the recovered N=992")
    print(" spec   " + LOCKED)
    print(" data   data/github/govphys_quadratic_results.csv (recovered + verified 7/7)")
    print("=" * 84)
    print("\n full sample     N=%d  defaults=%d" % (len(rows), sum(r["default"] for r in rows)))
    print(" MEASURED-ONLY   N=%d  defaults=%d   <- PRIMARY (imputation is asymmetric)"
          % (len(measured), sum(r["default"] for r in measured)))

    # D_min: outcome-free 40th percentile of D across the FULL cohort, fixed at lock time
    d_min = quantile([r["D"] for r in rows], 0.40)
    print(" D_min = 40th pct of D over the full cohort = %.6f" % d_min)

    # ---- P1  MAKE-OR-BREAK ------------------------------------------------------
    w_meas, n_above_meas, per_meas = stratified_auc(measured)
    w_full, n_above_full, _ = stratified_auc(rows)
    pooled = auc([r["tau_v"] for r in measured], [r["default"] for r in measured])
    detail = ("weighted within-stratum AUC(tau_v) = %.4f  (gate > 0.55); strata above 0.5: %d/5\n"
              "        pooled (unstratified) AUC = %.4f  ->  capacity stratification %s the signal\n"
              "        SECONDARY full-sample weighted AUC = %.4f (%d/5 above 0.5)\n"
              "        per stratum: %s"
              % (w_meas, n_above_meas, pooled,
                 "PRESERVES" if w_meas > 0.55 else "DESTROYS",
                 w_full, n_above_full,
                 ", ".join("Q%d n=%d auc=%s" % (p["stratum"], p["n"], p["auc"])
                           for p in per_meas)))
    gate("P1_fidelity_survives_capacity_stratification",
         w_meas > 0.55 and n_above_meas >= 3, detail)

    # ---- P2 ---------------------------------------------------------------------
    top = sorted(rows, key=lambda r: -r["stars"])[:len(rows) // 5]
    excluded = [r for r in top if r["D"] < d_min]
    frac = len(excluded) / len(top)
    gate("P2_the_floor_actually_binds", frac >= 0.20,
         "the D >= D_min floor excludes %d of %d top-quintile-by-stars nodes = %.1f%% "
         "(gate >= 20%%)" % (len(excluded), len(top), 100 * frac))

    # ---- P3  tail, not mean -----------------------------------------------------
    half = len(measured) // 2
    conv = [r["default"] for r in sorted(measured, key=lambda r: -r["stars"])[:half]]
    elig = [r for r in measured if r["D"] >= d_min]
    sov = [r["default"] for r in sorted(elig, key=lambda r: r["tau_v"])[:half]]
    if len(sov) < half:
        sov = sov + [r["default"] for r in sorted(
            [r for r in measured if r["D"] < d_min], key=lambda r: r["tau_v"])][:half - len(sov)]
    c95, cmean = bootstrap_p95(conv)
    s95, smean = bootstrap_p95(sov)
    gate("P3_tail_risk_not_mean_risk", s95 < c95,
         "book size %d each.  conventional (top stars): mean %.1f%%, 95th pct %.1f%%\n"
         "        sovereign (D>=D_min, then lowest tau_v): mean %.1f%%, 95th pct %.1f%%\n"
         "        the earlier design predicted a lower MEAN and lost that at N=44; this "
         "gate tests the DOWNSIDE" % (half, 100 * cmean, 100 * c95, 100 * smean, 100 * s95))

    # ---- P4  the Riba prediction, made falsifiable --------------------------------
    hi = sorted(rows, key=lambda r: -r["stars"])[:len(rows) // 5]
    inflated = [r["default"] for r in hi if r["D"] < d_min]
    sound = [r["default"] for r in hi if r["D"] >= d_min]
    ri = sum(inflated) / len(inflated) if inflated else float("nan")
    rs = sum(sound) / len(sound) if sound else float("nan")
    gate("P4_unearned_capacity_inflation_predicts_collapse", ri > rs,
         "among TOP-QUINTILE-BY-STARS nodes: high capacity on DEGRADED fidelity "
         "(D<D_min, n=%d) defaults at %.1f%%\n        vs high capacity on sound fidelity "
         "(D>=D_min, n=%d) at %.1f%%   ->  gap %+.1f pts"
         % (len(inflated), 100 * ri, len(sound), 100 * rs, 100 * (ri - rs)))

    # ---- P5  declared non-falsifiable --------------------------------------------
    deposits, claims, breaches = 0.0, 0.0, 0
    for r in sorted(elig, key=lambda r: r["tau_v"])[:half]:
        deposits += 1000.0
        claims += 1000.0                       # equity stake only; no credit creation
        if claims > deposits:
            breaches += 1
    gate("P5_full_reserve_invariant", breaches == 0,
         "%d equity contracts, deposits %.0f, claims issued %.0f, breaches %d. "
         "Enforced by construction — reported as conformance, never as evidence."
         % (half, deposits, claims, breaches), falsifiable=False)

    # ---- P6 ----------------------------------------------------------------------
    rho = spearman([r["stars"] for r in rows], [r["D"] for r in rows])
    dec = sorted(rows, key=lambda r: -r["stars"])[:len(rows) // 10]
    below = [r for r in dec if r["D"] < d_min]
    gate("P6_decoupled_evaluation_changes_the_allocation",
         abs(rho) < 0.50 and len(below) >= 1,
         "spearman(stars, D) = %+.4f (gate |rho| < 0.50); top-decile-by-stars nodes "
         "below the fidelity floor: %d" % (rho, len(below)))

    n_falsifiable = sum(1 for r in RESULTS if r["falsifiable"])
    met = sum(1 for r in RESULTS if r["pass"] and r["falsifiable"])
    print("\n" + "=" * 84)
    print(" RESULT: %d/%d falsifiable gates met  (P5 excluded — it cannot fail)"
          % (met, n_falsifiable))
    if FAILED:
        print(" NOT MET: %s" % FAILED)
    if "P1_fidelity_survives_capacity_stratification" in FAILED:
        print("\n P1 FAILED. Holding capacity constant did NOT restore the fidelity signal.")
        print(" The 'capacity momentum masks fidelity' explanation is therefore NOT supported")
        print(" by this cohort, and the prescriptive design loses its empirical motivation.")
        print(" This must be reported as a falsification, not reinterpreted.")
    else:
        print("\n P1 HELD. With capacity held constant, enforcement latency still")
        print(" discriminates default — which is the specific, falsifiable consequence of")
        print(" the capacity-momentum explanation. It could have come out otherwise.")
    print("=" * 84)

    json.dump({"spec_sha256_canonical": LOCKED,
               "csv_sha256": hashlib.sha256(open(CSV, "rb").read()).hexdigest(),
               "N_full": len(rows), "N_measured": len(measured),
               "defaults_measured": sum(r["default"] for r in measured),
               "D_min": round(d_min, 6),
               "P1_weighted_stratified_auc_measured": round(w_meas, 4),
               "P1_strata_above_half": n_above_meas,
               "P1_pooled_auc_measured": round(pooled, 4),
               "P1_weighted_stratified_auc_full": round(w_full, 4),
               "P1_per_stratum": per_meas,
               "P2_excluded_fraction_of_top_quintile": round(frac, 4),
               "P3_conventional_p95": round(c95, 4), "P3_sovereign_p95": round(s95, 4),
               "P3_conventional_mean": round(cmean, 4), "P3_sovereign_mean": round(smean, 4),
               "P4_inflated_default_rate": round(ri, 4), "P4_sound_default_rate": round(rs, 4),
               "P6_spearman_stars_D": round(rho, 4),
               "gates": RESULTS, "gates_not_met": FAILED},
              open(os.path.join(HERE, "results_prescriptive.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
