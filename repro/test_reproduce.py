"""pytest wrapper: the LISM tau_v finding recomputes from committed real data."""
import json
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reproduce_tauv import mann_whitney_u, mean  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPOS = json.load(open(os.path.join(HERE, "tauv_cohort.json")))["repos"]
FAILED = [r["tau_v"] for r in REPOS if r["E"] == 0]
SURV = [r["tau_v"] for r in REPOS if r["E"] == 1]


def test_failed_repos_have_higher_tau_v():
    assert mean(FAILED) > mean(SURV)


def test_separation_is_significant_one_tailed():
    _, _, p = mann_whitney_u(FAILED, SURV)
    assert p < 0.05


def test_u_statistic_matches_known_value():
    # U=65.0 on this frozen cohort (matches scipy.mannwhitneyu exactly).
    U, _, _ = mann_whitney_u(FAILED, SURV)
    assert abs(U - 65.0) < 1e-6


def test_cohort_is_real_and_labeled():
    assert len(REPOS) == 21 and all(r["E"] in (0, 1) and r["tau_v"] >= 0 for r in REPOS)


# --- GitHub N=992 arm: the archived CI run re-hashes to the committed lock ----
def test_github_ci_spec_hash_matches_source():
    import subprocess
    r = subprocess.run(["python3", os.path.join(HERE, "verify_github_ci.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


# --- Yeast arm: VIF recomputes to ~1.003 from committed STRING (needs graphs) --
def test_yeast_vif_reproduces():
    import importlib.util
    if any(importlib.util.find_spec(m) is None for m in ("networkx", "pandas", "numpy")):
        import pytest
        pytest.skip("yeast VIF needs networkx/pandas/numpy (stdlib tau_v test covers the zero-dep path)")
    import subprocess
    r = subprocess.run(["python3", os.path.join(HERE, "reproduce_yeast.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
