"""
test_lic.py -- locks the licensing run for Q3, Q4 and Q5.

    Q4  5/5   LICENSED
    Q3  3/4 in v1 (my control was implemented wrong), 4/4 in v2 -- LICENSED, narrowly
    Q5  3/4   PRIMARY REFUTED, and it is the arm the proposal was most confident about

THREE CORRECTIONS THE SPEC RECORDS BEFORE ANY RESULT.

 1. The proposal said Rule 110 defeated tau_v because a static oracle reached AUC ~0.99,
    leaving no headroom. Spec 0cd701a4 measured static prediction on the IRREDUCIBLE arm at
    0.4940 -- chance. The ~1.0 figures belong to the REDUCIBLE rules, which P5 never scored.
 2. The proposal cited tau_v at 19.8 vs 50.6 days. Those are MEANS from the smaller
    four-cohort study. On this committed file the MEDIANS are 20.53 vs 32.37 and the MEANS
    are 44.11 vs 47.00 -- nearly identical, the mean being dominated by a long tail.
 3. The proposal licensed Q3 on 10,000-event runs from three-proposals/. That is OUR OWN
    SIMULATOR. Q3 was re-scoped to the part that is falsifiable on real data.

Q4 -- THE ONE THAT WORKED, AND IT CLOSES SOMETHING HELM COULD NOT.

    AUC(execution kernel, declared correctness)   1.0000     bar 0.95
    AUC(HELM oriented verdict, correctness)       0.5365     bar 0.65  -- chance
    Spearman(kernel verdict, word count)         +0.0226     bar 0.20
    Spearman(HELM verdict, word count)           +0.2804     (-0.4831 on spec 5576e524)
    DCM DELTA = V 0.6000 * I 1.0000 * C 0.6500 =  0.3900     floor 0.20

  The DCM floor is CLEARED for the first time in six runs, and it was not moved to get
  there. Spec 5576e524's W8 -- does the evaluator respond to the RIGHT content -- was
  UNTESTABLE-HERE because manipulativeness has no ground truth. CODE CORRECTNESS DOES.
  That is the whole reason this arm closes what HELM's could not.

  Two confounds were found and removed BEFORE the lock: a first draft had
  Spearman(word count, correct) = +0.3547 and Spearman(self-certifying, correct) = -0.7917.
  The ARTIFACTS were rewritten, never a threshold. Residuals: +0.0177 and 0.0000.

  The kernel's AUC of exactly 1.0000 is FLAGGED by the too-perfect rule, and its perfect
  insensitivity to self-report scores NOTHING -- it is true by construction, and a quantity
  that cannot come out otherwise is not evidence.

Q5 -- REFUTED, AND THE FAILURE SURVIVES ITS OWN CONFOUND.

    AUC(STATIC: stars, U)      0.8000
    AUC(PROCESS: tau_v)        0.5947
    process - static          -0.2053     bar +0.05

  tau_v is 0.205 WORSE than stars and leverage, and COMBINED (0.7998) is no better than
  static alone, so tau_v adds nothing. The proposal's claim that "star counts fail to
  predict long-term maintenance survival" is not what this cohort holds.

  The cohort IS confounded: S4_failed is 100 percent archived, so the strata were built
  using the outcome. The failure is reported as measured -- a primary is not retracted
  because a reason was later found why it might have been unfair to one arm -- and the
  post-hoc check shows it SURVIVES: with S4 removed, static still wins 0.6801 to 0.5850.

  Q5_E is EXCLUDED: tau_v was harvested with no cutoff before archiving, so on this cohort
  it is CONTEMPORANEOUS, not leading. No gate here can separate the two.

Q3 -- LICENSED AT THE NARROW CLAIM ONLY.

  v1 scored 3/4 because Q3_D bootstrapped ONE fixed permutation instead of drawing many,
  which estimates the spread around that one permutation rather than the permutation null.
  The defect is mine. v1 is published unchanged and is NOT re-scored; the correction lives
  in a new spec, and not one threshold moved.

    SYSTEMIC 0.3653 vs ROUTINE 0.1946, difference +0.1707, bar +0.10
    permutation null over 2000 draws: mean +0.00093, band [-0.0548, +0.0613], p < 0.0005

  This licenses that the classification separates realised risk. It does NOT license that
  assigning Al-Qudah's instrument to one class and Irfan's to the other helps anyone --
  that is an intervention, and Q3v2_E records it as untestable here.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = "cd429dfa5208403d142f49d5ca8f6e4e09d8ce01dc6065c3e8892608dd8c4a9f"
V2 = "d7184ef95c804eb896488099412fe11406c03d7890abc652968e27310c263efd"
_C = {}


def _run(script, out):
    if script not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C[script] = json.load(open(os.path.join(HERE, out)))
    return _C[script]


def r1():
    return _run("lic.py", "results_lic.json")


def r2():
    return _run("q3v2.py", "results_q3v2.json")


def rd():
    return _run("diagnose.py", "results_lic_posthoc.json")


def _spec(n):
    return json.load(open(os.path.join(HERE, "prereg", n)))


def _sha(s):
    return hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_both_specs_are_locked():
    assert _sha(_spec("licensing_prereg.json")) == V1
    assert _sha(_spec("licensing_v2_prereg.json")) == V2
    assert _spec("licensing_v2_prereg.json")["supersedes"] == V1


def test_the_spec_records_the_three_corrections_to_the_proposal():
    c = _spec("licensing_prereg.json")["TWO_CORRECTIONS_TO_THE_PROPOSAL_THIS_SPEC_IMPLEMENTS"]
    assert "0.4940 -- chance" in c["correction_1_the_ceiling_explanation_is_backwards"]
    assert "REDUCIBLE rules" in c["correction_1_the_ceiling_explanation_is_backwards"]
    assert "MEANS from the smaller four-cohort study" in c["correction_2_the_tau_v_figures"]
    assert "OUR OWN SIMULATOR" in c["correction_3_Q3_cannot_be_licensed_by_a_simulator"]


def test_no_simulator_of_ours_is_used_anywhere():
    s = _spec("licensing_prereg.json")
    assert "three-proposals engine is deliberately not used" in s["simulator_rule"]
    # check actual USE, not the word: it appears in docstrings saying it is NOT used
    for f in ("lic.py", "q3v2.py", "diagnose.py"):
        src = open(os.path.join(HERE, f)).read()
        code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
        for banned in ("three-proposals/", "results_three", "settlement-mesh"):
            assert banned not in code, (f, banned)


# ------------------------------------------------------------------ Q4

def test_Q4_THE_EXECUTION_KERNEL_DISCRIMINATES_CORRECTNESS():
    r = r1()
    assert r["arms"]["Q4"]["score"] == "5/5"
    assert r["Q4"]["auc_kernel_vs_correctness"] >= 0.95


def test_Q4_HELM_DOES_NOT_and_that_is_the_contrast():
    r = r1()
    a = r["Q4"]["auc_helm_vs_correctness"]
    assert a <= 0.65
    assert abs(a - 0.50) < 0.10, "HELM is at chance on correctness, not merely below the bar"


def test_Q4_the_length_confound_is_gone_for_the_kernel():
    r = r1()
    assert abs(r["Q4"]["spearman_kernel_vs_wordcount"]) <= 0.20
    assert abs(r["Q4"]["spearman_kernel_vs_wordcount"]) < \
        abs(r["Q4"]["spearman_helm_vs_wordcount"])


def test_Q4_CLEARS_THE_DCM_FLOOR_FOR_THE_FIRST_TIME_AND_IT_WAS_NOT_MOVED():
    r = r1()
    d = r["Q4"]["dcm"]
    assert d["floor"] == 0.20, "the same floor that voided five runs"
    assert d["DELTA"] >= 0.20
    assert "Q4_E_DCM_SELF_AUDIT_ON_THE_KERNEL" not in r["gates_not_met"]


def test_Q4_the_kernel_scores_nothing_for_ignoring_self_report():
    """True by construction is not evidence."""
    r = r1()
    g = [x for x in r["gates"] if x["id"] == "Q4_F_the_kernel_ignores_self_report"][0]
    assert g["weight"] == "excluded" and g["met"] is None
    assert "true by construction" in g["detail"]
    assert "holds" in g["detail"], "the source-level assertion was verified"


def test_Q4_the_perfect_score_is_flagged_not_celebrated():
    r = r1()
    assert "Q4_kernel_AUC_at_1.0" in r["too_perfect_flag"]


def test_Q4_the_two_confounds_were_removed_before_the_lock():
    s = _spec("licensing_prereg.json")["Q4_the_execution_kernel"][
        "THE_TWO_CONFOUNDS_I_BUILT_IN_AND_REMOVED_BEFORE_LOCKING"]
    assert "+0.3547" in s["found_by_the_preflight"]
    assert "-0.7917" in s["found_by_the_preflight"]
    assert s["after_the_fix"]["spearman_selfcertifying_vs_correct"] == 0.0
    assert "artifacts were changed, never a threshold" in s["note"].lower()


def test_Q4_the_edge_cases_were_locked_so_the_bank_could_not_be_tuned():
    s = _spec("licensing_prereg.json")["Q4_the_execution_kernel"][
        "THE_HELD_OUT_TEST_BANK_AND_WHY_ITS_EDGE_CASES_ARE_LOCKED_HERE"]
    assert "self-fulfilling" in s["the_risk"]
    assert len(s["locked_edge_cases"]) == 4
    assert r1()["Q4"]["n_tests_in_bank"] > 200


def test_Q4_does_not_claim_to_generalise_to_prose():
    r = r1()
    g = [x for x in r["gates"] if x["id"] == "Q4_G_does_this_generalise_beyond_code"][0]
    assert g["weight"] == "excluded" and "UNTESTABLE-HERE" in g["detail"]
    assert "still needs independent raters" in g["detail"]


# ------------------------------------------------------------------ Q5

def test_Q5_THE_PRIMARY_WAS_REFUTED():
    r = r1()
    assert "Q5_C_PRIMARY_PROCESS_BEATS_STATIC" in r["gates_not_met"]
    assert r["Q5"]["process_minus_static"] < 0, "tau_v is WORSE than static, not merely tied"
    assert r["Q5"]["auc_static"] > r["Q5"]["auc_process"]


def test_Q5_the_ablation_held_so_the_refutation_is_interpretable():
    r = r1()
    assert "Q5_B_ABLATION_THE_STATIC_ARM_IS_ABOVE_CHANCE" not in r["gates_not_met"]
    assert "Q5_D_THE_SHUFFLED_LABEL_CONTROL_IS_AT_CHANCE" not in r["gates_not_met"]


def test_Q5_tau_v_adds_nothing_to_static():
    r = r1()
    assert r["Q5"]["auc_combined"] <= r["Q5"]["auc_static"] + 0.01


def test_Q5_THE_FAILURE_SURVIVES_THE_COHORT_CONFOUND():
    """S4_failed is 100% archived; the strata were built using the outcome."""
    d = rd()["Q5_the_cohort_is_confounded_by_its_own_construction"]
    assert d["strata"]["S4_failed"]["archived_share"] == 1.0
    sub = d["S4_EXCLUDED_rerun"]
    assert sub["auc_static"] > sub["auc_process"], "static still wins with S4 removed"
    assert sub["process_minus_static"] < 0
    assert "not an artefact of cohort construction" in d["THE_FAILURE_SURVIVES_THE_CONFOUND"]


def test_Q5_leading_indicator_stays_untestable():
    r = r1()
    g = [x for x in r["gates"] if x["id"] == "Q5_E_is_tau_v_a_LEADING_indicator"][0]
    assert g["weight"] == "excluded" and "CONTEMPORANEOUS" in g["detail"]


# ------------------------------------------------------------------ Q3

def test_Q3_v1_control_failed_and_is_not_re_scored():
    r = r1()
    assert "Q3_D_THE_PERMUTATION_CONTROL_IS_NULL" in r["gates_not_met"]
    assert r["arms"]["Q3"]["score"] == "3/4"
    d = rd()["Q3_the_permutation_control_was_implemented_wrong"]
    assert "bootstrapped ONE fixed permutation" in d["WHAT_THE_RUNNER_DID_WRONG"]
    assert "NOT retroactively passed" in d["AND_THE_GATE_STILL_COUNTS_AS_FAILED"]


def test_Q3_v2_corrected_the_control_and_moved_no_threshold():
    w = _spec("licensing_v2_prereg.json")["WHAT_WENT_WRONG_IN_V1_AND_IT_WAS_MY_RUNNER_NOT_THE_DATA"]
    assert "Not one threshold" in w["WHAT_IS_NOT_CHANGED"]
    assert "defect in my runner, not a property of the data" in w["the_consequence"]
    src = open(os.path.join(HERE, "q3v2.py")).read()
    assert "MIN_N, MIN_EV, MARGIN, N_BOOT, N_PERM, SEED = 50, 10, 0.10, 2000, 2000, 20260803" in src


def test_Q3_v2_THE_CLASSIFICATION_SEPARATES_REALISED_RISK():
    r = r2()
    assert r["score"] == "4/4" and r["gates_not_met"] == []
    assert r["rate_difference"] >= 0.10
    assert r["systemic"]["rate"] > r["routine"]["rate"]
    b = r["bootstrap_CI90"]
    assert b[0] > 0, "the bootstrap interval excludes zero"


def test_Q3_v2_the_corrected_null_is_centred_on_zero_and_the_observation_is_outside():
    r = r2()
    n = r["permutation_null"]
    assert n["contains_zero"] is True and n["observed_outside_band"] is True
    assert abs(n["mean"]) < 0.01, "a proper permutation null sits on zero"
    assert n["one_sided_p"] < 0.005


def test_Q3_does_not_claim_the_policy_assignment_helps_anyone():
    r = r2()
    g = [x for x in r["gates"]
         if x["id"] == "Q3v2_E_does_the_fixed_policy_ASSIGNMENT_improve_outcomes"][0]
    assert g["weight"] == "excluded" and "intervention" in g["detail"]
    assert "It does NOT follow" in r["primary_verdict"]


# ------------------------------------------------------------------ overall

def test_the_three_arms_are_scored_separately():
    r = r1()
    assert set(r["arms"]) == {"Q3", "Q4", "Q5"}
    assert r["arms"]["Q4"]["score"] == "5/5"
    assert r["arms"]["Q5"]["score"] == "3/4"
    assert r["simulated_values"] == 0
