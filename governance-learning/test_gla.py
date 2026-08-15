#!/usr/bin/env python3
"""Guards for the Governance Learning Algorithm.

    python3 -m pytest -q governance-learning/test_gla.py

Locks the six obligations, the pre-registration hash, and — most importantly —
the honest reading of L2, which clears its gate by about two rows.
"""
import hashlib
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
import sys  # noqa: E402
sys.path.insert(0, HERE)
from gla import (GovernanceError, GovernedLearner, Verdict, ece,  # noqa: E402
                 load, sealed_split, vif)


@pytest.fixture(scope="module")
def res():
    out = subprocess.run(["python3", os.path.join(HERE, "gla.py")],
                         capture_output=True, text=True, cwd=ROOT, timeout=900)
    assert out.returncode == 0, out.stdout + out.stderr
    return json.load(open(os.path.join(HERE, "results_gla.json")))


@pytest.fixture(scope="module")
def fitted():
    rows = load()
    tr, te = sealed_split(rows)
    return GovernedLearner().fit(tr, [r["E"] for r in tr]), te


def test_prereg_locked_before_fitting():
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json")))
    got = hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest()
    assert got == lock["prereg_sha256"], "PREREG.md changed after it was locked"


def test_split_is_sealed_not_shuffled():
    """A hash-based split cannot be re-rolled until it flatters the result."""
    rows = load()
    a1, b1 = sealed_split(rows)
    a2, b2 = sealed_split(list(reversed(rows)))
    assert {r["repo"] for r in b1} == {r["repo"] for r in b2}, (
        "the test set must not depend on input order")
    assert len(b1) + len(a1) == len(rows) == 992


# ------------------------------------------------- the six obligations -----
def test_L1_it_declines(res):
    assert res["L1_declines"]["result"] == "HOLDS"
    assert res["L1_declines"]["measured"] >= 0.10


def test_L2_holds_but_the_effect_is_noise(res):
    """The honest lock. HOLDS by the letter; the CI includes zero."""
    l2 = res["L2_selective_prediction_pays"]
    assert l2["result"] == "HOLDS"
    assert l2["ci_includes_zero"] is True, (
        "if this ever becomes False the honest reading must be rewritten, not kept")
    assert abs(l2["difference_in_rows"]) < 5
    assert "NOT distinguishable from noise" in l2["HONEST_READING"]
    assert "abstention did not hurt" in l2["HONEST_READING"]


def test_L3_blinding_is_physical(res, fitted):
    assert res["L3_blinding_is_physical"]["result"] == "HOLDS"
    m, te = fitted
    honest = dict(te[0])
    poisoned = dict(te[0], stars="999999999", archived="1")
    assert m.predict(honest).to_dict() == m.predict(poisoned).to_dict(), (
        "a blinded column must not be able to change any part of the verdict")


def test_L3_blinded_values_never_reach_the_receipt(fitted):
    m, te = fitted
    v = m.predict(dict(te[0], stars="SECRETMARKER"))
    assert "SECRETMARKER" not in json.dumps(v.to_dict())


def test_L4_independence_gate_halts(res):
    assert res["L4_independence_gate_halts"]["result"] == "HOLDS"
    rows = load()
    tr, _ = sealed_split(rows)
    m = GovernedLearner(features=("D_enc", "D_enc", "U")).fit(tr, [r["E"] for r in tr])
    assert m.halted, "a collapsed feature set must halt the fit"
    with pytest.raises(GovernanceError, match="halted at fit time"):
        m.predict(tr[0])


def test_L5_no_bare_return(res, fitted):
    assert res["L5_no_bare_return"]["result"] == "HOLDS"
    m, te = fitted
    for r in te[:25]:
        v = m.predict(r)
        assert isinstance(v, Verdict)
        assert v.reasons and v.receipt and v.evidence


def test_L5_a_verdict_without_reasons_is_impossible():
    with pytest.raises(GovernanceError, match="no reasons"):
        Verdict(1, 0.9, [], "3/3", "abc", False, (), True)
    with pytest.raises(GovernanceError, match="must carry a confidence"):
        Verdict(1, None, ["because"], "3/3", "abc", False, (), True)


def test_L6_self_training_is_refused(res):
    assert res["L6_self_training_refused"]["result"] == "HOLDS"
    rows = load()
    tr, _ = sealed_split(rows)
    with pytest.raises(GovernanceError, match="own outputs"):
        GovernedLearner().fit(tr, [r["E"] for r in tr], _source="model")


def test_L7_calibration_is_measured_with_no_gate(res):
    c = res["L7_calibration_measured_not_gated"]
    assert "no gate" in c["note"]
    assert c["ece_on_answered"] is not None
    assert c["reading"] in ("well calibrated", "usable", "POORLY CALIBRATED")


# ------------------------------------------- abstention is a real result ---
def test_it_declines_rather_than_extrapolating(fitted):
    m, te = fitted
    far = dict(te[0], U="99999", D_enc="99999", D_dec="99999")
    v = m.predict(far)
    assert v.abstained is True
    assert v.label is None
    assert "outside the range" in v.reasons[0]


def test_it_declines_when_it_is_near_indifferent(res):
    assert any("near-indifferent" in k for k in res["abstain_reasons"]), (
        "a coin flip with three decimal places is still a coin flip")


def test_missing_features_abstain_rather_than_guess(fitted):
    m, _ = fitted
    v = m.predict({"U": "1.0"})
    assert v.abstained and "missing feature" in v.reasons[0]


# --------------------------------------------------- honesty statements ----
def test_scope_limits_survive_edits(res):
    notes = " ".join(res["honest_notes"])
    assert "not predictive power" in notes
    assert "Blinding a column is not fairness" in notes
    assert "direct component of the" in notes
    src = open(os.path.join(HERE, "gla.py")).read()
    assert "can still be a" in src and "useless predictor" in src


def test_prereg_states_what_this_is_not():
    txt = open(os.path.join(HERE, "PREREG.md")).read()
    for phrase in ["Not a claim to be a good predictor",
                   "Not a general ML framework",
                   "Not fairness-tested"]:
        assert phrase in txt
