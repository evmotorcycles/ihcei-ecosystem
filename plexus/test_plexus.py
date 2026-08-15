#!/usr/bin/env python3
"""Plexus ships JavaScript. The JavaScript must agree with the Python.

    python3 -m pytest -q plexus/test_plexus.py

Plexus puts SPAR and FATHOM in a browser so they run on a phone with no server.
A port nobody checks drifts, and then the thing under test and the thing people
touch stop being the same thing. Both engines are run over the same structures
and any disagreement fails.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from fathom.fathom import Claim, sound  # noqa: E402
from spar.spar import Structure, bearings, single_points  # noqa: E402

TOL = 1e-9

STRUCTURES = [
    ("triangle", ["a", "b", "c"], [("a", "b", 1.0), ("b", "c", 1.0), ("a", "c", 1.0)]),
    ("path", ["a", "b", "c", "d"], [("a", "b", 1.0), ("b", "c", 1.0), ("c", "d", 1.0)]),
    ("kite", ["a", "b", "c", "d"],
     [("a", "b", 1.0), ("b", "c", 1.0), ("a", "c", 1.0), ("c", "d", 1.0)]),
    ("weighted", ["w", "x", "y", "z"],
     [("w", "x", 3.7), ("x", "y", 0.4), ("y", "z", 9.1), ("w", "z", 2.2)]),
    ("wide weights", ["p", "q", "r", "s"],
     [("p", "q", 1e-3), ("q", "r", 1e3), ("p", "r", 1.0), ("r", "s", 5.0)]),
    ("two pieces", ["a", "b", "c", "d", "e"],
     [("a", "b", 1.0), ("b", "c", 2.0), ("d", "e", 5.0)]),
    ("hub", ["hub", "a", "b", "c"],
     [("hub", "a", 1.0), ("hub", "b", 1.0), ("hub", "c", 1.0)]),
    ("the energy bill", ["Meter reading", "Unit rate", "Standing charge", "Subtotal",
                         "VAT", "Late fee", "Amount due"],
     [("Meter reading", "Subtotal", 8.0), ("Unit rate", "Subtotal", 8.0),
      ("Standing charge", "Subtotal", 3.0), ("Subtotal", "VAT", 6.0),
      ("Subtotal", "Amount due", 6.0), ("VAT", "Amount due", 6.0),
      ("Late fee", "Amount due", 0.4)]),
]

CLAIMS = [
    ("shared origin", "The claim", ["Origin"],
     [("The claim", "A", 1.0), ("The claim", "B", 1.0),
      ("A", "Origin", 1.0), ("B", "Origin", 1.0)]),
    ("separate sources", "The claim", ["S1", "S2"],
     [("The claim", "A", 1.0), ("The claim", "B", 1.0),
      ("A", "S1", 1.0), ("B", "S2", 1.0)]),
    ("lopsided", "The claim", ["Study", "Blog"],
     [("The claim", "Study", 9.0), ("The claim", "Blog", 0.2)]),
    ("long names that share a prefix", "The result",
     ["Source alpha", "Source alpha two"],
     [("The result", "Source alpha", 2.0), ("The result", "Source alpha two", 2.0)]),
]


@pytest.fixture(scope="module")
def js():
    script = os.path.join(HERE, "parity_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@pytest.mark.parametrize("i", range(len(STRUCTURES)))
def test_bearings_agree(js, i):
    name, parts, links = STRUCTURES[i]
    py = bearings(Structure(parts, links))
    got = js["bearings"][i]
    assert got["name"] == name
    assert abs(py["total"] - got["total"]) < TOL, f"{name}: totals differ"
    assert py["pieces"] == got["pieces"], f"{name}: piece counts differ"
    pym = {(min(r["from"], r["to"]), max(r["from"], r["to"])): r["bearing"]
           for r in py["links"]}
    jsm = {(min(r["from"], r["to"]), max(r["from"], r["to"])): r["bearing"]
           for r in got["links"]}
    assert set(pym) == set(jsm), f"{name}: different links"
    worst = max(abs(pym[k] - jsm[k]) for k in pym)
    assert worst < TOL, f"{name}: worst bearing disagreement {worst:.3e}"


@pytest.mark.parametrize("i", range(len(STRUCTURES)))
def test_single_points_agree(js, i):
    name, parts, links = STRUCTURES[i]
    py = sorted(x["part"] for x in single_points(Structure(parts, links)))
    got = sorted(x["part"] for x in js["singlePoints"][i]["parts"])
    assert py == got, f"{name}: the engines disagree about which parts everything passes through"


@pytest.mark.parametrize("i", range(len(CLAIMS)))
def test_soundings_agree(js, i):
    name, conclusion, sources, links = CLAIMS[i]
    py = sound(Claim(conclusion, sources, links))
    got = js["soundings"][i]
    assert got["name"] == name
    assert abs(py["deepest_dependence"] - got["deepest"]) < TOL, \
        f"{name}: deepest dependence differs"
    pym = {r["source"]: r["dependence"] for r in py["by_source"]}
    jsm = {r["source"]: r["dependence"] for r in got["bySource"]}
    assert set(pym) == set(jsm)
    worst = max(abs(pym[k] - jsm[k]) for k in pym)
    assert worst < TOL, f"{name}: worst dependence disagreement {worst:.3e}"


def test_the_names_that_share_a_prefix_are_really_a_hazard():
    """The browser port contracts source nodes and has to key pairs somehow. An
    early version joined names into a string and split it back per CHARACTER,
    which only worked for one-character names. This case would have caught it,
    so it must actually be in the parity set and must actually be tricky."""
    name, conclusion, sources, _ = CLAIMS[3]
    assert sources[0] in sources[1], "the two source names must share a prefix"
    assert len({s.replace(" ", "") for s in sources}) == 2


def test_the_shipped_page_carries_no_control_characters():
    """A literal NUL in the source works and is a hazard: grep calls the file
    binary, formatters strip it, and the separator silently becomes the empty
    string -- which merges different pairs onto one key."""
    for rel in ("app.html", "engines.js", "app_template.html"):
        raw = open(os.path.join(HERE, rel), "rb").read()
        assert b"\x00" not in raw, f"{rel} contains a literal NUL"


def test_the_page_reaches_no_network():
    src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
    for banned in ("fetch(", "XMLHttpRequest", "WebSocket", "//cdn.", "https://"):
        assert banned not in src, f"the page reaches out: {banned}"
    assert "navigator.serviceWorker.register" in src, \
        "without this it cannot be installed to a home screen"


def test_the_page_states_what_it_cannot_tell_you():
    src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
    assert "Whether a step is <em>useful</em>" in src
    assert "only knows the parts you entered" in src
    assert "Nothing leaves this device" in src


def test_every_control_is_at_least_44px():
    """Measured in a real browser by plexus/drive.js; this pins the CSS that
    made it true, because the two header chips shipped at 36px."""
    src = open(os.path.join(HERE, "app_template.html"), encoding="utf-8").read()
    assert "min-height:44px" in src, "the header chips lost their 44px floor"
    for rule in ("min-height:46px", "min-height:48px"):
        assert rule in src
