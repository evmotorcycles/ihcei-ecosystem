#!/usr/bin/env python3
"""run_yeast.py — the real yeast interactome, and its actual cut vertices.

    python3 yeast-audit/run_yeast.py

Offline. Predictions locked in prereg_yeast.md before the graph was built.
Cut vertices come from page-code/blueprint.py's articulation_points, which is
parity-checked against the tested spar engine on every graph small enough to
run both.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

_s = importlib.util.spec_from_file_location(
    "bp", os.path.join(ROOT, "page-code", "blueprint.py"))
bp = importlib.util.module_from_spec(_s)
_s.loader.exec_module(bp)

PREREG_SHA = "f8134f12f5223e736ce4c1dc3a76528d904c148d7f907039131c72e0ab1623d6"
STRING_GZ = os.path.join(ROOT, "repro", "data",
                         "4932.protein.physical.links.v12.0.csv.gz")
THRESHOLD = 400


def load_edges():
    """Same construction as biomedical-agency/build_yeast_features.py:
    STRING v12 physical links, combined_score >= 400, undirected, deduped."""
    edges, nodes = set(), set()
    with gzip.open(STRING_GZ, "rt") as fh:
        header = fh.readline().split()
        i_a, i_b, i_s = 0, 1, len(header) - 1
        for line in fh:
            f = line.split()
            if len(f) < 3:
                continue
            try:
                score = int(f[i_s])
            except ValueError:
                continue
            if score < THRESHOLD:
                continue
            a, b = f[i_a], f[i_b]
            if a == b:
                continue
            edges.add((a, b) if a < b else (b, a))
            nodes.add(a)
            nodes.add(b)
    return sorted(nodes), sorted(edges)


def components(parts, links):
    adj = {p: set() for p in parts}
    for a, b in links:
        adj[a].add(b)
        adj[b].add(a)
    seen, comps = set(), []
    for p in parts:
        if p in seen:
            continue
        stack, comp = [p], []
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            comp.append(u)
            stack.extend(adj[u] - seen)
        comps.append(comp)
    return sorted(comps, key=len, reverse=True)


def main():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_yeast.md"), "rb")
                         .read()).hexdigest()
    if got != PREREG_SHA:
        raise SystemExit(f"pre-registration edited\n locked {PREREG_SHA}\n now {got}")

    nodes, edges = load_edges()
    links = [(a, b, 1.0) for a, b in edges]
    cuts = bp.articulation_points(nodes, links)
    comps = components(nodes, edges)
    big = set(comps[0])
    big_edges = [(a, b, 1.0) for a, b in edges if a in big and b in big]
    big_cuts = bp.articulation_points(sorted(big), big_edges)

    deg = {}
    for a, b in edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    leaves = [n for n in nodes if deg.get(n, 0) == 1]

    out = {
        "source": "STRING v12 physical links, S. cerevisiae taxon 4932, "
                  f"combined_score >= {THRESHOLD}",
        "raw_sha256": hashlib.sha256(open(STRING_GZ, "rb").read()).hexdigest(),
        "n_nodes": len(nodes),
        "n_edges": len(edges),
        "n_cut_vertices": len(cuts),
        "n_pieces": len(comps),
        "largest_component": len(comps[0]),
        "cut_vertices_in_largest_component": len(big_cuts),
        "degree_one_nodes": len(leaves),
        "claimed_by_the_pasted_audit": {"n_edges": 15400, "n_cut_vertices": 0},
        "findings": {
            "Y1_many_cut_vertices": len(cuts) >= 100,
            "Y2_edge_count": len(edges),
            "Y3_more_than_one_piece": len(comps) >= 2,
            "Y4_largest_component_has_cuts": len(big_cuts) >= 1,
        },
        "_prereg": {"file": "yeast-audit/prereg_yeast.md", "sha256": got},
    }
    json.dump(out, open(os.path.join(HERE, "results_yeast.json"), "w"),
              indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in out.items() if k != "raw_sha256"}, indent=1))


if __name__ == "__main__":
    main()
