"""pytest guard for the OpenAlex LISM experiment — locks in the honest NULL.

    python3 -m pytest openalex-lism/test_openalex.py -q

This experiment's PRE-REGISTERED outcome on real data is a NULL: the locked
p90/median tail gate is not met because the OpenAlex sample is zero-inflated
(median citations = 0). The test verifies the pipeline runs on the real frozen
data, the locks hold, and the null is reported HONESTLY and reproducibly -- it
does NOT assert a hypothesis pass (there isn't one), and it confirms the gate
was not retuned.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_locks_match_manifest():
    spec = json.load(open(os.path.join(HERE, "prereg", "openalex_prereg.json")))
    man = json.load(open(os.path.join(HERE, "prereg", "MANIFEST.sha256.json")))
    spec_hash = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    fix_hash = hashlib.sha256(open(os.path.join(HERE, "data", "openalex_cohort_frozen.json"), "rb").read()).hexdigest()
    assert spec_hash == man["spec_sha256"]
    assert fix_hash == man["fixture_sha256"]


def test_reproduces_the_pre_registered_null_honestly():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "openalex_lism.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not reproduce cleanly:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_openalex.json")))
    assert r["ran_ok"] is True
    assert r["n"] == 50
    # the honest pre-registered NULL: the locked gate is NOT met, because median==0
    assert r["hypotheses_pass"] is False
    assert r["pass"] is False
    assert r["H1_citations"]["median_is_zero"] is True
    assert r["H2_references"]["median_is_zero"] is True
    assert r["H1_citations"]["pass"] is False
    assert r["H2_references"]["pass"] is False
    assert "NULL" in r["pre_registered_outcome"]
    assert r["null_by_zero_inflation"] is True
    assert r["honest_reporting"] is True
    # the concentration IS real (descriptive, non-gate) — the top work holds most citations
    assert r["descriptive_only"]["top_work_citation_share"] >= 0.5
