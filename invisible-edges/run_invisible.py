#!/usr/bin/env python3
"""Invisible edges, the quotient pass, and two frozen JEPA cards.

Offline, deterministic, no network. The Hugging Face fetch was an attested
manual step on 2026-09-15; everything here runs against cards/.

Predictions locked in prereg_invisible.md, sha256
1f3455944c51ef2f306bf2d50041e046438a8077ee2124c34c716b5d9f23edc9
"""

import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (HERE, ROOT, os.path.join(ROOT, "page-code"), os.path.join(ROOT, "lintel")):
    sys.path.insert(0, p)

from blueprint import blueprint, modules                       # noqa: E402
from candidates import (KIND_COMMENT, KIND_DYNAMIC, KIND_STRING,  # noqa: E402
                        find_candidates, indirection_nodes, quotient)
from lintel import cuts, insert_shim, merge_pair               # noqa: E402

PREREG_SHA = "1f3455944c51ef2f306bf2d50041e046438a8077ee2124c34c716b5d9f23edc9"
CARDS = os.path.join(HERE, "cards")


def hit(ok):
    return "HIT" if ok else "MISS"


def base_graph():
    bp = blueprint(ROOT, "repo")
    p = bp["project"]
    idx = modules(ROOT)
    paths = {rel: meta["path"] for rel, meta in idx.items()}
    return p["parts"], [tuple(e) for e in p["links"]], paths


def main():
    parts, links, paths = base_graph()
    declared = {(a, b) if a < b else (b, a) for a, b, *_ in links}
    raw = cuts(parts, links)

    # ------------------------------------------------ ARM 1: candidates ----
    cands = find_candidates(parts, paths, declared)
    kinds = {}
    for c in cands:
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    print("=== ARM 1 -- candidate invisible edges ===")
    print(f"  declared graph: {len(parts)} modules, {len(links)} imports, "
          f"{len(raw)} cut vertices")
    print(f"  candidates found: {len(cands)}")
    for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"    {v:>4}  {k}")
    print(f"\nI1 at least 20 candidates -> {hit(len(cands) >= 20)}")

    prose = [c for c in cands if c["kind"] == KIND_COMMENT]
    print(f"I2 at least one is a mention, not a dependency -> "
          f"{hit(len(prose) >= 1)}  ({len(prose)} sit only in prose)")
    for c in prose[:3]:
        print(f"    {c['from']}  ->  {c['to']}")

    widened = sorted(set(links) | {(c["from"], c["to"], 1.0) for c in cands})
    wparts = sorted(set(parts) | {c["from"] for c in cands}
                    | {c["to"] for c in cands})
    wide = cuts(wparts, widened)
    lost = raw - wide
    new = wide - raw
    print(f"\n  declared+candidates: {len(wparts)} modules, {len(widened)} edges, "
          f"{len(wide)} cut vertices")
    print(f"I3 at least one cut vertex lost -> {hit(len(lost) >= 1)}  "
          f"({len(lost)} lost)")
    print(f"I4 at least one new cut vertex  -> {hit(len(new) >= 1)}  "
          f"({len(new)} new)")
    print(f"I5 the two sets are not nested  -> "
          f"{hit(len(lost) >= 1 and len(new) >= 1)}")
    survived = len(raw & wide)
    print(f"I6 fewer than all {len(raw)} names survive -> "
          f"{hit(survived < len(raw))}  ({survived}/{len(raw)} survived)")
    if lost:
        print(f"    lost: {sorted(lost)[:6]}")
    if new:
        print(f"    new : {sorted(new)[:6]}")

    # -------------------------------------------------- ARM 2: quotient ----
    print("\n=== ARM 2 -- the quotient pass ===")
    rng = random.Random(0)
    edges = sorted({(a, b) for a, b, *_ in links})
    cols = {}
    for n_shims in (0, 20, 40):
        p, l = list(parts), list(links)
        for k, e in enumerate(rng.sample(edges, n_shims)):
            p, l = insert_shim(p, l, e, tag=f"#{k}")
        qp, ql, removed = quotient(p, l)
        cols[n_shims] = {"cuts_before": len(cuts(p, l)),
                         "quotient_cuts": len(cuts(qp, ql)),
                         "collapsed": len(removed),
                         "edges": sorted((a, b) for a, b, *_ in ql)}
    print(f"  {'shims':>6} {'cuts':>6} {'quotient cuts':>15} {'nodes collapsed':>17}")
    for n in (0, 20, 40):
        c = cols[n]
        print(f"  {n:>6} {c['cuts_before']:>6} {c['quotient_cuts']:>15} "
              f"{c['collapsed']:>17}")
    q1 = len({cols[n]["quotient_cuts"] for n in (0, 20, 40)}) == 1
    q2 = cols[0]["edges"] == cols[20]["edges"] == cols[40]["edges"]
    print(f"\nQ1 quotient count identical across all three -> {hit(q1)}")
    print(f"Q2 quotient edge sets identical               -> {hit(q2)}")

    real_indirection = indirection_nodes(parts, links)
    q3 = cols[0]["collapsed"] == 0
    print(f"Q3 quotient is the identity on the raw graph  -> {hit(q3)}  "
          f"({cols[0]['collapsed']} real modules collapsed)")
    if not q3:
        print(f"    it erased real modules: {real_indirection[:5]}")

    mergeable_cuts = [(a, b) for a, b, *_ in links
                      if b in raw and {x for x, y, *_ in links if y == b} == {a}]
    if mergeable_cuts:
        a, b = mergeable_cuts[0]
        mp, ml = merge_pair(parts, links, a, b)
        q4 = len(cuts(mp, ml)) < len(raw)
        print(f"Q4 merging a cut vertex reduces the count    -> {hit(q4)}  "
              f"({len(raw)} -> {len(cuts(mp, ml))}, merged {b!r} into {a!r})")
    else:
        q4 = None
        print("Q4 no cut vertex has a sole importer in this graph -> UNTESTABLE")

    # ------------------------------------------------ ARM 3: JEPA cards ----
    print("\n=== ARM 3 -- what two JEPA model cards say about collapse ===")
    card_text = {}
    for fn in sorted(os.listdir(CARDS)):
        card_text[fn] = open(os.path.join(CARDS, fn), encoding="utf-8").read().lower()
    terms_collapse = ("collapse", "collapsing")
    # PHRASES match as substrings. The ACRONYM must match on word boundaries:
    # a first version looked for "ema" as a substring and found it inside
    # "semantically", which read as the card naming the mechanism. That was a
    # defect in this instrument, not a property of the card.
    terms_mech = ("stop-gradient", "stop gradient", "stopgrad",
                  "exponential moving average", "moving average",
                  "target encoder", "target-encoder")
    acronyms = (r"\bema\b", r"\bemas\b")

    def names_mechanism(txt):
        return (any(t in txt for t in terms_mech)
                or any(re.search(a, txt) for a in acronyms))

    j1 = all(not any(t in txt for t in terms_collapse) for txt in card_text.values())
    j2 = all(not names_mechanism(txt) for txt in card_text.values())
    ijepa = next(t for f, t in card_text.items() if "ijepa" in f)
    j3 = "hand-crafted" in ijepa and "pixel-level details" in ijepa
    for fn, txt in card_text.items():
        print(f"  {fn}  ({len(txt)} chars)")
        print(f"    mentions collapse: "
              f"{any(t in txt for t in terms_collapse)}   "
              f"names the mechanism: {names_mechanism(txt)}")
    print(f"\nJ1 neither card mentions collapse        -> {hit(j1)}")
    print(f"J2 neither names the mechanism           -> {hit(j2)}")
    print(f"J3 the I-JEPA card states what it avoids -> {hit(j3)}")

    out = {
        "prereg_sha256": PREREG_SHA,
        "declared": {"modules": len(parts), "edges": len(links),
                     "cuts": sorted(raw)},
        "arm1": {"candidates": len(cands), "kinds": kinds,
                 "prose_only": len(prose),
                 "widened_cuts": sorted(wide), "lost": sorted(lost),
                 "new": sorted(new), "survived": survived,
                 "examples": cands[:40]},
        "arm2": {str(n): {k: v for k, v in cols[n].items() if k != "edges"}
                 for n in (0, 20, 40)},
        "arm2_real_indirection_nodes": real_indirection,
        "arm3": {"j1_no_collapse": j1, "j2_no_mechanism": j2,
                 "j3_states_avoidance": j3,
                 "cards": sorted(card_text)},
    }
    with open(os.path.join(HERE, "results_invisible.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("\nwrote results_invisible.json")
    return out


if __name__ == "__main__":
    main()
