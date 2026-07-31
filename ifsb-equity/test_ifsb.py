"""
test_ifsb.py -- locks the IFSB loss-absorbing-funding result: 1/6.

WHAT THIS IS. IFSB Detailed Financial Statements, 2017Q4 to 2023Q4, national aggregates
reported by supervisors. The primary panel is 117 country-quarters across Afghanistan,
Bangladesh, Kuwait, Pakistan, Palestine and Turkey. The risk-sharing variable is the
Profit-Sharing Investment Account share of the balance sheet -- the funding side, where
loss absorption actually lives. The outcome is realised provisioning for non-performing
financing over total financing. This is the only supplied dataset in which a
loss-absorbing line and a realised loss line both appear, which is why the claim that the
2016 interbank files 'completely supersede' it is wrong and is corrected in the spec.

THE PRIMARY GATE MISSED, AND MISSED CLEANLY.

  F3 FAILED, 3 of 6 countries in the risk-sharing direction against a locked bar of 4.
     Afghanistan, Bangladesh and Pakistan went one way; Kuwait, Palestine and Turkey the
     other. An even split.

  F4 FAILED, and this is the more informative miss. Shuffling the same variable within
     country, 200 seeded draws, puts 3.06 of 6 countries in the risk-sharing direction on
     average. The REAL variable put 3 there. It performed AT THE NOISE MEAN, not near a
     bar it narrowly missed. The BS04 interbank-share placebo managed 1.

  F5 scored not met by the locked rule: F3 did not hold, so there was no result whose
     fragility could be tested. Recorded as not met rather than skipped.

  F6 FAILED, 0 of 4.

F1 FAILED BECAUSE MY SPEC WAS WRONG, NOT BECAUSE THE DATA IS. The locked F1 asserted every
provisioning ratio would be non-negative. Eight country-quarters carry a negative one --
seven Afghan quarters and one Pakistani. A negative provision is a RELEASE, a write-back
of amounts previously reserved, and is ordinary accounting. The gate is NOT re-scored,
because a specification that turns out to be wrong is exactly the case the
no-moving-thresholds rule exists for. The half of F1 that tests the data -- the declared
per-country composition of both panels -- matched exactly.

THE FINDING THAT OUTWEIGHS THE SCORE. Kuwait reports EXACTLY ZERO equity-based financing
income in all 12 of its quarters, and Palestine in all 21 of its. Not small: zero, every
quarter, six years, on the supervisors' own returns. Their entire reported financing
income is sales-based and lease-based. In two of the four systems for which the IFSB
publishes the breakdown, the asset-side profit-and-loss-sharing line does not exist. That
is a measurement of what is booked, not a model output, and it is the substantive result
of this run.

WHAT THIS DOES NOT SHOW. It does not show that loss-absorbing funding fails to reduce
fragility. Six national aggregates cannot see a bank-level mechanism, and provisioning
policy is set by six different supervisors. F7 records that limit as UNTESTABLE-HERE.

NO INFERENTIAL STATISTICS ANYWHERE. n = 117 country-quarters from 6 systems, serially
dependent within country, not a sample of any population. A test below asserts the
results file contains no p-value, confidence interval or significance claim.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "0d52c8446d9f31edd2b117e2730029fb0c194c47f73f6df93fa7fadd5cc14e99"
BANNED = ("p-value", "p value", "significant", "confidence interval", "95%", "std err")


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "ifsb.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_ifsb.json")))


def test_spec_locked_and_corrects_the_supersession_claim():
    spec = json.load(open(os.path.join(HERE, "prereg", "ifsb_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    assert "They do not" in \
        spec["why_this_dataset_is_not_superseded_by_the_interbank_network"]["claim_being_corrected"]
    # the earlier 9-country misstatement is corrected inside the spec, not quietly
    assert "across 9 countries. It is 65 country-quarters across 4" in \
        spec["panels"]["SECONDARY_panel_S"]["correction_recorded"]
    # the opposite direction was declared publishable BEFORE the run
    assert "OPPOSITE" in spec["gates"][2]["opposite_direction_declared_now"]


def test_the_primary_gate_missed_three_of_six():
    r = _r()
    assert "F3_LOSS_ABSORBING_FUNDING_PREDICTS_LOWER_PROVISIONING" in r["gates_not_met"]
    assert r["countries_in_risk_sharing_direction"]["panel_P"] == 3
    signs = {c: v["sign"] for c, v in r["directions_panel_P"].items()}
    assert signs == {"Afghanistan": -1, "Bangladesh": -1, "Pakistan": -1,
                     "Kuwait": 1, "Palestine": 1, "Turkey": 1}


def test_the_real_variable_performed_at_the_permutation_mean():
    """F4, the cleanest null in the run."""
    r = _r()
    assert "F4_the_result_is_not_reproduced_by_a_placebo" in r["gates_not_met"]
    p = r["placebo"]
    assert p["BS04_interbank_share"] == 1
    assert abs(p["permutation_mean"] - 3.065) < 1e-3
    assert r["countries_in_risk_sharing_direction"]["panel_P"] <= p["permutation_mean"], \
        "the measured variable did not beat shuffling itself"


def test_two_systems_book_no_equity_based_income_at_all():
    """The substantive finding, worth more than the score."""
    r = _r()
    d = r["post_run_disclosures"]["D2_TWO_SYSTEMS_REPORT_ZERO_EQUITY_BASED_INCOME_THROUGHOUT"]
    assert d["countries"] == ["Kuwait", "Palestine"]
    assert d["quarters_each"] == {"Kuwait": 12, "Palestine": 21}
    assert r["directions_panel_S"]["Kuwait"]["sign"] is None
    assert r["directions_panel_S"]["Palestine"]["sign"] is None
    assert "does not exist" in d["why_this_matters_more_than_the_score"]


def test_F1_failed_on_my_own_over_assertion_and_was_not_re_scored():
    r = _r()
    assert "F1_data_integrity" in r["gates_not_met"]
    d = r["post_run_disclosures"]["D1_F1_failed_because_MY_SPEC_over_asserted"]
    assert len(d["cases"]) == 8
    assert d["whose_error_this_is"].startswith("Mine.")
    assert "NOT re-scored" in d["whose_error_this_is"]
    # the part of F1 that tests the DATA passed: composition matched exactly
    spec = json.load(open(os.path.join(HERE, "prereg", "ifsb_prereg.json")))
    assert r["panel_P"]["composition"] == \
        spec["panels"]["PRIMARY_panel_P"]["composition_declared_before_analysis"]
    assert r["panel_S"]["composition"] == \
        spec["panels"]["SECONDARY_panel_S"]["composition_declared_before_analysis"]


def test_the_failing_region_gate_passed_so_the_misses_are_real():
    """F2. Without this, F3 and F4 would be UNTESTABLE-HERE rather than results."""
    r = _r()
    assert "F2_the_failing_region_is_populated" not in r["gates_not_met"]
    assert sum(1 for v in r["within_country_rs_iqr"].values() if v >= 0.02) == 4


def test_no_inferential_statistics_are_claimed():
    r = _r()
    scan = json.dumps({k: v for k, v in r.items()
                       if k not in ("gates", "gates_not_met")}).lower()
    for w in BANNED:
        assert w not in scan, "found a statistical claim: %s" % w


def test_institution_level_gap_is_recorded_as_untestable_not_refuted():
    r = _r()
    f7 = [g for g in r["gates"] if g["id"] == "F7_institution_level_discrimination"][0]
    assert f7["weight"] == "excluded" and "UNTESTABLE-HERE" in f7["detail"]
    assert "does NOT show" in \
        r["post_run_disclosures"]["D4_what_this_does_and_does_not_show"]["does_not"]


def test_the_score_is_one_of_six():
    r = _r()
    assert r["score"] == "1/6"
    assert len(r["gates_not_met"]) == 5
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 6
