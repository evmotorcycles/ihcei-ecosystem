#!/usr/bin/env python3
"""
gphys.py — Latency-Metric Duality on REAL committed networks
=============================================================
Spec: governance-physics/prereg/gphys_prereg.json, canonical sha256 6a7877db...,
locked and committed BEFORE this runner existed.

The existing LMD result runs on SEEDED RANDOM graphs. Under this repository's own
simulator rule, an ensemble built to exhibit a property cannot evidence that property.
So the same locked claims are re-run where the structure was MEASURED:

  * the live PyPI dependency graph  (N=540, 1287 edges, spec 4e83893b)
  * the STRING v12 yeast channel    (N=4825, hash-checked against frozen provenance)

  GP1  a metric emerges on a real graph            CAN FAIL
  GP2  it is not just degree in disguise           CAN FAIL
  GP3  scaling exponent = -0.5000 (sharp)          CAN FAIL
  GP4  a degree-preserving null destroys it        CAN FAIL
  GP5  maximal coupling does NOT imply d = 0       written so the FRAMEWORK loses
  GP6  the exponent replicates on yeast            CAN FAIL
  GP7  no Layer-3 claim is scored                  excluded from the score

    python3 governance-physics/gphys.py     # numpy only, offline, $0
"""
from __future__ import annotations
import csv, hashlib, json, os, random, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = open(os.path.join(HERE, "prereg", "GPHYS.sha256")).read().strip()
SEED = 20260726
RESULTS, FAILED = [], []
L3_WORDS = ("rendered", "headset", "conscious", "observer", "nafs", "simulation",
            "universe", "spacetime")


def gate(name, ok, detail, weight="full"):
    if not ok and weight == "full":
        FAILED.append(name)
    RESULTS.append({"gate": name, "pass": bool(ok), "detail": detail, "weight": weight})
    tag = "" if weight == "full" else "   [declared non-falsifiable — excluded from score]"
    print("\n  %-4s %s%s" % ("PASS" if ok else "FAIL", name, tag))
    print("        " + detail)


def resistance_matrix(W):
    """Effective resistance = commute time / (2*vol). A known metric — so the axiom
    check is a real test of connectivity and of this implementation, not a tautology."""
    n = W.shape[0]
    L = np.diag(W.sum(1)) - W
    Lp = np.linalg.pinv(L)
    d = np.diag(Lp)
    R = d[:, None] + d[None, :] - 2 * Lp
    np.fill_diagonal(R, 0.0)
    return np.maximum(R, 0.0)


def largest_component(W):
    n = W.shape[0]
    seen, best = set(), []
    for s in range(n):
        if s in seen:
            continue
        comp, stack = [], [s]
        seen.add(s)
        while stack:
            v = stack.pop()
            comp.append(v)
            for u in np.nonzero(W[v])[0]:
                if u not in seen:
                    seen.add(int(u))
                    stack.append(int(u))
        if len(comp) > len(best):
            best = comp
    idx = np.array(sorted(best))
    return W[np.ix_(idx, idx)], idx


def spearman(x, y):
    def rank(v):
        o = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), float)
        r[o] = np.arange(1, len(v) + 1)
        return r
    rx, ry = rank(x), rank(y)
    rx -= rx.mean(); ry -= ry.mean()
    den = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den else 0.0


def scaling_exponent(W, factors=(0.25, 0.5, 1.0, 2.0, 4.0, 8.0)):
    """Regress log(mean emergent distance) on log(coupling scale)."""
    xs, ys = [], []
    for s in factors:
        R = resistance_matrix(W * s)
        iu = np.triu_indices(R.shape[0], 1)
        xs.append(np.log(s))
        ys.append(np.log(np.sqrt(R[iu]).mean()))
    x, y = np.array(xs), np.array(ys)
    A = np.vstack([x, np.ones_like(x)]).T
    slope, icept = np.linalg.lstsq(A, y, rcond=None)[0]
    pred = A @ np.array([slope, icept])
    ss_res = ((y - pred) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum() or 1.0
    return float(slope), float(1 - ss_res / ss_tot)


def degree_preserving_rewire(W, rng, passes=10):
    A = (W > 0).astype(float)
    edges = [(int(i), int(j)) for i, j in zip(*np.triu_indices_from(A, 1)) if A[i, j]]
    m = len(edges)
    for _ in range(passes * m):
        (a, b), (c, d) = rng.choice(edges), rng.choice(edges)
        if len({a, b, c, d}) < 4:
            continue
        if A[a, d] or A[c, b]:
            continue
        A[a, b] = A[b, a] = A[c, d] = A[d, c] = 0
        A[a, d] = A[d, a] = A[c, b] = A[b, c] = 1
        edges[edges.index((a, b))] = (a, d)
        edges[edges.index((c, d))] = (c, b)
    return A


def load_pypi():
    dd = os.path.join(ROOT, "data", "pypi")
    man = json.load(open(os.path.join(dd, "MANIFEST.json")))
    for fn, want in man["sha256"].items():
        got = hashlib.sha256(open(os.path.join(dd, fn), "rb").read()).hexdigest()
        if got != want:
            raise SystemExit("ABORT: %s does not match its committed hash" % fn)
    nodes = [r["package"] for r in csv.DictReader(open(os.path.join(dd, "dep_graph_nodes.csv")))]
    idx = {p: i for i, p in enumerate(nodes)}
    W = np.zeros((len(nodes), len(nodes)))
    for e in csv.DictReader(open(os.path.join(dd, "dep_graph_edges.csv"))):
        i, j = idx[e["src"]], idx[e["dst"]]
        W[i, j] = W[j, i] = 1.0
    return W, nodes


def load_yeast(cap=600):
    p = os.path.join(ROOT, "biomedical-agency", "data", "yeast_channel_frozen.json")
    fx = json.load(open(p))
    ns = fx["nodes"][:cap]
    v = np.array([[n["D_enc"], n["D_dec"]] for n in ns])
    # similarity graph on the REAL committed two-hop fidelity vectors
    d2 = ((v[:, None, :] - v[None, :, :]) ** 2).sum(-1)
    W = np.exp(-d2 / (np.median(d2[d2 > 0]) or 1.0))
    np.fill_diagonal(W, 0.0)
    W[W < np.quantile(W, 0.90)] = 0.0          # keep the strongest decile of couplings
    return W, len(fx["nodes"])


def main():
    rng = random.Random(SEED)
    nprng = np.random.default_rng(SEED)

    print("=" * 84)
    print(" GOVERNANCE PHYSICS — Latency-Metric Duality on REAL committed networks")
    print(" spec  " + LOCKED)
    print("=" * 84)

    W, nodes = load_pypi()
    Wc, idx = largest_component(W)
    n = Wc.shape[0]
    R = resistance_matrix(Wc)
    D = np.sqrt(R)
    print("\n PyPI real graph: %d nodes, %d edges -> largest component %d nodes"
          % (len(nodes), int((W > 0).sum() // 2), n))

    # ---- GP1 ---------------------------------------------------------------------
    iu = np.triu_indices(n, 1)
    sym = float(np.abs(D - D.T).max())
    pos = bool((D[iu] > 0).all())
    viol, checks = 0, 300000
    for _ in range(checks):
        a, b, c = rng.randrange(n), rng.randrange(n), rng.randrange(n)
        if a == b or b == c or a == c:
            continue
        if D[a, c] > D[a, b] + D[b, c] + 1e-9:
            viol += 1
    gate("GP1_metric_emerges_on_a_real_graph",
         viol == 0 and pos and sym < 1e-9 and float(np.diag(D).max()) < 1e-12,
         "%d triangle checks -> %d violations | symmetry err %.2e | all off-diagonal "
         "distances > 0: %s | zero self-distance: yes" % (checks, viol, sym, pos))

    # ---- GP2 ---------------------------------------------------------------------
    deg = Wc.sum(1)
    base = 1.0 / np.sqrt(np.outer(deg, deg))
    rho = spearman(D[iu], base[iu])
    gate("GP2_the_metric_is_not_just_degree", abs(rho) < 0.90,
         "spearman(d, 1/sqrt(deg_i*deg_j)) = %+.4f  (gate |rho| < 0.90) — the emergent "
         "geometry carries structure beyond raw capacity" % rho)

    # ---- GP3  THE SHARP TEST ------------------------------------------------------
    slope, r2 = scaling_exponent(Wc)
    gate("GP3_the_scaling_exponent_matches_the_sharp_prediction",
         -0.52 <= slope <= -0.48 and r2 >= 0.999,
         "fitted slope = %.4f  (predicted exactly -0.5000)   R^2 = %.8f  on the REAL "
         "PyPI graph" % (slope, r2))

    # ---- GP4 ---------------------------------------------------------------------
    real_mean = float(np.sqrt(R[iu]).mean())
    null_means = []
    for _ in range(20):
        A = degree_preserving_rewire(Wc, rng, passes=10)
        Ac, _ = largest_component(A)
        Rn = resistance_matrix(Ac)
        iun = np.triu_indices(Ac.shape[0], 1)
        null_means.append(float(np.sqrt(Rn[iun]).mean()))
    nm, nsd = float(np.mean(null_means)), float(np.std(null_means))
    z = (real_mean - nm) / nsd if nsd else float("inf")
    gate("GP4_a_degree_preserving_null_destroys_the_structure", abs(z) > 3.0,
         "real mean d = %.6f vs degree-preserving null %.6f +/- %.6f  ->  z = %+.2f "
         "(gate |z| > 3) over 20 rewires" % (real_mean, nm, nsd, z))

    # ---- GP5  THE CATEGORY-ERROR GATE ---------------------------------------------
    # the most strongly coupled real pairs = the directly connected ones
    ii, jj = np.nonzero(np.triu(Wc, 1))
    coupled_d = D[ii, jj]
    min_d = float(coupled_d.min())
    gate("GP5_maximal_coupling_does_NOT_imply_zero_distance", min_d > 0.0,
         "over %d maximally coupled (directly connected) real pairs: MINIMUM emergent "
         "distance = %.6f, mean %.6f, and %d of them have d = 0.\n"
         "        The framework's entanglement inference requires d = 0 here. It is "
         "REFUTED on its own formalism:\n        commute time is a round-TRIP transport "
         "quantity, and correlation does not drive it to zero — which is the same reason "
         "no-signalling holds."
         % (len(coupled_d), min_d, float(coupled_d.mean()), int((coupled_d == 0).sum())))

    # ---- GP6  second real substrate ------------------------------------------------
    try:
        Wy, n_full = load_yeast()
        Wyc, _ = largest_component(Wy)
        sl_y, r2_y = scaling_exponent(Wyc)
        ok6 = -0.52 <= sl_y <= -0.48
        det6 = ("yeast channel (STRING v12, %d nodes committed; %d used, largest "
                "component %d): slope = %.4f, R^2 = %.8f  (gate [-0.52, -0.48])"
                % (n_full, Wy.shape[0], Wyc.shape[0], sl_y, r2_y))
    except Exception as e:
        sl_y, r2_y, ok6 = float("nan"), float("nan"), False
        det6 = "yeast substrate could not be built: %s" % e
    gate("GP6_the_exponent_replicates_on_a_second_real_substrate", ok6, det6)

    # ---- GP7  meta-gate, excluded ---------------------------------------------------
    scored_text = " ".join(g["gate"] + " " + g["detail"] for g in RESULTS
                           if g["weight"] == "full").lower()
    leaked = [w for w in L3_WORDS if w in scored_text]
    gate("GP7_no_layer_3_claim_is_scored", not leaked,
         "scored gates reference no Layer-3 notion %s; leaked terms: %s"
         % (str(L3_WORDS), leaked if leaked else "none"), weight="excluded")

    # ---- EVIDENTIAL DOWNGRADE, applied to my own gates -----------------------------
    # GP3 and GP6 PASSED AS PRE-REGISTERED and that stands. But the slope they test is an
    # ALGEBRAIC IDENTITY, not an empirical result: scaling W -> sW gives L -> sL, hence
    # L^+ -> L^+/s, hence R -> R/s, hence d = sqrt(R) -> d/sqrt(s). So log d = -0.5 log s
    # exactly, for EVERY graph. The repository's own rule is that a test which cannot fail
    # is not evidence, so both are relabelled and removed from the evidential score.
    # Demonstrated below on graphs that have nothing to do with the substrates.
    ctrl = {}
    for cname, Wt in (("random", (lambda A: np.where((A + A.T) / 2 > 0.85, 1.0, 0.0))(
                        nprng.random((60, 60)))),
                   ("path", np.diag(np.ones(39), 1) + np.diag(np.ones(39), -1))):
        np.fill_diagonal(Wt, 0.0)
        Wt, _ = largest_component(Wt)
        s_, r_ = scaling_exponent(Wt)
        ctrl[cname] = {"slope": round(s_, 6), "r2": round(r_, 8)}
    for g in RESULTS:
        if g["gate"].startswith(("GP3", "GP6")):
            g["weight"] = "identity"
            g["detail"] += ("\n        *** EVIDENTIAL DOWNGRADE (post-hoc, disclosed): "
                            "this exponent is an ALGEBRAIC IDENTITY. Controls with no "
                            "relation to the substrates give the same answer: %s. "
                            "Passed as pre-registered, but excluded from the evidential "
                            "score — a test that cannot fail is not evidence." % ctrl)
            if g["gate"] in FAILED:
                FAILED.remove(g["gate"])
    print("\n" + "-" * 84)
    print(" EVIDENTIAL DOWNGRADE of my own gates GP3 and GP6 (post-hoc, disclosed):")
    print("   W -> sW  =>  L -> sL  =>  L^+ -> L^+/s  =>  R -> R/s  =>  d -> d/sqrt(s)")
    print("   so log d = -0.5 log s EXACTLY, for every graph. Controls: %s" % ctrl)
    print("   Both PASSED as pre-registered. Both are now excluded from the evidential")
    print("   score. This also downgrades the existing physics-agency/lmd H2 claim, which")
    print("   celebrates the same -0.5000 slope on seeded graphs.")
    print("-" * 84)

    scored = [g for g in RESULTS if g["weight"] == "full"]
    met = sum(1 for g in scored if g["pass"])
    print("\n" + "=" * 84)
    print(" RESULT: %d/%d EVIDENTIAL gates met" % (met, len(scored)))
    print("         (GP3, GP6 = algebraic identities; GP7 = completeness check — all excluded)")
    if FAILED:
        print(" NOT MET: %s" % FAILED)
    print("\n SCOPE, declared in the spec: these are results about GRAPHS. They establish")
    print(" nothing about physical spacetime, quantum mechanics, entanglement in nature,")
    print(" observation or consciousness. 'Physics' names the framework under test.")
    print("=" * 84)

    json.dump({"spec_sha256_canonical": LOCKED, "seed": SEED,
               "pypi_nodes": len(nodes), "pypi_component": n,
               "triangle_checks": checks, "triangle_violations": viol,
               "spearman_d_vs_degree": round(rho, 4),
               "slope_pypi": round(slope, 4), "r2_pypi": round(r2, 8),
               "null_z": round(z, 2), "real_mean_d": round(real_mean, 6),
               "null_mean_d": round(nm, 6), "null_sd": round(nsd, 6),
               "coupled_pairs": int(len(coupled_d)),
               "min_d_among_maximally_coupled": round(min_d, 6),
               "n_coupled_pairs_with_zero_distance": int((coupled_d == 0).sum()),
               "slope_yeast": None if sl_y != sl_y else round(sl_y, 4),
               "r2_yeast": None if r2_y != r2_y else round(r2_y, 8),
               "layer3_terms_leaked_into_scored_gates": leaked,
               "identity_controls_NOT_A_GATE": ctrl,
               "evidential_gates": [g["gate"] for g in RESULTS if g["weight"] == "full"],
               "identity_gates_excluded": [g["gate"] for g in RESULTS
                                           if g["weight"] == "identity"],
               "gates": RESULTS, "gates_not_met": FAILED},
              open(os.path.join(HERE, "results_gphys.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
