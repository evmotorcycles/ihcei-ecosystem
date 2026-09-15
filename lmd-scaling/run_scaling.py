#!/usr/bin/env python3
"""What does the -0.5 coupling slope measure?

Reproduces a GPU coupling sweep over a weighted ring Laplacian, then asks the
question the sweep does not: is -0.5 a reading of the graph, or a consequence of
multiplying every edge by one scalar?

Runs offline, on CPU, in float64. No GPU, no network, no keys.

Predictions are locked in prereg_scaling.md,
sha256 c4714e7827ddb942749c90d323a00d729fd3bb4a6d9596ab50a1f435745029be
"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

COUPLINGS = np.logspace(-1, 2, num=15)
N = 100
PAIR = (0, 50)


# ---------------------------------------------------------------- engine ----
def laplacian(n, edges):
    """edges: (i, j, weight). Undirected, no self-loops."""
    L = np.zeros((n, n), dtype=np.float64)
    for i, j, w in edges:
        L[i, i] += w
        L[j, j] += w
        L[i, j] -= w
        L[j, i] -= w
    return L


def metric(L):
    """d_ij = sqrt(R_ij), R_ij = L+_ii + L+_jj - 2 L+_ij."""
    P = np.linalg.pinv(L)
    diag = np.diag(P)
    R = diag[:, None] + diag[None, :] - 2.0 * P
    return np.sqrt(np.clip(R, 0.0, None))


def fit_loglog(x, y):
    lx, ly = np.log10(np.asarray(x, dtype=np.float64)), np.log10(np.asarray(y, dtype=np.float64))
    slope, intercept = np.polyfit(lx, ly, 1)
    r2 = float(np.corrcoef(lx, ly)[0, 1] ** 2)
    return float(slope), float(intercept), r2


# ---------------------------------------------------------------- graphs ----
def ring(n):
    return [(i, (i + 1) % n, 1.0) for i in range(n)]


def star(n):
    return [(0, i, 1.0) for i in range(1, n)]


def path(n):
    return [(i, i + 1, 1.0) for i in range(n - 1)]


def complete(n):
    return [(i, j, 1.0) for i in range(n) for j in range(i + 1, n)]


def erdos_renyi(n, p, seed):
    rng = np.random.default_rng(seed)
    return [(i, j, 1.0) for i in range(n) for j in range(i + 1, n) if rng.random() < p]


def two_rings(n):
    """Two disjoint rings of n/2. Nodes 0 and n/2 have NO path between them."""
    h = n // 2
    return ([(i, (i + 1) % h, 1.0) for i in range(h)]
            + [(h + i, h + (i + 1) % h, 1.0) for i in range(h)])


def components(n, edges):
    seen, count = set(), 0
    adj = {i: [] for i in range(n)}
    for i, j, _ in edges:
        adj[i].append(j)
        adj[j].append(i)
    for s in range(n):
        if s in seen:
            continue
        count += 1
        stack = [s]
        seen.add(s)
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
    return count


# -------------------------------------------------------- arm 1: global J ----
def sweep_global(edges, pair=PAIR):
    """Every edge multiplied by J. The notebook's arrangement."""
    out = []
    for J in COUPLINGS:
        D = metric(laplacian(N, [(i, j, w * J) for i, j, w in edges]))
        out.append(float(D[pair[0], pair[1]]))
    return out


def arm1():
    graphs = {
        "ring": ring(N),
        "star": star(N),
        "path": path(N),
        "complete": complete(N),
        "erdos_renyi_p0.1_seed0": erdos_renyi(N, 0.1, 0),
    }
    rows = {}
    for name, edges in graphs.items():
        pieces = components(N, edges)
        d = sweep_global(edges)
        slope, _, r2 = fit_loglog(COUPLINGS, d)
        # S4: does one coupling determine all fifteen?
        d1 = sweep_global(edges)[0] * math.sqrt(COUPLINGS[0])   # d at J=1, implied
        predicted = [d1 / math.sqrt(J) for J in COUPLINGS]
        dev = max(abs(a - b) / b for a, b in zip(d, predicted))
        rows[name] = {
            "edges": len(edges), "pieces": pieces,
            "slope": slope, "r2": r2,
            "abs_slope_err": abs(slope + 0.5),
            "one_minus_r2": abs(1.0 - r2),
            "max_rel_dev_from_one_point": dev,
            "d_at_first_J": d[0], "d_at_last_J": d[-1],
        }
    return rows


# --------------------------------------------------- arm 2: one edge only ----
def arm2():
    """Ring at weight 1 everywhere EXCEPT edge (0,1), which is swept."""
    base = ring(N)
    d = []
    for J in COUPLINGS:
        edges = [(i, j, J if (i, j) == (0, 1) else w) for i, j, w in base]
        d.append(float(metric(laplacian(N, edges))[PAIR[0], PAIR[1]]))
    slope, _, r2 = fit_loglog(COUPLINGS, d)
    return {
        "slope": slope, "r2": r2,
        "abs_slope_err": abs(slope + 0.5),
        "abs_slope": abs(slope),
        "d_at_first_J": d[0], "d_at_last_J": d[-1],
        "d": d,
    }


# ------------------------------------------- arm 3: no path between them ----
def arm3():
    edges = two_rings(N)
    pieces = components(N, edges)
    d = sweep_global(edges)
    slope, _, r2 = fit_loglog(COUPLINGS, d)
    # what the same pair reads inside one component, for contrast
    same_piece = [float(metric(laplacian(N, [(i, j, w * J) for i, j, w in edges]))[0, 25])
                  for J in COUPLINGS]
    return {
        "pieces": pieces,
        "all_finite": bool(all(math.isfinite(v) for v in d)),
        "slope": slope, "r2": r2,
        "abs_slope_err": abs(slope + 0.5),
        "d_across_components_at_J1": d[0] / math.sqrt(1.0 / COUPLINGS[0]) if False else d[0],
        "d_across_components": d,
        "d_within_component": same_piece,
    }


# ------------------------------------------------------- arm 4: precision ----
def closed_form_ring(n, k, J):
    """R(0,k) on an unweighted ring is k(n-k)/n. Every weight J divides it."""
    return math.sqrt((k * (n - k) / n) / J)


def arm4():
    exact = [closed_form_ring(N, PAIR[1], J) for J in COUPLINGS]
    f64 = sweep_global(ring(N))
    dev64 = max(abs(a - b) / b for a, b in zip(f64, exact))

    result = {
        "exact_at_first_J": exact[0],
        "float64": f64,
        "max_rel_dev_float64": dev64,
        "published_at_first_J": 15.811394,
        "published_rel_dev": abs(15.811394 - exact[0]) / exact[0],
    }

    try:
        import jax
        import jax.numpy as jnp
    except ImportError:
        result["float32"] = "jax not installed"
        return result

    def metric32(L):
        P = jnp.linalg.pinv(L)
        diag = jnp.diag(P)
        R = diag[:, None] + diag[None, :] - 2.0 * P
        return jnp.sqrt(jnp.clip(R, 0.0, None))

    f32 = []
    for J in COUPLINGS:
        L = jnp.asarray(laplacian(N, [(i, j, w * J) for i, j, w in ring(N)]), dtype=jnp.float32)
        f32.append(float(metric32(L)[PAIR[0], PAIR[1]]))
    dev32 = max(abs(a - b) / b for a, b in zip(f32, exact))
    slope32, _, r232 = fit_loglog(COUPLINGS, f32)
    result.update({
        "jax_backend": jax.default_backend(),
        "float32": f32,
        "max_rel_dev_float32": dev32,
        "float32_at_first_J": f32[0],
        "float32_slope": slope32,
        "float32_abs_slope_err": abs(slope32 + 0.5),
        "float32_passes_notebook_gate_atol_1e_4": bool(abs(slope32 + 0.5) < 1e-4),
    })
    return result


# ------------------------------------- arm 5: the repo's own scale rule ----
def arm5():
    """The engine already states the other half: bearings do not move.

    Measured with spar, not hand-written.
    """
    from spar.spar import INVOICE, bearings, scaled
    # a NAMED link, not links[0] -- the rows are sorted by bearing and ties
    # reorder, so position 0 is not the same link at every factor.
    WATCH = ("Subtotal", "VAT")
    out = {}
    for factor in (0.1, 1.0, 10.0, 1000.0):
        b = bearings(scaled(INVOICE, factor))
        row = next(r for r in b["links"] if (r["from"], r["to"]) == WATCH)
        out[str(factor)] = {
            "total": b["total"],
            "expected_total": b["expected_total"],
            "conserved": b["conserved"],
            "watched_link": " -> ".join(WATCH),
            "watched_bearing": row["bearing"],
            "watched_resistance": row["resistance"],
            "watched_weight": row["weight"],
        }
    return out


# ------------------------------------------------ arm 6: AFTER THE FACT ----
def rank_aware_metric(L, pieces):
    """Drop exactly `pieces` null modes, instead of guessing by rcond.

    np.linalg.pinv decides how many singular values are zero by comparing them
    to rcond * largest. On a dense graph the true null eigenvalue drifts across
    that line as the weights scale, so the same graph is inverted with a
    different rank at different J. The rank is not in doubt: it is n - pieces.
    """
    vals, vecs = np.linalg.eigh(L)
    order = np.argsort(vals)
    keep = order[pieces:]
    P = (vecs[:, keep] / vals[keep]) @ vecs[:, keep].T
    diag = np.diag(P)
    R = diag[:, None] + diag[None, :] - 2.0 * P
    return np.sqrt(np.clip(R, 0.0, None))


def arm6():
    """MEASURED AFTER THE RESULT. No prediction was registered for any of this.

    S2/S3/S4 missed on the complete graph. This asks why, and what the repo's
    own engine does with the same input. It is diagnosis, not a re-run of a
    prediction, and nothing here is scored HIT or MISS.
    """
    graphs = {"ring": ring(N), "star": star(N), "path": path(N),
              "complete": complete(N), "erdos_renyi_p0.1_seed0": erdos_renyi(N, 0.1, 0)}

    # (a) does fixing the rank restore the identity?
    fixed = {}
    for name, edges in graphs.items():
        pieces = components(N, edges)
        d = []
        for J in COUPLINGS:
            L = laplacian(N, [(i, j, w * J) for i, j, w in edges])
            d.append(float(rank_aware_metric(L, pieces)[PAIR[0], PAIR[1]]))
        slope, _, r2 = fit_loglog(COUPLINGS, d)
        fixed[name] = {"slope": slope, "abs_slope_err": abs(slope + 0.5),
                       "one_minus_r2": abs(1.0 - r2)}

    # (b) where the default cutoff sits relative to the true null eigenvalue
    drift = []
    for J in COUPLINGS:
        L = laplacian(N, [(i, j, w * J) for i, j, w in complete(N)])
        ev = np.linalg.eigvalsh(L)
        null_eig = float(abs(ev[0]))
        cutoff = float(1e-15 * abs(ev).max())
        drift.append({"J": float(J), "null_eigenvalue": null_eig,
                      "rcond_cutoff": cutoff, "leaks": bool(null_eig > cutoff)})

    # (c) what THIS REPO's shipped engine does with the same two inputs
    from smi.lmd import mesh_metric
    repo = {}
    per_J = []
    for J in COUPLINGS:
        L_c = laplacian(N, [(i, j, w * J) for i, j, w in complete(N)])
        D, _, _ = mesh_metric(L_c)
        got, exact = float(D[PAIR[0], PAIR[1]]), math.sqrt((2.0 / N) / J)
        per_J.append({"J": float(J), "engine": got, "exact": exact,
                      "rel_dev": abs(got - exact) / exact})
    worst = max(per_J, key=lambda r: r["rel_dev"])
    repo["complete_swept"] = {
        "worst_rel_dev": worst["rel_dev"], "worst_J": worst["J"],
        "worst_engine": worst["engine"], "worst_exact": worst["exact"],
        "per_coupling": per_J,
    }
    L_split = laplacian(N, two_rings(N))
    D2, lab, _ = mesh_metric(L_split)
    bare = float(metric(L_split)[PAIR[0], PAIR[1]])
    repo["disconnected_pair"] = {
        "engine": float(D2[PAIR[0], PAIR[1]]),
        "engine_is_inf": bool(math.isinf(float(D2[PAIR[0], PAIR[1]]))),
        "bare_pinv": bare,
        "pieces_seen_by_engine": int(lab.max()) + 1,
    }
    # (d) the verdict flips with the LIBRARY, at identical dtype and input.
    # numpy's default rcond is 1e-15; jax's is max(M,N)*eps, far looser, so it
    # truncates the null mode that numpy keeps. Same maths, same float64,
    # opposite answer to the notebook's own atol=1e-4 gate.
    import jax.numpy as jnp
    from smi.lmd import laplacian_from_edges

    inverters = {
        "numpy": lambda L: np.linalg.pinv(L),
        "jax": lambda L: np.asarray(jnp.linalg.pinv(jnp.asarray(L))),
    }
    # two ways to assemble the SAME Laplacian. Accumulating w into the diagonal
    # edge by edge sums 99 terms in sequence; summing a weight matrix once does
    # not. The matrices differ only in rounding.
    builders = {
        "accumulate": lambda es: laplacian(N, es),
        "sum_weight_matrix": lambda es: np.asarray(laplacian_from_edges(N, es)),
    }

    flip = {}
    for bname, build in builders.items():
        for lname, inv in inverters.items():
            d = []
            for J in COUPLINGS:
                P = inv(build([(i, j, w * J) for i, j, w in complete(N)]))
                dg = np.diag(P)
                Rm = dg[:, None] + dg[None, :] - 2.0 * P
                d.append(float(math.sqrt(max(Rm[PAIR[0], PAIR[1]], 0.0))))
            slope, _, _ = fit_loglog(COUPLINGS, d)
            flip[f"{bname}+{lname}"] = {
                "assembly": bname, "inverter": lname,
                "slope": slope, "abs_slope_err": abs(slope + 0.5),
                "notebook_verdict": ("PASS" if abs(slope + 0.5) < 1e-4 else "FAIL"),
            }

    return {"rank_aware": fixed, "cutoff_drift": drift, "repo_engine": repo,
            "library_flip_on_K100": flip}


def main():
    results = {
        "prereg_sha256": "c4714e7827ddb942749c90d323a00d729fd3bb4a6d9596ab50a1f435745029be",
        "couplings": [float(c) for c in COUPLINGS],
        "n": N, "pair": list(PAIR),
        "arm1_global_scalar": arm1(),
        "arm2_single_edge": arm2(),
        "arm3_disconnected": arm3(),
        "arm4_precision": arm4(),
        "arm5_repo_scale_rule": arm5(),
        "arm6_post_hoc_no_prediction": arm6(),
    }

    a1 = results["arm1_global_scalar"]
    print("=== ARM 1 -- every edge multiplied by J ===")
    print(f"{'graph':<26} {'edges':>7} {'slope':>12} {'|slope+0.5|':>13} {'1-R2':>10}")
    for name, r in a1.items():
        print(f"{name:<26} {r['edges']:>7} {r['slope']:>12.9f} "
              f"{r['abs_slope_err']:>13.2e} {r['one_minus_r2']:>10.2e}")
    print(f"\nS1 ring          |slope+0.5| = {a1['ring']['abs_slope_err']:.2e}  -> "
          f"{'HIT' if a1['ring']['abs_slope_err'] < 1e-9 else 'MISS'}")
    worst = max(r["abs_slope_err"] for r in a1.values())
    print(f"S2 all five      worst        = {worst:.2e}  -> "
          f"{'HIT' if worst < 1e-9 else 'MISS'}")
    worst_r2 = max(r["one_minus_r2"] for r in a1.values())
    print(f"S3 all five      worst 1-R2   = {worst_r2:.2e}  -> "
          f"{'HIT' if worst_r2 < 1e-12 else 'MISS'}")
    worst_dev = max(r["max_rel_dev_from_one_point"] for r in a1.values())
    print(f"S4 one point     worst dev    = {worst_dev:.2e}  -> "
          f"{'HIT' if worst_dev < 1e-12 else 'MISS'}")

    a2 = results["arm2_single_edge"]
    print("\n=== ARM 2 -- ONE edge swept, 99 edges held at 1 ===")
    print(f"slope = {a2['slope']:.6f}   R2 = {a2['r2']:.6f}   "
          f"d: {a2['d_at_first_J']:.6f} -> {a2['d_at_last_J']:.6f}")
    print(f"S5  |slope+0.5| = {a2['abs_slope_err']:.4f} > 0.3   -> "
          f"{'HIT' if a2['abs_slope_err'] > 0.3 else 'MISS'}")
    print(f"S5b |slope|     = {a2['abs_slope']:.4f} < 0.15  -> "
          f"{'HIT' if a2['abs_slope'] < 0.15 else 'MISS'}")
    print(f"S5c R2          = {a2['r2']:.6f} < 0.99  -> "
          f"{'HIT' if a2['r2'] < 0.99 else 'MISS'}")

    a3 = results["arm3_disconnected"]
    print("\n=== ARM 3 -- two disjoint rings; nodes 0 and 50 have NO path ===")
    print(f"pieces = {a3['pieces']}   all finite = {a3['all_finite']}   "
          f"slope = {a3['slope']:.9f}")
    print(f"d(0,50) across components = {a3['d_across_components'][0]:.6f}   "
          f"d(0,25) within one        = {a3['d_within_component'][0]:.6f}")
    print(f"S6 finite        -> {'HIT' if a3['all_finite'] else 'MISS'}")
    print(f"S7 |slope+0.5| = {a3['abs_slope_err']:.2e} -> "
          f"{'HIT' if a3['abs_slope_err'] < 1e-9 else 'MISS'}")

    a4 = results["arm4_precision"]
    print("\n=== ARM 4 -- precision ===")
    print(f"exact 5*sqrt(10)        = {a4['exact_at_first_J']:.9f}")
    print(f"published notebook      = {a4['published_at_first_J']:.9f}  "
          f"rel dev {a4['published_rel_dev']:.2e}")
    print(f"float64 here            = {a4['float64'][0]:.9f}  "
          f"rel dev {a4['max_rel_dev_float64']:.2e}")
    if isinstance(a4.get("float32"), list):
        print(f"float32 here            = {a4['float32_at_first_J']:.9f}  "
              f"rel dev {a4['max_rel_dev_float32']:.2e}   backend={a4['jax_backend']}")
        print(f"S8 float64 < 1e-12 -> "
              f"{'HIT' if a4['max_rel_dev_float64'] < 1e-12 else 'MISS'}")
        print(f"S9 float32 > 1e-8  -> "
              f"{'HIT' if a4['max_rel_dev_float32'] > 1e-8 else 'MISS'}")
        print(f"MEASURED (not predicted): float32 |slope+0.5| = "
              f"{a4['float32_abs_slope_err']:.2e}; notebook gate atol=1e-4 "
              f"{'absorbs it' if a4['float32_passes_notebook_gate_atol_1e_4'] else 'does not absorb it'}")

    a5 = results["arm5_repo_scale_rule"]
    print("\n=== ARM 5 -- the other half of the identity, from spar ===")
    print(f"watching the link {list(a5.values())[0]['watched_link']}")
    print(f"{'factor':>8} {'weight':>12} {'resistance':>16} {'bearing':>14} "
          f"{'total':>10} {'conserved':>10}")
    for f, r in a5.items():
        print(f"{f:>8} {r['watched_weight']:>12.4g} {r['watched_resistance']:>16.9f} "
              f"{r['watched_bearing']:>14.9f} {r['total']:>10.6f} {str(r['conserved']):>10}")

    a6 = results["arm6_post_hoc_no_prediction"]
    print("\n=== ARM 6 -- DIAGNOSIS, MEASURED AFTER THE RESULT ===")
    print("No prediction was registered for any of this. Nothing below is scored.")
    print(f"\n{'graph':<26} {'slope, rank fixed':>19} {'|slope+0.5|':>13}")
    for name, r in a6["rank_aware"].items():
        print(f"{name:<26} {r['slope']:>19.12f} {r['abs_slope_err']:>13.2e}")
    leaks = sum(1 for d in a6["cutoff_drift"] if d["leaks"])
    print(f"\ncomplete graph: null eigenvalue sits ABOVE the default rcond cutoff "
          f"at {leaks} of {len(a6['cutoff_drift'])} couplings")
    rc = a6["repo_engine"]["complete_swept"]
    print(f"\nthis repo's mesh_metric on K100, swept: worst rel dev "
          f"{rc['worst_rel_dev']:.2e} at J={rc['worst_J']:.4f} "
          f"({rc['worst_engine']:.9f} vs exact {rc['worst_exact']:.9f})")
    rd = a6["repo_engine"]["disconnected_pair"]
    print(f"this repo's mesh_metric across components (J=1): {rd['engine']}  "
          f"-- bare pinv said {rd['bare_pinv']:.6f}; pieces seen = "
          f"{rd['pieces_seen_by_engine']}")
    print("\nthe notebook's own verdict on K100, same graph, same float64:")
    print(f"  {'assembly':<20} {'pinv':<7} {'slope':>17} {'|err|':>10}  verdict")
    for r in a6["library_flip_on_K100"].values():
        print(f"  {r['assembly']:<20} {r['inverter']:<7} {r['slope']:>17.12f} "
              f"{r['abs_slope_err']:>10.2e}  {r['notebook_verdict']}")

    with open(os.path.join(HERE, "results_scaling.json"), "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)
    print("\nwrote results_scaling.json")
    return results


if __name__ == "__main__":
    main()
