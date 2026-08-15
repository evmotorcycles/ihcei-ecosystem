#!/usr/bin/env python3
"""The claim SPAR makes is exact, so the tests are exact.

    python3 -m pytest -q spar/test_spar.py

The central claim -- bearing = P(the link is in a random spanning tree) -- is
NOT taken from the literature here. It is checked against brute-force
enumeration of every spanning tree, on weighted graphs, where the two
computations share no code.
"""
from __future__ import annotations

import itertools
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from spar.spar import (CEREMONY_BELOW, SPAR_ABOVE, Structure,  # noqa: E402
                       bearings, scaled)

TOL = 1e-9


def struct(n, edges):
    names = [f"s{i}" for i in range(n)]
    return Structure(names, [(names[i], names[j], w) for i, j, w in edges])


GRAPHS = [
    ("triangle", 3, [(0, 1, 1.), (1, 2, 1.), (0, 2, 1.)]),
    ("path of 5", 5, [(k, k + 1, 1.) for k in range(4)]),
    ("ring of 6", 6, [(i, (i + 1) % 6, 1.) for i in range(6)]),
    ("star of 7", 7, [(0, k, 1.) for k in range(1, 7)]),
    ("K5", 5, [(i, j, 1.) for i in range(5) for j in range(i + 1, 5)]),
    ("weighted mix", 5, [(0, 1, 3.7), (1, 2, 0.4), (2, 3, 9.1),
                         (3, 4, 0.05), (0, 4, 2.2), (1, 3, 1.3)]),
    ("kite", 4, [(0, 1, 1.), (1, 2, 1.), (0, 2, 1.), (2, 3, 1.)]),
    ("wide weights", 4, [(0, 1, 1e-3), (1, 2, 1e3), (0, 2, 1.), (2, 3, 5.)]),
    ("two pieces", 6, [(0, 1, 1.), (1, 2, 2.), (3, 4, 1.), (4, 5, 5.)]),
    ("three pieces", 7, [(0, 1, 2.), (2, 3, 1.), (3, 4, 1.), (5, 6, 4.)]),
    ("invoice", 5, [(0, 2, 4.), (1, 2, 4.), (2, 3, 8.), (2, 4, 8.)]),
]


# ------------------------------------------------- the claim, checked hard --
def _spanning_trees(n, edges):
    """Every spanning tree, with its weight product. Shares no code with SPAR."""
    out = []
    for combo in itertools.combinations(range(len(edges)), n - 1):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        ok = True
        for c in combo:
            i, j, _ = edges[c]
            a, b = find(i), find(j)
            if a == b:
                ok = False
                break
            parent[a] = b
        if ok:
            wt = 1.0
            for c in combo:
                wt *= edges[c][2]
            out.append((set(combo), wt))
    return out


@pytest.mark.parametrize("name,n,edges", [g for g in GRAPHS if g[1] <= 5])
def test_bearing_is_the_probability_the_link_is_in_a_spanning_tree(name, n, edges):
    """The whole product rests on this. Two independent computations."""
    trees = _spanning_trees(n, edges)
    if not trees:
        pytest.skip(f"{name} is disconnected; no spanning tree exists")
    Z = sum(w for _, w in trees)
    r = bearings(struct(n, edges))
    by_pair = {(min(x["from"], x["to"]), max(x["from"], x["to"])): x["bearing"]
               for x in r["links"]}
    for c, (i, j, _) in enumerate(edges):
        key = (min(f"s{i}", f"s{j}"), max(f"s{i}", f"s{j}"))
        enumerated = sum(w for s, w in trees if c in s) / Z
        assert abs(by_pair[key] - enumerated) < TOL, \
            f"{name} link {i}-{j}: SPAR says {by_pair[key]:.9f}, " \
            f"counting every tree says {enumerated:.9f}"


# ------------------------------------------------------------ conservation --
@pytest.mark.parametrize("name,n,edges", GRAPHS)
def test_the_total_is_conserved_at_steps_minus_pieces(name, n, edges):
    """Foster's theorem. Not a normalisation -- it comes out that way, which is
    why nobody can argue with the allocation."""
    r = bearings(struct(n, edges))
    assert abs(r["total"] - (n - r["pieces"])) < TOL, \
        f"{name}: total {r['total']:.12f}, steps {n} - pieces {r['pieces']}"
    assert r["conserved"]


def test_the_total_counts_the_pieces():
    """The conserved total is n - k, so it reveals a broken structure without
    being asked. Otherwise the parametrised test above could be vacuous."""
    whole = bearings(struct(6, [(0, 1, 1.), (1, 2, 1.), (2, 3, 1.),
                                (3, 4, 1.), (4, 5, 1.)]))
    split = bearings(struct(6, [(0, 1, 1.), (1, 2, 1.), (3, 4, 1.), (4, 5, 1.)]))
    assert whole["pieces"] == 1 and abs(whole["total"] - 5.0) < TOL
    assert split["pieces"] == 2 and abs(split["total"] - 4.0) < TOL


# ------------------------------------------------------- ungameable by scale --
@pytest.mark.parametrize("factor", [1e-6, 0.01, 7.0, 1e3, 1e6])
def test_multiplying_every_weight_changes_nothing(factor):
    """Insisting that everything you touch is very important must not move a
    single number. w -> Jw and R -> R/J, so w*R is untouched."""
    s = struct(5, [(0, 1, 3.7), (1, 2, 0.4), (2, 3, 9.1), (0, 3, 2.2), (1, 3, 1.3)])
    base = {(x["from"], x["to"]): x["bearing"] for x in bearings(s)["links"]}
    got = {(x["from"], x["to"]): x["bearing"] for x in bearings(scaled(s, factor))["links"]}
    worst = max(abs(base[k] - got[k]) for k in base)
    assert worst < 1e-12, f"scaling by {factor} moved a bearing by {worst:.2e}"


def test_changing_one_weight_does_move_things():
    """Otherwise the scale-invariance tests are passing on a constant."""
    s = struct(4, [(0, 1, 1.), (1, 2, 1.), (0, 2, 1.), (2, 3, 1.)])
    before = {(x["from"], x["to"]): x["bearing"] for x in bearings(s)["links"]}
    t = struct(4, [(0, 1, 50.), (1, 2, 1.), (0, 2, 1.), (2, 3, 1.)])
    after = {(x["from"], x["to"]): x["bearing"] for x in bearings(t)["links"]}
    assert max(abs(before[k] - after[k]) for k in before) > 0.1, \
        "raising one weight fiftyfold changed nothing; the measure is inert"


# --------------------------------------------------- what it says, in words --
def test_a_link_with_no_alternative_reads_exactly_one():
    """A bridge. Remove it and the structure is in two pieces."""
    r = bearings(struct(4, [(0, 1, 1.), (1, 2, 1.), (0, 2, 1.), (2, 3, 9.9)]))
    bridge = [x for x in r["links"] if {x["from"], x["to"]} == {"s2", "s3"}][0]
    assert abs(bridge["bearing"] - 1.0) < TOL
    assert bridge["sole_route"]
    for x in r["links"]:
        if {x["from"], x["to"]} != {"s2", "s3"}:
            assert not x["sole_route"], "a link inside a cycle has alternatives"


def test_every_link_of_a_tree_reads_one_and_that_is_the_finding():
    """The declared limitation. SPAR cannot rank the steps of a tree -- and any
    tool that claimed to would be inventing the ranking. What it says instead
    is that nothing in the structure is checked against anything else."""
    r = bearings(struct(6, [(0, 1, 3.), (1, 2, 0.2), (2, 3, 88.), (1, 4, 5.), (4, 5, 1.)]))
    assert all(abs(x["bearing"] - 1.0) < TOL for x in r["links"])
    assert all(x["sole_route"] for x in r["links"])
    assert abs(r["total"] - 5.0) < TOL


def test_adding_a_second_route_lowers_the_first_one():
    """The direction has to be right, or the number means the opposite."""
    one = bearings(struct(3, [(0, 1, 1.), (1, 2, 1.)]))
    both = bearings(struct(3, [(0, 1, 1.), (1, 2, 1.), (0, 2, 1.)]))
    a = [x for x in one["links"] if {x["from"], x["to"]} == {"s0", "s1"}][0]
    b = [x for x in both["links"] if {x["from"], x["to"]} == {"s0", "s1"}][0]
    assert abs(a["bearing"] - 1.0) < TOL
    assert b["bearing"] < a["bearing"] - 0.2, \
        "adding an alternative route did not reduce the original's load"


def test_route_redundancy_is_NOT_evidential_independence():
    """A null, found while building this, and the reason the product is scoped
    the way it is.

    The tempting claim is that this measures whether a conclusion is genuinely
    corroborated. It does not, and it gets the sign BACKWARDS:

        A and B share one origin      (NOT independent)  highest link 0.75
        A and B have separate sources (INDEPENDENT)      highest link 1.00

    Independent sources form a tree; a shared origin closes a cycle; this
    measures cycles. An earlier version of spar.py asserted the opposite in its
    own docstring. This test exists so nobody re-derives the mistake.
    """
    shared = bearings(Structure(
        ["Claim", "A", "B", "Common origin"],
        [("Claim", "A", 1.0), ("Claim", "B", 1.0),
         ("A", "Common origin", 1.0), ("B", "Common origin", 1.0)]))
    separate = bearings(Structure(
        ["Claim", "A", "B", "Source 1", "Source 2"],
        [("Claim", "A", 1.0), ("Claim", "B", 1.0),
         ("A", "Source 1", 1.0), ("B", "Source 2", 1.0)]))
    top_shared = max(x["bearing"] for x in shared["links"])
    top_separate = max(x["bearing"] for x in separate["links"])
    assert top_separate > top_shared, \
        "the null has changed: check whether the interpretation now holds"
    assert abs(top_separate - 1.0) < TOL
    assert all(x["sole_route"] for x in separate["links"]), \
        "independent sources form a tree, so every link reads as sole route"


def test_a_part_everything_passes_through_is_found_by_removal():
    """What a link's bearing cannot answer: does all of this pass through one
    part. Computed by taking the part out and counting the pieces, not by a
    formula that could be argued with."""
    from spar.spar import single_points
    chain = Structure(["A", "Hub", "B", "C"],
                      [("A", "Hub", 1.0), ("Hub", "B", 1.0), ("Hub", "C", 1.0)])
    parts = [x["part"] for x in single_points(chain)]
    assert parts == ["Hub"], f"expected the hub, got {parts}"

    ring = Structure(["A", "B", "C", "D"],
                     [("A", "B", 1.0), ("B", "C", 1.0), ("C", "D", 1.0), ("D", "A", 1.0)])
    assert single_points(ring) == [], "a ring has no part everything passes through"


def test_adding_steps_raises_the_conserved_total():
    """Obfuscation is visible without anybody having to allege it."""
    short = bearings(struct(4, [(0, 1, 1.), (1, 2, 1.), (2, 3, 1.)]))
    padded = bearings(struct(7, [(0, 1, 1.), (1, 2, 1.), (2, 4, 1.),
                                 (4, 5, 1.), (5, 6, 1.), (6, 3, 1.)]))
    assert padded["total"] > short["total"]
    assert abs(padded["total"] - short["total"] - 3.0) < TOL, \
        "three extra steps must show up as exactly three extra units"


# ------------------------------------------------------------------ guards --
def test_a_structure_with_no_links_is_not_reported_as_perfect():
    r = bearings(Structure(["a", "b", "c"], []))
    assert r["dead"] and r["links"] == [] and r["total"] == 0.0


def test_a_zero_weight_link_is_refused_rather_than_silently_dropped():
    with pytest.raises(ValueError, match="left out, not weighted zero"):
        Structure(["a", "b"], [("a", "b", 0.0)])


def test_a_link_to_a_step_that_does_not_exist_is_refused():
    with pytest.raises(ValueError, match="does not exist"):
        Structure(["a", "b"], [("a", "z", 1.0)])


def test_a_step_cannot_depend_on_itself():
    with pytest.raises(ValueError, match="cannot depend on itself"):
        Structure(["a", "b"], [("a", "a", 1.0)])


def test_the_thresholds_are_labels_not_gates():
    """CEREMONY_BELOW and SPAR_ABOVE change what the report SAYS, never what it
    computes. If a threshold ever fed back into a bearing this fails."""
    src = open(os.path.join(os.path.dirname(__file__), "spar.py"), encoding="utf-8").read()
    body = src[src.index("def bearings("):src.index("def scaled(")]
    assert "CEREMONY_BELOW" not in body.split('"verdict"')[0], \
        "a threshold is being used before the bearing is computed"
    assert "bearing = w * R" in body or "bearing = w * R" in src
