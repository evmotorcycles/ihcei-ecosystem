#!/usr/bin/env python3
"""lmd_jax.py -- the LMD engine, standalone. One file, copy-and-run.

    python3 smi/lmd_jax.py

Nothing else in this repository is needed. Drop it in a notebook, a Colab cell
or a fresh directory and it runs: device check, the JIT-compiled metric, the
coupling sweep, and the two guards the raw formula needs.

Everything here also lives inside smi/lmd.py, which is what the rest of SMI
imports. This file exists so the engine can be read, run and taken away in one
piece.

WHAT IS BEING MEASURED
A dependency graph inside running software: which live elements determine which
others (J), and how far apart they should therefore sit (d). Information layer.
Not a claim about matter or physical distance.
"""
import math

import jax
import jax.numpy as jnp
import numpy as np

# A metric read to 1e-6 cannot run at float32: on a 100-node ring the slope
# below reads -0.500003, which is noise being mistaken for signal.
jax.config.update("jax_enable_x64", True)

DEAD_MESH_EPS = 1e-12


# ============================================================ the metric ====
@jax.jit
def reconstruct_metric_from_laplacian(L):
    """d_ij = sqrt(R_ij) from a graph Laplacian. Vectorised, JIT-compiled.

    R_ij = L+_ii + L+_jj - 2 L+_ij, the effective resistance. One pinv and two
    broadcasts produce every pair at once -- no Python loop anywhere.
    """
    L_pinv = jnp.linalg.pinv(L)
    diag = jnp.diag(L_pinv)
    R = diag[:, None] + diag[None, :] - 2.0 * L_pinv
    # NOTE: older JAX took clip(x, a_min=0.0). That keyword was removed; passing
    # it raises TypeError on jax >= 0.6. Positional works on every version.
    return jnp.sqrt(jnp.clip(R, 0.0))


# ============================================ the two things pinv gets wrong =
def components(L, tol=1e-12):
    """Which nodes can actually reach which. pinv neither knows nor cares."""
    A = np.array(L, dtype=float, copy=True)
    np.fill_diagonal(A, 0.0)
    adj = np.abs(A) > tol
    n, label, nxt = adj.shape[0], np.full(len(A), -1, dtype=int), 0
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

    Same as above, with the two lies removed:

      1. On a DISCONNECTED graph the pseudo-inverse returns a finite number
         between components -- 1.118 across a cut ring, which is NEARER than a
         genuine 1.732 inside one half. Unguarded, a layout puts two unrelated
         elements side by side. Components are detected explicitly.

      2. At J = 0 the whole Laplacian is zero, pinv(0) = 0, and every distance
         collapses to ZERO. A completely dead mesh measures as PERFECTLY
         CONTRACTED -- identical to a perfectly coupled one. Caught before the
         metric is trusted.
    """
    L = np.asarray(L, dtype=float)
    n = L.shape[0]
    off = np.abs(L - np.diag(np.diag(L))).sum()
    if off < DEAD_MESH_EPS:
        D = np.full((n, n), np.inf)
        np.fill_diagonal(D, 0.0)
        return D, np.arange(n), True

    # np.asarray on a JAX array is READ-ONLY; fill_diagonal below would throw.
    D = np.array(reconstruct_metric_from_laplacian(jnp.asarray(L)), dtype=float, copy=True)
    lab = components(L, tol)
    if lab.max() > 0:
        D = np.where(lab[:, None] == lab[None, :], D, np.inf)
    np.fill_diagonal(D, 0.0)
    return D, lab, False


# ================================================================ graphs ====
def ring_laplacian(n, J=1.0):
    W = np.zeros((n, n))
    for i in range(n):
        W[i, (i + 1) % n] = W[(i + 1) % n, i] = float(J)
    return np.diag(W.sum(1)) - W


def laplacian_from_edges(n, edges):
    W = np.zeros((n, n))
    for i, j, w in edges:
        W[i, j] = W[j, i] = float(w)
    return np.diag(W.sum(1)) - W


# ================================================================== demo ====
def sweep(L_unit, pair, steps=15):
    i, j = pair
    Js = np.logspace(-1, 2, steps)
    ds = np.array([float(reconstruct_metric_from_laplacian(
        jnp.asarray(J * np.asarray(L_unit)))[i, j]) for J in Js])
    slope, _ = np.polyfit(np.log10(Js), np.log10(ds), 1)
    r2 = float(np.corrcoef(np.log10(Js), np.log10(ds))[0, 1] ** 2)
    return Js, ds, float(slope), r2


def main():
    print("=" * 70)
    print("  LMD — effective resistance as a metric on a dependency graph")
    print("=" * 70)
    print(f"  backend {jax.default_backend()}   devices {jax.devices()}")
    print(f"  float64 {jax.config.read('jax_enable_x64')}   dtype {jnp.zeros(1).dtype}")

    Js, ds, slope, r2 = sweep(ring_laplacian(100, 1.0), (0, 50))
    print("\n  coupling sweep, ring N=100, d(0,50)")
    for J, d in zip(Js, ds):
        print(f"    J = {J:9.4f}   d = {d:11.6f}")
    print(f"\n    slope {slope:.6f}    R² {r2:.6f}")

    print("\n  THE SAME SLOPE ON EVERY GRAPH — this is an identity, not a result.")
    others = [
        ("ring N=7 (odd)", ring_laplacian(7, 1.0), (0, 3)),
        ("path N=40", laplacian_from_edges(40, [(k, k + 1, 1.0) for k in range(39)]), (0, 39)),
        ("star N=50", laplacian_from_edges(50, [(0, k, 1.0) for k in range(1, 50)]), (1, 2)),
        ("complete N=12", laplacian_from_edges(
            12, [(i, j, 1.0) for i in range(12) for j in range(i + 1, 12)]), (0, 11)),
    ]
    for name, L0, pair in others:
        _, _, s, r = sweep(L0, pair, 8)
        print(f"    {name:<16} slope {s:.6f}   R² {r:.6f}")
    print("\n    pinv(J·L) = J⁻¹·pinv(L), so d ∝ J^(−1/2) always. In an interface")
    print("    that is a GUARANTEE: a global tension control is a zoom, and cannot")
    print("    reorder anything. It is also why measuring it verifies nothing about")
    print("    any particular graph. Reported as an invariant, never as a pass.")

    print("\n  THE TWO GUARDS")
    L = ring_laplacian(8, 1.0)
    for a, b in [(0, 1), (4, 5)]:
        L[a, b] = L[b, a] = 0.0
        L[a, a] -= 1.0
        L[b, b] -= 1.0
    raw = float(np.asarray(reconstruct_metric_from_laplacian(jnp.asarray(L)))[0, 2])
    D, lab, _ = mesh_metric(L)
    print(f"    cut ring, nodes 0 and 2 have NO path between them")
    print(f"      raw pinv     d = {raw:.6f}   finite, and meaningless")
    print(f"      guarded      d = {D[0, 2]}          components: {lab.max() + 1}")
    d0 = float(np.asarray(reconstruct_metric_from_laplacian(jnp.asarray(ring_laplacian(8, 0.0))))[0, 4])
    Dd, _, dead = mesh_metric(ring_laplacian(8, 0.0))
    print(f"    every wire cut (J = 0)")
    print(f"      raw pinv     d = {d0:.6f}          zero — maximum contraction")
    print(f"      guarded      d = {Dd[0, 4]}          dead = {dead}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
