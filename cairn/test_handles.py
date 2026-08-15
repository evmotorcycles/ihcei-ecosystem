#!/usr/bin/env python3
"""The handles — what a person carries to a search engine.

    python3 -m pytest -q cairn/test_handles.py

THE CASE STUDY THIS LOCKS
-------------------------
An assistant produced: "According to a 2023 randomised trial of 240 participants
in the UK, green tea reduced self-reported stress by 12%." No such trial exists.

Cairn scored it 5 of 5. That is the CORRECT result and this file exists to keep
it that way. The Label does not adjudicate truth; it reports whether a claim is
built so that someone could go and check it. A fabrication written in the shape
of a well-specified finding is highly checkable and false at the same time, and
any change that "fixes" the 5/5 by making the score track truth would break the
one thing the tool is for.

What was missing was the next step. The label ticked "contains specific figures"
without saying WHICH, so the reader had to pull "2023 / 240 / 12% / UK" out by
hand before they could search. The handles are those spans, extracted and handed
over — and five seconds later the claim is dead.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ei_llm import assay, extract_handles, search_line  # noqa: E402

GREEN_TEA = ("According to a 2023 randomised trial of 240 participants in the UK, "
             "green tea reduced self-reported stress by 12%.")


# ----------------------------------------------- the result that must not move
def test_a_fabrication_still_scores_five_of_five():
    """Checkable is not true. This is the whole design, and it is not a bug."""
    r = assay(GREEN_TEA)
    assert r["verdict"] == "SUPPORTED"
    assert r["evidence_hits"] == 5 and r["evidence_total"] == 5


def test_the_engine_says_in_its_own_words_that_this_is_not_truth():
    r = assay(GREEN_TEA)
    assert "NOT that it is true" in r["limits"]


# ------------------------------------------------------- the handles themselves
def test_the_handles_are_the_exact_spans_someone_would_search_for():
    h = extract_handles(GREEN_TEA)
    assert h["time"] == ["2023"]
    assert h["figures"] == ["240 participants", "12%"]
    assert h["method"] == ["randomised trial"]
    assert h["scope"] == ["in the UK"]


def test_the_search_line_is_ready_to_paste():
    line = search_line(extract_handles(GREEN_TEA))
    assert line == "2023 240 participants 12% randomised trial in the UK"
    for handle in ("2023", "240", "12%", "UK"):
        assert handle in line, f"{handle} is load-bearing and must be carried over"


def test_a_claim_with_nothing_in_it_yields_no_handles():
    """Empty is the honest answer; an invented handle would be worse than none."""
    h = extract_handles("Green tea reduces stress.")
    assert search_line(h) == ""
    assert all(h[k] == [] for k in ("source", "figures", "method", "time", "scope"))


# --------------------------------------- what showing the spans made visible ---
def test_a_source_marker_is_reported_as_not_a_source_name():
    """'According to a trial' fires the source signal without naming anyone.

    The tick alone hides that. The span shows it, and the reader can see for
    themselves that there is nobody to go and ask.
    """
    h = extract_handles(GREEN_TEA)
    assert h["source"] == ["According to"]
    assert h["source_named"] is False


def test_a_real_named_source_is_recognised_as_one():
    h = extract_handles("A 2024 ONS survey of 1,180 households across the UK found energy use fell 8%.")
    assert h["source_named"] is True
    assert "ONS" in h["source"]


def test_naming_a_source_does_not_change_the_score():
    """source_named is reported, never scored. The gates are pre-registered."""
    marker = assay(GREEN_TEA)
    named = assay("According to the Lancet, a 2023 randomised trial of 240 participants "
                  "in the UK reduced self-reported stress by 12%.")
    assert marker["evidence_hits"] == named["evidence_hits"] == 5
    assert marker["handles"]["source_named"] is False
    assert named["handles"]["source_named"] is True


# ------------------------------------------------------------- the contract ---
def test_every_signal_that_fired_hands_over_at_least_one_handle():
    """A tick with nothing behind it is the thing this replaces."""
    for text in (GREEN_TEA,
                 "A 2024 ONS survey of 1,180 households across the UK found energy use fell 8%.",
                 "See https://example.gov/report for the 2019 audit of 15 clinics in the EU."):
        r = assay(text)
        for c in r["evidence"]:
            if c["hit"]:
                assert r["handles"][c["signal"]], \
                    f"{c['signal']} scored a tick for {text[:40]!r} with no span behind it"


def test_no_handle_is_invented_from_text_that_is_not_there():
    for text in (GREEN_TEA, "Green tea reduces stress.", "Epistemology is the study of knowledge."):
        h = extract_handles(text)
        for key in ("source", "figures", "method", "time", "scope"):
            for span in h[key]:
                assert span.lower() in text.lower(), f"{span!r} is not in the input"


@pytest.mark.parametrize("text", [
    "", "   ", "Green tea reduces stress.", GREEN_TEA,
    "Epistemology is the study of knowledge.",
    "I saw the Grand Canyon flying to New York.",
])
def test_handles_are_present_on_every_verdict_including_out_of_scope(text):
    r = assay(text)
    assert "handles" in r and "search_line" in r, \
        "a caller must never have to guess whether the handles are there"
    assert isinstance(r["search_line"], str)
