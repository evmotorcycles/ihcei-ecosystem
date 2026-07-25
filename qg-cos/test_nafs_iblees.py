"""pytest: Nafs (Salat*Zakat) vs Iblees (4D bias) -> Jinn = concealment, on real repos."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _run():
    return subprocess.run([sys.executable, os.path.join(HERE, "nafs_iblees.py")],
                          capture_output=True, text=True)


def test_all_four_predictions_supported():
    r = _run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: 4/4 predictions supported" in r.stdout


def test_jinn_is_concealment_and_salat_is_defense():
    out = _run().stdout
    assert "P2 Jinn = concealment" in out and "SUPPORTED" in out
    assert "P3 Salat is the defense" in out
    # Iblees strikes the Salat/decode channel, and the overpower->raw-death null is reported honestly
    assert "P1 Iblees strikes the Salat channel" in out
    assert "not archived death" in out
