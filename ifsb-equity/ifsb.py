"""
ifsb.py -- runs the pre-registered IFSB loss-absorbing-funding test.

Spec 0d52c8446d9f31edd2b117e2730029fb0c194c47f73f6df93fa7fadd5cc14e99, locked before
this file was written.

NO INFERENTIAL STATISTICS. n = 117 country-quarters from 6 banking systems, serially
dependent within country, not a sample of anything. Counts and directions only. A test
asserts this file's output contains no p-value, no confidence interval and no
significance claim.
"""
import hashlib
import json
import math
import os
import random
import statistics

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XLSX = os.path.join(ROOT, "data", "colab-audit", "ifsb_financial_statements.xlsx")
LOCKED = "0d52c8446d9f31edd2b117e2730029fb0c194c47f73f6df93fa7fadd5cc14e99"

SPEC = json.load(open(os.path.join(HERE, "prereg", "ifsb_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

P = SPEC["panels"]["PRIMARY_panel_P"]
S = SPEC["panels"]["SECONDARY_panel_S"]
F2_MIN_COUNTRIES, F2_MIN_IQR = 4, 0.02
F3_MIN_COUNTRIES = 4
F6_MIN_COUNTRIES = 3
MIN_QUARTERS = 5
N_PERMUTATIONS, SEED = 200, 20260801


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def wide():
    got = sha256(XLSX)
    if got != SPEC["data_provenance"]["sha256"]:
        raise SystemExit("DATA CHANGED: %s" % got)
    df = pd.read_excel(XLSX, header=SPEC["data_provenance"]["header_row"])
    df["v"] = pd.to_numeric(df["Values in USD Millions"], errors="coerce")
    return df.pivot_table(index=["Country", "Time Period"], columns="Indicator Code",
                          values="v", aggfunc="first")


def direction(rows, rs_key):
    """Split a country at its own median RS; return the sign of the difference in
    median PROV. Negative is the risk-sharing direction."""
    med = statistics.median(r[rs_key] for r in rows)
    hi = [r["prov"] for r in rows if r[rs_key] > med]
    lo = [r["prov"] for r in rows if r[rs_key] <= med]
    if not hi or not lo:
        return None, None
    d = statistics.median(hi) - statistics.median(lo)
    return d, (-1 if d < 0 else (1 if d > 0 else 0))


def count_risk_sharing(panel, rs_key):
    out = {}
    for c, rows in panel.items():
        if len(rows) < MIN_QUARTERS:
            continue
        d, sgn = direction(rows, rs_key)
        out[c] = {"n_quarters": len(rows), "median_prov_difference": d, "sign": sgn}
    return out, sum(1 for v in out.values() if v["sign"] == -1)


def _fmt(d):
    return {c: {"n_quarters": v["n_quarters"],
                "median_prov_difference": (round(v["median_prov_difference"], 6)
                                           if v["median_prov_difference"] is not None
                                           else None),
                "sign": v["sign"],
                "note": (None if v["sign"] is not None else
                         "RS is constant across this country's quarters, so a median "
                         "split leaves one side empty. No direction exists. Counted as "
                         "NOT in the risk-sharing direction, which is the conservative "
                         "treatment and is not a threshold move.")}
            for c, v in d.items()}


def main():
    w = wide()

    def build(cols, rs_fn, extra=()):
        need = list(cols)
        sub = w.dropna(subset=need).reset_index()
        panel = {}
        for _, r in sub.iterrows():
            rec = {"period": r["Time Period"], "rs": rs_fn(r),
                   "prov": r["IS12_010"] / r["BS03"]}
            for e in extra:
                rec[e] = r[e] / r["BS01"]
            panel.setdefault(r["Country"], []).append(rec)
        return panel

    panel_p = build(["BS13_010", "BS01", "BS03", "IS12_010"],
                    lambda r: r["BS13_010"] / r["BS01"], extra=("BS04",))
    panel_s = build(["IS01_010_010", "IS01_010_020", "IS01_010_030", "IS12_010", "BS03"],
                    lambda r: r["IS01_010_030"] / (r["IS01_010_010"] + r["IS01_010_020"]
                                                   + r["IS01_010_030"]))

    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    # ---- F1 integrity -------------------------------------------------------
    comp_p = {c: len(v) for c, v in panel_p.items()}
    comp_s = {c: len(v) for c, v in panel_s.items()}
    ranges_ok = all(0.0 <= r["rs"] <= 1.0 and math.isfinite(r["prov"]) and r["prov"] >= 0
                    for v in list(panel_p.values()) + list(panel_s.values()) for r in v)
    f1 = (comp_p == P["composition_declared_before_analysis"]
          and comp_s == S["composition_declared_before_analysis"] and ranges_ok)
    gate("F1_data_integrity", f1,
         "panel P %d obs %s; panel S %d obs %s; ranges ok=%s"
         % (sum(comp_p.values()), comp_p, sum(comp_s.values()), comp_s, ranges_ok))

    # ---- F2 populated failing region ---------------------------------------
    iqrs = {}
    for c, rows in panel_p.items():
        xs = sorted(r["rs"] for r in rows)
        q1 = statistics.median(xs[:len(xs) // 2])
        q3 = statistics.median(xs[(len(xs) + 1) // 2:])
        iqrs[c] = round(q3 - q1, 6)
    n_varying = sum(1 for v in iqrs.values() if v >= F2_MIN_IQR)
    f2 = n_varying >= F2_MIN_COUNTRIES
    gate("F2_the_failing_region_is_populated", f2,
         "%d of %d countries have within-country RS interquartile range >= %.2f: %s"
         % (n_varying, len(iqrs), F2_MIN_IQR, iqrs))

    # ---- F3 primary ---------------------------------------------------------
    dirs_p, n_rs = count_risk_sharing(panel_p, "rs")
    if f2:
        f3 = n_rs >= F3_MIN_COUNTRIES
        gate("F3_LOSS_ABSORBING_FUNDING_PREDICTS_LOWER_PROVISIONING", f3,
             "%d of %d countries in the risk-sharing direction (needs >= %d): %s"
             % (n_rs, len(dirs_p), F3_MIN_COUNTRIES,
                {c: v["sign"] for c, v in dirs_p.items()}))
    else:
        f3 = False
        gate("F3_LOSS_ABSORBING_FUNDING_PREDICTS_LOWER_PROVISIONING", False,
             "UNTESTABLE-HERE: F2 not met, the median split would be on noise")

    # ---- F4 placebos --------------------------------------------------------
    _, n_bs04 = count_risk_sharing(panel_p, "BS04")
    rng = random.Random(SEED)
    perm_counts = []
    for _ in range(N_PERMUTATIONS):
        shuffled = {}
        for c, rows in panel_p.items():
            vals = [r["rs"] for r in rows]
            rng.shuffle(vals)
            shuffled[c] = [dict(r, rs=v) for r, v in zip(rows, vals)]
        perm_counts.append(count_risk_sharing(shuffled, "rs")[1])
    perm_sorted = sorted(perm_counts)
    p90 = perm_sorted[int(0.9 * (len(perm_sorted) - 1))]
    f4 = f2 and n_rs > n_bs04 and n_rs > p90
    gate("F4_the_result_is_not_reproduced_by_a_placebo", f4,
         "real RS %d countries; BS04 interbank-share placebo %d; permutation null "
         "(seed %d, %d draws) 90th percentile %d, mean %.2f, max %d"
         % (n_rs, n_bs04, SEED, N_PERMUTATIONS, p90,
            sum(perm_counts) / len(perm_counts), max(perm_counts)))

    # ---- F5 leave-one-country-out ------------------------------------------
    loo = {}
    if f3:
        for drop in panel_p:
            rest = {c: v for c, v in panel_p.items() if c != drop}
            d, n = count_risk_sharing(rest, "rs")
            need = math.ceil(2 * len(d) / 3)
            loo[drop] = {"countries_in_direction": n, "of": len(d), "needed": need,
                         "holds": n >= need}
        f5 = all(v["holds"] for v in loo.values())
        gate("F5_no_single_country_carries_the_result", f5,
             "leave-one-out: %s" % {k: "%d/%d>=%d %s" % (v["countries_in_direction"],
                                                          v["of"], v["needed"],
                                                          "hold" if v["holds"] else "FLIP")
                                    for k, v in loo.items()})
    else:
        gate("F5_no_single_country_carries_the_result", False,
             "NOT-APPLICABLE: F3 not met, so there is no result to test for fragility. "
             "Scored as not met rather than skipped.")

    # ---- F6 secondary panel -------------------------------------------------
    dirs_s, n_rs_s = count_risk_sharing(panel_s, "rs")
    majority_sign_p = -1 if n_rs >= (len(dirs_p) - n_rs) else 1
    agree = sum(1 for v in dirs_s.values() if v["sign"] == majority_sign_p)
    f6 = agree >= F6_MIN_COUNTRIES
    gate("F6_the_secondary_income_share_panel_agrees", f6,
         "panel P majority sign %+d; panel S agrees in %d of %d countries (needs >= %d): %s"
         % (majority_sign_p, agree, len(dirs_s), F6_MIN_COUNTRIES,
            {c: v["sign"] for c, v in dirs_s.items()}))

    gates.append({"id": "F7_institution_level_discrimination", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. Every observation is a national aggregate; "
                            "no aggregation of these rows recovers bank-level behaviour."})

    scoring = [g for g in gates if g["weight"] == "full"]

    # ---- POST-RUN DISCLOSURES. No gate is re-scored and no threshold moves. ----
    neg_prov = sorted(("%s %s" % (c, r["period"]), round(r["prov"], 6))
                      for c, rows in panel_p.items() for r in rows if r["prov"] < 0)
    zero_equity = sorted(c for c, rows in panel_s.items()
                         if all(r["rs"] == 0.0 for r in rows))
    disclosures = {
        "D1_F1_failed_because_MY_SPEC_over_asserted": {
            "what_failed": "The locked F1 required every PROV to be non-negative. Eight "
                           "country-quarters carry a NEGATIVE provisioning figure.",
            "cases": neg_prov,
            "why_the_data_is_fine": "A negative provision line is a provision RELEASE -- a "
                                    "write-back of amounts previously reserved. It is "
                                    "ordinary and correct accounting, concentrated in "
                                    "Afghanistan 2018-2023 and one Pakistan quarter.",
            "whose_error_this_is": "Mine. The spec asserted a range the accounting standard "
                                   "does not impose. The gate is NOT re-scored and F1 stands "
                                   "as failed, because a spec that turns out to be wrong is "
                                   "exactly the case the no-moving-thresholds rule is for. "
                                   "The panel composition -- the part of F1 that tests the "
                                   "DATA -- matched the locked declaration exactly in both "
                                   "panels.",
        },
        "D2_TWO_SYSTEMS_REPORT_ZERO_EQUITY_BASED_INCOME_THROUGHOUT": {
            "countries": zero_equity,
            "quarters_each": {c: len(panel_s[c]) for c in zero_equity},
            "finding": "Kuwait reports 0.000 equity-based financing income in all 12 of its "
                       "quarters and Palestine in all 21 of its. Not small -- exactly zero, "
                       "in every quarter, for six years. Their entire reported financing "
                       "income is sales-based and lease-based.",
            "why_this_matters_more_than_the_score": "The variable on which the risk-sharing "
                       "claim rests is not merely weak in these systems; on the IFSB's own "
                       "returns it does not exist. This is a measurement of what is actually "
                       "booked, made by national supervisors, not a model output.",
            "consequence_for_panel_S": "33 of the 65 country-quarters carry a constant zero, "
                       "so no median split is possible for those two countries and panel S "
                       "is effectively Bangladesh and Turkey alone.",
        },
        "D3_the_primary_variable_performed_at_the_permutation_mean": {
            "real": n_rs, "permutation_mean": round(sum(perm_counts) / len(perm_counts), 3),
            "note": "The real loss-absorbing funding share put 3 of 6 countries in the "
                    "risk-sharing direction. Shuffling that same variable within country "
                    "put 3.06 of 6 there on average. The measured variable performed at "
                    "the noise mean, not merely below the 90th-percentile bar. That is a "
                    "cleaner null than a near miss would have been.",
        },
        "D4_what_this_does_and_does_not_show": {
            "does_not": "It does NOT show that loss-absorbing funding fails to reduce "
                        "fragility. Six national aggregates over 25 quarters cannot detect "
                        "a bank-level mechanism, and provisioning policy is set by "
                        "supervisors whose rules differ across these six systems.",
            "does": "It shows that at the resolution the IFSB publishes, no such signal is "
                    "visible, and that in two of four systems the asset-side risk-sharing "
                    "line is empty. Both are facts a proponent has to answer.",
        },
    }

    res = {
        "post_run_disclosures": disclosures,
        "primary_verdict": "F3 MISSED, 3 of 6. F4 MISSED against its own permutation null "
                           "at the null's mean. On this panel the loss-absorbing funding "
                           "share carries no visible information about realised "
                           "non-performing-financing provisioning.",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates,
        "gates_not_met": notmet,
        "panel_P": {"n": sum(comp_p.values()), "composition": comp_p,
                    "rs": "BS13_010/BS01 (PSIA share of balance sheet)",
                    "prov": "IS12_010/BS03"},
        "panel_S": {"n": sum(comp_s.values()), "composition": comp_s,
                    "rs": "IS01_010_030/(sales+lease+equity income)"},
        "within_country_rs_iqr": iqrs,
        "directions_panel_P": _fmt(dirs_p),
        "directions_panel_S": _fmt(dirs_s),
        "countries_with_no_usable_split": sorted(
            [c for c, v in dirs_p.items() if v["sign"] is None]
            + [c + " (panel S)" for c, v in dirs_s.items() if v["sign"] is None]),
        "countries_in_risk_sharing_direction": {"panel_P": n_rs, "of": len(dirs_p),
                                                "panel_S": n_rs_s, "of_S": len(dirs_s)},
        "placebo": {"BS04_interbank_share": n_bs04, "permutation_p90": p90,
                    "permutation_mean": round(sum(perm_counts) / len(perm_counts), 3),
                    "permutation_max": max(perm_counts), "seed": SEED},
        "leave_one_out": loo,
        "no_inferential_statistics": "n=117 country-quarters from 6 systems, serially "
                                     "dependent within country and not a sample of any "
                                     "population. Counts and directions only.",
        "historical_narrative_note": "The window spans COVID and several currency crises. "
                                     "Any account of why a country moved as it did is "
                                     "narrative, is Layer 3, and scores nothing.",
    }
    with open(os.path.join(HERE, "results_ifsb.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "countries_in_risk_sharing_direction",
                       "directions_panel_P", "placebo")}, indent=2))


if __name__ == "__main__":
    main()
