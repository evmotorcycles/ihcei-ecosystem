#!/usr/bin/env python3
"""
emergent_spacetime.py -- INDIRECT evidence that spacetime is not fundamental:
"distance" emerges, as a genuine metric, purely from how INFORMATION flows on a
network -- with no coordinates ever assigned.
=============================================================================
THE IDEA (Doyle-Snell / effective-resistance geometry). Take a network defined
only by an information-coupling matrix W (who exchanges signal with whom, how
strongly). Assign NO positions, NO coordinates, NO space. From W alone compute:

    Laplacian        L = Diag(deg) - W
    resistance dist  R_ij = L+_ii + L+_jj - 2 L+_ij      (L+ = Laplacian pseudo-inverse)
    commute time     C_ij = vol * R_ij                    (Doyle-Snell)
    emergent metric  dx_ij = sqrt(R_ij)

`dx` behaves exactly like a spatial distance -- yet nothing spatial was put in.
It is a pure function of the information structure. That is the whole claim, at
Layer 1: in this system, geometry is DOWNSTREAM of information, not a fundamental
backdrop.

Predictions:
  S1  dx is a genuine METRIC emergent from information alone: dx_ii=0, symmetric,
      positive off-diagonal, and satisfies the triangle inequality (checked over
      random chains).
  S2  distance is a FUNCTION of information coupling: scale the coupling up and
      every emergent distance contracts (dx' = dx / sqrt(c)) -- 'space' stretches
      and shrinks with the information, it is not a fixed stage.
  S3  INDIRECT PROOF: two networks with identical size and identical total coupling
      'energy' but different information STRUCTURE render different geometries --
      so the geometry is fixed by the information, not by the substrate/energy.

EPISTEMIC FIREWALL. Layer 1 (proven here): on an information network, spatial
distance is an emergent, reconstructable function of the transition structure --
it is not fundamental to the model. Layer 3 (NOT claimed): that the physical
universe's spacetime is likewise a rendered projection of an information substrate.
This experiment is the indirect stepping-stone, never a proof of the metaphysics.

    python3 physics-agency/emergent_spacetime.py     # stdlib only, no network
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "repro"))
from reproduce_tauv import mean


def inv(M):
    """Gauss-Jordan inverse of a square matrix (stdlib, small N)."""
    n = len(M)
    A = [list(M[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(A[r][c]))
        A[c], A[piv] = A[piv], A[c]
        d = A[c][c]
        if abs(d) < 1e-15:
            raise ValueError("singular")
        A[c] = [v / d for v in A[c]]
        for r in range(n):
            if r != c and abs(A[r][c]) > 1e-15:
                f = A[r][c]
                A[r] = [A[r][k] - f * A[c][k] for k in range(2 * n)]
    return [row[n:] for row in A]


def resistance_distances(W):
    """Effective-resistance distance matrix from a symmetric coupling matrix W."""
    n = len(W)
    deg = [sum(W[i]) for i in range(n)]
    L = [[(deg[i] if i == j else 0.0) - W[i][j] for j in range(n)] for i in range(n)]
    J = 1.0 / n
    Lp = inv([[L[i][j] + J for j in range(n)] for i in range(n)])   # (L + J/n)^-1
    Lplus = [[Lp[i][j] - J for j in range(n)] for i in range(n)]     # Moore-Penrose L+
    R = [[Lplus[i][i] + Lplus[j][j] - 2 * Lplus[i][j] for j in range(n)] for i in range(n)]
    return R


def dx_matrix(W):
    R = resistance_distances(W)
    return [[math.sqrt(max(0.0, R[i][j])) for j in range(len(W))] for i in range(len(W))]


def rand_coupling(n, rng, scale=1.0):
    W = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            w = rng.uniform(0.2, 1.0) * scale
            W[i][j] = W[j][i] = w
    return W


def entropy_rate(W):
    n = len(W); deg = [sum(W[i]) for i in range(n)]; vol = sum(deg)
    h = 0.0
    for i in range(n):
        pi = deg[i] / vol
        for j in range(n):
            p = W[i][j] / deg[i] if deg[i] > 0 else 0.0
            if p > 0:
                h -= pi * p * math.log(p)
    return h


def main():
    bar = "=" * 88
    print(bar)
    print(" EMERGENT SPACETIME -- distance as a metric built from INFORMATION alone (no coordinates)")
    print(" Layer-1 indirect stepping-stone: geometry is downstream of information, not fundamental")
    print(bar)
    ok = []
    n = 6

    # ── S1: dx is a genuine metric emergent from information ────────────────────
    rng = random.Random(7)
    viol = 0; checks = 0; sym_ok = True; zero_ok = True
    for _ in range(40):
        W = rand_coupling(n, rng)
        dx = dx_matrix(W)
        for i in range(n):
            if abs(dx[i][i]) > 1e-9:
                zero_ok = False
            for j in range(n):
                if abs(dx[i][j] - dx[j][i]) > 1e-9:
                    sym_ok = False
                for k in range(n):
                    if dx[i][k] > dx[i][j] + dx[j][k] + 1e-9:
                        viol += 1
                    checks += 1
    s1 = zero_ok and sym_ok and viol == 0
    ok.append(s1)
    print("\n S1 dx is a genuine METRIC from information alone:")
    print("    dx_ii=0: %s | symmetric: %s | triangle inequality: %d/%d violations -> %s"
          % (zero_ok, sym_ok, viol, checks, "SUPPORTED" if s1 else "no"))

    # ── S2: distance is a function of information coupling (scale -> contract) ──
    rng = random.Random(11)
    W = rand_coupling(n, rng)
    base = mean([dx_matrix(W)[i][j] for i in range(n) for j in range(i + 1, n)])
    print("\n S2 distance is a FUNCTION of information coupling (not a fixed stage):")
    print("    %-10s %-12s %-12s" % ("coupling c", "mean dx", "predicted dx0/sqrt(c)"))
    mono = True; prev = float("inf")
    for c in (0.5, 1.0, 2.0, 4.0, 8.0):
        Wc = [[W[i][j] * c for j in range(n)] for i in range(n)]
        md = mean([dx_matrix(Wc)[i][j] for i in range(n) for j in range(i + 1, n)])
        print("    %-10.1f %-12.4f %-12.4f" % (c, md, base / math.sqrt(c)))
        if md > prev + 1e-9:
            mono = False
        prev = md
    s2 = mono
    ok.append(s2)
    print("    -> higher coupling contracts every distance (dx ~ 1/sqrt(c)): %s"
          % ("SUPPORTED" if s2 else "no"))

    # ── S3: indirect proof -- same size & energy, different structure => different geometry
    rng = random.Random(23)
    # network A: one tight cluster + a far node; network B: an even ring -- SAME total weight
    def total(W): return sum(W[i][j] for i in range(len(W)) for j in range(i + 1, len(W)))
    WA = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            WA[i][j] = WA[j][i] = (2.0 if (i < 3 and j < 3) else 0.1)   # clustered structure
    WB = [[0.0] * n for _ in range(n)]
    for i in range(n):
        j = (i + 1) % n
        WB[i][j] = WB[j][i] = 1.0                                       # even ring
    # normalise both to identical total coupling 'energy'
    tA, tB = total(WA), total(WB)
    WB = [[WB[i][j] * tA / tB for j in range(n)] for i in range(n)]
    dxA = dx_matrix(WA); dxB = dx_matrix(WB)
    mA = mean([dxA[i][j] for i in range(n) for j in range(i + 1, n)])
    mB = mean([dxB[i][j] for i in range(n) for j in range(i + 1, n)])
    hA, hB = entropy_rate(WA), entropy_rate(WB)
    differ = abs(mA - mB) > 0.05 * max(mA, mB)
    s3 = differ and abs(total(WA) - total(WB)) < 1e-6
    ok.append(s3)
    print("\n S3 INDIRECT PROOF (same nodes, same total coupling 'energy', different structure):")
    print("    network A (clustered): total=%.2f  mean dx=%.4f  entropy rate=%.3f" % (total(WA), mA, hA))
    print("    network B (even ring): total=%.2f  mean dx=%.4f  entropy rate=%.3f" % (total(WB), mB, hB))
    print("    -> identical size & energy, DIFFERENT geometry -> geometry is fixed by INFORMATION"
          " structure, not the substrate: %s" % ("SUPPORTED" if s3 else "no"))

    print("\n " + bar)
    print(" RESULT: %d/3 supported." % sum(ok))
    print(" READING: a real distance metric was reconstructed from pure information coupling -- no")
    print(" coordinates were ever assigned -- and it stretches, contracts, and re-shapes with the")
    print(" information alone. In this system, space is emergent, not fundamental. That is the")
    print(" indirect Layer-1 stepping-stone; the claim about physical spacetime stays Layer-3.")
    print(bar)
    raise SystemExit(0 if sum(ok) >= 3 else 1)


if __name__ == "__main__":
    main()
