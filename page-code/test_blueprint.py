#!/usr/bin/env python3
"""Page Code's blueprint — the structure of projects an agent wrote.

    python3 -m pytest -q page-code/test_blueprint.py

Predictions locked before any import graph was looked at:

    sha256  bf47c93de29edd2cb030a23a370d04ec9e9b7e9a25132a221c6dadc36e2f1fc9

The test that matters most is test_the_reading_never_calls_a_hub_a_defect. A
module everything imports is usually the correct design. An audit that reported
it as a fault would be an oracle, and this one is not allowed to be.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

_spec = importlib.util.spec_from_file_location(
    "blueprint", os.path.join(HERE, "blueprint.py"))
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)

PREREG_SHA256 = "bf47c93de29edd2cb030a23a370d04ec9e9b7e9a25132a221c6dadc36e2f1fc9"


@pytest.fixture(scope="module")
def r():
    out = subprocess.run([sys.executable, os.path.join(HERE, "run_blueprint.py")],
                         capture_output=True, text=True, timeout=900)
    assert out.returncode == 0, out.stderr
    return json.load(open(os.path.join(HERE, "results_blueprint.json")))


def test_the_predictions_were_locked_before_any_graph_was_looked_at():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_blueprint.md"), "rb")
                         .read()).hexdigest()
    assert got == PREREG_SHA256


# ───────────────────────────────────────────────────────── the boundary ─────
def test_it_does_not_claim_to_understand_anything(r):
    assert r["_boundary"]["understands_language"] is False
    assert r["_boundary"]["proves"] == "NOTHING"
    assert bp.UNDERSTANDS_LANGUAGE is False


def test_the_reading_never_calls_a_hub_a_defect(r):
    """NULL-B1, and the reason this is an instrument rather than an oracle.

    spar/spar.py being imported by seventeen things means the project has a
    shared measurement kernel. That is correct design. The reading says where
    the load is; it is not allowed to say the load is misplaced.

    Greps the READINGS only. The first version greppped the whole document and
    failed on the boundary's own sentence -- "the reading names it, never that
    it is wrong" -- i.e. the promise not to judge tripped the search for
    judgement. Fourth time that shape has been caught in this repository.
    """
    readings = json.dumps({k: v for k, v in r.items()
                           if not k.startswith("_")}).lower()
    for w in ("defect", "bad design", "anti-pattern", "violation", "wrong",
              "unsafe", "risky", "fault", "smell"):
        assert w not in readings, f"the readout passes judgement: {w}"


def test_the_three_readouts_are_never_fused(r):
    blob = json.dumps(r).lower()
    for w in ("health_score", "overall_score", "quality_score", "grade"):
        assert w not in blob


# ─────────────────────────────────────────────────── the real predictions ───
def test_B1_and_B2_the_project_has_joints_and_is_in_pieces(r):
    """B1 and B2. NO ABSOLUTE COUNT — the same lesson as
    test_the_auditor_is_inside_the_corpus_it_measures, which I recorded one
    turn earlier and then did not apply here.

    This asserted 23 single points. Adding plumb/spec.py and plumb/emit.py made
    it 25 and the suite went red. The audit walks the repository it lives in, so
    every absolute structural count moves whenever the repository grows --
    including when it grows by the commit adding the assertion.
    """
    d = r["this_repo"]["sole_routes"]["detail"]
    assert len(d["single_points"]) >= 20
    assert d["pieces"] > 1
    # the named joints that should not vanish
    for expected in ("echo/echo.mjs", "spar/spar.py", "plexus/engines.js"):
        assert expected in d["single_points"], expected


def test_B3_most_of_what_the_agent_wrote_stands_alone(r):
    """THE FINDING. 401 files scanned, 127 in the graph, 274 isolated.

    Two thirds of the files in a large agent-built project import nothing else
    in that project. Registered in advance as the prediction I least expected to
    hold, because it bounds the reach of the whole service: on a typical file
    there is no structure to read.
    """
    c = r["this_repo"]["counts"]
    # NO ABSOLUTE FILE COUNT IS ASSERTED -- see the test below. The finding is
    # the ratio, and the ratio is what was predicted.
    assert c["files_isolated"] > c["files_in_graph"]
    assert c["files_isolated"] / c["files_scanned"] > 0.60
    assert c["files_in_graph"] >= 127


def test_the_auditor_is_inside_the_corpus_it_measures(r):
    """A DEFECT the first run of this suite found, recorded rather than hidden.

    The first version asserted files_scanned == 401. Adding this very test file
    made it 402 and the assertion failed. The audit walks the repository it
    lives in, so writing a test for a count CHANGES that count.

    Not fixable by excluding our own files -- any real customer running this on
    their repository has the same problem the moment the tool is vendored into
    it. The honest response is to assert relationships, which are stable, and
    never an absolute file count, which is not. This test exists so nobody
    reintroduces one.
    """
    src = open(os.path.join(HERE, "test_blueprint.py")).read()
    # Built rather than written literally: the first version of THIS test
    # forbade a string and then contained it, so it failed on itself. Fifth
    # instance of that shape here, and it happened inside the test recording
    # the fourth.
    for forbidden in ('files_scanned"] ' + "==",
                      'single_points"]) ' + "==",
                      'files_isolated"] ' + "=="):
        assert forbidden not in src, (
            "an absolute structural count was asserted again; it moves when a "
            "file is added, including by the commit that adds the assertion")
    assert r["this_repo"]["counts"]["files_scanned"] > 300


def test_B4_there_is_a_hub_and_it_is_imported_by_many(r):
    assert r["this_repo"]["hub"] == "echo/echo.mjs"
    assert r["this_repo"]["hub_fan_in"] == 22
    assert r["this_repo"]["hub_fan_in"] >= 5


def test_B8_the_separately_authored_stack_also_has_joints(r):
    """B8. ihcei_v3 is a frozen vendored snapshot, so an absolute count here
    would in fact be stable -- but a guard with an exception in it is a guard
    nobody trusts, so this asserts the same way the live-corpus tests do."""
    d = r["ihcei_v3"]["sole_routes"]["detail"]
    assert len(d["single_points"]) >= 4
    assert "ihcei_kernel_v3.py" in d["single_points"]
    assert r["ihcei_v3"]["hub"] == "gt_probabilistic.py"


def test_the_two_projects_are_shaped_oppositely(r):
    """Not predicted, and worth more than most of what was.

    This repository: 274 isolated vs 127 joined -- sprawling, mostly standalone.
    ihcei_v3: 6 isolated vs 20 joined -- dense and tightly wired. Same
    extractor, same day, opposite shapes. Whatever "an agent-built project looks
    like" is, it is not one thing.
    """
    a, b = r["this_repo"]["counts"], r["ihcei_v3"]["counts"]
    assert a["files_isolated"] > a["files_in_graph"]
    assert b["files_in_graph"] > b["files_isolated"]


def test_B9_the_law_holds_on_a_real_import_hub(r):
    """22 modules importing one file each settle 1/484. Arithmetic, listed as
    verification so it is not mistaken for a discovery."""
    ct = r["this_repo"]["counted_twice"]
    assert ct["status"] == "HALTED"
    assert abs(ct["detail"]["each_settles"] - 1 / 484) < 1e-12
    iv = r["ihcei_v3"]["counted_twice"]
    assert abs(iv["detail"]["each_settles"] - 1 / 36) < 1e-12


# ──────────────────────────────────────────────────── the extractor itself ──
def test_a_commented_out_import_is_not_an_edge():
    """Parsed by AST for Python, so documentation cannot become structure. This
    repository has caught the reverse mistake five times."""
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "a.py"), "w").write(
            "# import b\n'''import b'''\nimport c\n")
        open(os.path.join(d, "b.py"), "w").write("")
        open(os.path.join(d, "c.py"), "w").write("")
        g = bp.blueprint(d, "t")
        edges = [(x, y) for x, y, _ in g["project"]["links"]]
        assert ("a.py", "c.py") in edges
        assert ("a.py", "b.py") not in edges, "a comment became an edge"


def test_a_package_import_is_not_an_edge_in_this_project():
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "a.py"), "w").write("import os\nimport numpy\n")
        g = bp.blueprint(d, "t")
        assert g["project"]["links"] == []
        assert g["counts"]["external_imports_ignored"] == 2


def test_it_states_what_it_cannot_do(r):
    cannot = r["_boundary"]["cannot"]
    assert len(cannot) >= 4
    assert any("does not read code" in c for c in cannot)
    assert any("may be exactly right" in c for c in cannot)
    assert any("invisible" in c for c in cannot)
