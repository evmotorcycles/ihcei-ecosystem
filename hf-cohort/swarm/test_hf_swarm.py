"""pytest: HF digital-swarm test — decay holds, revocation halts all, nulls reported honestly."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_hf_swarm_runs_and_is_honest():
    r = subprocess.run([sys.executable, os.path.join(HERE, "hf_swarm.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    res = json.load(open(os.path.join(HERE, "results_hf_swarm.json")))
    assert res["lock_ok"] is True
    assert res["honest_reporting"] is True
    assert res["pass"] is True


def test_A1_reported_underpowered_not_mined():
    res = json.load(open(os.path.join(HERE, "results_hf_swarm.json")))
    a1 = res["A1_real_lineage"]
    assert a1["valid_powered_test"] is False          # N=24 is honestly too small
    assert "INCONCLUSIVE" in a1["verdict"]


def test_A2_multihop_fidelity_decays():
    res = json.load(open(os.path.join(HERE, "results_hf_swarm.json")))
    a2 = res["A2_swarm_coupling"]
    assert a2["n_nodes"] >= 434
    assert a2["fidelity_decays"] is True and a2["decay_corr"] < -0.5   # the robust claim
    # coupling may be confirmed OR an honest null; either is a valid reported outcome
    assert "linear_wins" in a2


def test_A3_revocation_halts_every_dependent():
    res = json.load(open(os.path.join(HERE, "results_hf_swarm.json")))
    a3 = res["A3_revocation_latency"]
    assert a3["all_halted"] is True                    # safety-critical: no dependent left running
    assert a3["un_halted"] == []
    assert a3["max_tau_v_hops"] >= 1                    # finite, propagates
