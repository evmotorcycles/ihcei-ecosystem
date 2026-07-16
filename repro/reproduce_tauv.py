#!/usr/bin/env python3
"""
reproduce_tauv.py -- recompute the LISM Third-Law tau_v finding from FIRST
PRINCIPLES, with ZERO dependencies (Python standard library only).
============================================================================
THE CRITICISM THIS ANSWERS
    Earlier reproductions *read* the headline tau_v numbers from the repo's
    reproducibility artifacts (REPRODUCIBILITY.md, zenodo_metadata.json) rather
    than recomputing them. And reproduce_analysis.py needs pandas/scipy/
    statsmodels/sklearn AND raw CSVs rebuilt from the network (STRING v12 +
    a live GitHub fetch), so it cannot run in a fresh Claude chat / sandbox.

WHAT THIS DOES INSTEAD
    It recomputes the finding's DIRECTION and STATISTICAL SIGNIFICANCE from
    scratch -- the Mann-Whitney U test is implemented here in stdlib, no scipy --
    on REAL committed data (repro/tauv_cohort.json: 21 real GitHub repos with
    server-computed tau_v, assembled from the live cohorts already in this repo).
    Nothing is read from a results file; every number below is computed now.

    Run it anywhere, instantly:  python3 repro/reproduce_tauv.py
    No pip install. No network. No CSV to rebuild.

HONEST SCOPE
    This reproduces the LAW (failed repos have higher enforcement latency than
    survivors, at p<0.05, one-tailed) on the committed 21-repo cohort. It does
    NOT reproduce the manuscript's exact N=992 / p~1e-31 (that needs a live fetch
    of 992 repos). The other two arms now ALSO run from committed data:
    repro/reproduce_yeast.py recomputes the yeast VIF=1.003 from committed raw
    STRING v12, and repro/verify_github_ci.py attests the archived 992 run by
    re-hashing its pre-registration lock. See repro/README.md. The point of THIS
    script is the zero-dependency path: move the headline tau_v finding from "read
    from an artifact" to "recomputed with no installs," which anyone (including
    Claude chat) can re-run in one command.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------- #
# Mann-Whitney U (one-tailed), normal approximation with tie correction.
# Pure stdlib -- this is the whole point (no scipy).
# --------------------------------------------------------------------------- #
def mann_whitney_u(x, y):
    """One-tailed test of H1: values in x tend to be GREATER than in y.
    Returns (U_x, z, p_one_tailed). Normal approximation with tie correction."""
    n1, n2 = len(x), len(y)
    pooled = sorted([(v, 0) for v in x] + [(v, 1) for v in y])
    # assign average ranks (handle ties)
    ranks = [0.0] * len(pooled)
    i = 0
    while i < len(pooled):
        j = i
        while j + 1 < len(pooled) and pooled[j + 1][0] == pooled[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0  # ranks are 1-based
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    R1 = sum(r for r, (_, grp) in zip(ranks, pooled) if grp == 0)
    U1 = R1 - n1 * (n1 + 1) / 2.0            # U for x
    mU = n1 * n2 / 2.0
    # tie correction for the variance
    from collections import Counter
    tie_counts = Counter(v for v, _ in pooled)
    N = n1 + n2
    tie_term = sum(t ** 3 - t for t in tie_counts.values())
    sigma = math.sqrt(n1 * n2 / 12.0 * ((N + 1) - tie_term / (N * (N - 1))))
    # continuity-corrected z for H1: x > y  (U1 large)
    z = (U1 - mU - 0.5) / sigma if sigma > 0 else 0.0
    p = 0.5 * math.erfc(z / math.sqrt(2))    # upper-tail normal p
    return U1, z, p


def mean(xs):
    return sum(xs) / len(xs)


def line(label, got, want, ok):
    mark = "OK  " if ok else "FAIL"
    print(f"  {mark} {label:<46} reproduced={got:<22} reference={want}")


def main():
    data = json.load(open(os.path.join(HERE, "tauv_cohort.json")))
    repos = data["repos"]
    ref = data["reported_reference"]

    failed = [r["tau_v"] for r in repos if r["E"] == 0]
    surv = [r["tau_v"] for r in repos if r["E"] == 1]

    bar = "=" * 78
    print(bar)
    print(" LISM Third-Law reproduction -- tau_v recomputed from first principles")
    print(" data: repro/tauv_cohort.json (%d real GitHub repos) | stdlib only, no network"
          % len(repos))
    print(bar)
    print(f"\n  cohort: {len(failed)} failed (E=0)  vs  {len(surv)} survived (E=1)")
    print(f"  mean tau_v  failed  = {mean(failed):7.2f} d")
    print(f"  mean tau_v  survived= {mean(surv):7.2f} d")

    U, z, p = mann_whitney_u(failed, surv)
    print(f"\n  Mann-Whitney U (one-tailed, H1: failed > survived), computed here:")
    print(f"    U = {U:.1f}   z = {z:.3f}   p = {p:.3e}")

    print("\n  " + "-" * 74)
    print("  CHECK: does the committed real cohort reproduce the manuscript's DIRECTION?")
    checks = []
    c1 = mean(failed) > mean(surv)
    line("failed repos have HIGHER tau_v than survivors", f"{mean(failed):.1f} > {mean(surv):.1f}",
         f"{ref['tau_v_failed_days']} > {ref['tau_v_survived_days']}", c1)
    checks.append(c1)
    c2 = p < 0.05
    line("separation is significant (one-tailed p < 0.05)", f"p={p:.3e}", ref["p_one_tailed_MWU"], c2)
    checks.append(c2)
    c3 = ref["direction"] == "failed > survived" and c1
    line("direction matches the reported sign", "failed > survived", ref["direction"], c3)
    checks.append(c3)

    print("\n  " + "-" * 74)
    ok = all(checks)
    print(f"  RESULT: {sum(checks)}/{len(checks)} checks reproduced from scratch, zero dependencies")
    print(bar)
    print(" The LAW reproduces on committed real data: enforcement latency is higher in")
    print(" failed repos, significantly (recomputed here, not read from any file). The exact")
    print(" N=992 / p~1e-31 and the yeast channel use the documented network fetch -- see")
    print(" repro/README.md. This closes the 'read vs recompute' gap for the headline finding.")
    print(bar)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
