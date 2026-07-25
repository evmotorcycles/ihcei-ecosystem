"""pytest: the four-cohort LISM meta-test locks, recomputes live, and stays honest."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _run():
    r = subprocess.run([sys.executable, os.path.join(HERE, "meta_lism.py")],
                       capture_output=True, text=True)
    return r


def test_meta_runs_green_and_locks():
    r = _run()
    assert r.returncode == 0, r.stdout + r.stderr
    res = json.load(open(os.path.join(HERE, "results_meta.json")))
    assert res["lock_ok"] is True
    assert res["pass"] is True
    assert res["honest_reporting"] is True


def test_all_four_cohorts_favor_linear():
    res = json.load(open(os.path.join(HERE, "results_meta.json")))
    c = res["cohorts"]
    assert c["A_yeast"]["N"] == 4825 and c["A_yeast"]["pass"] is True
    assert c["B_github"]["N"] == 992 and c["B_github"]["match"] is True
    assert c["C_knowledge"]["N"] == 793 and c["C_knowledge"]["pass"] is True
    assert c["D_swarm"]["N"] == 500 and c["D_swarm"]["linear_wins"] is True


def test_swarm_decays_and_beats_quadratic_live():
    res = json.load(open(os.path.join(HERE, "results_meta.json")))
    d = res["cohorts"]["D_swarm"]
    assert d["decays"] is True and d["decay_corr"] < -0.5
    assert d["r2_linear"] > d["r2_quadratic"]


def test_github_hash_attests_live():
    res = json.load(open(os.path.join(HERE, "results_meta.json")))
    b = res["cohorts"]["B_github"]
    assert b["live_spec_hash"] == b["archived_ci_hash"]


def test_negatives_register_is_emitted():
    # the honest nulls/negatives must be present — hiding them would be the failure mode
    res = json.load(open(os.path.join(HERE, "results_meta.json")))
    reg = res["negatives_register"]
    assert len(reg) >= 6
    joined = " ".join(reg).lower()
    assert "untestable" in joined and "null" in joined and "inconclusive" in joined
