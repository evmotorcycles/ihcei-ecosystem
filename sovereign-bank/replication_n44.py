#!/usr/bin/env python3
"""
replication_n44.py — the SAME locked gates, on a larger committed cohort
=======================================================================
Replication of sovereign-bank/underwriting_test.py (spec fbe085fc..., locked before
any data) on an expanded sample: N=44 with 13 defaults, up from N=27 with 6.

Two disciplines observed:
  * the GATES ARE NOT CHANGED. The same B1-B4 thresholds from the locked spec are
    applied verbatim. This is a replication, not a re-specification.
  * the DATA IS COMMITTED. Unlike the N=992 cohort — whose rows were computed, written
    to `govphys_quadratic_results.csv`, uploaded, and then discarded because that
    filename sat in .gitignore — this cohort lives in the repository as
    data/github/cohort_real_n44.csv and reproduces offline forever.

It does NOT retroactively rescue the earlier G2 miss (union N=35 predicted, 33
reached). G2 failed on the data available then and stays failed; this is a separate,
newer artifact.

Run:  python3 sovereign-bank/replication_n44.py
"""
from __future__ import annotations
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "fbe085fcf4cc2a7f5b3bf386a7e81f1542cda6f6f826996ca75ef41162f0d62a"
CSV = os.path.join(ROOT, "data", "github", "cohort_real_n44.csv")


def auc(scores, labels):
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return float("nan")
    return sum(1.0 if a > b else 0.5 if a == b else 0.0
               for a in pos for b in neg) / (len(pos) * len(neg))


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2.0 + 1
            i = j + 1
        return r
    rx, ry = rank(x), rank(y); n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def median(v):
    v = sorted(v); n = len(v)
    return float("nan") if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)


def main():
    rows = list(csv.DictReader(open(CSV)))
    stars = [float(r["stars"]) for r in rows]
    tau = [float(r["tau_v_days"]) for r in rows]
    dflt = [int(r["default"]) for r in rows]
    nd = sum(dflt)

    print("=" * 84)
    print(" REPLICATION on a COMMITTED cohort — same locked gates, larger N")
    print(f" spec {LOCKED}")
    print(f" data data/github/cohort_real_n44.csv  (committed; reproduces offline)")
    print("=" * 84)
    print(f"\n N={len(rows)}  defaults={nd}  performing={len(rows)-nd}   (was N=27, 6 defaults)")
    print(f" median tau_v  default={median([t for t,d in zip(tau,dflt) if d]):7.2f} d"
          f"   performing={median([t for t,d in zip(tau,dflt) if not d]):7.2f} d")
    print(f" median stars  default={median([s for s,d in zip(stars,dflt) if d]):7.0f}"
          f"     performing={median([s for s,d in zip(stars,dflt) if not d]):7.0f}")

    res, failed = [], []
    def gate(name, ok, detail):
        res.append({"gate": name, "pass": bool(ok), "detail": detail})
        if not ok:
            failed.append(name)
        print(f"\n  {'PASS' if ok else 'FAIL'} {name}\n        {detail}")

    auc_tau = auc(tau, dflt)
    auc_star = auc([-s for s in stars], dflt)
    gate("B1_tauv_beats_stars", auc_tau > auc_star,
         f"AUC(tau_v) = {auc_tau:.4f}   vs   AUC(low-stars) = {auc_star:.4f}")
    gate("B2_popularity_is_near_chance", 0.30 <= auc_star <= 0.70,
         f"AUC(stars) = {auc_star:.4f}  (locked near-chance band [0.30, 0.70])")

    half = len(rows) // 2
    conv = sorted(zip(stars, tau, dflt), key=lambda r: -r[0])[:half]
    sov = sorted(zip(stars, tau, dflt), key=lambda r: r[1])[:half]
    cr = sum(r[2] for r in conv) / len(conv)
    sr = sum(r[2] for r in sov) / len(sov)
    gate("B3_portfolio_default_rate", sr < cr,
         f"book of {half}: conventional (top stars) {cr:.1%}  |  sovereign (low tau_v) {sr:.1%}")

    rho = spearman(stars, tau)
    gate("B4_two_axes_not_collinear", abs(rho) < 0.50,
         f"spearman(stars, tau_v) = {rho:+.4f}")

    print("\n" + "=" * 84)
    print(f" RESULT: {len(res)-len(failed)}/{len(res)} gates met at N={len(rows)}"
          f"   (was 2/4 at N=27)")
    if failed:
        print(f" STILL NOT MET: {failed}")
    print("\n This cohort is COMMITTED — the failure mode that lost N=992 (evidence")
    print(" computed, then discarded by a .gitignore line) cannot happen to it.")
    print(" It does NOT rescue the earlier G2 miss, which stays recorded as missed.")
    print("=" * 84)

    json.dump({"spec_sha256_canonical": LOCKED, "N": len(rows), "defaults": nd,
               "auc_tau_v": round(auc_tau, 4), "auc_stars": round(auc_star, 4),
               "portfolio": {"conventional_default_rate": round(cr, 4),
                             "sovereign_default_rate": round(sr, 4)},
               "spearman_stars_tauv": round(rho, 4),
               "gates": res, "gates_not_met": failed},
              open(os.path.join(HERE, "results_replication_n44.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
