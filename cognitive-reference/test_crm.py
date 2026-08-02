"""
test_crm.py -- locks CRM, the Cognitive Reference Model: 4/6.

WHAT CRM IS. Novora model three. LISM asks how much fidelity survives a channel; CRM asks
FIDELITY TO WHAT. It carries two separately measurable references and stakes its existence
on that pair beating a single fidelity number AND beating LISM's own form:

    D_W = |rank corr( g(x), x )|        fidelity to the WORLD
    D_F = |rank corr( g(x), f_m(x) )|   fidelity to the PAYOFF

Both are computed from the perceptual map and the world only. Neither reads the realised
payoff, and a test below scans the source of both functions to enforce that.

THE HEADLINE: CRM DID NOT EARN ITS EXISTENCE ON THIS RUN.

    mean held-out |error|
      CRM two-reference   0.06611
      LISM U*D_enc*D_dec  0.06915     gain +0.00304 against a locked bar of 0.005 -> X5 FAILED
      single fidelity     0.07725
      D_F alone           0.06641     <- and this is the harsher number

  X5 missed. The spec said in its own words: 'If LISM's existing form predicts this
  cognitive outcome as well as a purpose-built two-reference model, then CRM adds
  vocabulary and no power, and the honest conclusion is to keep LISM and drop CRM.'

  Worse, and NOT pre-registered so it scores nothing: D_F ALONE scores 0.06641 against the
  two-reference model's 0.06611 -- a gain of 0.00030. The locked X3 compared CRM against
  the MEAN of the two fidelities, which is a weaker rival than the better single one.
  Against the best single reference, two references buy almost nothing. Reported because
  leaving it out would flatter the model.

X6 FAILED BECAUSE I MIS-SPECIFIED IT, AND THE BINDING FIRES ANYWAY. The locked spec said to
band realised payoff at its median. DCM's C factor is distinct outcome values over n, so
banding a continuous outcome to BINARY forces C = 2/2000 = 0.001 BY CONSTRUCTION and the
gate could not pass whatever the data did. On the unbanded payoff C would be 1.0000. That
number is a DIAGNOSIS, not a substitute verdict -- the gate is not re-scored, and X3, X4 and
X5 are reported UNINFORMATIVE exactly as the binding rule requires. Honouring a binding only
when convenient is the immunisation move the rule exists to stop.

SECOND CONSECUTIVE SELF-INFLICTED UN-PASSABLE GATE. In 6cb42dcd the cognitive arm could not
fail because noise was averaged away; here the self-audit could not pass because the outcome
was binarised. Different errors, same class: a threshold written without checking the
quantity could reach it. That is a pattern about this programme's spec-writing and it is
recorded as one.

WHAT DID HOLD, for whatever it is worth under the binding. X2 passed, so the earlier
could-not-fail failure mode did not recur -- payoff IQR 0.1815 against a floor of 0.02. X3
passed. X4's sign prediction held: corr(D_W, D_F) runs -0.6462 at the non-monotone extreme
to +1.0000 at the monotone one. But X4 TRIPS THE TOO-PERFECT RULE at m=0.75 and m=1.0, and
the reading is degeneracy rather than leakage -- when payoff is strictly increasing in the
world state the two references are the same ordering. Half (b) was disclosed as
near-definitional BEFORE the run for exactly this reason. Only the negative correlation at
m=0.0 carries information.

NOTHING HERE IS ABOUT PEOPLE. Four Hugging Face searches for human behavioural trial data
returned only text and multiple-choice QA corpora. X7 records UNTESTABLE-HERE. Every agent
is simulated.

THE TOOL ROLES, AND ONLY TWO COULD CHANGE A VERDICT. LISM supplied the rival in X5; DCM
supplied the self-audit in X6 with power to void the run. HELM, the Novora Suite screen and
Page Code audit the WRITE-UP and are excluded by X8, because a governance verdict on prose
is not evidence about agents. Claude Code wrote and locked the spec before the runner
existed; IHCEI carries the run. Recording this prevents the appearance that a large
toolchain was doing scientific work it was not doing.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "558f6fa11302867b7fd1dfc0254e45ad8a54544b74d1c2893d63c20ff1248787"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "crm.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_crm.json")))


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "crm_prereg.json")))


def test_spec_locked_and_stakes_CRMs_existence_on_beating_LISM():
    s = _spec()
    got = hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    x5 = [g for g in s["gates"] if g["id"] == "X5_CRM_BEATS_LISMS_OWN_TWO_HOP_FORM"][0]
    assert "the honest conclusion is to keep LISM and drop CRM" in x5["why"]
    assert x5["prediction"].startswith("AT GENUINE RISK")


def test_CRM_did_not_earn_its_existence():
    """X5, and the whole point of the run."""
    r = _r()
    assert "X5_CRM_BEATS_LISMS_OWN_TWO_HOP_FORM" in r["gates_not_met"]
    e = r["cv_mean_abs_error"]
    assert e["CRM_two_reference"] < e["LISM_two_hop"], "better, but not by enough"
    assert e["LISM_two_hop"] - e["CRM_two_reference"] < 0.005
    assert "DID NOT EARN ITS EXISTENCE" in r["primary_verdict"]


def test_the_harsher_unregistered_comparison_is_reported():
    """D_F alone is within 0.0003 of the two-reference model."""
    r = _r()
    e = r["cv_mean_abs_error"]
    assert e["D_F_alone"] - e["CRM_two_reference"] < 0.001
    d = r["post_run_disclosures"]["D7_X5_MISSED_AND_THE_SPEC_SAID_WHAT_THAT_MEANS"]
    assert "not pre-registered and scores nothing" in \
        d["and_a_harsher_reading_the_spec_did_not_lock"]
    assert "would flatter the model" in d["and_a_harsher_reading_the_spec_did_not_lock"]


def test_the_self_audit_was_mis_specified_and_the_binding_still_fires():
    r = _r()
    assert "X6_DCM_SELF_AUDIT" in r["gates_not_met"]
    a = r["dcm_self_audit"]
    assert a["C"] < 0.01, "C forced to 2/n by binarising a continuous outcome"
    d = r["post_run_disclosures"]["D6_X6_FAILED_BECAUSE_I_MIS_SPECIFIED_IT_AND_THE_BINDING_STILL_FIRES"]
    assert d["whose_error"].startswith("Mine.")
    assert "BY CONSTRUCTION" in d["what_went_wrong"]
    assert "not a substitute verdict" in d["diagnostic_only_NOT_a_re_score"]
    assert "UNINFORMATIVE" in d["THE_BINDING_IS_HONOURED_ANYWAY"]
    assert "UNINFORMATIVE" in r["primary_verdict"]


def test_the_second_consecutive_spec_error_is_named_as_a_pattern():
    r = _r()
    d = r["post_run_disclosures"]["D6_X6_FAILED_BECAUSE_I_MIS_SPECIFIED_IT_AND_THE_BINDING_STILL_FIRES"]
    assert "Second consecutive" in d["whose_error"]
    assert "6cb42dcd" in d["whose_error"]


def test_the_earlier_could_not_fail_flaw_did_not_recur():
    """X2 is the gate that would have caught the T2R error, and it passed."""
    r = _r()
    assert "X2_THE_FAILING_REGION_IS_POPULATED" not in r["gates_not_met"]
    assert r["iqr"]["payoff"] >= 0.02
    d = r["post_run_disclosures"]["D2_the_earlier_flaw_and_how_this_run_differs"]
    assert "AVERAGED" in d["what_went_wrong_in_6cb42dcd"]
    assert "DIRECTLY" in d["what_this_run_does"]


def test_the_sign_prediction_held_but_trips_the_too_perfect_rule():
    r = _r()
    c = r["corr_DW_DF_by_monotonicity"]
    assert c["0.0"] < 0 and c["1.0"] >= 0, "the sign flips with payoff monotonicity"
    assert "correlation_above_0.95" in r["too_perfect_flag"]
    d = r["post_run_disclosures"]["D8_X4_PASSED_BUT_TRIPS_THE_TOO_PERFECT_RULE"]
    assert "DEGENERACY" in d["note"] and "near-definitional" in d["note"]


def test_the_fidelities_never_read_the_outcome():
    src = open(os.path.join(HERE, "crm.py")).read()
    block = src.split("# ------------------------------------------------- the two reference fidelities")[1]
    block = block.split("# ------------------------------------------------------------- agents & world")[0]
    for banned in ("payoff\"", "realised", "cv_error", "total"):
        assert banned not in block, "the fidelity functions must not touch the outcome"


def test_nothing_is_claimed_about_people():
    r = _r()
    assert r["human_data_reachable"] is False
    x7 = [g for g in r["gates"] if g["id"] == "X7_anything_about_human_cognition"][0]
    assert x7["weight"] == "excluded" and "UNTESTABLE-HERE" in x7["detail"]
    assert r["post_run_disclosures"]["D4_what_this_says_about_people"]["statement"].startswith("NOTHING")


def test_only_LISM_and_DCM_could_change_a_verdict():
    r, s = _r(), _spec()
    d = r["post_run_disclosures"]["D5_only_two_tools_could_change_a_verdict"]
    assert len(d["could"]) == 2
    assert any("HELM" in x for x in d["could_not"])
    assert "not doing" in s["the_role_of_each_tool_declared_in_advance"][
        "the_honest_summary_of_these_roles"]
    # the governance layer ran and is recorded, and is excluded
    x8 = [g for g in r["gates"] if g["id"] == "X8_the_novora_governance_layer"][0]
    assert x8["weight"] == "excluded"
    assert r["novora_governance_audit"].get("helm_verdict") in ("PASS", "REVIEW", "FLAG",
                                                               "UNAVAILABLE")


def test_the_score_is_four_of_six():
    r = _r()
    assert r["score"] == "4/6"
    assert sorted(r["gates_not_met"]) == [
        "X5_CRM_BEATS_LISMS_OWN_TWO_HOP_FORM", "X6_DCM_SELF_AUDIT"]
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 6
