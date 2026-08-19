#!/usr/bin/env python3
"""Agent Gate: a perimeter, the steps with no way round, and a hazard.

    python3 -m pytest -q plexus/test_gate.py

Predictions were written down and the file hashed before any of this ran:

    sha256  543c29ee1050d354e63f7a2de02cc04dc1c1dcc5973e1af7b5bf35f25cfcb98a

The most important test in this file is a NEGATIVE one. The design this gate was
asked for stops an assistant when a product of per-hop fidelities falls below a
floor. This repository retired that floor with its own data -- the sensor is
blind 76.6% of the time and the pre-registered confirmatory run returned a
fully-powered null at p = 0.735 -- so the gate is built on enforcement latency
instead, and a test asserts the floor stays retired.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from spar.spar import Structure, bearings  # noqa: E402
from tau_v_monitor.core import Event, assess  # noqa: E402

PREREG_SHA256 = "543c29ee1050d354e63f7a2de02cc04dc1c1dcc5973e1af7b5bf35f25cfcb98a"
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def g():
    script = os.path.join(HERE, "gate_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_predictions_were_locked_before_anything_ran():
    path = os.path.join(HERE, "gate_preregistration.md")
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    assert got == PREREG_SHA256, (
        f"the pre-registration has been edited since it was locked\n"
        f"  locked {PREREG_SHA256}\n  now    {got}"
    )


# ------------------------------------------------------------- 1 perimeter ---
def test_the_perimeter_is_set_arithmetic_with_nothing_to_tune(g):
    """G1, G2. Two links inside, two crossing out, one wholly beyond."""
    p = g["perimeter"]
    assert len(p["within"]) == 2
    assert len(p["crossing"]) == 2
    assert len(p["beyond"]) == 1
    assert set(p["wouldReach"]) == {"The deposit", "The order ships"}
    assert p["sealed"] is False
    assert p["unknown"] == []


def test_a_perimeter_around_everything_is_sealed_and_says_so(g):
    s = g["sealed"]
    assert s["sealed"] is True
    assert s["crossing"] == []
    assert len(s["within"]) == 5


def test_naming_a_part_that_is_not_in_the_plan_is_reported_not_ignored(g):
    """Silently dropping an unknown name would let somebody believe they had
    granted or withheld access to something the gate never saw."""
    assert g["unknownPart"]["unknown"] == ["A part nobody entered"]


# ----------------------------------------------------------- 2 sole routes ---
def test_the_sole_route_is_found_and_the_bearings_conserve(g):
    """G3, G4, G5. One pendant link at 1.000, four cycle links at 0.750,
    summing to parts minus pieces exactly."""
    s = g["soleRoutes"]
    assert s["count"] == 1
    assert s["routes"][0]["from"] == "The supplier's price"
    assert s["routes"][0]["to"] == "The quote"
    assert abs(s["routes"][0]["bearing"] - 1.0) < 1e-9

    others = [r["bearing"] for r in s["all"] if not r["soleRoute"]]
    assert len(others) == 4
    for b in others:
        assert abs(b - 0.75) < 1e-9

    assert abs(s["totalBearing"] - 4.0) < 1e-9
    assert s["expected"] == 4 and s["pieces"] == 1 and s["conserved"] is True


def test_the_bearings_are_the_python_engine(g):
    plan = g["plan"]
    links = [(a, b, w) for a, b, w in plan["links"]]
    py = bearings(Structure(plan["parts"], links))
    assert abs(py["total"] - g["soleRoutes"]["totalBearing"]) < 1e-9
    pym = {(min(r["from"], r["to"]), max(r["from"], r["to"])): r["bearing"]
           for r in py["links"]}
    for r in g["soleRoutes"]["all"]:
        k = (min(r["from"], r["to"]), max(r["from"], r["to"]))
        assert abs(pym[k] - r["bearing"]) < 1e-9


# --------------------------------------------------------------- 3 hazard ---
def _events(history):
    return [
        Event(
            opened_at=EPOCH + timedelta(seconds=e["openedAt"]),
            closed_at=None if e["closedAt"] is None
            else EPOCH + timedelta(seconds=e["closedAt"]),
        )
        for e in history["events"]
    ]


def test_the_hazard_reads_as_predicted(g):
    """G6, G7, G8."""
    assert g["hazards"]["flat"]["status"] == "OK"
    assert g["hazards"]["flat"]["trendDirection"] == "no trend"

    rising = g["hazards"]["rising"]
    assert rising["trendDirection"] == "increasing"
    assert rising["status"] in ("WATCH", "ALERT")

    assert g["hazards"]["short"]["status"] == "INSUFFICIENT_DATA"
    assert g["emptyHistory"]["status"] == "INSUFFICIENT_DATA"


def test_a_thin_history_refuses_to_calibrate_rather_than_guessing(g):
    """One closed item per window is below the minimum, so there is no local
    baseline to compare against and the honest answer is to say so. On a fresh
    install this is what every gate reads, and that is not a defect."""
    thin = g["hazards"]["thin"]
    assert thin["status"] == "INSUFFICIENT_DATA"
    assert thin["currentTauV"] is None and thin["robustZ"] is None
    assert "need >=" in thin["reasons"][0]


@pytest.mark.parametrize(
    "name", ["flat", "rising", "falling", "noisy", "jump", "thin", "short",
             "with-backlog"],
)
def test_the_browser_port_is_the_python_monitor(g, name):
    """G9. The one that could kill the port.

    A port nobody checks drifts, and then the thing that was tested and the
    thing on somebody's phone stop being the same thing. Every history is run
    through tau_v_monitor/core.py and through the JavaScript, and any
    disagreement past 1e-9 fails.
    """
    history = g["histories"][name]
    now = EPOCH + timedelta(seconds=history["now"])
    py = assess(_events(history), now=now).as_dict()
    js = g["hazards"][name]

    assert py["status"] == js["status"], f"{name}: status"
    assert py["trend_direction"] == js["trendDirection"], f"{name}: direction"

    for pk, jk in (("trend_p", "trendP"),
                   ("trend_slope_per_window", "trendSlopePerWindow"),
                   ("baseline_tau_v", "baselineTauV"),
                   ("current_tau_v", "currentTauV"),
                   ("robust_z", "robustZ"),
                   ("tail_ratio", "tailRatio")):
        a, b = py[pk], js[jk]
        if a is None or b is None:
            assert a is None and b is None, f"{name}: {pk} is None on one side only"
            continue
        # as_dict rounds to 2 places (4 for p); compare against the rounded form
        nd = 4 if pk == "trend_p" else 2
        assert abs(a - round(b, nd)) < 1e-9, f"{name}: {pk} {a} vs {b}"


def test_the_erf_port_is_accurate_where_the_p_value_lives(g):
    """The Mann-Kendall p is an erfc, and the language has no erf.

    Python's math.erf is correct to about one unit in the last place. The usual
    rational approximation has a fractional error of 1.2e-7, which would show up
    directly in p, so the port uses a Taylor series below |x| = 3 -- where every
    p that is actually informative lives -- and the approximation only out in
    the tail where erfc is already smaller than the tolerance.

    Checked in the sensitive band rather than at the extremes: a p of 1.0 or
    1e-40 would agree under any approximation and prove nothing.
    """
    informative = []
    for name in g["histories"]:
        py = assess(_events(g["histories"][name]),
                    now=EPOCH + timedelta(seconds=g["histories"][name]["now"])).as_dict()
        p = py["trend_p"]
        if p is not None and 1e-3 < p < 0.9:
            informative.append((name, p, g["hazards"][name]["trendP"]))
    assert informative, "no history produced a p in the band where accuracy matters"
    for name, want, got in informative:
        assert abs(want - round(got, 4)) < 1e-9, f"{name}: p {want} vs {got}"


def test_the_disclaimer_travels_with_every_number(g):
    """A day-count without it invites exactly the transplantation the floor was
    retired for. It is part of the result, not a footnote on a website."""
    assert "not a" in g["disclaimer"] and "transplantable" in g["disclaimer"]
    for name, h in g["hazards"].items():
        assert h["disclaimer"] == g["disclaimer"], name
    assert g["emptyHistory"]["disclaimer"] == g["disclaimer"]


# ------------------------------------------------------- the retired floor ---
def test_the_retired_floor_stays_retired(g):
    """G10. The test that matters most in this file.

    The gate was asked for as a product of per-hop fidelities against a floor
    D_min. That gate was retired here: the sensor is blind on 76.6% of records
    and the pre-registered confirmatory run on an unseen cohort returned a
    fully-powered null at p = 0.735. Rebuilding it inside the tool whose whole
    claim is that it prints its limits would be the most complete way to
    falsify that claim, so the source is read and the floor must be absent.
    """
    src = open(os.path.join(HERE, "gate.js"), encoding="utf-8").read()
    body = src.split("*/", 1)[1] if "*/" in src else src

    import re
    # The name appears exactly once, inside the record of its own retirement.
    # Banning the string outright would also delete the explanation, so what is
    # asserted is that every occurrence sits on a line that says it is retired.
    hits = [ln for ln in body.splitlines() if re.search(r"D_?min", ln, re.I)]
    assert len(hits) == 1, f"D_min occurs {len(hits)} times in the body, not once"
    assert "retired" in hits[0], \
        "D_min appears somewhere other than the record of its retirement"

    for banned in (r"\bdMin\b", r"fidelityProduct", r"\bfloor\s*\)", r"\bDMIN\b"):
        assert not re.search(banned, body), \
            f"the retired floor is back in the code: {banned}"

    r = g["retiredFloor"]
    assert "D_min" in r["retired"]
    assert any("0.735" in b for b in r["because"]), \
        "the null that retired the floor is not carried with the refusal"
    assert any("89.8%" in b for b in r["because"])
    assert r["record"] == "FLOOR_RETIREMENT.md"


def test_the_three_readouts_are_never_added_together(g):
    """The same rule cairn.js applies to structure and rhetoric.

    A single "agent safety score" fusing a perimeter, a spanning-tree bearing
    and a latency trend would be the most saleable thing this file could
    produce. They are three different kinds of quantity and there is no
    arithmetic that combines them honestly.
    """
    assert set(g["reviewKeys"]) == {"perimeter", "soleRoutes", "hazard", "retiredFloor"}
    for banned in ("combined", "score", "safety", "overall", "rating"):
        assert banned not in g["reviewKeys"]


# ------------------------------------------------------------------- lens ----
def test_a_tool_with_no_refusal_is_refused(g):
    """G11. What an oracle looks like, caught at registration.

    A tool that declares nothing it cannot do is claiming to be one. A tool with
    nowhere to go afterwards expects the reader to stop at its picture, which is
    the definition this stack is arranged against.
    """
    r = g["lensRefusals"]
    assert r["ok"] == []
    assert any("oracle" in w for w in r["noCannot"])
    assert any("handle" in w or "destination" in w for w in r["noGoCheck"])
    assert r["noMeasures"] and r["emptyCheck"] and r["noName"]


def test_every_registered_tool_says_what_it_cannot_do_and_where_to_go_next(g):
    for t in g["tools"]:
        assert t["measures"], f"{t['name']} does not say what it computes"
        assert t["cannot"], f"{t['name']} declares no limit"
        assert t["goCheck"], f"{t['name']} leaves the reader nowhere to go"
        for c in t["goCheck"]:
            assert c.strip(), f"{t['name']} has an empty check"


def test_the_distinction_is_stated_once_and_holds_its_own_limit(g):
    p = g["paradigm"]
    assert "ends the enquiry" in p["mask"]
    assert "go and check" in p["lens"]
    assert "printed" in p["limit"] and "true" in p["limit"], \
        "the paradigm must carry the fact that it can only check what is printed"


def _flat(s):
    """Collapse runs of whitespace.

    HTML collapses whitespace when it renders, so a sentence wrapped across
    three source lines is one sentence on the screen. Comparing the raw bytes
    would make this test about line lengths rather than about what the reader is
    actually told, and would be silently satisfied by reflowing a paragraph.
    """
    import re
    return re.sub(r"\s+", " ", s)


def test_every_shipped_page_prints_its_own_refusals(g):
    """G12. The reason this is code and not a manifesto.

    Each tool's `cannot` sentences must appear verbatim in the page that hosts
    it. Edit a limit in lens.js without editing the page and the build fails in
    the same commit that did it.
    """
    checked = 0
    for page, refusals in g["refusals"].items():
        path = os.path.join(HERE, page)
        assert os.path.exists(path), f"{page} is registered in lens.js and was never built"
        src = _flat(open(path, encoding="utf-8").read())
        for sentence in refusals:
            assert _flat(sentence) in src, \
                f"{page} does not print its own limit: {sentence!r}"
        checked += 1
    assert checked == 7, "a page dropped out of the register without anyone noticing"


def test_every_shipped_page_says_where_to_go_afterwards(g):
    """The half that makes it a lens rather than a careful disclaimer.

    Printing a limit and stopping is still a destination. Each page must also
    carry at least one thing a person does NEXT, outside this software, with
    their own eyes -- which is the whole difference the paradigm turns on.
    """
    checks = {}
    for t in g["tools"]:
        if not t["page"]:
            # A tool with no page has no interface yet. Its limits are asserted
            # against its own source instead; see the note in lens.js.
            continue
        checks.setdefault(t["page"], []).extend(t["goCheck"])
    assert checks, "no tool is attached to a page at all"
    for page, items in checks.items():
        src = _flat(open(os.path.join(HERE, page), encoding="utf-8").read())
        assert any(_flat(c) in src for c in items), \
            f"{page} tells the reader nothing to do outside the software"


def test_no_page_is_registered_without_refusals(g):
    """A page in the register with an empty refusal list would pass the test
    above vacuously, which is the quietest way for this whole idea to stop
    meaning anything."""
    for page, refusals in g["refusals"].items():
        assert refusals, f"{page} is registered but declares no limit at all"
