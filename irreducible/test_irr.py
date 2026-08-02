"""
test_irr.py -- locks the Computational Irreducibility Testbed for Q5.

    v1  spec 0de17fc4  2/5   my rule choice was defective, and its own gates caught it
    v2  spec 0cd701a4  5/6   clean rule set, same thresholds, same code

WHY A CELLULAR AUTOMATON AT ALL. Q5 asks whether a system's future can be read off its
present or whether it has to be run. On real institutions a null is uninterpretable: "no
shortcut was found" and "no shortcut exists" cannot be separated by field data. Rule 110 is
proven Turing-complete, so for it the answer is not in doubt, and a null there means
something because it can be compared against rules where a shortcut demonstrably exists.

WHAT V1 GOT WRONG, AND IT WAS MINE. v1 hand-picked SIMPLE = [4, 108, 132, 160]. Rule 160
drives the centre cell to a CONSTANT 0 by step 60, so its AUC is UNDEFINED -- not low. The
ablation P4's pre-registered quantity is the mean across ALL FOUR simple rules, and that
mean does not exist. P4 was therefore recorded as UNTESTABLE-HERE and EXCLUDED, its binding
consequence was still applied so v1's P3 is UNINFORMATIVE even though P3 itself was met, and
the mean over the surviving three (0.9559) was reported as a post-hoc figure scoring nothing.
Treating an ablation that could not be run as an ablation that passed would have been the
immunising move. v1's P1 and P6 failed for the same single reason.

WHAT V2 CHANGED, AND WHAT IT DID NOT. Only the four SIMPLE rules, chosen by a MECHANICAL
screen: 74 published class-1/2 candidates, admit base rate in [0.20, 0.80], take the four
lowest numbers. The screen computed BASE RATE ONLY -- never AUC, never a fitted model -- and
base rate is the admissibility criterion v1's own P2 declared before any data. Not one
threshold moved. irr.py and ca.py are the same files for both runs.

THE RESULT.

    static AUC, 4 SIMPLE rules      0.7656      bar 0.75    P4 MET
    static AUC, 4 COMPLEX rules     0.4940      ceiling 0.60  P3 MET
    shuffled-label control          all in [0.40, 0.60]       P6 MET

So the same predictor that reaches 0.7656 on reducible rules sits at CHANCE on the
irreducible ones. Rule 110, proven Turing-complete: 0.4945.

AND P5 FAILED, WHICH IS A NULL AGAINST OUR OWN ADVICE. Giving the predictor the first 30
steps of the actual trajectory -- the "monitor rather than forecast" arm -- gained +0.0051
on the complex rules against a 0.10 bar. On computationally irreducible systems, partial
observation does NOT rescue what static structure cannot reach. The governance
recommendation to watch a leading indicator instead of predicting has NO support from this
testbed. The bar was not lowered after v1 measured the same +0.0051.

THE CAVEAT THAT MATTERS MOST. The simple arm clears 0.75 only because rules 1 and 5 are
near-perfect (0.9878, 1.0000) while rules 3 and 6 sit at 0.5684 and 0.5062 -- near chance,
despite both being class 2. Wolfram class does NOT determine static predictability. The
mean passes; the arm is not homogeneous, and that is disclosed rather than smoothed over.

DCM SCORES NOTHING HERE, BY THE RULE. DELTA = V*I*C is an admissibility check for
concentrated or categorical outcomes. AUC is continuous and unbanded, so V and C sit near 1
by construction and DELTA cannot fail. A gate that cannot fail is not evidence, so P7 is
EXCLUDED rather than counted as a pass. That is a scope limit on our own instrument.

AND NONE OF IT TRANSFERS. A cellular automaton is not an institution. P8 is UNTESTABLE-HERE.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = "0de17fc489bbdad37ee2a8d7b5496fea85acd206f65753c4b9b8edbd781984f2"
V2 = "0cd701a45bb725c499f5313786d0e463e2986df4eb617c682aeb4388e66a1a84"


def _run(which):
    p = subprocess.run([sys.executable, os.path.join(HERE, "irr.py"), which],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_irr_%s.json" % which)))


def _spec(name):
    return json.load(open(os.path.join(HERE, "prereg", name)))


def _sha(s):
    return hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_both_specs_are_locked():
    assert _sha(_spec("irreducible_prereg.json")) == V1
    assert _sha(_spec("irreducible_v2_prereg.json")) == V2
    assert _spec("irreducible_v2_prereg.json")["supersedes"] == V1


def test_the_spec_says_up_front_that_none_of_this_transfers_to_institutions():
    w = _spec("irreducible_prereg.json")["WHY_THIS_TESTBED_AND_NOT_AN_INSTITUTION"]
    assert "Rule 110 is proven Turing-complete" in w["what_a_CA_buys"]
    assert "NOTHING measured here transfers to a real organisation" in w["WHAT_THIS_IS_NOT"]
    assert "P3 alone" in w["THE_ABLATION_THAT_MAKES_THE_PRIMARY_MEAN_ANYTHING"]


def test_the_preflight_bracketed_every_bar_before_the_lock():
    p = _spec("irreducible_prereg.json")["PRE_FLIGHT_FEASIBILITY_PROBE_RECORDED_BEFORE_THIS_LOCK"]
    assert p["rule_232"]["static_auc"] >= 0.75, "the 0.75 bar is attainable"
    assert p["rule_62"]["static_auc"] <= 0.60, "the 0.60 ceiling is not automatic"
    assert p["rule_62"]["partial_minus_static"] >= 0.10, "the 0.10 gain is attainable"
    assert "None of the eight scored rules" in p["WHAT_WAS_DELIBERATELY_NOT_PROBED"]


# ---- v1: the run whose own gates caught my rule choice ------------------------------

def test_v1_ablation_was_UNTESTABLE_not_quietly_passed():
    r = _run("v1")
    assert r["rules_with_undefined_auc"] == [160]
    g = [x for x in r["gates"]
         if x["id"] == "P4_THE_ABLATION_THE_SAME_PREDICTOR_SUCCEEDS_ON_THE_SIMPLE_RULES"][0]
    assert g["weight"] == "excluded" and g["met"] is None
    assert "UNTESTABLE-HERE" in g["detail"]
    assert "not replaced by a mean over the survivors" in g["detail"]


def test_v1_primary_is_reported_as_UNINFORMATIVE_even_though_it_was_met():
    """The binding consequence applies to an ablation that could not be run."""
    r = _run("v1")
    assert "P3_PRIMARY_STATIC_PREDICTION_FAILS_ON_THE_COMPLEX_RULES" not in r["gates_not_met"]
    assert "P3 IS UNINFORMATIVE" in r["primary_verdict"]
    assert "not an ablation that passed" in r["primary_verdict"]
    assert r["score"] == "2/5"


def test_v1_failures_trace_to_the_one_bad_rule():
    r = _run("v1")
    assert sorted(r["gates_not_met"]) == [
        "P1_integrity_and_the_preflight_is_recorded",
        "P5_MONITORING_BEATS_PREDICTING_ON_THE_COMPLEX_RULES",
        "P6_THE_SHUFFLED_LABEL_CONTROL_IS_AT_CHANCE",
    ]
    # P1 and P6 fail only because rule 160's AUC is undefined
    assert r["per_rule"]["160"]["base_rate"] == 0.0
    for rule in ("4", "108", "132", "30", "90", "110", "150"):
        assert 0.40 <= r["per_rule"][rule]["shuffled_static_auc"] <= 0.60


# ---- the screen --------------------------------------------------------------------

def test_the_screen_looked_at_base_rate_only_and_had_no_discretion():
    s = _spec("irreducible_v2_prereg.json")["THE_MECHANICAL_SCREEN_THAT_CHOSE_THE_NEW_SIMPLE_RULES"]
    assert s["CHOSEN"] == [1, 3, 5, 6]
    assert "AUC -- the actual outcome -- was never computed" in \
        s["why_this_is_not_selecting_on_the_outcome"]
    assert "FOUR LOWEST rule numbers" in s["choice_rule"]
    assert "real risk carried deliberately" in s["note_on_the_risk_this_carries"]
    assert s["v1_rules_the_screen_rejects"]["160"] == 0.0


def test_v2_moved_no_threshold_and_reuses_the_same_code():
    src = open(os.path.join(HERE, "irr.py")).read()
    assert "P2_LO, P2_HI, P2_MIN_RULES = 0.20, 0.80, 6" in src
    assert "P3_CEILING, P4_BAR, P5_GAIN = 0.60, 0.75, 0.10" in src
    assert "P6_LO, P6_HI = 0.40, 0.60" in src
    w = _spec("irreducible_v2_prereg.json")["WHAT_WENT_WRONG_IN_V1_AND_IT_WAS_MY_RULE_CHOICE_NOT_THE_METHOD"]
    assert "Not one threshold" in w["WHAT_IS_NOT_CHANGED_HERE"]


# ---- v2: the clean run -------------------------------------------------------------

def test_STATIC_PREDICTION_IS_AT_CHANCE_ON_THE_IRREDUCIBLE_RULES():
    """P3, and it is interpretable because P4 was met."""
    r = _run("v2")
    assert "P3_PRIMARY_STATIC_PREDICTION_FAILS_ON_THE_COMPLEX_RULES" not in r["gates_not_met"]
    assert r["summary"]["static_complex"] <= 0.60
    assert abs(r["summary"]["static_complex"] - 0.50) < 0.05, "at chance, not merely below"
    assert r["per_rule"]["110"]["static_auc"] <= 0.60, "rule 110 is proven Turing-complete"


def test_THE_ABLATION_HELD_so_the_primary_means_something():
    r = _run("v2")
    assert "P4_THE_ABLATION_THE_SAME_PREDICTOR_SUCCEEDS_ON_THE_SIMPLE_RULES" \
        not in r["gates_not_met"]
    assert r["summary"]["static_simple"] >= 0.75
    assert "P4 WAS MET, so P3 is interpretable" in r["primary_verdict"]
    sep = r["summary"]["static_simple"] - r["summary"]["static_complex"]
    assert sep > 0.25, "the same predictor separates the two classes"


def test_MONITORING_DID_NOT_RESCUE_PREDICTION_and_the_bar_was_not_lowered():
    """P5. A null against our own governance recommendation, measured twice."""
    r2, r1 = _run("v2"), _run("v1")
    assert "P5_MONITORING_BEATS_PREDICTING_ON_THE_COMPLEX_RULES" in r2["gates_not_met"]
    assert r2["summary"]["monitoring_gain_complex"] < 0.10
    assert r1["summary"]["monitoring_gain_complex"] == r2["summary"]["monitoring_gain_complex"], \
        "the complex arm is identical in both runs, so the null replicates exactly"
    d = r2["post_run_disclosures"]["D3_monitoring_versus_predicting"]
    assert "has no testbed support" in d["note"] or "no testbed support" in d["note"]


def test_the_simple_arm_is_NOT_homogeneous_and_that_is_disclosed():
    """Wolfram class does not determine static predictability."""
    r = _run("v2")
    per = r["per_rule"]
    assert per["1"]["static_auc"] > 0.95 and per["5"]["static_auc"] > 0.95
    assert per["3"]["static_auc"] < 0.60 and per["6"]["static_auc"] < 0.60
    assert r["summary"]["static_simple"] >= 0.75, "the mean still clears the bar"


def test_the_shuffled_label_control_is_at_chance_everywhere_in_v2():
    r = _run("v2")
    assert "P6_THE_SHUFFLED_LABEL_CONTROL_IS_AT_CHANCE" not in r["gates_not_met"]
    for rule, v in r["per_rule"].items():
        assert 0.40 <= v["shuffled_static_auc"] <= 0.60, rule


def test_DCM_is_excluded_because_it_cannot_fail_on_a_continuous_outcome():
    r = _run("v2")
    g = [x for x in r["gates"] if x["id"] == "P7_DCM_self_audit"][0]
    assert g["weight"] == "excluded"
    assert "cannot fail" in g["detail"]
    d = r["post_run_disclosures"]["D4_WHY_DCM_SCORES_NOTHING_HERE"]
    assert "scope limit on our own instrument" in d["note"]


def test_no_transfer_to_institutions_is_claimed():
    r = _run("v2")
    g = [x for x in r["gates"]
         if x["id"] == "P8_does_any_of_this_transfer_to_institutions"][0]
    assert g["weight"] == "excluded" and "UNTESTABLE-HERE" in g["detail"]
    d = r["post_run_disclosures"]["D5_WHAT_THIS_DOES_NOT_LICENSE"]
    assert "is not an institution" in d["note"]
    assert "tau_v is the right thing to monitor" in d["note"]


def test_v2_score_is_five_of_six_and_nothing_is_simulated():
    r = _run("v2")
    assert r["score"] == "5/6"
    assert r["gates_not_met"] == ["P5_MONITORING_BEATS_PREDICTING_ON_THE_COMPLEX_RULES"]
    assert r["simulated_values"] == 0
    assert r["n_cellular_automaton_runs"] == 12800
    assert r["rules_with_undefined_auc"] == []
