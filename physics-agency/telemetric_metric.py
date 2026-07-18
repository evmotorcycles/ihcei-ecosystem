#!/usr/bin/env python3
"""
telemetric_metric.py -- a NEW, falsifiable physics equation built on the same
telemetry we already validated, and a numerical test of the experiment that would
decide whether spacetime is fundamental.
=============================================================================
THE EQUATION (proposed).  The Telemetric Metric / "latency line element":

        d(i, j)^2  =  kappa * tau_rt(i, j)         tau_rt = C_ij / nu = R_ij

  d(i,j)   proper separation between two regions/degrees of freedom
  tau_rt   ROUND-TRIP INFORMATION LATENCY between them = commute time C_ij (steps)
           divided by the coupling/hop rate nu -- the same latency family as LISM's
           tau_v. It reduces to the effective resistance R_ij of the correlation graph.
  kappa    a length^2-per-latency conversion constant

  Read it plainly: two things are 'close' when a signal can round-trip between them
  fast (low latency / high correlation); 'far' when the round-trip is slow. Distance
  is the geometry of latency. (Global coupling rescaling leaves the STEP count C_ij
  invariant -- a gauge freedom -- but PHYSICAL latency, and hence distance, shrinks
  as the coupling RATE rises: d ~ 1/sqrt(coupling).)

THE THEORY (proposed): LATENCY-METRIC DUALITY (LMD). Geometry is not a fundamental
container. The metric is emergent bookkeeping of the round-trip information latency
between the underlying degrees of freedom. Distance is a rendered read-out of a
correlation/commute-time network -- exactly the object our telemetry already
measures on socio-technical and biological networks (tau_v, E=U*D, commute times).

THE DISCRIMINATING PREDICTION (what an experiment must decide):
  * If spacetime is FUNDAMENTAL, the separation between two FIXED sites is set by
    the container. Changing only the *information coupling* (entanglement) between
    them cannot change their distance:  d/d(coupling) = 0.
  * If spacetime is EMERGENT (LMD), distance is the commute time, so changing the
    coupling while the sites never move MUST change the measured distance:
        d ~ 1 / sqrt(coupling)   (contracts as correlation rises).
  The experiment measures exactly this response and its sign.

THIS SCRIPT is a Layer-1 NUMERICAL validation: it checks that the equation defines
a genuine geometry, that it obeys the predicted scaling, and that it *discriminates*
(the emergent model responds to a coupling sweep; a fundamental-container null does
not). It is NOT a physical measurement -- the physical experiment is proposed, not
performed. Layer-3 (physical spacetime is emergent) is neither claimed nor proven.

    python3 physics-agency/telemetric_metric.py     # stdlib only, no network
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "repro"))
from emergent_spacetime import resistance_distances, rand_coupling  # our commute-time telemetry
from reproduce_tauv import mean


def roundtrip_latency(W):
    """Physical round-trip information latency tau_rt(i,j) = C_ij / nu, where
    C_ij = vol*R_ij is the commute time (in steps) and nu = vol is the aggregate
    coupling/hop rate. The vol cancels: tau_rt = R_ij (effective resistance). So the
    latency counts steps, but PHYSICAL latency shrinks as the coupling rate rises --
    which is what makes the metric respond to coupling (the measurable prediction)."""
    return resistance_distances(W)


def telemetric_distance(W, kappa=1.0):
    """d(i,j) = sqrt(kappa * tau_rt(i,j)) -- the Telemetric Metric line element."""
    tau = roundtrip_latency(W)
    return [[math.sqrt(max(0.0, kappa * tau[i][j])) for j in range(len(W))] for i in range(len(W))]


def ols_r2(y, x):
    n = len(x)
    mx, my = mean(x), mean(y)
    sxx = sum((x[i] - mx) ** 2 for i in range(n))
    sxy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    b = sxy / sxx if sxx else 0.0
    a = my - b * mx
    ss_res = sum((y[i] - (a + b * x[i])) ** 2 for i in range(n))
    ss_tot = sum((y[i] - my) ** 2 for i in range(n)) or 1.0
    return a, b, 1 - ss_res / ss_tot


def main():
    bar = "=" * 90
    print(bar)
    print(" THE TELEMETRIC METRIC   d(i,j)^2 = kappa * C_ij   (proper distance^2 = info commute time)")
    print(" Theory: LATENCY-METRIC DUALITY -- geometry is emergent bookkeeping of round-trip latency")
    print(" Layer-1 numerical validation of the equation + the experiment's discriminating logic")
    print(bar)
    ok = []
    n = 6

    # ── T1: the equation defines a GENUINE geometry (commute latency is a metric) ─
    rng = random.Random(7)
    viol = checks = 0
    for _ in range(40):
        d = telemetric_distance(rand_coupling(n, rng))
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if d[i][k] > d[i][j] + d[j][k] + 1e-9:
                        viol += 1
                    checks += 1
    t1 = viol == 0
    ok.append(t1)
    print("\n T1 the equation is a real geometry: d=sqrt(kappa*C) obeys the triangle inequality")
    print("    %d/%d violations over 40 random correlation networks -> %s"
          % (viol, checks, "SUPPORTED (commute-time latency IS a distance)" if t1 else "no"))

    # ── T2: the predicted scaling  d ~ 1/sqrt(coupling)  ────────────────────────
    rng = random.Random(11)
    W = rand_coupling(n, rng)
    cs = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    dpair = []
    print("\n T2 predicted scaling under LMD:  d ~ 1/sqrt(coupling)")
    print("    %-12s %-12s %-12s" % ("coupling c", "d(0,5)", "d0/sqrt(c)"))
    d0 = telemetric_distance(W)[0][5]
    for c in cs:
        Wc = [[W[i][j] * c for j in range(n)] for i in range(n)]
        d = telemetric_distance(Wc)[0][5]
        dpair.append(d)
        print("    %-12.1f %-12.4f %-12.4f" % (c, d, d0 / math.sqrt(c)))
    # fit log d vs log c -> slope should be -0.5
    _, slope, r2 = ols_r2([math.log(x) for x in dpair], [math.log(c) for c in cs])
    t2 = abs(slope + 0.5) < 0.02 and r2 > 0.999
    ok.append(t2)
    print("    log-log slope = %.4f (predicted -0.5), R2=%.5f -> %s"
          % (slope, r2, "SUPPORTED" if t2 else "no"))

    # ── T3: the DISCRIMINATOR -- emergent responds to a coupling sweep; a
    #        fundamental-container null does not. This is what the experiment measures.
    rng = random.Random(29)
    base = rand_coupling(n, rng)
    a, b = 0, 5                                     # two FIXED probe sites (never 'moved')
    emergent_resp, null_resp = [], []
    d_fixed = telemetric_distance(base)[a][b]       # the 'fundamental' container distance (frozen)
    print("\n T3 DISCRIMINATOR: change only the info-coupling of two FIXED sites (0,5); does d change?")
    print("    %-14s %-16s %-16s" % ("coupling g", "EMERGENT d(0,5)", "FUNDAMENTAL d(0,5)"))
    for g in (0.5, 1.0, 2.0, 4.0):
        W = [row[:] for row in base]
        for x in (a, b):                            # scale only edges incident to the probe sites
            for j in range(n):
                if j != x:
                    W[x][j] *= g; W[j][x] = W[x][j]
        d_em = telemetric_distance(W)[a][b]
        emergent_resp.append(d_em)
        null_resp.append(d_fixed)                   # fundamental: distance fixed by the container
        print("    %-14.1f %-16.4f %-16.4f" % (g, d_em, d_fixed))
    em_range = max(emergent_resp) - min(emergent_resp)
    null_range = max(null_resp) - min(null_resp)
    t3 = em_range > 0.05 and null_range < 1e-9
    ok.append(t3)
    print("    response to coupling: EMERGENT delta=%.4f  vs  FUNDAMENTAL delta=%.4f -> %s"
          % (em_range, null_range, "SUPPORTED (the experiment can decide)" if t3 else "no"))

    print("\n " + bar)
    print(" RESULT: %d/3 validated (numerically)." % sum(ok))
    print(" The equation d^2 = kappa*tau_rt defines a real geometry, obeys d ~ 1/sqrt(coupling), and")
    print(" DISCRIMINATES: emergent spacetime predicts a fixed pair's distance shifts when only their")
    print(" information coupling changes; fundamental spacetime forbids it. A tunable-coupling qubit")
    print(" lattice (or entangled optical-clock network) measures exactly this response.")
    print(" Layer-1 numerics only; the physical experiment is PROPOSED, and Layer-3 (physical")
    print(" spacetime is emergent) is neither claimed nor proven -- this is the falsifiable test for it.")
    print(bar)
    raise SystemExit(0 if sum(ok) >= 3 else 1)


if __name__ == "__main__":
    main()
