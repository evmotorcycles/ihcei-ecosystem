"""Pre-registered perception tests, P1-P6.

Locked in prereg_perception.md, sha256
4cee849de5c8fe786c7bb1e22967a429d65cf077339dd318c5cd597d4ea7c4f5

Three defects in the supplied P1-P3 are kept as evidence rather than deleted:
D1 (P2 could not show what it claimed), D2 (P1's rank half could not fail),
D3 (the disconnection guard was inert).
"""

from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from stack.perception.lmd_distance import (  # noqa: E402
    PINNED_SYMMETRIZATION, DisconnectedSpaceError, SymmetrizationError,
    components, perception_distance, rank_order, resistance_and_distance)

PREREG_SHA = "4cee849de5c8fe786c7bb1e22967a429d65cf077339dd318c5cd597d4ea7c4f5"
COHORT_SHA = "020562667229a1c24e06b1a075786c2f86d700e5fbf1a4c0bb99a905b95f7a15"
PREMISE = 0


# ----------------------------------------------------------- the ledger ----
def test_the_preregistration_is_the_one_that_was_hashed():
    with open(os.path.join(HERE, "prereg_perception.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == PREREG_SHA


def test_the_declarations_carry_the_real_cohort_hash():
    root = os.path.dirname(os.path.dirname(HERE))
    dec = open(os.path.join(root, "stack", "governance", "declarations.md"),
               encoding="utf-8").read()
    assert "REPLACE_WITH" not in dec
    assert COHORT_SHA in dec
    with open(os.path.join(root, "adg-tqg", "fixtures",
                           "experiment_cohort.json"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == COHORT_SHA


def test_the_declarations_state_foster_is_an_invariant_not_a_health_score():
    root = os.path.dirname(os.path.dirname(HERE))
    dec = " ".join(open(os.path.join(root, "stack", "governance",
                                     "declarations.md"),
                        encoding="utf-8").read().split())
    assert "harness invariant only" in dec
    assert "does not gate health" in dec
    assert "invariance group" in dec


# ------------------------------------------------------------- fixtures ----
def _ring_attention(n: int, w: float = 1.0) -> np.ndarray:
    A = np.zeros((n, n))
    for i in range(n):
        A[i, (i + 1) % n] = w
    return A


def _diluted_complete(n: int) -> np.ndarray:
    """The supplied construction. Kept so D1 stays measurable."""
    return np.ones((n, n)) / n


def _window(n: int, k: int = 2, w: float = 1.0, floor: float = 1e-4,
            boost_middle: bool = False) -> np.ndarray:
    """Local-window attention, mass NOT renormalised by n.

    `where`: chosen for this run to model attention that is local plus a weak
    background. The floor keeps the graph in one piece; it is a free parameter.
    """
    A = np.full((n, n), floor)
    np.fill_diagonal(A, 0.0)
    for i in range(n):
        for j in range(max(0, i - k), min(n, i + k + 1)):
            if i != j:
                A[i, j] = w
    if boost_middle:
        A[PREMISE, n // 2] = 10.0
    return A


# ----------------------------------------- P1R: the identity, and a control --
def test_p1r_a_uniform_scale_contracts_by_the_square_root():
    """VERIFICATION OF AN IDENTITY, NOT A RESULT.

    pinv(cL) = pinv(L)/c, so d -> d * c^(-1/2) on every graph. smi/PREREG.md
    locked this as "IDENTITY, NOT A RESULT" before this module existed.
    """
    A = _ring_attention(8)
    c = 4.0
    _, d1 = resistance_and_distance(A)
    _, d2 = resistance_and_distance(c * A)
    mask = d1 > 1e-12
    assert np.allclose(d2[mask] / d1[mask], c ** -0.5, rtol=1e-9, atol=1e-12)


def test_the_supplied_rank_comparison_could_not_fail():
    """D2, kept as evidence.

    The ratio API divides the scale out, so the two ratio matrices are
    bit-identical and comparing their ranks is a tautology.
    """
    A = _ring_attention(8)
    r1 = perception_distance(A, PINNED_SYMMETRIZATION, (0, 4))
    r2 = perception_distance(4.0 * A, PINNED_SYMMETRIZATION, (0, 4))
    assert np.abs(r1 - r2).max() == 0.0
    assert np.array_equal(rank_order(r1, 0), rank_order(r2, 0))


def test_p1r_b_the_rank_control_that_does_move():
    """So rank equality above means something when it is asserted elsewhere."""
    A = _ring_attention(8)
    B = A.copy()
    B[0, 4] = 5.0                      # a genuine chord, not a rescale
    r1 = perception_distance(A, PINNED_SYMMETRIZATION, (0, 1))
    r2 = perception_distance(B, PINNED_SYMMETRIZATION, (0, 1))
    assert not np.array_equal(rank_order(r1, 0), rank_order(r2, 0))


# ----------------------------------------------- P2R: lost in the middle ----
def test_the_prediction_that_the_supplied_p2_could_not_show():
    """D1, kept as evidence.

    ones(n,n)/n symmetrized is K_n at weight 2/n, and R = 2/(n*w) = 1 exactly,
    for every n. The supplied assertion uses >=, so it passes while the claim
    in its own docstring never happens.
    """
    vals = []
    for n in (16, 32, 64):
        R, _ = resistance_and_distance(_diluted_complete(n))
        vals.append(float(R[PREMISE, n // 2]))
    assert max(vals) - min(vals) < 1e-9        # P2R-c
    assert all(abs(v - 1.0) < 1e-9 for v in vals)
    assert vals[1] >= vals[0] - 1e-9           # the supplied assertion: passes
    assert not (vals[0] < vals[1] < vals[2])   # the supplied claim: does not


def test_p2r_a_distance_to_the_middle_grows_with_context_length():
    vals = []
    for n in (16, 32, 64, 128):
        R, _ = resistance_and_distance(_window(n))
        vals.append(float(R[PREMISE, n // 2]))
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)), vals


def test_p2r_b_it_grows_at_least_threefold_from_16_to_128():
    """The prediction the pre-registration flagged as uncertain.

    The background floor gives a route that gets CHEAPER as n grows -- more
    parallel background edges -- working against the window path lengthening.
    Which term wins was not settled by writing it down.
    """
    r16 = float(resistance_and_distance(_window(16))[0][PREMISE, 8])
    r128 = float(resistance_and_distance(_window(128))[0][PREMISE, 64])
    assert r128 / r16 >= 3.0, (r16, r128, r128 / r16)
    assert r128 / r16 < 3.5, "it hit at 3.112, which is thin -- see the reversal"


def test_the_growth_reverses_one_sample_past_the_registered_range():
    """POST HOC. No prediction was registered, and it undoes the two above.

    P2R-a and P2R-b were registered over n = 16, 32, 64, 128 and both hit. One
    more doubling and the trend turns over:

        n=128  2.894   x1.07
        n=256  2.171   x0.75
        n=384  1.784   x0.82

    The background floor is a parallel conductance whose total grows with n, so
    it eventually beats the lengthening window path: the far token gets CLOSER,
    not further. Lost-in-the-middle reverses into found-by-the-crowd.

    So the registered predictions hit on the sampled range and the claim they
    were testing does not survive one extra point. That is the same sampling
    trap as geometric-gate's coarse leak sweep, set again and caught only by
    looking past the range I had written down.
    """
    vals = {n: float(resistance_and_distance(_window(n))[0][PREMISE, n // 2])
            for n in (128, 256, 384)}
    assert vals[256] < vals[128]
    assert vals[384] < vals[256]


def test_without_the_background_floor_the_growth_is_clean_and_linear():
    """Which is how we know the reversal is the floor and not the window.

    Pure local window, no background: R_eff roughly doubles per doubling of n,
    the path-graph behaviour. The floor is a free parameter and it is doing all
    of the reversing.
    """
    vals = [float(resistance_and_distance(_window(n, floor=0.0))[0]
                  [PREMISE, n // 2]) for n in (16, 32, 64, 128)]
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))
    for i in range(1, len(vals) - 1):
        assert 1.8 < vals[i + 1] / vals[i] < 2.1, vals


# ------------------------------------------------------------ P6: decoy ----
def test_p6_a_one_injected_edge_shortens_the_reading():
    """The padding attack, in the perception layer.

    Not a bug being tolerated. A declared edge is a declared edge; the layer
    reads the conductance it was given.
    """
    n = 64
    plain = float(resistance_and_distance(_window(n))[0][PREMISE, n // 2])
    decoy = float(resistance_and_distance(
        _window(n, boost_middle=True))[0][PREMISE, n // 2])
    assert decoy < plain


def test_p6_b_it_more_than_halves_it():
    n = 64
    plain = float(resistance_and_distance(_window(n))[0][PREMISE, n // 2])
    decoy = float(resistance_and_distance(
        _window(n, boost_middle=True))[0][PREMISE, n // 2])
    assert decoy / plain < 0.5, (plain, decoy, decoy / plain)


# ------------------------------------------------- P4: the guard that fires --
def _two_rings(n: int = 8) -> np.ndarray:
    h = n // 2
    A = np.zeros((n, n))
    for i in range(h):
        A[i, (i + 1) % h] = 1.0
        A[h + i, h + (i + 1) % h] = 1.0
    return A


def test_p4_a_a_cross_component_reference_pair_refuses():
    with pytest.raises(DisconnectedSpaceError, match="two pieces"):
        perception_distance(_two_rings(), PINNED_SYMMETRIZATION, (0, 4))


def test_p4_b_bare_pinv_would_have_answered_confidently():
    """D3, kept as evidence. The guard was inert because it never looked."""
    A = _two_rings()
    C = A + A.T
    L = np.diag(C.sum(1)) - C
    P = np.linalg.pinv(L)
    dg = np.diag(P)
    bare = float(np.sqrt(max(dg[0] + dg[4] - 2 * P[0, 4], 0.0)))
    assert np.isfinite(bare) and bare > 0.0
    assert abs(bare - 0.790569) < 1e-5


def test_the_guarded_reading_returns_infinity_where_there_is_no_route():
    R, d = resistance_and_distance(_two_rings())
    assert np.isinf(R[0, 4]) and np.isinf(d[0, 4])
    assert np.isfinite(R[0, 1])            # within a piece it still reads


def test_components_are_walked_not_inferred_from_the_matrix():
    lab = components(_two_rings() + _two_rings().T)
    assert lab.max() == 1
    assert set(lab[:4]) == {lab[0]} and set(lab[4:]) == {lab[4]}
    assert lab[0] != lab[4]


# --------------------------------------------------- P3: the pinned token ----
def test_p3_a_wrong_symmetrization_raises():
    with pytest.raises(SymmetrizationError):
        perception_distance(_ring_attention(6), "pi_P", (0, 3))


def test_p3_b_the_pinned_choice_runs():
    d = perception_distance(_ring_attention(6), PINNED_SYMMETRIZATION, (0, 3))
    assert d.shape == (6, 6)
    assert np.isclose(d[0, 3], 1.0)


def test_a_negative_conductance_is_refused_rather_than_clipped():
    A = _ring_attention(6)
    A[0, 1] = -1.0
    with pytest.raises(ValueError, match="not an edge"):
        resistance_and_distance(A)


# --------------------------------------------------------- no overclaim ----
def test_the_module_states_its_blindnesses():
    from stack.perception import lmd_distance
    doc = " ".join(lmd_distance.__doc__.split())
    assert "BLIND TO" in doc
    assert "UNIFORM SCALE" in doc
    assert "It does not know what any token is" in doc or "does not know" in doc
    assert "does not remove it from the READING" in doc


def test_nothing_here_claims_to_be_an_attention_matrix_from_a_model():
    prereg = " ".join(open(os.path.join(HERE, "prereg_perception.md"),
                           encoding="utf-8").read().split())
    assert "Nothing here is a language model" in prereg
    assert "not as something measured in a transformer" in prereg


def test_the_forbidden_words_are_absent_from_the_shipped_stack():
    """CI grep: no un-gameable, no thermodynamics for LISM, no fused score."""
    root = os.path.join(os.path.dirname(os.path.dirname(HERE)), "stack")
    banned = ["un" + "-gameable", "thermodynamic", "integrity" + "_score"]
    # Exempt BY ROLE, not by name. Four kinds of file must be able to quote what
    # they forbid: the ledger, a pre-registration, a test, and a results
    # write-up. A hand-listed allowlist was the first attempt and needed a new
    # entry for every module added -- which is an exemption list that grows,
    # exactly what the ledger says must not happen quietly.
    #
    # It took four tries to get this right. The first exempted only this file
    # and failed on the ledger's own "not thermodynamic entropy"; the second
    # failed on the write-up OF that failure; the third failed when Patch 2 added
    # a test file quoting the same word. Tenth through thirteenth times this
    # session a check has matched the text forbidding the thing it checks for.
    def states_the_rules(name):
        return (name.startswith("test_") and name.endswith(".py")
                or name.startswith("prereg_") and name.endswith(".md")
                or name in ("declarations.md", "RESULTS.md"))

    decoy = "adg_cfe.py"
    assert not states_the_rules(decoy), "shipped code must never be exempt"

    seen = 0
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith((".py", ".md")) or states_the_rules(f):
                continue
            seen += 1
            text = open(os.path.join(dirpath, f), encoding="utf-8").read().lower()
            for b in banned:
                assert b not in text, f"{dirpath}/{f} contains {b}"
    assert seen >= 2, "the grep walked nothing, so it proved nothing"


def test_the_ledger_forbids_the_words_rather_than_merely_avoiding_them():
    """The exemption above is not a hole: the ledger must still say the rule."""
    root = os.path.dirname(os.path.dirname(HERE))
    dec = " ".join(open(os.path.join(root, "stack", "governance",
                                     "declarations.md"),
                        encoding="utf-8").read().split()).lower()
    assert "not thermodynamic" in dec
    assert "the word is not to appear in the module" in dec
    assert 'no fused scalar "integrity"' in dec


def test_the_organization_block_was_lifted_by_a_recorded_decision():
    """Patch 1 blocked this module and asserted the block. Patch 2 lifted it.

    The test is updated rather than deleted: the assertion now pins the
    RESOLUTION, so the ledger cannot quietly drop the rule that produced it.
    """
    root = os.path.dirname(os.path.dirname(HERE))
    dec = " ".join(open(os.path.join(root, "stack", "governance",
                                     "declarations.md"),
                        encoding="utf-8").read().split())
    assert "A1 resolved" in dec
    assert "appears nowhere under `stack/`" in dec
    assert "faithful rename" in dec
    # the old name never ships; the renamed module does
    assert not os.path.exists(os.path.join(root, "stack", "organization",
                                           "adg_tqg.py"))
    assert os.path.exists(os.path.join(root, "stack", "organization",
                                       "adg_cfe.py"))
