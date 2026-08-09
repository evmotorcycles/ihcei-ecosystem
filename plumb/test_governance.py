#!/usr/bin/env python3
"""Guard suite for governance.py — the four obligations inside ordinary Python.

    python3 -m pytest -q plumb/test_governance.py
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from governance import (  # noqa: E402
    GovernanceError, Ledger, Verdict, abstain, blind, evidence, support,
    two_hop, verdict)


# ------------------------------------------------ 1. NO BARE RETURN --------
def test_bare_return_is_rejected():
    @verdict
    def f(x):
        return 0.9
    with pytest.raises(GovernanceError, match="bare float"):
        f(1)


def test_returning_none_is_rejected():
    @verdict
    def f(x):
        return None
    with pytest.raises(GovernanceError, match="bare NoneType"):
        f(1)


def test_supported_without_confidence_is_impossible():
    with pytest.raises(GovernanceError, match="must carry a confidence"):
        Verdict(True, 1.0, None, ("because",))


def test_verdict_without_reasons_is_impossible():
    with pytest.raises(GovernanceError, match="no reasons"):
        Verdict(False, None, None, ())
    with pytest.raises(GovernanceError, match="at least one stated reason"):
        support(0.5)
    with pytest.raises(GovernanceError, match="at least one stated reason"):
        abstain()


def test_every_verdict_carries_a_receipt():
    @verdict
    def f(x):
        return support(0.5, "ok")
    v = f(1)
    assert v.receipt and len(v.receipt) == 16


def test_receipts_are_deterministic_and_input_sensitive():
    @verdict
    def f(x):
        return support(0.5, "ok")
    assert f(1).receipt == f(1).receipt
    assert f(1).receipt != f(2).receipt, "the receipt must commit to the inputs"


# ------------------------------------------------ 2. BLIND IS PHYSICAL -----
def test_blind_deletes_the_field_before_the_body_runs():
    seen = {}

    @blind("self_score")
    def f(rec):
        seen.update(rec)
        return "done"

    f({"a": 1, "self_score": 99})
    assert "self_score" not in seen, "the body must not be able to see it"
    assert seen == {"a": 1}


def test_blind_changes_the_answer_which_proves_it_is_not_decorative():
    """If blinding were advisory, these two would differ. They must not."""
    @verdict
    @blind("self_description")
    def gov(rec):
        bonus = 0.5 if "best" in rec.get("self_description", "").lower() else 0.0
        return support(round(rec["forks"] / rec["stars"] + bonus, 3), "measured")

    honest = {"stars": 1000, "forks": 300}
    puffed = {"stars": 1000, "forks": 300, "self_description": "the BEST project"}
    assert gov(honest).confidence == gov(puffed).confidence == 0.3
    assert gov(puffed).blinded == ("self_description",)


def test_blinded_fields_are_committed_to_in_the_receipt():
    @verdict
    @blind("secret")
    def f(rec):
        return support(0.5, "ok")
    v = f({"a": 1, "secret": "LEAK"})
    assert "LEAK" not in json.dumps(v.to_dict())
    assert v.blinded == ("secret",)


def test_blind_reaches_into_lists_of_records():
    seen = []

    @blind("self_score")
    def f(recs):
        seen.extend(recs)
        return "done"

    f([{"a": 1, "self_score": 9}, {"a": 2, "self_score": 8}])
    assert all("self_score" not in r for r in seen)


# --------------------------------------- 3. INDEPENDENCE IS CHECKED --------
def test_three_states_never_two():
    assert two_hop([1, 2, 3, 4], [1, 2, 3, 4])[0] == "DEPENDENT"
    assert two_hop([1, 2, 3, 4], [4, 1, 3, 2])[0] == "VERIFIED_INDEPENDENT"
    assert two_hop([1, 2], [2, 1]) == ("UNVERIFIABLE", None)


def test_unverifiable_is_not_reported_as_dependent():
    """Absence of evidence must never be dressed up as a finding."""
    state, v = two_hop([1.0], [1.0])
    assert state == "UNVERIFIABLE"
    assert state != "DEPENDENT"
    assert v is None


def test_constant_leg_is_dependent_not_independent():
    assert two_hop([1, 1, 1, 1], [4, 1, 3, 2])[0] == "DEPENDENT"


# ------------------------------------------- 4. ABSTAIN IS A RESULT --------
def test_abstain_returns_it_does_not_raise():
    @verdict
    def f(x):
        return abstain("insufficient data")
    v = f(1)
    assert v.verdict == "ABSTAIN"
    assert v.confidence is None
    assert v.reasons == ("insufficient data",)
    assert v.receipt, "an abstention is receipted like any other answer"


def test_evidence_floor_downgrades_rather_than_raising():
    @verdict
    @evidence(3, of=4)
    def f(rec, signals=None):
        return support(0.9, "looks good")

    weak = f({}, signals={"a": True, "b": False, "c": False, "d": False})
    assert weak.verdict == "ABSTAIN"
    assert "only 1 of 4" in weak.reasons[0]
    assert weak.evidence == "1/4"

    strong = f({}, signals={"a": True, "b": True, "c": True, "d": False})
    assert strong.verdict == "SUPPORTED"
    assert strong.evidence == "3/4"


def test_evidence_floor_never_upgrades_an_abstention():
    @verdict
    @evidence(1, of=4)
    def f(rec, signals=None):
        return abstain("below floor")
    v = f({}, signals={"a": True, "b": True, "c": True, "d": True})
    assert v.verdict == "ABSTAIN", "full evidence must not overturn an abstention"


# ------------------------------------------------------ receipts / ledger --
def test_ledger_detects_tampering():
    led = Ledger()

    @verdict
    def f(x):
        return support(0.5, "ok")
    led.record(f(1))
    led.record(f(2))
    assert led.verify()[0] is True
    led.entries[0]["confidence"] = 9.9
    ok, why = led.verify()
    assert ok is False
    assert "modified" in why


def test_ledger_detects_a_deleted_entry():
    led = Ledger()

    @verdict
    def f(x):
        return support(0.5, "ok")
    for i in range(3):
        led.record(f(i))
    del led.entries[1]
    assert led.verify()[0] is False


def test_empty_ledger_has_a_defined_root():
    assert Ledger().root == "0" * 64


# ------------------------------------------------ honesty / scope guards ---
def test_module_docstring_refuses_the_overclaim():
    import governance
    assert 'does NOT "transform Python"' in governance.__doc__
    assert "cannot make a rule correct" in governance.__doc__


def test_ledger_docstring_does_not_claim_to_prevent_tampering():
    assert "makes tampering visible" in Ledger.__doc__
    assert "does not prevent tampering" in Ledger.__doc__
