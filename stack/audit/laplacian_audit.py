"""Layer-1 audit on a DECLARED graph.

WHAT THIS CANNOT DO, in the same size type as what it does
==========================================================
  * It reads a DECLARED graph. Absence of an edge is absence of a declaration.
    `invisible-edges/` measured candidate undeclared edges moving 9 of 27 names
    on a real import graph, and nothing here recovers them.
  * A cut vertex is a ROUTING FACT, not a fault. A shared kernel that everything
    routes through is usually correct.
  * Load concentration is a routing fact too. It is reported beside the cuts and
    is never combined with them into one number.
  * It is defeated by declared padding. Compose it with structure/lintel.py and
    OR-gate before acting on cuts.
  * Foster's total is an ASSEMBLY self-check. `n - k` is true of every drawing,
    so it can catch a Laplacian that does not match its conductance matrix and
    can never catch a wrong graph.

Pre-registration: stack/audit/prereg_audit.md, sha256
bd6aaae34e41cb2a66b39044d3124fcb282cf383f7ad72093e2283e86d4eb283
"""

from __future__ import annotations

import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from stack.governance.certificate import (  # noqa: E402
    GROUP_NONE, stamp, subject_hash_of_matrix)

try:
    import networkx as nx
except ImportError:                                    # pragma: no cover
    nx = None

#: a DECLARED PREFERENCE, not a found number. The drafted contract names it.
#: It replaces numpy's default rcond, which lmd-scaling/RESULTS.md measured
#: flipping a published verdict on a dense graph at n = 100 depending on how the
#: matrix had been assembled.
DEFAULT_TOL_RATIO = 1e-10


class AssemblyInvariantError(ValueError):
    """The Laplacian does not match the conductance matrix it came from."""


def _components(C, tol=0.0):
    n = C.shape[0]
    adj = np.abs(C) > tol
    np.fill_diagonal(adj, False)
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
    return label, nxt


def foster_selfcheck(C, R, k, atol=1e-8):
    """Two paths to the same quantity: measured sum against parts minus pieces.

    Returned to the CALLER of this function only, for testing. `audit()` never
    puts it in its result dict, because a quantity true of every drawing is not
    a reading of any particular one.
    """
    n = C.shape[0]
    iu = np.triu_indices(n, k=1)
    w = C[iu]
    r = np.where(np.isfinite(R[iu]), R[iu], 0.0)
    measured = float((w * r).sum())
    counted = float(n - k)
    return {"measured": measured, "counted": counted,
            "ok": bool(abs(measured - counted) < atol)}


def audit(C, tol_ratio: float = DEFAULT_TOL_RATIO, _force_pieces=None,
          at=None) -> dict:
    """Cut vertices, effective resistance, guarded distance and per-piece load.

    Carries the certificate schema `(readout, invariance_group, subject_hash,
    date)`, with `invariance_group = GROUP_NONE`. **That is not an oversight.**
    An audit output is a RAW READING: it has survived no family of
    transformations, and this module was in fact measured to be defeated by
    declared padding. Stamping it with a group it never survived would be the
    exact overclaim the schema exists to prevent; naming the absence is the
    honest field value.

    `_force_pieces` exists only so a test can hand in a deliberately wrong
    component count and show that the null-mode cross-check catches it.
    """
    C = np.asarray(C, dtype=float)
    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise ValueError("C must be square")
    if not np.allclose(C, C.T):
        raise ValueError("C must be symmetric; symmetrize before auditing")
    if np.any(C < 0):
        raise ValueError("a negative conductance is not an edge; leave it out")
    n = C.shape[0]

    label, k = _components(C)
    if _force_pieces is not None:
        k = _force_pieces

    L = np.diag(C.sum(1)) - C

    # pinned tolerance, and a cross-check that the algebra agrees with the walk
    w, Q = np.linalg.eigh(L)
    tol = tol_ratio * max(abs(w).max(), 1.0)
    n_null = int((w <= tol).sum())
    if n_null != k:
        raise AssemblyInvariantError(
            f"null-mode count {n_null} != component count {k}; the Laplacian "
            "does not match the conductance matrix it came from")

    inv = np.where(w > tol, 1.0 / np.where(w > tol, w, 1.0), 0.0)
    L_pinv = (Q * inv) @ Q.T
    d = np.diag(L_pinv)
    R = np.maximum(d[:, None] + d[None, :] - 2.0 * L_pinv, 0.0)

    same = label[:, None] == label[None, :]
    # BOTH R and D are masked. Returning a raw R would hand the caller exactly
    # the confident finite number across a void that the guard exists to refuse.
    R = np.where(same, R, np.inf)
    np.fill_diagonal(R, 0.0)
    D = np.sqrt(R)

    check = foster_selfcheck(C, R, k)
    if not check["ok"]:
        raise AssemblyInvariantError(
            f"Foster self-check failed: measured {check['measured']:.9f} "
            f"against parts - pieces {check['counted']:.1f}. This is an "
            "assembly bug, not a finding about the graph.")

    if nx is None:                                     # pragma: no cover
        raise ImportError("networkx is required for cuts and load")
    G = nx.from_numpy_array(C)
    load = {}
    for piece in range(k):
        members = sorted(int(v) for v in np.flatnonzero(label == piece))
        sub = G.subgraph(members)
        if sub.number_of_nodes() > 2:
            load.update(nx.current_flow_betweenness_centrality(sub,
                                                               weight="weight"))
        else:
            load.update({v: 0.0 for v in members})

    return {
        **stamp("cut vertices, per-piece load and guarded resistance",
                GROUP_NONE, subject_hash_of_matrix(C), at=at),
        "D": D, "R": R,
        "cuts": sorted(nx.articulation_points(G)),
        "pieces": k,
        "load": load,
        "tol_ratio": tol_ratio,
        # no Foster total here, at any depth. It is a self-check, not a reading.
    }
