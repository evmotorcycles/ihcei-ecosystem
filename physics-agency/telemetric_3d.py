#!/usr/bin/env python3
"""
telemetric_3d.py -- the Doyle-Snell coordinate-emergence visualization: a
coordinate-free network whose RENDERED 3D space contracts as we crank up the
information coupling, while the underlying topology (who is connected to whom)
never changes. Layer-1 illustration of the H3 discriminator.
=============================================================================
Method: build one fixed graph. For each coupling factor, weight every edge by it
(the 'container' / topology is unchanged), compute the Telemetric Metric distance
matrix d(i,j)=sqrt(kappa*R_ij) from the effective resistance R_ij, then embed that
distance matrix into 3D with MDS. The node LABELS are fixed; only the coupling
changes -- yet the rendered coordinates contract. That is emergent geometry.

Saves a 4-panel figure to physics-agency/figures/telemetric_3d_contraction.png.

    python3 physics-agency/telemetric_3d.py     # needs numpy, networkx, sklearn, matplotlib
"""
import os
import numpy as np
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
COUPLINGS = [0.5, 1.0, 2.0, 5.0]


def telemetric_distance_matrix(G, kappa=1.0):
    """d(i,j) = sqrt(kappa * R_ij), R_ij = effective resistance from L^+ (Doyle-Snell)."""
    nodes = list(G.nodes())
    n = len(nodes)
    L = nx.laplacian_matrix(G, nodelist=nodes).todense().astype(float)
    Lp = np.linalg.pinv(L)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            R = Lp[i, i] + Lp[j, j] - 2 * Lp[i, j]
            D[i, j] = np.sqrt(max(0.0, kappa * R))
    return D


def avg_distance(G, kappa=1.0):
    D = telemetric_distance_matrix(G, kappa)
    n = D.shape[0]
    return float(np.mean(D[np.triu_indices(n, k=1)]))


def base_graph(n=8, seed=42):
    return nx.connected_watts_strogatz_graph(n, 4, 0.5, seed=seed)


def coupling_sweep_averages(couplings=COUPLINGS, n=8, seed=42):
    """The H3 discriminator numerically: avg telemetric distance vs coupling (topology fixed)."""
    G0 = base_graph(n, seed)
    out = []
    for w in couplings:
        G = G0.copy()
        for u, v in G.edges():
            G[u][v]["weight"] = w
        out.append((w, avg_distance(G)))
    return out


def render():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.manifold import MDS

    G0 = base_graph(8, 42)
    fig = plt.figure(figsize=(15, 11))
    fig.suptitle("Latency–Metric Duality: emergent space contracts as coupling rises "
                 "(topology fixed)", fontsize=15, fontweight="bold", y=0.98)
    printed = []
    for idx, w in enumerate(COUPLINGS):
        G = G0.copy()
        for u, v in G.edges():
            G[u][v]["weight"] = w
        D = telemetric_distance_matrix(G)
        mds = MDS(n_components=3, dissimilarity="precomputed", random_state=42, normalized_stress="auto")
        coords = mds.fit_transform(D)
        ax = fig.add_subplot(2, 2, idx + 1, projection="3d")
        ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], s=140, c="#2bb3c0", edgecolors="black", zorder=3)
        for i, j in G.edges():
            ax.plot([coords[i, 0], coords[j, 0]], [coords[i, 1], coords[j, 1]],
                    [coords[i, 2], coords[j, 2]], color="gray", alpha=0.35, zorder=1)
        avg = float(np.mean(D[np.triu_indices(D.shape[0], k=1)]))
        printed.append((w, avg))
        ax.set_title(f"coupling = {w}   ·   avg telemetric distance = {avg:.3f}", fontsize=11, fontweight="bold")
        ax.set_xlabel("emergent X"); ax.set_ylabel("emergent Y"); ax.set_zlabel("emergent Z")
        m = float(np.max(np.abs(coords))) + 0.3
        ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_zlim(-m, m)
    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    outdir = os.path.join(HERE, "figures")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "telemetric_3d_contraction.png")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path, printed


def main():
    print("=" * 78)
    print(" DOYLE-SNELL 3D COORDINATE EMERGENCE -- rendered space vs information coupling")
    print("=" * 78)
    print("\n  H3 discriminator (topology fixed, coupling swept):")
    for w, avg in coupling_sweep_averages():
        print("    coupling %-4s -> avg telemetric distance %.4f" % (w, avg))
    path, _ = render()
    print("\n  Figure saved: %s" % os.path.relpath(path, os.path.dirname(HERE)))
    print("  Reading: node labels/topology never change; only coupling does -- yet the rendered")
    print("  coordinates contract. Distance is a function of correlation, not a fixed container.")
    print("  Layer-1 illustration; the physical-spacetime claim stays a proposed, unperformed test.")
    print("=" * 78)


if __name__ == "__main__":
    main()
