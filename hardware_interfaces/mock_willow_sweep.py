#!/usr/bin/env python3
"""
mock_willow_sweep.py -- an HONEST coupler-sweep template for a hardware team.
================================================================================
This is the "map your native coupler flux bias to this function in an afternoon"
interface. It does TWO things and is scrupulously clear about which is which:

  1. PREDICTION (real, runs here, offline): from a coupling-weight matrix it
     computes the LMD-predicted distance between two pinned probe sites using the
     repo's effective-resistance engine. Sweeping a global coupling factor yields
     the analytic  d ∝ coupling^(-1/2)  (log-log slope -0.5). This is Layer-1
     self-consistency -- algebraically expected, NOT a physical discovery.

  2. MEASUREMENT (a stub you fill in): `measure_scrambling_latency()` is where a
     hardware team plugs in the REAL round-trip latency from an OTOC / butterfly-
     front sequence on physical qubits. It raises NotImplementedError on purpose.
     We do NOT fabricate a measurement or hard-code tau_rt = 1/J and then "confirm"
     the slope -- that would be circular and prove nothing.

The physical experiment is the fork the prediction cannot settle:
    slope  -0.5   -> operational distance contracts with coupling  (emergent, LMD)
    slope   0.0   -> distance invariant to coupling                (fixed container)

    python3 hardware_interfaces/mock_willow_sweep.py    # runs the PREDICTION only

See physics-agency/lmd/GOOGLE_QUANTUM_AI_PITCH.md and RED_TEAM.md (decoherence
controls) for the full protocol.
"""
import math
import os
import sys

# reuse the validated engine -- identical code path, no reinvention
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "physics-agency"))
from telemetric_metric import telemetric_distance   # noqa: E402
from emergent_spacetime import rand_coupling          # noqa: E402
import random                                          # noqa: E402


# --------------------------------------------------------------------------- #
#  1. PREDICTION -- real, offline, algebraically exact                        #
# --------------------------------------------------------------------------- #
def predicted_distance(coupling_matrix, pair=(0, 1), kappa=1.0):
    """LMD-predicted distance d = sqrt(kappa * R_ij) between two pinned sites,
    where R_ij is the effective resistance (round-trip commute time) of the graph.
    `coupling_matrix[i][j]` is your tunable-coupler weight W_ij (>= 0, symmetric)."""
    i, j = pair
    return telemetric_distance(coupling_matrix, kappa)[i][j]


def predicted_sweep(coupling_matrix, pair=(0, 1), factors=(0.25, 0.5, 1, 2, 4, 8)):
    """Scale the whole coupling matrix by each factor (a global coupling-rate sweep)
    and return (factors, distances, slope, r2). Slope is analytically -0.5."""
    ds = []
    for c in factors:
        Wc = [[coupling_matrix[a][b] * c for b in range(len(coupling_matrix))]
              for a in range(len(coupling_matrix))]
        ds.append(predicted_distance(Wc, pair))
    lx = [math.log(c) for c in factors]
    ly = [math.log(d) for d in ds]
    n = len(lx); mx = sum(lx) / n; my = sum(ly) / n
    sxx = sum((v - mx) ** 2 for v in lx)
    sxy = sum((lx[k] - mx) * (ly[k] - my) for k in range(n))
    slope = sxy / sxx if sxx else 0.0
    yhat = [my + slope * (v - mx) for v in lx]
    ss_res = sum((ly[k] - yhat[k]) ** 2 for k in range(n))
    ss_tot = sum((v - my) ** 2 for v in ly) or 1.0
    return list(factors), ds, slope, 1 - ss_res / ss_tot


# --------------------------------------------------------------------------- #
#  2. MEASUREMENT -- the stub a hardware team fills in                        #
# --------------------------------------------------------------------------- #
def measure_scrambling_latency(qubit_a, qubit_b, coupler_bias_J, backend=None):
    """HARDWARE HOOK (not implemented on purpose).

    Return the measured round-trip information latency tau_rt between two PINNED
    qubits at tunable-coupler bias J, via an OTOC forward-reverse sequence or the
    butterfly-front arrival time. Then distance = sqrt(kappa * tau_rt).

    Fill this in with your native pulse sequence + error mitigation. Do NOT return
    a hard-coded 1/J -- the whole point is to measure whether the PHYSICS gives
    slope -0.5 (emergent) or 0 (fixed container). Pre-register the decoherence null
    control first (RED_TEAM.md, Objection 2): hold J fixed, vary a noise knob, and
    require the reconstructed distance to stay invariant.
    """
    raise NotImplementedError(
        "Plug in your OTOC / butterfly-front measurement here. This template "
        "deliberately does not fabricate tau_rt; see RED_TEAM.md for the controls."
    )


def _demo():
    bar = "=" * 78
    print(bar)
    print(" mock_willow_sweep — LMD PREDICTION (offline, algebraic). Measurement = your hook.")
    print(bar)
    W = rand_coupling(6, random.Random(20260720))
    factors, ds, slope, r2 = predicted_sweep(W, pair=(0, 5))
    print("\n predicted d(0,5) vs global coupling factor:")
    for c, d in zip(factors, ds):
        print("   J x %-5.2f  ->  d = %.4f" % (c, d))
    print("\n log-log slope = %.4f   R^2 = %.6f   (analytic target -0.5; expected, not a discovery)"
          % (slope, r2))
    print("\n PHYSICAL FORK (only hardware can settle it):")
    print("   measured slope ~ -0.5  ->  emergent metric (distance contracts with coupling)")
    print("   measured slope ~  0.0  ->  fixed background container")
    print(" Implement measure_scrambling_latency() with your OTOC sequence to run the real test.")
    try:
        measure_scrambling_latency(0, 5, 1.0)
    except NotImplementedError as e:
        print("\n measure_scrambling_latency(): NotImplementedError — %s" % str(e).split(".")[0])
    print(bar)


if __name__ == "__main__":
    _demo()
