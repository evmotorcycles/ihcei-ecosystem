"""
allometry.py -- runs the pre-registered Tusko scaling test.

Spec 6666f1a958139c6b661b6df61b42c5c2863d4bd7001ab60aa6599b03d8c32710, locked before
this file was written.

Nothing here is simulated. Every tau_v and star count is a recorded observation about a
real public GitHub repository, collected earlier in this programme and hash-pinned.

Two requested arms are BLOCKED at the egress gateway and are recorded as blocked, not
substituted. See G7 and G8.
"""
import csv
import hashlib
import json
import math
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "data", "github", "govphys_quadratic_results.csv")
LOCKED = "6666f1a958139c6b661b6df61b42c5c2863d4bd7001ab60aa6599b03d8c32710"

SPEC = json.load(open(os.path.join(HERE, "prereg", "allometry_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

SHAPE = SPEC["data_provenance"]["declared_shape_before_analysis"]
G2_MIN_PER_DECADE = 20
G3_RATIO = 2.0
G4_MARGIN = 0.02
G5_FACTOR2 = 0.301029995663981   # log10(2)
SEED = 20260801
CALIB_DECADES, TARGET_DECADE = (1, 2), 5
FIT_DECADES, HELDOUT_DECADES = (2, 3, 4), (1, 5)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load():
    got = sha256(CSV)
    if got != SPEC["data_provenance"]["sha256"]:
        raise SystemExit("DATA CHANGED: %s" % got)
    rows = list(csv.DictReader(open(CSV)))
    measured = []
    for r in rows:
        if r["tau_v_imputed"] != "0":
            continue
        u, t = int(r["stars"]), float(r["tau_v"])
        if u <= 0 or t <= 0:
            continue
        measured.append({"repo": r["repo"], "U": u, "tau": t,
                         "decade": int(math.floor(math.log10(u)))})
    return len(rows), measured


def ols_loglog(rows):
    """alpha, c from least squares of log10(tau) on log10(U)."""
    xs = [math.log10(r["U"]) for r in rows]
    ys = [math.log10(r["tau"]) for r in rows]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    alpha = sxy / sxx
    return alpha, my - alpha * mx


def dex(pred, rows):
    """median |log10(predicted / actual)|. One dex is a factor of ten."""
    return statistics.median(abs(math.log10(pred(r["U"]) / r["tau"])) for r in rows)


def three_models(calib):
    k = statistics.median(r["tau"] / r["U"] for r in calib)
    alpha, c = ols_loglog(calib)
    const = statistics.median(r["tau"] for r in calib)
    return ({"linear": lambda u: k * u,
             "power": lambda u: (10 ** c) * (u ** alpha),
             "constant": lambda u: const},
            {"k": k, "alpha": alpha, "c": c, "constant": const})


def main():
    n_total, m = load()
    by_dec = {}
    for r in m:
        by_dec.setdefault(r["decade"], []).append(r)
    counts = {"1e%d" % d: len(v) for d, v in sorted(by_dec.items())}

    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    # ---- G1 integrity -------------------------------------------------------
    stars = [r["U"] for r in m]
    g1 = (n_total == SHAPE["rows_total"] and len(m) == SHAPE["rows_measured"]
          and min(stars) == SHAPE["stars_min"] and max(stars) == SHAPE["stars_max"]
          and counts == SHAPE["measured_rows_per_star_decade"])
    gate("G1_data_integrity", g1,
         "%d rows, %d measured, stars %d..%d, per-decade %s"
         % (n_total, len(m), min(stars), max(stars), counts))

    # ---- G2 populated across scale -----------------------------------------
    worst = min(counts.values())
    gate("G2_the_failing_region_is_populated_across_scale", worst >= G2_MIN_PER_DECADE,
         "smallest decade carries %d measured repositories (needs >= %d); %s"
         % (worst, G2_MIN_PER_DECADE, counts))

    # ---- G3 the Tusko gate --------------------------------------------------
    calib = [r for r in m if r["decade"] in CALIB_DECADES]
    target = by_dec[TARGET_DECADE]
    models, params = three_models(calib)
    d_lin, d_pow, d_con = (dex(models["linear"], target), dex(models["power"], target),
                           dex(models["constant"], target))
    ratio = d_lin / d_pow
    gate("G3_THE_TUSKO_GATE", ratio >= G3_RATIO,
         "calibrated on decades 1e1+1e2 (n=%d), extrapolated to 1e5 (n=%d). "
         "median dex: linear %.3f, power %.3f, constant %.3f. ratio linear/power = %.2f "
         "(needs >= %.1f)" % (len(calib), len(target), d_lin, d_pow, d_con, ratio, G3_RATIO))

    # ---- G4 cross-validated ablation ---------------------------------------
    rng = random.Random(SEED)
    shuffled = list(m)
    rng.shuffle(shuffled)
    folds = [shuffled[i::5] for i in range(5)]
    pow_dex, con_dex = [], []
    for i in range(5):
        test = folds[i]
        train = [r for j, f in enumerate(folds) if j != i for r in f]
        mods, _ = three_models(train)
        pow_dex.append(dex(mods["power"], test))
        con_dex.append(dex(mods["constant"], test))
    mp, mc = statistics.fmean(pow_dex), statistics.fmean(con_dex)
    gate("G4_the_power_law_beats_a_constant_under_cross_validation", mp < mc - G4_MARGIN,
         "5-fold CV seed %d: mean held-out dex power %.4f vs constant %.4f, "
         "improvement %+.4f (needs > %.2f)" % (SEED, mp, mc, mc - mp, G4_MARGIN))

    # ---- G5 held-out scale invariance --------------------------------------
    fit_rows = [r for r in m if r["decade"] in FIT_DECADES]
    a_mid, _ = ols_loglog(fit_rows)
    norm_med, raw_med = {}, {}
    for d in HELDOUT_DECADES:
        norm_med[d] = statistics.median(r["tau"] / (r["U"] ** a_mid) for r in by_dec[d])
        raw_med[d] = statistics.median(r["tau"] for r in by_dec[d])
    lo, hi = HELDOUT_DECADES
    gap_norm = abs(math.log10(norm_med[hi] / norm_med[lo]))
    gap_raw = abs(math.log10(raw_med[hi] / raw_med[lo]))
    g5 = gap_norm <= G5_FACTOR2 and gap_raw > G5_FACTOR2
    gate("G5_HELD_OUT_SCALE_INVARIANCE", g5,
         "alpha fitted on decades 1e2/1e3/1e4 = %.4f. held-out 1e1 vs 1e5: "
         "normalised medians %.4g vs %.4g, gap %.3f dex (needs <= %.3f); "
         "raw medians %.3f vs %.3f, gap %.3f dex (needs > %.3f)"
         % (a_mid, norm_med[lo], norm_med[hi], gap_norm, G5_FACTOR2,
            raw_med[lo], raw_med[hi], gap_raw, G5_FACTOR2))

    # ---- G6 descriptive, scores nothing ------------------------------------
    a_all, c_all = ols_loglog(m)
    decade_medians = {"1e%d" % d: round(statistics.median(r["tau"] for r in v), 3)
                      for d, v in sorted(by_dec.items())}
    gates.append({
        "id": "G6_the_exponent_itself", "met": None, "weight": "descriptive",
        "detail": "alpha over all %d measured rows = %+.4f, intercept %.4f. Per-decade "
                  "median tau_v: %s. SCORES NOTHING -- these medians were inspected "
                  "before the spec was locked, as disclosed in the pre-registration, so "
                  "a gate on the exponent's sign could not have failed."
                  % (len(m), a_all, c_all, decade_medians)})

    for gid, host in (("G7_hugging_face_model_lineage_arm", "huggingface.co:443"),
                      ("G8_biological_allometry_arm", "genomics.senescence.info:443")):
        gates.append({"id": gid, "met": None, "weight": "excluded",
                      "detail": "BLOCKED: %s answered 403 to CONNECT at the egress "
                                "gateway. BLOCKED is not REFUTED and is not "
                                "UNTESTABLE-HERE -- the data exists and the test is "
                                "well posed; this session cannot reach it. No "
                                "substitute dataset was used." % host})

    # ---- POST-RUN DISCLOSURES. No gate re-scored, no threshold moved. -------
    at_cap = [r["repo"] for r in m if r["tau"] >= 365.0]
    sub_hour = [r["repo"] for r in m if r["tau"] < 0.01]
    trimmed = [r for r in m if 0.01 <= r["tau"] < 365.0]
    a_trim, _ = ols_loglog(trimmed)
    disclosures = {
        "D1_censoring_and_bot_closures_retained": {
            "at_the_365_day_ceiling": len(at_cap), "repos": at_cap,
            "below_0_01_days": len(sub_hour), "repos_fast": sub_hour,
            "note": "The 365.0 values are a collection ceiling, not observations, and "
                    "the sub-15-minute values are almost certainly automated closure. "
                    "Both groups are RETAINED because the spec said so and removing them "
                    "after seeing results would be a threshold move.",
            "effect_if_they_were_dropped": "alpha would be %+.4f instead of %+.4f, a "
                    "change of %.4f. Reported so the reader can see the sensitivity "
                    "without the gate being re-scored on it."
                    % (a_trim, a_all, abs(a_trim - a_all)),
        },
        "D2_what_the_sign_of_alpha_means": {
            "alpha": round(a_all, 4),
            "reading": "alpha is negative, so LARGER repositories close issues FASTER. "
                       "That inverts the naive reading of the analogy, in which bigger "
                       "systems are assumed slower and more sclerotic.",
            "the_biological_parallel_is_LAYER_3_AND_SCORES_NOTHING": "Kleiber's law also "
                       "gives a RATE that falls with mass -- heart rate as m^(-1/4). A "
                       "latency falling with capacity is therefore the analogous "
                       "direction rather than a contradiction. This sentence is an "
                       "interpretation. It is not evidence and nothing is inferred from it.",
            "no_biological_confirmation_is_claimed": True,
        },
        "D5_THE_CALIBRATION_SLOPE_HAS_THE_OPPOSITE_SIGN_TO_THE_GLOBAL_SLOPE": {
            "alpha_fitted_on_the_small_decades_1e1_1e2": round(params["alpha"], 4),
            "alpha_over_all_866_measured_rows": round(a_all, 4),
            "finding": "Fitting the power law on the SMALL end alone gives %+.4f. Fitting "
                       "it on the whole range gives %+.4f. THE SIGN FLIPS. At small scale "
                       "latency appears to RISE with capacity; across the full range it "
                       "FALLS." % (params["alpha"], a_all),
            "why_this_is_the_sharpest_form_of_the_Tusko_error": "The 1962 error was using "
                       "the wrong EXPONENT, 1 instead of a fractional one. This is worse: "
                       "the small-scale data supports the wrong DIRECTION. Any law fitted "
                       "at small scale and extrapolated is not merely mis-scaled, it "
                       "points the wrong way, which is why the power law extrapolates to a "
                       "42-fold error while simply assuming no change errs by 8-fold.",
        },
        "D6_THE_CONSTANT_MODEL_WINS_BOTH_COMPARISONS": {
            "extrapolation_fold_errors": {"linear": round(10 ** d_lin, 1),
                                          "power": round(10 ** d_pow, 2),
                                          "constant": round(10 ** d_con, 2)},
            "cross_validated_mean_dex": {"power": round(mp, 4), "constant": round(mc, 4)},
            "stated_first_as_the_spec_required": "The locked spec said that if the constant "
                       "model beat the power law this must be stated first. IT DID, in both "
                       "comparisons. On extrapolation to the top decade the constant errs "
                       "8.3-fold against the power law's 42-fold, and under 5-fold "
                       "cross-validation the constant's mean held-out dex is LOWER. G4 is "
                       "recorded as failed on exactly this.",
            "the_honest_conclusion": "Across 866 real repositories spanning 3.65 decades, "
                       "capacity does not predict enforcement latency well enough to "
                       "extrapolate with. The correct operational lesson from Tusko here "
                       "is NOT 'use a power law instead of a linear rule'. It is 'a rule "
                       "calibrated at one scale should not be extrapolated to another at "
                       "all'. The linear rule is catastrophic, the power law is bad, and "
                       "assuming nothing changes is merely poor.",
        },
        "D7_G5_flattened_the_gap_but_not_to_invariance": {
            "raw_gap_dex": round(gap_raw, 4), "normalised_gap_dex": round(gap_norm, 4),
            "note": "Normalising by the held-out exponent cut the 1e1-vs-1e5 gap from "
                    "%.3f dex to %.3f dex -- a real reduction, from a 12-fold difference "
                    "to a 4-fold one. But the locked bar was a factor of 2 and 4-fold "
                    "misses it. There is no scale-invariant latency constant here. The "
                    "'one billion heartbeats' structure does not appear in this substrate "
                    "at this range, and the partial flattening is reported without credit."
                    % (gap_raw, gap_norm),
        },
        "D3_what_stars_are_not": {
            "note": "Stars are not a cause of latency. Both plausibly follow from project "
                    "maturity, funding and maintainer count, none of which are in this "
                    "cohort. Every result here is an association across scale, not a "
                    "mechanism, and no intervention is implied.",
        },
        "D4_the_range_actually_covered": {
            "stars_min": min(stars), "stars_max": max(stars),
            "note": "The design asked for 1 star upward. This session cannot sample new "
                    "repositories -- GitHub endpoints outside session scope answer 403 -- "
                    "so the floor is 99. Nothing here extrapolates below 99 or above "
                    "442,738, and the Tusko lesson applies to this result too.",
        },
    }

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates,
        "gates_not_met": notmet,
        "n_rows_total": n_total, "n_measured": len(m), "n_imputed_excluded": n_total - len(m),
        "stars_range": [min(stars), max(stars)],
        "orders_of_magnitude": round(math.log10(max(stars) / min(stars)), 3),
        "measured_per_decade": counts,
        "tusko_extrapolation": {
            "calibrated_on_decades": list(CALIB_DECADES), "n_calibration": len(calib),
            "extrapolated_to_decade": TARGET_DECADE, "n_target": len(target),
            "median_dex_linear": round(d_lin, 4),
            "median_dex_power": round(d_pow, 4),
            "median_dex_constant": round(d_con, 4),
            "linear_over_power": round(ratio, 3),
            "linear_fold_error": round(10 ** d_lin, 1),
            "power_fold_error": round(10 ** d_pow, 2),
            "constant_fold_error": round(10 ** d_con, 2),
            "calibration_params": {k: round(v, 6) for k, v in params.items()},
        },
        "cross_validation": {"seed": SEED, "folds": 5,
                             "power_dex_per_fold": [round(x, 4) for x in pow_dex],
                             "constant_dex_per_fold": [round(x, 4) for x in con_dex],
                             "mean_power": round(mp, 4), "mean_constant": round(mc, 4)},
        "held_out_invariance": {"alpha_from_middle_decades": round(a_mid, 4),
                                "normalised_medians": {"1e%d" % d: norm_med[d]
                                                       for d in HELDOUT_DECADES},
                                "gap_normalised_dex": round(gap_norm, 4),
                                "raw_medians": {"1e%d" % d: round(raw_med[d], 3)
                                                for d in HELDOUT_DECADES},
                                "gap_raw_dex": round(gap_raw, 4)},
        "alpha_all_measured": round(a_all, 4),
        "decade_medians_tau_v": decade_medians,
        "blocked_arms": {"huggingface.co": "403 at egress gateway",
                         "genomics.senescence.info": "403 at egress gateway",
                         "github_repos_outside_session_scope": "403, no new sampling"},
        "simulated_quantities": 0,
        "post_run_disclosures": disclosures,
        "layer_3_boundary": "Tusko and Kleiber generated this hypothesis and supplied its "
                            "vocabulary. Neither is evidence about software. No biological "
                            "law is confirmed, tested or invoked as support anywhere in "
                            "this file.",
    }
    with open(os.path.join(HERE, "results_allometry.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "tusko_extrapolation", "cross_validation",
                       "held_out_invariance", "alpha_all_measured", "decade_medians_tau_v")},
                     indent=2))


if __name__ == "__main__":
    main()
