#!/usr/bin/env python3
"""FATHOM exists because SPAR got a sign backwards. The first test is that one.

    python3 -m pytest -q fathom/test_fathom.py
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fathom.fathom import Claim, ONE_THREAD, sound  # noqa: E402
from spar.spar import Structure, bearings  # noqa: E402

TOL = 1e-9

SHARED = dict(conclusion="Claim", sources=["Origin"],
              links=[("Claim", "A", 1.0), ("Claim", "B", 1.0),
                     ("A", "Origin", 1.0), ("B", "Origin", 1.0)])
SEPARATE = dict(conclusion="Claim", sources=["S1", "S2"],
                links=[("Claim", "A", 1.0), ("Claim", "B", 1.0),
                       ("A", "S1", 1.0), ("B", "S2", 1.0)])


# ------------------------------------------------- the reason it was built --
def test_fathom_reads_independence_the_way_round_that_spar_could_not():
    """SPAR measures route redundancy and reports the genuinely independent
    structure as the MORE fragile one, because independent sources form a tree
    and a shared origin closes a cycle. That null is in spar/README.md. This is
    the test that the new tool actually fixes it rather than restating it."""
    spar_shared = max(x["bearing"] for x in bearings(Structure(
        ["Claim", "A", "B", "Origin"],
        [("Claim", "A", 1.0), ("Claim", "B", 1.0),
         ("A", "Origin", 1.0), ("B", "Origin", 1.0)]))["links"])
    spar_separate = max(x["bearing"] for x in bearings(Structure(
        ["Claim", "A", "B", "S1", "S2"],
        [("Claim", "A", 1.0), ("Claim", "B", 1.0),
         ("A", "S1", 1.0), ("B", "S2", 1.0)]))["links"])
    assert spar_separate > spar_shared, "the SPAR null has changed; recheck both tools"

    f_shared = sound(Claim(**SHARED))["deepest_dependence"]
    f_separate = sound(Claim(**SEPARATE))["deepest_dependence"]
    assert f_shared > f_separate, \
        f"FATHOM has the same defect: shared {f_shared:.2f}, separate {f_separate:.2f}"
    assert f_shared >= ONE_THREAD, "one origin must read as carrying it alone"
    assert f_separate < 0.6, "two separate sources must not read as one thread"


# -------------------------------------------------------- the arithmetic ----
@pytest.mark.parametrize("k,expected", [(1, 1.0), (2, 0.5), (3, 1 / 3), (4, 0.25)])
def test_k_equal_independent_sources_each_carry_one_kth(k, expected):
    """The number that makes it readable by a person: with k equal, separate
    sources, losing any one costs exactly 1/k of the support."""
    links = []
    for i in range(k):
        links += [("Claim", f"h{i}", 1.0), (f"h{i}", f"S{i}", 1.0)]
    r = sound(Claim("Claim", [f"S{i}" for i in range(k)], links))
    assert abs(r["deepest_dependence"] - expected) < 1e-9, \
        f"{k} sources gave {r['deepest_dependence']:.6f}, expected {expected:.6f}"
    assert abs(r["remaining_after_worst_loss"] - (1 - expected)) < 1e-9


def test_a_strong_source_and_a_weak_one_are_not_treated_as_two():
    """The failure mode a citation count has: one real study plus one blog post
    reads as 'two sources' everywhere else and as 97.8% dependence here."""
    r = sound(Claim("Claim", ["Study", "Blog"],
                    [("Claim", "Study", 9.0), ("Claim", "Blog", 0.2)]))
    by = {x["source"]: x["dependence"] for x in r["by_source"]}
    assert by["Study"] > 0.95 and by["Blog"] < 0.05
    assert abs(by["Study"] + by["Blog"] - 1.0) < 1e-9, \
        "with sources in parallel the dependences must partition the support"


def test_scaling_every_link_changes_no_dependence():
    """Insisting everything is very important must not move a sounding, exactly
    as in SPAR. Dependence is a ratio of conductances, so the factor cancels."""
    base = sound(Claim(**SEPARATE))
    for factor in (1e-6, 0.01, 1e3, 1e6):
        scaled = dict(SEPARATE)
        scaled["links"] = [(a, b, w * factor) for a, b, w in SEPARATE["links"]]
        got = sound(Claim(**scaled))
        worst = max(abs(x["dependence"] - y["dependence"])
                    for x, y in zip(base["by_source"], got["by_source"]))
        assert worst < 1e-9, f"scaling by {factor} moved a dependence by {worst:.2e}"


def test_a_longer_chain_to_the_same_single_source_is_still_one_thread():
    """Depth is not independence. Relaying an account through more hands does
    not make it two accounts, and the sounding must not reward the padding."""
    for hops in (1, 2, 5):
        links = [("Claim", "h0", 1.0)]
        for i in range(hops - 1):
            links.append((f"h{i}", f"h{i+1}", 1.0))
        links.append((f"h{hops-1}", "Origin", 1.0))
        r = sound(Claim("Claim", ["Origin"], links))
        assert r["rests_on_one_thread"], f"{hops} hops stopped reading as one thread"
        assert abs(r["deepest_dependence"] - 1.0) < TOL


def test_a_source_with_no_path_to_the_conclusion_adds_nothing():
    """Listing a source does not make it support anything."""
    attached = sound(Claim("Claim", ["S1"], [("Claim", "S1", 1.0)]))
    plus_orphan = sound(Claim("Claim", ["S1", "S2"],
                              [("Claim", "S1", 1.0), ("S2", "Elsewhere", 1.0)]))
    assert abs(plus_orphan["support"] - attached["support"]) < TOL
    by = {x["source"]: x["dependence"] for x in plus_orphan["by_source"]}
    assert abs(by["S2"]) < TOL, "an unattached source registered as support"
    assert abs(by["S1"] - 1.0) < TOL


# -------------------------------------------------------------- the guards --
def test_a_claim_with_no_sources_is_refused():
    with pytest.raises(ValueError, match="no sources cannot be sounded"):
        Claim("Claim", [], [("Claim", "x", 1.0)])


def test_a_conclusion_cannot_be_its_own_source():
    with pytest.raises(ValueError, match="cannot also be one of its own sources"):
        Claim("Claim", ["Claim"], [("Claim", "x", 1.0)])


def test_a_source_listed_twice_is_refused():
    with pytest.raises(ValueError, match="listed twice"):
        Claim("Claim", ["S", "S"], [("Claim", "S", 1.0)])


def test_a_zero_weight_link_is_refused_rather_than_silently_dropped():
    with pytest.raises(ValueError, match="leave it out"):
        Claim("Claim", ["S"], [("Claim", "S", 0.0)])


def test_the_boundary_is_stated_in_the_module_itself():
    """FATHOM measures the structure it was given. Two sources that secretly
    share an origin will be reported as robust, and that has to be said where
    somebody reading the code will see it."""
    src = open(os.path.join(os.path.dirname(__file__), "fathom.py"),
               encoding="utf-8").read()
    assert "if they secretly share an origin and you did not say so" in src
    assert "It measures the structure you described." in src
