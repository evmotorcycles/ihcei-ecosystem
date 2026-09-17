"""Commit 3, the guarded Laplacian audit. P4-P6 / A1-A8.

Locked in prereg_audit.md, sha256
bd6aaae34e41cb2a66b39044d3124fcb282cf383f7ad72093e2283e86d4eb283
"""

from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from stack.audit.laplacian_audit import (  # noqa: E402
    DEFAULT_TOL_RATIO, AssemblyInvariantError, audit, foster_selfcheck)

PREREG_SHA = "bd6aaae34e41cb2a66b39044d3124fcb282cf383f7ad72093e2283e86d4eb283"


def _ring(n, w=1.0):
    C = np.zeros((n, n))
    for i in range(n):
        C[i, (i + 1) % n] = C[(i + 1) % n, i] = w
    return C


def _two_rings(n=8):
    h = n // 2
    C = np.zeros((n, n))
    for i in range(h):
        C[i, (i + 1) % h] = C[(i + 1) % h, i] = 1.0
        C[h + i, h + (i + 1) % h] = C[h + (i + 1) % h, h + i] = 1.0
    return C


def _chain_with_cut(n=9):
    """Two rings of 4 joined through a single middle node: node 4 is the cut."""
    C = np.zeros((n, n))
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4),
                 (4, 5), (5, 6), (6, 7), (7, 8), (8, 5)]:
        C[a, b] = C[b, a] = 1.0
    return C


def _band(n, b=2, w=1.0, floor=0.0):
    A = np.full((n, n), floor)
    np.fill_diagonal(A, 0.0)
    for i in range(n):
        for j in range(max(0, i - b), min(n, i + b + 1)):
            if i != j:
                A[i, j] = w
    return A


# ------------------------------------------------------------- the lock ----
def test_the_preregistration_is_the_one_that_was_hashed():
    with open(os.path.join(HERE, "prereg_audit.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == PREREG_SHA


def test_the_module_declares_the_same_hash():
    from stack.audit import laplacian_audit
    assert PREREG_SHA in laplacian_audit.__doc__


# ------------------------------------------- the symmetrization finding ----
def test_the_supplied_regime_numbers_skip_the_pinned_symmetrization():
    """RECORDED, measured before the pre-registration was written.

    A banded matrix is already symmetric, so A + A.T = 2A: every conductance
    doubles and every resistance halves. The supplied Regime-2 figures match
    the UNSYMMETRIZED reading exactly, to three decimals.
    """
    supplied = {16: 3.358, 32: 6.558, 64: 12.958, 128: 25.758}
    for n, want in supplied.items():
        A = _band(n)
        assert np.allclose(A, A.T), "the fixture is already symmetric"
        plain = audit(A)["R"][0, n - 1]
        pinned = audit(A + A.T)["R"][0, n - 1]
        assert abs(plain - want) < 5e-3, (n, plain, want)
        assert abs(pinned - want / 2.0) < 5e-3, (n, pinned, want / 2.0)


def test_regime_one_reproduces_the_complete_graph_identity():
    """This one agrees with the supplied numbers, and independently."""
    for n in (16, 32, 64):
        A = np.ones((n, n)) / n
        R = audit(A + A.T)["R"]
        off = R[~np.eye(n, dtype=bool)]
        assert np.abs(off - 1.0).max() < 1e-14, n


# --------------------------------------------- A1-A3: the assembly check ----
def test_a1_an_injected_assembly_bug_raises():
    """An edge in C that the Laplacian does not carry."""
    C = _ring(8)
    L = np.diag(C.sum(1)) - C
    L[0, 1] = L[1, 0] = 0.0                  # drop one edge from L only
    L[0, 0] -= 1.0
    L[1, 1] -= 1.0
    # rebuild the conductance matrix this broken L implies, then hand the
    # ORIGINAL C in with it -- the two-path check must notice
    n = 8
    k = 1
    w, Q = np.linalg.eigh(L)
    tol = DEFAULT_TOL_RATIO * max(abs(w).max(), 1.0)
    inv = np.where(w > tol, 1.0 / np.where(w > tol, w, 1.0), 0.0)
    P = (Q * inv) @ Q.T
    d = np.diag(P)
    R = np.maximum(d[:, None] + d[None, :] - 2.0 * P, 0.0)
    assert not foster_selfcheck(C, R, k)["ok"]


def test_a2_a_clean_graph_does_not_raise_connected_or_not():
    for C in (_ring(8), _two_rings(8), _chain_with_cut(9)):
        out = audit(C)
        assert out["pieces"] >= 1


def test_a3_a_wrong_component_count_is_caught_by_the_null_modes():
    with pytest.raises(AssemblyInvariantError, match="null-mode count"):
        audit(_two_rings(8), _force_pieces=1)
    with pytest.raises(AssemblyInvariantError, match="null-mode count"):
        audit(_ring(8), _force_pieces=3)


def test_the_self_check_raises_rather_than_asserts():
    """`python -O` strips assert statements. A self-check that can be compiled
    away is not a self-check, so this deviates from the drafted code."""
    src = open(os.path.join(HERE, "laplacian_audit.py"), encoding="utf-8").read()
    body = src.split('"""', 2)[-1]                 # skip the module docstring
    assert "raise AssemblyInvariantError" in body
    assert "\n    assert " not in body


# ------------------------------------------------- A4-A5: the component guard --
def test_a4_cross_component_pairs_are_infinite_in_both_r_and_d():
    out = audit(_two_rings(8))
    assert out["pieces"] == 2
    assert np.isinf(out["R"][0, 4]) and np.isinf(out["D"][0, 4])
    assert np.isfinite(out["R"][0, 1]) and np.isfinite(out["D"][0, 1])
    assert out["R"][0, 0] == 0.0


def test_a5_bare_pinv_would_have_answered_confidently():
    """The control that makes A4 mean something."""
    C = _two_rings(8)
    L = np.diag(C.sum(1)) - C
    P = np.linalg.pinv(L)
    d = np.diag(P)
    bare = float(np.sqrt(max(d[0] + d[4] - 2 * P[0, 4], 0.0)))
    assert np.isfinite(bare) and bare > 0.0
    assert abs(bare - 0.790569) < 1e-5


# --------------------------------------------------- A6: Foster stays out ----
def test_a6_the_foster_total_appears_nowhere_in_the_result():
    out = audit(_chain_with_cut(9))

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield str(k)
                yield from walk(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                yield from walk(v)

    keys = " ".join(walk(out)).lower()
    for banned in ("foster", "measured", "counted", "conserved", "expected_total"):
        assert banned not in keys, banned


def test_the_self_check_still_runs_and_still_agrees():
    """Absent from the output is not absent from the code."""
    C = _chain_with_cut(9)
    out = audit(C)
    chk = foster_selfcheck(C, out["R"], out["pieces"])
    assert chk["ok"]
    assert abs(chk["measured"] - (9 - 1)) < 1e-8


def test_foster_is_conserved_across_components_too():
    C = _two_rings(8)
    out = audit(C)
    chk = foster_selfcheck(C, out["R"], out["pieces"])
    assert chk["ok"] and abs(chk["counted"] - (8 - 2)) < 1e-12


# ----------------------------------------------- A7-A8: padding and load ----
def _padded(C):
    """Declared edges only. No new nodes, no new evidence."""
    P = C.copy()
    for a, b in [(0, 5), (1, 6), (2, 7), (3, 8)]:
        P[a, b] = P[b, a] = 1.0
    return P


def test_a7_padding_clears_the_cut_vertices():
    base = audit(_chain_with_cut(9))
    assert base["cuts"], "the fixture must have a cut vertex to clear"
    after = audit(_padded(_chain_with_cut(9)))
    assert after["cuts"] == []


def test_the_prediction_that_missed(cohort=None):
    """A8. The maximum load FALLS under padding: 0.5714 -> 0.3088.

    Registered the other way, and the miss is worth more than the hit would
    have been. Padding adds routes, and routes SPREAD current-flow betweenness
    rather than concentrating it -- so both sensors in the proposed OR-gate move
    in the attacker's favour:

        cuts      3 -> 0     gamed
        max load  0.5714 -> 0.3088   gamed

    An OR-gate of (cuts fell) OR (load rose) therefore does NOT trip on the
    padding attack. A cuts-only gate misses it and the proposed two-sensor gate
    misses it too. The second sensor has to be something else --
    see the test below.
    """
    before = audit(_chain_with_cut(9))
    after = audit(_padded(_chain_with_cut(9)))
    lo = max(before["load"].values())
    hi = max(after["load"].values())
    assert hi < lo, "the prediction was that it rises; record the miss"
    assert abs(lo - 0.5714285714) < 1e-6
    assert abs(hi - 0.3088474026) < 1e-6


def test_the_sensor_that_does_move_against_the_padding():
    """POST HOC. No prediction was registered.

    `fathom.sound`'s deepest dependence RISES under the same padding, on a
    fixture with nothing in common with agi-stack/'s except the attack:

        deepest dependence  0.133333 -> 0.257161

    agi-stack/ measured 0.111 -> 0.619 on its own graph. Two independent
    constructions, same direction. So the OR-gate's second sensor should be
    deepest dependence, not load -- which is a change to a proposed design and
    is recorded here rather than made silently in the module.
    """
    from fathom.fathom import Claim, sound

    def as_edges(C):
        n = C.shape[0]
        return [(f"n{i}", f"n{j}", float(C[i, j]))
                for i in range(n) for j in range(i + 1, n) if C[i, j] > 0]

    sources = ["n0", "n1", "n2"]
    before = sound(Claim("n8", sources, as_edges(_chain_with_cut(9))))
    after = sound(Claim("n8", sources, as_edges(_padded(_chain_with_cut(9)))))
    assert after["deepest_dependence"] > before["deepest_dependence"]
    assert abs(before["deepest_dependence"] - 0.133333) < 1e-5
    assert abs(after["deepest_dependence"] - 0.257161) < 1e-5


def test_the_two_sensors_are_reported_separately_and_never_fused():
    out = audit(_chain_with_cut(9))
    assert isinstance(out["cuts"], list)
    assert isinstance(out["load"], dict)
    assert set(out) == {"D", "R", "cuts", "pieces", "load", "tol_ratio"}


# ------------------------------------------------------- the refusals ----
def test_an_asymmetric_input_is_refused_rather_than_symmetrized_quietly():
    A = np.zeros((4, 4))
    A[0, 1] = 1.0
    with pytest.raises(ValueError, match="symmetric"):
        audit(A)


def test_a_negative_conductance_is_refused():
    C = _ring(6)
    C[0, 1] = C[1, 0] = -1.0
    with pytest.raises(ValueError, match="not an edge"):
        audit(C)


def test_the_tolerance_is_declared_not_inherited():
    out = audit(_ring(8))
    assert out["tol_ratio"] == DEFAULT_TOL_RATIO
    assert audit(_ring(8), tol_ratio=1e-8)["tol_ratio"] == 1e-8
    prereg = " ".join(open(os.path.join(HERE, "prereg_audit.md"),
                           encoding="utf-8").read().split())
    assert "declared preference, not a found number" in prereg


def test_the_module_states_what_it_cannot_do():
    from stack.audit import laplacian_audit
    doc = " ".join(laplacian_audit.__doc__.split())
    assert "ROUTING FACT, not a fault" in doc
    assert "absence of a declaration" in doc
    assert "defeated by declared padding" in doc
    assert "can never catch a wrong graph" in doc
