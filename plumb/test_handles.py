#!/usr/bin/env python3
"""The `handles` obligation — a count never travels without what it counted.

    python3 -m pytest -q plumb/test_handles.py

WHERE THIS CAME FROM
An assistant produced a claim that scored 5 of 5 on the Label and turned out to
be entirely fabricated. The score was right: the claim really was built so that
someone could go and check it. What was missing was the next step — "5 of 5"
does not tell a reader WHICH five, so they cannot go and check any of them.

The same failure exists in a numeric verdict. `evidence 4/5` is a bare count.
`handles` makes the verdict name the signals it met, the ones it did not, and
the numbers behind them. It changes no verdict; it makes the verdict arguable.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from plumb import parse, run  # noqa: E402

COHORT = os.path.join(ROOT, "github-lism/data/github_cohort_frozen.json")
WITH = os.path.join(HERE, "examples/handles.plumb")
WITHOUT = os.path.join(HERE, "examples/vendor.plumb")


@pytest.fixture(scope="module")
def rows():
    return json.load(open(COHORT, encoding="utf-8"))["repos"]


def go(path, rows):
    return run(parse(open(path, encoding="utf-8").read()), rows)


def test_the_obligation_is_off_unless_asked_for(rows):
    """Existing pre-registered programs must be untouched by this."""
    out = go(WITHOUT, rows)
    assert out["verdicts"], "the control program should still produce verdicts"
    assert all("handles" not in v for v in out["verdicts"])


def test_declaring_handles_names_every_signal(rows):
    out = go(WITH, rows)
    assert out["verdicts"]
    for v in out["verdicts"]:
        h = v["handles"]
        assert len(h["met"]) + len(h["missing"]) == 5, "every signal is accounted for"
        got, total = v["evidence"].split("/")
        assert len(h["met"]) == int(got), "the named signals must equal the count"
        assert len(h["met"]) + len(h["missing"]) == int(total)


def test_the_numbers_behind_the_signals_are_handed_over(rows):
    v = go(WITH, rows)["verdicts"][0]
    for key in ("capacity", "encode", "decode", "weakest_leg", "floor"):
        assert key in v["handles"]["values"], f"{key} is load-bearing and must be shown"


def test_handles_change_no_verdict(rows):
    """It makes the answer checkable. It must not make it different."""
    a = go(WITHOUT, rows)["verdicts"]
    b = go(WITH, rows)["verdicts"]
    assert len(a) == len(b)
    for x, y in zip(a, b):
        assert x["verdict"] == y["verdict"]
        assert x["evidence"] == y["evidence"]
        assert x.get("confidence") == y.get("confidence")


def test_a_missing_signal_is_named_not_merely_subtracted(rows):
    """The reader must be able to see WHICH one failed, or they cannot argue."""
    out = go(WITH, rows)
    partial = [v for v in out["verdicts"] if v["handles"]["missing"]]
    assert partial, "this cohort should contain at least one incomplete record"
    for v in partial:
        for name in v["handles"]["missing"]:
            assert isinstance(name, str) and name, "a missing signal must have a name"


def test_the_example_states_the_case_that_produced_it():
    src = open(WITH, encoding="utf-8").read()
    assert "green tea" in src and "5 of 5" in src
    assert "does not change any verdict" in src
