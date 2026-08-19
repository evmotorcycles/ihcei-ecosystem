#!/usr/bin/env python3
"""Auditing a metaphor, including our own.

    python3 -m pytest -q plexus/test_metaphor.py

Predictions were written down and the file hashed before any of this ran:

    sha256  c2588fcdbad5b7adf5ca022fc6b2b383d71549993abc08d8790cc79f906e0b33

The test that could have embarrassed us is test_our_own_metaphors_are_held_to_
the_same_rule. An audit that puts somebody else's pictures under a standard and
its own in a section headed "why ours are different" is not an audit.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from fathom.fathom import Claim, sound  # noqa: E402
from spar.spar import Structure, bearings  # noqa: E402

PREREG_SHA256 = "c2588fcdbad5b7adf5ca022fc6b2b383d71549993abc08d8790cc79f906e0b33"


@pytest.fixture(scope="module")
def a():
    script = os.path.join(HERE, "metaphor_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_predictions_were_locked_before_anything_ran():
    path = os.path.join(HERE, "metaphor_preregistration.md")
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    assert got == PREREG_SHA256


def test_every_metaphor_in_the_library_is_well_formed(a):
    for i in a["order"]:
        assert a["audits"][i]["ok"], f"{i}: {a['audits'][i]['why']}"


# ------------------------------------------------------------ the same law ---
@pytest.mark.parametrize("m,want", [(1, 1.0), (2, 0.25), (3, 1 / 9)])
def test_predictions_on_one_picture_follow_the_same_law_as_handles(a, m, want):
    """M1. The reuse was not a metaphor for a metaphor: it is the same graph.

    A claim's handles hang off its origin; a picture's predictions hang off the
    picture. If the picture is wrong they all go together, exactly as handles go
    when their source turns out not to exist. So 1/m^2 should reproduce, and it
    does at every m.
    """
    row = a["law"][str(m)]
    assert len(row["settles"]) == m
    for s in row["settles"]:
        assert abs(s - want) < 1e-9
    st = row["structure"]
    assert st["parts"] == m + 2 and st["conserved"] is True
    for b in st["bearings"]:
        assert abs(b - 1.0) < 1e-9


def test_the_browser_engine_agrees_with_the_python(a):
    lib = json.loads(subprocess.run(
        ["node", "-e",
         "globalThis.LMD=require('../smi/lmd.js');"
         "globalThis.PLEXUS=require('./engines.js');"
         "const M=require('./metaphor.js'),L=require('./metaphorlib.js');"
         "process.stdout.write(JSON.stringify(L.metaphors.filter(m=>m.predicts.length)"
         ".map(m=>({id:m.id,g:M.graph(m)}))))"],
        cwd=HERE, capture_output=True, text=True, timeout=120).stdout)
    for row in lib:
        g = row["g"]
        links = [(x, y, w) for x, y, w in g["links"]]
        py = bearings(Structure(g["parts"], links))
        got = a["audits"][row["id"]]["structure"]
        assert abs(py["total"] - got["totalBearing"]) < 1e-9, row["id"]
        pyf = sound(Claim(g["claim"], g["predictions"], links))
        want = a["audits"][row["id"]]["predictions"][0]["settles"]
        assert abs(pyf["deepest_dependence"] - want) < 1e-9, row["id"]


# ------------------------------------------------------------ the classes ----
def test_a_picture_that_predicts_nothing_gets_no_number(a):
    """M2, M6. Not a criticism. A legend on a map cannot be wrong either."""
    for i in ("cloud-storage", "desktop-and-folders", "for-you"):
        r = a["audits"][i]
        assert r["klass"] == "notation", i
        assert r["refutable"] is False
        assert r["structure"] is None, "a number was produced for a picture that risks nothing"
        assert r["predictions"] == []
        assert "not a fault" in r["verdict"]


def test_the_metaphoros_pictures_are_refutable_only_about_themselves(a):
    """M5. The finding, and the one most likely to be wrong.

    These are not vacuous -- each really does predict something, and each could
    come back false. But every one of them could be made true again by the
    people who built it, editing their own code. Newton could not have rescued
    corpuscles by editing anything except the theory.

    If anyone can state a prediction of the pipe metaphor that its own builders
    could NOT make true that way, this classification flips and the audit was
    mistaken. That is the whole way to overturn it.
    """
    for i in ("wider-pipe", "scale-slider", "snapping-bricks", "water-grid-budget"):
        r = a["audits"][i]
        assert r["klass"] == "self-referring", i
        assert r["refutable"] is True, "they do predict something -- that is the point"
        assert r["uncontrolled"] == 0, i
        assert "demonstration, not an instrument" in r["verdict"]


def test_the_picture_that_its_own_prediction_destroyed(a):
    """M7. The gold standard, and it is the example from the brief.

    Two of the three came back false: light travels slower in water, not faster,
    and it does bend round a sharp edge. The metaphor died of its own
    predictions, which is exactly what earned it the name.
    """
    r = a["audits"]["corpuscles"]
    assert r["klass"] == "lens"
    assert r["killed"] is True
    assert r["uncontrolled"] == 3
    assert len(r["predictions"]) == 3
    for p in r["predictions"]:
        assert abs(p["settles"] - 1 / 9) < 1e-9
        assert p["presenterControls"] is False
    assert "SLOWER in water" in r["killedBy"]


def test_our_own_metaphors_are_held_to_the_same_rule(a):
    """M8. The one that could have embarrassed us, and the reason ours are in
    the same table rather than in a section explaining why they are different.

    If any of these had come out self-referring, the standard would have been
    applied in one direction only -- which is the failure this whole stack is
    arranged against -- and the honest fix would be to give it a real prediction
    or stop calling it a lens.
    """
    for i in a["ours"]:
        r = a["audits"][i]
        assert r["klass"] == "lens", f"{i} is not a lens by our own rule"
        assert r["uncontrolled"] >= 1, i


def test_one_of_our_own_predictions_is_marked_as_ours_to_control(a):
    """Foster conservation is a fact about our arithmetic, not about the world.

    Marking it presenterControls: true costs nothing here -- the sole-route
    metaphor still qualifies on its other prediction -- and marking it false
    would have been the cheap way to inflate our own count.
    """
    r = a["audits"]["sole-route"]
    flags = [p["presenterControls"] for p in r["predictions"]]
    assert flags.count(True) == 1 and flags.count(False) == 1
    assert r["uncontrolled"] == 1


def test_the_counts_across_the_audit(a):
    """M9."""
    assert a["tally"] == {"lens": 5, "self-referring": 4, "notation": 3}
    assert len(a["order"]) == 12


# ------------------------------------------------------------- refusals ------
def test_a_metaphor_nobody_asked_the_question_of_is_refused(a):
    """M10. An absent predicts list and an empty one are different things.

    Empty is a finding: this picture risks nothing. Absent means nobody looked,
    and publishing a class for something nobody looked at is the failure this
    file exists to name.
    """
    r = a["refusals"]
    assert r["ok"] == []
    assert any("nobody has asked what it puts at risk" in w for w in r["noPredictsField"])
    assert any("changing their own work" in w for w in r["noControlFlag"])
    for key in ("emptyPrediction", "noWhere", "badId"):
        assert isinstance(r[key], list) and r[key], key
        for w in r[key]:
            assert not w.startswith("THREW")


def test_every_reading_says_where_it_came_from(a):
    """The prediction lists are hand-written -- a Layer 3 reading over Layer 1
    arithmetic. Each carries where it came from so a person can disagree with
    the reading rather than with the number."""
    for i in a["order"]:
        assert a["audits"][i]["where"].strip()


# --------------------------------------------------------------- the page ----
def test_the_shipped_lens_page_obeys_the_same_rules():
    import re
    page = os.path.join(HERE, "metaphor.html")
    assert os.path.exists(page)
    raw = open(page, "rb").read()
    src = raw.decode("utf-8")
    assert b"\x00" not in raw
    assert not re.search(r"<script[^>]+\bsrc\s*=", src)
    assert "{{" not in src
    assert "min-height:44px" in src and "min-height:48px" in src
    assert 'href="index.html"' in src
    assert "Nothing leaves this device" in src


def test_the_page_says_how_to_overturn_its_own_verdict():
    """A published judgement about somebody else's design that does not say how
    to overturn it is not a measurement, it is an opinion with a number on it."""
    import re
    src = re.sub(r"\s+", " ", open(os.path.join(HERE, "metaphor.html"),
                                   encoding="utf-8").read())
    assert "written by a person" in src
    assert "add one" in src or "add a prediction" in src
    assert "self-referring is not an accusation" in src.lower()


def test_the_service_worker_caches_the_lens_page():
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    assert "./metaphor.html" in sw
