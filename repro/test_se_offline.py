"""pytest: the knowledge (Barakah) cohort now reproduces OFFLINE (Jules fix).

Regenerates the deterministic SE-shaped fixture and runs se_barakah_test.py against
it with NO network, asserting the linear-adequate / channel-intact verdict. This
upgrades the knowledge cohort from network-gated to independently reproducible.
"""
import importlib.util
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIXTURE = os.path.join(HERE, "data", "se_fixture_barakah.json")

_HEAVY = ("numpy", "pandas", "scipy", "statsmodels", "sklearn")


@pytest.mark.skipif(any(importlib.util.find_spec(m) is None for m in _HEAVY),
                    reason="knowledge cohort needs numpy/pandas/scipy/statsmodels/sklearn "
                           "(see requirements.txt); stdlib arms cover the zero-dep path")
def test_se_barakah_reproduces_linear_offline():
    # 1) regenerate the fixture deterministically (seeded, no network)
    g = subprocess.run([sys.executable, os.path.join(HERE, "make_se_fixture.py")],
                       capture_output=True, text=True)
    assert g.returncode == 0, g.stdout + g.stderr
    assert os.path.exists(FIXTURE)

    # 2) run the ACTUAL knowledge-cohort test offline against it
    r = subprocess.run([sys.executable, os.path.join(ROOT, "se_barakah_test.py"),
                        "--json", FIXTURE], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    out = r.stdout
    assert "PASS (channel intact)" in out          # VIF ~ 1: a valid two-hop test
    assert "LINEAR adequate" in out                # no curvature on a no-D^2 ground truth
    assert "high-reuse E=1" in out
