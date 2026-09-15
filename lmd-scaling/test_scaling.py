"""The coupling sweep, checked against predictions locked before it ran.

Three of the nine predictions MISSED. They are asserted here as misses, by
name, because softening one costs more than the miss did.
"""

import hashlib
import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import run_scaling as R  # noqa: E402

PREREG_SHA = "c4714e7827ddb942749c90d323a00d729fd3bb4a6d9596ab50a1f435745029be"


@pytest.fixture(scope="module")
def out():
    return {
        "a1": R.arm1(), "a2": R.arm2(), "a3": R.arm3(),
        "a4": R.arm4(), "a5": R.arm5(), "a6": R.arm6(),
    }


# ------------------------------------------------------------ the lock ----
def test_the_preregistration_is_the_one_that_was_hashed():
    with open(os.path.join(HERE, "prereg_scaling.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == PREREG_SHA


def test_the_run_declares_the_same_hash():
    src = open(os.path.join(HERE, "run_scaling.py")).read()
    assert PREREG_SHA in src


# ------------------------------------------------- arm 1: what was hit ----
def test_s1_the_ring_reproduces_the_notebook(out):
    assert out["a1"]["ring"]["abs_slope_err"] < 1e-9


def test_s1_the_ring_matches_the_closed_form_exactly(out):
    # d(0,50) = sqrt(50*50/100 / J) = 5/sqrt(J)
    d = out["a4"]["float64"]
    for J, got in zip(R.COUPLINGS, d):
        assert abs(got - 5.0 / math.sqrt(J)) / got < 1e-12


# ------------------------------------------------- arm 1: what missed ----
def test_the_three_predictions_that_missed(out):
    """S2, S3 and S4 all missed, and all for the same reason: one graph.

    The prediction was that -0.5 would hold for every graph. It did not hold
    for the complete graph under numpy's pseudo-inverse. The identity is not
    wrong -- test_the_identity_holds_once_the_rank_is_not_guessed shows it
    holding to 1e-15 on the same graph -- but the prediction as written said
    the SWEEP would return it, and the sweep did not.
    """
    a1 = out["a1"]
    worst_name = max(a1, key=lambda k: a1[k]["abs_slope_err"])
    assert worst_name == "complete"

    # S2 missed: not every graph came back at -0.5
    assert max(r["abs_slope_err"] for r in a1.values()) > 1e-9
    # S3 missed: R^2 was not 1 to floating point everywhere
    assert max(r["one_minus_r2"] for r in a1.values()) > 1e-12
    # S4 missed: one coupling did NOT determine all fifteen
    assert max(r["max_rel_dev_from_one_point"] for r in a1.values()) > 1e-12

    # the other four did land where predicted
    for name in ("ring", "star", "path", "erdos_renyi_p0.1_seed0"):
        assert a1[name]["abs_slope_err"] < 1e-9, name
        assert a1[name]["one_minus_r2"] < 1e-12, name


def test_the_miss_is_a_leaked_null_mode_not_a_broken_law(out):
    """The complete graph's zero eigenvalue drifts across numpy's rcond line."""
    drift = out["a6"]["cutoff_drift"]
    leaking = [d for d in drift if d["leaks"]]
    assert 0 < len(leaking) < len(drift), (
        "if it leaked at every coupling or none, the drift story is wrong")
    for d in leaking:
        assert d["null_eigenvalue"] > d["rcond_cutoff"]


def test_the_identity_holds_once_the_rank_is_not_guessed(out):
    """MEASURED AFTER THE FACT. Not a prediction, and not scored as one."""
    for name, r in out["a6"]["rank_aware"].items():
        assert r["abs_slope_err"] < 1e-9, name


def test_the_notebooks_verdict_flips_on_choices_that_are_not_physics(out):
    """Same graph, same float64, same gate -- opposite verdict.

    Exactly one of the four (assembly, inverter) pairs fails, and the analytic
    answer is -0.5 for all four. Neither assembly is wrong.
    """
    flip = out["a6"]["library_flip_on_K100"]
    assert len(flip) == 4
    failing = [k for k, r in flip.items() if r["notebook_verdict"] == "FAIL"]
    assert failing == ["accumulate+numpy"], failing
    for k, r in flip.items():
        if k != "accumulate+numpy":
            assert r["abs_slope_err"] < 1e-12, k


def test_assembly_order_alone_flips_it_holding_the_library_fixed(out):
    """numpy in both rows; only the way the degree was summed differs."""
    flip = out["a6"]["library_flip_on_K100"]
    a = flip["accumulate+numpy"]
    b = flip["sum_weight_matrix+numpy"]
    assert a["inverter"] == b["inverter"] == "numpy"
    assert a["notebook_verdict"] == "FAIL"
    assert b["notebook_verdict"] == "PASS"


def test_this_run_does_not_claim_the_identity_as_its_own_finding():
    """smi/ pre-registered it first. Saying so is part of the result."""
    prereg = open(os.path.join(os.path.dirname(HERE), "smi", "PREREG.md"),
                  encoding="utf-8").read()
    assert "IDENTITY, NOT A RESULT" in prereg
    results = open(os.path.join(HERE, "RESULTS.md"), encoding="utf-8").read()
    assert "already known here" in results
    assert "re-derivations, not findings" in results


# ------------------------------------------ arm 2: the version that bites ----
def test_s5_breaking_the_global_scalar_destroys_the_exponent(out):
    assert out["a2"]["abs_slope_err"] > 0.3


def test_s5b_the_heterogeneous_sweep_is_shallow(out):
    assert out["a2"]["abs_slope"] < 0.15


def test_s5c_the_heterogeneous_sweep_is_not_a_straight_line(out):
    assert out["a2"]["r2"] < 0.99


def test_sweeping_one_edge_barely_moves_the_far_pair(out):
    """99 unswept edges carry a route that J cannot touch."""
    a2 = out["a2"]
    assert a2["d_at_first_J"] > a2["d_at_last_J"] > 4.0
    # a thousandfold change in one weight moves the distance by under 5%
    assert abs(a2["d_at_first_J"] - a2["d_at_last_J"]) / a2["d_at_last_J"] < 0.05


# --------------------------------- arm 3: a number for an absent route ----
def test_s6_bare_pinv_reports_a_finite_distance_across_components(out):
    assert out["a3"]["pieces"] == 2
    assert out["a3"]["all_finite"]


def test_s7_and_it_scales_at_minus_a_half_just_like_a_real_route(out):
    """Slope alone cannot tell a measured distance from an unreachable one."""
    assert out["a3"]["abs_slope_err"] < 1e-9


def test_this_repos_engine_refuses_where_the_bare_sweep_answers(out):
    """mesh_metric walks the adjacency; it does not ask pinv whether a path exists."""
    rd = out["a6"]["repo_engine"]["disconnected_pair"]
    assert rd["engine_is_inf"]
    assert math.isfinite(rd["bare_pinv"])
    assert rd["pieces_seen_by_engine"] == 2


# ------------------------------------------------------- arm 4: dtype ----
def test_s8_float64_matches_the_closed_form(out):
    assert out["a4"]["max_rel_dev_float64"] < 1e-12


def test_s9_float32_does_not(out):
    if not isinstance(out["a4"].get("float32"), list):
        pytest.skip("jax not installed")
    assert out["a4"]["max_rel_dev_float32"] > 1e-8


def test_the_published_figure_is_not_a_float64_figure(out):
    """15.811394 is not 5*sqrt(10). The gap is float32-sized."""
    exact = out["a4"]["exact_at_first_J"]
    assert abs(exact - 5.0 * math.sqrt(10.0)) < 1e-12
    assert out["a4"]["published_rel_dev"] > 1e-8
    assert out["a4"]["published_rel_dev"] < 1e-5


def test_the_notebooks_own_tolerance_absorbs_its_dtype_error(out):
    """atol=1e-4 is wide enough that the float32 error never surfaces."""
    if not isinstance(out["a4"].get("float32"), list):
        pytest.skip("jax not installed")
    assert out["a4"]["float32_abs_slope_err"] < 1e-4
    assert out["a4"]["float32_abs_slope_err"] > 1e-9


# ------------------------------- arm 5: the half of the identity that holds ----
def test_scaling_every_weight_moves_resistance_and_not_bearing(out):
    """The engine's own rule, measured: w rises by c, R falls by c, w*R fixed."""
    a5 = out["a5"]
    base = a5["1.0"]
    for factor, r in a5.items():
        f = float(factor)
        assert abs(r["watched_resistance"] - base["watched_resistance"] / f) < 1e-12
        assert abs(r["watched_bearing"] - base["watched_bearing"]) < 1e-12
        assert r["conserved"]
        assert abs(r["total"] - r["expected_total"]) < 1e-9


def test_the_two_halves_are_the_same_identity(out):
    """d falls as c^-0.5 and R falls as c^-1; bearing w*R is why nothing moves.

    The sweep measures the moving half of a cancellation this repository
    already relies on. That is the whole finding.
    """
    a5 = out["a5"]
    r10, r1 = a5["10.0"], a5["1.0"]
    assert abs(r10["watched_resistance"] * 10.0 - r1["watched_resistance"]) < 1e-12
    assert abs(r10["watched_weight"] / 10.0 - r1["watched_weight"]) < 1e-12
    assert abs(r10["watched_bearing"] - r1["watched_bearing"]) < 1e-12


# --------------------------------------------------------- no overclaim ----
def test_nothing_here_claims_to_have_settled_whether_space_is_emergent():
    doc = open(os.path.join(HERE, "prereg_scaling.md")).read().lower()
    assert "inconclusive" in doc
    assert "cannot confirm a physical thesis" in doc
    results = open(os.path.join(HERE, "RESULTS.md")).read().lower()
    for banned in ("proves that space", "confirms that space",
                   "disproves", "we have shown space"):
        assert banned not in results, banned
