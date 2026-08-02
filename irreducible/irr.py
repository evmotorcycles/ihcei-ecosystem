"""
irr.py -- the Computational Irreducibility Testbed for Q5, run against its pre-registration.

Spec 0de17fc489bbdad37ee2a8d7b5496fea85acd206f65753c4b9b8edbd781984f2, locked after a
recorded pre-flight on two throwaway rules and before any of the eight scored rules was
evolved.

Real cellular automata, evolved directly. Nothing simulated, nothing imputed.
"""
import hashlib
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ca import run_rule, N_INIT, HORIZON, PARTIAL, WIDTH  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# BOTH runs execute this same file. v2 differs from v1 ONLY in which rules it names --
# not in the pipeline, not in a threshold, not in a line of scoring code.
SPECS = {
    "v1": ("irreducible_prereg.json",
           "0de17fc489bbdad37ee2a8d7b5496fea85acd206f65753c4b9b8edbd781984f2"),
    "v2": ("irreducible_v2_prereg.json",
           "0cd701a45bb725c499f5313786d0e463e2986df4eb617c682aeb4388e66a1a84"),
}
WHICH = sys.argv[1] if len(sys.argv) > 1 else "v1"
SPEC_FILE, LOCKED = SPECS[WHICH]

SPEC = json.load(open(os.path.join(HERE, "prereg", SPEC_FILE)))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

R = SPEC.get("the_rules_declared_before_any_of_them_was_run") or SPEC["the_rules"]
SIMPLE = R["SIMPLE_expected_reducible"]
COMPLEX = R["COMPLEX_expected_irreducible"]

P2_LO, P2_HI, P2_MIN_RULES = 0.20, 0.80, 6
P3_CEILING, P4_BAR, P5_GAIN = 0.60, 0.75, 0.10
P6_LO, P6_HI = 0.40, 0.60


def main():
    real = {r: run_rule(r) for r in SIMPLE + COMPLEX}
    ctrl = {r: run_rule(r, shuffle_labels=True) for r in SIMPLE + COMPLEX}
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    # A rule whose outcome is constant has an UNDEFINED AUC, not a low one. It is recorded
    # as undefined and never silently averaged over. See D7.
    undefined = sorted(r for r in real
                       if real[r]["static_auc"] is None or real[r]["partial_auc"] is None)

    def m(rules, key, src=real):
        vals = [src[r][key] for r in rules if src[r][key] is not None]
        return statistics.fmean(vals) if len(vals) == len(rules) else None

    def m_admissible(rules, key, src=real):
        """Clearly-labelled POST-HOC figure over only the computable rules."""
        vals = [src[r][key] for r in rules if src[r][key] is not None]
        return statistics.fmean(vals) if vals else None

    s_simple, s_complex = m(SIMPLE, "static_auc"), m(COMPLEX, "static_auc")
    p_simple, p_complex = m(SIMPLE, "partial_auc"), m(COMPLEX, "partial_auc")

    # ---- P1 ------------------------------------------------------------------
    finite = all(v[k] is not None and 0.0 <= v[k] <= 1.0
                 for v in list(real.values()) + list(ctrl.values())
                 for k in ("static_auc", "partial_auc"))
    pre = SPEC.get("PRE_FLIGHT_FEASIBILITY_PROBE_RECORDED_BEFORE_THIS_LOCK") or \
        SPEC["PRE_FLIGHT_FEASIBILITY_PROBE"]
    ca_hash = hashlib.sha256(open(os.path.join(HERE, "ca.py"), "rb").read()).hexdigest()
    gate("P1_integrity_and_the_preflight_is_recorded",
         len(real) == 8 and finite and bool(pre),
         "%d rules x %d initial conditions, width %d, horizon %d, partial %d. AUCs finite "
         "in [0,1]=%s. Pre-flight record present=%s. Shared engine ca.py sha256 %s"
         % (len(real), N_INIT, WIDTH, HORIZON, PARTIAL, finite, bool(pre), ca_hash[:16]))

    # ---- P2 admissibility: the outcome must not be degenerate ----------------
    ok_rules = [r for r in real if P2_LO <= real[r]["base_rate"] <= P2_HI]
    gate("P2_THE_OUTCOME_IS_NOT_DEGENERATE", len(ok_rules) >= P2_MIN_RULES,
         "%d of 8 rules have a centre-cell base rate inside [%.2f, %.2f] (need >= %d). "
         "Rates: %s" % (len(ok_rules), P2_LO, P2_HI, P2_MIN_RULES,
                        {r: round(real[r]["base_rate"], 3) for r in sorted(real)}))

    # ---- P3 primary ----------------------------------------------------------
    p3 = s_complex <= P3_CEILING
    gate("P3_PRIMARY_STATIC_PREDICTION_FAILS_ON_THE_COMPLEX_RULES", p3,
         "mean static AUC on the 4 COMPLEX rules = %.4f (needs <= %.2f). Per rule: %s"
         % (s_complex, P3_CEILING,
            {r: round(real[r]["static_auc"], 4) for r in COMPLEX}))

    # ---- P4 the ablation that makes P3 mean anything -------------------------
    # If any SIMPLE rule has an undefined AUC the pre-registered quantity -- the mean over
    # ALL FOUR -- does not exist. That is UNTESTABLE-HERE, not a pass and not a failure.
    # Treating it as a pass would be the immunising move, so P4 is excluded from scoring
    # and its binding consequence on P3 still applies.
    if s_simple is None:
        p4 = False
        gates.append({"id": "P4_THE_ABLATION_THE_SAME_PREDICTOR_SUCCEEDS_ON_THE_SIMPLE_RULES",
                      "met": None, "weight": "excluded",
                      "detail": "UNTESTABLE-HERE. The pre-registered quantity is the mean "
                                "static AUC across ALL FOUR simple rules, and rule(s) %s "
                                "have a CONSTANT outcome so their AUC is undefined rather "
                                "than low. The mean over four does not exist and is not "
                                "replaced by a mean over the survivors. Post-hoc, over the "
                                "computable simple rules only, it is %s -- a figure that "
                                "scores nothing."
                                % (undefined,
                                   round(m_admissible(SIMPLE, "static_auc"), 4)
                                   if m_admissible(SIMPLE, "static_auc") is not None
                                   else "undefined")})
    else:
        p4 = s_simple >= P4_BAR
        gate("P4_THE_ABLATION_THE_SAME_PREDICTOR_SUCCEEDS_ON_THE_SIMPLE_RULES", p4,
             "mean static AUC on the 4 SIMPLE rules = %.4f (needs >= %.2f), same predictor, "
             "same features, same pipeline. Per rule: %s"
             % (s_simple, P4_BAR, {r: round(real[r]["static_auc"], 4) for r in SIMPLE}))

    # ---- P5 monitoring vs predicting ----------------------------------------
    gain = p_complex - s_complex
    gate("P5_MONITORING_BEATS_PREDICTING_ON_THE_COMPLEX_RULES", gain >= P5_GAIN,
         "mean partial-run AUC %.4f minus mean static AUC %.4f = %+.4f on the COMPLEX "
         "rules (needs >= %.2f). Per rule gain: %s"
         % (p_complex, s_complex, gain, P5_GAIN,
            {r: round(real[r]["partial_auc"] - real[r]["static_auc"], 4) for r in COMPLEX}))

    # ---- P6 shuffled-label control ------------------------------------------
    def in_band(v):
        return v is not None and P6_LO <= v <= P6_HI
    bad = {r: (ctrl[r]["static_auc"], ctrl[r]["partial_auc"]) for r in ctrl
           if not (in_band(ctrl[r]["static_auc"]) and in_band(ctrl[r]["partial_auc"]))}
    gate("P6_THE_SHUFFLED_LABEL_CONTROL_IS_AT_CHANCE", not bad,
         "every rule and both predictors must land in [%.2f, %.2f] with labels permuted. "
         "Outside that range or undefined: %s" % (P6_LO, P6_HI, bad if bad else "none"))

    gates.append({"id": "P7_DCM_self_audit", "met": None, "weight": "excluded",
                  "detail": "EXCLUDED. DELTA = V*I*C is an admissibility check for "
                            "CONCENTRATED or CATEGORICAL outcomes. The outcome here is "
                            "cross-validated AUC -- continuous, unbanded, spread across "
                            "cells -- so V and C sit near 1 by construction and DELTA "
                            "cannot fail. A gate that cannot fail is not evidence, so it "
                            "scores nothing rather than inflating the total."})
    gates.append({"id": "P8_does_any_of_this_transfer_to_institutions", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. A cellular automaton is not an institution. "
                            "Establishing transfer needs a demonstration that some real "
                            "governance outcome is computationally irreducible, and nothing "
                            "in this repository provides one."})

    def _f(v, nd=4):
        return round(v, nd) if v is not None else None

    suspect = []
    for r in real:
        for k in ("static_auc", "partial_auc"):
            if real[r][k] is not None and real[r][k] >= 0.99995:
                suspect.append("rule_%d_%s_at_1.0" % (r, k))
    if undefined:
        suspect.append("rules_with_UNDEFINED_AUC_constant_outcome_%s" % undefined)
    if bad:
        suspect.append("shuffled_label_control_off_chance")

    binding = ("P4 WAS MET, so P3 is interpretable: the same predictor that succeeds on the "
               "reducible rules fails on the irreducible ones." if p4 and s_simple is not None
               else ("P4 COULD NOT BE COMPUTED, SO P3 IS UNINFORMATIVE. Rule(s) %s have a "
                     "CONSTANT outcome, so the ablation's pre-registered quantity does not "
                     "exist. An ablation that could not be run is not an ablation that "
                     "passed." % undefined) if s_simple is None else
               "P4 WAS NOT MET, SO P3 IS UNINFORMATIVE. A predictor that fails everywhere "
               "has shown nothing about irreducibility, only about itself.")

    disclosures = {
        "D1_THE_BINDING_CONSEQUENCE": {"statement": binding, "P4_met": bool(p4)},
        "D2_the_separation": {
            "static_AUC_simple": _f(s_simple),
            "static_AUC_simple_POST_HOC_computable_rules_only":
                _f(m_admissible(SIMPLE, "static_auc")),
            "static_AUC_complex": _f(s_complex),
            "per_rule_static": {str(r): _f(real[r]["static_auc"])
                                for r in SIMPLE + COMPLEX},
        },
        "D3_monitoring_versus_predicting": {
            "complex_static": _f(s_complex), "complex_partial": _f(p_complex),
            "complex_gain": _f(gain),
            "simple_static": _f(s_simple),
            "simple_partial_POST_HOC_computable_rules_only":
                _f(m_admissible(SIMPLE, "partial_auc")),
            "note": "The simple arm has little to gain because static prediction has already "
                    "saturated there. The complex arm is where the governance recommendation "
                    "lives: if partial observation does not rescue what static structure "
                    "cannot reach, then 'monitor rather than predict' has no testbed support.",
        },
        "D4_WHY_DCM_SCORES_NOTHING_HERE": {
            "note": "DCM has voided five runs in this programme, every one of them on an "
                    "outcome that lands on a small lattice. It is silent on continuous "
                    "outcomes such as AUC, where V and C are near 1 by construction. That is "
                    "a scope limit on our own instrument, recorded here rather than "
                    "discovered later, and it is why P7 is EXCLUDED instead of counted as a "
                    "pass.",
        },
        "D5_WHAT_THIS_DOES_NOT_LICENSE": {
            "note": "A cellular automaton is not an institution. No result here is evidence "
                    "that any organisation is computationally irreducible, that tau_v is the "
                    "right thing to monitor, or that 'monitor rather than predict' is good "
                    "advice for anyone. P8 records this and no write-up may weaken it.",
        },
        "D6_the_class_labels_came_from_the_literature": {
            "note": "Simple and complex were assigned from published Wolfram classifications "
                    "before any rule here was evolved. They are not read off our own results, "
                    "which would have made P3 and P4 circular.",
        },
    }

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": SPEC["model"],
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet,
        "simulated_values": 0,
        "n_cellular_automaton_runs": 8 * N_INIT * 2,
        "rules": {"SIMPLE": SIMPLE, "COMPLEX": COMPLEX},
        "rules_with_undefined_auc": undefined,
        "per_rule": {str(r): {"base_rate": _f(real[r]["base_rate"]),
                              "static_auc": _f(real[r]["static_auc"]),
                              "partial_auc": _f(real[r]["partial_auc"]),
                              "shuffled_static_auc": _f(ctrl[r]["static_auc"])}
                     for r in SIMPLE + COMPLEX},
        "summary": {"static_simple": _f(s_simple),
                    "static_complex": _f(s_complex),
                    "partial_simple": _f(p_simple),
                    "partial_complex": _f(p_complex),
                    "monitoring_gain_complex": _f(gain)},
        "too_perfect_flag": suspect,
        "post_run_disclosures": disclosures,
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        ("Static prediction came in at mean AUC %.4f on the COMPLEX rules against a %.2f "
         "ceiling." % (s_complex, P3_CEILING)) if p3 else
        ("Static prediction came in at mean AUC %.4f on the COMPLEX rules against a %.2f "
         "ceiling, so the pre-registered primary is NOT supported on this testbed."
         % (s_complex, P3_CEILING))) + " " + binding
    res["spec_version"] = WHICH
    with open(os.path.join(HERE, "results_irr_%s.json" % WHICH), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "summary", "per_rule",
                       "too_perfect_flag", "primary_verdict")}, indent=2))


if __name__ == "__main__":
    main()
