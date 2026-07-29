"""
test_submesh.py — locks the sub-mesh pooling result: 3/5, and the proposal's headline
prediction was wrong by a wide margin on both halves.

THE PROPOSAL: replace the pure mesh's missing pool with LOCAL k-neighbour mutual-guarantee
pools, absorbing routine friction without any single entity intermediating the network.
Published prediction: a cluster of 20 drops settlement failures by over 90% while holding
blast radius to about 0.02.

MEASURED, inside the same settlement engine already built and attacked, driven by the same
committed 4,886 real shocks:

  k        failed   vs k=1     blast radius
  1         2430        —          0.0050
  2         1982     -18.4%        0.0100     ← best
  10        2024     -16.7%        0.0500
  20        2024     -16.7%        0.1000     ← the predicted sweet spot
  50        2021     -16.8%        0.2500
  200       2046     -15.8%        1.0000

WHAT HELD
  S2  local pooling DOES reduce friction — every cluster size beat the pure mesh.
  S4  8,734 draws executed, ZERO exceeded a pool balance or drove one negative.
  S1  pooling conserves value exactly (after the metric was corrected — see below).

WHAT FAILED, and these are the findings
  S5  the published prediction is wrong on BOTH halves: measured 16.7% reduction against
      a predicted >90%, at blast radius 0.1000 against a predicted ~0.02.
  S3  NO cluster size achieves both <50% of baseline failures and blast radius <0.10.
      The two objectives are in direct tension and no operating zone exists at these
      parameters.

THE SHAPE IS THE REAL RESULT. Friction reduction is essentially FLAT at 16-18% from k=2
to k=200 — a 100-fold increase in cluster size buys nothing. That is incompatible with the
exp(-0.15*(k-1)) curve the proposal assumed, which predicts monotonic decay toward zero.
The mechanism is visible in the design: each member's draw is capped at a multiple of its
OWN contribution, so a bigger pool has proportionally more claimants and per-member
capacity does not improve. Pooling helps once; it does not help more.

DISCLOSED HARNESS FIX. S1 initially failed on a value drift of 1.9e4. That drift was the
exogenous shock withdrawing reserves BY DESIGN, not an accounting leak: verified
independently, gross drift equals total withdrawals and unexplained drift is 0.000000.
The gate now measures conservation across the POOLING operations, which is what it was
written to test. No fix converted a mechanism failure into a pass — S3 and S5 failed
before and after.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "9091d0567ca9b3d7bf6a9fee5d8515dfe774ce86ca717d7412b4db2cbcedc87a"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "submesh.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_submesh.json")))


def test_spec_locked_and_refuses_the_tuned_formula_in_writing():
    spec = json.load(open(os.path.join(HERE, "prereg", "submesh_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    trap = spec["the_simulation_trap_being_avoided_again"]
    assert "sixth appearance" in trap and "exp(-0.15" in trap
    assert "MEASURED outputs" in trap
    # the published prediction must be named in the spec BEFORE it was tested
    assert "over 90%" in spec["gates"]["S5_the_published_k20_prediction_is_tested_as_stated"]


def test_it_runs_on_the_committed_real_shock_source():
    r = _r()
    assert r["spec_sha256_canonical"] == LOCKED
    assert r["n_shocks"] == 4886


def test_pooling_conserves_value_exactly():
    """The property that matters most: pooling must MOVE value, never create it."""
    r = _r()
    assert r["max_value_drift"] < 1e-6
    for row in r["sweep"]:
        assert abs(row["unexplained_drift"]) < 1e-6
        # and the gross change is exactly the exogenous withdrawals
        gross = row["value_before"] - row["value_after"]
        assert abs(gross - row["shock_withdrawn"]) < 1e-5
    assert r["bad_draws"] == 0 and r["total_draws"] > 8000


def test_local_pooling_helps_but_only_a_little():
    r = _r()
    base = r["baseline_failed_k1"]
    assert base == 2430
    assert r["best_failed"] < base, "every cluster size beat the pure mesh"
    # ...but the best available improvement is modest
    assert r["best_failed"] / base > 0.75, \
        "the best cluster size still leaves >75% of the failures"
    assert r["best_k"] == 2


def test_the_published_prediction_failed_on_both_halves():
    """S5 tested a specific published claim. It was wrong, and stays wrong."""
    r = _r()
    assert "S5_the_published_k20_prediction_is_tested_as_stated" in r["gates_not_met"]
    assert r["k20_reduction_pct"] < 20.0, \
        "predicted >90% reduction; measured ~16.7%"
    assert r["k20_blast_radius"] == 0.10, \
        "predicted blast radius ~0.02; measured 0.10 — five times larger"


def test_no_operating_zone_exists():
    r = _r()
    assert "S3_an_operating_zone_exists_that_is_both_liquid_and_quarantined" in \
        r["gates_not_met"]
    assert r["operating_zone_k"] == [], \
        "no cluster size achieves both <50% failures and <0.10 blast radius"


def test_the_friction_curve_is_flat_not_exponential():
    """The shape is the finding: a 100x increase in cluster size buys nothing."""
    r = _r()
    base = r["baseline_failed_k1"]
    reductions = {row["k"]: 100.0 * (base - row["failed"]) / base
                  for row in r["sweep"] if row["k"] > 1}
    vals = list(reductions.values())
    assert max(vals) - min(vals) < 5.0, \
        "reduction varies by <5 points across k=2..200 — flat, not exponential decay"
    assert all(10.0 < v < 25.0 for v in vals)
    # an exponential curve would have driven k=200 to near-total absorption
    assert reductions[200] < reductions[2], \
        "the largest cluster is WORSE than the smallest; bigger pools do not help more"


def test_the_two_failures_stand_and_the_score_is_not_inflated():
    r = _r()
    assert len(r["gates_not_met"]) == 2, "the run is 3/5; it must not be re-scored"
    excluded = {g["gate"] for g in r["gates"] if g["weight"] == "excluded"}
    assert len(excluded) == 3, "S6, S7 and S8 cannot fail and must not inflate the score"
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 5
