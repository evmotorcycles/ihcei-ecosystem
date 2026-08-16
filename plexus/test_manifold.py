#!/usr/bin/env python3
"""Apps and AI as nodes, with LMD deciding the space between them.

    python3 -m pytest -q plexus/test_manifold.py

This is the file that keeps the sandbox honest. A workspace that rearranges
itself is exactly where an easing curve, a tuned constant or a flattering
exponent would never be noticed, so every number the interface shows is checked
here against spar/ -- and the headline law is checked at the place it is FALSE
as well as the place it is true.
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
def m():
    script = os.path.join(HERE, "manifold_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def _distance(parts, links, a, b):
    """d = sqrt(R) between two joined nodes, straight from the Python engine."""
    bb = bearings(Structure(parts, links))
    for r in bb["links"]:
        if {r["from"], r["to"]} == {a, b}:
            w = [l[2] for l in links if {l[0], l[1]} == {a, b}][0]
            return math.sqrt(r["bearing"] / w)
    raise AssertionError("no such link")


def test_with_one_route_the_exponent_is_exactly_minus_a_half(m):
    """d = J^(-1/2), exactly, when there is a single route.

    Not approximately and not asymptotically: with one route the effective
    resistance is 1/J, so the log-log slope is -1/2 at every J. This is the one
    place the headline law is exact, and it is pinned tightly so that any easing
    or smoothing added to make the animation prettier fails here.
    """
    for row in m["oneRoute"]:
        assert abs(row["exponent"] + 0.5) < 1e-3, \
            f"J={row['J']}: exponent {row['exponent']:.4f}, expected -0.5"
        assert abs(row["distance"] - row["J"] ** -0.5) < 1e-9, \
            f"J={row['J']}: distance is not J^(-1/2)"


def test_with_another_route_the_exponent_is_not_minus_a_half(m):
    """The correction that matters, and the reason the readout is worth showing.

    "d proportional to J^-0.5" is widely stated as if it were a general law. It
    is not. Add a second route and raising the direct coupling buys much less
    collapse, because the other route was already holding the two ends close.
    Measured: -0.019 at J=0.02, climbing back toward -1/2 only once the direct
    link dominates. So the exponent reads out whether a thing has another way
    in -- the same question SPAR asks about links, arriving as a number that
    falls out of the metric rather than a label someone applied.
    """
    rows = m["twoRoutes"]
    assert rows[0]["exponent"] > -0.2, \
        "with a second route present, a weak direct link cannot behave like -1/2"
    for row in rows:
        assert row["exponent"] > -0.5, \
            f"J={row['J']}: a redundant node cannot collapse as fast as a sole one"
    # and it must tighten monotonically toward -1/2 as the direct link takes over
    for a, b in zip(rows, rows[1:]):
        assert b["exponent"] < a["exponent"], \
            "the exponent must approach -1/2 as the direct coupling dominates"
    assert rows[-1]["exponent"] < -0.45, "it never gets near -1/2 at all"


def test_the_distances_are_the_python_engine_to_nine_places(m):
    """The interface gets no private arithmetic."""
    for row in m["oneRoute"]:
        want = _distance(["You", "Solo"], [("You", "Solo", row["J"])], "You", "Solo")
        assert abs(want - row["distance"]) < 1e-9


def test_intent_pulls_the_named_things_closer_and_clearing_lets_go(m):
    """The whole interaction, as a measurement rather than an impression."""
    idle = {r["name"]: r for r in m["idle"]["rows"]}
    busy = {r["name"]: r for r in m["busy"]["rows"]}
    cleared = {r["name"]: r for r in m["cleared"]["rows"]}

    for name in ("Water bill", "Summariser"):
        assert busy[name]["distance"] < idle[name]["distance"], \
            f"{name} was named by the intent and did not come closer"
        assert busy[name]["intent"] is True

    assert busy["Files"]["distance"] > busy["Water bill"]["distance"], \
        "something the intent did not name should sit further out"

    for name in idle:
        assert abs(cleared[name]["distance"] - idle[name]["distance"]) < 1e-9, \
            "clearing the intent did not return things to where they were"

    assert m["busy"]["span"] > 0
    assert m["busy"]["chosen"] == 2


def test_an_idle_thing_is_still_reachable_rather_than_lost(m):
    """Residual coupling is deliberately small and NOT zero. At zero the node has
    no route at all, the metric correctly refuses to place it, and it would
    disappear from the picture instead of drifting to the edge of it. "Installed
    and idle" is a real state and has to be drawable."""
    for row in m["idle"]["rows"]:
        assert math.isfinite(row["distance"]), f"{row['name']} became unreachable when idle"
        assert row["coupling"] > 0
    assert m["idle"]["pieces"] == 1
    assert abs(m["idle"]["integrity"] - 1.0) < 1e-9


def test_refusals_come_back_as_reasons_not_exceptions(m):
    e = m["errors"]
    assert e["okInstall"] is None
    for key in ("duplicate", "badKind", "empty", "reservedName", "selfCouple", "missing"):
        assert isinstance(e[key], str) and e[key], f"{key} was allowed through"
    assert "already something called Files" in e["duplicate"]


def test_removing_a_thing_takes_its_couplings_with_it(m):
    """A coupling to something that is gone would be a link to a node the graph
    no longer has, and the metric would be computed over a structure nobody
    described."""
    u = m["uninstall"]
    assert "Water bill" not in u["names"]
    assert u["affinities"] == 0
    assert u["after"] < u["before"]


def test_an_empty_manifold_draws_nothing_rather_than_something(m):
    """No nodes means no couplings means no space. Inventing a layout for an
    empty graph is the same class of lie as placing a disconnected node."""
    assert m["empty"]["dead"] is True
    assert m["empty"]["nodes"] == 0
    assert m["empty"]["integrity"] == 0


def test_intent_changes_only_the_couplings_and_not_the_graph(m):
    """Running an intent must not quietly add or drop nodes: the same things are
    present either way, and only the weights differ. Otherwise 'collapse' could
    be produced by deleting whatever was inconvenient."""
    idle, busy = m["graphIdle"], m["graphBusy"]
    assert idle["names"] == busy["names"]
    assert len(idle["links"]) == len(busy["links"])
    changed = [b for a, b in zip(idle["links"], busy["links"]) if a[2] != b[2]]
    assert len(changed) == 2, "intent named two things and should have moved two weights"
    for a, b in zip(idle["links"], busy["links"]):
        assert a[0] == b[0] and a[1] == b[1]
        assert b[2] >= a[2], "intent must not weaken a coupling"


# ------------------------------------------------------- the shipped page ----
def test_the_shipped_manifold_page_obeys_the_same_rules():
    """Third page, same invariants. The CSP has no script-src 'self', so an
    external script would silently not load; a literal NUL has already been
    written into this codebase twice."""
    import re
    page = os.path.join(HERE, "manifold.html")
    assert os.path.exists(page), "manifold.html was never rendered"
    raw = open(page, "rb").read()
    src = raw.decode("utf-8")
    assert b"\x00" not in raw, "manifold.html contains a literal NUL"
    assert not re.search(r"<script[^>]+\bsrc\s*=", src), \
        "an external script cannot load under this CSP"
    assert "{{" not in src, "an unfilled placeholder was shipped"
    for banned in ("fetch(", "XMLHttpRequest", "WebSocket", "//cdn.", "https://"):
        assert banned not in src, f"the manifold page reaches out: {banned}"
    assert "min-height:44px" in src and "min-height:48px" in src
    assert 'href="index.html"' in src, "there is no way back to the simple view"


def test_the_page_refuses_to_call_itself_an_operating_system():
    """The idea this came from was explicitly science fiction. The page has to
    say what it is, next to the thing that makes it look like it is more."""
    src = open(os.path.join(HERE, "manifold.html"), encoding="utf-8").read()
    assert "It is not an operating system" in src
    assert "leaves the browser" in src
    assert "Nothing leaves this device" in src
    assert "not a constant" in src, "the page must not present -1/2 as a general law"


def test_the_service_worker_caches_the_manifold_page():
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    assert "./manifold.html" in sw, "manifold.html ships and is never cached"


def test_naming_a_thing_does_not_destroy_the_chip_you_pressed():
    """The third time this defect has appeared in this codebase.

    Toggling intent rebuilt the whole list with innerHTML, replacing the chip
    just pressed. Keyboard focus drops to the top of the page, and a driven run
    selecting two things registered only the FIRST, because the rest of the list
    had been detached from the document mid-gesture -- which then reported a
    cluster span of 0.000 for what should have been a pair.
    """
    src = open(os.path.join(HERE, "manifold_template.html"), encoding="utf-8").read()
    i = src.index('$("#list").addEventListener')
    body = src[i:src.index('var d = ev.target.closest("button[data-drop]")', i)]
    assert 'setAttribute("aria-pressed"' in body, "the flag is not flipped in place"
    assert "all()" not in body, \
        "rebuilding the list destroys the chip that was pressed"


def test_the_empty_message_can_actually_be_hidden():
    """A shipped CSS defect, found by rendering the page.

    .void sets display:flex. An author rule beats the user-agent's
    [hidden]{display:none}, so toggling the hidden attribute had no effect and
    the "nothing is installed, so there is no space" overlay stayed painted
    across a graph with seven nodes in it. Nothing in the JS was wrong and
    nothing in the markup looked wrong.
    """
    src = open(os.path.join(HERE, "manifold_template.html"), encoding="utf-8").read()
    assert ".void[hidden]{display:none}" in src, \
        "the overlay cannot be hidden while an author display: rule outranks [hidden]"
