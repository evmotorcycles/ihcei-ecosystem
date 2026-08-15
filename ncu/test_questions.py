#!/usr/bin/env python3
"""The distinction between a check and an answer has to be enforced, not asserted.

    python3 -m pytest -q ncu/test_questions.py
"""
from __future__ import annotations

import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from ncu.questions import ANSWERS, CANNOT, STAMP, build, render  # noqa: E402


def test_all_five_questions_are_stated():
    """plumb/GOVERNANCE_VS_RT.md names Q2 and Q5 as unresolved and never says
    what they are. A boundary you have not written down is a gap with a label."""
    qs = build()
    assert [q.n for q in qs] == [1, 2, 3, 4, 5]
    for q in qs:
        assert q.asks.endswith("?"), f"Q{q.n} does not state a question"
        assert len(q.asks) > 40, f"Q{q.n}'s question is a stub"
        assert len(q.why_no_measurement_answers_it) > 80


def test_the_repo_still_names_two_questions_it_never_stated():
    """The gap this file closes. If GOVERNANCE_VS_RT.md is ever updated to state
    Q2 and Q5 itself, this test should be deleted -- not silenced."""
    src = open(os.path.join(ROOT, "plumb", "GOVERNANCE_VS_RT.md"), encoding="utf-8").read()
    assert "Q2 and Q5 are not resolved" in src
    assert not re.search(r"###\s*Q2\s*—", src), \
        "GOVERNANCE_VS_RT.md now states Q2; update ncu/questions.py's premise"
    assert not re.search(r"###\s*Q5\s*—", src)


def test_no_question_is_recorded_as_answered():
    """The count of substantive answers from measurement is zero and stays zero.
    Adding checks is not adding answers, and this is the line most likely to be
    crossed by someone summarising the work in good faith."""
    assert ANSWERS == "SUBSTANTIVE ANSWERS FROM MEASUREMENT: 0 of 5"
    blob = " ".join(
        [q.asks + q.why_no_measurement_answers_it for q in build()]
        + [c.checks + c.does_not_supply for c in (q.check for q in build()) if c])
    for banned in ("answers the question", "this answers", "proves that", "shows that"):
        assert banned not in blob.lower(), f"a check is claiming to answer: {banned!r}"


def test_every_check_cites_a_number_that_is_on_disk():
    """A check that cannot be re-read is a claim. build() calls _read at import
    time, so a missing file or field raises before any of this runs -- this test
    additionally requires the value to be real rather than a placeholder."""
    for q in build():
        if q.check is None:
            continue
        assert os.path.exists(os.path.join(ROOT, q.check.source)), \
            f"Q{q.n} cites a file that does not exist"
        assert q.check.value is not None
        assert q.check.field.count(".") >= 1


def test_every_check_declares_what_it_does_not_supply():
    """The half that gets dropped when a result is repeated by someone else."""
    for q in build():
        if q.check is None:
            continue
        assert len(q.check.does_not_supply) > 30, \
            f"Q{q.n}'s check does not say what it fails to cover"


def test_every_figure_carries_the_stamp_and_it_is_not_editable():
    for q in build():
        assert q.figures, f"Q{q.n} has no figure, so nothing carries its meaning"
        for f in q.figures:
            assert f.proves == STAMP
        d = q.as_dict()
        for f in d["figures"]:
            assert f["proves"] == STAMP


def test_a_tampered_stamp_is_refused():
    """Otherwise the assertion above is decorative."""
    import dataclasses

    from ncu.questions import Figure, Question
    bad = Question(n=9, name="x", asks="?" * 41,
                   why_no_measurement_answers_it="y" * 81, check=None,
                   figures=[dataclasses.replace(
                       Figure(figure="f", drawn_from="d", schema="s"),
                       proves="PROVES: SOMETHING")])
    with pytest.raises(AssertionError, match="stamp is not editable"):
        bad.as_dict()


def test_the_two_newly_checked_questions_are_the_ones_that_were_open():
    r = render()
    assert set(r["newly_checked"]) == {"Scope", "Disclosure"}
    assert r["checked"] == 5


def test_the_disclosure_check_declares_the_boundary_it_cannot_cross():
    """Q5 is the one where a passed check most resembles an answer. The limit --
    a computable blind spot is not an omission -- has to be in the record."""
    q5 = [q for q in build() if q.n == 5][0]
    assert "cannot contain its own omissions" in q5.why_no_measurement_answers_it
    assert "cannot COMPUTE" in q5.check.does_not_supply
    assert "provably not the second" in q5.check.does_not_supply


def test_no_philosophy_vocabulary_leaks_into_a_measurement_module():
    """The valve, still one-way. These terms live in ncu/ and nowhere else."""
    terms = ("Nafs", "Salat", "Zakat", "NCU")
    measured = []
    for pkg in ("smi", "spar", "plumb", "keel", "lism-cohorts", "swarm-lmd"):
        d = os.path.join(ROOT, pkg)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.endswith((".py", ".js")):
                measured.append(os.path.join(d, fn))
    assert len(measured) > 15, "the scan found almost no measurement modules"
    for path in measured:
        body = open(path, encoding="utf-8").read()
        for t in terms:
            assert t not in body, f"{os.path.relpath(path, ROOT)} mentions {t}"


def test_the_cannot_statement_is_unambiguous():
    for phrase in ("A check is not an answer", "a figure is not evidence",
                   "one direction"):
        assert phrase in CANNOT
