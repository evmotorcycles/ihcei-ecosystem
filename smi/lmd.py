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

*** THE PART THAT IS AN IDENTITY, NOT A DISCOVERY ***
For a scalar J > 0, pinv(J*L0) = (1/J) * pinv(L0). So R(J) = R(1)/J and
d = sqrt(R) is proportional to J^-0.5 EXACTLY -- for every pair, on every graph,
at every size. The famous -0.5 log-log slope is elementary linear algebra. It is
worth measuring because it catches a broken implementation, and it is worth
being clear that it is not evidence about anything else.

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

from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np

# A layout engine measured to 1e-6 cannot run at float32: on a 100-node ring the
# identity slope reads -0.500003, which is noise mistaken for signal.
jax.config.update("jax_enable_x64", True)

#: below this total edge weight the mesh is treated as dead rather than measured
DEAD_MESH_EPS = 1e-12


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


def normalised(D):
    """Layout SHAPE with scale divided out -- what H1 says J cannot change."""
    finite = D[np.isfinite(D)]
    m = finite.max() if finite.size else 1.0
    return D / (m if m > 0 else 1.0)
