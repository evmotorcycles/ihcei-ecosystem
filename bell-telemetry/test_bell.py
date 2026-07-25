"""pytest guard for the Bell Monitor (device-independent nonlocality telemetry).

    python3 -m pytest bell-telemetry/test_bell.py -q

Locks the proven-physics constants and the tool's regime classification:
  P1  the local (hidden-variable) bound is EXACTLY 2; a shared-cause source stays LOCAL.
  P2  the quantum Tsirelson value is 2*sqrt(2); the MC singlet source CERTIFIES a violation.
  P3  the PR box (S=4) is rejected as BEYOND_TSIRELSON_INVALID; quantum/classical classify right.
  P4  the device-independent independence gate: collusion doesn't certify, entanglement does.
Fixed seeds make every Monte-Carlo number reproducible.
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TSIRELSON = 2.0 * math.sqrt(2.0)


def test_bell_monitor():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "bell_monitor.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, "runner did not exit GREEN:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_bell.json")))
    assert r["lock_ok"] is True
    assert abs(r["tsirelson_bound"] - TSIRELSON) < 1e-12

    # P1 -- classical bound is exactly 2; a shared-cause source cannot certify a violation.
    p1 = r["P1_classical"]
    assert abs(p1["bruteforce_max"] - 2.0) < 1e-12
    assert p1["mc_S"] < 2.0
    assert p1["regime"] == "LOCAL"
    assert p1["pass"] is True

    # P2 -- 'not locally real': quantum reaches 2*sqrt(2); the MC violation is certified.
    p2 = r["P2_quantum"]
    assert abs(p2["analytic_S"] - TSIRELSON) < 1e-6
    assert abs(p2["mc_S"] - TSIRELSON) < 0.05
    assert p2["sigma_over_2"] > 5.0
    assert p2["certified_nonlocal"] is True
    assert p2["regime"] == "NONLOCAL_CERTIFIED"
    assert p2["pass"] is True

    # P3 -- Tsirelson ceiling as an un-gameable fraud detector.
    p3 = r["P3_tsirelson"]
    assert abs(p3["pr_box_S"] - 4.0) < 1e-6
    assert p3["pr_regime"] == "BEYOND_TSIRELSON_INVALID"
    assert p3["quantum_regime"] == "NONLOCAL_CERTIFIED"
    assert p3["classical_regime"] == "LOCAL"
    assert p3["pass"] is True

    # P4 -- device-independent independence gate (the LISM bridge).
    p4 = r["P4_lism_bridge"]
    assert p4["collusion_certifies"] is False
    assert p4["entangled_certifies"] is True
    assert p4["pass"] is True

    assert r["honest_reporting"] is True
    assert r["pass"] is True
