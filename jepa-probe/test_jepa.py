"""The collapse probe, checked against predictions locked before it ran.

All five predictions hit, including J2, which the pre-registration said was the
one most likely to miss. That is recorded by name rather than quietly enjoyed:
`test_the_prediction_i_expected_to_miss_and_did_not`.
"""

import hashlib
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import run_jepa as R                                              # noqa: E402
from mini_jepa import (knn_edges, make_data, mean_pairwise_distance,  # noqa: E402
                       spread, target_embeddings, train)

PREREG_SHA = "65522d024b5f06db18e871cf527fbec151ae9375b38bc362bdedea0ea6b98dc9"


@pytest.fixture(scope="module")
def seeds():
    return {s: R.one_seed(s) for s in R.SEEDS}


@pytest.fixture(scope="module")
def base(seeds):
    return seeds[0]


# ------------------------------------------------------------- the lock ----
def test_the_preregistration_is_the_one_that_was_hashed():
    with open(os.path.join(HERE, "prereg_jepa.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == PREREG_SHA


def test_the_run_declares_the_same_hash():
    assert PREREG_SHA in open(os.path.join(HERE, "run_jepa.py")).read()


def test_the_preregistration_cites_the_paper_and_the_sentence_under_test():
    src = open(os.path.join(HERE, "prereg_jepa.md"), encoding="utf-8").read()
    assert "arXiv:2301.08243" in src
    # the quote wraps across lines; compare on collapsed whitespace, the same
    # way test_gate.py compares shipped refusal sentences
    flat = " ".join(src.split())
    assert "representation collapse is also a concern with JEPAs" in flat
    assert "we leverage an asymmetric architecture" in flat


# --------------------------------------------- arm 1: the mechanism ----
def test_j1_the_symmetric_arm_collapses_on_every_seed(seeds):
    for s, r in seeds.items():
        assert r["symmetric"]["spread_ratio"] < 0.01, s


def test_the_prediction_i_expected_to_miss_and_did_not(seeds):
    """J2. The pre-registration said a linear toy might not show the mechanism.

    It shows it, on all five seeds. Collapse remains a global optimum of the
    asymmetric arm -- if the context encoder goes to zero the moving average
    follows it -- and the arrangement still does not reach it.
    """
    for s, r in seeds.items():
        assert r["asymmetric"]["spread_ratio"] > 0.5, s
    prereg = open(os.path.join(HERE, "prereg_jepa.md"), encoding="utf-8").read()
    assert "J2 is the one I expect to be wrong about" in prereg


def test_j3_the_collapsed_arm_reaches_a_flat_energy_landscape(seeds):
    """Near-zero loss carrying no information -- the failure the paper names."""
    for s, r in seeds.items():
        assert r["symmetric"]["final_loss"] < 0.01, s


def test_the_two_arms_differ_in_exactly_one_thing():
    """Otherwise the comparison would not isolate the asymmetry.

    Behavioural rather than a grep: the same data, the same initialisation, the
    same steps and rate, so the first step is identical in both arms and only
    the target-branch arrangement can account for the divergence after it.
    """
    X, _ = make_data(seed=0)
    a = train(X, symmetric=True, seed=0, steps=50)
    b = train(X, symmetric=False, seed=0, steps=50)
    assert a["history"][0]["loss"] == pytest.approx(b["history"][0]["loss"])
    assert a["final_loss"] != b["final_loss"]


def test_splitting_the_switch_did_not_change_either_arm():
    """`symmetric` was split into `shared_target` and `leak`. Bit-identical.

    A refactor that quietly moved a number would invalidate every result above.
    """
    X, _ = make_data(seed=1)
    for sym, shared, leak in ((True, True, 1.0), (False, False, 0.0)):
        old = train(X, symmetric=sym, seed=1, steps=120)
        new = train(X, symmetric=sym, seed=1, steps=120,
                    shared_target=shared, leak=leak)
        assert np.array_equal(old["Wt"], new["Wt"]), sym
        assert old["final_loss"] == new["final_loss"], sym


def test_the_run_is_deterministic():
    X, _ = make_data(seed=3)
    a = train(X, symmetric=False, seed=3, steps=200)
    b = train(X, symmetric=False, seed=3, steps=200)
    assert a["final_loss"] == b["final_loss"]
    assert np.array_equal(a["Wt"], b["Wt"])


def test_the_data_actually_has_structure_to_represent():
    """A collapse result would be uninteresting on structureless data."""
    X, which = make_data(seed=0)
    flat = X.reshape(len(X), -1)
    within = np.mean([flat[which == c].var(axis=0).mean()
                      for c in np.unique(which)])
    between = flat.mean(axis=1).var()
    assert within > 0
    assert between > within / 10


# ------------------------------------------- arm 2: what the readouts see ----
def test_j4_foster_is_conserved_in_both_arms(base):
    sym = R.structural(base["symmetric"]["embeddings"])
    asym = R.structural(base["asymmetric"]["embeddings"])
    assert sym["conserved"] and asym["conserved"]
    assert sym["total_bearing"] == pytest.approx(sym["expected_total"])
    assert asym["total_bearing"] == pytest.approx(asym["expected_total"])


def test_j5_the_collapsed_embeddings_are_orders_of_magnitude_smaller(base):
    r = (base["symmetric"]["mean_pairwise_distance"] /
         base["asymmetric"]["mean_pairwise_distance"])
    assert r < 0.01


def test_the_structural_readouts_cannot_tell_collapse_from_health(base):
    """The limitation this run exists to record.

    A millionfold difference in embedding scale, and both readouts available
    here report the same thing.
    """
    sym = R.structural(base["symmetric"]["embeddings"])
    asym = R.structural(base["asymmetric"]["embeddings"])
    assert sym["total_bearing"] == pytest.approx(asym["total_bearing"])
    assert sym["cut_parts"] == asym["cut_parts"] == 0
    # and the graphs really are different, so this is blindness, not sameness
    ea = {(i, j) for i, j, _ in knn_edges(base["symmetric"]["embeddings"])}
    eb = {(i, j) for i, j, _ in knn_edges(base["asymmetric"]["embeddings"])}
    assert ea != eb


def test_the_noise_control_scores_the_same_way(base):
    """MEASURED AFTER THE FACT. No prediction was registered.

    Foster's total is parts - pieces, so untrained noise is conserved too. The
    quantity is a property of the node and component count, not of the
    representation.
    """
    rng = np.random.default_rng(12345)
    noise = R.structural(rng.normal(size=base["asymmetric"]["embeddings"].shape))
    assert noise["conserved"]
    assert noise["total_bearing"] == pytest.approx(
        noise["parts"] - noise["pieces"])
    assert noise["cut_parts"] == 0


def test_this_is_the_same_scale_invariance_measured_in_lmd_scaling(base):
    """Multiplying every embedding by a constant moves no structural readout."""
    E = base["asymmetric"]["embeddings"]
    a = R.structural(E)
    b = R.structural(E * 1e-6)
    assert a["total_bearing"] == pytest.approx(b["total_bearing"])
    assert a["cut_parts"] == b["cut_parts"]
    assert a["pieces"] == b["pieces"]


# -------------------------------------------------- arm 3: not run ----
def test_c1_the_claude_arm_is_unrun_and_reports_no_number():
    out = R.main()
    assert out["arm3"]["status"] == "UNRUN"
    assert out["arm3"]["number_reported"] is None


def test_the_reason_the_claude_arm_is_unrun_is_on_the_record():
    prereg = open(os.path.join(HERE, "prereg_jepa.md"), encoding="utf-8").read()
    assert "DESIGNED, NOT RUN" in prereg
    assert "Self-report is not" in prereg
    assert "contaminated by construction" in prereg


def test_the_claude_protocol_is_specific_enough_for_someone_else_to_run():
    prereg = open(os.path.join(HERE, "prereg_jepa.md"), encoding="utf-8").read()
    for piece in ("party-inversions", "two\nsurface rewordings",
                  "sealed before the model sees"):
        assert piece.replace("\n", " ") in " ".join(prereg.split()), piece


# ------------------------------------------------------- no overclaim ----
def test_nothing_here_claims_to_be_i_jepa():
    doc = open(os.path.join(HERE, "mini_jepa.py"), encoding="utf-8").read()
    assert "NOT I-JEPA" in doc
    assert "No Vision Transformer" in doc
    results = open(os.path.join(HERE, "RESULTS.md"), encoding="utf-8").read().lower()
    for banned in ("we reproduce i-jepa", "reproduces the paper",
                   "confirms i-jepa", "matches the paper's results"):
        assert banned not in results, banned


def test_the_results_say_what_the_probe_cannot_do():
    results = open(os.path.join(HERE, "RESULTS.md"), encoding="utf-8").read()
    assert "What this run cannot do" in results
    assert "is not a result" in results
