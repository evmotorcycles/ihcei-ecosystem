#!/usr/bin/env python3
"""Guards for the growth study.

    python3 -m pytest -q growth-study/test_growth.py

The important lock here is the one that keeps a SUPPORTED result discounted
because its control failed. That is the whole point of running a control.
"""
import hashlib
import json
import os
import re
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


@pytest.fixture(scope="module")
def res():
    out = subprocess.run(["python3", os.path.join(HERE, "growth.py")],
                         capture_output=True, text=True, cwd=ROOT, timeout=600)
    assert out.returncode == 0, out.stdout + out.stderr
    return json.load(open(os.path.join(HERE, "results_growth.json")))


def test_prereg_locked_before_any_statistic():
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json")))
    got = hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest()
    assert got == lock["prereg_sha256"], "PREREG.md changed after it was locked"


def test_cohorts_are_the_locked_ones(res):
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json")))
    for rel, digest in lock["cohorts"].items():
        got = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
        assert got == digest, f"{rel} changed after the pre-registration was locked"


def test_the_control_failed_and_G1_is_discounted_because_of_it(res):
    """The headline lock. G1 cleared its gate; the control did not clear its own,
    and the pre-registration said in advance to discount G1 in that case."""
    assert res["G2_capacity_rises_with_age_CONTROL"]["result"] == "FAILED"
    g1 = res["G1_composition_changed"]
    assert g1["result"] == "SUPPORTED"
    assert g1["DISCOUNTED_BY_CONTROL"] is True
    assert "THE CONTROL FAILED" in g1["HONEST_READING"]
    assert "honoured rather than" in g1["HONEST_READING"]


def test_a_supported_result_is_not_quietly_promoted(res):
    """If the control ever starts holding, the honest reading must be rewritten
    deliberately — not inherited from a run where it failed."""
    g1, g2 = res["G1_composition_changed"], res["G2_capacity_rises_with_age_CONTROL"]
    if g2["result"] == "HOLDS":
        assert g1["DISCOUNTED_BY_CONTROL"] is False
    else:
        assert g1["DISCOUNTED_BY_CONTROL"] is True


def test_G3_measures_whether_the_raw_material_exists(res):
    g3 = res["G3_evidence_mostly_absent"]
    assert g3["result"] == "SUPPORTED"
    assert g3["with_eval_results"] < 0.50
    assert g3["n"] == 43
    # the finding that matters for the tools: most models publish nothing to check
    assert g3["with_eval_results"] <= 0.30


def test_G4_popularity_is_not_evidence(res):
    g4 = res["G4_popularity_is_not_evidence"]
    assert g4["result"] == "SUPPORTED"
    assert abs(g4["r"]) < 0.30
    assert "popularity is not evidence" in g4["reading"]


def test_no_forecast_is_produced_anywhere(res):
    """G5 is a pre-registered refusal, so violating it is a test failure."""
    assert res["G5_no_forecast_produced"]["result"] == "HOLDS"
    blob = json.dumps(res) + open(os.path.join(HERE, "growth.py")).read() + \
        open(os.path.join(HERE, "PREREG.md")).read()
    for pat in (r"\$\s*\d+\s*(billion|trillion|B\b|T\b)", r"\bTAM\b",
                r"projected (users|adoption|revenue)", r"by 20\d\d we (will|expect)"):
        assert not re.search(pat, blob, re.I), f"a forecast leaked in: {pat}"


def test_survivorship_is_stated_as_the_dominant_limit(res):
    d = res["dominant_limit"]
    assert "SURVIVORSHIP" in d
    assert "denominator was deleted" in d
    notes = " ".join(res["honest_notes"])
    assert "not a growth rate" in notes
    assert "not of the field" in notes


def test_prereg_separates_the_answerable_half_from_the_unanswerable_one():
    txt = open(os.path.join(HERE, "PREREG.md")).read()
    assert "is not answerable at all" in txt
    assert "makes no growth forecast for any tool" in txt
    assert "cannot tell you whether anyone will use the tooling" in txt
