"""pytest guard for the Two-Regime Telemetry Law.

    python3 -m pytest two-regime/test_two_regime.py -q

Asserts the pre-registered gates R1 (soft->linear), R2 (hard->threshold),
R3 (serial->quadratic), G (real GitHub deterministic gate), and independently
re-checks the two exact predictions (a line cannot fit the step; two-gate is d^2).
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_locks_match_manifest():
    spec = json.load(open(os.path.join(HERE, "prereg", "two_regime_prereg.json")))
    man = json.load(open(os.path.join(HERE, "prereg", "MANIFEST.sha256.json")))
    spec_hash = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    fix_hash = hashlib.sha256(open(os.path.join(HERE, "data", "github_pr_survival_frozen.json"), "rb").read()).hexdigest()
    assert spec_hash == man["spec_sha256"]
    assert fix_hash == man["fixture_sha256"]


def test_three_regimes_and_github_gate():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "two_regime.py")], capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not exit GREEN:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_two_regime.json")))
    assert r["lock_ok"] is True
    # R1 — soft verifier is linear (E=U*D)
    assert r["R1_soft_linear"]["pass"] is True
    assert r["R1_soft_linear"]["r2"] >= 0.98 and 0.9 <= r["R1_soft_linear"]["slope"] <= 1.1
    # R2 — hard gate is a threshold; a line provably cannot fit it (D>Dmin)
    assert r["R2_hard_threshold"]["pass"] is True
    assert r["R2_hard_threshold"]["threshold_residual"] == 0.0
    assert r["R2_hard_threshold"]["linear_residual"] > 0.0
    # R3 — two serial gates are quadratic (E=U*D^2), strictly below the linear line
    assert r["R3_serial_quadratic"]["pass"] is True
    assert r["R3_serial_quadratic"]["r2_vs_d2"] >= 0.98
    assert r["R3_serial_quadratic"]["two_at_0.5"] < r["R3_serial_quadratic"]["soft_at_0.5"]
    # G — the real GitHub deterministic gate is a genuine filter (0 < s < 1) on every clean repo
    assert r["G_github_gate"]["pass"] is True
    assert all(0 < s < 1 for s in r["G_github_gate"]["survival"].values())
    assert r["pass"] is True
