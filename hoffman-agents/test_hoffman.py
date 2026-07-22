"""pytest: the Hoffman conscious-agent simulation — FBT control + tau_v coherence hold,
P2 coupling reported honestly."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_runs_green_and_locks():
    r = subprocess.run([sys.executable, os.path.join(HERE, "hoffman_sim.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    res = json.load(open(os.path.join(HERE, "results_hoffman.json")))
    assert res["lock_ok"] is True and res["honest_reporting"] is True and res["pass"] is True


def test_P1_is_a_genuine_hoffman_world():
    res = json.load(open(os.path.join(HERE, "results_hoffman.json")))
    # FBT: fitness-tuned strategy outcompetes truth-tuned (the substrate is a real Hoffman world)
    assert res["P1_fbt"]["fbt_reproduced"] is True
    assert res["P1_fbt"]["fitness_final_share"] > 0.60


def test_P2_coupling_reported_with_direction():
    res = json.load(open(os.path.join(HERE, "results_hoffman.json")))
    p2 = res["P2_lism"]
    # either a clean linear win OR an honest weak/null — but the direction must be recorded
    assert "linear_wins" in p2 and "linear_directionally_beats_quad" in p2


def test_P3_tau_v_predicts_coherence():
    res = json.load(open(os.path.join(HERE, "results_hoffman.json")))
    p3 = res["P3_tau_v"]
    assert p3["predicts"] is True and p3["corr_tau_coherence"] < -0.5
