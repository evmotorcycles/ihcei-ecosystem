"""
test_financial_lism.py — locks both arms, including the blocked one.

ARM T (stratified relative floors, real recovered N=992): 2/5.
  T2 FAILED    56.9% stratified vs 3.2% conventional — the stratified mesh defaults at
               nearly EIGHTEEN TIMES the rate of simply selecting on capacity.
  T3 FAILED    tail is worse too (62.5% vs 5.6% at the 95th percentile).
  T5 FAILED    and this is the root cause: weighted within-tier AUC(low D -> default)
               = 0.3397, i.e. BELOW 0.5. Within a capacity tier, LOW fidelity predicts
               SURVIVAL. The tier-local floor is not sorting on noise — it is sorting in
               the WRONG DIRECTION, so admitting high-D nodes actively selects failure.
  T1 passed    stratification does repair ~23 points of the flat floor's self-inflicted
               damage (56.9% vs 80.1%) — declared a low-value sanity check, because
               beating a design already known to anti-select proves little.

  The honest summary: the remedy mitigates a wound the design inflicted on itself and
  still produces no advantage whatsoever over doing nothing clever.

ARM F (LISM laws on real regulatory filings): BLOCKED, 0/5. Every live FinancialReports
endpoint returns HTTP 403 "User profile not found for the provided token". A blocked
gate counts as NOT MET. No filings cohort was synthesized to fill the arm.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "95d96f917f7351c35da801034ccc3f1cc5cf7f008bc5881100f85d209fecdbf8"


def _run(script, out):
    p = subprocess.run([sys.executable, os.path.join(HERE, script)],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, out)))


def test_spec_was_locked_before_the_gates_ran():
    spec = json.load(open(os.path.join(HERE, "prereg", "finlism_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    # the spec must keep refusing the simulator as evidence, in its own words
    s = spec["the_synthetic_evidence_problem_stated_up_front"]
    assert "is not evidence" in s and "ENFORCED" in s
    # and it must name T2 as make-or-break BEFORE the result was known
    assert "T2 is the make-or-break gate" in spec["the_hardest_gate_named_in_advance"]


def test_arm_T_runs_on_the_verified_cohort():
    r = _run("stratified_test.py", "results_stratified.json")
    rec = json.load(open(os.path.join(ROOT, "cohort-audit", "results_992_recovery.json")))
    assert r["csv_sha256"] == rec["csv_sha256"], \
        "the remedy must be tested on the cohort that passed recovery verification"
    assert r["N_measured"] == 866


def test_the_stratified_remedy_failed_where_it_mattered():
    r = _run("stratified_test.py", "results_stratified.json")
    assert len(r["gates_not_met"]) == 3, "the run is 2/5; it must not be re-scored"
    for g in ("T2_stratified_beats_conventional_baseline",
              "T3_stratified_tail_is_better",
              "T5_within_tier_fidelity_actually_discriminates"):
        assert g in r["gates_not_met"], "%s was rescued after the fact" % g

    # T2: not marginally worse — an order of magnitude worse.
    assert r["default_rate_stratified"] > r["default_rate_conventional"]
    assert r["default_rate_conventional"] < 0.05
    assert r["default_rate_stratified"] > 0.50
    assert (r["default_rate_stratified"] / r["default_rate_conventional"]) > 10, \
        "the stratified book defaulted at ~18x the conventional rate; do not soften this"

    # T3: the tail is worse too
    assert r["p95_stratified"] > r["p95_conventional"]


def test_the_mechanism_is_inverted_not_merely_absent():
    """T5 is the finding. D does not fail to inform within a tier — it informs
    BACKWARDS. Any future 'fix' that keeps selecting on high D inherits this."""
    r = _run("stratified_test.py", "results_stratified.json")
    assert r["T5_usable_tiers"] == 2, "two of four tiers are 100% default and unusable"
    assert r["T5_weighted_within_tier_auc"] < 0.50, \
        "within-tier, low fidelity predicts SURVIVAL — the floor sorts the wrong way"
    assert abs(r["T5_weighted_within_tier_auc"] - 0.3397) < 5e-3
    for t in r["T5_per_tier"]:
        if t["auc_lowD_predicts_default"] is not None:
            assert t["auc_lowD_predicts_default"] < 0.50, \
                "every usable tier points the same wrong way; keep that visible"


def test_the_one_pass_is_labelled_as_the_low_bar_it_is():
    r = _run("stratified_test.py", "results_stratified.json")
    g = {x["gate"]: x for x in r["gates"]}
    assert g["T1_stratified_beats_flat_floor"]["pass"] is True
    assert g["T1_stratified_beats_flat_floor"]["weight"] == "low"
    assert g["T4_capacity_access_is_preserved"]["weight"] == "supporting"
    # stratification really did repair the flat floor's damage — state it, don't inflate it
    assert r["default_rate_stratified"] < r["default_rate_flat_floor"]


def test_arm_F_is_blocked_and_nothing_was_fabricated():
    r = _run("arm_f_filings.py", "results_arm_f.json")
    assert r["status"] == "BLOCKED"
    assert r["http_status_live_endpoints"] == 403
    assert r["data_synthesized"] is False
    assert len(r["gates_not_met"]) == 5, "a blocked gate counts as NOT MET, not absent"
    assert not os.path.exists(os.path.join(ROOT, "data", "financial",
                                           "filings_cohort.csv")), \
        "if a filings cohort now exists, arm F must be re-run rather than left BLOCKED"

    probe = json.load(open(os.path.join(HERE, "connector_probe.json")))
    live = [c for c in probe["calls_attempted"] if c["http_status"] == 403]
    assert len(live) >= 3, "the blockage must be evidenced across several endpoints"
    ok = [c for c in probe["calls_attempted"] if c["http_status"] == 200]
    assert all("STATIC" in c.get("note", "").upper() for c in ok), \
        "only a bundled static resource resolved; it must not be mistaken for live data"
