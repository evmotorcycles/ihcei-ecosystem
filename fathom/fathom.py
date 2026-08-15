#!/usr/bin/env python3
"""fathom.py -- how deep does this actually go? Take a sounding.

    python3 fathom/fathom.py

To fathom is to drop a line and find the depth rather than judge it from the
surface. FATHOM answers the one question SPAR provably cannot:

    IF ANY SINGLE SOURCE TURNED OUT TO BE WRONG, HOW MUCH WOULD BE LEFT?

WHY THIS TOOL EXISTS
SPAR measures route redundancy, and while building it we established that route
redundancy is NOT evidential independence -- it gets the sign backwards, because
independent sources form a tree and a shared origin closes a cycle:

    A and B share one origin  (NOT independent)   highest link 0.75
    A and B separate sources  (INDEPENDENT)       highest link 1.00

That null is on the record in spar/README.md. It leaves a real gap, and this
fills it the only way that worked anywhere else in this stack: BY REMOVAL. Not by
a formula that could be argued with -- take the source out, recompute, and report
what fell over.

WHAT IS MEASURED
Sources are the places a conclusion's support enters from. Contract them all into
one ground and the conclusion's support is the effective CONDUCTANCE between the
conclusion and that ground:

    support = 1 / R(conclusion, ground)

Then leave each source out in turn:

    dependence(s) = 1 - support_without_s / support_with_all

    dependence = 1.00   remove that one source and NOTHING is left. The whole
                        conclusion was resting on it.
    dependence = 0.31   removing it costs about a third of the support. The rest
                        stands on its own.

The deepest single dependence is the sounding: the depth to which this
conclusion rests on one thread.

WHAT THIS IS NOT
It is not a measure of whether the sources are TRUE, or of whether they are
really independent in the world. Two sources entered as separate are treated as
separate; if they secretly share an origin and you did not say so, FATHOM will
report robustness that is not there. It measures the structure you described.
Every tool in this stack has this boundary and it is the one most worth stating
twice.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from smi.lmd import laplacian_from_edges, mesh_metric  # noqa: E402

#: at or above this, a conclusion collapses when one source is withdrawn
ONE_THREAD = 0.999


class Claim:
    """A conclusion, the sources it draws on, and the links between."""

    def __init__(self, conclusion, sources, links):
        self.conclusion = conclusion
        self.sources = list(sources)
        if conclusion in self.sources:
            raise ValueError("the conclusion cannot also be one of its own sources")
        if len(self.sources) != len(set(self.sources)):
            raise ValueError("a source is listed twice")
        self.links = []
        names = {conclusion} | set(self.sources)
        for a, b, w in links:
            if a == b:
                raise ValueError(f"a step cannot depend on itself: {a!r}")
            if float(w) <= 0:
                raise ValueError(f"link {a!r}->{b!r} has weight {w}; leave it out "
                                 "rather than weighting it zero")
            self.links.append((a, b, float(w)))
            names |= {a, b}
        self.nodes = sorted(names)
        if not self.sources:
            raise ValueError("a claim with no sources cannot be sounded")


GROUND = "\x00ground"


def _support(claim, drop=None):
    """Effective conductance between the conclusion and all sources at once.

    The sources are CONTRACTED into a single ground. Contraction is what makes
    this a question about sources rather than about routes: it stops asking
    "is there another way round this link" and starts asking "is there another
    way in".
    """
    keep_src = [s for s in claim.sources if s != drop]
    if not keep_src:
        return 0.0
    live = [(a, b, w) for a, b, w in claim.links if a != drop and b != drop]

    def relabel(x):
        return GROUND if x in keep_src else x

    merged = {}
    for a, b, w in live:
        ra, rb = relabel(a), relabel(b)
        if ra == rb:
            continue                      # a link between two sources is inside
        key = (ra, rb) if ra < rb else (rb, ra)   # the ground once contracted
        merged[key] = merged.get(key, 0.0) + w

    if not merged:
        return 0.0
    names = sorted({n for pair in merged for n in pair})
    if claim.conclusion not in names or GROUND not in names:
        return 0.0
    idx = {n: i for i, n in enumerate(names)}
    L = laplacian_from_edges(len(names),
                             [(idx[a], idx[b], w) for (a, b), w in merged.items()])
    D, _, dead = mesh_metric(L)
    if dead:
        return 0.0
    R = float(D[idx[claim.conclusion]][idx[GROUND]]) ** 2
    if not np.isfinite(R) or R <= 0:
        return 0.0
    return 1.0 / R


def sound(claim):
    """Drop the line. Returns each source's dependence and the deepest one."""
    base = _support(claim)
    rows = []
    for s in claim.sources:
        without = _support(claim, drop=s)
        dep = 1.0 - (without / base) if base > 0 else 1.0
        rows.append({
            "source": s,
            "support_without_it": without,
            "dependence": dep,
            "carries_it_alone": bool(dep >= ONE_THREAD),
        })
    rows.sort(key=lambda r: -r["dependence"])
    deepest = rows[0] if rows else None
    return {
        "conclusion": claim.conclusion,
        "sources": len(claim.sources),
        "support": base,
        "by_source": rows,
        "deepest_dependence": deepest["dependence"] if deepest else 1.0,
        "rests_on_one_thread": bool(deepest and deepest["carries_it_alone"]),
        # what is actually left after the worst single loss. Stating this rather
        # than a second threshold: "survives losing any one" is true at 97.8%
        # dependence and thoroughly misleading, and the honest fix is the number,
        # not another tunable.
        "remaining_after_worst_loss": (1.0 - deepest["dependence"]) if deepest else 0.0,
    }


# ------------------------------------------------------------------ demo ----
SHARED = Claim("The claim", ["Common origin"],
               [("The claim", "Account A", 1.0), ("The claim", "Account B", 1.0),
                ("Account A", "Common origin", 1.0),
                ("Account B", "Common origin", 1.0)])

SEPARATE = Claim("The claim", ["Source 1", "Source 2"],
                 [("The claim", "Account A", 1.0), ("The claim", "Account B", 1.0),
                  ("Account A", "Source 1", 1.0), ("Account B", "Source 2", 1.0)])

THREE = Claim("The claim", ["Source 1", "Source 2", "Source 3"],
              [("The claim", "A", 1.0), ("The claim", "B", 1.0), ("The claim", "C", 1.0),
               ("A", "Source 1", 1.0), ("B", "Source 2", 1.0), ("C", "Source 3", 1.0)])

LOPSIDED = Claim("The claim", ["Main study", "A blog post"],
                 [("The claim", "Main study", 9.0), ("The claim", "A blog post", 0.2)])


def report(name, claim):
    r = sound(claim)
    print(f"\n  {name}")
    print(f"  {'-' * 64}")
    for row in r["by_source"]:
        bar = "#" * int(round(row["dependence"] * 24))
        note = "  <- carries it alone" if row["carries_it_alone"] else ""
        print(f"    lose {row['source']:<22}{row['dependence']:>7.1%}  {bar}{note}")
    print(f"    {'sounding':<27}{r['deepest_dependence']:>7.1%}"
          f"   {r['remaining_after_worst_loss']:.1%} of the support would remain")
    return r


def main():
    print("=" * 72)
    print("  FATHOM — if any single source turned out to be wrong,")
    print("           how much would be left?")
    print("=" * 72)
    print("\n  support = 1 / R(conclusion, all sources contracted to one ground)")
    print("  dependence(s) = 1 - support without s / support with all")

    a = report("Two accounts that trace to ONE origin", SHARED)
    b = report("Two accounts with SEPARATE sources", SEPARATE)
    c = report("Three separate sources", THREE)
    d = report("A study and a blog post", LOPSIDED)

    print("\n  THE GAP THIS FILLS")
    print("    SPAR reads route redundancy, and gets evidential independence")
    print("    BACKWARDS -- the independent structure looks the more fragile:")
    print("      shared origin  (not independent)  SPAR highest link 0.75")
    print("      separate       (independent)      SPAR highest link 1.00")
    print("    Sounding by removal reads them the right way round:")
    print(f"      shared origin  (not independent)  FATHOM {a['deepest_dependence']:.0%}")
    print(f"      separate       (independent)      FATHOM {b['deepest_dependence']:.0%}")
    print("    The two tools answer different questions and disagree on purpose.")

    out = {
        "shared_origin": {"deepest_dependence": a["deepest_dependence"],
                          "rests_on_one_thread": a["rests_on_one_thread"]},
        "separate_sources": {"deepest_dependence": b["deepest_dependence"],
                             "rests_on_one_thread": b["rests_on_one_thread"]},
        "three_sources": {"deepest_dependence": c["deepest_dependence"]},
        "lopsided": {"deepest_dependence": d["deepest_dependence"],
                     "by_source": d["by_source"]},
    }
    json.dump(out, open(os.path.join(HERE, "results_fathom.json"), "w",
                        encoding="utf-8"), indent=2)
    print("\n  wrote fathom/results_fathom.json\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
