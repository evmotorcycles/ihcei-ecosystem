#!/usr/bin/env python3
"""Run the collapse probe and read the result with this repository's engines.

Offline, deterministic, CPU, no network, no keys, no model downloads.

Predictions locked in prereg_jepa.md, sha256
65522d024b5f06db18e871cf527fbec151ae9375b38bc362bdedea0ea6b98dc9
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

from mini_jepa import (knn_edges, make_data, mean_pairwise_distance,   # noqa: E402
                       spread, target_embeddings, train)
from spar.spar import Structure, bearings, single_points               # noqa: E402

PREREG_SHA = "65522d024b5f06db18e871cf527fbec151ae9375b38bc362bdedea0ea6b98dc9"
HELD_OUT = 40
SEEDS = [0, 1, 2, 3, 4]


def hit(ok):
    return "HIT" if ok else "MISS"


def one_seed(seed):
    X, _ = make_data(seed=seed)
    out = {}
    for name, symmetric in (("symmetric", True), ("asymmetric", False)):
        res = train(X, symmetric=symmetric, seed=seed)
        E0 = target_embeddings(res["Wt"] * 0 + _initial_target(seed), X[:HELD_OUT])
        E = target_embeddings(res["Wt"], X[:HELD_OUT])
        out[name] = {
            "final_loss": res["final_loss"],
            "spread_at_init": spread(E0),
            "spread_after": spread(E),
            "spread_ratio": spread(E) / spread(E0),
            "mean_pairwise_distance": mean_pairwise_distance(E),
            "embeddings": E,
        }
    return out


def _initial_target(seed):
    """The target encoder at initialisation -- the denominator for the ratio."""
    from mini_jepa import _init
    We, _, _ = _init(seed)
    return We


def structural(E):
    """Read a kNN graph over the embeddings with spar. Measured, not derived."""
    edges = knn_edges(E, k=3)
    names = [f"s{i:03d}" for i in range(len(E))]
    st = Structure(names, [(names[a], names[b], w) for a, b, w in edges])
    b = bearings(st)
    return {
        "edges": len(edges),
        "parts": b["steps"],
        "pieces": b["pieces"],
        "total_bearing": b["total"],
        "expected_total": b["expected_total"],
        "conserved": b["conserved"],
        "cut_parts": len(single_points(st)),
    }


def main():
    per_seed = {}
    for s in SEEDS:
        per_seed[s] = one_seed(s)

    base = per_seed[0]
    sym, asym = base["symmetric"], base["asymmetric"]

    print("=== ARM 1 -- the collapse mechanism (seed 0) ===")
    print(f"{'arm':<12} {'final loss':>12} {'spread@init':>13} {'spread after':>14} "
          f"{'ratio':>10}")
    for name in ("symmetric", "asymmetric"):
        r = base[name]
        print(f"{name:<12} {r['final_loss']:>12.3e} {r['spread_at_init']:>13.6f} "
              f"{r['spread_after']:>14.3e} {r['spread_ratio']:>10.3e}")

    print(f"\nJ1 symmetric collapses,  ratio < 0.01 -> "
          f"{hit(sym['spread_ratio'] < 0.01)}  ({sym['spread_ratio']:.3e})")
    print(f"J2 asymmetric holds,     ratio > 0.5  -> "
          f"{hit(asym['spread_ratio'] > 0.5)}  ({asym['spread_ratio']:.3e})")
    print(f"J3 symmetric loss near zero, < 0.01   -> "
          f"{hit(sym['final_loss'] < 0.01)}  ({sym['final_loss']:.3e})")

    print("\n  across seeds:")
    print(f"  {'seed':>5} {'sym ratio':>12} {'asym ratio':>12} {'sym loss':>12}")
    for s in SEEDS:
        p = per_seed[s]
        print(f"  {s:>5} {p['symmetric']['spread_ratio']:>12.3e} "
              f"{p['asymmetric']['spread_ratio']:>12.3e} "
              f"{p['symmetric']['final_loss']:>12.3e}")
    j1_all = all(per_seed[s]["symmetric"]["spread_ratio"] < 0.01 for s in SEEDS)
    j2_all = all(per_seed[s]["asymmetric"]["spread_ratio"] > 0.5 for s in SEEDS)
    print(f"  J1 on every seed -> {hit(j1_all)}    J2 on every seed -> {hit(j2_all)}")

    print("\n=== ARM 2 -- what spar sees (seed 0, 40 held-out samples) ===")
    st_sym = structural(sym["embeddings"])
    st_asym = structural(asym["embeddings"])
    print(f"{'arm':<12} {'edges':>6} {'pieces':>7} {'total bearing':>15} "
          f"{'expected':>9} {'conserved':>10} {'cut parts':>10}")
    for name, st in (("symmetric", st_sym), ("asymmetric", st_asym)):
        print(f"{name:<12} {st['edges']:>6} {st['pieces']:>7} "
              f"{st['total_bearing']:>15.6f} {st['expected_total']:>9.1f} "
              f"{str(st['conserved']):>10} {st['cut_parts']:>10}")

    print(f"\nJ4 Foster conserved in BOTH arms      -> "
          f"{hit(st_sym['conserved'] and st_asym['conserved'])}")
    ratio = sym["mean_pairwise_distance"] / asym["mean_pairwise_distance"]
    print(f"J5 collapsed distances < 1% of healthy -> {hit(ratio < 0.01)}  "
          f"({sym['mean_pairwise_distance']:.3e} vs "
          f"{asym['mean_pairwise_distance']:.3e}, ratio {ratio:.3e})")

    # ---- post-hoc control. MEASURED AFTER THE RESULT, no prediction registered.
    rng = np.random.default_rng(12345)
    noise_E = rng.normal(size=asym["embeddings"].shape)
    st_noise = structural(noise_E)
    print("\n  post-hoc control, no prediction was registered for this:")
    print(f"{'noise':<12} {st_noise['edges']:>6} {st_noise['pieces']:>7} "
          f"{st_noise['total_bearing']:>15.6f} {st_noise['expected_total']:>9.1f} "
          f"{str(st_noise['conserved']):>10} {st_noise['cut_parts']:>10}")
    print("  Foster's total is parts - pieces. It is a property of the node and")
    print("  component count, not of the embeddings, so untrained noise scores")
    print("  the same way a trained representation does.")

    print("\n=== ARM 3 -- Claude in the semantic seam ===")
    print("  C1 status: UNRUN, by design and on the record.")
    print("  Claude wrote the pre-registration. A model answering its own probe")
    print("  after writing down the expected answer is contaminated by")
    print("  construction -- the A3/A6 defect already recorded in agi-stack/.")
    print("  There is also no offline, resamplable model access here, so the run")
    print("  could not be reproduced even if it were clean.")
    print("  No number is reported for this arm.")

    out = {
        "prereg_sha256": PREREG_SHA,
        "seeds": SEEDS,
        "arm1": {str(s): {k: {kk: vv for kk, vv in v.items() if kk != "embeddings"}
                          for k, v in per_seed[s].items()} for s in SEEDS},
        "arm2": {"symmetric": st_sym, "asymmetric": st_asym,
                 "distance_ratio": ratio,
                 "post_hoc_noise_control": st_noise},
        "arm3": {"status": "UNRUN",
                 "why": "author contamination; no offline resamplable model access",
                 "number_reported": None},
    }
    with open(os.path.join(HERE, "results_jepa.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("\nwrote results_jepa.json")
    return out


if __name__ == "__main__":
    main()
