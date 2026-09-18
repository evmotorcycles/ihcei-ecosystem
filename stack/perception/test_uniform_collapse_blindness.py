"""D0 — the blindness null, held by a test instead of by prose.

WHAT THIS LOCKS
===============
`declarations.md` and Table 2 §C4 split metric collapse into two modes:

  * **UNIFORM** — every conductance scales together. Invisible to **every**
    ratio of distances, pair ratios included, because a uniform rescale cancels
    in *any* quotient.
  * **DIFFERENTIAL** — background conductance rises relative to structure.
    Visible to pair ratios; this is the mode the 40-agent ring measured.

The first draft of that row said the collapse "must be measured on ratios
between pairs, not absolutes." **That was wrong**, and the correction is the
reason this file exists: pair ratios cannot see uniform collapse either.

**THE NULL IS THE RESULT.** A uniform rescale leaving every pair ratio unchanged
is not a failed measurement — it is the control that establishes what the
ratio instrument cannot do. A null that lives only in prose can be summarised
away in a later abstract; one held by a test cannot.

WHAT THIS CANNOT DO
===================
  * It shows the instrument is blind to uniform scale. It does **not** show
    that any real system ever collapses uniformly.
  * It is a statement about the readout, not about attention, not about
    latency, and not about any physical medium.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stack.perception.lmd_distance import (  # noqa: E402
    perception_distance, resistance_and_distance)

PINNED = "A+A.T"


def _ring_with_clique(n=12, clique=4, w=1.0):
    """A ring, plus a denser clique — structure worth having ratios about."""
    A = np.zeros((n, n))
    for i in range(n):
        A[i, (i + 1) % n] = A[(i + 1) % n, i] = w
    for i in range(clique):
        for j in range(i + 1, clique):
            A[i, j] = A[j, i] = w
    return A


def _pair_ratios(A):
    """Every finite ratio d(i,j)/d(k,l) — the instrument under examination."""
    _, d = resistance_and_distance(A, PINNED)
    n = d.shape[0]
    vals = np.array([d[i, j] for i in range(n) for j in range(i + 1, n)])
    finite = vals[np.isfinite(vals) & (vals > 0)]
    return finite[:, None] / finite[None, :]


# ------------------------------------------------- D0: the blindness null ----
@pytest.mark.parametrize("scale", [2.0, 10.0, 0.5, 1e3])
def test_d0_a_uniform_rescale_leaves_every_pair_ratio_unchanged(scale):
    """THE CONTROL. The expected result is *no change*, and that is the point."""
    A = _ring_with_clique()
    before, after = _pair_ratios(A), _pair_ratios(A * scale)
    assert before.shape == after.shape
    assert np.allclose(before, after, rtol=0, atol=1e-9), (
        f"a pair ratio moved under a uniform rescale by {scale}; if this ever "
        "fires, the ratio API is not scale-invariant and C1 is wrong")


@pytest.mark.parametrize("scale", [2.0, 10.0, 0.5])
def test_d0_the_absolute_distances_DO_move_so_the_null_is_not_vacuous(scale):
    """Otherwise the test above would pass on an instrument that reads nothing.

    `d → d·c^(−1/2)` is identity C1: scaling conductance by c divides every
    distance by √c. This is the half that makes the blindness meaningful.
    """
    A = _ring_with_clique()
    _, d0 = resistance_and_distance(A, PINNED)
    _, d1 = resistance_and_distance(A * scale, PINNED)
    m = np.isfinite(d0) & (d0 > 0)
    assert not np.allclose(d0[m], d1[m]), "absolutes did not move; fixture is inert"
    np.testing.assert_allclose(d1[m], d0[m] / np.sqrt(scale), rtol=1e-9)


def test_d0_differential_change_IS_visible_to_pair_ratios():
    """The other arm: the mode pair ratios *can* see.

    Raising background conductance relative to structure is not a uniform
    rescale, and the ratios move. Without this, the blindness result could be
    mistaken for 'ratios never move'.
    """
    A = _ring_with_clique()
    B = A.copy()
    background = (B == 0)
    np.fill_diagonal(background, False)
    B[background] = 0.25                      # raise the floor, not the whole
    before, after = _pair_ratios(A), _pair_ratios(B)
    assert not np.allclose(before, after, atol=1e-6), (
        "differential change was invisible to pair ratios; then pair ratios "
        "would be useless for C4b as well as C4a")


def test_the_two_modes_are_named_and_not_conflated():
    """Any 'collapse' claim must say WHICH mode. Table 2 C4a / C4b."""
    doc = " ".join(__doc__.split())
    assert "UNIFORM" in doc and "DIFFERENTIAL" in doc
    assert "pair ratios cannot see uniform collapse either" in doc
    assert "THE NULL IS THE RESULT." in doc


def test_this_file_claims_nothing_about_any_physical_medium():
    doc = " ".join(__doc__.split())
    assert "not about any physical medium" in doc
    assert "does **not** show" in doc
