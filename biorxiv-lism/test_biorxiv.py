"""pytest guard for the bioRxiv LISM enforcement-latency (tau_v) experiment.

    python3 -m pytest biorxiv-lism/test_biorxiv.py -q

Runs the real, offline experiment on the frozen, SHA-256-locked fixture and asserts
the pre-registered outcomes: locks intact, H1 heavy tail PASS, H2 field variation PASS,
H3 coupling honestly declared UNTESTABLE. stdlib only, $0.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_locks_match_manifest():
    spec = json.load(open(os.path.join(HERE, "prereg", "biorxiv_prereg.json")))
    man = json.load(open(os.path.join(HERE, "prereg", "MANIFEST.sha256.json")))
    spec_hash = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    fix_hash = hashlib.sha256(
        open(os.path.join(HERE, "data", "biorxiv_cohort_frozen.json"), "rb").read()
    ).hexdigest()
    assert spec_hash == man["spec_sha256"], "prereg spec hash drifted from manifest"
    assert fix_hash == man["fixture_sha256"], "frozen fixture hash drifted from manifest"


def test_experiment_runs_green_and_reports_honestly():
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "biorxiv_tau_v.py")],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, "runner did not exit GREEN:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_biorxiv.json")))
    assert r["lock_ok"] is True
    assert r["n"] == 40
    # H1: tau_v is heavy-tailed (the hazard signature) -- mean > median, wide upper tail
    assert r["H1_heavy_tail"]["pass"] is True
    assert r["H1_heavy_tail"]["mean"] > r["H1_heavy_tail"]["median"]
    assert r["H1_heavy_tail"]["tail_ratio"] >= 2.0
    # H2: latency differs across scientific fields
    assert r["H2_field_variation"]["pass"] is True
    assert r["H2_field_variation"]["ratio"] >= 2.0
    # H3: coupling honestly declared untestable on this metadata (construct validity)
    assert "UNTESTABLE" in r["H3_coupling"]
    assert r["honest_reporting"] is True
    assert r["pass"] is True
