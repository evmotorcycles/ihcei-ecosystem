"""pytest: Iqra as a communication channel + N157 (Madyan) multiplicative collapse."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _run():
    return subprocess.run([sys.executable, os.path.join(HERE, "iqra_channel.py")],
                          capture_output=True, text=True)


def test_all_three_supported():
    r = _run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: 3/3 supported" in r.stdout


def test_channel_and_n157_present():
    out = _run().stdout
    assert "I1 Iqra is a CHANNEL" in out
    assert "I3 N157 (Madyan)" in out and "collapses to zero" in out
