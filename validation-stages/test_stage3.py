"""pytest: Stage 3 swarm fidelity — decay with hop depth + linear (not quadratic) coupling."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_swarm_fidelity_decays_and_couples_linearly():
    r = subprocess.run([sys.executable, os.path.join(HERE, "stage3_swarm.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    res = json.load(open(os.path.join(HERE, "results_stage3.json")))
    assert res["n_nodes"] >= 434
    assert res["fidelity_decays_with_depth"] is True
    assert res["linear_coupling_wins"] is True
    assert res["r2_linear"] > res["r2_quadratic"]
