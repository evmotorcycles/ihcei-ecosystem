"""
test_prescriptive.py — locks the prescriptive banking test on the recovered N=992.

Result: 3/5 falsifiable gates. P1 and P3 failed, and the mechanism behind the failure
is now identified, which makes this the most informative of the three banking runs.

THE DIAGNOSIS THAT MUST NOT BE LOST
  In this cohort D is INVERSELY related to capacity: spearman(stars, D) = -0.4702.
  Nodes clearing the fidelity floor have median 935 stars and default at 89.9%;
  nodes below it have median 16,807 stars and default at 54.0%. Capacity dominates
  survival here (top star quintile defaults at 2.5% against a 75.6% base rate), so a
  D >= D_min admission rule ANTI-SELECTS: it systematically buys the failing half of
  the population. That is why the sovereign book's tail is worse, not better.

  This directly contradicts the real-PyPI result in real-cohorts/, where the same
  construct came out POSITIVELY correlated with capacity (rho = +0.5695). Two real
  substrates disagree on the SIGN of the capacity-fidelity relationship, which means
  D is not yet measuring a stable construct. That is a measurement-validity problem,
  and it must be fixed by re-deriving D — never by reinterpreting a gate.

P1 additionally failed for a reason that could not have been foreseen at lock time:
three of the five star strata are single-outcome (100% default), so AUC is undefined
there and they were excluded. The weighted-AUC clause PASSED (0.7487 > 0.55) and
stratification did NOT destroy the signal (pooled 0.7462), but only 2 of 5 strata
were usable, so the gate fails as written. The threshold is NOT moved.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "00d5d2770abc44510c6367565c773f4b6923bbac89791dc03dba7068a39e54ea"


def _r():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "prescriptive_test.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.load(open(os.path.join(HERE, "results_prescriptive.json")))


def test_spec_was_not_edited_after_locking():
    spec = json.load(open(os.path.join(HERE, "prereg", "prescriptive_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    # the unfalsifiability hazard must stay named in the pre-registration itself
    assert "unfalsifiable" in spec["the_unfalsifiability_hazard_stated_up_front"]
    assert "CAN COME OUT WRONG" in spec["the_unfalsifiability_hazard_stated_up_front"]
    assert spec["gates"]["P5_full_reserve_invariant"].startswith("STRUCTURAL SPEC CHECK")


def test_it_runs_on_the_verified_recovered_cohort():
    r = _r()
    rec = json.load(open(os.path.join(ROOT, "cohort-audit", "results_992_recovery.json")))
    assert r["csv_sha256"] == rec["csv_sha256"], \
        "the banking test must run on the cohort that passed recovery verification"
    assert r["N_full"] == 992
    # the imputation asymmetry is handled, not ignored
    assert r["N_measured"] == 866 and r["N_measured"] < r["N_full"]


def test_the_two_failures_stand():
    r = _r()
    assert len(r["gates_not_met"]) == 2, "the run is 3/5; it must not be re-scored"
    for g in ("P1_fidelity_survives_capacity_stratification",
              "P3_tail_risk_not_mean_risk"):
        assert g in r["gates_not_met"], "%s was rescued after the fact" % g

    # P1: the weighted clause passed, the coverage clause did not. Keep both visible.
    assert r["P1_weighted_stratified_auc_measured"] > 0.55
    assert r["P1_strata_above_half"] < 3, "P1 failed on stratum coverage, not on AUC"
    assert abs(r["P1_weighted_stratified_auc_measured"] - 0.7487) < 5e-3
    # stratification did NOT destroy the signal — that part of the claim survived
    assert abs(r["P1_weighted_stratified_auc_measured"]
               - r["P1_pooled_auc_measured"]) < 0.05

    # P3: the floored book is dramatically WORSE, not marginally so.
    assert r["P3_sovereign_p95"] > r["P3_conventional_p95"]
    assert r["P3_sovereign_mean"] > 0.85 and r["P3_conventional_mean"] < 0.50, \
        "the sovereign book defaulted at ~87.5% against ~46.4%; do not soften this"


def test_the_anti_selection_mechanism_is_recorded():
    """The floor selects the failing population. This is the finding, not a footnote."""
    r = _r()
    assert r["P6_spearman_stars_D"] < -0.40, \
        "in this cohort fidelity is INVERSELY related to capacity"
    # the floor binds hard — and that is precisely why the book gets worse
    assert r["P2_excluded_fraction_of_top_quintile"] > 0.70


def test_two_real_substrates_disagree_on_the_sign():
    """Construct-validity alarm: D correlates +0.57 with capacity on real PyPI and
    -0.47 here. Both are real, committed cohorts. Until that is resolved, no claim
    about 'fidelity' should be stated as if D were a settled measurement."""
    here = _r()["P6_spearman_stars_D"]
    p = os.path.join(ROOT, "real-cohorts", "results_real.json")
    if os.path.exists(p):
        pypi = json.load(open(p))["rho_U_D"]
        assert pypi > 0.40 and here < -0.40, \
            "the sign disagreement between substrates must stay visible"


def test_p4_passed_but_is_not_oversold():
    """P4 met its gate by 0.5 percentage points with 46 nodes in one arm. A gate that
    passes on noise is not support, and the test says so rather than banking it."""
    r = _r()
    gap = r["P4_inflated_default_rate"] - r["P4_sound_default_rate"]
    assert gap > 0                      # the gate did pass, as recorded
    assert gap < 0.02, "the P4 margin is negligible; it must not be cited as a result"


def test_p5_is_labelled_as_a_spec_check_and_excluded_from_the_score():
    r = _r()
    p5 = [g for g in r["gates"] if g["gate"].startswith("P5")][0]
    assert p5["pass"] is True and p5["falsifiable"] is False
    # a gate that cannot fail must not inflate the headline score
    assert sum(1 for g in r["gates"] if g["falsifiable"]) == 5
