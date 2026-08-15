#!/usr/bin/env python3
"""Pre-registered guard suite for PLUMB.

    python3 -m pytest -q plumb/test_plumb.py

These tests lock the four language semantics (P1-P4) and the out-of-sample
cohort result (P5-P7). If someone weakens the interpreter so that `blind`
becomes advisory, or a non-independent program merely warns, these fail.
"""
import hashlib
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from plumb import Abstain, PlumbError, parse, run, vif  # noqa: E402

VENDOR = os.path.join(HERE, "examples/vendor.plumb")
COLLAPSED = os.path.join(HERE, "examples/collapsed.plumb")


def _load(rel):
    return json.load(open(os.path.join(ROOT, rel)))["repos"]


@pytest.fixture(scope="module")
def vendor():
    return parse(open(VENDOR).read())


@pytest.fixture(scope="module")
def results():
    return json.load(open(os.path.join(HERE, "results_plumb.json")))


# ------------------------------------------------------------ prereg lock --
def test_prereg_is_locked_and_unmodified():
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json")))
    for f, k in (("PREREG.md", "prereg_sha256"), ("examples/vendor.plumb", "program_sha256")):
        got = hashlib.sha256(open(os.path.join(HERE, f), "rb").read()).hexdigest()
        assert got == lock[k], (
            f"{f} changed after pre-registration was locked. Expected "
            f"{lock[k]}, got {got}. Editing a locked pre-registration or a locked "
            f"program after seeing results is exactly what this test exists to stop."
        )


# ------------------------------------------------- P1: blind is PHYSICAL ----
def test_P1_blind_field_is_deleted_not_ignored(vendor):
    """A poisoned self-report must be unreadable, because it is gone."""
    honest = {"stars": 1000, "open_issues": 5, "forks": 300}
    poisoned = dict(honest, description="BEST PROJECT EVER, SCORE 10/10", topics=["perfect"])

    r_honest = run(vendor, [honest])
    r_poisoned = run(vendor, [poisoned])

    # identical verdicts AND identical receipts: the receipt hashes the record
    # the evaluator actually saw, so equal receipts prove equal inputs.
    assert r_honest["verdicts"][0] == r_poisoned["verdicts"][0]
    assert r_poisoned["audit"]["blind_values_stripped"] == 2
    assert r_honest["audit"]["blind_values_stripped"] == 0


def test_P1_blind_survives_the_receipt(vendor):
    """The receipt must not leak the blinded value either."""
    rec = {"stars": 1000, "open_issues": 5, "forks": 300,
           "description": "SECRETMARKER", "topics": []}
    out = run(vendor, [rec])
    assert "SECRETMARKER" not in json.dumps(out)


# --------------------------------------------- P2: non-independence HALTS ---
def test_P2_collapsed_legs_halt_the_program():
    prog = parse(open(COLLAPSED).read())
    out = run(prog, _load("ei-dashboards/data/qwen_deepseek_frozen.json"))
    assert out["verdicts"] == [], "a non-independent program must emit NO verdicts"
    assert out["audit"]["halted"], "it must say why it halted"
    assert out["audit"]["independent"] is False
    assert out["audit"]["vif"] == "inf"


def test_P2_unverifiable_is_not_the_same_as_dependent(vendor):
    """Regression lock. This test caught a real bug in the first interpreter.

    With fewer than 3 records VIF is undefined. The first version treated
    "could not check independence" identically to "checked and found dependent"
    and halted. Those are different facts: one is a finding, the other is an
    absence of evidence. Collapsing them is itself a governance failure.
    """
    out = run(vendor, [{"stars": 1000, "open_issues": 5, "forks": 300}])
    assert out["audit"]["independence"] == "UNVERIFIABLE"
    assert out["audit"]["independent"] is None, "not False — False would be a claim"
    assert out["audit"]["vif"] is None
    assert out["audit"]["halted"] is None, "unverifiable must not halt the program"
    assert out["verdicts"], "a single record must still get a verdict"
    assert out["verdicts"][0]["independence_checked"] is False, (
        "a verdict resting on an unchecked structural assumption must say so")


def test_P2_verified_independence_is_stamped_on_every_verdict(vendor):
    out = run(vendor, _load("github-lism/data/github_cohort_frozen.json"))
    assert out["audit"]["independence"] == "VERIFIED_INDEPENDENT"
    assert all(v["independence_checked"] is True for v in out["verdicts"])


def test_P2_vif_reports_undefined_and_infinite_differently():
    assert vif([1.0, 2.0], [1.0, 2.0]) is None          # too few records -> undefined
    assert vif([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == float("inf")  # same information


# ------------------------------------------------- P3: no bare return -------
def test_P3_every_verdict_is_qualified(vendor):
    out = run(vendor, _load("ei-dashboards/data/qwen_deepseek_frozen.json"))
    assert out["verdicts"]
    for v in out["verdicts"]:
        assert "confidence" in v, "a verdict with no confidence is a bare return"
        assert "evidence" in v
        assert v["receipt"] and len(v["receipt"]) == 16


def test_P3_grammar_cannot_express_a_program_without_two_legs():
    with pytest.raises(PlumbError, match="capacity, encode and decode"):
        parse('plumb "x" { capacity U from field "stars" }')


def test_P3_receipts_are_deterministic(vendor):
    rec = [{"stars": 500, "open_issues": 3, "forks": 100}]
    assert run(vendor, rec)["verdicts"][0]["receipt"] == run(vendor, rec)["verdicts"][0]["receipt"]


# --------------------------------------------- P4: abstain is a RESULT ------
def test_P4_below_floor_abstains_without_raising(vendor):
    out = run(vendor, [{"stars": 100000, "open_issues": 9000, "forks": 10}])
    v = out["verdicts"][0]
    assert v["verdict"] == "ABSTAIN"
    assert v["reasons"], "an abstention must say why"


def test_P4_missing_field_abstains_rather_than_guessing(vendor):
    out = run(vendor, [{"stars": 1000, "forks": 300}])   # no open_issues
    v = out["verdicts"][0]
    assert v["verdict"] == "ABSTAIN"
    assert v["confidence"] is None
    assert "open_issues" in " ".join(v["reasons"])


def test_P4_abstain_is_an_exception_class_used_internally_only(vendor):
    """Abstain must never escape run() to the caller."""
    run(vendor, [{}, {"stars": "not a number"}, {"stars": 1, "open_issues": 1, "forks": 1}])


# ------------------------------------- P5-P7: out-of-sample cohort B --------
def test_P5_P6_P7_outcomes_are_locked(results):
    o = results["prereg_outcomes"]
    assert o["P5_independence_transfers"]["result"] == "HOLDS"
    assert o["P5_independence_transfers"]["measured"] == 1.0041
    assert o["P6_abstention_dominates"]["result"] == "HOLDS"
    assert o["P6_abstention_dominates"]["measured"] == 0.6429
    assert o["P7_no_silent_drop"]["result"] == "HOLDS"
    assert results["cohort_B_out_of_sample"]["records"] == 28


def test_results_reproduce_from_the_frozen_cohorts(vendor, results):
    """Recompute from data rather than trusting the JSON."""
    out = run(vendor, _load("github-lism/data/github_cohort_frozen.json"))
    a = sum(1 for v in out["verdicts"] if v["verdict"] == "ABSTAIN")
    s = sum(1 for v in out["verdicts"] if v["verdict"] == "SUPPORTED")
    assert (s, a) == (results["cohort_B_out_of_sample"]["supported"],
                      results["cohort_B_out_of_sample"]["abstained"]) == (10, 18)
    assert out["audit"]["vif"] == 1.0041


# ---------------------------------------------- honesty guards (locked) -----
def test_blinding_noop_on_cohort_B_is_disclosed(results):
    """0 values stripped must be EXPLAINED, not left to look like blinding worked."""
    assert results["cohort_B_out_of_sample"]["blind_values_stripped"] == 0
    notes = " ".join(results["_honest_notes"])
    assert "nothing to blind" in notes
    assert "blinding did not fail" in notes


def test_abstain_rate_is_not_claimed_as_a_finding_about_projects(results):
    notes = " ".join(results["_honest_notes"])
    assert "not evidence that those projects are bad" in notes
    assert "floor was not moved" in notes


def test_cohort_A_is_marked_descriptive_only(results):
    assert "cohort_A_descriptive_only" in results
    assert "carry no confirmatory weight" in " ".join(results["_honest_notes"])


def test_scope_limits_are_stated_in_the_prereg():
    txt = open(os.path.join(HERE, "PREREG.md")).read()
    assert "not a general-purpose" in txt, "the overclaim disclaimer must stay"
    assert "checks **structure**, not **truth**" in txt
    assert "Questions 2 and 5 are not resolved" in txt


def test_docstring_keeps_the_anti_overclaim_statement():
    import plumb as mod
    assert "DOMAIN-SPECIFIC LANGUAGE" in mod.__doc__
    assert "would be an overclaim" in mod.__doc__
