#!/usr/bin/env python3
"""run_audit.py — Page Code on real third-party open source, and on our products.

    python3 page-code/run_audit.py

Offline, deterministic, no network. Predictions locked in prereg_audit.md
before any package below was looked at.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

_spec = importlib.util.spec_from_file_location(
    "blueprint", os.path.join(HERE, "blueprint.py"))
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)

from keel.keel import survey   # noqa: E402

PREREG_SHA = "cb63407c02c6806c92bfb99919750bd6897db711e713a00da9cdebc32793df01"
DIST = "/usr/local/lib/python3.11/dist-packages"

THIRD_PARTY = ["pandas", "scipy", "statsmodels", "sklearn",
               "jax", "networkx", "numpy", "pygments"]

# Trig is listed DELIBERATELY. It has no code, and the audit must say so rather
# than report a project with zero of everything. That is prediction C5.
PRODUCTS = ["novora-suite", "plexus", "cairn", "trig", "novora-helm",
            "keel", "echo", "weir", "smi", "spar", "fathom", "page-code"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _pieces(parts, links):
    adj = {p: set() for p in parts}
    for a, b, *_ in links:
        if a in adj and b in adj:
            adj[a].add(b); adj[b].add(a)
    seen, n = set(), 0
    for p in parts:
        if p in seen:
            continue
        n += 1
        stack = [p]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            stack.extend(adj[u] - seen)
    return n


def audit(root, name):
    if not os.path.isdir(root):
        # ABSENT is not EMPTY. A project with no code has no structure to read,
        # and reporting zeros would say something false about a thing that is
        # not there.
        return {"name": name, "status": "ABSENT",
                "says": f"{name} has no code in this repository. There is "
                        f"nothing to read, which is not the same as a project "
                        f"with nothing in it."}
    g = bp.blueprint(root, name)
    c = g["counts"]
    row = {"name": name, "status": "READ", "counts": c}
    if c["files_scanned"]:
        row["isolated_fraction"] = round(c["files_isolated"] / c["files_scanned"], 4)
    fi = bp.fan_in(g)
    row["fan_in_top"] = fi[:5]
    parts, links = g["project"]["parts"], g["project"]["links"]
    if parts:
        # Linear-time cut vertices. spar.single_points answers the same question
        # by removal and was timed at 103.9s for n=200, so it cannot reach a
        # real library. parity_ok() shows the two agree wherever both can run.
        cuts = bp.articulation_points(parts, links)
        row["sole_routes"] = {"status": "READ",
                              "n_single_points": len(cuts),
                              "pieces": _pieces(parts, links),
                              "reader": "articulation_points (linear)"}
    else:
        row["sole_routes"] = {"status": "ABSTAINED",
                              "n_single_points": 0, "pieces": None}
    if fi:
        hub, n = fi[0]
        row["hub"] = hub
        row["hub_fan_in"] = n
        # The counted_twice survey removes each support in turn, so it is the
        # slow reader. Above 60 supports it ABSTAINS rather than being given a
        # number derived from the law instead of measured from the graph.
        if n <= 60:
            cs = survey(bp.as_claim(g, hub))
            row["hub_each_settles"] = cs.counted_twice.detail.get("each_settles")
            row["hub_counted_twice"] = cs.counted_twice.status
        else:
            row["hub_counted_twice"] = "ABSTAINED"
            row["hub_each_settles"] = None
            row["hub_abstain_reason"] = (
                f"{n} supports; this reading removes each in turn and does not "
                f"finish at that size. No number is given rather than one "
                f"derived from the law instead of measured.")
    return row


if __name__ == "__main__":
    got = sha(os.path.join(HERE, "prereg_audit.md"))
    if got != PREREG_SHA:
        raise SystemExit(f"pre-registration edited since it was locked\n"
                         f"  locked {PREREG_SHA}\n  now    {got}")

    out = {"third_party": {}, "products": {}}
    for pkg in THIRD_PARTY:
        out["third_party"][pkg] = audit(os.path.join(DIST, pkg), pkg)
    for prod in PRODUCTS:
        out["products"][prod] = audit(os.path.join(ROOT, prod), prod)

    tp = [r for r in out["third_party"].values() if r["status"] == "READ"]
    fr = [r["isolated_fraction"] for r in tp]
    out["_summary"] = {
        "third_party_n": len(tp),
        "median_isolated_fraction": round(statistics.median(fr), 4),
        "this_repo_isolated_fraction": 0.6833,
        "max_third_party_fan_in": max(r.get("hub_fan_in", 0) for r in tp),
        "this_repo_fan_in": 22,
        "all_have_single_point": all(
            r["sole_routes"]["n_single_points"] >= 1 for r in tp),
        "products_with_zero_edges": sorted(
            k for k, r in out["products"].items()
            if r["status"] == "READ" and r["counts"]["edges"] == 0),
        "products_absent": sorted(k for k, r in out["products"].items()
                                  if r["status"] == "ABSENT"),
    }
    out["_prereg"] = {"file": "page-code/prereg_audit.md", "sha256": got}
    json.dump(out, open(os.path.join(HERE, "results_audit.json"), "w"),
              indent=1, sort_keys=True)

    print(json.dumps(out["_summary"], indent=1))
    print("\n── third-party open source ──")
    print(f"{'package':14s} {'files':>6s} {'graph':>6s} {'iso':>6s} {'isoF':>6s} "
          f"{'edges':>6s} {'cuts':>5s} {'hub fan-in'}")
    for k, r in out["third_party"].items():
        c = r["counts"]
        print(f"{k:14s} {c['files_scanned']:6d} {c['files_in_graph']:6d} "
              f"{c['files_isolated']:6d} {r['isolated_fraction']:6.3f} "
              f"{c['edges']:6d} {r['sole_routes']['n_single_points']:5d} "
              f"{r.get('hub_fan_in','-')}")
    print("\n── our products ──")
    for k, r in out["products"].items():
        if r["status"] == "ABSENT":
            print(f"{k:14s} ABSENT — {r['says'][:60]}")
        else:
            c = r["counts"]
            print(f"{k:14s} {c['files_scanned']:4d} files  {c['edges']:4d} edges  "
                  f"iso {r.get('isolated_fraction', 0):.2f}  "
                  f"cuts {r['sole_routes']['n_single_points']}  "
                  f"hub {r.get('hub','-')} ({r.get('hub_fan_in','-')})")
