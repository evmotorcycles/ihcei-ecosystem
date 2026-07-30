"""
test_v2.py — locks Two-Register v2: 3/5. The proposed improvement did not improve it, and
the recommended configuration is Al-Qudah's model unmixed.

WHAT v2 PROPOSED. Adopt Al-Qudah's asset-backed / diminishing co-ownership contracts as the
RECOVERY-register primitive, confine participation to CONTAINMENT, re-centre the headline on
continuous distribution. The reasoning was sound: in the three-proposal run his arm scored
88.5 against our 96.7.

WHY THE SWEEP IS HONEST. At containment share 0.0 this architecture IS Al-Qudah's arm; at
1.0 it IS Irfan's arm. The sweep interpolates between two NAMED positions, so any advantage
has to appear as an interior point beating both of its own endpoints.

  containment    shortfall   secondary
        0.00         36.1         121     <- Al-Qudah arm
        0.10         46.2         119
        0.25         71.0         119
        0.40         77.0         119
        0.60        107.8         109
        0.80        138.7         108
        1.00        167.6         101     <- Irfan arm

V2 FAILED — THE MIX ADDS NOTHING. Across the whole range cascades fall only 121 -> 101
(16.5%) while shortfall rises 36.1 -> 167.6 (4.6x). No interior share delivers a 15%
cascade reduction inside a 25% shortfall budget. The recommendation is to pick an endpoint.

V4 FAILED — AND THIS CORRECTS THE PROPOSAL DIRECTLY. Importing Al-Qudah's contracts into
our mix made it WORSE: 71.0 against 51.8 for fixed claims at the same share, and v2 loses
on 0 OF 5 SEEDS. His arm's 88.5 came from being PURE (share 0.0), not from the contract
primitive being superior inside a mix. The correct reading is not "adopt his contracts into
our architecture" but "his architecture at share 0.0 is the best configuration tested."

V3 PASSED, AND STRONGLY: 50.9x. Continuous distribution still dominates on the NEW
composition -- measured on amortising co-ownership rather than assumed to carry over from
the fixed-claim run. Flow beats stock again.

V5 -- THE CHECK THIS PROGRAMME NEVER RAN. Passed on the criterion that carries information
and VACUOUSLY on the one that does not: with V2 failing, no seed has a qualifying interior
share, so "None appears 5/5" tests nothing and is disclosed as such. The number that
matters is the CV: **single-seed results in this repository carry roughly +/-22%
variation** (mean 60.2, sd 13.2, range 34.7 to 71.0 on the same quantity). Every
single-seed finding elsewhere in this repository should be read with that band attached.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "f14596f111c9378ae33c3ffa1e490a535086205692269bebeb8652215b8bb5cd"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "v2.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_v2.json")))


def test_spec_locked_and_states_the_band_before_the_run():
    spec = json.load(open(os.path.join(HERE, "prereg", "v2_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    assert "15%" in spec["gates"]["V2_an_interior_share_beats_BOTH_of_its_own_endpoints_"
                                  "inside_a_declared_band"]
    assert "ELEVENTH appearance" in spec["the_simulation_trap_being_avoided_again"]
    assert "does not replace" in spec["what_this_does_NOT_do"]
    assert "reported separately and never merged" in spec["no_combined_objective_again"]
    assert len(spec["fixed_parameters"]["robustness_seeds"]) == 5


def test_the_sweep_really_interpolates_between_two_named_positions():
    """Share 0.0 is Al-Qudah's arm; share 1.0 is Irfan's. No strawmen."""
    r = _r()
    assert r["endpoint_alqudah"]["share"] == 0.0
    assert r["endpoint_irfan"]["share"] == 1.0
    # and they behave as the named positions did: Irfan fewer cascades, worse shortfall
    assert r["endpoint_irfan"]["secondary"] < r["endpoint_alqudah"]["secondary"]
    assert r["endpoint_irfan"]["shortfall"] > r["endpoint_alqudah"]["shortfall"]


def test_full_reserve_holds_at_every_share():
    r = _r()
    assert max(x["unbacked"] for x in r["sweep"]) < 1e-6


def test_the_mix_adds_nothing_over_picking_an_endpoint():
    """V2, the primary gate."""
    r = _r()
    assert "V2_an_interior_share_beats_BOTH_of_its_own_endpoints_inside_a_declared_band" \
        in r["gates_not_met"]
    assert r["best_interior"] is None
    z = r["endpoint_alqudah"]
    one = r["endpoint_irfan"]
    # cascades barely move while shortfall multiplies — that is why no band point exists
    assert (z["secondary"] - one["secondary"]) / z["secondary"] < 0.20
    assert one["shortfall"] / z["shortfall"] > 4.0


def test_importing_alqudahs_contracts_made_our_model_worse_on_every_seed():
    """V4 corrects the proposal. His 88.5 came from being PURE, not from the primitive."""
    r = _r()
    assert "V4_v2_actually_improves_on_v1" in r["gates_not_met"]
    assert r["distribution_on"]["shortfall"] > r["v1_fixed_claims_comparator"]["shortfall"]
    assert r["v4_v2_better_on_n_seeds"] == 0, \
        "co-ownership-in-the-mix loses to fixed claims on all five seeds"
    assert len(r["v4_multi_seed"]) == 5


def test_flow_still_dominates_stock_on_the_new_composition():
    """V3, measured on amortising co-ownership rather than assumed to carry over."""
    r = _r()
    assert r["distribution_ratio"] > 5.0
    assert r["distribution_off"]["shortfall"] > 10 * r["distribution_on"]["shortfall"]


def test_seed_robustness_reports_the_variation_band_and_its_own_vacuity():
    """V5: the CV is the part that carries information, and the rest is disclosed."""
    r = _r()
    sr = r["seed_robustness"]
    assert len(sr["per_seed"]) == 5
    assert 0.15 < sr["cv"] < 0.25, "single-seed results carry roughly +/-22% variation"
    assert r["v5_modal_criterion_vacuous"] is True, \
        "with no interior optimum, the modal-share criterion tests nothing and says so"


def test_the_score_is_three_of_five_and_the_proposal_was_corrected_not_confirmed():
    r = _r()
    assert r["score"] == "3/5"
    assert sorted(r["gates_not_met"]) == sorted([
        "V2_an_interior_share_beats_BOTH_of_its_own_endpoints_inside_a_declared_band",
        "V4_v2_actually_improves_on_v1"])
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 5
