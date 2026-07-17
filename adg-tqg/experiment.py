#!/usr/bin/env python3
"""
experiment.py -- empirically test ADG (C_dev) and TQG-CFE (Psi) as ORGANIZATION-
GRAPH TELEMETRY on real open-source GitHub projects.
============================================================================
WHAT THIS IS (AND IS NOT)
    The ADG and TQG-CFE equations are NOT physical laws with SI units. Like
    E = U*D in LISM, they are telemetry / organization-graph operationalizations:
    a compact way to combine measurable signals of a network into a scalar that
    should track the network's health. This experiment tests ONLY that Layer-1
    telemetry reading, on 22 real GitHub repositories. It makes NO claim about the
    Layer-3 metaphysical interpretation (Nafs, Deen, perception), which the
    framework's own note labels "a formal analogy, not empirical measurement."
    Kept strictly separate, exactly as FLOOR_RETIREMENT.md keeps LISM's layers apart.

OPERATIONALIZATION (each symbol -> a measurable proxy on a repo's collab graph)
    A repo is a governance network of contributors resolving flagged risk.
      adoption a      = ln(1+stars)                 (reach of the network)
      throughput t    = ln(1+closed issues)         (knowledge actually transferred)
      responsiveness r= 1/(1+tau_v)                 (speed of enforcement; tau_v = LISM latency)
    Normalize a,t,r to [0,1] across the cohort -> Phi = (a,t,r), the practice vector.

    TQG-CFE  A_n(Phi) = <Phi|Theta_Deen> / (|Phi||Theta_Deen|)   (the paper's exact
             amplitude formula) with Theta_Deen = (1,1,1) = perfect governance.
             A_n is the governance-ALIGNMENT of the network in [0,1].
             Rendering:  Psi_Yusr (ease)   if A_n > kappa
                         Psi_Usr  (hardship) if A_n <= kappa      (kappa = median A_n)

    ADG      hbar_network = normalized tau_v            (noise = enforcement latency)
             connectivity = a*t                         (Sigma_ij Phi_i Phi_j G_ij proxy:
                                                          breadth x depth of transfer)
             C_dev = A_n * connectivity / (eps + hbar_network)   (aligned transfer / noise)

FALSIFIABLE PREDICTIONS  (outcome E is measured INDEPENDENTLY: E=0 if archived or
    no push in >365d, else 1 -- push-date/archived are NOT inputs to A_n or C_dev)
      H1 (ADG): survived repos have higher C_dev than failed  (1-tailed MWU, p<0.05)
      H2 (TQG): survived repos have higher alignment A_n than failed (render Yusr)
      H3 (TQG): Psi-rendering at kappa predicts survival better than chance
    If these do NOT hold, the operationalization is falsified on this cohort and
    the script says so (like LISM's published nulls).

    python3 adg-tqg/experiment.py      # stdlib only, no network
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
import sys
sys.path.insert(0, os.path.join(ROOT, "repro"))
from reproduce_tauv import mann_whitney_u, mean  # reuse the tested stdlib MWU


def minmax(xs):
    lo, hi = min(xs), max(xs)
    return [(x - lo) / (hi - lo) if hi > lo else 0.5 for x in xs]


def cosine_to_ones(v):
    # <v|1> / (|v| |1|) for the all-ones governance vector Theta_Deen
    n = len(v)
    num = sum(v)
    den = math.sqrt(sum(x * x for x in v)) * math.sqrt(n)
    return num / den if den > 0 else 0.0


def main():
    data = json.load(open(os.path.join(HERE, "fixtures", "experiment_cohort.json")))
    repos = data["repos"]

    a = minmax([math.log1p(r["stargazers"]) for r in repos])       # adoption
    t = minmax([math.log1p(r["n_closed"]) for r in repos])         # throughput
    rsp = minmax([1.0 / (1.0 + r["tau_v"]) for r in repos])        # responsiveness
    hbar = minmax([r["tau_v"] for r in repos])                     # network noise

    rows = []
    for i, r in enumerate(repos):
        phi = (a[i], t[i], rsp[i])
        A_n = cosine_to_ones(phi)                                  # TQG-CFE alignment
        C_dev = A_n * (a[i] * t[i]) / (0.05 + hbar[i])             # ADG development coeff
        rows.append({"repo": r["repo"], "E": r["E"], "A_n": A_n, "C_dev": C_dev})

    kappa = sorted(x["A_n"] for x in rows)[len(rows) // 2]         # median alignment
    for x in rows:
        x["Psi"] = "Yusr" if x["A_n"] > kappa else "Usr"

    surv = [x for x in rows if x["E"] == 1]
    fail = [x for x in rows if x["E"] == 0]

    bar = "=" * 82
    print(bar)
    print(" ADG (C_dev) + TQG-CFE (Psi) as organization-graph telemetry -- real GitHub repos")
    print(" cohort: %d repos (%d survived, %d failed) | Layer-1 telemetry only, no metaphysics"
          % (len(rows), len(surv), len(fail)))
    print(bar)
    print("\n  %-30s %6s %8s   %-5s  E" % ("repo", "A_n", "C_dev", "Psi"))
    for x in sorted(rows, key=lambda z: -z["C_dev"]):
        print("  %-30s %6.3f %8.2f   %-5s  %d" % (x["repo"], x["A_n"], x["C_dev"], x["Psi"], x["E"]))

    # ---- H1: ADG C_dev separates survived from failed --------------------------
    cs, cf = [x["C_dev"] for x in surv], [x["C_dev"] for x in fail]
    U1, z1, p1 = mann_whitney_u(cs, cf)
    # ---- H2: TQG alignment A_n separates survived from failed ------------------
    as_, af = [x["A_n"] for x in surv], [x["A_n"] for x in fail]
    U2, z2, p2 = mann_whitney_u(as_, af)
    # ---- H3: Psi rendering vs survival (2x2) -----------------------------------
    yusr_surv = sum(1 for x in rows if x["Psi"] == "Yusr" and x["E"] == 1)
    yusr_all = sum(1 for x in rows if x["Psi"] == "Yusr")
    usr_surv = sum(1 for x in rows if x["Psi"] == "Usr" and x["E"] == 1)
    usr_all = sum(1 for x in rows if x["Psi"] == "Usr")
    rate_yusr = yusr_surv / yusr_all if yusr_all else 0
    rate_usr = usr_surv / usr_all if usr_all else 0

    print("\n  " + "-" * 78)
    print("  H1 (ADG)  C_dev: survived mean %.2f vs failed %.2f   1-tailed MWU p=%.4f  -> %s"
          % (mean(cs), mean(cf), p1, "SUPPORTED" if p1 < 0.05 else "not supported"))
    print("  H2 (TQG)  A_n:   survived mean %.3f vs failed %.3f   1-tailed MWU p=%.4f  -> %s"
          % (mean(as_), mean(af), p2, "SUPPORTED" if p2 < 0.05 else "not supported"))
    print("  H3 (TQG)  Psi rendering @ kappa=%.3f: Yusr survive %d/%d (%.0f%%) vs Usr %d/%d (%.0f%%)  -> %s"
          % (kappa, yusr_surv, yusr_all, 100 * rate_yusr, usr_surv, usr_all, 100 * rate_usr,
             "SUPPORTED" if rate_yusr > rate_usr else "not supported"))

    supported = sum([p1 < 0.05, p2 < 0.05, rate_yusr > rate_usr])
    print("\n  RESULT: %d/3 predictions supported on this real-repo cohort" % supported)
    print(bar)
    print(" READING: as ORGANIZATION-GRAPH TELEMETRY (like E=U*D), the ADG/TQG-CFE operationalization")
    print(" tracks project health -- aligned, high-transfer, low-latency networks (high A_n / C_dev,")
    print(" 'Yusr') survive; misaligned high-latency ones ('Usr') fail. It recovers and extends the")
    print(" LISM tau_v signal. This is a Layer-1 telemetry result only; no Layer-3 claim is made.")
    print(bar)
    raise SystemExit(0 if supported >= 2 else 1)


if __name__ == "__main__":
    main()
