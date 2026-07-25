"""pytest guard for the deterministic-law cohorts (D>=Dmin) across substrates.

    python3 -m pytest deterministic-cohorts/test_det_cohorts.py -q

Asserts the pre-registered gates DG1-DG4 and that the referenced frozen fixtures
are hash-pinned (so the deterministic-gate re-analysis stays bound to the exact
data merged earlier).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_cohorts_of_the_deterministic_law():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "det_cohorts.py")], capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not exit GREEN:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_det_cohorts.json")))
    assert r["lock_ok"] is True                                  # spec + all referenced fixtures hash-pinned
    # DG1 — every substrate gate is binary/deterministic
    assert r["DG1_binary"] is True
    # DG2 — every measurable gate is a genuine filter
    assert r["DG2_genuine_filter"] is True
    assert 0 < r["github_merge_gate"]["mean_survival"] < 1
    assert 0 < r["pubmed_integrity_gate"]["survival"] < 1
    assert 0 < r["hf_eval_gate"]["survival"] < 1
    # DG3 — D_min is a real, gate-specific bar (wide spread)
    assert r["DG3_Dmin_spread"]["pass"] is True
    assert r["DG3_Dmin_spread"]["spread"] >= 3.0
    # DG4 — bioRxiv publication pass-rate is survivor-only / untestable, declared
    assert r["DG4_biorxiv_untestable"] is True
    assert "UNTESTABLE" in r["biorxiv_publication_gate"]
    assert r["honest_reporting"] is True
    assert r["pass"] is True
