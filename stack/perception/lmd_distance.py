"""Perception-layer LMD distance on attention/latent conductance graphs.

Object graph: symmetrized attention (or JEPA transition) conductances.
Readout: pairwise d = sqrt(R_eff), exposed only as ratios/ranks vs a reference
pair.

WHAT THIS IS BLIND TO, in the same size type as what it does
============================================================
  * UNIFORM SCALE. Under C -> c*C, d -> d/sqrt(c) exactly, because
    pinv(cL) = pinv(L)/c. The ratio API divides that out of the OUTPUT; it does
    not remove it from the READING. Two graphs differing only by a global factor
    stay indistinguishable, by design.
  * THE SYMMETRIZATION CHOICE. A+A.T is pinned in the ledger. A different choice
    is a different object graph and a different number.
  * MEANING. R_eff reads a conductance graph somebody supplied. It does not know
    what any token is.
  * DECLARED EDGES. One injected high-conductance edge shortens the reading.
    That is not a bug being tolerated; it is the same result as agi-stack/, and
    the remedy is to say so rather than to claim the reading is robust.

This does NOT audit declared claims and does NOT return absolute product
distances.
"""

from __future__ import annotations

import numpy as np

PINNED_SYMMETRIZATION = "A+A.T"

#: below this a conductance is treated as no edge when walking components.
EDGE_EPS = 1e-12


class SymmetrizationError(ValueError):
    pass


class DisconnectedSpaceError(ValueError):
    pass


def _symmetrize(A: np.ndarray, symmetrization: str) -> np.ndarray:
    if symmetrization != PINNED_SYMMETRIZATION:
        raise SymmetrizationError(
            f"undeclared symmetrization {symmetrization!r}; "
            f"ledger requires {PINNED_SYMMETRIZATION!r}")
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if not np.all(np.isfinite(A)):
        raise ValueError("A carries a non-finite conductance")
    if np.any(A < 0.0):
        raise ValueError("a negative conductance is not an edge; leave it out")
    return A + A.T


def _laplacian(C: np.ndarray) -> np.ndarray:
    # a self-loop adds equally to the degree and to the diagonal of C, so it
    # cancels here and contributes nothing. Left in rather than stripped, so
    # the arithmetic matches the declared C.
    deg = np.sum(C, axis=1)
    return np.diag(deg) - C


def components(C: np.ndarray, tol: float = EDGE_EPS) -> np.ndarray:
    """Which nodes can actually reach which, by walking the conductances.

    pinv does not know or care that a graph is in pieces. This does. On two
    disjoint 4-rings bare pinv returns d(0,4) = 0.790569 -- finite, positive and
    meaningless -- so the walk runs before any reading is handed out.
    """
    A = np.asarray(C, dtype=float).copy()
    np.fill_diagonal(A, 0.0)
    adj = np.abs(A) > tol
    n = adj.shape[0]
    label = np.full(n, -1, dtype=int)
    nxt = 0
    for start in range(n):
        if label[start] != -1:
            continue
        stack = [start]
        label[start] = nxt
        while stack:
            u = stack.pop()
            for v in np.flatnonzero(adj[u]):
                if label[v] == -1:
                    label[v] = nxt
                    stack.append(int(v))
        nxt += 1
    return label


def _effective_resistance(L: np.ndarray) -> np.ndarray:
    # Moore-Penrose on a real symmetric PSD Laplacian.
    # NOTE: numpy's default rcond decides the rank by comparing singular values
    # to rcond * largest. lmd-scaling/RESULTS.md measured that choice flipping a
    # published verdict on a DENSE graph at n=100. Sparse conductance graphs sit
    # well away from that line; dense ones do not, and this does not solve it.
    L_pinv = np.linalg.pinv(L)
    diag = np.diag(L_pinv)
    R = diag[:, None] + diag[None, :] - 2.0 * L_pinv
    return np.maximum(R, 0.0)


def resistance_and_distance(A: np.ndarray,
                            symmetrization: str = PINNED_SYMMETRIZATION):
    """Internal: R_eff and d = sqrt(R), with unreachable pairs set to inf.

    Callers of product code use `perception_distance`.
    """
    C = _symmetrize(A, symmetrization)
    lab = components(C)
    R = _effective_resistance(_laplacian(C))
    if lab.max() > 0:
        same = lab[:, None] == lab[None, :]
        R = np.where(same, R, np.inf)
    np.fill_diagonal(R, 0.0)
    return R, np.sqrt(R)


def perception_distance(A: np.ndarray, symmetrization: str,
                        reference_pair: tuple) -> np.ndarray:
    """Ratio API: d_ij / d_ref.

    Rank order is meaningful. Absolute scale is not a product claim.
    """
    C = _symmetrize(A, symmetrization)
    lab = components(C)
    u, v = reference_pair
    if lab[u] != lab[v]:
        raise DisconnectedSpaceError(
            f"reference_pair {reference_pair} spans two pieces of the graph; "
            "there is no route between them, so there is nothing to normalise "
            "by. This is an empty reading, not a large one.")
    _, d = resistance_and_distance(A, symmetrization)
    ref = float(d[u, v])
    if ref <= 0.0 or not np.isfinite(ref):
        raise DisconnectedSpaceError(
            f"reference_pair {reference_pair} has non-positive distance; "
            "cannot normalise")
    return d / ref


def rank_order(d_ratio: np.ndarray, row: int) -> np.ndarray:
    """Argsort distances from `row`. Stable, so ranks are reproducible."""
    return np.argsort(d_ratio[row], kind="mergesort")
