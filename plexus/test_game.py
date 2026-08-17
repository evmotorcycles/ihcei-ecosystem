#!/usr/bin/env python3
"""Quarry: the game's map is the metric, so the game is testable.

    python3 -m pytest -q plexus/test_game.py

A game is where a tuned constant hides best: nobody audits a difficulty number.
So there isn't one. The win condition is a comparison of two measured distances,
and these tests assert that the interesting behaviour FALLS OUT of the graph
rather than being arranged.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from spar.spar import Structure, bearings  # noqa: E402


@pytest.fixture(scope="module")
def g():
    try:
        out = subprocess.run(["node", os.path.join(HERE, "game_dump.mjs")],
                             capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_map_is_the_metric_and_not_a_level(g):
    """Every distance the game shows is sqrt(effective resistance) out of the
    same engine that reads a bill. Checked against the Python."""
    st = g["allFlee"]
    parts = st["cast"]
    links = [(a, b, w) for a, b, w in st["links"]]
    bb = bearings(Structure(parts, links))
    got = None
    for r in bb["links"]:
        if {r["from"], r["to"]} == {"You", "The Way Out"}:
            w = [l[2] for l in links if {l[0], l[1]} == {"You", "The Way Out"}][0]
            got = math.sqrt(r["bearing"] / w)
    assert got is not None
    assert abs(got - st["toPortal"]) < 1e-9


def test_you_start_losing(g):
    """If the opening position were already a win there would be no game."""
    assert g["idle"]["escaped"] is False
    assert g["idle"]["toPortal"] > g["idle"]["toBoss"]


def test_fighting_pulls_the_boss_onto_you(g):
    """Attention is coupling. Looking hard at the Boss brings the Boss closer,
    which is the opposite of what a player wants, and it is not scripted -- it
    is what raising a conductance does."""
    assert g["allFight"]["toBoss"] < g["idle"]["toBoss"]
    assert g["allFight"]["escaped"] is False


def test_fleeing_wins_and_is_the_only_single_move_that_does(g):
    assert g["allFlee"]["escaped"] is True
    assert g["allFight"]["escaped"] is False
    assert g["allGreed"]["escaped"] is False


def test_greed_is_a_trap_that_nobody_designed(g):
    """The Hoard is tied to the Way Out in the dungeon graph, so chasing loot
    does drag the exit nearer -- but never enough, because it drags the Boss
    nearer too through the Boss-Hoard tie. No difficulty knob produces this; the
    wiring does."""
    pulls = g["greedPulls"]
    assert pulls[-1]["toLoot"] < pulls[0]["toLoot"], "greed did not reach the hoard"
    assert pulls[-1]["toPortal"] < pulls[0]["toPortal"], "the tie to the exit is not real"
    assert all(p["escaped"] is False for p in pulls), "greed alone should not win"


def test_scaling_the_whole_graph_changes_no_comparison(g):
    """The invariance that IS true: scale every link, dungeon ties included,
    and every distance moves by the same factor, so nothing is nearer or
    further than anything else than it was."""
    a, b = g["globalScale"]
    assert b["k"] == 9 and a["k"] == 1
    expect = 1.0 / math.sqrt(9)
    for key in ("toBoss", "toPortal", "toLoot"):
        assert abs(b[key] / a[key] - expect) < 1e-9, \
            "global scaling did not scale distances by 1/sqrt(k)"


def test_an_even_spend_is_not_global_scaling_and_i_was_wrong_about_it(g):
    """A claim of mine that this suite falsified.

    I wrote that spending evenly does nothing, reasoning from the scale
    invariance above. It does not apply: an even spend scales only the three
    attention edges, while the dungeon's own ties stay put, so the ratio between
    them moves and the world genuinely changes shape. Measured, 4/4/4 against
    0.4/0.4/0.4 gives 1.9319 rather than the sqrt(10) = 3.1623 that true global
    scaling would give. What survives is only the weaker, measured statement:
    in THIS dungeon an even spend never flips the verdict.
    """
    big, small = g["even"], g["evenSmall"]
    ratio = small["toBoss"] / big["toBoss"]
    assert abs(ratio - math.sqrt(10)) > 0.5, \
        "if this is now global scaling, the correction above needs rereading"
    shapes = [small[k] / big[k] for k in ("toBoss", "toPortal", "toLoot")]
    assert max(shapes) - min(shapes) > 1e-6, "an even spend did change the shape"
    assert big["escaped"] == small["escaped"] is False, \
        "measured: an even spend does not win in this dungeon"


def test_attention_is_conserved(g):
    """You cannot buy your way out by typing a bigger number."""
    over = g["overspend"]
    assert abs(over["spend"]["spent"] - over["budget"]) < 1e-9
    for k in ("fight", "greed", "flee"):
        assert over["spend"][k] > 0


def test_nothing_is_ever_fully_ignored(g):
    """A coupling of exactly zero strands a node: it has no route, the metric
    correctly refuses to place it, and a piece of the map would vanish
    mid-game. The floor is why that cannot happen."""
    for st in (g["idle"], g["allFight"], g["allFlee"], g["allGreed"]):
        for name, d in st["distances"].items():
            assert math.isfinite(d), f"{name} fell out of the world"


def test_there_is_no_difficulty_constant_to_tune():
    """The only numbers in the file are the dungeon's wiring, the attention
    budget, and the floor that stops a node stranding. No score, no threshold,
    no balance pass."""
    src = open(os.path.join(HERE, "game.js"), encoding="utf-8").read()
    code = src[src.index("(function (root)"):]      # skip the prose header
    for banned in ("difficulty", "DIFFICULTY", "score", "points", "tuning"):
        assert banned not in code, f"a tuning knob appeared in the code: {banned}"
    assert "d(Player, Portal) < d(Player, Boss)" in src
