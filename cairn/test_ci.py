"""pytest guard for Centric Intelligence — locks the FALSIFIED calibration gate.

    python3 -m pytest cairn/test_ci.py -q

C1 came out POORLY CALIBRATED (ECE 0.3727) against a band fixed before running. That
failure is asserted here so it cannot later be smoothed away, and the band itself is
asserted so it cannot be moved.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_ci_experiment_reproduces_including_the_falsified_gate():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "ci_test.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_ci.json")))
    assert r["lock_ok"] is True and r["cohort_n"] == 22

    # C1 — THE FALSIFICATION, locked. The band must never move.
    c1 = r["C1_calibration"]
    assert c1["ece"] > 0.30                      # measured: poorly calibrated
    assert c1["band"] == "POORLY CALIBRATED"
    assert c1["falsified"] is True
    assert c1["band_moved"] is False
    assert c1["pass"] is False
    assert "<=0.15" in c1["pre_registered_band"]  # the original band, verbatim
    # direction and the user-facing consequence must stay in the record
    assert "UNDER-confident" in c1["direction"]
    assert "NOT a probability" in c1["user_consequence"]
    # every bin gap is negative (systematic under-confidence, not noise)
    assert all(b["gap"] < 0 for b in c1["bins"] if b["n"])

    # C2 / C3 — option-space and self-verifiability
    assert r["C2_option_space"]["fraction"] == 1.0
    assert r["C3_self_verifiability"]["fraction"] == 1.0

    # C4 — CI observes, never adjusts
    assert r["C4_ci_does_not_adjust_ei"]["verdicts_identical"] is True

    # C5 — stack components on the real cohort
    c5 = r["C5_stack_on_real_cohort"]
    assert c5["tamper_caught"] is True
    assert c5["page_code_default_deny"] is True
    assert len(c5["merkle_root"]) == 64
    assert len(c5["unlicensed"]) == 2            # real governance finding

    # the honest disclosures must persist
    assert "no fresh HF pull" in r["hugging_face_note"]
    assert "does NOT mean all gates passed" in r["meaning_of_pass"]
    assert r["honest_reporting"] is True


def test_console_is_offline_and_carries_measured_numbers():
    html = open(os.path.join(HERE, "console.html")).read()
    import re
    assert not re.search(r"(src|href)\s*=\s*[\"']https?:|@import|url\(https?:", html, re.I)
    assert "{{" not in html                      # every placeholder rendered
    r = json.load(open(os.path.join(HERE, "results_ci.json")))
    assert str(r["C1_calibration"]["ece"]) in html          # the real number, not a mock
    assert "calibration gate FAILED" in html                # the failure is shown, not hidden
    for app in ('data-p="ei"', 'data-p="pc"', 'data-p="helm"', 'data-p="ci"'):
        assert app in html
