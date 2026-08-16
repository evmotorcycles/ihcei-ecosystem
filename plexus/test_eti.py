#!/usr/bin/env python3
"""The topology view must not become a place where numbers are invented.

    python3 -m pytest -q plexus/test_eti.py

ETI is a skin over the same engines. That is easy to say and easy to lose: a
spatial view is exactly where a tuned constant or a flattering curve slips in,
because it looks like design rather than arithmetic. Every quantity the view
shows is checked here against spar/ and fathom/, and the one claim the view
makes about itself -- that space collapses as coupling rises -- is checked as a
monotonicity, not as an impression.
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

from spar.spar import Structure, bearings  # noqa: E402

TOL = 1e-9


@pytest.fixture(scope="module")
def eti():
    script = os.path.join(HERE, "eti_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


CASES = {
    "triangle": (["a", "b", "c"], [("a", "b", 1.0), ("b", "c", 1.0), ("a", "c", 1.0)]),
    "path": (["a", "b", "c", "d"],
             [("a", "b", 1.0), ("b", "c", 1.0), ("c", "d", 1.0)]),
    "kite": (["a", "b", "c", "d"],
             [("a", "b", 1.0), ("b", "c", 1.0), ("a", "c", 1.0), ("c", "d", 1.0)]),
    "two pieces": (["a", "b", "c", "d", "e"],
                   [("a", "b", 1.0), ("b", "c", 2.0), ("d", "e", 5.0)]),
    "hub": (["hub", "a", "b", "c"],
            [("hub", "a", 1.0), ("hub", "b", 1.0), ("hub", "c", 1.0)]),
}


def test_the_view_reports_the_same_totals_as_the_python(eti):
    """If the skin and the engine ever disagree, the skin is lying."""
    for row in eti["cases"]:
        if row["name"] not in CASES:
            continue
        parts, links = CASES[row["name"]]
        py = bearings(Structure(parts, links))
        assert abs(py["total"] - row["total"]) < TOL, f"{row['name']}: totals differ"
        assert py["pieces"] == row["pieces"], f"{row['name']}: piece counts differ"


def test_integrity_is_fosters_theorem_over_its_own_ceiling(eti):
    """integrity = (parts - pieces) / (parts - 1).

    Nothing is chosen here. The numerator is the conserved total the second tab
    already prints -- Foster's theorem makes it exact -- and the denominator is
    the largest value that total could take on those parts. A structure in one
    piece reads 1.0 because it is carrying everything it could carry, not
    because 1.0 was picked as a pass mark.
    """
    for row in eti["cases"]:
        if row["name"] not in CASES:
            continue
        parts, links = CASES[row["name"]]
        py = bearings(Structure(parts, links))
        n, k = len(parts), py["pieces"]
        want = (n - k) / (n - 1) if n > 1 else 0.0
        assert abs(want - row["integrity"]) < TOL, f"{row['name']}: integrity differs"
        assert 0.0 <= row["integrity"] <= 1.0


def test_a_whole_structure_reads_one_and_a_fractured_one_reads_less(eti):
    """The ring has to fall when the structure breaks, or it is decoration."""
    assert abs(eti["whole"]["integrity"] - 1.0) < TOL, "an unbroken path is not whole"
    assert eti["whole"]["pieces"] == 1
    assert eti["fractured"]["pieces"] == 2
    # four parts in two pieces: (4 - 2) / 3
    assert abs(eti["fractured"]["integrity"] - 2.0 / 3.0) < TOL
    assert eti["fractured"]["integrity"] < eti["whole"]["integrity"]


def test_space_collapses_as_coupling_rises(eti):
    """The one claim the view makes about itself.

    d_ij = sqrt(R_ij) and bearing = w_ij * R_ij, so d = sqrt(bearing / weight).
    Rayleigh's monotonicity law says raising a conductance cannot raise any
    effective resistance, so turning a coupling up must pull its ends together
    -- every time, not on average. This is checked as a strict monotonicity so
    that no smoothing, easing or clamp can be added later without failing.
    """
    rows = eti["collapse"]
    assert len(rows) >= 5
    for a, b in zip(rows, rows[1:]):
        assert b["w"] > a["w"]
        assert b["distance"] < a["distance"], \
            f"coupling {a['w']} -> {b['w']} did not collapse space"
        # and the same link necessarily carries more as it tightens
        assert b["bearing"] > a["bearing"]
    assert rows[0]["distance"] / rows[-1]["distance"] > 5, \
        "the collapse is too small to be visible, so the view would be inert"


def test_the_collapse_matches_sqrt_bearing_over_weight(eti):
    """The distance drawn is the metric, not a curve chosen to look good."""
    import math
    for row in eti["collapse"]:
        want = math.sqrt(row["bearing"] / row["w"])
        assert abs(want - row["distance"]) < 1e-9, \
            "the view is drawing something other than sqrt(R)"


def test_parts_in_another_piece_are_not_given_invented_positions(eti):
    """pinv neither knows nor cares that a graph is in pieces. A node with no
    finite distance to the rest must be set apart, not placed somewhere
    plausible -- placing it is the precise lie these guards exist to stop."""
    two = [r for r in eti["cases"] if r["name"] == "two pieces"][0]
    assert two["pieces"] == 2
    assert two["stranded"] == 2, "the smaller piece was folded into the layout"
    assert two["nodes"] == 5, "a part went missing from the view"

    dead = [r for r in eti["cases"] if r["name"] == "nothing left"][0]
    assert dead["stranded"] == dead["nodes"] == 3
    assert dead["integrity"] == 0.0


def test_the_hub_shows_every_link_as_a_sole_route(eti):
    """A star has no second route to anything: every spoke reads 100%."""
    hub = [r for r in eti["cases"] if r["name"] == "hub"][0]
    assert hub["soles"] == 3
    assert abs(hub["integrity"] - 1.0) < TOL


def test_the_same_structure_draws_the_same_picture_twice(eti):
    """Classical MDS fixes an embedding only up to rotation and reflection, and
    a layout that flips between redraws tells a person the positions are
    arbitrary -- which is the claim this whole tool argues against."""
    assert eti["deterministic"] is True


def _boxes(case):
    """Rebuild the label boxes with the same constants eti.js uses."""
    out = []
    for n in case["nodes"]:
        if not n["shown"]:
            continue
        w = max(len(n["name"]) * 4.5, 10)
        lx, a = n["lx"], n["anchor"]
        x0 = lx - w / 2 if a == "middle" else lx if a == "start" else lx - w
        out.append((n["name"], x0, x0 + w, n["ly"] - 9, n["ly"] + 3))
    return out


def test_the_names_do_not_print_on_top_of_each_other(eti):
    """The defect that was reported on the shipped page.

    Ten parts of a water bill, tightly coupled, collapsed to nearly the same
    place -- which is the correct answer -- and their names were drawn over each
    other into unreadable mush, with one clipped off the right edge. Labels are
    now placed around the dots, and this fails if any two overlap or any leaves
    the frame.
    """
    case = [c for c in eti["labels"] if c["name"] == "water bill"][0]
    boxes = _boxes(case)
    assert len(boxes) == len(case["nodes"]) == 10, "a name went unplaced"
    v = case["view"]
    for name, x0, x1, y0, y1 in boxes:
        assert 0 <= x0 and x1 <= v["w"], f"{name}: label runs off the frame in x"
        assert 0 <= y0 and y1 <= v["h"], f"{name}: label runs off the frame in y"
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            apart = a[2] < b[1] or a[1] > b[2] or a[4] < b[3] or a[3] > b[4]
            assert apart, f"{a[0]!r} and {b[0]!r} print on top of each other"


def test_placing_the_labels_does_not_move_the_nodes(eti):
    """The nodes ARE the measurement.

    This view claims screen distance is sqrt(bearing/strength). Nudging a dot to
    make room for text would quietly falsify that claim while making the picture
    look better -- the most tempting kind of lie available here. So the text
    moves and the dots do not, and that is checked rather than trusted: the
    drawn positions must be one uniform scale-and-shift of the embedding, which
    means every pair keeps the same ratio.
    """
    import math
    case = [c for c in eti["labels"] if c["name"] == "water bill"][0]
    by_name = {n["name"]: n for n in case["nodes"] if not n["stranded"]}
    keep, xy = case["keep"], case["xy"]
    assert len(keep) == len(xy) >= 3
    pts = [n for n in case["nodes"] if not n["stranded"]]
    assert len(pts) == len(xy)

    ratios = []
    for i in range(len(xy)):
        for j in range(i + 1, len(xy)):
            emb = math.dist(xy[i], xy[j])
            scr = math.dist((pts[i]["x"], pts[i]["y"]), (pts[j]["x"], pts[j]["y"]))
            if emb > 1e-9:
                ratios.append(scr / emb)
    assert ratios
    assert max(ratios) - min(ratios) < 1e-6, \
        "a node was displaced: the drawing is no longer the metric"
    assert by_name  # names round-tripped


def test_a_name_with_nowhere_to_go_is_reported_not_dropped(eti):
    """A part that silently vanishes from the picture is the same lie as a part
    drawn where it is not. Crushed into a frame far too small, some names cannot
    be placed -- every node must still be drawn, and the ones without a name
    must be named out loud so a person can ask for them."""
    tiny = [c for c in eti["labels"] if c["name"].endswith("tiny frame")][0]
    assert len(tiny["nodes"]) == 10, "nodes disappeared when labels did not fit"
    assert tiny["hidden"], "the tiny frame fitted every label, so this proves nothing"
    unshown = {n["name"] for n in tiny["nodes"] if not n["shown"]}
    assert unshown == set(tiny["hidden"]), \
        "the hidden list does not match the labels actually withheld"


def test_the_shipped_topology_page_obeys_the_same_rules_as_the_app():
    """A second page is a second chance to break the invariants that were paid
    for once. The CSP has no script-src 'self', so an external script would not
    load; a literal NUL makes grep call the file binary and lets a formatter
    turn the pair separator into the empty string, merging different pairs onto
    one key. Both of those were real defects here -- and a literal NUL DID get
    written into eti.js while this view was being built, caught only because the
    check runs on bytes."""
    import re
    page = os.path.join(HERE, "topology.html")
    assert os.path.exists(page), "topology.html was never rendered"
    raw = open(page, "rb").read()
    src = raw.decode("utf-8")
    assert b"\x00" not in raw, "topology.html contains a literal NUL"
    assert not re.search(r"<script[^>]+\bsrc\s*=", src), \
        "an external script cannot load under this CSP"
    assert "{{" not in src, "an unfilled placeholder was shipped"
    for banned in ("fetch(", "XMLHttpRequest", "WebSocket", "//cdn.", "https://"):
        assert banned not in src, f"the topology page reaches out: {banned}"
    assert 'href="index.html"' in src, "there is no way back to the simple view"
    assert "min-height:44px" in src and "min-height:48px" in src, \
        "the 44px floor does not apply to this page"


def test_the_service_worker_caches_the_topology_page():
    """caches.addAll is atomic. A page that is shipped and not cached is a page
    that vanishes offline; a page that is cached and not shipped rejects the
    whole install and takes offline down with it."""
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    assert "./topology.html" in sw, "topology.html ships and is never cached"
    assert os.path.exists(os.path.join(HERE, "topology.html"))


def test_the_topology_page_states_what_it_cannot_tell_you():
    """The same epistemic floor as the simple view. A HUD is exactly where a
    number starts looking more certain than it is."""
    src = open(os.path.join(HERE, "topology.html"), encoding="utf-8").read()
    assert "Whether a step is <em>useful</em>" in src
    assert "only knows the parts you entered" in src
    assert "Nothing leaves this device" in src
    assert "100% means in one piece, not correct" in src


def test_every_node_lands_inside_the_frame(eti):
    """A node drawn outside the viewBox is invisible and silently absent."""
    v = eti["view"]
    for row in eti["cases"]:
        b = row["box"]
        if row["nodes"] == 0:
            continue
        assert -1 <= b["x0"] and b["x1"] <= v["w"] + 1, f"{row['name']}: off frame in x"
        assert -1 <= b["y0"] and b["y1"] <= v["h"] + 1, f"{row['name']}: off frame in y"
