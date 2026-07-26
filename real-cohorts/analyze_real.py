#!/usr/bin/env python3
"""
analyze_real.py — evaluate the locked gates on the REAL committed PyPI graph
============================================================================
Spec: real-cohorts/prereg/realsub_prereg.json, canonical sha256 4e83893b...,
locked and committed BEFORE the fetcher was written.

Gates, each with whether it can fail:
  KR0  graph is real, committed, N >= 250, depth >= 3          CAN FAIL
  KR1  fidelity-adjusted capacity beats raw capacity           CAN FAIL  (prior: NEGATIVE)
  KR2  the two hops are independent (VIF < 5) + control        CAN FAIL
  KR3  capacity does not confer fidelity (rho <= 0.50)         CAN FAIL
  SR1  fidelity decays with hop depth                          CAN FAIL
  SR2  linear U*D >= quadratic U*D^2                           CAN FAIL
  SR3  the failing region is populated (>= 30 below median)    CAN FAIL
  SR4  revocation reaches every real dependent                 CANNOT FAIL (traversal check)

    python3 real-cohorts/analyze_real.py     # stdlib only, offline, $0

Exit 0 means "reproduces as pre-registered, INCLUDING the gates that fail".
"""
from __future__ import annotations
import csv, hashlib, json, math, os, sys
from collections import defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "pypi")
LOCKED = open(os.path.join(HERE, "prereg", "REALSUB.sha256")).read().strip()
RESULTS, FAILED = [], []


def gate(name, ok, detail="", falsifiable=True):
    if not ok:
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail,
                    "falsifiable": falsifiable})
    mark = "" if falsifiable else "   [traversal check, not evidence]"
    print("  %-4s %s%s" % ("PASS" if ok else "FAIL", name, mark))
    if detail:
        print("        " + detail)


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = math.sqrt(sum((a - mx) ** 2 for a in x))
    dy = math.sqrt(sum((b - my) ** 2 for b in y))
    return num / (dx * dy) if dx and dy else 0.0


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def vif2(a, b):
    r = pearson(a, b)
    return 1.0 / (1.0 - r * r) if abs(r) < 0.999999 else float("inf")


def r2_on(y, x):
    """R^2 of a simple OLS fit of y on a single regressor x (with intercept)."""
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0:
        return 0.0
    beta = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
    alpha = my - beta * mx
    ss_res = sum((b - (alpha + beta * a)) ** 2 for a, b in zip(x, y))
    ss_tot = sum((b - my) ** 2 for b in y) or 1.0
    return 1.0 - ss_res / ss_tot


def median(v):
    v = sorted(v)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def main():
    man = json.load(open(os.path.join(DATA, "MANIFEST.json")))
    nodes = list(csv.DictReader(open(os.path.join(DATA, "dep_graph_nodes.csv"))))
    edges = list(csv.DictReader(open(os.path.join(DATA, "dep_graph_edges.csv"))))

    print("=" * 84)
    print(" REAL-DATA REPLACEMENT for the two SIMULATED cohorts")
    print(" spec   " + LOCKED)
    print(" data   data/pypi/dep_graph_{nodes,edges}.csv  (live PyPI, committed)")
    print("=" * 84)

    # the analysis is pinned to exactly the rows that were fetched
    for fn, want in man["sha256"].items():
        got = hashlib.sha256(open(os.path.join(DATA, fn), "rb").read()).hexdigest()
        if got != want:
            print("  ABORT: %s does not match its fetch-time hash" % fn)
            return 1
    if man["spec_sha256_canonical"] != LOCKED:
        print("  ABORT: manifest was produced under a different spec")
        return 1

    U = [float(n["U_versions"]) for n in nodes]
    Denc = [float(n["D_enc_release_hygiene"]) for n in nodes]
    Ddec = [float(n["D_dec_pin_clarity"]) for n in nodes]
    D = [a * b for a, b in zip(Denc, Ddec)]
    E = [float(n["E_indegree"]) for n in nodes]
    depth = [int(n["depth"]) for n in nodes]
    N = len(nodes)

    print("\n N=%d nodes | %d internal edges | max depth %d | seeds %d"
          % (N, len(edges), max(depth), len(man["seeds"])))
    print(" mean D_enc %.4f | mean D_dec %.4f | mean E %.2f | max E %d\n"
          % (sum(Denc) / N, sum(Ddec) / N, sum(E) / N, int(max(E))))

    # ---- KR0 ---------------------------------------------------------------------
    gate("KR0_data_is_real_and_committed", N >= 250 and max(depth) >= 3,
         "N=%d (floor 250), max depth=%d (floor 3), fetched %s"
         % (N, max(depth), man["fetched_utc"][:10]))

    # ---- KR1  CENTRAL CLAIM ------------------------------------------------------
    rho_status = spearman(U, E)
    rho_fid = spearman([u * d for u, d in zip(U, D)], E)
    gate("KR1_fidelity_beats_status", rho_fid > rho_status,
         "spearman(U, E) = %+.4f   vs   spearman(U*D_enc*D_dec, E) = %+.4f"
         % (rho_status, rho_fid))

    # ---- KR2 ---------------------------------------------------------------------
    v_real = vif2(Denc, Ddec)
    v_ctrl = vif2(Denc, Denc)
    gate("KR2_independence_gate", v_real < 5.0 and v_ctrl >= 5.0,
         "VIF(D_enc, D_dec) = %.4f (gate <5.0) | circular control VIF = %s (must be >=5)"
         % (v_real, "inf" if v_ctrl == float("inf") else "%.2f" % v_ctrl))

    # ---- KR3 ---------------------------------------------------------------------
    rho_UD = spearman(U, D)
    gate("KR3_capacity_does_not_confer_fidelity", rho_UD <= 0.50,
         "spearman(U, D) = %+.4f  (gate <= 0.50)" % rho_UD)

    # ---- SR1 ---------------------------------------------------------------------
    dmax = max(depth)
    shallow = [d for d, k in zip(D, depth) if k <= 1]
    deepest = [d for d, k in zip(D, depth) if k == dmax]
    m_sh = sum(shallow) / len(shallow)
    m_dp = sum(deepest) / len(deepest)
    prof = {k: round(sum(d for d, q in zip(D, depth) if q == k)
                     / max(1, sum(1 for q in depth if q == k)), 4)
            for k in range(dmax + 1)}
    gate("SR1_fidelity_decays_with_depth", m_dp < m_sh,
         "mean D depth<=1 = %.4f  ->  depth %d = %.4f  | profile %s"
         % (m_sh, dmax, m_dp, prof))

    # ---- SR2 ---------------------------------------------------------------------
    y = [math.log1p(e) for e in E]
    x_lin = [u * d for u, d in zip(U, D)]
    x_quad = [u * d * d for u, d in zip(U, D)]
    r2l, r2q = r2_on(y, x_lin), r2_on(y, x_quad)
    gate("SR2_linear_not_quadratic", r2l >= r2q,
         "R2 linear (U*D) = %.4f   vs   R2 quadratic (U*D^2) = %.4f   delta = %+.4f"
         % (r2l, r2q, r2l - r2q))

    # ---- SR3 ---------------------------------------------------------------------
    med = median(D)
    n_below = sum(1 for d in D if d < med)
    gate("SR3_populated_failing_region", n_below >= 30,
         "%d nodes below median D=%.4f  (floor 30)" % (n_below, med))

    # ---- SR4  traversal check, declared non-falsifiable ---------------------------
    dependents = defaultdict(list)     # dst -> packages that require it
    for e in edges:
        dependents[e["dst"]].append(e["src"])
    indeg = {n["package"]: int(n["E_indegree"]) for n in nodes}
    hub = max(indeg, key=lambda p: indeg[p])
    halted, q, hops = {hub}, deque([(hub, 0)]), 0
    while q:
        p, h = q.popleft()
        hops = max(hops, h)
        for dep in dependents.get(p, []):
            if dep not in halted:
                halted.add(dep)
                q.append((dep, h + 1))
    reachable = len(halted) - 1
    gate("SR4_tau_v_propagates_on_real_topology", True,
         "revoked '%s' (in-degree %d): %d real dependents halted in %d hops; unhalted=0"
         % (hub, indeg[hub], reachable, hops), falsifiable=False)

    print("\n" + "=" * 84)
    print(" RESULT: %d/%d gates met" % (len(RESULTS) - len(FAILED), len(RESULTS)))
    if FAILED:
        print(" NOT MET: %s" % FAILED)
    print("\n Both cohorts that the audit called SIMULATION now have a REAL, COMMITTED")
    print(" substitute. Whatever these gates say, they say it about a registry that was")
    print(" under no obligation to agree with the essay.")
    print(" This does NOT close the GitHub 992 gap, which stays open and declared.")
    print("=" * 84)

    json.dump({"spec_sha256_canonical": LOCKED, "N": N, "n_edges": len(edges),
               "max_depth": dmax, "attempts_disclosed": 3,
               "rho_status_E": round(rho_status, 4), "rho_fidelity_E": round(rho_fid, 4),
               "vif_denc_ddec": round(v_real, 4), "rho_U_D": round(rho_UD, 4),
               "depth_profile_meanD": prof,
               "r2_linear": round(r2l, 4), "r2_quadratic": round(r2q, 4),
               "n_below_median_D": n_below, "revocation_hub": hub,
               "revocation_dependents_halted": reachable, "revocation_hops": hops,
               "gates": RESULTS, "gates_not_met": FAILED},
              open(os.path.join(HERE, "results_real.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
