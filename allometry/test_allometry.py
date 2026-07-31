"""
test_allometry.py -- locks the Tusko scaling test: 3/5.

WHAT WAS ASKED AND WHAT COULD BE REACHED. Three arms were requested: biological allometry,
multi-scale code and AI model lineages, and SME loan ledgers. TWO ARE BLOCKED AT THE EGRESS
GATEWAY and are recorded as blocked, never substituted:

    huggingface.co:443             403 to CONNECT (policy denial)
    datasets-server.huggingface.co 403 to CONNECT
    genomics.senescence.info:443   403 to CONNECT

GitHub repository endpoints outside this session's scope also answer 403, so no new
repositories could be sampled and the capacity floor is 99 stars rather than the 1 the
design called for. The 24-model frozen Hugging Face fixture in this repository was
DELIBERATELY NOT USED: it is a trending snapshot, not capacity-stratified, and a scaling
test on 24 models has no power to fail. BLOCKED is not REFUTED and is not UNTESTABLE-HERE.

WHAT RAN. 866 real public GitHub repositories with DIRECTLY MEASURED issue-close latency,
spanning 99 to 442,738 stars -- 3.65 orders of magnitude, populated in every decade
(44 / 362 / 185 / 253 / 22). The 126 imputed rows were excluded: an imputed latency is a
model output and cannot test how latency scales. Nothing was simulated.

THE PRIMARY GATE PASSED -- AND THE REFERENCE ARM REVERSES WHAT IT MEANS.

  G3 PASSED. Calibrating on the small decades and extrapolating to the largest:

        linear rule (dose proportional to mass -- the 1962 error)   4,406x error
        power law fitted on the small end                               42x error
        constant, i.e. assume nothing changes with scale               8.3x error

     The linear/power ratio is 2.24 against a locked bar of 2.0, so the gate is met. BUT
     THE CONSTANT MODEL BEATS BOTH. The locked spec required that outcome to be stated
     first, and it is.

  G4 FAILED, and this is the gate that kills the framing. Under 5-fold cross-validation
     the constant model's mean held-out error (0.4251 dex) is LOWER than the fitted power
     law's (0.4728). Capacity carries no usable predictive information about latency once
     within-decade spread is accounted for.

  G5 FAILED. Normalising by an exponent fitted on the middle decades cut the gap between
     the two held-out decades from 1.069 dex to 0.592 -- from 12-fold to 4-fold. Real
     flattening, but the locked bar was a factor of 2. There is no scale-invariant latency
     constant here; the 'one billion heartbeats' structure does not appear.

THE SHARPEST FINDING, WHICH IS A DISCLOSURE AND NOT A GATE. The power law fitted on the
small decades alone has exponent +0.3211. Fitted across all 866 rows it is -0.1741. THE
SIGN FLIPS. The 1962 error was using the wrong exponent, 1 instead of a fractional one.
This is worse: small-scale data supports the wrong DIRECTION. That is why extrapolating a
fitted law errs 42-fold while assuming no change errs 8-fold.

THE HONEST OPERATIONAL LESSON is therefore NOT 'use a power law instead of a linear rule'.
It is that a rule calibrated at one scale should not be extrapolated to another at all.

LAYER 3 BOUNDARY, ENFORCED BY TEST. Tusko and Kleiber generated this hypothesis and
supplied its vocabulary. Neither is evidence about software. No biological law is
confirmed anywhere in the output, and a test below asserts the results file claims none.

G6 SCORES NOTHING, BY PRIOR DISCLOSURE. Per-decade median latency was inspected while
checking feasibility, before the spec was locked. That fixes the exponent's sign, so a
gate on it could not have failed. It is reported without credit. G3, G4 and G5 depend on
out-of-sample error and within-decade spread, none of which was seen before the lock.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "6666f1a958139c6b661b6df61b42c5c2863d4bd7001ab60aa6599b03d8c32710"
BIO_CLAIMS = ("confirms kleiber", "obeys kleiber", "proves kleiber",
              "software obeys", "biological law confirmed", "same law as")


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "allometry.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_allometry.json")))


def test_spec_locked_and_discloses_the_pre_lock_inspection():
    spec = json.load(open(os.path.join(HERE, "prereg", "allometry_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    d = spec["DISCLOSURE_OF_WHAT_WAS_INSPECTED_BEFORE_THIS_LOCK"]
    assert "could not fail" in d["why_this_matters"]
    assert "SCORES NOTHING" in d["consequence_enforced_here"]
    # the biology boundary was declared before the run, not added afterwards
    assert "cannot confirm it" in \
        spec["the_idea_being_tested_and_where_it_came_from"]["the_boundary_being_enforced"]


def test_the_blocked_arms_are_recorded_not_substituted():
    r = _r()
    assert set(r["blocked_arms"]) == {
        "huggingface.co", "genomics.senescence.info",
        "github_repos_outside_session_scope"}
    for gid in ("G7_hugging_face_model_lineage_arm", "G8_biological_allometry_arm"):
        g = [x for x in r["gates"] if x["id"] == gid][0]
        assert g["weight"] == "excluded" and g["met"] is None
        assert "BLOCKED is not REFUTED" in g["detail"]
        assert "No substitute dataset was used" in g["detail"]
    # the 24-model HF fixture exists in the repo and was deliberately left alone
    spec = json.load(open(os.path.join(HERE, "prereg", "allometry_prereg.json")))
    hf = spec["what_this_session_could_and_could_not_reach"]["arm_2b_hugging_face"]
    assert "It is NOT used" in hf["what_exists_offline"]
    assert "24" in hf["what_exists_offline"]


def test_the_tusko_gate_passed_on_real_repositories():
    """G3. Linear extrapolation across 3.65 decades errs by four thousand fold."""
    r = _r()
    assert "G3_THE_TUSKO_GATE" not in r["gates_not_met"]
    t = r["tusko_extrapolation"]
    assert t["linear_fold_error"] > 4000 and t["power_fold_error"] < 50
    assert t["linear_over_power"] >= 2.0
    assert t["n_calibration"] == 406 and t["n_target"] == 22


def test_but_the_constant_model_beats_both_and_is_stated_first():
    """The spec required this outcome to lead if it occurred. It occurred."""
    r = _r()
    t = r["tusko_extrapolation"]
    assert t["constant_fold_error"] < t["power_fold_error"] < t["linear_fold_error"]
    d = r["post_run_disclosures"]["D6_THE_CONSTANT_MODEL_WINS_BOTH_COMPARISONS"]
    assert "IT DID, in both" in d["stated_first_as_the_spec_required"]
    assert "should not be extrapolated" in d["the_honest_conclusion"]


def test_capacity_does_not_predict_latency_under_cross_validation():
    """G4, the gate the pre-registration said it would bet against."""
    r = _r()
    assert "G4_the_power_law_beats_a_constant_under_cross_validation" in r["gates_not_met"]
    cv = r["cross_validation"]
    assert cv["mean_constant"] < cv["mean_power"], "the constant won the CV outright"
    assert len(cv["power_dex_per_fold"]) == 5 and cv["seed"] == 20260801


def test_there_is_no_scale_invariant_latency_constant():
    """G5. Normalising flattens 12-fold to 4-fold, and the bar was 2-fold."""
    r = _r()
    assert "G5_HELD_OUT_SCALE_INVARIANCE" in r["gates_not_met"]
    h = r["held_out_invariance"]
    assert h["gap_raw_dex"] > h["gap_normalised_dex"] > 0.301, \
        "real flattening, still short of a factor of two"
    assert "billion heartbeats" in \
        r["post_run_disclosures"]["D7_G5_flattened_the_gap_but_not_to_invariance"]["note"]


def test_the_small_scale_slope_points_the_wrong_way():
    """The sharpest result in the run, carried as a disclosure rather than a gate."""
    r = _r()
    d = r["post_run_disclosures"]["D5_THE_CALIBRATION_SLOPE_HAS_THE_OPPOSITE_SIGN_TO_THE_GLOBAL_SLOPE"]
    small = d["alpha_fitted_on_the_small_decades_1e1_1e2"]
    whole = d["alpha_over_all_866_measured_rows"]
    assert small > 0 > whole, "the sign flips between the small end and the full range"
    assert r["alpha_all_measured"] == whole


def test_the_exponent_gate_scores_nothing_because_it_was_seen_first():
    r = _r()
    g6 = [g for g in r["gates"] if g["id"] == "G6_the_exponent_itself"][0]
    assert g6["weight"] == "descriptive" and g6["met"] is None
    assert "SCORES NOTHING" in g6["detail"]
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 5


def test_no_biological_confirmation_is_claimed():
    r = _r()
    scan = json.dumps(r).lower()
    for w in BIO_CLAIMS:
        assert w not in scan, "found a biological confirmation claim: %s" % w
    assert r["post_run_disclosures"]["D2_what_the_sign_of_alpha_means"][
        "no_biological_confirmation_is_claimed"] is True
    assert "is not evidence" in r["post_run_disclosures"]["D2_what_the_sign_of_alpha_means"][
        "the_biological_parallel_is_LAYER_3_AND_SCORES_NOTHING"]


def test_censoring_is_retained_and_its_effect_shown():
    r = _r()
    d = r["post_run_disclosures"]["D1_censoring_and_bot_closures_retained"]
    assert d["at_the_365_day_ceiling"] == 5 and d["below_0_01_days"] == 6
    assert "RETAINED" in d["note"]
    assert "-0.1812" in d["effect_if_they_were_dropped"], "sensitivity shown, not applied"


def test_nothing_was_simulated_and_imputed_rows_were_dropped():
    r = _r()
    assert r["simulated_quantities"] == 0
    assert r["n_measured"] == 866 and r["n_imputed_excluded"] == 126
    assert r["stars_range"] == [99, 442738] and r["orders_of_magnitude"] > 3.6


def test_the_score_is_three_of_five():
    r = _r()
    assert r["score"] == "3/5"
    assert sorted(r["gates_not_met"]) == [
        "G4_the_power_law_beats_a_constant_under_cross_validation",
        "G5_HELD_OUT_SCALE_INVARIANCE"]
