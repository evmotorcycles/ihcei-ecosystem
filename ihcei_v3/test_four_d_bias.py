"""pytest: the IHCEI 4D Bias Engine localizes the fatal bias channel on real repos."""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "repro"))
from four_d_bias import score_repos, DIMS  # noqa: E402
from reproduce_tauv import mann_whitney_u, mean  # noqa: E402

REPOS = json.load(open(os.path.join(ROOT, "adg-tqg", "fixtures", "experiment_cohort.json")))["repos"]


def test_scores_are_nonnegative_and_have_four_dims():
    for r in score_repos(REPOS):
        assert all(r[d] >= 0.0 for d in DIMS)
        assert abs(r["load"] - sum(r[d] for d in DIMS)) < 1e-9
        assert r["dominant"] in DIMS + ["-"]


def test_communication_channel_is_the_fatal_bias():
    rows = score_repos(REPOS)
    surv = [r for r in rows if r["E"] == 1]
    fail = [r for r in rows if r["E"] == 0]
    _, _, p = mann_whitney_u([r["Communication"] for r in fail], [r["Communication"] for r in surv])
    assert p < 0.05
    assert mean([r["Communication"] for r in fail]) > mean([r["Communication"] for r in surv])


def test_vanity_channels_are_honest_nulls():
    # Moral/Temporal fire on healthy famous repos and must NOT predict failure.
    rows = score_repos(REPOS)
    surv = [r for r in rows if r["E"] == 1]
    fail = [r for r in rows if r["E"] == 0]
    for dim in ("Moral", "Temporal"):
        _, _, p = mann_whitney_u([r[dim] for r in fail], [r[dim] for r in surv])
        assert p >= 0.05  # reported honestly as a null, not massaged


def test_script_exits_zero_localizing_a_fatal_channel():
    r = subprocess.run([sys.executable, os.path.join(HERE, "four_d_bias.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "FATAL BIAS (localized): Communication" in r.stdout
