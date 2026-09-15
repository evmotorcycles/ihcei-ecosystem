#!/usr/bin/env python3
"""Run LINTEL on this repository's real import graph.

Offline, CPU, deterministic, no network, no keys.

Predictions locked in prereg_lintel.md, sha256
87f7bc79f3b81ec6c61f66dbec84a7b8b02ad08907a9af8679823abbaed54189
"""

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "page-code"))

from blueprint import blueprint                                   # noqa: E402
from lintel import (bridges, collapse_passthrough, cuts,          # noqa: E402
                    insert_shim, merge_pair, pieces, report,
                    split_module, survivors)
from spar.spar import Structure, bearings                         # noqa: E402

PREREG_SHA = "87f7bc79f3b81ec6c61f66dbec84a7b8b02ad08907a9af8679823abbaed54189"


def hit(ok):
    return "HIT" if ok else "MISS"


def graph():
    bp = blueprint(ROOT, "repo")
    p = bp["project"]
    return p["parts"], [tuple(e) for e in p["links"]], bp["counts"]


def foster(parts, links):
    b = bearings(Structure(list(parts), [tuple(e) for e in links]))
    return b["total"], b["expected_total"], b["conserved"]


def main():
    parts, links, counts = graph()
    raw = cuts(parts, links)
    print("=== the subject: this repository's real import graph ===")
    print(f"  {counts}")
    print(f"  {len(parts)} modules in the graph, {len(links)} edges, "
          f"{pieces(parts, links)} pieces")
    print(f"\nN1 at least 5 cut vertices -> {hit(len(raw) >= 5)}  "
          f"({len(raw)} found)")
    print(f"  first ten: {sorted(raw)[:10]}")

    # ------------------------------------------- N2: a shim on a bridge ----
    br = bridges(parts, links)
    print(f"\n=== N2 -- inserting a shim on a bridge edge ===")
    print(f"  {len(br)} bridge edges in the graph")
    made_cut = 0
    for e in br:
        p2, l2 = insert_shim(parts, links, e)
        shim = [n for n in p2 if n not in parts][0]
        if shim in cuts(p2, l2):
            made_cut += 1
    print(f"  shims that became cut vertices: {made_cut}/{len(br)}")
    print(f"N2 every one -> {hit(made_cut == len(br) and len(br) > 0)}")

    # ------------------------------------------------ N5: splitting one ----
    print(f"\n=== N5 -- splitting a cut vertex in two ===")
    both = [c for c in sorted(raw)
            if any(l[1] == c for l in links) and any(l[0] == c for l in links)]
    target = both[0]
    p2, l2 = split_module(parts, links, target)
    c2 = cuts(p2, l2)
    halves = {target + "#in", target + "#out"}
    print(f"  split {target!r}")
    print(f"  cut vertices before {len(raw)}, after {len(c2)}")
    print(f"  both halves are cut vertices: {halves <= c2}")
    n5 = (halves <= c2) and len(c2) == len(raw) + 1
    print(f"N5 one becomes two, count rises by exactly 1 -> {hit(n5)}  "
          f"(rose by {len(c2) - len(raw)})")
    # the mechanism behind the miss, measured across every eligible cut vertex
    tally = {"in_only": 0, "out_only": 0, "both": 0, "neither": 0}
    for t in both:
        pp, ll = split_module(parts, links, t)
        cc = cuts(pp, ll)
        i, o = (t + "#in") in cc, (t + "#out") in cc
        tally["both" if i and o else "in_only" if i else
              "out_only" if o else "neither"] += 1
    print(f"  across all {len(both)} eligible cut vertices: {tally}")
    print("  the fan-in half inherits the cut; the fan-out half does not.")
    print("  articulation is about what routes THROUGH you from your importers.")

    # -------------------------------------- N6: inflate the count at will ----
    print(f"\n=== N6 -- is the count inflatable with no behaviour change? ===")
    rng = random.Random(0)
    edges = sorted(set((a, b) for a, b, *_ in links))
    p3, l3 = list(parts), list(links)
    counts_seq = [len(cuts(p3, l3))]
    picks = rng.sample(edges, 40)
    for k, e in enumerate(picks):
        p3, l3 = insert_shim(p3, l3, e, tag=f"#{k}")
        counts_seq.append(len(cuts(p3, l3)))
    print(f"  shims inserted:  0   10   20   30   40")
    print(f"  cut vertices:  " + "  ".join(
        f"{counts_seq[i]:>3}" for i in (0, 10, 20, 30, 40)))
    monotone = all(counts_seq[i] <= counts_seq[i + 1]
                   for i in range(len(counts_seq) - 1))
    print(f"N6 monotone rising -> {hit(monotone and counts_seq[-1] > counts_seq[0])}"
          f"  ({counts_seq[0]} -> {counts_seq[-1]}, "
          f"{counts_seq[-1] / counts_seq[0]:.2f}x)")

    # ---------------------------------------------- N7: can Foster judge? ----
    print(f"\n=== N7 -- can Foster's total arbitrate? ===")
    t0, e0, c0 = foster(parts, links)
    t1, e1, c1 = foster(*insert_shim(parts, links, br[0])[:2]) if br else (0, 0, 0)
    t2, e2, c2f = foster(p2, l2)
    print(f"  raw            total {t0:.4f}  expected {e0:.1f}  conserved {c0}")
    print(f"  after INSERT   total {t1:.4f}  expected {e1:.1f}  conserved {c1}")
    print(f"  after SPLIT    total {t2:.4f}  expected {e2:.1f}  conserved {c2f}")
    print(f"N7 total moves, so it cannot arbitrate -> "
          f"{hit(t1 != t0 and t2 != t0 and c0 and c1 and c2f)}")
    print("  it stays conserved in all three, which is the point: a counting")
    print("  identity is true of every drawing and so prefers none of them.")

    # ------------------------------------------------- N3/N4: survival ----
    print(f"\n=== N3/N4 -- which findings survive every rewrite ===")
    passthroughs = [n for n in parts
                    if len([l for l in links if l[1] == n]) == 1
                    and len([l for l in links if l[0] == n]) == 1]
    mergeable = []
    for a, b, *_ in links:
        if {x for x, y, *_ in links if y == b} == {a}:
            mergeable.append((a, b))

    rewrites = [("INSERT on first bridge",
                 lambda p, l: insert_shim(p, l, br[0]))]
    if passthroughs:
        rewrites.append(("COLLAPSE a pass-through",
                         lambda p, l: collapse_passthrough(p, l, passthroughs[0])))
    rewrites.append(("SPLIT the first cut vertex",
                     lambda p, l: split_module(p, l, target)))
    if mergeable:
        rewrites.append(("MERGE a sole-importer pair",
                         lambda p, l: merge_pair(p, l, *mergeable[0])))

    print(f"  rewrites applied: {[r[0] for r in rewrites]}")
    print(f"  ({len(passthroughs)} pass-throughs, {len(mergeable)} mergeable "
          f"pairs available)")
    res = survivors(parts, links, rewrites)
    for r in res["per_rewrite"]:
        print(f"    {r['rewrite']:<28} cuts after {r['cuts_after']:>3}  "
              f"invented-and-cut {r['invented_nodes_that_are_cuts']:>2}  "
              f"raw lost {len(r['raw_cuts_lost']):>2}")
    print(f"\n  raw cut vertices : {len(res['raw_cuts'])}")
    print(f"  survivors        : {len(res['survivors'])}")
    print(f"  casualties       : {len(res['casualties'])}")
    print(f"N3 at least one casualty -> {hit(len(res['casualties']) >= 1)}")
    print(f"N4 at least one survivor -> {hit(len(res['survivors']) >= 1)}")
    if res["casualties"]:
        print(f"\n  stopped being reported: {res['casualties'][:6]}")
    if res["survivors"]:
        print(f"  still reported       : {res['survivors'][:6]}")

    # ---- POST HOC. No prediction registered. N3 missed with four single
    # rewrites; this asks whether a much heavier reorganisation shifts the set.
    print("\n=== POST HOC -- a heavy rewrite regime, no prediction registered ===")
    rng2 = random.Random(7)
    hp, hl = list(parts), list(links)
    for k, e in enumerate(rng2.sample(sorted(set((a, b) for a, b, *_ in links)), 60)):
        hp, hl = insert_shim(hp, hl, e, tag=f"@{k}")
    for t in rng2.sample(both, min(8, len(both))):
        if t in hp:
            hp, hl = split_module(hp, hl, t)
    for a, b in mergeable[:8]:
        if b in hp and {x for x, y, *_ in hl if y == b} == {a}:
            hp, hl = merge_pair(hp, hl, a, b)
    heavy = cuts(hp, hl)
    mapped = set()
    for n in heavy:
        o = n
        for suf in ("#in", "#out"):
            if o.endswith(suf):
                o = o[: -len(suf)]
        if "→shim→" not in o:
            mapped.add(o)
    kept = set(res["raw_cuts"]) & mapped
    lost = set(res["raw_cuts"]) - mapped
    print(f"  60 shims + 8 splits + up to 8 merges applied together")
    print(f"  cut vertices after: {len(heavy)} (raw was {len(raw)})")
    print(f"  original findings still reported: {len(kept)}/{len(raw)}")
    print(f"  original findings lost:           {len(lost)}")
    if lost:
        print(f"    {sorted(lost)[:6]}")
    print("  -> the COUNT moves a great deal; the NAMES are what hold still.")

    print("\n=== what a person is handed ===")
    print(report(parts, links, res))

    out = {"prereg_sha256": PREREG_SHA, "counts": counts,
           "modules": len(parts), "edges": len(links),
           "raw_cut_count": len(raw), "bridges": len(br),
           "n2_shims_that_became_cuts": made_cut,
           "n5_split_target": target, "n5_cuts_after": len(cuts(p2, l2)),
           "n6_sequence": counts_seq,
           "n7_foster": {"raw": t0, "insert": t1, "split": t2},
           "survival": res}
    with open(os.path.join(HERE, "results_lintel.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("\nwrote results_lintel.json")
    return out


if __name__ == "__main__":
    main()
