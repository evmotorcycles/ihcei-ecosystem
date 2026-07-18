"""pytest: F=ma / E=mc^2 as a two-hop telemetry channel — scaling, decay, stability."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from telemetry_machines import deliver, run_loop  # noqa: E402


def test_two_hop_delivery_is_multiplicative():
    # E = U * D_enc * D_dec (two lossy hops in series)
    assert abs(deliver(1.0, 1.0, 1.0) - 1.0) < 0.05
    assert abs(deliver(2.0, 0.5, 0.5) - 0.5) < 0.05
    assert deliver(1.0, 0.0, 1.0) < 0.05      # blind sensor collapses output
    assert deliver(1.0, 1.0, 0.0) < 0.05      # jammed actuator collapses output


def test_open_loop_diverges_but_low_latency_governor_stabilises():
    assert run_loop(0.0, 0)[1] is True        # no telemetry -> explodes
    assert run_loop(0.6, 1)[1] is False       # low tau_v governor -> stable machine


def test_high_latency_redestabilises():
    assert run_loop(0.6, 1)[1] is False
    assert run_loop(0.6, 8)[1] is True        # past the delay margin -> diverges again


def test_script_exits_zero_all_four():
    r = subprocess.run([sys.executable, os.path.join(HERE, "telemetry_machines.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: 4/4 verified" in r.stdout
