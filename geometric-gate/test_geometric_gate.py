"""The geometric gate, checked against predictions locked before it ran.

Eight hit. G9 MISSED, on both of its clauses, and the miss is the answer to the
question that prompted the study: no threshold is picked out by the data.
"""

import hashlib
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "jepa-probe"))

from gate import (covariance_trace, effective_rank, halts,        # noqa: E402
                  project_to_rank, reading)
from mini_jepa import knn_edges, make_data, train                 # noqa: E402
from mini_jepa import target_embeddings                           # noqa: E402

PREREG_SHA = "ddaa4b4a3ca7f02c0e468bf14b765fa23b926db19f17a45534ffde21e602cca4"
HELD_OUT = 40


@pytest.fixture(scope="module")
def emb():
    X, _ = make_data(seed=0)
    out = {}
    for name, sym in (("healthy", False), ("collapsed", True)):
        r = train(X, symmetric=sym, seed=0)
        out[name] = target_embeddings(r["Wt"], X[:HELD_OUT])
    out["dim_collapsed"] = project_to_rank(out["healthy"], k=2)
    return out


# ------------------------------------------------------------- the lock ----
def test_the_preregistration_is_the_one_that_was_hashed():
    with open(os.path.join(HERE, "prereg_gate.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == PREREG_SHA


def test_the_run_declares_the_same_hash():
    assert PREREG_SHA in open(os.path.join(HERE, "run_gate.py")).read()


# -------------------------------- arm 1: is an absolute floor an instrument? --
@pytest.mark.parametrize("c", [1e-3, 1e-2, 1e-1, 1e1, 1e2, 1e3])
def test_g1_trace_scales_as_c_squared(emb, c):
    t0 = covariance_trace(emb["healthy"])
    assert covariance_trace(emb["healthy"] * c) / (c * c) == pytest.approx(
        t0, rel=1e-9)


@pytest.mark.parametrize("c", [1e-3, 1e-2, 1e-1, 1e1, 1e2, 1e3])
def test_g3_effective_rank_is_scale_invariant(emb, c):
    r0 = effective_rank(emb["healthy"])
    assert abs(effective_rank(emb["healthy"] * c) - r0) < 1e-9


def test_g2_a_fixed_epsilon_is_defeated_by_multiplication(emb):
    """A gate that can be cleared by choosing units is not a gate."""
    eps = covariance_trace(emb["healthy"]) / 100.0
    collapsed = emb["collapsed"]
    assert covariance_trace(collapsed) < eps            # halts
    assert covariance_trace(collapsed * 1e7) > eps      # does not halt
    # and the space is exactly as collapsed after the rescale
    assert effective_rank(collapsed) == pytest.approx(
        effective_rank(collapsed * 1e7), rel=1e-9)


# ------------------------------------- arm 2: neither sensor catches both ----
def test_g4_effective_rank_misses_volumetric_collapse(emb):
    r0 = effective_rank(emb["healthy"])
    assert effective_rank(emb["collapsed"]) / r0 >= 0.5


def test_g5_trace_misses_dimensional_collapse(emb):
    t0 = covariance_trace(emb["healthy"])
    assert covariance_trace(emb["dim_collapsed"]) / t0 >= 0.5


def test_g6_effective_rank_catches_dimensional_collapse(emb):
    r0 = effective_rank(emb["healthy"])
    assert effective_rank(emb["dim_collapsed"]) / r0 < 0.5


def test_g7_the_two_by_two_has_a_miss_on_both_off_diagonals(emb):
    """So a one-sensor gate is blind to one of the two failures, either way."""
    t0, r0 = covariance_trace(emb["healthy"]), effective_rank(emb["healthy"])
    vol, dim = emb["collapsed"], emb["dim_collapsed"]
    assert covariance_trace(vol) / t0 < 0.5      # trace catches volumetric
    assert effective_rank(vol) / r0 >= 0.5       # rank misses it
    assert covariance_trace(dim) / t0 >= 0.5     # trace misses dimensional
    assert effective_rank(dim) / r0 < 0.5        # rank catches it


def test_a_single_point_space_reports_undefined_rank_not_a_tidy_one():
    """Empty is not a number. A collapsed-to-a-point space has no rank."""
    E = np.ones((20, 8)) * 3.0
    assert np.isnan(effective_rank(E))


# --------------------------------------------------- arm 3: the miss ----
def test_the_prediction_that_missed(emb):
    """G9, on BOTH clauses, and the second only after finer sampling.

    Clause (a): the momentum sweep has no abrupt transition -- its largest
    adjacent step is 0.008 orders of magnitude, not the 6 predicted, because
    the sweep never collapses at all. Momentum is the wrong dial.

    Clause (b): the coarse leak sweep DID show an empty band, which would have
    made a cutoff inside it defensible. Sampled finely, the band fills: the
    spread ratio walks through 0.44, 0.35, 0.29, 0.24, 0.11, 0.013. The empty
    band was an artefact of resolution, and a threshold read off it would have
    been an artefact too.
    """
    from run_gate import SEEDS
    from mini_jepa import _init, embed

    def spread_ratio(seed, leak):
        X, _ = make_data(seed=seed)
        We0, _, _ = _init(seed)
        E0 = embed(We0, X[:HELD_OUT][:, [2, 3], :]).mean(axis=1)
        r = train(X, symmetric=False, seed=seed, shared_target=False, leak=leak)
        E = target_embeddings(r["Wt"], X[:HELD_OUT])
        return float(E.var(axis=0).mean()) / float(E0.var(axis=0).mean())

    coarse = {lk: float(np.median([spread_ratio(s, lk) for s in SEEDS]))
              for lk in (0.0, 0.1)}
    assert not (0.01 <= coarse[0.1] <= 0.5)      # coarse: band looks empty

    fine = {lk: float(np.median([spread_ratio(s, lk) for s in SEEDS]))
            for lk in (0.005, 0.02, 0.05)}
    inside = [lk for lk, v in fine.items() if 0.01 <= v <= 0.5]
    assert len(inside) == 3, fine                # fine: the band is occupied


def _momentum_medians(seed_list):
    from run_gate import MOMENTA
    from mini_jepa import _init, embed
    import mini_jepa

    meds = []
    for m in MOMENTA:
        old = mini_jepa.EMA_MOMENTUM
        mini_jepa.EMA_MOMENTUM = m
        try:
            vals = []
            for s in seed_list:
                X, _ = make_data(seed=s)
                We0, _, _ = _init(s)
                E0 = embed(We0, X[:HELD_OUT][:, [2, 3], :]).mean(axis=1)
                r = train(X, symmetric=False, seed=s)
                E = target_embeddings(r["Wt"], X[:HELD_OUT])
                vals.append(float(E.var(axis=0).mean()) /
                            float(E0.var(axis=0).mean()))
        finally:
            mini_jepa.EMA_MOMENTUM = old
        meds.append(float(np.median(vals)))
    return meds


def test_g8_the_momentum_sweep_is_monotone_but_never_collapses():
    """On the five seeds the pre-registration named."""
    from run_gate import SEEDS
    meds = _momentum_medians(SEEDS)
    assert all(meds[i] <= meds[i + 1] * 1.0000001 for i in range(len(meds) - 1))
    assert min(meds) > 0.5, "the momentum sweep never collapses, so it has no knee"


def test_g8s_monotonicity_does_not_survive_a_three_seed_subsample():
    """Recorded rather than tidied away.

    G8 hit on the registered five seeds. On seeds 0-2 alone the medians are not
    monotone. The prediction was about the registered protocol and it held
    there, but the margins are of the order of the seed noise -- the whole
    sweep spans 0.698 to 0.717 -- so the monotonicity is a thin result and
    should not be leaned on.
    """
    meds3 = _momentum_medians([0, 1, 2])
    assert not all(meds3[i] <= meds3[i + 1] * 1.0000001
                   for i in range(len(meds3) - 1))
    assert min(meds3) > 0.5          # still never collapses, which is the point
    assert max(meds3) - min(meds3) < 0.1


# ------------------------------- arm 4: which half is load-bearing ----
def test_the_stop_gradient_is_the_mechanism_not_the_moving_average():
    """POST HOC. No prediction was registered, and this revises jepa-probe.

    That commit attributed collapse-prevention to the asymmetry as a whole.
    Split into its two halves, the exponential moving average contributes
    nothing here and the stop-gradient does all of the work.
    """
    from mini_jepa import _init, embed
    X, _ = make_data(seed=0)
    We0, _, _ = _init(0)
    E0 = embed(We0, X[:HELD_OUT][:, [2, 3], :]).mean(axis=1)
    base = float(E0.var(axis=0).mean())

    def ratio(shared, leak):
        r = train(X, symmetric=False, seed=0, shared_target=shared, leak=leak)
        E = target_embeddings(r["Wt"], X[:HELD_OUT])
        return float(E.var(axis=0).mean()) / base

    # stop-gradient alone, with NO moving average, is enough
    assert ratio(True, 0.0) > 0.5
    # the moving average alone, with a full gradient, is not
    assert ratio(False, 1.0) < 0.01
    # both halves off collapses; both on holds
    assert ratio(True, 1.0) < 0.01
    assert ratio(False, 0.0) > 0.5


# --------------------------------------------- the gate refuses a default ----
def test_the_gate_has_no_default_cutoffs(emb):
    with pytest.raises(ValueError, match="no default cutoffs"):
        halts(emb["healthy"], None, None)


def test_the_gate_reports_both_sensors_and_fuses_nothing(emb):
    r = reading(emb["healthy"])
    assert set(r) == {"covariance_trace", "effective_rank", "dimensions",
                      "samples"}
    for k in r:
        assert not any(w in k for w in ("score", "combined", "index", "health"))


def test_the_knn_graphs_really_do_differ_under_collapse(emb):
    """The correction carried in: the topology is NOT preserved.

    The message proposing this gate said kNN "draws the exact same topological
    connections" under collapse. It does not.
    """
    a = {(i, j) for i, j, _ in knn_edges(emb["healthy"])}
    b = {(i, j) for i, j, _ in knn_edges(emb["collapsed"])}
    assert a != b
    jaccard = len(a & b) / len(a | b)
    assert 0.3 < jaccard < 0.8, jaccard


# --------------------------------------------------------- no overclaim ----
def test_the_results_refuse_to_name_an_empirical_threshold():
    results = open(os.path.join(HERE, "RESULTS.md"), encoding="utf-8").read()
    assert "declared preference" in results
    assert "What this run cannot do" in results
    low = results.lower()
    for banned in ("the correct threshold is", "we recommend a threshold of",
                   "the optimal cutoff"):
        assert banned not in low, banned
