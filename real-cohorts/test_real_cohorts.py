"""
test_real_cohorts.py — locks the real-data replacement, INCLUDING its three failures.

The two cohorts the audit called SIMULATION now have a real, committed substitute:
540 live PyPI packages, 1287 internal dependency edges, depth 3. The locked gates
score 5/8, and the three misses are the scientifically important part:

  KR1  fidelity-adjusted capacity is WORSE than raw capacity at explaining reuse
       -> the knowledge-exchange thesis is now falsified TWICE, on independent real
          substrates (HF/GitHub previously, PyPI here)
  KR3  capacity DOES confer fidelity (rho=+0.57) -> "status is inert" is refuted,
       and this is very likely WHY KR1 fails: D is partly redundant with U
  SR2  the pre-registered linear>=quadratic gate is missed -- but BOTH models explain
       ~1% of variance, so the honest reading is "neither coupling explains reuse
       here", not "quadratic wins"

This suite exists so none of that can later be softened, re-specified, or quietly
swapped back for the seeded simulations that flattered the thesis.
"""
import csv
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "pypi")
LOCKED = "4e83893b0eb37567b39c7c5ad128379f11a77416e8d4abdf0da647415110db8c"


def _results():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "analyze_real.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.load(open(os.path.join(HERE, "results_real.json")))


def test_prereg_hash_is_the_one_locked_before_the_fetch():
    spec = json.load(open(os.path.join(HERE, "prereg", "realsub_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED, "the pre-registration was edited after it was locked"
    assert open(os.path.join(HERE, "prereg", "REALSUB.sha256")).read().strip() == LOCKED


def test_the_graph_is_real_and_actually_committed():
    """The N=992 failure mode was evidence computed then lost to .gitignore.
    These rows must be in the repository, not merely on this disk."""
    for fn in ("dep_graph_nodes.csv", "dep_graph_edges.csv", "MANIFEST.json"):
        p = os.path.join(DATA, fn)
        assert os.path.exists(p), fn
        rel = os.path.relpath(p, ROOT)
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                                 cwd=ROOT, capture_output=True, text=True)
        assert tracked.returncode == 0, "%s exists but is NOT git-tracked" % rel

    man = json.load(open(os.path.join(DATA, "MANIFEST.json")))
    for fn, want in man["sha256"].items():
        got = hashlib.sha256(open(os.path.join(DATA, fn), "rb").read()).hexdigest()
        assert got == want, "%s changed after the fetch that produced the manifest" % fn

    nodes = list(csv.DictReader(open(os.path.join(DATA, "dep_graph_nodes.csv"))))
    assert len(nodes) == 540 and max(int(n["depth"]) for n in nodes) == 3


def test_attempt_one_is_preserved_not_deleted():
    """Three crawls were run before any gate was computed. The first is kept on the
    record with its disclosure, so the sample-size changes stay auditable."""
    a1 = json.load(open(os.path.join(DATA, "MANIFEST.attempt1_n69.json")))
    assert a1["n_nodes"] == 69
    assert "BEFORE any gate was computed" in a1["disclosure"]


def test_the_three_failures_stand():
    r = _results()
    assert r["spec_sha256_canonical"] == LOCKED
    assert r["N"] == 540 and r["max_depth"] == 3

    assert len(r["gates_not_met"]) == 3, "the run is 5/8; it must not be re-scored"
    for g in ("KR1_fidelity_beats_status",
              "KR3_capacity_does_not_confer_fidelity",
              "SR2_linear_not_quadratic"):
        assert g in r["gates_not_met"], "%s was rescued after the fact" % g

    # KR1: raw status out-explains the fidelity-adjusted product. Direction matters.
    assert r["rho_fidelity_E"] < r["rho_status_E"], \
        "KR1 failed because fidelity did WORSE, not merely no better"
    assert abs(r["rho_status_E"] - 0.0794) < 5e-3
    assert abs(r["rho_fidelity_E"] - 0.0165) < 5e-3

    # KR3: capacity buys fidelity -- "status is inert" is refuted on real data.
    assert r["rho_U_D"] > 0.50
    assert abs(r["rho_U_D"] - 0.5695) < 5e-3

    # SR2: the gate is missed, but do not let it be restated as "quadratic wins".
    assert r["r2_quadratic"] > r["r2_linear"]
    assert r["r2_linear"] < 0.02 and r["r2_quadratic"] < 0.02, \
        "both couplings explain ~1% of variance; neither is a working model here"


def test_what_survived_is_reported_at_full_strength():
    r = _results()
    # SR1 is a genuine, falsifiable win on real data: fidelity really does decay.
    prof = r["depth_profile_meanD"]
    assert prof["0"] > prof["3"], "the decay result must not be softened either"
    assert prof["0"] > 0.60 and prof["3"] < 0.40

    # KR2: the two hops are independent, and the circular control is still rejected.
    assert r["vif_denc_ddec"] < 5.0
    assert r["n_below_median_D"] >= 30       # invariant I2: failing region populated


def test_revocation_is_labelled_as_a_traversal_check_not_evidence():
    r = _results()
    sr4 = [g for g in r["gates"] if g["gate"].startswith("SR4")][0]
    assert sr4["pass"] is True
    assert sr4["falsifiable"] is False, \
        "a check that cannot fail must never be counted as empirical support"


def test_this_does_not_close_the_github_992_gap():
    """Guard against the exact substitution that was proposed and refused: presenting
    a different (or generated) dataset as if it restored the lost 992 cohort."""
    spec = json.load(open(os.path.join(HERE, "prereg", "realsub_prereg.json")))
    rel = spec["relationship_to_github_992"]
    assert "does NOT close" in rel and "unrecoverable" in rel
    assert "curve-fitting" in rel

    audit = subprocess.run([sys.executable,
                            os.path.join(ROOT, "cohort-audit", "cohort_audit.py")],
                           capture_output=True, text=True)
    assert "NOT_OFFLINE_REPRODUCIBLE" in audit.stdout, \
        "the 992 gap must still be reported as open"
