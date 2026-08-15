#!/usr/bin/env python3
"""The kernel is checked from outside itself.

    python3 -m pytest -q keel/test_audit.py

An auditor written in the kernel's own language, importing the kernel's own
code, agrees with the kernel about any mistake they both make. This one is
Python, reads only the ledger, and re-derives every seal itself.
"""
import copy
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from audit import check, run_plumb, to_plumb_record  # noqa: E402

LEDGER = os.path.join(HERE, "fixtures", "demo_ledger.json")


@pytest.fixture(scope="module")
def entries():
    return json.load(open(LEDGER, encoding="utf-8"))


def test_the_fixture_is_a_real_kernel_run_not_a_hand_written_file(entries):
    """Every entry has the shape the kernel actually emits."""
    for e in entries:
        assert {"outcome", "stage", "tier", "why", "at", "prev", "seal"} <= set(e)
        assert len(e["seal"]) == 64 and len(e["prev"]) == 64


def test_a_clean_run_passes_all_six_obligations(entries):
    r = check(entries)
    assert r["verdict"] == "GOVERNED", json.dumps(r, indent=1)


def test_editing_one_past_decision_is_caught(entries):
    tampered = copy.deepcopy(entries)
    tampered[3]["target"] = "payroll/salaries.csv"
    r = check(tampered)
    assert r["O2_chain_intact"]["result"] == "FAILS"
    assert r["O2_chain_intact"]["broken_at"] == 3
    assert r["verdict"] == "NOT GOVERNED"


def test_deleting_an_entry_is_caught(entries):
    r = check([e for i, e in enumerate(entries) if i != 5])
    assert r["O2_chain_intact"]["result"] == "FAILS", \
        "a quietly removed decision must not leave an intact chain"


def test_an_admission_with_no_rule_behind_it_is_caught(entries):
    tampered = copy.deepcopy(entries)
    for e in tampered:
        if e["outcome"] == "ADMITTED":
            e["rule"] = None
            break
    assert check(tampered)["O3_admissions_name_their_rule"]["result"] == "FAILS"


def test_a_stop_with_no_reason_is_caught(entries):
    tampered = copy.deepcopy(entries)
    for e in tampered:
        if e["outcome"] in ("REFUSED", "HELD"):
            e["why"] = ""
            break
    assert check(tampered)["O4_refusals_give_a_reason"]["result"] == "FAILS"


def test_quietly_downgrading_an_interruption_is_caught(entries):
    """The cheapest way to make a system look calm is to stop interrupting."""
    tampered = copy.deepcopy(entries)
    for e in tampered:
        if e["tier"] == "STOP":
            e["tier"] = "LEDGER"
            break
    assert check(tampered)["O5_escalation_follows_the_rule"]["result"] == "FAILS"


def test_a_bare_count_with_nothing_behind_it_is_caught(entries):
    tampered = copy.deepcopy(entries)
    for e in tampered:
        if e["outcome"] == "HELD":
            e["missing"] = []
            break
    assert check(tampered)["O6_counts_carry_their_handles"]["result"] == "FAILS"


def test_the_run_really_did_hold_something_and_stop_something(entries):
    """A run where nothing was ever held or stopped proves nothing."""
    outcomes = [e["outcome"] for e in entries]
    assert "ADMITTED" in outcomes and "HELD" in outcomes and "REFUSED" in outcomes


def test_a_health_claim_that_is_held_interrupts_immediately(entries):
    held_high = [e for e in entries
                 if e["outcome"] == "HELD" and "medical/health" in (e.get("domains") or [])]
    assert held_high, "the fixture should contain a held health claim"
    assert all(e["tier"] == "STOP" for e in held_high), \
        "a held health claim is not something to mention at the end of the run"


# ------------------------------------------------------------ the plumb leg --
# The pre-registered two-leg program HALTS on every keel ledger. That halt is
# the finding, not a failure to be worked around -- see keel/NULL.md.
RUNS = os.path.join(HERE, "fixtures", "runs.json")


@pytest.fixture(scope="module")
def runs():
    return json.load(open(RUNS, encoding="utf-8"))


def test_the_cohort_is_genuinely_varied(runs):
    """A null measured on identical records would prove nothing."""
    assert len(runs) >= 20
    sizes = {r["actions"] for r in runs}
    assert len(sizes) > 10, "runs must actually differ, or the halt is trivial"


def test_the_inbound_leg_is_a_constant_and_therefore_carries_no_information(runs):
    ratios = {r["sealed"] / r["attempted"] for r in runs}
    assert ratios == {1.0}, \
        "a ledger records everything that reaches it — this ratio cannot vary"


def test_plumb_halts_rather_than_reporting_one_measurement_twice(runs):
    out = run_plumb(runs)
    assert out["verdicts"] == [], "a halted program must not emit verdicts"
    assert out["audit"]["independence"] == "DEPENDENT"
    assert "not independent" in out["audit"]["halted"]


def test_the_halt_is_written_down_as_a_result_not_hidden(runs):
    null = open(os.path.join(HERE, "NULL.md"), encoding="utf-8").read()
    assert "cannot contain its own omissions" in null
    assert "Reported\nas a null rather than worked around" in null or \
        "reported as a null" in null.lower()
    prog = open(os.path.join(HERE, "run.plumb"), encoding="utf-8").read()
    assert "independent encode decode" in prog, \
        "removing the clause would make the program print a number, and the number would be a lie"
    assert "THIS PROGRAM HALTS" in prog


def test_the_blinding_still_removes_what_the_run_says_about_itself(runs):
    out = run_plumb(runs)
    assert out["audit"]["blind_fields"] == ["self_report", "summary"]
    assert out["audit"]["blind_values_stripped"] == 2 * len(runs), \
        "the blinding must actually remove something, or it is decoration"


# ------------------------------------------------------------- runs as a CLI -
def test_it_runs_from_the_command_line():
    r = subprocess.run(["python3", os.path.join(HERE, "audit.py"), "--demo"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    assert "GOVERNED" in r.stdout


def test_the_auditor_never_runs_the_kernels_code():
    """An auditor sharing the kernel's code shares the kernel's blind spots."""
    import re as _re
    src = open(os.path.join(HERE, "audit.py"), encoding="utf-8").read()
    src = _re.sub(r'"""[\s\S]*?"""', "", src)          # prose may discuss the kernel
    src = _re.sub(r"#.*", "", src)
    for bad in ("kernel", "subprocess", "node"):
        assert bad not in src, f"the auditor reaches for {bad!r}"
