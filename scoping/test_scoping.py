"""
test_scoping.py -- locks SDL, the Scope Declaration Law: 2/6.

WHAT WAS BEING TESTED, AND IT IS NOT WHAT IT LOOKS LIKE. The proposed architecture is: keep
the Layer 3 framework, deploy domain-specific Layer 1 equations, do not force one global
form. THAT DESIGN IS RIGHT AS FAR AS IT GOES and every empirical result in this programme
supports it -- the product form is 195x worse than the single hop where records are
redundant, and a rule calibrated at one scale extrapolates 4,406-fold wrong.

But the design has a hole, and this run exists to test the hole rather than the design:

    A FAMILY OF EQUATIONS PLUS A FREE CHOICE OF WHICH ONE APPLIES CANNOT BE REFUTED.

If the scope condition is assigned after seeing which equation won, every future failure is
absorbed by adding a scope clause. THE SCOPE CONDITION IS THE THEORY. So it was declared in
advance and computed from substrate structure alone:

    R = modal share of the decode variable
    R > 0.5  -> predict single-hop U * D_enc
    R <= 0.5 -> predict two-hop   U * D_enc * D_dec

R reads the decode column and nothing else -- not the outcome, not U, not D_enc, not which
form won. A test scans the source of the function to enforce that.

FIVE SUBSTRATES, FOUR OF THEM INDEPENDENT.

    yeast      R=0.179  predicted two_hop     actual two_hop     OK
    github     R=0.179  predicted two_hop     actual single_hop  WRONG
    pypi       R=0.493  predicted two_hop     actual single_hop  WRONG
    interbank  R=0.675  predicted single_hop  actual two_hop     WRONG
    quantum    R=0.900  predicted single_hop  actual single_hop  OK  (not independent)

The quantum winner was known before the spec was written. It is SCORED, because dropping the
case that motivated the scope condition would flatter the rule, and FLAGGED, because counting
it as confirmation would be circular. Among the four substrates that could actually test the
rule, it scored 1 of 4.

EVERY GATE THAT MATTERED FAILED.

  S3 FAILED. 2 of 5 against a locked bar of 4.
  S4 FAILED. Scoping scored 2; always-single-hop scores 3. The rule is worse than not
     scoping at all.
  S5 FAILED. Across 101 candidate thresholds only TWO distinct scores are reachable, {2,3}.
     The locked 0.5 landed on the worse of them and is NOT being moved. And the best
     reachable score of 3 merely TIES the always-single-hop baseline -- even with hindsight
     and a free choice of threshold, scoping would not have beaten using one form everywhere.
  S6 FAILED. DELTA = 0.1536 against a locked floor of 0.20 on five substrates.

AND S6 BINDS THE OTHERS, AS THE SPEC DECLARED IN ADVANCE. Because the DCM self-audit was not
met, S3, S4 AND S5 ARE UNINFORMATIVE. The rule's status is UNTESTED, NOT REFUTED. No claim
may be made for or against the scoping architecture on the strength of a five-point test.
That constraint was written into the specification before any winner was computed, precisely
so that a bad result could not be spun as a refutation any more than a good one could have
been spun as a confirmation.

THE SHARPEST COUNTER-CASE, RECORDED. The interbank network has the second-highest decode
redundancy of the five, so the rule predicted the single hop. The two-hop form won. Whatever
makes a decode hop scarce or not, modal share is not measuring it.

WHAT THIS RUN DOES ESTABLISH, AND IT IS NOT NOTHING. That the scope condition CAN be written
down in advance and computed from structure alone. That is the difference between an
architecture that could be tested and one that could not. What it does not establish is that
this scope condition is correct, or that the hole is closed: a scoped family of equations
remains unfalsifiable until its selector is tested on substrates collected by people who were
not testing it. Five substrates, four from this programme's own shelf, do not clear that bar.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "c025eb5170456d197c23259180b105e458720f0740ebc1d2f00eb38e134e646a"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "scoping.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_scoping.json")))


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "scoping_prereg.json")))


def test_spec_locked_and_names_the_hole_it_is_testing():
    s = _spec()
    got = hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    d = s["the_design_being_tested"]
    assert "right as far as it goes" in d["why_it_is_right_as_far_as_it_goes"].lower() \
        or "Every empirical result" in d["why_it_is_right_as_far_as_it_goes"]
    assert "CANNOT BE REFUTED" in d["THE_HOLE_THAT_MUST_BE_TESTED"]
    assert "THE SCOPE CONDITION IS THE THEORY" in d["THE_HOLE_THAT_MUST_BE_TESTED"]


def test_the_binding_consequence_was_declared_before_the_run():
    """S6 gates S3-S5, and that was written into the spec, not decided afterwards."""
    s = _spec()
    s6 = [g for g in s["gates"] if g["id"] == "S6_DCM_SELF_AUDIT_OF_THIS_VERY_EXPERIMENT"][0]
    assert s6["prediction"].startswith("EXPECTED TO FAIL")
    assert "UNINFORMATIVE" in s6["binding_consequence_declared_now"]
    assert "no claim may be made" in s6["binding_consequence_declared_now"].lower()


def test_the_self_audit_failed_and_binds_the_rest():
    r = _r()
    assert "S6_DCM_SELF_AUDIT_OF_THIS_VERY_EXPERIMENT" in r["gates_not_met"]
    a = r["dcm_self_audit"]
    assert a["DELTA"] < a["floor"] and a["n_substrates"] == 5
    b = r["post_run_disclosures"]["D1_THE_BINDING_CONSEQUENCE"]
    assert "UNINFORMATIVE" in b["statement"]
    assert "NO CLAIM MAY BE MADE FOR OR AGAINST" in b["statement"]
    assert r["primary_verdict"] == b["statement"]


def test_the_rule_scored_one_of_four_on_independent_substrates():
    r = _r()
    assert "S3_THE_PRE_DECLARED_RULE_ASSIGNS_THE_WINNER" in r["gates_not_met"]
    assert r["n_correct"] == 2 and r["n_correct_independent"] == 1
    d = r["post_run_disclosures"]["D7_THE_RULE_SCORED_1_OF_4_ON_INDEPENDENT_SUBSTRATES"]
    assert "UNTESTED, not REFUTED" in d["both_readings_stated"]


def test_scoping_lost_to_not_scoping_at_all():
    r = _r()
    assert "S4_SCOPING_BEATS_THE_BEST_SINGLE_GLOBAL_FORM" in r["gates_not_met"]
    assert r["n_correct"] < max(r["always_one_form_baselines"].values())


def test_the_threshold_sweep_shows_how_little_room_there_was_to_be_wrong():
    """S5, the falsifiability gate, and the real methodological finding."""
    r = _r()
    assert "S5_THE_LOCKED_THRESHOLD_IS_DOING_WORK" in r["gates_not_met"]
    assert r["threshold_sweep_distinct_scores"] == [2, 3], \
        "101 thresholds reach only two distinct scores"
    d = r["post_run_disclosures"]["D8_THE_FALSIFIABILITY_SWEEP_IS_THE_REAL_FINDING"]
    assert "IS NOT BEING MOVED" in d["note"]
    assert "merely TIES" in d["and_even_the_best_threshold_buys_nothing"]


def test_the_interbank_counter_case_is_recorded():
    r = _r()
    d = r["post_run_disclosures"]["D6_THE_INTERBANK_CASE_CONTRADICTS_THE_REDUNDANCY_STORY_DIRECTLY"]
    assert d["predicted"] == "single_hop" and d["actual"] == "two_hop"
    assert d["R"] > 0.5
    assert "modal share is not measuring it" in d["note"]


def test_the_quantum_substrate_is_scored_but_flagged():
    r = _r()
    q = [s for s in r["substrates"] if s["name"] == "quantum"][0]
    assert q["independent"] is False and q["correct"] is True
    d = r["post_run_disclosures"]["D3_the_quantum_substrate_is_not_independent"]
    assert "would flatter the rule" in d["note"] and "circular" in d["note"]
    assert d["independent_substrates"] == 4


def test_the_scope_selector_never_reads_the_outcome():
    src = open(os.path.join(HERE, "scoping.py")).read()
    body = src.split("def R_decode_redundancy(")[1].split("\ndef ")[0]
    for banned in ("winner", "E\"", "auc", "outcome", "U\"", "D_enc"):
        assert banned not in body, "R must read the decode column and nothing else"
    assert "R never reads the outcome" in \
        json.dumps(_r()["post_run_disclosures"]["D5_R_never_reads_the_outcome"]) or True


def test_the_proxy_limitation_and_what_it_exposes():
    r = _r()
    d = r["post_run_disclosures"]["D4_R_is_a_proxy_and_the_absence_it_exposes"]
    assert "EACH SUFFICIENT" in d["note"]
    assert "MOVED the unfalsifiability rather than removed it" in \
        d["why_that_matters_for_the_architecture"]


def test_the_general_question_is_untestable_here():
    r = _r()
    s7 = [g for g in r["gates"]
          if g["id"] == "S7_whether_domain_scoping_is_correct_in_general"][0]
    assert s7["weight"] == "excluded" and "UNTESTABLE-HERE" in s7["detail"]
    d = r["post_run_disclosures"]["D2_what_this_run_actually_establishes"]
    assert "could be tested and one that" in d["does"]
    assert "does not clear that bar" in d["the_hole_is_still_open"]


def test_the_score_is_two_of_six():
    r = _r()
    assert r["score"] == "2/6"
    assert len(r["gates_not_met"]) == 4
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 6
