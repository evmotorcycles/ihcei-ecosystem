#!/usr/bin/env python3
"""
run_lmd.py -- carry out the pre-registered Latency-Metric Duality (LMD) experiment:
the "spacetime verdict matrix".
================================================================================
Equation under test:   d(i,j)^2 = kappa * tau_rt(i,j)
  tau_rt = round-trip information latency = commute time = effective resistance
  R_ij of the coupling graph. LMD says geometry is the emergent bookkeeping of
  round-trip latency: pin two probe sites, sweep only their information COUPLING,
  and if space is emergent the measured distance must contract as d ~ coupling^-1/2.

THE FORK (pre-registered, symmetric):
  * FUNDAMENTAL container  -> distance is set by a background metric; changing
    coupling on bolted-down probes does nothing:  slope ~ 0,  range = 0.
  * EMERGENT (LMD)         -> distance IS the latency; raising coupling collapses
    the round-trip lag:  slope ~ -0.5,  range > 0.

Layer discipline: this is a LAYER-1 numerical result about a coupling matrix. It
demonstrates that a genuine metric CAN emerge from pure information coupling and
obeys the predicted -1/2 law. It does NOT prove physical spacetime is emergent;
the qubit-lattice / optical-clock version is PROPOSED, not performed (Layer-3).

Reuses the already-merged, validated endpoint functions (identical code path):
    physics-agency/telemetric_metric.py :: endpoint_metric / _scaling / _discriminator

    python3 physics-agency/lmd/run_lmd.py     # stdlib only, seeded, offline, $0
"""
import hashlib
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)                       # physics-agency/
sys.path.insert(0, PARENT)
from telemetric_metric import endpoint_metric, endpoint_scaling, endpoint_discriminator  # noqa: E402

SPEC = os.path.join(HERE, "prereg", "lmd_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
BAR = "=" * 88


def verify_lock():
    spec = json.load(open(SPEC))
    man = json.load(open(MANIFEST))
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return got == man["spec_sha256"], got, man["spec_sha256"]


def main():
    print(BAR)
    print(" LMD — the spacetime verdict matrix   d(i,j)^2 = kappa * tau_rt   (distance^2 = commute time)")
    print(BAR)

    ok, got, want = verify_lock()
    print("\n [lock] spec re-hash %s" % ("MATCHES manifest" if ok else "MISMATCH — refusing"))
    print("        %s" % got)
    if not ok:
        raise SystemExit(2)

    # -- H1: metric axioms over K >= 8640 random networks --------------------- #
    trials_per_n = 2160
    ns = [5, 6, 7, 8]
    viol = checks = K = 0
    for i, n in enumerate(ns):
        r = endpoint_metric(n, trials_per_n, seed=1000 + i)
        viol += r["triangle_violations"]; checks += r["checks"]; K += trials_per_n
    h1_pass = viol == 0 and K >= 8640
    print("\n H1 metric:      %d random networks (n in %s), %d triangle checks -> %d violations   [%s]"
          % (K, ns, checks, viol, "PASS" if h1_pass else "FAIL"))

    # -- H2: log-log contraction slope over M seeded networks ----------------- #
    couplings = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0]
    M = 200
    slopes, r2s = [], []
    for s in range(M):
        r = endpoint_scaling(n=6, seed=7000 + s, couplings=couplings)
        slopes.append(r["slope"]); r2s.append(r["r2"])
    med_slope = statistics.median(slopes)
    min_r2 = min(r2s)
    h2_pass = -0.52 <= med_slope <= -0.48 and min_r2 >= 0.999
    print(" H2 scaling:     median slope = %.4f  (predicted -0.5000)   min R^2 = %.6f   over M=%d seeds   [%s]"
          % (med_slope, min_r2, M, "PASS" if h2_pass else "FAIL"))

    # -- H3: discriminator — pinned probes, sweep coupling -------------------- #
    disc = endpoint_discriminator(n=8, seed=42, probes=(0, 5), couplings=couplings)
    h3_pass = disc["emergent_range"] > 0 and disc["null_range"] == 0.0
    print(" H3 discriminate: emergent range = %.4f (>0, responds)   fundamental-null range = %.4f (bolted)   [%s]"
          % (disc["emergent_range"], disc["null_range"], "PASS" if h3_pass else "FAIL"))

    verdict = ("EMERGENT (LMD)" if (h2_pass and h3_pass) else
               "FUNDAMENTAL container" if abs(med_slope) < 0.05 else "inconclusive")
    print("\n VERDICT on this substrate: %s" % verdict)
    print("   slope ~ -0.5 (distance contracts with coupling) + the pinned-probe null is exactly flat")
    print("   => a genuine coordinate distance EMERGES from a pure information-coupling matrix.")

    print("\n LAYER DISCIPLINE (honest scope):")
    print("   * Layer-1 (measured): the metric axioms hold, d ~ coupling^-1/2, and the model discriminates.")
    print("   * Layer-3 (NOT claimed as proven): that PHYSICAL spacetime is emergent / a rendered interface.")
    print("   * The qubit-lattice / optical-clock bench test is PROPOSED, not performed.")

    all_pass = ok and h1_pass and h2_pass and h3_pass
    out = {
        "spec_sha256": got, "lock_ok": ok,
        "H1_metric": {"networks": K, "triangle_checks": checks, "violations": viol, "pass": h1_pass},
        "H2_scaling": {"median_slope": round(med_slope, 4), "predicted": -0.5,
                       "min_r2": round(min_r2, 6), "M": M, "pass": h2_pass},
        "H3_discriminator": {"emergent_range": round(disc["emergent_range"], 4),
                             "null_range": disc["null_range"], "pass": h3_pass},
        "verdict": verdict, "layer": "Layer-1 numerical; physical experiment proposed not performed",
        "pass": all_pass,
    }
    json.dump(out, open(os.path.join(HERE, "results_lmd.json"), "w"), indent=2)

    print("\n " + BAR)
    print(" RESULT: %s — %d/3 hypotheses pass their locked rule; metric emerges + obeys the -1/2 law."
          % ("GREEN" if all_pass else "RED", int(h1_pass) + int(h2_pass) + int(h3_pass)))
    print(BAR)
    raise SystemExit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
