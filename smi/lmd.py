#!/usr/bin/env python3
"""lmd.py -- the metric engine behind the Synaptic Mesh Interface.

    from smi.lmd import metric_from_laplacian, mesh_metric

Distance between two on-screen elements is not authored. It is the effective
resistance between them on the graph of what depends on what:

    L+   = pinv(L)
    R_ij = L+_ii + L+_jj - 2 L+_ij
    d_ij = sqrt(R_ij)

Two elements joined by many strong paths sit close together; two joined only by
a long weak chain drift apart. Nobody positions anything.

*** WHAT IS BEING MEASURED ***
A dependency graph inside running software: which live elements determine which
others, and how strongly. J is the strength of one such dependency; d is how far
apart two elements should sit given all of them. This is telemetry on an
information layer. It is not a statement about matter or distance, and the name
is a name -- see SCOPE.md.

*** GLOBAL COUPLING IS A ZOOM, BY CONSTRUCTION ***
For a scalar J > 0, pinv(J*L0) = (1/J) * pinv(L0). So R(J) = R(1)/J and
d = sqrt(R) is proportional to J^-0.5 EXACTLY -- for every pair, on every graph,
at every size. That is elementary linear algebra, and in an interface it is a
property worth having deliberately: a global tension control rescales the whole
picture and changes NOTHING ELSE. It cannot reorder elements, cannot change what
is near what, and cannot alter a value. It is safe to hand to a user.

The corollary matters just as much: because the -0.5 slope comes out on every
graph, measuring it verifies nothing about any particular graph. It is kept as a
smoke test -- it breaks the moment pinv, the Laplacian or the clipping breaks --
and never reported as a result. What carries information here is TOPOLOGY and
LOCAL coupling.

*** THE TWO PLACES pinv WILL QUIETLY LIE TO YOU ***
1. On a DISCONNECTED graph it returns a finite number between components. Two
   elements with no path between them should be infinitely far apart; the
   pseudo-inverse gives them a modest distance and the layout puts unrelated
   things side by side. Components are therefore detected explicitly here.
2. At J -> 0 the whole Laplacian goes to zero, pinv(0) = 0, and every distance
   collapses to ZERO. A completely broken mesh would render as a perfectly
   contracted one. The dead case is caught before the metric is trusted.

Both are guarded below and both are asserted by smi/test_smi.py.
"""
from __future__ import annotations

import math

from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np

# A layout engine measured to 1e-6 cannot run at float32: on a 100-node ring the
# identity slope reads -0.500003, which is noise mistaken for signal.
jax.config.update("jax_enable_x64", True)

#: below this total edge weight the mesh is treated as dead rather than measured
DEAD_MESH_EPS = 1e-12

#: A coupling below this is DECLARED FADING: still connected, but too weak to
#: show at display precision. Without a name for it, a wire reading 0.00 in a
#: readout while the legend insists "live" is a fourth, unnamed state -- the
#: interface saying connected and the arithmetic saying I move nothing.
FADE_BELOW = 0.01


@jax.jit
def metric_from_laplacian(L):
    """Proper distances d_ij = sqrt(R_ij) from a graph Laplacian. JIT-compiled.

    Vectorised: one pinv and two broadcasts, no Python loop over pairs. This is
    the whole hot path -- everything else in the interface is bookkeeping.
    """
    L_pinv = jnp.linalg.pinv(L)
    diag = jnp.diag(L_pinv)
    R = diag[:, None] + diag[None, :] - 2.0 * L_pinv
    # tiny negative values are floating-point dust, not negative resistance
    return jnp.sqrt(jnp.clip(R, 0.0))


def components(L, tol=1e-12):
    """Which nodes can actually reach which, by walking the adjacency.

    pinv does not know or care that a graph is in pieces. This does.
    Returns an integer label per node; equal labels mean connected.
    """
    A = np.asarray(L, dtype=float).copy()
    np.fill_diagonal(A, 0.0)
    adj = np.abs(A) > tol
    n = adj.shape[0]
    label = np.full(n, -1, dtype=int)
    nxt = 0
    for start in range(n):
        if label[start] != -1:
            continue
        stack, label[start] = [start], nxt
        while stack:
            u = stack.pop()
            for v in np.nonzero(adj[u])[0]:
                if label[v] == -1:
                    label[v] = nxt
                    stack.append(v)
        nxt += 1
    return label


def mesh_metric(L, tol=1e-12):
    """The distance matrix an interface may actually trust.

    Same as metric_from_laplacian, with the two lies removed:
      * pairs in different components come back as inf, not as a small number
      * a mesh with no coupling left at all comes back as all-inf, not all-zero
    """
    L = np.asarray(L, dtype=float)
    n = L.shape[0]
    off = np.abs(L - np.diag(np.diag(L))).sum()
    if off < DEAD_MESH_EPS:
        # every link is gone. The metric would say zero -- maximum contraction --
        # which is the exact opposite of the truth.
        D = np.full((n, n), np.inf)
        np.fill_diagonal(D, 0.0)
        return D, np.arange(n), True

    # np.asarray on a JAX array gives a READ-ONLY view; the diagonal fix below
    # then fails, but only on connected graphs, because the disconnected branch
    # happens to build a fresh array. Copy explicitly.
    D = np.array(metric_from_laplacian(jnp.asarray(L)), dtype=float, copy=True)
    lab = components(L, tol)
    if lab.max() > 0:
        D = np.where(lab[:, None] == lab[None, :], D, np.inf)
    np.fill_diagonal(D, 0.0)
    return D, lab, False


# ----------------------------------------------------------------- graphs ---
def ring_laplacian(n, J=1.0):
    """Weighted 1-D ring. Each node joined to its two neighbours with weight J."""
    if n < 3:
        raise ValueError("a ring needs at least 3 nodes")
    W = np.zeros((n, n))
    for i in range(n):
        W[i, (i + 1) % n] = W[(i + 1) % n, i] = float(J)
    return np.diag(W.sum(1)) - W


def laplacian_from_edges(n, edges):
    """Laplacian from (i, j, weight) triples. Symmetric by construction."""
    W = np.zeros((n, n))
    for i, j, w in edges:
        if i == j:
            raise ValueError(f"a node cannot depend on itself: node {i}")
        W[i, j] = W[j, i] = float(w)
    return np.diag(W.sum(1)) - W


@dataclass(frozen=True)
class Sweep:
    """The result of scaling every edge by J and watching distance contract."""
    couplings: np.ndarray
    distances: np.ndarray
    slope: float
    r_squared: float
    pair: tuple

    @property
    def matches_identity(self):
        return abs(self.slope + 0.5) <= 1e-4 and self.r_squared >= 0.999999


def sweep_coupling(L_unit, pair, lo=-1.0, hi=2.0, steps=15):
    """Scale a unit-weight Laplacian across J and record one pair's distance.

    The slope this produces is -0.5 on ANY graph. It is a check that the engine
    is right, not a discovery about the graph.
    """
    i, j = pair
    Js = np.logspace(lo, hi, steps)
    ds = np.array([float(metric_from_laplacian(jnp.asarray(J * np.asarray(L_unit)))[i, j])
                   for J in Js])
    if np.any(ds <= 0):
        raise ValueError("a zero distance appeared; the pair is probably not connected")
    slope, _ = np.polyfit(np.log10(Js), np.log10(ds), 1)
    r2 = float(np.corrcoef(np.log10(Js), np.log10(ds))[0, 1] ** 2)
    return Sweep(Js, ds, float(slope), r2, (i, j))


def procrustes2d(Q, P):
    """Rotate/reflect a new embedding onto the previous one.

    Classical MDS fixes an embedding only up to rotation and reflection: the
    eigenvectors are defined up to sign, so a small change in the graph can hand
    back the same picture upside down. Deterministic per input, and to a person
    dragging it, the map flipping under their finger reads as the positions
    being arbitrary -- which is exactly the claim this engine makes against.

    Whichever orthogonal transform moves the shared nodes least is chosen. Real
    change still shows; the cosmetic flips stop. Closed form: 2-D needs no SVD.
    """
    Q = np.asarray(Q, dtype=float)
    P = np.asarray(P, dtype=float)
    n = min(len(Q), len(P))
    if n < 2:
        return Q.copy()
    qc, pc = Q[:n].mean(0), P[:n].mean(0)
    best = None
    for flip in (1.0, -1.0):
        q = (Q[:n] - qc) * np.array([flip, 1.0])
        p = P[:n] - pc
        num = float((q[:, 0] * p[:, 1] - q[:, 1] * p[:, 0]).sum())
        den = float((q[:, 0] * p[:, 0] + q[:, 1] * p[:, 1]).sum())
        th = math.atan2(num, den)
        c, s = math.cos(th), math.sin(th)
        rot = np.array([[c, -s], [s, c]])
        resid = float((((q @ rot.T) - p) ** 2).sum())
        if best is None or resid < best[0]:
            best = (resid, th, flip)
    _, th, flip = best
    c, s = math.cos(th), math.sin(th)
    rot = np.array([[c, -s], [s, c]])
    return ((Q - qc) * np.array([flip, 1.0])) @ rot.T + pc


FLAT_WARN = 0.25


def layout2d(D, keep):
    """Classical MDS: double-centre the squared distances, take the top two
    eigenvectors. The flat picture that best preserves the metric.

    Mirrors smi/lmd.js layout2d exactly; smi/test_parity.py checks that.
    """
    keep = list(keep)
    m = len(keep)
    sq = np.array([[float(D[a][b]) ** 2 for b in keep] for a in keep], dtype=float)
    rm = sq.mean(1)
    B = -0.5 * (sq - rm[:, None] - rm[None, :] + rm.mean())
    w, V = np.linalg.eigh(B)
    order = np.argsort(w)[::-1]
    k1 = order[0]
    k2 = order[1] if m > 1 else order[0]
    return np.column_stack([
        V[:, k1] * math.sqrt(max(float(w[k1]), 0.0)),
        V[:, k2] * math.sqrt(max(float(w[k2]), 0.0)),
    ])


def flatness(D, keep, xy):
    """How much of the metric survived being flattened onto a plane.

    Returns (worst_ratio, a, b): the pair whose DRAWN separation is the smallest
    fraction of its TRUE distance, and which pair that is. 1.0 means every
    distance in the picture is the real one.

    This is not a nicety. A mesh of five elements generally needs four
    dimensions; a screen has two, and classical MDS drops the difference in
    silence. On the invoice mesh SMI ships with, `VAT` and `Total` are drawn on
    top of each other while their true distance is 0.5 -- among the largest in
    the mesh. An interface whose whole claim is that POSITION MEANS SOMETHING
    cannot leave that unsaid, any more than it can print 0.00 for a wire it
    still calls live. Measure it, name it, show it.
    """
    keep = list(keep)
    worst, pair = 1.0, (None, None)
    for i in range(len(keep)):
        for j in range(i + 1, len(keep)):
            true_d = float(D[keep[i]][keep[j]])
            if not np.isfinite(true_d) or true_d <= 0:
                continue
            drawn = float(np.hypot(xy[i][0] - xy[j][0], xy[i][1] - xy[j][1]))
            ratio = drawn / true_d
            if ratio < worst:
                worst, pair = ratio, (keep[i], keep[j])
    return worst, pair[0], pair[1]


def normalised(D):
    """Layout SHAPE with scale divided out -- what H1 says J cannot change."""
    finite = D[np.isfinite(D)]
    m = finite.max() if finite.size else 1.0
    return D / (m if m > 0 else 1.0)
