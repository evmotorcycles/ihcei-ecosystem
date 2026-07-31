"""
test_dcm.py -- locks DCM, the Discriminating Capacity Model: 5/6.

WHAT DCM IS. Novora's second open-source model. LISM asks what makes an institution stable.
DCM asks the prior question: given a dataset and a claim, can that dataset distinguish the
claim from its rival at all?

    DELTA = V * I * C

    V   1 - modal fraction of the outcome      the outcome never moves
    I   4p(1-p) on the group split             no populated failing region
    C   distinct outcome values / n            administrative, not measured

WHERE IT CAME FROM. From this programme's NULLS, which outnumbered its passes and shared a
structure that had nothing to do with whether the mechanism was real. The contract
schedules held an asset value of exactly 400,000 in every row. The outcome panels wrote
down exactly -85.0% at every event while the asset moved under 2%. Kuwait and Palestine
booked exactly zero equity income across all 12 and all 21 of their quarters. The interbank
network had no column in 74 distinguishing a fixed claim from a participation. In none of
those was a model shown to be wrong -- the data was shown to be incapable. Sample size was
never the problem: the outcome panels had 720 rows.

WHAT RAN. 400 sub-datasets of REAL ROWS drawn from two real open-source substrates -- 866
GitHub repositories with measured issue-close latency, and 540 PyPI packages. Detection is
a seeded 200-draw label permutation, so the null is self-contained. V, I and C never read
the association between group and outcome. No mechanism is simulated.

RESULTS.

  K3 PASSED, the primary. AUC(DELTA) = 0.9442 against a locked 0.70.

  K4 PASSED, AGAINST THE WRITTEN PREDICTION. The spec recorded this as expected to fail,
     because sample size is the incumbent explanation and varies 16-fold across the grid.
     DELTA scored 0.9442 against n's 0.6700. That is a genuine surprise and it is the
     strongest result in the run.

  K5 FAILED -- AND IT IS THE GATE THAT TESTED THE MODEL'S ACTUAL CONTENT. The
     pre-registration named multiplicativity as 'the substantive and falsifiable content of
     the model'. V ALONE SCORES 0.9207 AGAINST THE PRODUCT'S 0.9442, an improvement of
     0.0235 against a locked bar of 0.03. On this evidence a one-factor model -- does the
     outcome actually move? -- does nearly all the work. The formula is NOT being rewritten
     to fit this; DCM is reported as specified with K5 failed.

  K6 PASSED but must not be read as support. Only 4 of 200 PyPI sub-datasets detected
     anything, so its 0.669 AUC rests on 4 positive cases and clears the 0.65 bar by 0.019.
     The gate stands because the threshold was locked; the weakness is disclosed.

THE POOLED AUC IS PARTLY A SUBSTRATE LABEL. 0.9442 sits just under the 0.95 too-perfect
trigger and is not the model's accuracy. GitHub is naturally clean and PyPI naturally
degenerate. The honest figures are the within-substrate ones: 0.8754 and 0.6690.

THE CLEAREST DEMONSTRATION SCORES NOTHING. Coarsening the RECORDING while leaving the
relationship untouched drops detection from 29.0% to 5.5% to 0.5%. The effect was still
there and the data stopped being able to see it. That arm is controlled degradation of real
data, is excluded by the locked spec, and is quoted for the detection collapse only -- its
AUCs rest on 2 and 22 events and are meaningless.

WHAT A LOW DELTA DOES NOT MEAN. It says THIS DATASET CANNOT SETTLE THIS QUESTION. It never
says the claim is false. Using DELTA to dismiss a claim would inertly invert the model's
purpose, which is to stop nulls being read as refutations.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "3a33d53e178b9c6f9178a77fe9d2e60780eff74d63c5606878b8bf61f9947ffe"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "dcm.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_dcm.json")))


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "dcm_prereg.json")))


def test_spec_locked_and_the_model_is_named_and_positioned():
    s = _spec()
    got = hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    assert s["model_name"].startswith("DCM")
    pos = s["position_in_the_novora_open_source_programme"]
    assert "does not replace it" in pos["this_model"]
    # the lineage to LISM is declared as structural, never evidential
    assert "It inherits no evidence" in s["the_model"]["lineage_to_LISM_is_STRUCTURAL_not_evidential"]


def test_the_model_was_built_from_the_nulls_and_they_are_cited_with_hashes():
    s = _spec()
    nulls = s["the_telemetry_this_model_was_built_from"]["nulls"]
    assert len(nulls) >= 6
    for key in nulls:
        assert "(" in key or "submesh" in key, "each null carries its spec hash"
    assert "720 rows" in s["the_telemetry_this_model_was_built_from"]["the_pattern"], \
        "sample size was never the problem"


def test_the_primary_gate_passed():
    r = _r()
    assert "K3_DELTA_PREDICTS_DETECTION" not in r["gates_not_met"]
    assert r["auc"]["delta"] >= 0.70
    assert r["n_natural_subdatasets"] == 400


def test_delta_beat_sample_size_against_the_written_prediction():
    """K4. The spec recorded this as expected to fail. It passed."""
    r, s = _r(), _spec()
    k4 = [g for g in s["gates"] if g["id"] == "K4_DELTA_BEATS_SAMPLE_SIZE"][0]
    assert k4["prediction"].startswith("EXPECTED TO FAIL")
    assert "K4_DELTA_BEATS_SAMPLE_SIZE" not in r["gates_not_met"]
    assert r["auc"]["delta"] - r["auc"]["n_rows"] >= 0.05


def test_the_multiplicative_claim_did_not_earn_its_keep():
    """K5, the gate that tested what the model actually asserts."""
    r = _r()
    assert "K5_THE_PRODUCT_BEATS_ITS_BEST_SINGLE_FACTOR" in r["gates_not_met"]
    assert r["best_single_factor"] == "V"
    gap = r["auc"]["delta"] - r["auc"]["V"]
    assert 0 < gap < 0.03, "the product improves on V by %.4f, short of the locked bar" % gap
    d = r["post_run_disclosures"]["D6_K5_FAILED_SO_THE_MULTIPLICATIVE_CLAIM_IS_NOT_EARNED"]
    assert "IT DID NOT EARN ITS KEEP" in d["what_this_means"]
    assert "not being redefined" in d["what_is_NOT_being_done"]


def test_the_formula_was_not_rewritten_after_seeing_the_result():
    """The immunisation check: the spec and the runner still say V * I * C."""
    r = _r()
    assert r["formula"] == "DELTA = V * I * C"
    assert _spec()["the_model"]["statement"].endswith("DELTA = V * I * C")


def test_the_pooled_auc_is_disclosed_as_partly_substrate_separation():
    r = _r()
    d = r["post_run_disclosures"]["D5_THE_POOLED_AUC_IS_PARTLY_SUBSTRATE_SEPARATION"]
    assert d["within_github"] < d["pooled"] and d["within_pypi"] < d["pooled"]
    assert "HONEST FIGURES ARE THE WITHIN-SUBSTRATE" in d["note"]
    assert r["too_perfect_flag"] == [], "0.9442 sits just under the 0.95 trigger"


def test_the_pypi_pass_is_disclosed_as_resting_on_four_events():
    r = _r()
    assert "K6_IT_HOLDS_ON_BOTH_SUBSTRATES_SEPARATELY" not in r["gates_not_met"]
    d = r["post_run_disclosures"]["D7_K6_PASSED_ON_THE_PYPI_SIDE_ON_FOUR_EVENTS"]
    assert d["pypi_detections"] == 4 and d["pypi_subdatasets"] == 200
    assert "THAT IS NOT A RESULT" in d["note"]


def test_degrading_the_recording_collapses_detection_and_scores_nothing():
    r = _r()
    k8 = [g for g in r["gates"] if g["id"] == "K8_degraded_recording_arm"][0]
    assert k8["weight"] == "excluded" and k8["met"] is None
    assert "not simulation of a mechanism" in k8["detail"]
    d = r["post_run_disclosures"]["D8_the_degraded_arm_directionally_agrees_but_is_underpowered"]
    assert d["detection_rate_natural"] > d["detection_rate_quantised_10"] \
        > d["detection_rate_quantised_3"]
    assert "meaningless" in d["note"]


def test_delta_never_reads_the_association_it_predicts():
    """V, I and C are functions of the value distribution and group sizes only."""
    src = open(os.path.join(HERE, "dcm.py")).read()
    body = src.split("# ---------------------------------------------------------------- the model")[1]
    body = body.split("# ------------------------------------------------------------- the harness")[0]
    for banned in ("detected", "median", "observed_diff", "permut"):
        assert banned not in body, "the model functions must not touch the relationship"


def test_the_misuse_of_a_low_delta_is_forbidden_in_writing():
    r, s = _r(), _spec()
    d = r["post_run_disclosures"]["D1_what_a_low_DELTA_does_NOT_mean"]
    assert "never says the claim is false" in d["statement"]
    assert "never that the claim is false" in \
        s["what_a_pass_would_and_would_not_license"]["would_not"]


def test_the_failing_region_gate_passed_so_the_misses_are_real():
    r = _r()
    assert "K2_the_failing_region_is_populated" not in r["gates_not_met"]
    assert 0.10 <= r["detection_rate"] <= 0.90


def test_nothing_was_simulated():
    r = _r()
    assert r["simulated_mechanisms"] == 0
    assert "not a simulator" in \
        _spec()["experimental_design_declared_before_any_draw"]["resampling_is_not_simulation"]


def test_the_score_is_five_of_six():
    r = _r()
    assert r["score"] == "5/6"
    assert r["gates_not_met"] == ["K5_THE_PRODUCT_BEATS_ITS_BEST_SINGLE_FACTOR"]
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 6
