#!/usr/bin/env python3
"""Press to Evidence, as six stages that can each refuse.

    python3 -m pytest -q plexus/test_pipeline.py

The stage that does the work is six. A project claiming a measured result with
no pre-registration hash is refused outright -- the discipline of this whole
repository turned into a field that cannot be left blank.

Neither worked project claims a measured result. That is the honest state.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from spar.spar import Structure, bearings, single_points  # noqa: E402

BOOT = ("globalThis.LMD=require('../smi/lmd.js');"
        "globalThis.PLEXUS=require('./engines.js');"
        "globalThis.METAPHOR=require('./metaphor.js');"
        "const P=require('./pipeline.js'),L=require('./pipelinelib.js');")


def _node(expr, payload=None):
    src = BOOT + ("let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{"
                  f"const a=s?JSON.parse(s):null;process.stdout.write(JSON.stringify({expr}))}})")
    out = subprocess.run(["node", "-e", src], cwd=HERE,
                         input=json.dumps(payload) if payload is not None else "",
                         capture_output=True, text=True, timeout=180)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@pytest.fixture(scope="module")
def runs():
    return _node("Object.fromEntries(L.projects.map(p=>[p.id,P.run(p)]))")


@pytest.fixture(scope="module")
def projects():
    return _node("L.projects")


def test_both_projects_are_well_formed(runs):
    for pid, r in runs.items():
        assert r["ok"] is True, f"{pid}: {r['why']}"


# ------------------------------------------------------- stage six refuses ---
def test_a_measured_result_without_a_locked_prediction_is_refused(projects):
    """The discipline of this repository, as a field that cannot be left blank.

    Every other locked file here was hashed before its data existed. A project
    that says "measured" and cannot produce the hash is claiming the thing those
    files exist to make expensive.
    """
    p = copy.deepcopy(projects[0])
    p["evidence"] = {"status": "measured", "result": "it worked"}
    why = _node("P.problems(a)", p)
    assert any("sha256 of the" in w for w in why)

    p["evidence"]["preregSha256"] = "not-a-hash"
    why = _node("P.problems(a)", p)
    assert any("sha256" in w for w in why)

    p["evidence"]["preregSha256"] = "a" * 64
    why = _node("P.problems(a)", p)
    assert why == [], "a real hash and a stated result should pass"


def test_a_shrug_with_a_label_on_is_refused(projects):
    """untestable-here without naming the missing artefact, and not-yet without
    a date, are the two ways stage six gets skipped while looking filled in."""
    p = copy.deepcopy(projects[0])
    p["evidence"] = {"status": "untestable-here"}
    assert any("shrug with a label on" in w for w in _node("P.problems(a)", p))

    p["evidence"] = {"status": "not-yet"}
    assert any("still be not-yet in a year" in w for w in _node("P.problems(a)", p))

    p["evidence"] = {"status": "definitely true"}
    assert any("must be one of" in w for w in _node("P.problems(a)", p))


def test_a_schema_that_thinks_it_proves_something_is_refused(projects):
    """A mental model organises thinking and certifies nothing. A project that
    treats its schema as a finding hands a conclusion nobody measured to
    everything downstream of it."""
    p = copy.deepcopy(projects[0])
    p["schema"]["provesNothing"] = False
    assert any("provesNothing: true" in w for w in _node("P.problems(a)", p))
    del p["schema"]["provesNothing"]
    assert any("provesNothing: true" in w for w in _node("P.problems(a)", p))


def test_a_solution_that_cannot_be_abandoned_is_refused(projects):
    """Every solution carries what would show it was the wrong thing to build.
    Without that it can only ever be defended."""
    p = copy.deepcopy(projects[0])
    del p["solutions"][0]["wrongIf"]
    assert any("cannot be abandoned" in w for w in _node("P.problems(a)", p))


def test_a_press_that_risks_nothing_is_refused(projects):
    """Stage one is audited by metaphor.js -- the same instrument used on
    MetaphorOS's pictures and this stack's own."""
    p = copy.deepcopy(projects[0])
    del p["press"]["predicts"]
    assert any("puts at risk" in w for w in _node("P.problems(a)", p))


# ------------------------------------------------------------- the finding ---
def test_both_presses_are_lenses(runs):
    for pid, r in runs.items():
        assert r["press"]["klass"] == "lens", pid
        assert r["press"]["uncontrolled"] >= 1


def test_the_claim_is_a_chain_with_no_second_route_anywhere(runs):
    """The topology finding, and it is the same for both readings.

    Every link is a sole route. There is no redundancy in this claim at all:
    people must be using assistants for things that matter before wrong answers
    cost anything, answers must be costly before a check is worth having, a
    check must exist before anyone uses it, people must use it before anyone
    pays. Each really does presuppose the last.
    """
    a = runs["check-at-the-tap"]["topology"]
    assert a["parts"] == 6 and a["links"] == 5
    assert a["soleRoutes"] == 5, "every link carries the whole load"
    assert a["conserved"] is True and abs(a["totalBearing"] - 5) < 1e-9
    assert a["restsOn"]["restsOnOneThread"] is True
    assert abs(a["restsOn"]["deepest"] - 1.0) < 1e-9


def test_the_rival_reading_needs_one_more_link_and_names_it(runs):
    """The uncomfortable result, and the reason the second press is here.

    The seatbelt reading inserts one condition the tap reading does not have --
    that the check is on by DEFAULT -- and that raises the chain from five sole
    routes to six, and the single points from four to five. If that reading is
    right, the claim needs one more thing to hold, and it is precisely the thing
    a page sold one at a time cannot buy.
    """
    a = runs["check-at-the-tap"]["topology"]
    b = runs["the-seatbelt-reading"]["topology"]

    assert b["parts"] == a["parts"] + 1
    assert b["soleRoutes"] == a["soleRoutes"] + 1 == 6
    assert len(b["singlePoints"]) == len(a["singlePoints"]) + 1 == 5

    extra = set(b["singlePoints"]) - set(a["singlePoints"])
    assert extra == {"The check is on by default"}


def test_the_conjunction_is_drawn_as_a_chain_and_not_as_a_star(projects):
    """The lesson already recorded in the Shapes library as atomic-install-list.

    Four conditions that must ALL hold, drawn as four independent supports of
    one conclusion, understate by a lot -- the twelve-asset install measured
    0.083 per asset when the truth was 1.000. So the parts are wired in series,
    each depending on the one before, and a test reads the links to make sure
    nobody quietly re-draws it as a star later.
    """
    for p in projects:
        t = p["topology"]
        conclusion = t["conclusion"]
        into_conclusion = [l for l in t["links"] if l[1] == conclusion]
        assert len(into_conclusion) == 1, \
            "more than one link straight into the conclusion means a star crept back in"
        assert len(t["links"]) == len(t["parts"]) - 1, "a chain has parts - 1 links"
        assert len(t["sources"]) == 1, "a chain is entered at one end"


def test_the_python_engine_agrees(runs, projects):
    for p in projects:
        t = p["topology"]
        links = [(a, b, w) for a, b, w in t["links"]]
        py = bearings(Structure(t["parts"], links))
        got = runs[p["id"]]["topology"]
        assert abs(py["total"] - got["totalBearing"]) < 1e-9, p["id"]
        pysp = sorted(x["part"] for x in single_points(Structure(t["parts"], links)))
        assert pysp == sorted(got["singlePoints"]), p["id"]


# -------------------------------------------------------------- the honest --
def test_neither_project_claims_a_measured_result(runs):
    """The state of this whole thing, in one assertion.

    One is not-yet with a trigger. The other is untestable-here with the missing
    artefact named. Nothing has shipped, nothing has been sold, no integrator
    exists, and every adoption figure in either project is unmeasured.
    """
    statuses = {pid: r["evidence"]["status"] for pid, r in runs.items()}
    assert statuses == {"check-at-the-tap": "not-yet",
                        "the-seatbelt-reading": "untestable-here"}
    assert "Nothing has shipped" in runs["the-seatbelt-reading"]["evidence"]["missing"]
    assert "contribution rate is absent rather than low" \
        in runs["check-at-the-tap"]["evidence"]["note"]

    for r in runs.values():
        assert "measured against a prediction locked beforehand" not in r["standing"]


def test_the_rival_press_says_it_threatens_the_business_model(runs):
    """Running one press and stopping is how a process fixes its own answer.
    The second press is here because it is the uncomfortable one, and the file
    says so rather than burying it."""
    w = runs["the-seatbelt-reading"]["press"]["where"]
    assert "RIVAL" in w and "threatens the business model" in w


# ------------------------------------------- the two stages that were missing --
def test_a_project_with_no_invariant_is_refused(projects):
    """Stage 1, and it comes BEFORE the carrier for a reason.

    Choosing the picture first is how a project ends up with a carrier picked
    for its decoration. The invariant is what survives when every particular is
    changed, and it has to be stated before anything is allowed to illustrate it.
    """
    p = copy.deepcopy(projects[0])
    del p["invariant"]
    assert any("chosen for its decoration" in w for w in _node("P.problems(a)", p))


def test_the_governability_test_refuses_a_carrier_that_cannot_fill_ten(projects):
    """Stage 3's gate, and it is what separates a picture that generates from
    one that decorates.

    A restaurant has a real procedure manual, so every element fills. A sunset
    fills none and can only illustrate. The blanks are exactly where a carrier
    will mislead, so a partial fill is refused and the missing ones are named.
    """
    p = copy.deepcopy(projects[0])
    del p["schema"]["fills"]["procedures"]
    del p["schema"]["fills"]["exceptions"]
    why = _node("P.problems(a)", p)
    assert any("8/10" in w for w in why)
    assert any("procedures, exceptions" in w for w in why)
    assert any("decorates rather than governs" in w for w in why)


def test_a_carrier_with_no_declared_leaks_is_refused(projects):
    """Every carrier permits an inference the target forbids. Naming none means
    none was looked for.

    The canonical case is the bowling ball on the trampoline: the marble rolls
    into the dip because gravity pulls it onto the sheet, so the carrier
    explains gravity by presupposing gravity. Nobody wrote that into an
    exceptions list, and it has been teaching a false inference ever since.
    """
    p = copy.deepcopy(projects[0])
    p["schema"]["leaks"] = []
    assert any("does quiet damage" in w for w in _node("P.problems(a)", p))


def test_both_projects_now_fill_all_ten_and_declare_their_leaks(runs):
    """The new gate found both worked examples incomplete -- they had been
    admitted under the weaker spec. Fixed rather than grandfathered."""
    for pid, r in runs.items():
        assert r["governability"] == "10/10", pid
        assert r["leaks"] >= 3, pid
        assert r["invariant"].strip()


def test_the_loop_rule_points_at_stage_two_not_stage_one(runs):
    """When the evidence comes back against the theories, choose another
    carrier. Reality did not fail; the picture failed to carry it.

    Newton's corpuscles died at the double slit in 1801 and optics went back
    for a new carrier, not for a new subject. Returning to stage 1 would claim
    the invariant itself was mis-stated, which is rarer and much more serious.
    """
    for r in runs.values():
        assert "return to stage 2" in r["onFailure"]
        assert "Reality did not fail" in r["onFailure"]
        assert "stage 1" in r["onFailure"] and "mis-stated" in r["onFailure"]


def test_the_twelve_by_twelve_cascade_verified_independently():
    """The arithmetic claim on the demonstration page, re-derived here rather
    than taken on trust: 144 -> 78 -> 21 -> 6 -> 1.

    And one correction. The page names 36 as the product sitting at three
    addresses. There are THREE such products, not one: 12, 24 and 36 each
    answer at three distinct doors.
    """
    from itertools import combinations_with_replacement as cwr
    from collections import Counter

    pairs = list(cwr(range(1, 13), 2))
    assert len(pairs) == 78, "144 ordered cells are 78 unordered pairs"

    gates, doubles, steps = {1, 2, 5, 9, 10, 11}, {4, 8, 12}, {3, 6}
    after_gates = [p for p in pairs if not set(p) & gates]
    after_doubles = [p for p in after_gates if not set(p) & doubles]
    after_steps = [p for p in after_doubles if not set(p) & steps]

    assert len(after_gates) == 21
    assert len(after_doubles) == 6
    assert sorted(after_doubles) == [(3, 3), (3, 6), (3, 7), (6, 6), (6, 7), (7, 7)]
    assert after_steps == [(7, 7)], "one door no rule reaches"

    counts = Counter(a * b for a, b in pairs)
    namesakes = [v for v, c in counts.items() if c > 1]
    assert len(namesakes) == 16, "sixteen products answer at more than one door"

    at_three = sorted(v for v, c in counts.items() if c >= 3)
    assert at_three == [12, 24, 36], \
        "the page names only 36; 12 and 24 also sit at three addresses"
