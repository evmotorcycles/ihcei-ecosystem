"""
test_replication.py — locks the N=44 replication, which went the WRONG way.

At N=27 the banking design scored 2/4 and its portfolio gate (B3) survived.
At N=44, on a larger COMMITTED cohort using the SAME locked gates, it scores 1/4:
B3 collapsed to an exact tie. The decoupled-underwriting claim is not supported.

This suite exists so that result cannot later be softened, re-specified, or quietly
replaced by the smaller, friendlier N=27 run.
"""
import csv
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "fbe085fcf4cc2a7f5b3bf386a7e81f1542cda6f6f826996ca75ef41162f0d62a"


def test_replication_reproduces_and_the_thesis_stays_falsified():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "replication_n44.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_replication_n44.json")))

    # the gates were NOT re-specified between runs
    assert r["spec_sha256_canonical"] == LOCKED

    # --- the cohort is genuinely committed (the N=992 failure mode cannot recur) ---
    csv_path = os.path.join(ROOT, "data", "github", "cohort_real_n44.csv")
    assert os.path.exists(csv_path), "the replication cohort must be committed, not ephemeral"
    rows = list(csv.DictReader(open(csv_path)))
    assert len(rows) == 44 and sum(int(x["default"]) for x in rows) == 13
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch",
                              "data/github/cohort_real_n44.csv"],
                             cwd=ROOT, capture_output=True, text=True)
    assert tracked.returncode == 0, "cohort CSV exists on disk but is NOT git-tracked"

    assert r["N"] == 44 and r["defaults"] == 13

    # --- THE FALSIFICATION MUST STAND -------------------------------------------
    # More data made the central claim WORSE, not better.
    assert len(r["gates_not_met"]) == 3, "the replication is 1/4; it must not be re-scored"
    for g in ("B1_tauv_beats_stars",
              "B2_popularity_is_near_chance",
              "B3_portfolio_default_rate"):
        assert g in r["gates_not_met"], "%s was rescued after the fact" % g

    # stars out-discriminate tau_v by MORE at larger N
    assert r["auc_stars"] > r["auc_tau_v"]
    assert abs(r["auc_tau_v"] - 0.7792) < 5e-3
    assert abs(r["auc_stars"] - 0.8635) < 5e-3

    # the portfolio advantage did not shrink — it disappeared entirely
    p = r["portfolio"]
    assert p["sovereign_default_rate"] == p["conventional_default_rate"], \
        "B3 collapsed to an exact tie at N=44; do not restate it as an advantage"

    # only the two-axes observation survives, and it moved toward the gate boundary
    assert abs(r["spearman_stars_tauv"]) < 0.50
    assert abs(r["spearman_stars_tauv"]) > 0.40, \
        "the axes are less independent at larger N; keep that visible"
