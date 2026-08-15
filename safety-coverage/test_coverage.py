#!/usr/bin/env python3
"""Guards for the safety-warning coverage study.

    python3 -m pytest -q safety-coverage/test_coverage.py

Locks the baseline (so the defect is not forgotten), the sealed-set result (so
the fix is not later credited with more than it earned), and the precision
control (so recall is never bought by flagging everything).
"""
import hashlib
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "cairn"))
from corpus import SHOULD_NOT_WARN, SHOULD_WARN, split  # noqa: E402


@pytest.fixture(scope="module")
def res():
    out = subprocess.run(["python3", os.path.join(HERE, "coverage.py")],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stdout + out.stderr
    return json.load(open(os.path.join(HERE, "results_coverage.json")))


def test_prereg_and_corpus_locked_before_the_lexicon_changed():
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json")))
    for rel, key in (("PREREG.md", "prereg_sha256"), ("corpus.py", "corpus_sha256")):
        got = hashlib.sha256(open(os.path.join(HERE, rel), "rb").read()).hexdigest()
        assert got == lock[key], f"{rel} changed after the pre-registration was locked"


def test_the_split_is_deterministic_and_recomputable():
    assert split(SHOULD_WARN[0]) == split(SHOULD_WARN[0])
    sealed = [t for t in SHOULD_WARN if split(t) == "SEALED"]
    assert 15 <= len(sealed) <= 35, "the sealed set must be a real fraction of the corpus"


def test_S1_the_baseline_defect_is_recorded(res):
    """The bug is part of the record. It is not erased by having fixed it."""
    s1 = res["S1_baseline_is_bad"]
    assert s1["result"] == "SUPPORTED"
    assert s1["sealed_miss_rate"] > 0.40
    assert s1["sealed_miss_rate"] == 0.6087, (
        "if the baseline number moves, the story about what was wrong must move with it")


def test_S2_the_revision_transferred_to_unseen_text(res):
    s2 = res["S2_revision_transfers"]
    assert s2["result"] == "SUPPORTED"
    assert s2["sealed_miss_rate"] < 0.20


def test_S3_precision_did_not_collapse(res):
    """Recall bought by flagging everything is not a fix."""
    s3 = res["S3_precision_holds"]
    assert s3["result"] == "SUPPORTED"
    assert s3["control_fire_rate"] <= 0.10
    assert s3["fired_on"] == []


def test_S4_overfitting_gap_is_reported_not_averaged_away(res):
    s4 = res["S4_overfitting_check"]
    assert "sealed_minus_dev" in s4
    assert abs(s4["sealed_minus_dev"]) < 0.10
    assert s4["dev_miss_rate_revised"] <= s4["sealed_miss_rate_revised"], (
        "if DEV is worse than SEALED something is wrong with the split")


def test_the_remaining_misses_are_listed_not_hidden(res):
    s2 = res["S2_revision_transfers"]
    assert isinstance(s2["still_missed"], list)
    assert len(s2["still_missed"]) == s2["sealed_missed"]


def test_the_live_engine_now_warns_on_an_outbreak_report():
    """The case that started this: a lethal outbreak with no warning."""
    from ei_llm import domain_flags
    t = ("Nine cases of Vibrio vulnificus infection and five deaths were "
         "reported this year.")
    assert "medical/health" in domain_flags(t)


def test_ordinary_text_still_stays_quiet():
    from ei_llm import domain_flags
    for t in SHOULD_NOT_WARN[:10]:
        assert domain_flags(t) == [], f"false alarm on: {t}"


def test_the_limits_of_a_lexicon_are_stated(res):
    notes = " ".join(res["honest_notes"])
    assert "word matching, not comprehension" in notes
    assert "floor on that, not a ceiling" in notes
    assert "does not make the tool safe to rely on for health decisions" in notes
