"""pytest: the pre-registered LMD spacetime-verdict-matrix experiment reproduces."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_lmd_experiment_runs_green_and_locks():
    r = subprocess.run([sys.executable, os.path.join(HERE, "run_lmd.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    res = json.load(open(os.path.join(HERE, "results_lmd.json")))
    assert res["lock_ok"] is True
    # H1: metric axioms hold over >= 8640 networks, zero violations
    assert res["H1_metric"]["networks"] >= 8640
    assert res["H1_metric"]["violations"] == 0
    # H2: contraction slope is the predicted -1/2 with essentially perfect fit
    assert -0.52 <= res["H2_scaling"]["median_slope"] <= -0.48
    assert res["H2_scaling"]["min_r2"] >= 0.999
    # H3: emergent responds to coupling; the bolted-down null does not
    assert res["H3_discriminator"]["emergent_range"] > 0
    assert res["H3_discriminator"]["null_range"] == 0.0
    assert res["verdict"].startswith("EMERGENT")
    assert res["pass"] is True
