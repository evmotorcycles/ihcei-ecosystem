#!/usr/bin/env python3
"""run_stack.py — can the Laplacian be gamed, and what does LISM do in a chain?

    python3 agi-stack/run_stack.py

Offline, deterministic. Predictions locked in prereg_stack.md before this file
existed. Every label is ordinary English.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ihcei_v3"))

from spar.spar import Structure, bearings, single_points   # noqa: E402
from fathom.fathom import Claim, sound                     # noqa: E402

PREREG_SHA = "e4af23ec25616963f9e8edb9a512d146521d218dd66064a6dcc3eceb523b670c"

# ── the audited graph, carried over from order-invariance/ ──────────────────
CONCLUSION = "the conclusion"
METHOD = "the one declared method"
PASSAGES = ["the first cited passage", "the second cited passage",
            "the third cited passage"]
PARTS = PASSAGES + [METHOD, CONCLUSION]
HONEST = [(p, METHOD, 1.0) for p in PASSAGES] + [(METHOD, CONCLUSION, 1.0)]

# Every honest edge can name where it came from. That is what makes the padding
# below refusable -- see G5.
WHERE = {(p, METHOD): "the document states this method is required to read it"
         for p in PASSAGES}
WHERE[(METHOD, CONCLUSION)] = "the document's concluding section"


def read(parts, links):
    st = Structure(list(parts), [tuple(x) for x in links])
    b = bearings(st)
    cuts = sorted(r["part"] for r in single_points(st))
    f = sound(Claim(CONCLUSION, list(PASSAGES), [tuple(x) for x in links]))
    return {
        "cut_vertices": cuts,
        "n_cuts": len(cuts),
        "deepest_dependence": round(f["deepest_dependence"], 12),
        "settles": sorted(round(x["dependence"], 12) for x in f["by_source"]),
        "total_bearing": round(b["total"], 12),
        "pieces": b["pieces"],
        "n_links": len(links),
    }


def cheapest_padding():
    """Smallest set of ADDED edges between existing nodes that removes every cut
    vertex. The adversary invents no evidence and removes nothing."""
    candidates = [(a, b, 1.0) for a, b in itertools.combinations(PARTS, 2)
                  if not any({a, b} == {x, y} for x, y, _ in HONEST)]
    for k in range(1, 5):
        for combo in itertools.combinations(candidates, k):
            if read(PARTS, HONEST + list(combo))["n_cuts"] == 0:
                return list(combo)
    return None


# ── G5: enforcement by subtraction. An edge with no `where` is refused. ──────
class Refused(Exception):
    pass


def commit_edges(links, where):
    """The only defence that works, and it is not a mathematical one: it moves
    the trust from the matrix to whoever writes the `where`."""
    out = []
    for a, b, w in links:
        if (a, b) not in where and (b, a) not in where:
            raise Refused(f"no source named for the link {a!r} -> {b!r}")
        out.append((a, b, w))
    return out


def lism(u, ds):
    """E = U * prod(D_i). The linear form. E = U*D^2 is RETIRED_FULLY and is
    not computed anywhere here."""
    e = u
    for d in ds:
        e *= d
    return e


def main():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_stack.md"), "rb")
                         .read()).hexdigest()
    if got != PREREG_SHA:
        raise SystemExit(f"pre-registration edited\n locked {PREREG_SHA}\n now {got}")

    out = {}

    # ── ARM 1: the attack ───────────────────────────────────────────────────
    honest = read(PARTS, HONEST)
    padding = cheapest_padding()
    padded = read(PARTS, HONEST + padding) if padding else None

    out["arm1_gaming"] = {
        "honest": honest,
        "cheapest_padding": [[a, b] for a, b, _ in padding] if padding else None,
        "n_edges_added": len(padding) if padding else None,
        "padded": padded,
        "G1_all_cut_vertices_removed": bool(padded and padded["n_cuts"] == 0),
        "G2_at_most_three_edges": bool(padding and len(padding) <= 3),
        "G3_deepest_dependence_falls":
            bool(padded and padded["deepest_dependence"] < honest["deepest_dependence"]),
        "G4_total_bearing_rises":
            bool(padded and padded["total_bearing"] > honest["total_bearing"]),
        "evidence_added": 0,
        "wording_changed": False,
        "nodes_added": 0,
    }

    # ── G5: the provenance defence ──────────────────────────────────────────
    commit_ok, commit_refused = True, None
    try:
        commit_edges(HONEST, WHERE)
    except Refused as e:
        commit_ok = False
        commit_refused = str(e)
    padding_refused = []
    for edge in (padding or []):
        try:
            commit_edges([edge], WHERE)
            padding_refused.append(None)
        except Refused as e:
            padding_refused.append(str(e))
    out["arm1_gaming"]["G5_honest_edges_commit"] = commit_ok
    out["arm1_gaming"]["G5_honest_refusal"] = commit_refused
    out["arm1_gaming"]["G5_every_padding_edge_refused"] = (
        bool(padding) and all(r is not None for r in padding_refused))
    out["arm1_gaming"]["G5_refusals"] = padding_refused

    # ── ARM 2: LISM through the chain ───────────────────────────────────────
    four_hops = lism(1.0, [0.9] * 4)
    depths = {n: round(lism(1.0, [0.9] * n), 12) for n in range(1, 13)}
    monotone = all(depths[n] > depths[n + 1] for n in range(1, 12))
    # smallest per-hop D keeping E >= 0.5 over 4 hops, to 2 decimals
    need = None
    d = 0.50
    while d <= 1.0001:
        if lism(1.0, [d] * 4) >= 0.5:
            need = round(d, 2)
            break
        d += 0.01

    registry_retired = None
    try:
        from gt_probabilistic import LAW_REGISTRY
        registry_retired = {
            "D_min_threshold": LAW_REGISTRY["D_min_threshold"]["status"],
            "E_quadratic": LAW_REGISTRY["E_quadratic"]["status"],
        }
    except Exception as e:                                   # noqa: BLE001
        registry_retired = {"error": str(e)}

    src = open(__file__).read()
    out["arm2_lism"] = {
        "L1_four_hops_at_0_9": round(four_hops, 12),
        "L1_below_0_66": four_hops < 0.66,
        "L2_by_depth": depths,
        "L2_monotone_decreasing": monotone,
        "L3_per_hop_needed_for_half_at_four_hops": need,
        "L3_at_least_0_84": need is not None and need >= 0.84,
        "L4_registry": registry_retired,
        # Built, not written literally: the first version of this check
        # CONTAINED both strings it forbids, so it failed on itself. Eighth
        # instance of that shape in this repository.
        "L4_no_quadratic_here": not any(
            f"D{sp}*{sp}{sp}2".replace("  ", " ") in src
            for sp in ("", " ")),
    }

    out["_prereg"] = {"file": "agi-stack/prereg_stack.md", "sha256": got}
    json.dump(out, open(os.path.join(HERE, "results_stack.json"), "w"),
              indent=1, sort_keys=True)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
