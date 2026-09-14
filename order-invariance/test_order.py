#!/usr/bin/env python3
"""A next-token reading and a structural reading, on one document.

    python3 -m pytest -q order-invariance/test_order.py

Predictions locked before the run:

    sha256  9c9872e465270422bd30093720255a97b2d48ebba995589a994f987e23e3c40f

All six held. The one that came back STRONGER than predicted is qualified in
test_the_qualification_found_by_asking_why_it_was_exactly_zero, because "exactly
zero" turned out to be a property of this graph rather than a guarantee of the
engine.
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

PREREG_SHA256 = "9c9872e465270422bd30093720255a97b2d48ebba995589a994f987e23e3c40f"


@pytest.fixture(scope="module")
def r():
    out = subprocess.run([sys.executable, os.path.join(HERE, "run_order.py")],
                         capture_output=True, text=True, timeout=900)
    assert out.returncode == 0, out.stderr
    return json.load(open(os.path.join(HERE, "results_order.json")))


def test_the_predictions_were_locked_before_the_run():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_order.md"), "rb")
                         .read()).hexdigest()
    assert got == PREREG_SHA256


def test_the_reading_says_where_it_came_from(r):
    """A hand-drawn link needs a `where`. CLAUDE.md, and test_metaphor.py
    refuses one without."""
    assert "uploaded PDF" in r["where"]
    assert "will not make any sense to you" in r["where"]


# ─────────────────────────────────────────────────────── the structure ──────
def test_N1_three_passages_on_one_method_settle_one_ninth(r):
    """The document cites three passages and declares one method required to
    read any of them. So they are not three supports; they are one support
    counted three times, and each single check settles 1/9.

    NULL-N4 applies: this is not a criticism. A shared method being load-bearing
    is what a method IS."""
    assert r["N1_three_on_one_settles_one_ninth"] is True
    for s in r["structure"]["settles"]:
        assert abs(s - 1 / 9) < 1e-9
    assert r["structure"]["conserved"] is True
    assert r["structure"]["total_bearing"] == 4.0


def test_N2_the_declared_method_is_the_only_cut_vertex(r):
    assert r["N2_method_is_a_cut_vertex"] is True
    assert r["structure"]["single_points"] == ["the one declared method"]


def test_N6_prerequisites_are_not_evidence(r):
    """The document lists prior segments a reader must watch. Those are
    prerequisites for the READER, not supports for the claim, and they do not
    enter the graph. Absence of an edge is absence of a declaration."""
    assert r["N6_prerequisites_absent_from_support_graph"] is True


# ──────────────────────────────────── the answer to the actual question ─────
def test_N3_shuffling_the_input_does_not_move_the_structural_reading(r):
    """THE ANSWER. 500 random shuffles of the order in which parts and links are
    presented. Worst deviation across all of them: 0.0.

    There is no first node and no last node. Effective resistance is computed
    from the whole Laplacian at once, so "next" is not a thing the engine has.
    """
    assert r["N3_permutations"] == 500
    assert r["N3_worst_deviation"] == 0.0
    assert r["N3_invariant"] is True


def test_N3_reading_it_backwards_changes_nothing(r):
    """Reverse the presentation entirely -- the structural analogue of reading
    the document back to front -- and the numbers are identical."""
    assert r["N3_reversed_identical"] is True


def test_N4_renaming_every_node_changes_nothing(r):
    """Mask each label to an opaque token. The engine never read the words, so
    there is nothing for the renaming to take away."""
    assert r["N4_invariant_under_renaming"] is True
    assert r["N4_mask_deviation"] == 0.0


def test_N5_the_next_token_proxy_collapses_under_the_same_shuffle(r):
    """THE CONTRAST. A bigram next-word model fitted on this document's own
    text. Shuffle the sentences and the words inside them -- the same operation
    the structural reading ignored completely -- and mean log-probability falls
    from -4.900 to -6.062, a drop of 1.162 nats.

    NOT an LLM, and no claim is made about what one would output. The proxy
    shares exactly one property with a language model: it predicts a next token
    from a previous one. That property is what the shuffle destroys.
    """
    p = r["N5_proxy"]
    assert p["drops"] is True
    assert p["mean_logprob_original"] == -4.899789
    assert p["mean_logprob_shuffled"] == -6.061812
    assert abs(p["drop"] - 1.162022) < 1e-6
    assert p["n_sentences"] == 97


def test_the_qualification_found_by_asking_why_it_was_exactly_zero(r):
    """N3 came back at EXACTLY 0.0, which is stronger than the < 1e-12 I
    predicted. Checking why found that it is a property of this graph, not a
    guarantee of the engine.

    Structure.index() is list position, so node order DOES reach the matrix and
    the eigendecomposition runs in a different operation order. Over 40 random
    graphs and 480 permutations, 440 differed -- worst deviation 1.499e-14.

    So the honest statement is: order-invariant as ARITHMETIC, not bit-identical
    in floating point. Exactly what mask.js already recorded at 5.55e-16 for
    renaming. The contrast with the next-token proxy survives it and then some:
    1.5e-14 against 1.162, thirteen orders of magnitude apart.
    """
    assert r["N3_general_that_differed"] == 440
    assert r["N3_general_permutations"] == 480
    assert r["N3_bit_identical_in_general"] is False
    assert r["N3_same_to_tolerance"] is True
    assert r["N3_general_worst_deviation"] < 1e-13
    # and the gap that matters
    assert r["N5_proxy"]["drop"] / r["N3_general_worst_deviation"] > 1e12


def test_the_engine_never_read_a_word_of_the_document(r):
    """NULL-N3, asserted rather than trusted. Every label is a placeholder the
    reader assigned; the document's own vocabulary appears nowhere in the
    structural reading."""
    blob = json.dumps(r["structure"]).lower()
    for w in ("pomegranate", "surah", "quran", "verse", "juice", "press"):
        assert w not in blob, f"the structural reading contains a word: {w}"


def test_order_invariance_is_not_claimed_as_a_virtue():
    """NULL-N1, which is the half that keeps this honest: order-invariance is
    the right property for reading a structure and the WRONG one for reading
    prose. 'A therefore B' is not 'B therefore A', and the engine is blind to
    that. Whoever draws the arrow backwards gets a confident, stable, wrong
    number."""
    import re as _re
    txt = _re.sub(r"\s+", " ", open(os.path.join(HERE, "prereg_order.md")).read())
    low = txt.lower()
    assert "order-invariance is not a virtue" in low
    assert "wrong** property for reading prose" in low
    assert "confident, stable, wrong number" in low
