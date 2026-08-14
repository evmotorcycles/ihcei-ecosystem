"""PROX core — resistance geometry at scale.

The LMD telemetry computes proper distance as d(i,j) = sqrt(R_ij), where R is the
effective resistance of a coupling graph, via a dense Moore-Penrose pseudo-inverse
of the Laplacian. That is O(N^3) time and O(N^2) memory: fine for the N=100 ring,
impossible for the 10^6 items on a phone.

This module removes that barrier. The identity

    R_ij = (e_i - e_j)^T A^-1 (e_i - e_j),      A = L + eps*I = C^T C

with C the weighted incidence matrix stacked on sqrt(eps)*I, means R is a squared
Euclidean norm of the map Y = C A^-1. Any Johnson-Lindenstrauss projection Q of Y
therefore preserves every pairwise resistance to within (1 +/- tol), and

    Z = Q C A^-1   =>   R_ij ~= || z_i - z_j ||^2

so k = O(log n / tol^2) columns give every node a coordinate vector whose ordinary
Euclidean distance IS the LMD proper distance. Building Z costs k sparse solves,
not one dense inverse. This is the Spielman-Srivastava resistance sketch.

Two consequences carry the whole design:

  * sqrt(R) is a metric for any positive-definite A, not merely approximately --
    the triangle inequality is an algebraic fact, so proximity can be audited.
  * Scaling every coupling by J scales A by J and Z by J^-1/2 *exactly*, with the
    same Q. The -1/2 contraction law of the telemetry survives compression to
    machine precision, which is what turns coupling into a user-facing dial.

The eps ground term is a weak coupling from every node to one shared "horizon"
node. It keeps the graph connected (otherwise resistance between components is
infinite), makes A positive definite instead of merely semi-definite, and bounds
the condition number so the solves converge. Semantically it is a reach control:
large eps pulls the horizon close and distances saturate locally, small eps lets
association propagate further through the graph.
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import cg, splu

__all__ = [
    "build_system",
    "resistance_embedding",
    "exact_resistance_matrix",
    "distance_matrix",
    "triangle_violations",
]

# Solver crossover, measured on bipartite item-feature graphs (bench/bench_scale.py).
# The direct path factorises once and reuses it across all `dim` right-hand sides,
# which wins decisively while fill-in stays bounded: at 30.5k nodes it took 8.3 s
# against conjugate gradients' 55.8 s. Fill-in then grows faster than problem size,
# and by 60.4k nodes the ordering reverses -- 167 s direct against 99.5 s iterative.
# The crossover sits between those two points; hub features (common n-grams touching
# many items) are what make fill-in outrun the node count.
_DIRECT_SOLVE_MAX_N = 40_000


def build_system(edges, weights, n_nodes, reach=1e-2):
    """Assemble the incidence matrix C and the grounded Laplacian A = C^T C.

    edges    -- (m, 2) integer array of node pairs
    weights  -- (m,) positive couplings; the J of the telemetry, per edge
    reach    -- eps, the universal coupling to the horizon node

    Returns (C, A). C has m + n_nodes rows: one per graph edge, then one per node
    carrying the horizon coupling.
    """
    edges = np.asarray(edges, dtype=np.int64)
    weights = np.asarray(weights, dtype=np.float64)
    if edges.ndim != 2 or edges.shape[1] != 2:
        raise ValueError("edges must have shape (m, 2)")
    if edges.shape[0] != weights.shape[0]:
        raise ValueError("edges and weights must agree in length")
    if np.any(weights <= 0):
        raise ValueError("couplings must be strictly positive")
    if reach <= 0:
        raise ValueError("reach (eps) must be strictly positive")

    m = edges.shape[0]
    sqrt_w = np.sqrt(weights)

    # Edge rows: sqrt(w) * (e_i - e_j).
    rows = np.repeat(np.arange(m, dtype=np.int64), 2)
    cols = edges.reshape(-1)
    vals = np.empty(2 * m, dtype=np.float64)
    vals[0::2] = sqrt_w
    vals[1::2] = -sqrt_w

    # Horizon rows: sqrt(eps) * e_i, one per node.
    g_rows = np.arange(m, m + n_nodes, dtype=np.int64)
    g_cols = np.arange(n_nodes, dtype=np.int64)
    g_vals = np.full(n_nodes, np.sqrt(reach), dtype=np.float64)

    C = sp.csr_matrix(
        (
            np.concatenate([vals, g_vals]),
            (np.concatenate([rows, g_rows]), np.concatenate([cols, g_cols])),
        ),
        shape=(m + n_nodes, n_nodes),
    )
    A = (C.T @ C).tocsc()
    return C, A


def _solve_multi(A, B, tol=1e-8, maxiter=None, solver="auto"):
    """Solve A X = B for X, choosing a direct or iterative path.

    The direct path factorises A once and applies it to all `dim` right-hand sides
    in a single batched triangular solve, which measured ~11x faster than running
    conjugate gradients per column. Fill-in is the only risk, so a memory failure
    falls back to the iterative path rather than aborting the build.
    """
    n, k = B.shape
    if solver in ("auto", "direct") and n <= _DIRECT_SOLVE_MAX_N:
        try:
            return splu(A).solve(B)
        except (MemoryError, RuntimeError):
            if solver == "direct":
                raise

    # Jacobi-preconditioned conjugate gradients. A is symmetric positive definite
    # by construction, so CG is the right solver and the horizon term bounds the
    # condition number.
    diag = A.diagonal()
    diag = np.where(diag > 0, diag, 1.0)
    M = sp.diags(1.0 / diag)
    X = np.empty((n, k), dtype=np.float64)
    for j in range(k):
        try:
            xj, info = cg(A, B[:, j], rtol=tol, maxiter=maxiter, M=M)
        except TypeError:  # scipy < 1.12 spells the tolerance differently
            xj, info = cg(A, B[:, j], tol=tol, maxiter=maxiter, M=M)
        if info != 0:
            raise RuntimeError(f"CG failed to converge on column {j} (info={info})")
        X[:, j] = xj
    return X


def resistance_embedding(
    edges, weights, n_nodes, dim=64, reach=1e-2, seed=0, tol=1e-8, solver="auto"
):
    """Give every node a coordinate vector whose Euclidean distance is LMD distance.

    Returns X of shape (n_nodes, dim) with || X[i] - X[j] || ~= sqrt(R_ij).

    Cost is `dim` sparse solves. Memory is O(m + n*dim) -- never the O(n^2) of a
    dense pseudo-inverse.
    """
    C, A = build_system(edges, weights, n_nodes, reach=reach)
    n_rows = C.shape[0]
    rng = np.random.default_rng(seed)

    # QC = Q @ C, built one sketch row at a time so the (dim x n_rows) Rademacher
    # matrix Q is never materialised. Scale 1/sqrt(dim) makes E||Qv||^2 = ||v||^2.
    scale = 1.0 / np.sqrt(dim)
    QC = np.empty((dim, n_nodes), dtype=np.float64)
    for r in range(dim):
        q = rng.integers(0, 2, size=n_rows).astype(np.float64)
        q = (2.0 * q - 1.0) * scale
        QC[r] = C.T @ q

    # X = A^-1 (QC)^T, so row i of X is the coordinate of node i.
    return _solve_multi(A, np.ascontiguousarray(QC.T), tol=tol, solver=solver)


def exact_resistance_matrix(edges, weights, n_nodes, reach=1e-2):
    """Dense ground-truth R_ij, for validating the sketch. O(n^3) -- tests only."""
    _, A = build_system(edges, weights, n_nodes, reach=reach)
    M = np.linalg.inv(A.toarray())
    d = np.diag(M)
    return d[:, None] + d[None, :] - 2.0 * M


def distance_matrix(X):
    """Pairwise LMD distances from an embedding. O(n^2) -- diagnostics only."""
    sq = np.einsum("ij,ij->i", X, X)
    D2 = sq[:, None] + sq[None, :] - 2.0 * (X @ X.T)
    return np.sqrt(np.maximum(D2, 0.0))


def triangle_violations(D, atol=1e-9):
    """Count triples where d(i,k) > d(i,j) + d(j,k). Must be 0 for a true metric."""
    n = D.shape[0]
    worst = 0.0
    count = 0
    for j in range(n):
        # d(i,k) - (d(i,j) + d(j,k)) for all i,k at this waypoint j
        slack = D - (D[:, j][:, None] + D[j, :][None, :])
        bad = slack > atol
        count += int(np.count_nonzero(bad))
        if bad.any():
            worst = max(worst, float(slack[bad].max()))
    return count, worst
