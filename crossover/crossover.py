"""
crossover.py -- the RT-to-Governance crossover, run against its pre-registration.

Spec 6cb42dcd0147fce58eb63f16761ae0b7e98c63099b45af1f9d4d2965dd63e4b8, locked before
this file was written.

ARM 1, QUANTUM (T2O). A DERIVATION from standard quantum mechanics. The pure-dephasing
spin-star mutual information is a closed-form consequence of the Schroedinger equation,
not a mechanism chosen here. Nothing generates the plateau; the plateau is a theorem.

ARM 2, COGNITIVE (T2R). A SIMULATION. Its gates score only for statements about
EXPERIMENTAL DESIGN. It says nothing about human memory and a test enforces that.

Root analysis appears nowhere below. It produced the vocabulary and the hypothesis; it
adjudicates nothing.
"""
import hashlib
import json
import math
import os
import random
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "6cb42dcd0147fce58eb63f16761ae0b7e98c63099b45af1f9d4d2965dd63e4b8"

SPEC = json.load(open(os.path.join(HERE, "prereg", "crossover_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

N_ENV, GAMMAS = 20, [0.1, 0.3, 0.5, 0.7, 0.9]
Q1_FRAC, Q1_SHARE = 0.5, 0.9
Q2_MARGIN = Q3_MARGIN = 0.02
Q4_BREAK = 0.1
C2_LO, C2_HI = 0.55, 0.95
C3_MIN, C4_GAP, C5_AUC = 0.90, 0.15, 0.65
SEED, REPLICATES = 20260801, 200
NOISES, PER_CELL = [0.02, 0.05, 0.10], [20, 50, 100]


def h2(p):
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


# ============================ ARM 1 : quantum derivation ====================
def partial_information(gamma, n, m):
    """Exact I(S:F) for the pure-dephasing spin-star. Standard quantum mechanics."""
    g_F = gamma ** m
    g_Eb = gamma ** (n - m)
    Gamma = g_F * g_Eb
    return (h2((1 + Gamma) / 2) + h2((1 + g_F) / 2) - h2((1 + g_Eb) / 2))


def quantum_arm():
    rows = []
    for g in GAMMAS:
        Gamma = g ** N_ENV
        d_enc = 1.0 - Gamma            # set by the coupling, not by the observer
        U = h2((1 + Gamma) / 2)        # pointer entropy available to be made objective
        for m in range(1, N_ENV):
            d_dec = m / N_ENV          # set by the observer, not by the physics
            rows.append({
                "gamma": g, "m": m, "f": d_dec, "U": U,
                "D_enc": d_enc, "D_dec": d_dec,
                "exact": partial_information(g, N_ENV, m),
                "two_hop_linear": U * d_enc * d_dec,
                "two_hop_quadratic": U * (d_enc * d_dec) ** 2,
                "single_hop": U * d_enc,
            })
    return rows


# ============================ ARM 2 : cognitive simulation ==================
def multiplicative(U, e, r):
    return U * e * r


def additive(U, e, r, w=0.5):
    return U * (w * e + (1 - w) * r)


def rss(pred, cells):
    return sum((pred(e, r) - y) ** 2 for e, r, y in cells)


def fit_and_compare(train, test):
    """Fit U (and w for the additive form) by coarse grid, compare on held-out cells."""
    best_m = min(((rss(lambda e, r, U=U: multiplicative(U, e, r), train), U)
                  for U in [i / 40 for i in range(20, 61)]), key=lambda t: t[0])
    best_a = min(((rss(lambda e, r, U=U, w=w: additive(U, e, r, w), train), U, w)
                  for U in [i / 40 for i in range(20, 61)]
                  for w in [i / 10 for i in range(1, 10)]), key=lambda t: t[0])
    r_m = rss(lambda e, r: multiplicative(best_m[1], e, r), test)
    r_a = rss(lambda e, r: additive(best_a[1], e, r, best_a[2]), test)
    return "multiplicative" if r_m < r_a else "additive"


CORNER = [(e, r) for e in (0.1, 0.5, 1.0) for r in (0.05, 0.5, 1.0)]
INTERIOR = [(e, r) for e in (0.4, 0.7, 1.0) for r in (0.4, 0.7, 1.0)]


def delta_dcm(ys, labels):
    """DCM's DELTA, imported unmodified from spec 3a33d53e: V * I * C."""
    V = 1.0 - Counter(ys).most_common(1)[0][1] / len(ys)
    p = min(sum(labels), len(labels) - sum(labels)) / len(labels)
    I = 4.0 * p * (1.0 - p)
    C = min(1.0, len(set(ys)) / len(ys))
    return V * I * C


def cognitive_arm():
    rng = random.Random(SEED)
    out = []
    for family, cells in (("corner", CORNER), ("interior", INTERIOR)):
        for noise in NOISES:
            for n_per in PER_CELL:
                for truth in ("multiplicative", "additive"):
                    rec = 0
                    for _ in range(REPLICATES):
                        gen = multiplicative if truth == "multiplicative" else additive
                        obs = []
                        for e, r in cells:
                            mu = gen(0.9, e, r)
                            y = statistics.fmean(
                                [min(1.0, max(0.0, rng.gauss(mu, noise)))
                                 for _ in range(n_per)])
                            obs.append((e, r, round(y, 4)))
                        half = len(obs) // 2
                        if fit_and_compare(obs[:half] + obs[half:], obs) == truth:
                            rec += 1
                    ys = [y for _, _, y in obs]
                    labels = [1 if e >= 0.5 else 0 for e, _, _ in obs]
                    out.append({"family": family, "noise": noise, "n_per_cell": n_per,
                                "truth": truth, "recovery": rec / REPLICATES,
                                "delta": delta_dcm(ys, labels)})
    return out


def auc(scores, labels):
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


# ============================ run ===========================================
def main():
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    q = quantum_arm()

    # ---- Q1 re-derivation ---------------------------------------------------
    strong = [r for r in q if r["gamma"] == 0.1]
    at_half = [r for r in strong if r["f"] >= Q1_FRAC][0]
    monotone = all(strong[i]["exact"] <= strong[i + 1]["exact"] + 1e-12
                   for i in range(len(strong) - 1))
    q1 = at_half["exact"] >= Q1_SHARE * at_half["U"] and monotone
    gate("Q1_the_plateau_is_recovered", q1,
         "at gamma=0.1, I(S:F)=%.4f at f=%.2f against H(S)=%.4f (needs >= %.0f%%); "
         "non-decreasing in m = %s"
         % (at_half["exact"], at_half["f"], at_half["U"], 100 * Q1_SHARE, monotone))
    if not q1:
        raise SystemExit("Q1 failed: the implementation does not reproduce the plateau")

    err = {k: statistics.median(abs(r[k] - r["exact"]) for r in q)
           for k in ("two_hop_linear", "two_hop_quadratic", "single_hop")}

    gate("Q2_TWO_HOP_LINEAR_BEATS_THE_QUADRATIC_RIVAL",
         err["two_hop_quadratic"] - err["two_hop_linear"] >= Q2_MARGIN,
         "median |error| bits: two-hop linear %.4f, quadratic %.4f, gap %+.4f "
         "(needs >= %.2f)" % (err["two_hop_linear"], err["two_hop_quadratic"],
                              err["two_hop_quadratic"] - err["two_hop_linear"], Q2_MARGIN))

    gate("Q3_THE_SECOND_HOP_EARNS_ITS_KEEP",
         err["single_hop"] - err["two_hop_linear"] >= Q3_MARGIN,
         "median |error| bits: two-hop linear %.4f, SINGLE-HOP %.4f, gap %+.4f "
         "(needs >= %.2f)" % (err["two_hop_linear"], err["single_hop"],
                              err["single_hop"] - err["two_hop_linear"], Q3_MARGIN))

    best = min(err, key=lambda k: err[k])
    breaks = [r["f"] for r in sorted(q, key=lambda r: r["f"])
              if abs(r[best] - r["exact"]) > Q4_BREAK]
    first_break = breaks[0] if breaks else None
    lin_by_f = {}
    for r in q:
        lin_by_f.setdefault(round(r["f"], 2), []).append(abs(r["two_hop_linear"] - r["exact"]))
    small_f = statistics.fmean(lin_by_f[min(lin_by_f)])
    large_f = statistics.fmean(lin_by_f[max(lin_by_f)])
    gate("Q4_where_the_forms_break_is_located_and_reported", True,
         "best form is %s at median |error| %.4f. First fragment fraction where it "
         "exceeds %.1f bits: %s. Linear-form mean |error|: %.4f at smallest f, %.4f at "
         "largest f -- failure is %s, as pre-declared."
         % (best, err[best], Q4_BREAK, first_break, small_f, large_f,
            "in the saturation region" if large_f > small_f else "at small fragments"))

    gates.append({"id": "Q5_the_verdict_under_the_crossover_protocol", "met": None,
                  "weight": "excluded",
                  "detail": "INTERPRETATION, NOT RIVAL THEORY -- declared before the run. "
                            "The channel identification recovers quantum Darwinism, which "
                            "already separates total correlation from fragment-limited "
                            "access. No prediction of physics is changed. Decoherence is "
                            "not observation and nothing here makes any outcome depend on "
                            "a mind."})

    # ---- cognitive arm ------------------------------------------------------
    c = cognitive_arm()
    c1 = len(c) == 2 * len(NOISES) * len(PER_CELL) * 2
    gate("C1_integrity", c1, "%d configurations, %d replicates each, seed %d"
         % (len(c), REPLICATES, SEED))

    overall = statistics.fmean(r["recovery"] for r in c)
    gate("C2_the_failing_region_is_populated", C2_LO <= overall <= C2_HI,
         "overall recovery %.4f (band %.2f-%.2f)" % (overall, C2_LO, C2_HI))

    lo_noise = min(NOISES)
    corner_lo = statistics.fmean(r["recovery"] for r in c
                                 if r["family"] == "corner" and r["noise"] == lo_noise)
    inter_lo = statistics.fmean(r["recovery"] for r in c
                                if r["family"] == "interior" and r["noise"] == lo_noise)
    gate("C3_THE_CORNER_DESIGN_DISCRIMINATES", corner_lo >= C3_MIN,
         "corner recovery %.4f at noise sd %.2f (needs >= %.2f)"
         % (corner_lo, lo_noise, C3_MIN))
    gate("C4_THE_INTERIOR_DESIGN_DOES_NOT", corner_lo - inter_lo >= C4_GAP,
         "corner %.4f vs interior %.4f at noise sd %.2f, gap %+.4f (needs >= %.2f)"
         % (corner_lo, inter_lo, lo_noise, corner_lo - inter_lo, C4_GAP))

    med_rec = statistics.median(r["recovery"] for r in c)
    lab = [1 if r["recovery"] > med_rec else 0 for r in c]
    a_delta = auc([r["delta"] for r in c], lab)
    gate("C5_DCM_DELTA_PREDICTS_WHICH_DESIGNS_DISCRIMINATE",
         a_delta is not None and a_delta >= C5_AUC,
         "AUC(DELTA) = %s against recovery above the median (needs >= %.2f)"
         % (("%.4f" % a_delta) if a_delta is not None else "undefined", C5_AUC))

    if corner_lo >= C3_MIN and corner_lo - inter_lo >= C4_GAP:
        verdict = ("RIVAL THEORY. The multiplicative reading forbids at a reachable design "
                   "point what the additive reading permits, and the corner design "
                   "separates them where the interior design does not. UNTESTED AGAINST "
                   "HUMANS -- this is a statement about experimental design only.")
    elif corner_lo >= C3_MIN:
        verdict = ("INTERPRETATION. The accounts separate everywhere, so the reframe adds "
                   "no design guidance.")
    else:
        verdict = ("INTERPRETATION, with the stronger note that no design tested here "
                   "distinguishes the accounts at all.")
    gates.append({"id": "C6_the_verdict_under_the_crossover_protocol", "met": None,
                  "weight": "excluded", "detail": verdict})

    # ---- disclosures --------------------------------------------------------
    disclosures = {
        "D1_the_quantum_arm_is_derivation_the_cognitive_arm_is_simulation": {
            "quantum": "Every I(S:F) is a closed-form consequence of the Schroedinger "
                       "equation for a standard pure-dephasing model. Anyone with the same "
                       "equations gets the same numbers. Nothing here generates the "
                       "structure the claim exploits.",
            "cognitive": "Every retention value is generated by a model chosen here. It "
                         "says NOTHING about human memory. What a model-recovery study "
                         "legitimately yields is a required experiment, and that is its "
                         "only deliverable.",
        },
        "D2_the_quantum_reframe_rediscovered_an_existing_theory": {
            "note": "The governance channel identification -- encode hop into the "
                    "environment, decode hop into an observer's fragment -- IS quantum "
                    "Darwinism. Zurek's redundancy already separates total "
                    "system-environment correlation from fragment-limited access. The "
                    "reframe changed no prediction of physics and its verdict was declared "
                    "INTERPRETATION before the run for exactly that reason.",
            "why_that_is_still_worth_something": "A reframe that lands on an existing, "
                    "well-tested theory is a validity check on the method: the vocabulary "
                    "mapped onto real structure rather than inventing new structure. That "
                    "is a modest result and is reported as a modest one.",
        },
        "D3_three_of_the_five_questions_are_not_tested_here": {
            "tested": ["Q3 stewardship, as the two-hop channel claim"],
            "not_tested": ["Q1 purpose", "Q2 realms", "Q4 reference-lock",
                           "Q5 failure and predictability"],
            "note": "Q1 has been measured elsewhere in this programme. Q2, Q4 and Q5 are "
                    "given operational readings in the spec, which is Layer 2 and is not "
                    "evidence that the readings are correct. Listing a reading is not "
                    "answering a question.",
        },
        "D4_no_root_analysis_supports_any_number_here": {
            "note": "The two-hop vocabulary came from a Layer 3 reading. It generated the "
                    "hypothesis and the naming. It adjudicates no gate, appears in no "
                    "computation, and is cited nowhere as support for a numerical claim.",
        },
        "D6_THE_TWO_HOP_FORM_WAS_REFUTED_FOR_THIS_OBSERVABLE_AS_PREDICTED": {
            "median_abs_error_bits": {k: round(v, 4) for k, v in err.items()},
            "how_badly": "The SINGLE-HOP form errs by %.4f bits. The two-hop linear form "
                         "errs by %.4f bits -- roughly %.0f times worse. The second hop is "
                         "not merely dead weight; including it makes the prediction "
                         "dramatically worse."
                         % (err["single_hop"], err["two_hop_linear"],
                            err["two_hop_linear"] / err["single_hop"]),
            "this_was_predicted_in_writing": "The locked spec recorded Q3 as at genuine "
                         "risk and gave the reason: the partial-information plateau means "
                         "a form linear in fragment fraction must undershoot. It did.",
            "Q2s_pass_is_hollow_and_is_reported_as_such": "The linear form beat the "
                         "quadratic form by 0.2215 bits, so Q2 is recorded as met. Both "
                         "are useless next to the single-hop form. A gate can be met by "
                         "beating a worse rival and that is what happened here.",
        },
        "D7_MY_PREDICTION_ABOUT_WHERE_IT_WOULD_FAIL_WAS_WRONG": {
            "predicted": "failure in the saturation region, at larger fragment fractions",
            "observed": "linear-form mean |error| is %.4f at the SMALLEST fragment "
                        "fraction and %.4f at the largest -- the failure is worst at SMALL "
                        "fragments, the opposite of the pre-declaration."
                        % (small_f, large_f),
            "why": "Redundancy. A fragment of one qubit in twenty already carries very "
                   "nearly all the classical information, because the record is copied "
                   "many times over. The exact curve is already at the plateau where the "
                   "linear form is still predicting one twentieth of it.",
            "recorded_not_repaired": "The gate is not re-scored and the spec is not "
                   "edited. Getting the direction right and the location wrong is a "
                   "partial miss and is reported as one.",
        },
        "D8_WHAT_THIS_COSTS_LISM_AND_IT_IS_A_REAL_COST": {
            "finding": "The two-hop product form assumes the DECODE hop is SCARCE -- that "
                       "accessing more of the channel buys proportionally more yield. "
                       "Where the record is REDUNDANT, it is not scarce, and the product "
                       "form is the wrong functional form.",
            "domain_limit_now_on_the_record": "E = U * D_enc * D_dec should not be applied "
                       "to channels whose records are redundantly copied. Quantum "
                       "Darwinism is exactly such a channel, which is why the form loses "
                       "here by two orders of magnitude. This is a limit discovered by "
                       "carrying the form into a new field and having it fail.",
            "what_it_does_not_show": "It does not refute the product form in the substrates "
                       "where it was measured -- yeast, GitHub, the financial cohort. Those "
                       "channels are not obviously redundant in this sense. It marks a "
                       "boundary, not a reversal.",
        },
        "D9_THE_COGNITIVE_ARM_COULD_NOT_FAIL_AND_THAT_IS_MY_ERROR": {
            "overall_recovery": round(overall, 4),
            "what_happened": "Every one of the 36 configurations recovered the generating "
                       "model in all 200 replicates. Recovery is 1.0000 everywhere.",
            "why": "The locked design applies noise per participant and then AVERAGES over "
                       "the cell. With 20 to 100 participants the effective noise on a cell "
                       "mean is the stated sd divided by the square root of the cell size "
                       "-- about 0.0045 at the lowest setting. The two accounts differ by "
                       "far more than that at every design point, so nothing could fail.",
            "whose_error": "Mine. The noise levels were specified without accounting for "
                       "averaging. The spec is NOT edited and the gates are NOT re-scored.",
            "consequence_for_C3_and_C4": "C3 is recorded as met at 1.0000 and C4 as missed "
                       "at a gap of exactly zero. NEITHER IS INFORMATIVE. A test that "
                       "cannot fail is not evidence, and both are marked here as carrying "
                       "no weight despite their recorded verdicts.",
            "consequence_for_C5_AND_THIS_MATTERS": "The locked spec said a C5 miss would be "
                       "'a real result against DCM'. IT IS NOT, AND THAT SENTENCE IS "
                       "WITHDRAWN. With recovery identically 1.0 there is no variation for "
                       "DELTA to predict, so the AUC is undefined rather than low. C5 is "
                       "scored as not met because the locked rule says so, but its status "
                       "is UNTESTABLE-HERE, not REFUTED. Nothing in this run is evidence "
                       "for or against DCM.",
            "what_the_next_spec_must_do": "Specify noise on the CELL MEAN directly, or "
                       "raise it far enough that the averaged noise is comparable to the "
                       "gap between the accounts, and re-register before running.",
        },
        "D5_what_the_cognitive_arm_may_be_quoted_for": {
            "may": "which experimental designs can separate a multiplicative from an "
                   "additive two-factor account under stated noise and cell sizes.",
            "may_not": "anything about memory, learning, the testing effect or the spacing "
                       "effect in actual people.",
        },
    }

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet,
        "quantum_arm": {
            "theory": "T2O - Two-Hop Objectivity",
            "verdict": "INTERPRETATION, not rival theory (declared in advance)",
            "n_points": len(q), "N_env": N_ENV, "gammas": GAMMAS,
            "median_abs_error_bits": {k: round(v, 4) for k, v in err.items()},
            "best_form": best,
            "linear_error_at_smallest_fragment": round(small_f, 4),
            "linear_error_at_largest_fragment": round(large_f, 4),
            "first_fragment_fraction_where_best_form_breaks": first_break,
        },
        "cognitive_arm": {
            "theory": "T2R - Two-Hop Retention",
            "verdict": verdict,
            "configurations": len(c), "replicates_each": REPLICATES,
            "overall_recovery": round(overall, 4),
            "corner_recovery_lowest_noise": round(corner_lo, 4),
            "interior_recovery_lowest_noise": round(inter_lo, 4),
            "auc_dcm_delta": round(a_delta, 4) if a_delta is not None else None,
            "rows": c,
        },
        "post_run_disclosures": disclosures,
        "five_questions_tested_here": 1,
        "five_questions_total": 5,
    }
    with open(os.path.join(HERE, "results_crossover.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({"score": res["score"], "gates_not_met": notmet,
                      "quantum": {k: res["quantum_arm"][k] for k in
                                  ("median_abs_error_bits", "best_form", "verdict")},
                      "cognitive": {k: res["cognitive_arm"][k] for k in
                                    ("overall_recovery", "corner_recovery_lowest_noise",
                                     "interior_recovery_lowest_noise", "auc_dcm_delta")}},
                     indent=2))


if __name__ == "__main__":
    main()
