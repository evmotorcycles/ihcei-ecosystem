#!/usr/bin/env python3
"""
compare_theories.py -- what does LMD actually offer, next to the four "spacetime is
emergent" frameworks?  No hype. Honest verdicts, live computations.
================================================================================
The four frameworks people cite for "spacetime is doomed":
  (1) Holographic / AdS-CFT  (Ryu-Takayanagi, Van Raamsdonk): geometry ~ entanglement.
  (2) Quantum-information / emergent spacetime: distance ~ information / entropy.
  (3) Loop Quantum Gravity / spin networks: space is discrete at the Planck scale.
  (4) Amplituhedron / positive geometry: amplitudes without spacetime coordinates.

LMD is NOT a theory of quantum gravity and does not compete with these. It is a
Layer-1 TOY: operational distance = round-trip information latency = effective
resistance of a coupling graph. This script runs two live tests to show exactly
where LMD's behavior lines up with these ideas and -- just as honestly -- where it
offers nothing at all.

    python3 physics-agency/lmd/comparison/compare_theories.py     # stdlib, offline, $0

HARD DISCLAIMER: LMD was NOT "developed in collaboration with Google Quantum AI."
No such collaboration exists; a hardware test has only been *proposed*. Any claim
otherwise is false and must not be repeated.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "physics-agency"))
from emergent_spacetime import resistance_distances   # noqa: E402
import json                                             # noqa: E402

BAR = "=" * 82


# ---- Experiment A: Van Raamsdonk "entanglement sews space together" ---------- #
def _two_clusters(bridge_w, n=4):
    N = 2 * n
    W = [[0.0] * N for _ in range(N)]
    for i in range(n):
        for j in range(i + 1, n):
            W[i][j] = W[j][i] = 1.0            # dense region A
            W[n + i][n + j] = W[n + j][n + i] = 1.0  # dense region B
    W[0][n] = W[n][0] = bridge_w              # one bridge between the regions
    return W


def _multi_bridge(k, n=4, w=0.2):
    N = 2 * n
    W = [[0.0] * N for _ in range(N)]
    for i in range(n):
        for j in range(i + 1, n):
            W[i][j] = W[j][i] = 1.0
            W[n + i][n + j] = W[n + j][n + i] = 1.0
    for m in range(k):
        W[m][n + m] = W[n + m][m] = w
    return W


def experiment_A():
    print("\n [A] Van Raamsdonk / RT test: does weakening the 'entanglement' link pull the")
    print("     two regions apart (and does adding links pull them together)?")
    sweep = []
    for w in (2.0, 1.0, 0.5, 0.25, 0.1, 0.05, 0.01):
        d = math.sqrt(resistance_distances(_two_clusters(w))[0][4])
        sweep.append((w, d))
    for w, d in sweep:
        print("       bridge weight %-5.2f  ->  distance = %.4f" % (w, d))
    diverges = sweep[-1][1] > 5 * sweep[0][1]           # d blows up as w -> 0
    inv_sqrt = abs(sweep[-1][1] - 1.0 / math.sqrt(sweep[-1][0])) < 1e-6  # d ~ 1/sqrt(w)
    links = [(k, math.sqrt(resistance_distances(_multi_bridge(k))[0][4])) for k in (1, 2, 3, 4)]
    print("       adding parallel links (more 'entanglement'):",
          "  ".join("%d->%.2f" % (k, d) for k, d in links))
    shrinks = links[-1][1] < links[0][1]
    ok = diverges and shrinks
    print("     RESULT: regions pinch off as the link vanishes (d ~ 1/sqrt(w)) and merge as links"
          " are added -> %s" % ("MATCHES the entanglement->geometry picture" if ok else "no match"))
    return {"sweep": sweep, "diverges": diverges, "inverse_sqrt_law": inv_sqrt,
            "more_links_shrink_distance": shrinks, "pass": ok}


# ---- Experiment B: is the emergent distance a genuine geometry (a metric)? ---- #
def experiment_B():
    print("\n [B] Is it a real geometry? (a metric must obey the triangle inequality)")
    import random
    rng = random.Random(7)
    viol = checks = 0
    for _ in range(200):
        n = 6
        W = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                w = rng.random()
                W[i][j] = W[j][i] = w
        R = resistance_distances(W)
        d = [[math.sqrt(max(0.0, R[i][j])) for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if d[i][k] > d[i][j] + d[j][k] + 1e-9:
                        viol += 1
                    checks += 1
    print("       %d random networks, %d triangle checks -> %d violations" % (200, checks, viol))
    print("     RESULT: %s -- LMD distance IS a genuine metric (like a real geometry's), though a"
          % ("PASS" if viol == 0 else "FAIL"))
    print("     coarse-grained classical one, not a smooth spacetime with dynamics.")
    return {"networks": 200, "triangle_checks": checks, "violations": viol, "pass": viol == 0}


# ---- The honest scorecard ---------------------------------------------------- #
SCORECARD = [
    ("Holographic / AdS-CFT (RT, Van Raamsdonk)",
     "COMPARABLE (qualitatively)",
     "LMD reproduces the signature behavior live (Exp A): cut the link and regions recede to "
     "infinity; add links and they merge. But LMD uses classical effective resistance, not "
     "entanglement entropy -- no bulk/boundary dictionary, no gravity, no dynamics."),
    ("Quantum-information / emergent spacetime",
     "MOST ALIGNED (in spirit)",
     "LMD literally defines distance from information latency, a concrete instance of "
     "'distance = information cost'. But it is a coarse-grained toy, NOT a derivation of "
     "Einstein's equations from entropy (Jacobson / Van Raamsdonk)."),
    ("Loop Quantum Gravity / spin networks",
     "SILENT (offers nothing on its core claims)",
     "LMD lives on a discrete network, so it is compatible with a discrete substrate -- but it "
     "predicts NO area/volume quantization, NO Planck-scale discreteness, and NO Lorentz-violation "
     "signature (e.g. cosmic gamma-ray birefringence). It simply does not speak to LQG."),
    ("Amplituhedron / positive geometry",
     "NOT COMPARABLE (different problem)",
     "That program computes scattering amplitudes without spacetime coordinates. LMD is about "
     "distance from latency. They do not overlap; LMD offers nothing on amplitudes."),
]


def main():
    print(BAR)
    print(" WHAT DOES LMD ACTUALLY OFFER, NEXT TO THE FOUR 'EMERGENT SPACETIME' THEORIES?")
    print(" (no hype; LMD is a Layer-1 toy, not a theory of quantum gravity)")
    print(BAR)
    A = experiment_A()
    B = experiment_B()

    print("\n" + BAR)
    print(" HONEST SCORECARD")
    print(BAR)
    for name, verdict, note in SCORECARD:
        print("\n  * %s" % name)
        print("      verdict: %s" % verdict)
        words, line = note.split(), "      "
        for w in words:
            if len(line) + len(w) + 1 > 82:
                print(line); line = "      "
            line += w + " "
        print(line.rstrip())

    print("\n" + BAR)
    print(" BOTTOM LINE (honest): LMD is a cheap, computable, FALSIFIABLE toy in the")
    print(" quantum-information/holographic family. Its only real advantage over the four")
    print(" theories is testability at a benchtop -- most of them are out of experimental reach.")
    print(" It does NOT prove, replace, or compete with any of them, and the physical OTOC test")
    print(" is only PROPOSED. LMD was NOT developed with Google Quantum AI -- that claim is false.")
    print(BAR)

    out = {"experiment_A_van_raamsdonk": A, "experiment_B_metric": B,
           "scorecard": [{"theory": n, "verdict": v, "note": note} for n, v, note in SCORECARD],
           "disclaimer": "LMD is a Layer-1 toy; not quantum gravity; no Google collaboration; "
                         "hardware test only proposed.",
           "pass": A["pass"] and B["pass"]}
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_comparison.json"), "w"), indent=2)
    raise SystemExit(0 if out["pass"] else 1)


if __name__ == "__main__":
    main()
