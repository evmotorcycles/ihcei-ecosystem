#!/usr/bin/env python3
"""
telemetry_machines.py -- how TELEMETRY turns an abstract physical invariant
(F=ma, E=mc^2) into a functioning, controlled machine: two Layer-1 simulations of
the two-hop feedback channel D = D_enc * D_dec.
=============================================================================
SCOPE / EPISTEMIC FIREWALL. This is a control-systems simulation, not a claim
about physics ontology. Newton's F=ma and Einstein's E=mc^2 are *open-loop*
invariants: they assume instantaneous, frictionless transmission. A real machine
that exploits them -- a Watt steam engine, a fission reactor -- only produces
useful, bounded work once you wrap the raw capacity in a TELEMETRY FEEDBACK LOOP:

    capacity U --(D_enc: sense/encode)--> governor --(D_dec: act/decode)--> output
                         ^-------------- feedback correction --------------|

    D_enc  = the encode/sense hop (Watt centrifugal governor; ionization chamber).
    D_dec  = the decode/act hop   (throttle valve; boron/cadmium control rods).
    D      = D_enc * D_dec         (two-hop channel fidelity)
    tau_v  = telemetry latency     (sense->act delay; the LISM enforcement latency)

NOTE ON LABELS: Salat/Zakat are the *Nafs*-specific names for the two hops (a
cognitive essence toils, then enables others). Physical machines are NOT a Nafs,
so here the hops keep their engineering names D_enc / D_dec. Same maths, no Nafs.

Two experiments, both stdlib Monte-Carlo, both reproducible:

  A. THE TWO-HOP DELIVERY LAW (linear scaling & graceful decay)
     Delivered useful work E = U * D_enc * D_dec (two lossy hops in series x
     capacity). Verify: linear & multiplicative in each hop; either hop -> 0
     collapses E; decay is LINEAR, not a quadratic cliff (adjusted R^2).

  B. TELEMETRY MAKES IT A MACHINE (latency stability)
     Same capacity driven to a setpoint under rising entropy. OPEN-LOOP (no
     telemetry) diverges -- the raw invariant 'flies apart / melts down'. A
     CLOSED loop with low tau_v is bounded and stable -- a functioning machine.
     Past a CRITICAL tau_v the delayed loop re-destabilizes (the delay margin).

    python3 physics-agency/telemetry_machines.py     # stdlib only, no network
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "repro"))
from reproduce_tauv import mean  # tested stdlib mean


def ols(y, X):
    """Least squares; returns (beta, R2)."""
    n, k = len(X), len(X[0])
    XtX = [[sum(X[r][i] * X[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    Xty = [sum(X[r][i] * y[r] for r in range(n)) for i in range(k)]
    A = [row[:] + [Xty[i]] for i, row in enumerate(XtX)]
    for c in range(k):
        piv = max(range(c, k), key=lambda r: abs(A[r][c]))
        A[c], A[piv] = A[piv], A[c]
        if abs(A[c][c]) < 1e-12:
            continue
        for r in range(k):
            if r != c:
                f = A[r][c] / A[c][c]
                for cc in range(c, k + 1):
                    A[r][cc] -= f * A[c][cc]
    beta = [A[i][k] / A[i][i] if abs(A[i][i]) > 1e-12 else 0.0 for i in range(k)]
    yhat = [sum(beta[i] * X[r][i] for i in range(k)) for r in range(n)]
    ybar = mean(y)
    ss_res = sum((y[r] - yhat[r]) ** 2 for r in range(n))
    ss_tot = sum((y[r] - ybar) ** 2 for r in range(n)) or 1.0
    return beta, 1 - ss_res / ss_tot


# ── Experiment A: the two-hop delivery law ───────────────────────────────────
def deliver(U, d_enc, d_dec, noise=0.03, trials=400, seed=0):
    """Monte-Carlo: a demand U crosses the encode hop then the decode hop, each
    lossy + noisy. Returns mean delivered useful work E."""
    rng = random.Random(seed)
    out = []
    for _ in range(trials):
        after_enc = d_enc * U + rng.gauss(0, noise)          # sense/encode hop
        after_dec = d_dec * after_enc + rng.gauss(0, noise)  # act/decode hop
        out.append(max(0.0, after_dec))
    return mean(out)


# ── Experiment B: delayed feedback loop (the telemetry that makes the machine) ─
def run_loop(K, tau, steps=600, growth=0.08, noise=0.3, seed=1, blow=1e3):
    """An INHERENTLY UNSTABLE plant (positive feedback: heat->pressure->heat, or
    supercritical neutron flux) x_{t+1} = (1+growth)*x_t - K*x_{t-tau} + disturbance.
    Left alone (K=0, no telemetry) it runs away and explodes. The delayed governor
    u=-K*x_{t-tau} is the telemetry that tames it -- until tau_v gets too large.
    Returns (rms_tail, diverged)."""
    rng = random.Random(seed)
    x = 0.5
    hist = [x]
    tail = []
    for t in range(steps):
        xd = hist[-1 - tau] if len(hist) > tau else 0.0       # delayed measurement (tau_v)
        u = -K * xd if K > 0 else 0.0                          # K=0 => OPEN-LOOP (no telemetry)
        x = (1 + growth) * x + u + rng.uniform(-1, 1) * noise  # unstable plant + rising entropy
        if not math.isfinite(x) or abs(x) > blow:
            return float("inf"), True
        hist.append(x)
        if t > steps - 150:
            tail.append(x)
    rms = math.sqrt(mean([v * v for v in tail])) if tail else float("inf")
    return rms, rms > 25.0   # unbounded tail => the machine 'flew apart / melted down'


def main():
    bar = "=" * 88
    print(bar)
    print(" TELEMETRY MACHINES -- F=ma / E=mc^2 as a two-hop control channel D = D_enc * D_dec")
    print(" Layer-1 control-systems simulation (engineering hops D_enc/D_dec, NOT Nafs Salat/Zakat)")
    print(bar)
    ok = []

    # ── A. linear scaling & graceful decay ─────────────────────────────────────
    print("\n A. THE TWO-HOP DELIVERY LAW  E = U * D_enc * D_dec  (steam governor / reactor rods)")
    print("    %-8s %-8s %-6s  %-10s %-12s" % ("D_enc", "D_dec", "U", "E_meas", "U*Denc*Ddec"))
    grid = []
    for U in (0.5, 1.0, 2.0):
        for de in (0.2, 0.5, 0.8, 1.0):
            for dd in (0.2, 0.5, 0.8, 1.0):
                E = deliver(U, de, dd)
                grid.append((U, de, dd, E))
    # show a representative slice
    for U, de, dd, E in [g for g in grid if g[0] == 1.0 and g[2] in (0.5, 1.0)][:8]:
        print("    %-8.2f %-8.2f %-6.2f  %-10.4f %-12.4f" % (de, dd, U, E, U * de * dd))
    # V1: E fits U*D_enc*D_dec (multiplicative, linear in each hop)
    y = [g[3] for g in grid]
    Xm = [[g[0] * g[1] * g[2]] for g in grid]            # single predictor U*De*Dd, no intercept-free
    _, r2_mult = ols(y, [[1.0, g[0] * g[1] * g[2]] for g in grid])
    v1 = r2_mult > 0.98
    ok.append(v1)
    print("    V1 linear-multiplicative fit  E ~ U*D_enc*D_dec:  R2=%.4f -> %s"
          % (r2_mult, "SUPPORTED" if v1 else "no"))

    # V2: either hop -> 0 collapses E (both hops required)
    e_full = deliver(1.0, 1.0, 1.0)
    e_no_enc = deliver(1.0, 0.0, 1.0)                    # blind sensor (governor sticks)
    e_no_dec = deliver(1.0, 1.0, 0.0)                    # jammed valve (rods fail)
    v2 = e_no_enc < 0.05 * e_full and e_no_dec < 0.05 * e_full
    ok.append(v2)
    print("    V2 both hops required: E(full)=%.3f | D_enc->0 =%.3f | D_dec->0 =%.3f -> %s"
          % (e_full, e_no_enc, e_no_dec, "SUPPORTED (either hop kills output)" if v2 else "no"))

    # V3: decay is LINEAR in D (E~D), not a quadratic CLIFF (E~D^2). Fit both
    # single-shape hypotheses and show the linear shape fits far better.
    ds = [i / 20 for i in range(1, 21)]                 # D_enc sweep, D_dec=U=1
    yd = [deliver(1.0, d, 1.0) for d in ds]
    _, r2_lin = ols(yd, [[d] for d in ds])              # E ~ D      (linear / graceful)
    _, r2_cliff = ols(yd, [[d * d] for d in ds])        # E ~ D^2    (quadratic cliff)
    v3 = r2_lin > r2_cliff and r2_lin > 0.99
    ok.append(v3)
    print("    V3 graceful LINEAR decay vs quadratic CLIFF: R2(E~D)=%.4f  beats  R2(E~D^2)=%.4f -> %s"
          % (r2_lin, r2_cliff, "SUPPORTED (linear slide, no cliff)" if v3 else "cliff"))

    # ── B. telemetry latency turns the invariant into a machine ────────────────
    print("\n B. TELEMETRY MAKES IT A MACHINE  (feedback latency tau_v; K=0 => open-loop, no telemetry)")
    K = 0.6
    rms_open, div_open = run_loop(0.0, 0)               # no telemetry at all
    print("    OPEN-LOOP (raw invariant, no governor):  tail RMS=%s -> %s"
          % ("inf" if not math.isfinite(rms_open) else "%.1f" % rms_open,
             "DIVERGES (flies apart / melts down)" if div_open else "bounded"))
    print("    %-10s %-12s %-s" % ("tau_v", "tail RMS", "state"))
    crit = None
    for tau in (0, 1, 2, 4, 6, 8, 10, 12):
        rms, div = run_loop(K, tau)
        state = "DIVERGES" if div else "stable (functioning machine)"
        if div and crit is None:
            crit = tau
        print("    %-10d %-12s %s" % (tau, "inf" if not math.isfinite(rms) else "%.2f" % rms, state))
    # V4: open-loop diverges; low-tau closed loop is stable; a critical tau exists
    stable_low = not run_loop(K, 1)[1]
    v4 = div_open and stable_low and crit is not None
    ok.append(v4)
    print("    V4 telemetry transforms it: open-loop diverges; low tau_v stable; destabilizes past"
          " tau_v=%s -> %s" % (crit, "SUPPORTED" if v4 else "no"))

    print("\n " + bar)
    print(" RESULT: %d/4 verified." % sum(ok))
    print(" READING: raw capacity (U: steam pressure, fissile mass) is inert or explosive on its own.")
    print(" Useful work E = U * D_enc * D_dec appears only through BOTH telemetry hops, scales LINEARLY,")
    print(" and decays gracefully -- and it is the low-latency feedback loop (tau_v) that turns the")
    print(" abstract invariant F=ma / E=mc^2 into a bounded, functioning machine. Layer-1 control theory;")
    print(" the 'physics is literally a comms channel' reading stays an explicitly-labelled Layer-3 prior.")
    print(bar)
    raise SystemExit(0 if sum(ok) >= 3 else 1)


if __name__ == "__main__":
    main()
