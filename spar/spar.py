#!/usr/bin/env python3
"""spar.py -- which parts of a structure carry it, and which are ceremony.

    python3 spar/spar.py

A spar is the member that carries the load. Everything else on a rig is fittings.
This tells you, for any structure of dependent steps, which links are spars.

THE ONE NUMBER
--------------
For a link between i and j with weight w, on the graph of what depends on what:

    bearing = w * R_ij        where R_ij is the effective resistance

and that quantity is EXACTLY the probability that the link appears in a random
spanning tree of the structure -- which is to say, exactly how often the link is
genuinely the thing holding the structure together rather than one of several
interchangeable routes.

    bearing = 1.00   there is NO other route. Remove this link and the structure
                     falls into two pieces. It is a single point of failure.
    bearing = 0.29   there are other ways through. 71% of the time this link is
                     not the one carrying anything.

A NULL, FOUND WHILE BUILDING THIS AND KEPT
------------------------------------------
The obvious next claim -- that this measures whether evidence is genuinely
corroborated -- IS FALSE, and it was written into an earlier version of this
file before being checked:

    A and B share one origin      (NOT independent)  highest link 0.75
    A and B have separate sources (INDEPENDENT)      highest link 1.00

The genuinely independent structure reads as the MORE fragile one. Independent
sources form a tree; a shared origin closes a cycle; and this measures cycles.
ROUTE REDUNDANCY IS NOT EVIDENTIAL INDEPENDENCE, and any product built on the
assumption that it is would have had the sign backwards. Recorded in
test_spar.py so nobody re-derives the mistake.

This is verified in test_spar.py against brute-force enumeration of every
spanning tree, on weighted graphs, not taken from a textbook.

WHY THIS IS NOT A SCORE
-----------------------
Every "criticality score" in every dashboard is a formula somebody chose, with
weights somebody tuned, which somebody else can argue with. This is not that.

  1. CONSERVED.  Foster's theorem: the bearings of all links sum to exactly
     n - k, where n is the number of steps and k the number of separate pieces.
     Not normalised to sum to something. It comes out that way.

  2. PARAMETER-FREE.  There is nothing to tune. No thresholds, no priors, no
     model. Two people running it on the same structure get the same numbers.

  3. UNGAMEABLE BY SCALE.  Multiply every weight in the structure by any factor
     and every bearing is unchanged, to machine precision -- because w -> Jw and
     R -> R/J. Nobody can inflate their own importance by insisting everything
     they touch is very important.

  4. OBFUSCATION IS VISIBLE.  Adding steps raises the conserved total, because
     the total IS n - k. A process that carried 9.00 last quarter and carries
     14.00 now, for the same outcome, has had five steps' worth of structure
     added to it, and the number says so without anybody having to allege it.

THE LIMITATION, STATED PLAINLY
------------------------------
On a pure TREE -- a structure with no alternative routes anywhere -- every link
is a bridge and every bearing is exactly 1.000. SPAR cannot rank the steps of a
tree, and any tool claiming to would be inventing the ranking.

That reading is not a failure to say something. It says: NO STEP IN THIS
STRUCTURE HAS AN ALTERNATIVE ROUTE. EVERY ONE OF THEM IS A SINGLE POINT OF
FAILURE, AND NOTHING HERE IS CHECKED AGAINST ANYTHING ELSE. For a bill, a
benefits decision or a chain of custody, that is the finding, not the absence
of one.

SPAR is informative about *ranking* exactly where redundancy exists, and
informative about *fragility* everywhere.

WHAT THIS IS NOT
----------------
It is not a measure of importance, quality, blame, or cost. It measures one
thing: whether a link is structurally unavoidable. A step can be indispensable
and useless -- a required form that changes no outcome reads 1.00, because
removing it does disconnect the process. That is a true statement about the
structure and a claim about nothing else. See SCOPE.md.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smi.lmd import laplacian_from_edges, mesh_metric  # noqa: E402

#: below this bearing a link is doing almost nothing structural. Not a gate --
#: nothing is decided by it -- only the point at which the report says so in
#: words as well as in a number.
CEREMONY_BELOW = 0.25

#: a link at or above this is unavoidable: no other route exists.
SPAR_ABOVE = 0.999


class Structure:
    """A set of steps and the links between them."""

    def __init__(self, steps, links):
        """steps: list of names. links: (from, to, weight) using names."""
        self.steps = list(steps)
        seen = set()
        for s in self.steps:
            if s in seen:
                raise ValueError(f"two steps are both called {s!r}")
            seen.add(s)
        self.links = []
        for a, b, w in links:
            if a not in seen or b not in seen:
                raise ValueError(f"link {a!r}->{b!r} names a step that does not exist")
            if a == b:
                raise ValueError(f"a step cannot depend on itself: {a!r}")
            if float(w) <= 0:
                raise ValueError(f"link {a!r}->{b!r} has weight {w}; a link that is "
                                 "not there should be left out, not weighted zero")
            self.links.append((a, b, float(w)))

    def index(self, name):
        return self.steps.index(name)

    def laplacian(self):
        return laplacian_from_edges(
            len(self.steps),
            [(self.index(a), self.index(b), w) for a, b, w in self.links])


def bearings(structure):
    """The load each link is carrying, as a probability.

    Returns a list of dicts, heaviest first, plus the conserved total.
    """
    n = len(structure.steps)
    if not structure.links:
        return {"links": [], "total": 0.0, "expected_total": 0.0, "pieces": n,
                "steps": n, "conserved": True, "dead": True}

    D, labels, dead = mesh_metric(structure.laplacian())
    pieces = int(labels.max()) + 1

    rows = []
    total = 0.0
    for a, b, w in structure.links:
        i, j = structure.index(a), structure.index(b)
        d = float(D[i][j])
        if not math.isfinite(d):
            # cannot happen: a link IS a path. Guard anyway rather than
            # silently reporting a bearing of nan.
            raise RuntimeError(f"link {a}->{b} came back at infinite distance")
        R = d * d
        bearing = w * R
        total += bearing
        rows.append({
            "from": a, "to": b, "weight": w, "resistance": R,
            "bearing": bearing,
            "redundancy": 1.0 - bearing,
            "sole_route": bool(bearing >= SPAR_ABOVE),
            "verdict": ("no alternative route" if bearing >= SPAR_ABOVE else
                        "mostly redundant" if bearing < CEREMONY_BELOW else
                        "one of several routes"),
        })

    rows.sort(key=lambda r: -r["bearing"])
    expected = n - pieces
    return {
        "links": rows,
        "total": total,
        "expected_total": float(expected),
        "conserved": abs(total - expected) < 1e-9,
        "pieces": pieces,
        "steps": n,
        "dead": bool(dead),
    }


def single_points(structure):
    """The PARTS whose removal breaks the structure into more pieces.

    A link's bearing answers "is there another way round this connection". It
    does not answer the question a person actually asks about evidence, which is
    "does all of this rest on one thing". Two accounts that both trace back to
    the same origin sit in a perfectly good cycle -- no link is a bridge -- and
    are still not two accounts. The origin is an articulation point, and that is
    the finding.

    Computed by removal, not by a formula: take each part out and count the
    pieces left behind.
    """
    n = len(structure.steps)
    if n < 3 or not structure.links:
        return []
    base = bearings(structure)["pieces"]
    out = []
    for name in structure.steps:
        rest = [s for s in structure.steps if s != name]
        links = [(a, b, w) for a, b, w in structure.links if a != name and b != name]
        # NOT `if not links: continue` -- a part whose removal leaves no links at
        # all is the most complete break there is, and skipping it was hiding
        # exactly the hubs this function exists to find.
        after = bearings(Structure(rest, links))["pieces"]
        # removing an isolated part cannot break anything; removing a leaf
        # leaves one fewer part and the same number of pieces
        if after > base:
            out.append({"part": name, "pieces_after": after})
    return out


def scaled(structure, factor):
    """The same structure with every weight multiplied. Bearings must not move."""
    return Structure(structure.steps,
                     [(a, b, w * factor) for a, b, w in structure.links])


# ------------------------------------------------------------------ demo ----
INVOICE = Structure(
    ["Meter reading", "Unit rate", "Standing charge", "Subtotal",
     "VAT", "Late fee", "Amount due"],
    [("Meter reading", "Subtotal", 8.0),
     ("Unit rate", "Subtotal", 8.0),
     ("Standing charge", "Subtotal", 3.0),
     ("Subtotal", "VAT", 6.0),
     ("Subtotal", "Amount due", 6.0),
     ("VAT", "Amount due", 6.0),
     ("Late fee", "Amount due", 0.4)])

COMPLAINT = Structure(
    ["Complaint filed", "Acknowledgement", "Triage", "Team A review",
     "Team B review", "Manager sign-off", "Outcome letter"],
    [("Complaint filed", "Acknowledgement", 5.0),
     ("Acknowledgement", "Triage", 5.0),
     ("Triage", "Team A review", 4.0),
     ("Triage", "Team B review", 4.0),
     ("Team A review", "Manager sign-off", 4.0),
     ("Team B review", "Manager sign-off", 4.0),
     ("Manager sign-off", "Outcome letter", 5.0)])


def report(name, structure):
    r = bearings(structure)
    print(f"\n  {name}")
    print(f"  {'-' * 68}")
    print(f"  {'link':<44}{'carries':>10}{'':>4}")
    for row in r["links"]:
        bar = "#" * int(round(row["bearing"] * 20))
        link = f"{row['from']} -> {row['to']}"
        print(f"  {link:<44}{row['bearing']:>9.3f}  {bar}")
    print(f"  {'-' * 68}")
    print(f"  total {r['total']:.6f}   steps {r['steps']} - pieces {r['pieces']} "
          f"= {r['expected_total']:.0f}   conserved: {r['conserved']}")
    sp = single_points(structure)
    if sp:
        print("  parts everything passes through: " +
              ", ".join(f"{x['part']} (-> {x['pieces_after']} pieces)" for x in sp))
    sole = [x for x in r["links"] if x["sole_route"]]
    red = [x for x in r["links"] if x["bearing"] < CEREMONY_BELOW]
    print(f"  single points of failure: {len(sole)} of {len(r['links'])} links")
    if len(sole) == len(r["links"]):
        print("  -> nothing here is checked against anything else.")
    if red:
        print("  mostly redundant: " +
              ", ".join(f"{x['from']}->{x['to']} ({x['bearing']:.0%})" for x in red))
    return r


CORROBORATION = [
    ("one source, relayed",
     Structure(["Claim", "Report", "Witness"],
               [("Claim", "Report", 1.0), ("Report", "Witness", 1.0)])),
    ("two witnesses who share a source",
     Structure(["Claim", "Witness A", "Witness B", "Common origin"],
               [("Claim", "Witness A", 1.0), ("Claim", "Witness B", 1.0),
                ("Witness A", "Common origin", 1.0),
                ("Witness B", "Common origin", 1.0)])),
    ("three genuinely separate routes",
     Structure(["Claim", "Route 1", "Route 2", "Route 3"],
               [("Claim", "Route 1", 1.0), ("Claim", "Route 2", 1.0),
                ("Claim", "Route 3", 1.0), ("Route 1", "Route 2", 1.0),
                ("Route 2", "Route 3", 1.0), ("Route 1", "Route 3", 1.0)])),
]


def main():
    print("=" * 72)
    print("  SPAR — which parts of a structure carry it")
    print("=" * 72)
    print("\n  bearing = weight x effective resistance")
    print("          = P(this link is in a random spanning tree)")
    print("          = how often the link is the thing holding the structure up")

    a = report("A UTILITY BILL", INVOICE)
    b = report("A COMPLAINTS PROCESS", COMPLAINT)

    print("\n  SCALE CANNOT MOVE IT")
    base = bearings(INVOICE)["links"]
    for f in (0.001, 1000.0):
        got = bearings(scaled(INVOICE, f))["links"]
        worst = max(abs(x["bearing"] - y["bearing"]) for x, y in zip(base, got))
        print(f"    every weight x {f:<9g}  worst bearing change {worst:.2e}")
    print("    Insisting everything you touch is very important changes nothing.")

    print("\n  DOES IT REST ON ONE THREAD?")
    for name, st in CORROBORATION:
        rr = bearings(st)
        top = max(x["bearing"] for x in rr["links"])
        sole = sum(1 for x in rr["links"] if x["sole_route"])
        print(f"    {name:<36} highest link {top:.3f}   "
              f"no alternative: {sole}/{len(rr['links'])}")
    print("    Two witnesses who were standing together do not read as two.")

    print("\n  ADDING STEPS IS VISIBLE")
    padded = Structure(
        COMPLAINT.steps + ["Compliance check", "Second sign-off"],
        [l for l in COMPLAINT.links if l[:2] != ("Manager sign-off", "Outcome letter")] +
        [("Manager sign-off", "Compliance check", 5.0),
         ("Compliance check", "Second sign-off", 5.0),
         ("Second sign-off", "Outcome letter", 5.0)])
    p = bearings(padded)
    print(f"    before: {b['steps']} steps, total {b['total']:.2f}")
    print(f"    after : {p['steps']} steps, total {p['total']:.2f}   "
          f"(+{p['total'] - b['total']:.2f} for the same outcome)")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
