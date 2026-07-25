"""pytest: ADG/TQG-CFE address Wolfram (computational universe) & Hoffman (interface theory)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _run():
    r = subprocess.run([sys.executable, os.path.join(HERE, "experiment_wolfram_hoffman.py")],
                       capture_output=True, text=True)
    return r


def test_experiment_exits_zero_and_all_four_supported():
    r = _run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: 4/4 predictions supported" in r.stdout


def test_w1_substrate_independence_supported():
    assert "W1 SUBSTRATE INDEPENDENCE" in _run().stdout


def test_w2_process_dominates_static_snapshot():
    out = _run().stdout
    assert "W2 COMPUTATIONAL IRREDUCIBILITY" in out and "DOMINATES" in out


def test_h1_interface_rendering_and_h2_linear_decay():
    out = _run().stdout
    assert "H1 INTERFACE RENDERING" in out
    assert "H2 FBT PERSISTENCE" in out and "adjusted R2 prefers LINEAR" in out
