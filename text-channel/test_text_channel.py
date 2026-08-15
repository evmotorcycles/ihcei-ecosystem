#!/usr/bin/env python3
"""Guards for the pre-registered textual claims.

    python3 -m pytest -q text-channel/test_text_channel.py

These lock three things that are easy to lose: the pre-registration hash, the
UNTESTABLE and NOT_OPERATIONALISED verdicts (which are results, not gaps), and
the fragility of the one claim that came back SUPPORTED.
"""
import hashlib
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


@pytest.fixture(scope="module")
def res():
    out = subprocess.run(["python3", os.path.join(HERE, "text_channel.py")],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stdout + out.stderr
    return json.load(open(os.path.join(HERE, "results_text_channel.json")))


# ------------------------------------------------------------ prereg lock --
def test_prereg_and_corpus_are_locked_and_unmodified():
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json")))
    for rel, key in (("PREREG.md", "prereg_sha256"),
                     ("data/quran-uthmani.xml", "corpus_sha256")):
        got = hashlib.sha256(open(os.path.join(HERE, rel), "rb").read()).hexdigest()
        assert got == lock[key], f"{rel} changed after the pre-registration was locked"


def test_corpus_matches_the_publishers_own_checksum():
    """Provenance: the file is the publisher's, not something we assembled."""
    import re
    published = open(os.path.join(HERE, "data/quran-uthmani-md5.txt")).read()
    claimed = re.search(r"([0-9a-f]{32})", published).group(1)
    got = hashlib.md5(open(os.path.join(HERE, "data/quran-uthmani.xml"), "rb").read()).hexdigest()
    assert got == claimed == "6aae945d556a1b28cfe682c0ea5ab518"


def test_corpus_parses_to_the_expected_shape(res):
    assert res["corpus_sha256"].startswith("bb2fe2b9")
    assert res["prereg_lock_ok"] is True


# -------------------------------- claim 1: untestable is a RESULT ----------
def test_claim1_is_reported_untestable_not_quietly_dropped(res):
    c1 = res["claim1_orthographic_partition"]
    assert c1["status"] == "UNTESTABLE_AT_THIS_N"
    assert c1["total_n"] == 7
    assert c1["alif_omitted_n"] == 3 and c1["alif_retained_n"] == 4


def test_claim1_records_the_two_locations_the_proposal_omitted(res):
    """The proposal named 5 of the 7 instances. A claim about a 7-item partition
    that omits 2 of the 7 has not been checked against its own data."""
    c1 = res["claim1_orthographic_partition"]
    assert [11, 41] in [list(x) for x in c1["alif_omitted_at"]]
    assert [69, 52] in [list(x) for x in c1["alif_retained_at"]]


def test_claim1_is_not_dressed_up_as_confirmatory(res):
    c1 = res["claim1_orthographic_partition"]
    assert "DESCRIPTIVE" in c1["not_a_finding_note"]
    assert "no confirmatory weight" in c1["not_a_finding_note"]
    assert "statement about sample size" in c1["why_untestable"]


# ------------------------------- claim 2: the verdict AND its fragility ----
def test_claim2_verdict_is_as_measured(res):
    c2 = res["claim2_directed_transmission"]
    assert c2["verdict"] == "SUPPORTED"
    assert c2["difference_A_minus_B"] == 0.1534
    assert c2["permutation_p_two_sided"] < 0.01
    assert c2["gate_moved"] is False


def test_claim2_margin_over_the_gate_is_recorded_as_tiny(res):
    """0.1534 against a 0.15 gate. A verdict decided by 0.0034 must never be
    reported as a clean win."""
    c2 = res["claim2_directed_transmission"]
    margin = c2["difference_A_minus_B"] - 0.15
    assert 0 < margin < 0.005, f"margin {margin} — if this changes, re-read the claim"


def test_claim2_fragility_is_locked(res):
    """The direction is robust; the verdict is not. Both must stay on the record."""
    rob = res["claim2_robustness_post_hoc"]
    assert rob["status"] == "POST_HOC_NOT_PREREGISTERED"
    assert rob["direction_held_in_all_variants"] is True
    assert len(rob["terms_whose_removal_drops_below_gate"]) == 5, (
        "5 of 10 single-term removals dropped it below the gate; if that count "
        "changes the fragility statement must change with it")
    assert "direction robust, magnitude marginal" in rob["reading"]


def test_length_confound_was_checked_not_ignored(res):
    c2 = res["claim2_directed_transmission"]
    a = c2["length_adjusted_payload_per_10_words_A"]
    b = c2["length_adjusted_payload_per_10_words_B"]
    assert a > b, "the length-adjusted check must be reported whatever it shows"
    assert abs(c2["mean_words_A"] - c2["mean_words_B"]) < 2


def test_the_giving_verb_exclusion_is_declared_and_counted(res):
    c2 = res["claim2_directed_transmission"]
    assert c2["n_form_IV_excluded"] > 0
    txt = open(os.path.join(HERE, "PREREG.md")).read()
    assert "Form IV" in txt and "EXCLUDED and the exclusion is" in txt


# ------------------------ claim 3: not-tested is also a result -------------
def test_claim3_is_reported_not_operationalised(res):
    c3 = res["claim3_adversarial_vocabulary"]
    assert c3["status"] == "NOT_OPERATIONALISED"
    assert "choosing them chooses the answer" in c3["why"]


# ------------------------------------- the boundaries must survive edits ---
def test_the_category_boundary_is_stated(res):
    txt = open(os.path.join(HERE, "PREREG.md")).read()
    assert "No measurement of a protein\ninteractome can license a claim about the status, authorship or purpose of a\ntext." in txt.replace("**", "")
    assert any("licenses a claim about a text" in b for b in res["boundaries"])


def test_structure_is_not_claimed_to_be_purpose(res):
    assert any("Structure is evidence about a text; purpose is a claim about" in b
               for b in res["boundaries"])
    txt = open(os.path.join(HERE, "PREREG.md")).read()
    assert "would **not** license" in txt


def test_the_dataset_availability_audit_is_honest():
    txt = open(os.path.join(HERE, "PREREG.md")).read()
    for phrase in ["DOES NOT EXIST HERE",
                   "not backed by any committed data",
                   "SELF-DECLARED SIMULATION"]:
        assert phrase in txt, f"the availability audit must keep: {phrase!r}"


def test_prove_was_refused_as_a_design():
    txt = open(os.path.join(HERE, "PREREG.md")).read()
    assert "A design that sets out to prove a conclusion is not a test" in txt.replace("**", "")
