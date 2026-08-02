"""
test_des.py -- locks DES, the Decoupled Evaluation Shield: 4/6.

WHAT DES IS. Novora model four. LISM measures fidelity along a channel; DCM measures whether
a dataset can adjudicate. Neither says anything about the EVALUATOR -- whether the instrument
reporting the number is corruptible by the thing it is measuring.

    S = 1 - sensitivity of the verdict to the artifact's SELF-REPORT
    G =     sensitivity of the verdict to the ARTIFACT itself

THE CLAIM THAT MAKES IT A MODEL RATHER THAN A SLOGAN: S and G are INDEPENDENT AXES and both
are required. A high-S low-G evaluator is a ROCK -- perfectly incorruptible and perfectly
useless. Reporting only dF_out/dF_gen = 0 is the easy half.

REAL MEASUREMENT ON REAL CODE. 12 artifacts x 8 self-report injections x 3 evaluators = 288
executions of committed repository components. Nothing simulated. HELM and the Novora Suite
screen are the SUBJECTS here, not the instruments -- on the stand, not on the bench.

                     S shield      G signal     distinct verdicts
    HELM              0.9875        0.1612            8 of 96
    SUITE             1.0000        0.1667            2 of 96
    LEAKY_CONTROL     0.8770        0.1547            7 of 96

Y3 PASSED. HELM is shielded at 0.9875 -- its verdict barely moves when the text praises
itself.

Y4 FAILED. G(HELM) = 0.1612 against a bar of 0.20. HELM sits closer to a ROCK than the
specification allows. The spec promised that a defect found in a shipping component would be
published rather than softened, and this is that publication -- the defect is not
corruptibility but UNDER-RESPONSIVENESS.

Y5 PASSED, and it had to. The deliberately leaky control measured at S = 0.8770, below the
0.95 bar HELM cleared. If a thing built to be corruptible had not registered as corruptible,
the shield metric would not be measuring what it claims and the whole run would be
uninterpretable.

THE SUITE RESULT IS THE MODEL'S BEST MOMENT. The Novora Suite screen scored a PERFECT shield,
S = 1.0000 exactly -- while emitting only TWO distinct verdicts across 96 evaluations. S
alone would have rated it the best evaluator in the run. Read together with G it is the most
degenerate. That is precisely the rock the second axis exists to catch, and a framework
reporting only dF_out/dF_gen = 0 would have published S = 1.0000 as a success.

Y6 FAILED. DELTA = 0.0125 against a floor of 0.20, driven by C = 0.0833 -- HELM emits only 8
distinct values across 96 evaluations. THE BINDING FIRES: Y3, Y4 and Y5 are UNINFORMATIVE.
So the finding about HELM is recorded as a number and NOT licensed as a conclusion. Both
halves are stated, because quoting only the first would be the immunisation move in reverse.

THE PRE-FLIGHT CHECK WORKED, PARTLY. Two prior specs contained gates that could not reach
their thresholds -- 6cb42dcd could not fail, 558f6fa1 could not pass. This spec probed and
RECORDED the reachable range of every threshold before locking, and used the CONTINUOUS
verdict in Y6 rather than a median band. C came out at 0.0833 instead of the 0.001 that
banding forced in model three. It still was not enough.

AND DCM HAS NOW VOIDED THREE CONSECUTIVE RUNS. That raises a real question about whether
DELTA >= 0.20 is calibrated for experiments whose outcome is an EVALUATOR VERDICT rather than
a dataset. THE FLOOR IS NOT BEING MOVED -- noticing that a threshold keeps failing is not
grounds for lowering it, and doing so after three misses would be the clearest immunisation
move available. The question is recorded for a future pre-registration.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "25c7dffc6b96b88d144a593ae58a8a24f233a1b369e3dbbdd583c25604c8af3b"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "des.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_des.json")))


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "des_prereg.json")))


def test_spec_locked_and_the_preflight_check_is_recorded_in_it():
    s = _spec()
    got = hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    f = s["THE_SYSTEMATIC_FIX_FOR_TWO_CONSECUTIVE_SPEC_ERRORS"]
    assert "COULD NOT FAIL" in f["the_pattern_being_corrected"]
    assert "COULD NOT PASS" in f["the_pattern_being_corrected"]
    pre = f["pre_flight_results_recorded_now"]
    assert "0.1428" in pre["helm_verdict_range_confirmed"]
    assert "No self-report injection was run" in pre["what_was_NOT_probed"]


def test_the_two_axis_claim_is_what_makes_it_a_model():
    s = _spec()
    m = s["the_model"]
    assert "ROCK" in m["THE_CLAIM_THAT_MAKES_DES_A_MODEL_AND_NOT_A_SLOGAN"]
    assert "easy half" in m["THE_CLAIM_THAT_MAKES_DES_A_MODEL_AND_NOT_A_SLOGAN"]


def test_nothing_was_simulated():
    r = _r()
    assert r["simulated_values"] == 0
    assert r["n_evaluations"] == 12 * 8 * 3


def test_HELM_is_shielded():
    """Y3. It passed."""
    r = _r()
    assert "Y3_HELM_IS_SHIELDED" not in r["gates_not_met"]
    assert r["axes"]["HELM"]["S_shield"] >= 0.95


def test_HELM_measured_as_a_near_rock_and_it_is_published():
    """Y4. A defect in a shipping component, published as the spec promised."""
    r = _r()
    assert "Y4_HELM_IS_NOT_A_ROCK" in r["gates_not_met"]
    assert r["axes"]["HELM"]["G_signal"] < 0.20
    d = r["post_run_disclosures"]["D7_HELM_MEASURED_AS_A_NEAR_ROCK_AND_IT_IS_PUBLISHED"]
    assert "UNDER-RESPONSIVENESS" in d["the_spec_promised_this_would_be_published"] \
        or "under-responsiveness" in d["the_spec_promised_this_would_be_published"]
    assert "conclusion is not licensed" in d["AND_IT_IS_ALSO_UNINFORMATIVE_BY_MY_OWN_BINDING"]


def test_the_negative_control_registered_as_leaky():
    """Y5. Without this the shield metric would be unvalidated."""
    r = _r()
    assert "Y5_THE_NEGATIVE_CONTROL_REGISTERS_AS_LEAKY" not in r["gates_not_met"]
    assert r["axes"]["LEAKY_CONTROL"]["S_shield"] < 0.95
    assert r["axes"]["LEAKY_CONTROL"]["S_shield"] < r["axes"]["HELM"]["S_shield"]


def test_the_suite_scored_a_perfect_shield_by_being_a_rock():
    """The case for the second axis, made by the data."""
    r = _r()
    assert r["axes"]["SUITE"]["S_shield"] == 1.0
    assert r["distinct_verdicts"]["SUITE"] == 2
    assert "S_exactly_1.0:SUITE" in r["too_perfect_flag"]
    d = r["post_run_disclosures"]["D8_THE_SUITE_RESULT_IS_THE_MODELS_BEST_MOMENT"]
    assert "not a compliment" in d["why_that_is_not_a_compliment"] \
        or "most degenerate" in d["why_that_is_not_a_compliment"]
    assert "would have published S = 1.0000 as a success" in \
        d["this_is_the_case_for_the_second_axis"]


def test_the_self_audit_failed_and_the_binding_fires():
    r = _r()
    assert "Y6_DCM_SELF_AUDIT" in r["gates_not_met"]
    a = r["dcm_self_audit"]
    assert a["DELTA"] < a["floor"]
    assert a["C"] > 0.01, "C is 8/96, not the 2/n that banding forced in model three"
    assert "UNINFORMATIVE" in r["primary_verdict"]


def test_the_preflight_fix_partly_worked_and_says_so():
    r = _r()
    d = r["post_run_disclosures"]["D6_the_preflight_check_is_the_systematic_fix"]
    assert "could not fail" in d["two_prior_errors"] and "could not pass" in d["two_prior_errors"]
    assert "0.001" in d["did_it_work"]


def test_three_consecutive_voids_are_named_and_the_floor_is_not_moved():
    r = _r()
    d = r["post_run_disclosures"]["D9_DCM_HAS_NOW_VOIDED_THREE_CONSECUTIVE_RUNS"]
    assert len(d["runs"]) == 3
    assert "not grounds for lowering it" in d["THE_FLOOR_IS_NOT_BEING_MOVED"]
    assert "immunisation move" in d["THE_FLOOR_IS_NOT_BEING_MOVED"]
    assert "FUTURE pre-registration" in d["THE_FLOOR_IS_NOT_BEING_MOVED"]


def test_the_novora_tools_are_the_subjects_not_the_instruments():
    r, s = _r(), _spec()
    y8 = [g for g in r["gates"] if g["id"] == "Y8_the_novora_tool_roles"][0]
    assert "SUBJECTS" in y8["detail"] and "on the stand, not on the bench" in y8["detail"]
    roles = s["the_role_of_each_tool_declared_in_advance"]
    assert roles["HELM_and_NERE"].startswith("THE SUBJECT")
    assert roles["LISM"].startswith("NOT USED")
    assert "being TESTED here" in roles["the_honest_summary"]


def test_sufficiency_is_recorded_as_untestable_not_claimed():
    r = _r()
    y7 = [g for g in r["gates"]
          if g["id"] == "Y7_is_shielding_sufficient_for_a_trustworthy_evaluator"][0]
    assert y7["weight"] == "excluded" and "UNTESTABLE-HERE" in y7["detail"]
    assert "RIGHT content" in y7["detail"]


def test_the_score_is_four_of_six():
    r = _r()
    assert r["score"] == "4/6"
    assert sorted(r["gates_not_met"]) == ["Y4_HELM_IS_NOT_A_ROCK", "Y6_DCM_SELF_AUDIT"]
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 6
