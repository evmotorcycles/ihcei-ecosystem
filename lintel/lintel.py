#!/usr/bin/env python3
"""LINTEL -- which of the reported single points of failure are real.

A lintel is the beam that actually carries the load over a doorway. People
point at the frame.

WHAT THIS IS FOR
================
Dependency tools report articulation points and call them single points of
failure. The number goes on dashboards and gets compared between projects.

That number moves when somebody adds a re-export shim, splits a module in two,
or inlines a facade -- none of which change what the system depends on. So a
reported single point of failure may be a fact about file layout rather than
about fragility.

This applies a family of rewrites that preserve what-depends-on-what, and
reports which findings SURVIVE. A survivor is a finding about the system. A
casualty was a finding about the drawing.

WHAT IT DOES NOT DO
===================
    understands_code = False
    proves           = NOTHING

It reads a graph someone else built from import statements. A cut vertex is not
a fault -- a shared kernel that everything routes through is usually correct.
Survival makes a finding stable; it does not make it bad news.

"Behaviour-preserving" here means REACHABILITY-preserving in the declared import
graph. It does not mean the refactor is safe: a re-export shim can change import
time, circular-import behaviour and namespace contents. This repository broke 41
tests that way.

An edge exists only because somebody wrote an import. Dependencies reached
through a string, a registry, a subprocess or reflection are invisible here and
no rewrite can reveal them.
"""

from __future__ import annotations

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "page-code"))

from blueprint import articulation_points          # noqa: E402

UNDERSTANDS_CODE = False
PROVES = "NOTHING"

SHIM = "→shim→"          # marks a node this tool invented, not the project's
SPLIT_IN, SPLIT_OUT = "#in", "#out"


# ------------------------------------------------------------------ graph ----
def cuts(parts, links):
    """Articulation points, from the tested engine. Not reimplemented."""
    return set(articulation_points(list(parts), [tuple(e) for e in links]))


def undirected(links):
    seen = set()
    for a, b, *_ in links:
        seen.add((a, b) if a < b else (b, a))
    return seen


def bridges(parts, links):
    """Edges whose removal increases the number of pieces. Measured by removal."""
    base = pieces(parts, links)
    out = []
    for e in sorted(undirected(links)):
        kept = [l for l in links if tuple(sorted(l[:2])) != e]
        if pieces(parts, kept) > base:
            out.append(e)
    return out


def pieces(parts, links):
    adj = {p: set() for p in parts}
    for a, b, *_ in links:
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
    seen, n = set(), 0
    for s in parts:
        if s in seen:
            continue
        n += 1
        stack = [s]
        seen.add(s)
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
    return n


# --------------------------------------------------------------- rewrites ----
def insert_shim(parts, links, edge, tag=""):
    """A->B becomes A->P->B. Mirrors adding a re-export shim or barrel file.

    The edge is matched in EITHER direction. `bridges()` returns its endpoints
    sorted, and a first version of this matched only the stored direction, so
    for 36 of 67 bridges the original edge survived beside the shim and left a
    parallel route. The shim then read as no cut vertex at all, which looked
    like a finding and was a defect.
    """
    a, b = edge
    p = f"{a}{SHIM}{b}{tag}"
    new = [l for l in links
           if not ((l[0] == a and l[1] == b) or (l[0] == b and l[1] == a))]
    new += [(a, p, 1.0), (p, b, 1.0)]
    return sorted(set(parts) | {p}), sorted(set(new))


def collapse_passthrough(parts, links, node):
    """A->P->B becomes A->B, for a node with exactly one in and one out."""
    ins = [l for l in links if l[1] == node]
    outs = [l for l in links if l[0] == node]
    if len(ins) != 1 or len(outs) != 1:
        raise ValueError(f"{node!r} is not a one-in one-out pass-through")
    a, b = ins[0][0], outs[0][1]
    new = [l for l in links if l[0] != node and l[1] != node]
    if a != b:
        new.append((a, b, 1.0))
    return sorted(set(parts) - {node}), sorted(set(new))


def split_module(parts, links, node):
    """A becomes A#in -> A#out. In-edges to A#in, out-edges from A#out."""
    i, o = node + SPLIT_IN, node + SPLIT_OUT
    new = []
    for a, b, *_ in links:
        if b == node and a == node:
            continue
        if b == node:
            new.append((a, i, 1.0))
        elif a == node:
            new.append((o, b, 1.0))
        else:
            new.append((a, b, 1.0))
    new.append((i, o, 1.0))
    return sorted((set(parts) - {node}) | {i, o}), sorted(set(new))


def merge_pair(parts, links, a, b):
    """Merge B into A. Only valid when A is B's ONLY importer."""
    importers = {x for x, y, *_ in links if y == b}
    if importers != {a}:
        raise ValueError(f"{b!r} is not imported solely by {a!r}")
    new = []
    for x, y, *_ in links:
        if x == b and y == a:
            continue
        if (x, y) == (a, b):
            continue
        new.append((a if x == b else x, a if y == b else y, 1.0))
    new = [(x, y, w) for x, y, w in new if x != y]
    return sorted(set(parts) - {b}), sorted(set(new))


# ----------------------------------------------------------- the survival ----
def _origin(name):
    """Map a rewritten node back to the project module it came from."""
    if SHIM in name:
        return None                       # a node this tool invented
    for suf in (SPLIT_IN, SPLIT_OUT):
        if name.endswith(suf):
            return name[: -len(suf)]
    return name


def survivors(parts, links, rewrites, seed=0):
    """Which raw cut vertices are still cut vertices after every rewrite.

    Returns the raw set, the survivors, the casualties, and what each rewrite
    invented -- nodes that are cut vertices only because this tool added them.
    """
    raw = cuts(parts, links)
    still = set(raw)
    per = []
    invented_total = set()
    for label, fn in rewrites:
        p2, l2 = fn(parts, links)
        c2 = cuts(p2, l2)
        mapped = {o for o in (_origin(n) for n in c2) if o is not None}
        invented = {n for n in c2 if _origin(n) is None}
        invented_total |= invented
        lost = raw - mapped
        still &= mapped
        per.append({"rewrite": label, "cuts_after": len(c2),
                    "invented_nodes_that_are_cuts": len(invented),
                    "raw_cuts_lost": sorted(lost)})
    return {
        "raw_cuts": sorted(raw),
        "survivors": sorted(still),
        "casualties": sorted(raw - still),
        "invented_cut_nodes": sorted(invented_total),
        "per_rewrite": per,
    }


def report(parts, links, result):
    """Words, not a score. There is no combined number anywhere in here."""
    n_raw, n_ok = len(result["raw_cuts"]), len(result["survivors"])
    lost = n_raw - n_ok
    lines = [
        f"{len(parts)} modules, {len(links)} declared imports.",
        f"{n_raw} modules are reported as single points of failure by a plain "
        f"articulation-point reading.",
    ]
    if lost == 0:
        lines.append(
            f"All {n_ok} are still reported after every behaviour-preserving "
            "rewrite. None of them was an artefact of how the files are "
            "arranged.")
    else:
        lines.append(
            f"{n_ok} are still reported after every behaviour-preserving "
            f"rewrite. {lost} stopped being reported, and those were findings "
            "about how the files are arranged.")
    lines += [
        "",
        "The COUNT is not something to act on: inserting re-export shims that "
        "change no behaviour raises it at will, so this number cannot be "
        "compared between two projects, or against the same project last "
        "month. It partly measures how finely the code is split into files.",
        "",
        "The NAMES are stable under how the code is DRAWN -- shims, splits and "
        "merges leave the list alone. They are NOT stable under what the "
        "drawing LEAVES OUT: adding candidate undeclared edges (string "
        "dispatch, registries, subprocess calls) left 18 of 27 standing. See "
        "invisible-edges/. Read the list twice and act on the agreed part.",
        "",
        "A surviving module is not a fault. A shared kernel that everything "
        "routes through is usually correct; this says the finding is stable, "
        "not that it is bad news.",
    ]
    return "\n".join(lines)
