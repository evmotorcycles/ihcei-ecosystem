#!/usr/bin/env python3
"""Measure what the two sensors can see, and whether a threshold is defensible.

Offline, CPU, deterministic, no network, no keys.

Predictions locked in prereg_gate.md, sha256
ddaa4b4a3ca7f02c0e468bf14b765fa23b926db19f17a45534ffde21e602cca4
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "jepa-probe"))

from gate import (covariance_trace, effective_rank, halts,      # noqa: E402
                  project_to_rank, reading)
from mini_jepa import (knn_edges, make_data, target_embeddings,  # noqa: E402
                       train)

PREREG_SHA = "ddaa4b4a3ca7f02c0e468bf14b765fa23b926db19f17a45534ffde21e602cca4"
HELD_OUT = 40
SEEDS = [0, 1, 2, 3, 4]
MOMENTA = [0.0, 0.5, 0.9, 0.99, 0.996, 0.999]
SCALES = [1e-3, 1e-2, 1e-1, 1.0, 1e1, 1e2, 1e3]


def hit(ok):
    return "HIT" if ok else "MISS"


def arms(seed=0, momentum=0.996):
    X, _ = make_data(seed=seed)
    out = {}
    for name, sym in (("symmetric", True), ("asymmetric", False)):
        import mini_jepa
        old = mini_jepa.EMA_MOMENTUM
        mini_jepa.EMA_MOMENTUM = momentum
        try:
            r = train(X, symmetric=sym, seed=seed)
        finally:
            mini_jepa.EMA_MOMENTUM = old
        out[name] = target_embeddings(r["Wt"], X[:HELD_OUT])
    return out


def main():
    base = arms(seed=0)
    healthy, collapsed = base["asymmetric"], base["symmetric"]

    # ---------------------------------------------------- arm 1: scale ----
    print("=== ARM 1 -- is an absolute variance floor a valid instrument? ===")
    print(f"{'scale c':>10} {'trace':>14} {'trace/c^2':>16} {'eff. rank':>12}")
    t0, r0 = covariance_trace(healthy), effective_rank(healthy)
    g1_err, g3_err = 0.0, 0.0
    for c in SCALES:
        E = healthy * c
        t, r = covariance_trace(E), effective_rank(E)
        g1_err = max(g1_err, abs(t / (c * c) - t0) / t0)
        g3_err = max(g3_err, abs(r - r0))
        print(f"{c:>10.0e} {t:>14.6e} {t / (c * c):>16.9f} {r:>12.6f}")
    print(f"\nG1 trace scales as c^2, rel err < 1e-9 -> {hit(g1_err < 1e-9)} "
          f"({g1_err:.2e})")
    print(f"G3 effective rank is scale-invariant   -> {hit(g3_err < 1e-9)} "
          f"({g3_err:.2e})")

    # G2: a fixed epsilon defeated by multiplication
    eps = t0 / 100.0          # a floor at 1% of healthy volumetric spread
    t_coll = covariance_trace(collapsed)
    boost = 1e7
    t_boost = covariance_trace(collapsed * boost)
    print(f"\n  a floor set at 1% of healthy trace: eps = {eps:.6e}")
    print(f"  collapsed trace            {t_coll:.6e}   halts = {t_coll < eps}")
    print(f"  collapsed x {boost:.0e} trace    {t_boost:.6e}   halts = "
          f"{t_boost < eps}")
    g2 = (t_coll < eps) and not (t_boost < eps)
    print(f"G2 a rescale defeats the fixed floor   -> {hit(g2)}")

    # ------------------------------------------- arm 2: two failures ----
    print("\n=== ARM 2 -- does either sensor catch both failures? ===")
    dim_collapsed = project_to_rank(healthy, k=2)
    rows = {"healthy": healthy, "volumetric (trained)": collapsed,
            "dimensional (rank-2)": dim_collapsed}
    print(f"{'embedding':<24} {'trace':>14} {'trace/healthy':>15} "
          f"{'eff rank':>10} {'rank/healthy':>13}")
    read = {}
    for name, E in rows.items():
        r = reading(E)
        read[name] = r
        print(f"{name:<24} {r['covariance_trace']:>14.6e} "
              f"{r['covariance_trace'] / t0:>15.6e} "
              f"{r['effective_rank']:>10.4f} "
              f"{r['effective_rank'] / r0:>13.4f}")

    vol, dim = read["volumetric (trained)"], read["dimensional (rank-2)"]
    g4 = vol["effective_rank"] / r0 >= 0.5
    g5 = dim["covariance_trace"] / t0 >= 0.5
    g6 = dim["effective_rank"] / r0 < 0.5
    print(f"\nG4 rank MISSES volumetric collapse   -> {hit(g4)}  "
          f"(rank kept {vol['effective_rank'] / r0:.3f} of healthy)")
    print(f"G5 trace MISSES dimensional collapse -> {hit(g5)}  "
          f"(trace kept {dim['covariance_trace'] / t0:.3f} of healthy)")
    print(f"G6 rank CATCHES dimensional collapse -> {hit(g6)}  "
          f"(rank kept {dim['effective_rank'] / r0:.3f} of healthy)")
    print(f"G7 both off-diagonals miss           -> {hit(g4 and g5)}")

    # ----------------------------------------------- arm 3: the knee ----
    print("\n=== ARM 3 -- is there a knee to put a threshold on? ===")
    print(f"{'momentum':>10} " + " ".join(f"{'seed ' + str(s):>12}" for s in SEEDS))
    sweep = {}
    for m in MOMENTA:
        ratios = []
        for s in SEEDS:
            a = arms(seed=s, momentum=m)
            init_spread = None
            E = a["asymmetric"]
            # ratio against the healthy reference at this seed's initialisation
            X, _ = make_data(seed=s)
            from mini_jepa import _init, embed
            We0, _, _ = _init(s)
            E0 = embed(We0, X[:HELD_OUT][:, [2, 3], :]).mean(axis=1)
            init_spread = float(E0.var(axis=0).mean())
            ratios.append(float(E.var(axis=0).mean()) / init_spread)
        sweep[m] = ratios
        print(f"{m:>10.3f} " + " ".join(f"{v:>12.3e}" for v in ratios))

    medians = [float(np.median(sweep[m])) for m in MOMENTA]
    monotone = all(medians[i] <= medians[i + 1] * 1.0000001
                   for i in range(len(medians) - 1))
    in_band = [m for m, v in zip(MOMENTA, medians) if 0.01 <= v <= 0.5]
    # G9 has TWO clauses and both must hold. Scoring only the second one
    # flattered the result on the first pass; this checks the gap as well.
    adjacent_orders = [abs(np.log10(medians[i + 1] / medians[i]))
                       for i in range(len(medians) - 1)]
    has_gap = max(adjacent_orders) > 6.0
    g9 = has_gap and not in_band
    print(f"\n  medians: " + "  ".join(f"{v:.3e}" for v in medians))
    print(f"G8 monotone non-decreasing in momentum -> {hit(monotone)}")
    print(f"G9 abrupt transition AND empty band    -> {hit(g9)}")
    print(f"   clause a, an adjacent pair > 6 orders apart: {has_gap}  "
          f"(largest {max(adjacent_orders):.3f} orders)")
    print(f"   clause b, nothing inside [0.01, 0.5]:        {not in_band}")
    print("   -> the momentum sweep never collapses at all, so it has no")
    print("      transition to find a knee in. Clause b holds vacuously.")

    # ---- ARM 4. POST HOC. No prediction was registered for any of this. ----
    print("\n=== ARM 4 -- DIAGNOSIS, MEASURED AFTER THE RESULT ===")
    print("Nothing here is scored. The momentum dial turned out to be the wrong")
    print("dial, so this asks which half of the asymmetry is load-bearing.")
    from mini_jepa import target_embeddings as _te

    def spread_ratio(seed, shared_target, leak):
        X, _ = make_data(seed=seed)
        from mini_jepa import _init, embed
        We0, _, _ = _init(seed)
        E0 = embed(We0, X[:HELD_OUT][:, [2, 3], :]).mean(axis=1)
        r = train(X, symmetric=False, seed=seed,
                  shared_target=shared_target, leak=leak)
        E = _te(r["Wt"], X[:HELD_OUT])
        return float(E.var(axis=0).mean()) / float(E0.var(axis=0).mean())

    print(f"\n  {'arrangement':<44} {'spread ratio (seed 0)':>22}")
    for label, shared, leak in (
            ("shared weights + full gradient  (symmetric)", True, 1.0),
            ("shared weights + STOP-GRADIENT, no EMA", True, 0.0),
            ("EMA target + full gradient", False, 1.0),
            ("EMA target + stop-gradient  (asymmetric)", False, 0.0)):
        print(f"  {label:<44} {spread_ratio(0, shared, leak):>22.3e}")

    print(f"\n  gradient leak sweep, EMA target held fixed:")
    print(f"  {'leak':>8} " + " ".join(f"{'seed ' + str(s):>12}" for s in SEEDS))
    leak_sweep = {}
    for lk in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
        vals = [spread_ratio(s, False, lk) for s in SEEDS]
        leak_sweep[lk] = vals
        print(f"  {lk:>8.2f} " + " ".join(f"{v:>12.3e}" for v in vals))
    leak_med = {lk: float(np.median(v)) for lk, v in leak_sweep.items()}
    mid = [lk for lk, v in leak_med.items() if 0.01 <= v <= 0.5]
    print(f"\n  values landing inside [0.01, 0.5] at this resolution: {mid}")

    # The coarse sweep above shows an EMPTY band, which would make a cutoff
    # inside it defensible. That conclusion is an artefact of the sampling.
    print("\n  the same sweep, sampled finely near zero:")
    print(f"  {'leak':>8} {'median spread ratio':>21}   in band?")
    fine = {}
    for lk in [0.0, 0.001, 0.0025, 0.005, 0.0075, 0.01, 0.02, 0.05, 0.1]:
        vals = [spread_ratio(s, False, lk) for s in SEEDS]
        m = float(np.median(vals))
        fine[lk] = vals
        print(f"  {lk:>8.4f} {m:>21.3e}   "
              f"{'YES' if 0.01 <= m <= 0.5 else ''}")
    fine_med = {lk: float(np.median(v)) for lk, v in fine.items()}
    fine_mid = [lk for lk, v in fine_med.items() if 0.01 <= v <= 0.5]
    print(f"\n  values inside [0.01, 0.5] when sampled finely: {fine_mid}")
    print("  -> the band is NOT empty. The sensor walks continuously through it.")
    print("     The coarse sweep's empty band was an artefact of resolution, and")
    print("     a threshold read off it would have been an artefact too.")

    # the gate refuses to invent a number
    try:
        halts(healthy, None, None)
        refused = False
    except ValueError:
        refused = True
    print(f"\n  gate refuses to run without stated cutoffs -> {refused}")

    out = {
        "prereg_sha256": PREREG_SHA,
        "arm1": {"healthy_trace": t0, "healthy_rank": r0,
                 "g1_max_rel_err": g1_err, "g3_max_rank_change": g3_err,
                 "eps_at_1pct": eps, "collapsed_trace": t_coll,
                 "collapsed_boosted_trace": t_boost, "g2": g2},
        "arm2": read,
        "arm3": {"momenta": MOMENTA, "sweep": sweep, "medians": medians,
                 "monotone": monotone, "occupants_of_band": in_band,
                 "largest_adjacent_orders": float(max(adjacent_orders)),
                 "has_gap": bool(has_gap), "g9": bool(g9)},
        "arm4_post_hoc_no_prediction": {
            "leak_sweep": leak_sweep, "leak_medians": leak_med,
            "leak_values_inside_band_coarse": mid,
            "fine_sweep": fine, "fine_medians": fine_med,
            "leak_values_inside_band_fine": fine_mid,
            "band_is_empty": not fine_mid},
        "gate_refuses_default_cutoffs": refused,
    }
    with open(os.path.join(HERE, "results_gate.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("\nwrote results_gate.json")
    return out


if __name__ == "__main__":
    main()
