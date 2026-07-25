"""
test_gap_closure.py — locks the gap-closure outcome, INCLUDING the missed prediction.

Two things this suite exists to prevent:
  1. the yeast outcome gap being marked closed WITHOUT the numbers that close it;
  2. the missed G2 prediction being quietly rescued by lowering the pre-registered
     threshold (N >= 35) after seeing the result (N = 33).
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED_SPEC = "f8a94c655dc0ec5c9add082114dd7048a5d148827fd6e0cb33226461c3dbd03a"


def _canon(v):
    if v is None or not isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ",".join(_canon(x) for x in v) + "]"
    return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + _canon(v[k])
                          for k in sorted(v)) + "}"


def test_gap_closure_reproduces_including_its_miss():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "gap_closure.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_gapclosure.json")))

    # -- the protocol must still be the one that was locked BEFORE the runner existed
    spec = json.load(open(os.path.join(HERE, "prereg", "gapclosure_prereg.json")))
    assert hashlib.sha256(_canon(spec).encode()).hexdigest() == LOCKED_SPEC, \
        "the pre-registered spec was edited after locking"
    assert r["spec_sha256_canonical"] == LOCKED_SPEC

    # -- YEAST: the gap is closed, and only on the strength of real numbers
    y = r["yeast"]
    assert r["yeast_outcome_gap_closed"] is True
    assert y["N"] == 4825 and 1000 <= y["n_essential"] <= 1100
    assert y["vif"] < 1.10                                  # channel intact
    assert y["cv_auc_linear"] > y["cv_auc_quadratic"]       # quadratic adds nothing
    assert 0.60 <= y["cv_auc_linear"] <= 0.72

    # -- the published 'quadratic AUC ~0.47' stays identified as an ARTIFACT
    assert y["multivariate_converged"] is False
    assert y["cv_auc_quadratic"] >= 0.55                    # above chance under a real fit
    assert y["multivariate_insample_auc"] < 0.50            # the sub-chance number is the artifact

    # -- GITHUB 992: DYNAMIC GAP GATING
    g = r["github"]
    if r["github_992_gap_closed"]:
        assert r["github_992_gap_open"] is False
        assert g["gap992_open"] is False
        assert g["union_N"] >= 992
        assert g["union_failed"] >= 750
        assert g["median_tau_v_failed"] > g["median_tau_v_survived"]
        assert "G2_expanded_labelled_cohort" not in r["missed_predictions"]
    else:
        assert r["github_992_gap_open"] is True
        assert g["gap992_open"] is True
        assert g["largest_labelled_json"] < 992

        # -- G2 MISS IS PERMANENT: recorded as missed, threshold not moved
        assert "G2_expanded_labelled_cohort" in r["missed_predictions"], \
            "the missed G2 prediction was rescued -- thresholds must not move after the fact"
        assert g["union_N"] == 33 and g["union_N"] < 35          # predicted >= 35, reached 33
        assert g["union_failed"] == 9                            # up from the audit's 4, still short
        assert g["median_tau_v_failed"] > g["median_tau_v_survived"]   # direction did hold

    # -- the swarm stays a simulation, and its real-data analogue carries the weight
    s = r["swarm"]
    assert s["real_graph_quad"] - s["real_graph_lin"] <= 0.01
    labels = {x["gate"]: x for x in r["gates"]}
    assert labels["S1_swarm_is_simulation"]["falsifiable"] is False, \
        "a simulation label must never be counted as falsifiable evidence"
