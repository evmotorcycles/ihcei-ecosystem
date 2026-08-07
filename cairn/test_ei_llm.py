"""pytest guard for the Cairn EI engine and Hinton's Grand Canyon test.

    python3 -m pytest cairn/test_ei_llm.py -q

Locks the engine's behaviour AND — just as hard — its declared limits. H5 is the
anti-overclaim control: it asserts that the engine flags a structurally identical
sentence in which both readings are plausible, which demonstrates that it is doing
syntactic pattern matching and NOT understanding. If anyone later rewrites the
results to claim comprehension, these assertions break.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ei_llm import assay, IMMOBILE                              # noqa: E402


def test_engine_declines_on_underdetermined_text():
    r = assay("I saw the Grand Canyon flying to Chicago.")
    assert r["verdict"] == "AMBIGUOUS"
    assert r["committed_answer"] is None          # it must NOT pick a reading
    assert len(r["ambiguity"]["readings"]) == 2
    assert r["question"]                           # it must ask
    assert r["abstained"] is True
    # the absurd reading is flagged, the ordinary one is not
    by_id = {x["id"]: x for x in r["ambiguity"]["readings"]}
    assert by_id["A"]["plausible"] is True
    assert by_id["B"]["plausible"] is False


def test_disambiguated_text_is_not_flagged():
    r = assay("I was flying to Chicago and I saw the Grand Canyon.")
    assert r["ambiguity"]["ambiguous"] is False    # the flag tracks structure


def test_engine_never_claims_understanding():
    r = assay("The Grand Canyon was flying to Chicago.")
    assert r["verdict"] == "IMPLAUSIBLE"
    assert "NOT comprehension" in r["implausible"]["basis"]
    assert "does not understand language" in r["limits"]


def test_revision_is_auditable():
    a = assay("I saw the Grand Canyon flying to Chicago.")
    b = assay("No, it was me flying to Chicago.", parent_receipt=a["receipt"])
    assert b["parent_receipt"] == a["receipt"]     # prior state is retained and linked
    assert b["receipt"] != a["receipt"]


def test_hinton_experiment_reproduces_including_its_limits():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "hinton_test.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_hinton.json")))
    assert r["lock_ok"] is True
    assert r["H1_ambiguity_not_committed"]["committed_answer"] is None
    assert r["H1_ambiguity_not_committed"]["readings"] == 2
    assert r["H2_disambiguated_resolves"]["ambiguous"] is False
    assert r["H3_impossible_flagged"]["verdict"] == "IMPLAUSIBLE"
    assert r["H4_revision_auditable"]["chained"] is True

    # H5 — THE ANTI-OVERCLAIM CONTROL. Passing this LIMITS the claim: the engine
    # flags a sentence where both readings are fine, proving pattern-matching.
    h5 = r["H5_anti_overclaim_control"]
    assert h5["ambiguity_flagged"] is True
    assert h5["both_readings_plausible"] is True
    assert "not comprehension" in h5["conclusion"].lower()
    assert h5["pass"] is True

    # the disclaimers must stay in the emitted record
    assert "does not refute Hinton" in r["what_this_does_not_show"]
    assert "failure modes" in r["what_it_does_show"]
    assert str(len(IMMOBILE)) in r["declared_limitation"]
    assert r["honest_reporting"] is True
    assert r["pass"] is True
