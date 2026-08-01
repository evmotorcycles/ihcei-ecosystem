"""
test_crossover.py -- locks the RT-to-Governance crossover on physics and cognition: 5/9.

TWO THEORIES WERE NAMED AND PRE-REGISTERED BEFORE ANY FIT.
  T2O  Two-Hop Objectivity   quantum arm, a DERIVATION from standard quantum mechanics
  T2R  Two-Hop Retention     cognitive arm, a SIMULATION

THE CROSSOVER PROTOCOL WAS FOLLOWED INCLUDING STEP 4. Step 1 states the RT reading at full
strength -- decoherence theory and quantum Darwinism for physics, the New Theory of Disuse
for cognition, both of which ALREADY have the structure the reframe proposes. Step 2 names
the channel. Step 3 re-derives a known result: the partial-information plateau, recovered
exactly, gate Q1. Step 4 produces the discriminating prediction, and both arms are assigned
one of the three verdicts.

THE QUANTUM ARM'S VERDICT WAS DECLARED BEFORE THE RUN: INTERPRETATION, NOT RIVAL THEORY.
The governance channel identification -- encode hop into the environment, decode hop into
an observer's fragment -- IS quantum Darwinism. It changes no prediction of physics.
Declaring the verdict in advance is what stopped a good numerical fit being presented
afterwards as a physical discovery. It also means the reframe landed on real structure
rather than inventing new structure, which is a modest validity check on the method and is
reported as a modest one.

Q3 FAILED DECISIVELY, AND THE SPEC PREDICTED IT IN WRITING.

    median absolute error against exact I(S:F)
      single-hop      U * D_enc                    0.0028 bits
      two-hop linear  U * D_enc * D_dec            0.5495 bits    ~195x worse
      quadratic       U * (D_enc * D_dec)^2        0.7709 bits

  The second hop is not merely dead weight. Including it makes the prediction dramatically
  worse. Q2 is recorded as MET because the linear form beat the quadratic one, but that
  pass is hollow and is reported as hollow: a gate can be met by beating a worse rival.

MY PREDICTION ABOUT WHERE IT WOULD FAIL WAS WRONG. The spec said the linear form would fail
in the saturation region at large fragments. It fails worst at SMALL fragments -- mean error
0.6787 at the smallest fraction against 0.3434 at the largest -- because redundancy means
one qubit in twenty already carries nearly all the classical information. Direction right,
location wrong. Recorded, not repaired.

WHAT THIS COSTS LISM, AND IT IS A REAL COST. The product form assumes the DECODE HOP IS
SCARCE. Where records are redundantly copied it is not scarce, and the product form is
wrong by two orders of magnitude. E = U * D_enc * D_dec now carries a stated domain limit.
This does not reverse the substrates where it was measured; it marks a boundary discovered
by carrying the form into a new field and having it fail.

THE COGNITIVE ARM COULD NOT FAIL, AND THAT IS MY ERROR. Recovery is 1.0000 in all 36
configurations and all 200 replicates. The locked design applies noise per participant and
then averages over the cell, so effective noise at the lowest setting is about 0.0045 --
far smaller than the gap between the two accounts everywhere. C3 is recorded as met and C4
as missed at a gap of exactly zero, and NEITHER IS INFORMATIVE. A test that cannot fail is
not evidence.

AND ONE SENTENCE OF THE SPEC IS WITHDRAWN. It said a C5 miss would be 'a real result
against DCM'. IT IS NOT. With recovery identically 1.0 there is no variation for DELTA to
predict, so the AUC is undefined rather than low. C5 scores as not met because the locked
rule says so, but its status is UNTESTABLE-HERE, not REFUTED. NOTHING IN THIS RUN IS
EVIDENCE FOR OR AGAINST DCM.

THE FIVE QUESTIONS. The claim asserted is narrow: each admits an operational reading that
names a measurable quantity, which is what makes a question governance-tractable. That is
Layer 2 and it is not evidence that any reading is correct. ONLY ONE OF THE FIVE -- Q3,
stewardship as a two-hop channel -- was put at risk by this run, and it lost. The other
four are recorded as untested.

ROOT ANALYSIS SUPPORTS NO NUMBER HERE. It produced the vocabulary and the hypothesis. It
adjudicates no gate and appears in no computation.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "6cb42dcd0147fce58eb63f16761ae0b7e98c63099b45af1f9d4d2965dd63e4b8"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "crossover.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_crossover.json")))


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "crossover_prereg.json")))


def test_spec_locked_and_step_4_is_mandatory():
    s = _spec()
    got = hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    p = s["THE_CROSSOVER_PROTOCOL_IS_BEING_FOLLOWED_INCLUDING_STEP_4"]
    assert "renaming, not reframing" in p["rule"]
    assert "determined by their gates" in p["verdicts_will_be_assigned_by_the_run"] \
        or "not by preference" in p["verdicts_will_be_assigned_by_the_run"]


def test_the_RT_reading_was_stated_at_full_strength_not_as_a_strawman():
    s = _spec()
    q = s["ARM_1_QUANTUM"]["step_1_the_RT_reading_at_full_strength"]
    assert "settled physics and is not in dispute" in q["decoherence_theory"]
    assert "ALREADY distinguishes" in q["why_this_matters_for_honesty"]
    c = s["ARM_2_COGNITIVE"]["step_1_the_RT_reading_at_full_strength"]
    assert "is not new and is not claimed as new" in c["standard_account"]


def test_the_known_result_was_re_derived_before_anything_was_claimed():
    """Q1, step 3 of the protocol. The plateau is a theorem, not a fitted artefact."""
    r = _r()
    assert "Q1_the_plateau_is_recovered" not in r["gates_not_met"]
    assert r["quantum_arm"]["n_points"] == 95 and r["quantum_arm"]["N_env"] == 20


def test_the_second_hop_was_refuted_and_the_spec_predicted_it():
    """Q3, and the sharpest result in the run."""
    r, s = _r(), _spec()
    assert "Q3_THE_SECOND_HOP_EARNS_ITS_KEEP" in r["gates_not_met"]
    e = r["quantum_arm"]["median_abs_error_bits"]
    assert e["single_hop"] < e["two_hop_linear"] < e["two_hop_quadratic"]
    assert e["two_hop_linear"] / e["single_hop"] > 100, "roughly 195x worse"
    assert r["quantum_arm"]["best_form"] == "single_hop"
    q3 = [g for g in s["ARM_1_QUANTUM"]["gates"]
          if g["id"] == "Q3_THE_SECOND_HOP_EARNS_ITS_KEEP"][0]
    assert "I expect the two-hop linear form to LOSE this gate" in q3["prediction"]


def test_the_Q2_pass_is_reported_as_hollow():
    r = _r()
    assert "Q2_TWO_HOP_LINEAR_BEATS_THE_QUADRATIC_RIVAL" not in r["gates_not_met"]
    d = r["post_run_disclosures"]["D6_THE_TWO_HOP_FORM_WAS_REFUTED_FOR_THIS_OBSERVABLE_AS_PREDICTED"]
    assert "met by beating a worse rival" in d["Q2s_pass_is_hollow_and_is_reported_as_such"]


def test_the_location_prediction_was_wrong_and_says_so():
    r = _r()
    q = r["quantum_arm"]
    assert q["linear_error_at_smallest_fragment"] > q["linear_error_at_largest_fragment"], \
        "failure is worst at SMALL fragments, opposite to the pre-declaration"
    d = r["post_run_disclosures"]["D7_MY_PREDICTION_ABOUT_WHERE_IT_WOULD_FAIL_WAS_WRONG"]
    assert "opposite of the pre-declaration" in d["observed"]
    assert "Recorded, not repaired" in d["recorded_not_repaired"] \
        or "not re-scored" in d["recorded_not_repaired"]


def test_the_domain_limit_this_puts_on_LISM_is_recorded():
    r = _r()
    d = r["post_run_disclosures"]["D8_WHAT_THIS_COSTS_LISM_AND_IT_IS_A_REAL_COST"]
    assert "DECODE hop is SCARCE" in d["finding"]
    assert "should not be applied" in d["domain_limit_now_on_the_record"]
    # and the limit is not overstated
    assert "does not refute the product form" in d["what_it_does_not_show"]


def test_the_quantum_verdict_was_declared_before_the_run():
    r, s = _r(), _spec()
    assert r["quantum_arm"]["verdict"].startswith("INTERPRETATION")
    q5 = [g for g in s["ARM_1_QUANTUM"]["gates"]
          if g["id"] == "Q5_the_verdict_under_the_crossover_protocol"][0]
    assert q5["verdict_declared_now"].startswith("INTERPRETATION")
    assert "recovers quantum Darwinism" in q5["reason"]
    # the no-go constraint is respected explicitly
    assert "Decoherence is not observation" in q5["hard_constraint_respected"]


def test_the_cognitive_arm_could_not_fail_and_it_is_owned():
    r = _r()
    assert "C2_the_failing_region_is_populated" in r["gates_not_met"]
    assert r["cognitive_arm"]["overall_recovery"] == 1.0
    d = r["post_run_disclosures"]["D9_THE_COGNITIVE_ARM_COULD_NOT_FAIL_AND_THAT_IS_MY_ERROR"]
    assert d["whose_error"].startswith("Mine.")
    assert "NEITHER IS INFORMATIVE" in d["consequence_for_C3_and_C4"]
    assert "square root of the cell size" in d["why"]


def test_the_C5_sentence_is_withdrawn_and_DCM_is_not_impugned():
    """The distinction that matters: UNTESTABLE-HERE is not REFUTED."""
    r = _r()
    assert "C5_DCM_DELTA_PREDICTS_WHICH_DESIGNS_DISCRIMINATE" in r["gates_not_met"]
    assert r["cognitive_arm"]["auc_dcm_delta"] is None, "undefined, not low"
    d = r["post_run_disclosures"]["D9_THE_COGNITIVE_ARM_COULD_NOT_FAIL_AND_THAT_IS_MY_ERROR"]
    w = d["consequence_for_C5_AND_THIS_MATTERS"]
    assert "THAT SENTENCE IS WITHDRAWN" in w
    assert "UNTESTABLE-HERE, not REFUTED" in w
    assert "evidence for or against DCM" in w


def test_derivation_and_simulation_are_kept_apart():
    r = _r()
    d = r["post_run_disclosures"]["D1_the_quantum_arm_is_derivation_the_cognitive_arm_is_simulation"]
    assert "Schroedinger equation" in d["quantum"]
    assert "NOTHING about human memory" in d["cognitive"]
    may = r["post_run_disclosures"]["D5_what_the_cognitive_arm_may_be_quoted_for"]
    assert "testing effect" in may["may_not"]


def test_only_one_of_the_five_questions_was_put_at_risk():
    r = _r()
    assert r["five_questions_tested_here"] == 1 and r["five_questions_total"] == 5
    d = r["post_run_disclosures"]["D3_three_of_the_five_questions_are_not_tested_here"]
    assert len(d["not_tested"]) == 4
    assert "Listing a reading is not answering a question" in d["note"]
    # and the spec's own framing of the governance claim is narrow
    s = _spec()["the_five_governance_questions_and_why_they_are_governance"]
    assert "NOT that the five questions are secular rather than religious" in s["layer"]
    assert "TRACTABILITY" in s["the_test_of_the_claim"]


def test_no_root_analysis_supports_any_number():
    r = _r()
    d = r["post_run_disclosures"]["D4_no_root_analysis_supports_any_number_here"]
    assert "adjudicates no gate" in d["note"]
    src = open(os.path.join(HERE, "crossover.py")).read()
    for w in ("Kh-L-Q", "Salat", "Zakat", "Al-Haqq", "As-Sidq", "jidhr"):
        assert w not in src, "no root vocabulary may appear in the computation"


def test_a_lab_experiment_is_specified_and_not_oversold():
    s = _spec()["ARM_1_QUANTUM"]["the_laboratory_experiment_this_arm_would_hand_to_a_physics_lab"]
    assert "HOLD THE TOTAL DECOHERENCE FACTOR" in s["protocol"]
    assert "Nothing about governance" in s["what_it_would_NOT_settle"]
    assert "NOT as an unprecedented one" in s["honest_note"]


def test_the_score_is_five_of_nine():
    r = _r()
    assert r["score"] == "5/9"
    assert sorted(r["gates_not_met"]) == sorted([
        "Q3_THE_SECOND_HOP_EARNS_ITS_KEEP",
        "C2_the_failing_region_is_populated",
        "C4_THE_INTERIOR_DESIGN_DOES_NOT",
        "C5_DCM_DELTA_PREDICTS_WHICH_DESIGNS_DISCRIMINATE"])
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 9
