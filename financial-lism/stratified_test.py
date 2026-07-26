#!/usr/bin/env python3
"""
stratified_test.py — the stratified relative floor, tested on REAL data
=======================================================================
Spec: financial-lism/prereg/finlism_prereg.json, canonical sha256 95d96f91...,
locked and committed BEFORE this runner existed.

ARM T. The flat fidelity floor anti-selected on the recovered N=992 cohort. The proposed
remedy is capacity-stratified RELATIVE floors: segment applicants into capacity tiers and
apply the same quantile rule inside each tier, so a corner shop is not measured against a
conglomerate's structural overhead.

The existing evidence for that remedy is a simulator that generates a population with the
capacity-fidelity correlation enforced, then shows the remedy working. That cannot count.
Here the remedy meets a cohort where the correlation was MEASURED.

  T1  stratified beats the flat floor            CAN FAIL   (low bar, declared)
  T2  stratified beats the naive capacity baseline  MAKE-OR-BREAK
  T3  stratified has the better tail             CAN FAIL
  T4  capacity access is preserved               SUPPORTING (construction-favoured)
  T5  fidelity discriminates WITHIN a tier       MECHANISM GATE

    python3 financial-lism/stratified_test.py     # stdlib only, offline, $0
"""
from __future__ import annotations
import csv, hashlib, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "data", "github", "govphys_quadratic_results.csv")
LOCKED = open(os.path.join(HERE, "prereg", "FINLISM.sha256")).read().strip()
SEED = 42
RESULTS, FAILED = [], []


def gate(name, ok, detail="", weight="full"):
    if not ok:
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail, "weight": weight})
    tag = {"full": "", "low": "   [low-value sanity check]",
           "supporting": "   [construction-favoured, supporting only]"}[weight]
    print("\n  %-4s %s%s" % ("PASS" if ok else "FAIL", name, tag))
    print("        " + detail)


def quantile(v, q):
    v = sorted(v)
    if not v:
        return float("nan")
    i = q * (len(v) - 1)
    lo = int(i)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (i - lo) * (v[hi] - v[lo])


def auc(scores, labels):
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return None
    return sum(1.0 if a > b else 0.5 if a == b else 0.0
               for a in pos for b in neg) / (len(pos) * len(neg))


def boot_p95(book, trials=2000):
    rnd = random.Random(SEED)
    rates = [sum(book[rnd.randrange(len(book))] for _ in range(len(book))) / len(book)
             for _ in range(trials)]
    return quantile(rates, 0.95)


def main():
    raw = list(csv.DictReader(open(CSV)))
    rows = [{"stars": float(r["stars"]), "tau_v": float(r["tau_v"]), "D": float(r["D"]),
             "imputed": int(float(r["tau_v_imputed"])), "default": 1 - int(r["E"])}
            for r in raw]
    meas = [r for r in rows if not r["imputed"]]
    N = len(meas)

    print("=" * 84)
    print(" ARM T — CAPACITY-STRATIFIED RELATIVE FLOORS vs a flat floor vs doing nothing")
    print(" spec  " + LOCKED)
    print(" data  data/github/govphys_quadratic_results.csv (recovered + verified 7/7)")
    print("=" * 84)
    print("\n measured-only N=%d  defaults=%d  (%.1f%% base rate)"
          % (N, sum(r["default"] for r in meas), 100 * sum(r["default"] for r in meas) / N))

    # ---- build the three books, all the same size --------------------------------
    flat_min = quantile([r["D"] for r in rows], 0.40)

    ordered = sorted(meas, key=lambda r: r["stars"])
    tiers = [ordered[k * N // 4:(k + 1) * N // 4] for k in range(4)]
    strat_eligible, tier_report = [], []
    for k, t in enumerate(tiers):
        local = quantile([r["D"] for r in t], 0.40)
        keep = [r for r in t if r["D"] >= local]
        strat_eligible += keep
        tier_report.append({"tier": k + 1, "n": len(t), "local_D_min": round(local, 6),
                            "admitted": len(keep),
                            "median_stars": round(quantile([r["stars"] for r in t], .5)),
                            "default_rate": round(sum(r["default"] for r in t) / len(t), 4)})

    print("\n capacity tiers (quartiles) and their LOCAL floors:")
    for t in tier_report:
        print("   T%d  n=%3d  median stars %8d  local D_min %.6f  admitted %3d  "
              "tier default %.1f%%"
              % (t["tier"], t["n"], t["median_stars"], t["local_D_min"],
                 t["admitted"], 100 * t["default_rate"]))

    size = N // 4                      # equal book size across all three strategies
    conv = [r["default"] for r in sorted(meas, key=lambda r: -r["stars"])[:size]]
    flat_pool = [r for r in meas if r["D"] >= flat_min]
    flat = [r["default"] for r in sorted(flat_pool, key=lambda r: r["tau_v"])[:size]]
    strat = [r["default"] for r in sorted(strat_eligible, key=lambda r: r["tau_v"])[:size]]

    def rate(b):
        return sum(b) / len(b)

    print("\n three books of %d each:" % size)
    print("   conventional (capacity only)      default %.1f%%" % (100 * rate(conv)))
    print("   flat floor   (D >= global 40pct)  default %.1f%%" % (100 * rate(flat)))
    print("   STRATIFIED   (tier-local floors)  default %.1f%%" % (100 * rate(strat)))

    # ---- T1 ----------------------------------------------------------------------
    gate("T1_stratified_beats_flat_floor", rate(strat) < rate(flat),
         "stratified %.1f%% vs flat floor %.1f%%  (delta %+.1f pts). The flat floor is "
         "already known to anti-select, so this is a sanity check, not merit."
         % (100 * rate(strat), 100 * rate(flat), 100 * (rate(strat) - rate(flat))),
         weight="low")

    # ---- T2  MAKE-OR-BREAK ---------------------------------------------------------
    gate("T2_stratified_beats_conventional_baseline", rate(strat) < rate(conv),
         "stratified %.1f%% vs conventional capacity-only %.1f%%  (delta %+.1f pts).\n"
         "        This is the gate that decides whether the design earns its complexity."
         % (100 * rate(strat), 100 * rate(conv), 100 * (rate(strat) - rate(conv))))

    # ---- T3 ------------------------------------------------------------------------
    s95, c95 = boot_p95(strat), boot_p95(conv)
    gate("T3_stratified_tail_is_better", s95 < c95,
         "bootstrap 95th pct of default rate: stratified %.1f%% vs conventional %.1f%%"
         % (100 * s95, 100 * c95))

    # ---- T4 ------------------------------------------------------------------------
    med_strat = quantile(sorted([r["stars"] for r in strat_eligible], key=lambda x: x), .5)
    med_flat = quantile([r["stars"] for r in flat_pool], .5)
    gate("T4_capacity_access_is_preserved", med_strat > med_flat,
         "median capacity of the admitted pool: stratified %d vs flat floor %d"
         % (round(med_strat), round(med_flat)), weight="supporting")

    # ---- T5  MECHANISM --------------------------------------------------------------
    usable, per = [], []
    for k, t in enumerate(tiers):
        a = auc([-r["D"] for r in t], [r["default"] for r in t])
        per.append({"tier": k + 1, "n": len(t),
                    "auc_lowD_predicts_default": None if a is None else round(a, 4)})
        if a is not None:
            usable.append((len(t), a))
    w = (sum(n * a for n, a in usable) / sum(n for n, _ in usable)) if usable else float("nan")
    gate("T5_within_tier_fidelity_actually_discriminates",
         len(usable) >= 2 and w > 0.55,
         "weighted within-tier AUC(low D -> default) = %s over %d usable tier(s) "
         "(gate > 0.55 and >= 2 usable)\n        per tier: %s\n"
         "        If fidelity carries no within-tier information, a tier-local floor is "
         "sorting on noise." % ("%.4f" % w if usable else "n/a", len(usable),
                                ", ".join("T%d n=%d auc=%s" % (p["tier"], p["n"],
                                          p["auc_lowD_predicts_default"]) for p in per)))

    print("\n" + "=" * 84)
    print(" ARM T RESULT: %d/%d gates met" % (len(RESULTS) - len(FAILED), len(RESULTS)))
    if FAILED:
        print(" NOT MET: %s" % FAILED)
    print("=" * 84)

    json.dump({"arm": "T", "spec_sha256_canonical": LOCKED,
               "csv_sha256": hashlib.sha256(open(CSV, "rb").read()).hexdigest(),
               "N_measured": N, "book_size": size, "flat_D_min": round(flat_min, 6),
               "tiers": tier_report,
               "default_rate_conventional": round(rate(conv), 4),
               "default_rate_flat_floor": round(rate(flat), 4),
               "default_rate_stratified": round(rate(strat), 4),
               "p95_conventional": round(c95, 4), "p95_stratified": round(s95, 4),
               "median_capacity_stratified_pool": round(med_strat),
               "median_capacity_flat_pool": round(med_flat),
               "T5_weighted_within_tier_auc": None if not usable else round(w, 4),
               "T5_usable_tiers": len(usable), "T5_per_tier": per,
               "gates": RESULTS, "gates_not_met": FAILED},
              open(os.path.join(HERE, "results_stratified.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
