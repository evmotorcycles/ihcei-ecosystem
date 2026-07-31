"""
dcm.py -- the Discriminating Capacity Model, run against its pre-registration.

Spec 3a33d53e178b9c6f9178a77fe9d2e60780eff74d63c5606878b8bf61f9947ffe, locked before
this file was written.

    DELTA = V * I * C

    V   1 - modal fraction of the outcome      the outcome never moves
    I   4 * p * (1 - p) on the group split     no populated failing region
    C   distinct outcome values / n            administrative, not measured

None of the three reads the association between group and outcome. They are functions of
the outcome's value distribution and the group sizes only.

The 400 primary sub-datasets contain real rows drawn from two real open-source substrates,
and detect only relationships genuinely present in those substrates. Nothing is simulated.
"""
import csv
import hashlib
import json
import math
import os
import random
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "3a33d53e178b9c6f9178a77fe9d2e60780eff74d63c5606878b8bf61f9947ffe"

SPEC = json.load(open(os.path.join(HERE, "prereg", "dcm_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

PROV = SPEC["data_provenance"]
NS = [20, 40, 80, 160, 320]
PS = [0.05, 0.15, 0.30, 0.50]
REPS, SEED, N_PERM = 10, 20260801, 200
K2_LO, K2_HI = 0.10, 0.90
K3_MIN, K4_MARGIN, K5_MARGIN, K6_MIN = 0.70, 0.05, 0.03, 0.65
TOO_PERFECT = 0.95


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- the model
def V_variation(ys):
    """1 - modal fraction. Zero when the outcome never moves."""
    return 1.0 - Counter(ys).most_common(1)[0][1] / len(ys)


def I_incidence(labels):
    """4p(1-p) on the group split. Invariant I2, made continuous."""
    p = min(sum(labels), len(labels) - sum(labels)) / len(labels)
    return 4.0 * p * (1.0 - p)


def C_coupling(ys):
    """distinct / n. Near zero when the outcome is a handful of admin values."""
    return min(1.0, len(set(ys)) / len(ys))


def delta(ys, labels):
    v, i, c = V_variation(ys), I_incidence(labels), C_coupling(ys)
    return v * i * c, v, i, c


# ------------------------------------------------------------- the harness
def detected(ys, labels, rng):
    """Permutation test on the difference in group medians. Real relationship or none."""
    a = [y for y, g in zip(ys, labels) if g]
    b = [y for y, g in zip(ys, labels) if not g]
    if not a or not b:
        return False, 0.0
    obs = abs(statistics.median(a) - statistics.median(b))
    lab = list(labels)
    null = []
    for _ in range(N_PERM):
        rng.shuffle(lab)
        aa = [y for y, g in zip(ys, lab) if g]
        bb = [y for y, g in zip(ys, lab) if not g]
        null.append(abs(statistics.median(aa) - statistics.median(bb)) if aa and bb else 0.0)
    null.sort()
    return obs > null[int(0.95 * (len(null) - 1))], obs


def auc(scores, labels):
    """Mann-Whitney U / (n_pos * n_neg), ties take the mean rank."""
    pairs = sorted(zip(scores, labels))
    ranks, i = [0.0] * len(pairs), 0
    while i < len(pairs):
        j = i
        while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        mr = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = mr
        i = j + 1
    npos = sum(1 for _, y in pairs if y)
    nneg = len(pairs) - npos
    if npos == 0 or nneg == 0:
        return None
    rsum = sum(r for r, (_, y) in zip(ranks, pairs) if y)
    return (rsum - npos * (npos + 1) / 2.0) / (npos * nneg)


def load():
    for key in ("substrate_A_github", "substrate_B_pypi"):
        p = os.path.join(ROOT, PROV[key]["file"])
        got = sha256(p)
        if got != PROV[key]["sha256"]:
            raise SystemExit("DATA CHANGED: %s %s" % (p, got))

    gh = []
    for r in csv.DictReader(open(os.path.join(ROOT, PROV["substrate_A_github"]["file"]))):
        if r["tau_v_imputed"] != "0":
            continue
        gh.append({"y": float(r["tau_v"]), "g": int(r["E"])})

    rows = list(csv.DictReader(open(os.path.join(ROOT, PROV["substrate_B_pypi"]["file"]))))
    med = statistics.median(float(r["E_indegree"]) for r in rows)
    py = [{"y": float(r["D_dec_pin_clarity"]), "g": int(float(r["E_indegree"]) > med)}
          for r in rows]
    return {"github": gh, "pypi": py}


def draw(pool, n, p, rng):
    """n real rows with a target minority proportion p. Real rows only."""
    pos = [r for r in pool if r["g"]]
    neg = [r for r in pool if not r["g"]]
    k = max(1, min(n - 1, int(round(n * p))))
    if len(pos) < k or len(neg) < n - k:
        return None
    return rng.sample(pos, k) + rng.sample(neg, n - k)


def quantise(ys, levels):
    """Controlled degradation of REAL data: coarsen the RECORDING, not the relationship."""
    lo, hi = min(ys), max(ys)
    if hi == lo:
        return list(ys)
    step = (hi - lo) / levels
    return [lo + step * min(levels - 1, int((y - lo) / step)) for y in ys]


def run_grid(pools, levels=None):
    rng = random.Random(SEED if levels is None else SEED + levels)
    out = []
    for sub, pool in pools.items():
        for n in NS:
            for p in PS:
                for rep in range(REPS):
                    d = draw(pool, n, p, rng)
                    if d is None:
                        continue
                    ys = [r["y"] for r in d]
                    if levels is not None:
                        ys = quantise(ys, levels)
                    labels = [r["g"] for r in d]
                    dl, v, i, c = delta(ys, labels)
                    det, obs = detected(ys, labels, rng)
                    out.append({"substrate": sub, "n": n, "p": p, "rep": rep,
                                "delta": dl, "V": v, "I": i, "C": c,
                                "detected": det, "observed_diff": obs})
    return out


def main():
    pools = load()
    nat = run_grid(pools)
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    # ---- K1 integrity -------------------------------------------------------
    ranges_ok = all(0.0 <= r[k] <= 1.0 for r in nat for k in ("delta", "V", "I", "C"))
    k1 = (len(pools["github"]) == 866 and len(pools["pypi"]) == 540
          and len(nat) == len(NS) * len(PS) * REPS * 2 and ranges_ok)
    gate("K1_integrity", k1,
         "github %d rows, pypi %d rows, %d natural sub-datasets, all V/I/C/DELTA in [0,1]=%s"
         % (len(pools["github"]), len(pools["pypi"]), len(nat), ranges_ok))

    # ---- K2 populated failing region ---------------------------------------
    labels = [r["detected"] for r in nat]
    rate = sum(labels) / len(labels)
    gate("K2_the_failing_region_is_populated", K2_LO <= rate <= K2_HI,
         "%d of %d natural sub-datasets detected = %.1f%% (band %.0f-%.0f%%)"
         % (sum(labels), len(labels), 100 * rate, 100 * K2_LO, 100 * K2_HI))

    # ---- K3 primary ---------------------------------------------------------
    a_delta = auc([r["delta"] for r in nat], labels)
    gate("K3_DELTA_PREDICTS_DETECTION", a_delta is not None and a_delta >= K3_MIN,
         "AUC(DELTA) = %.4f (needs >= %.2f)" % (a_delta or float("nan"), K3_MIN))

    # ---- K4 the ablation ----------------------------------------------------
    a_n = auc([r["n"] for r in nat], labels)
    gate("K4_DELTA_BEATS_SAMPLE_SIZE", a_delta - a_n >= K4_MARGIN,
         "AUC(DELTA) %.4f vs AUC(n) %.4f, delta %+.4f (needs >= %.2f)"
         % (a_delta, a_n, a_delta - a_n, K4_MARGIN))

    # ---- K5 multiplicativity ------------------------------------------------
    singles = {k: auc([r[k] for r in nat], labels) for k in ("V", "I", "C")}
    best_k = max(singles, key=lambda k: singles[k])
    gate("K5_THE_PRODUCT_BEATS_ITS_BEST_SINGLE_FACTOR",
         a_delta - singles[best_k] >= K5_MARGIN,
         "AUC(DELTA) %.4f vs best single factor %s %.4f, delta %+.4f (needs >= %.2f). "
         "all singles: %s" % (a_delta, best_k, singles[best_k],
                              a_delta - singles[best_k], K5_MARGIN,
                              {k: round(v, 4) for k, v in singles.items()}))

    # ---- K6 within each substrate ------------------------------------------
    per_sub = {}
    for sub in ("github", "pypi"):
        s = [r for r in nat if r["substrate"] == sub]
        per_sub[sub] = auc([r["delta"] for r in s], [r["detected"] for r in s])
    ok6 = all(v is not None and v >= K6_MIN for v in per_sub.values())
    gate("K6_IT_HOLDS_ON_BOTH_SUBSTRATES_SEPARATELY", ok6,
         "within-substrate AUC(DELTA): %s (each needs >= %.2f)"
         % ({k: (round(v, 4) if v is not None else None) for k, v in per_sub.items()}, K6_MIN))

    gates.append({"id": "K7_the_C_factor_on_longitudinal_data", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. The sharpest coupling failure -- successive "
                            "outcome values following a fixed multiplicative rule -- needs "
                            "panel data. Both substrates are cross-sectional and the "
                            "distinct-value proxy for C is a weaker instrument."})

    # ---- secondary degraded arm, scores nothing ----------------------------
    degraded = {}
    for lv in (10, 3):
        g = run_grid(pools, levels=lv)
        gl = [r["detected"] for r in g]
        degraded["quantised_to_%d_levels" % lv] = {
            "n_subdatasets": len(g), "detection_rate": round(sum(gl) / len(gl), 4),
            "auc_delta": round(auc([r["delta"] for r in g], gl), 4) if 0 < sum(gl) < len(gl) else None,
            "mean_C": round(statistics.fmean(r["C"] for r in g), 4)}
    gates.append({"id": "K8_degraded_recording_arm", "met": None, "weight": "excluded",
                  "detail": "CONTROLLED DEGRADATION OF REAL DATA, not simulation of a "
                            "mechanism: the relationship is untouched and only the "
                            "recording is coarsened. Scores nothing, by the locked spec, "
                            "so that no gate rests on a manipulation. %s" % degraded})

    # ---- POST-RUN DISCLOSURES ----------------------------------------------
    by_sub = {}
    for sub in ("github", "pypi"):
        s = [r for r in nat if r["substrate"] == sub]
        by_sub[sub] = {"n": len(s),
                       "detection_rate": round(sum(r["detected"] for r in s) / len(s), 4),
                       "mean_V": round(statistics.fmean(r["V"] for r in s), 4),
                       "mean_I": round(statistics.fmean(r["I"] for r in s), 4),
                       "mean_C": round(statistics.fmean(r["C"] for r in s), 4),
                       "mean_delta": round(statistics.fmean(r["delta"] for r in s), 4)}
    disclosures = {
        "D1_what_a_low_DELTA_does_NOT_mean": {
            "statement": "A low DELTA says THIS DATASET CANNOT SETTLE THIS QUESTION. It "
                         "never says the claim is false. Using DELTA to dismiss a claim "
                         "would invert the model's entire purpose, which is to stop nulls "
                         "being read as refutations.",
            "worked_example_from_this_programme": "The contract schedules scored 3/6 and "
                         "the outcome panels 2/5. Neither result is evidence that Islamic "
                         "contracts are debt. Both are evidence that the supplied data "
                         "could not tell the difference.",
        },
        "D2_V_and_C_are_correlated_by_construction": {
            "note": "Both are computed from the outcome's value distribution, so a "
                    "degenerate outcome depresses both. They are not independent channels "
                    "and DELTA is not a variance decomposition. K5 is the gate that tests "
                    "whether combining them earns anything over the best single one.",
        },
        "D3_per_substrate_profile": by_sub,
        "D5_THE_POOLED_AUC_IS_PARTLY_SUBSTRATE_SEPARATION": {
            "pooled": round(a_delta, 4),
            "within_github": round(per_sub["github"], 4),
            "within_pypi": round(per_sub["pypi"], 4),
            "note": "The pooled 0.9442 sits just under the 0.95 too-perfect trigger and "
                    "should NOT be read as the model's accuracy. GitHub is naturally clean "
                    "and PyPI naturally degenerate, so a large part of the pooled "
                    "separation is DELTA acting as a substrate label -- exactly what K6 "
                    "was written to catch. THE HONEST FIGURES ARE THE WITHIN-SUBSTRATE "
                    "ONES: 0.8754 and 0.6690. The second of those clears its 0.65 bar by "
                    "0.019 and is the weakest number in the run.",
        },
        "D6_K5_FAILED_SO_THE_MULTIPLICATIVE_CLAIM_IS_NOT_EARNED": {
            "delta_auc": round(a_delta, 4),
            "best_single_factor": best_k,
            "best_single_auc": round(singles[best_k], 4),
            "improvement_from_multiplying": round(a_delta - singles[best_k], 4),
            "locked_bar": K5_MARGIN,
            "what_this_means": "The pre-registration named multiplicativity as 'the "
                    "substantive and falsifiable content of the model'. It was tested and "
                    "IT DID NOT EARN ITS KEEP: V alone scores %.4f against the product's "
                    "%.4f, an improvement of %.4f against a locked bar of %.2f. On this "
                    "evidence a ONE-FACTOR model -- does the outcome actually move? -- "
                    "does nearly all the work."
                    % (singles[best_k], a_delta, a_delta - singles[best_k], K5_MARGIN),
            "what_is_NOT_being_done": "The model is not being redefined to fit this "
                    "result, and DELTA is not being quietly replaced by V. DCM is reported "
                    "as specified, with K5 recorded as failed. Rewriting the formula after "
                    "seeing the AUC is the immunisation move the pre-registration exists "
                    "to prevent.",
            "the_honest_caveat_in_the_models_favour": "V and C were pre-disclosed as "
                    "correlated by construction, both being functions of the outcome's "
                    "value distribution. Two substrates in which they move together cannot "
                    "separate them. A substrate where the outcome varies widely but takes "
                    "few distinct values -- high V, low C -- would decouple them, and none "
                    "was available here. That is a reason the test is weak on this point, "
                    "not a reason to discount the result.",
            "what_the_next_spec_must_do": "Either find a substrate that decouples V from "
                    "C, or drop to the one-factor model and pre-register it against this "
                    "same harness before claiming anything for it.",
        },
        "D7_K6_PASSED_ON_THE_PYPI_SIDE_ON_FOUR_EVENTS": {
            "pypi_detection_rate": by_sub["pypi"]["detection_rate"],
            "pypi_detections": int(round(by_sub["pypi"]["detection_rate"] * 200)),
            "pypi_subdatasets": 200,
            "pypi_auc": round(per_sub["pypi"], 4),
            "bar": K6_MIN,
            "note": "K6 is recorded as MET because the locked rule was met. It should not "
                    "be read as support. Only 4 of 200 PyPI sub-datasets detected "
                    "anything, so the 0.669 AUC rests on 4 positive cases and clears its "
                    "0.65 bar by 0.019. THAT IS NOT A RESULT. The gate stands as passed "
                    "because the threshold was locked and is not being moved, and the "
                    "weakness is recorded here rather than absorbed into the score.",
            "why_pypi_detects_almost_nothing": "Its outcome, pin clarity, takes 26 distinct "
                    "values across 540 packages with 49 percent sharing one value. Mean C "
                    "in the PyPI draws is 0.125 against GitHub's 0.999. That is the "
                    "model's own prediction about this substrate coming true -- which is "
                    "consistent with DCM but is NOT independent evidence for it, because "
                    "the same degeneracy drives both DELTA and the non-detection.",
        },
        "D8_the_degraded_arm_directionally_agrees_but_is_underpowered": {
            "detection_rate_natural": round(rate, 4),
            "detection_rate_quantised_10": degraded["quantised_to_10_levels"]["detection_rate"],
            "detection_rate_quantised_3": degraded["quantised_to_3_levels"]["detection_rate"],
            "note": "Coarsening the RECORDING while leaving the relationship untouched "
                    "drops detection from 29.0 percent to 5.5 percent to 0.5 percent. That "
                    "is the model's central claim visible directly: the effect was still "
                    "there and the data stopped being able to see it. But the quantised-3 "
                    "arm carries 2 detections in 400, so its AUC of 0.9322 is meaningless "
                    "and is not quoted as support. The arm scores nothing by the locked "
                    "spec and is reported for the detection-rate collapse only.",
        },
        "D4_the_relationship_being_detected_is_real": {
            "github": "failed repositories close issues more slowly -- established "
                      "independently in this programme at 50.6 vs 19.8 days and surviving "
                      "a within-decade check at 2.7x.",
            "pypi": "widely-depended-on packages versus the rest, on pin clarity. Whether "
                    "this relationship is strong is NOT assumed; the harness detects "
                    "whatever is there, and a weak true effect is a legitimate reason for "
                    "low detection.",
        },
    }

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "DCM - the Discriminating Capacity Model",
        "formula": "DELTA = V * I * C",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates,
        "gates_not_met": notmet,
        "n_natural_subdatasets": len(nat),
        "detection_rate": round(rate, 4),
        "auc": {"delta": round(a_delta, 4), "n_rows": round(a_n, 4),
                **{k: round(v, 4) for k, v in singles.items()}},
        "auc_within_substrate": {k: (round(v, 4) if v is not None else None)
                                 for k, v in per_sub.items()},
        "best_single_factor": best_k,
        "degraded_arm_scores_nothing": degraded,
        "too_perfect_flag": [k for k, v in {"delta": a_delta}.items() if v > TOO_PERFECT],
        "simulated_mechanisms": 0,
        "post_run_disclosures": disclosures,
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "K3 MET at AUC %.4f. " % a_delta if a_delta >= K3_MIN else
        "K3 MISSED at AUC %.4f against a locked 0.70. " % a_delta) + (
        "DELTA %s sample size (%.4f vs %.4f) and %s its best single factor %s (%.4f)."
        % ("beat" if a_delta - a_n >= K4_MARGIN else "did NOT beat", a_delta, a_n,
           "beat" if a_delta - singles[best_k] >= K5_MARGIN else "did NOT beat",
           best_k, singles[best_k]))
    with open(os.path.join(HERE, "results_dcm.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "detection_rate", "auc",
                       "auc_within_substrate", "primary_verdict")}, indent=2))


if __name__ == "__main__":
    main()
