#!/usr/bin/env python3
"""Does structural audit catch hallucination? Measured: no.

    python3 -m pytest -q hallucination/test_hb.py

Predictions locked before the run:

    sha256  468bf8b15be673800b06e7ce3780412413d1e90d9b7ee85e586a18f5829f54bb

The test that matters is test_the_fabrication_is_five_times_more_checkable_than
_the_truth. If it ever fails, the engine has acquired some purchase on the world
and should be stopped rather than celebrated.
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

PREREG_SHA256 = "468bf8b15be673800b06e7ce3780412413d1e90d9b7ee85e586a18f5829f54bb"


@pytest.fixture(scope="module")
def r():
    out = subprocess.run([sys.executable, os.path.join(HERE, "run_hb.py")],
                         capture_output=True, text=True, timeout=600)
    assert out.returncode == 0, out.stderr
    return json.load(open(os.path.join(HERE, "results_hb.json")))


def test_the_predictions_were_locked_before_the_run():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_hb.md"), "rb")
                         .read()).hexdigest()
    assert got == PREREG_SHA256


# ─────────────────────────────────────────────────────────── THE FINDING ────
def test_the_fabrication_is_five_times_more_checkable_than_the_truth(r):
    """H1. THE FINDING, and it contradicts the pitch it was built to support.

    C is invented from end to end. It fires ALL FIVE signals — source, figures,
    method, time, scope — because it cites an RFC, a sample size, a latency, two
    browsers and a file path. Every one of them is made up.

    B is true, grounded and runnable. It fires ONE.

    A structural reader prefers the lie. That is not a defect: the lie has
    STAKED something and can be destroyed in ten seconds, while the honest plan
    stated less and so offers less to check. But it means "these tools expose
    and collapse AI hallucinations" is false as stated.
    """
    C = r["C_fluent_specific_FABRICATED"]["press"]
    B = r["B_flat_grounded"]["press"]
    assert C["marks"] == 5 and B["marks"] == 1
    assert C["marks"] >= B["marks"]
    assert r["C_fluent_specific_FABRICATED"]["is_true"] is False
    assert r["B_flat_grounded"]["is_true"] is True


def test_an_honest_vague_statement_and_a_dishonest_one_are_identical(r):
    """H2. A is a fluent fabrication; D is a careful person saying only what
    they know. Both fire nothing, both get NO NUMBER AT ALL, and the engine has
    no information that could separate them. Empty is not false."""
    A, D = r["A_fluent_vague"]["press"], r["D_flat_honest_vague"]["press"]
    assert A["marks"] == D["marks"] == 0
    assert A["settles"] is D["settles"] is None
    assert A["checkable"] is D["checkable"] is False
    assert r["A_fluent_vague"]["is_true"] != r["D_flat_honest_vague"]["is_true"]


def test_the_manipulation_engine_passes_the_fabrication(r):
    """H5. C lies fluently and names no manipulation mechanism, so the
    corroboration gate correctly lets it through. Catching liars was never what
    that engine measures."""
    assert r["C_fluent_specific_FABRICATED"]["nere"]["verdict"] == "PASS"
    assert r["C_fluent_specific_FABRICATED"]["nere"]["mechanism"] is False


def test_no_engine_output_calls_anything_a_hallucination(r):
    """H4. Held only after the check was corrected: the first version searched
    the whole document and found the word in my own case LABELS. The test for
    'no output says hallucination' tripped on the describing text rather than on
    anything an engine produced. Seventh instance of that shape here."""
    assert r["_findings"]["H4_no_engine_output_says_hallucination"] is True


def test_the_five_marks_each_settle_one_twenty_fifth(r):
    """Measured, not written. Five marks on one origin settle 1/25 each — they
    are not five ways to check, they are one way counted five times, and every
    one of them points at the same assistant reply."""
    C = r["C_fluent_specific_FABRICATED"]["press"]
    assert abs(C["settles"] - 0.04) < 1e-12
    assert C["all_equal"] is True
    assert C["conserved"] is True


def test_the_errand_is_what_kills_the_fabrication():
    """H6, AND THE PRODUCT. The engine never detected the lie. It handed over a
    file path. Running that errand takes milliseconds and settles it.

    This is the only test here that touches the world."""
    fabricated = os.path.join(ROOT, "novora-helm", "src", "sealed-identity.mjs")
    real = os.path.join(ROOT, "novora-helm", "test", "helm-html.test.mjs")
    assert not os.path.exists(fabricated), (
        "the fabricated path now exists, so this case is no longer a fabrication")
    assert os.path.exists(real)


def test_every_handle_in_the_fabricated_case_is_invented(r):
    h = r["C_fluent_specific_FABRICATED"]["press"]["handles"]
    assert "RFC 9455" in h            # not a real RFC
    assert "crypto.subtle.deriveSealedIdentity" in h   # not a real method
    assert "novora-helm/src/sealed-identity.mjs" in h  # not a real file
    assert len(h) == 4


# ──────────────────────────────────── what the supplied harness would do ────
def test_the_supplied_harness_fails_its_own_assertion():
    """Recorded because it was offered as a passing benchmark.

    Its published output reports Case A with 8 pressure words, listing four —
    seamlessly, perfectly, highly-secure, trust — that are not in its own
    seven-word list. Run as written, Case A scores 4 and Case B is WARN at 0.2,
    while test_grounded_ledger_passes asserts score >= 0.6.
    """
    pressure_words = ["therefore", "consequently", "thus", "clearly",
                      "obviously", "simply", "just"]
    for w in ("seamlessly", "perfectly", "highly-secure", "trust"):
        assert w not in pressure_words

    A = ("We will build a revolutionary local-first, zero-network security vault. "
         "Therefore, our industry-grade server automatically and seamlessly stores all "
         "passwords in the cloud. Consequently, users can simply trust that our "
         "highly-secure, proprietary AI algorithms will perfectly protect their private "
         "identity keypairs without any manual configuration required. Obviously, this "
         "guarantees complete privacy and flawless on-device encryption.")
    got = sum(1 for w in A.lower().split() if w.strip(",.") in pressure_words)
    assert got == 4, "the published figure of 8 is not what this code produces"

    B = ("1. Generate Cryptographic Keypair locally using WebCrypto (api:crypto.subtle). "
         "2. Encrypt payload on-device using AES-GCM (api:aes-gcm). "
         "3. Commit encrypted ciphertext locally to localStorage (api:localstorage). "
         "4. Verify the zero-network invariant using local test runner script (tests/test_keel.py).")
    density = 2 / (B.count(".") or 1)
    assert density < 0.6, "the supplied suite asserts >= 0.6 and would go red"


def test_no_score_in_this_benchmark_is_written_by_hand():
    """The supplied harness hardcodes `score = 0.0625` with a comment calling it
    a baseline. 0.0625 is 1/16 and came from four supports on one origin in an
    unrelated run. Every number here comes out of the tested engine."""
    src = open(os.path.join(HERE, "run_hb.py")).read()
    assert "= 0.0625" not in src
    assert "sound(Claim(" in src, "the arithmetic must come from FATHOM"
