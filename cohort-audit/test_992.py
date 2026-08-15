#!/usr/bin/env python3
"""Locks the N=992 GitHub cohort as genuinely closed — and closed for the right
reason: the rows are committed, and the published summary reproduces from them.

    python3 -m pytest -q cohort-audit/test_992.py

History this guards against: results_gapclosure.json once reported the gap as
closed on the strength of a file that was gitignored and had never been
committed. It was true on one machine and false from a clean clone. The fix is
not a flag — it is the 992 rows being in the repository, and an independent
re-analysis that recomputes the verdict instead of reading it.
"""
import csv
import hashlib
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(HERE, "data/govphys_quadratic_results.csv")
SUMMARY = os.path.join(HERE, "data/govphys_quadratic_summary.json")
SCRIPT = os.path.join(ROOT, "govphys_quadratic_prereg_test.py")


def test_the_rows_are_actually_committed():
    """The whole point. A flag saying 'closed' is not evidence; rows are."""
    assert os.path.exists(CSV), "the 992-row cohort must be committed, not gitignored"
    out = subprocess.run(["git", "check-ignore", CSV], cwd=ROOT, capture_output=True)
    assert out.returncode != 0, (
        "the committed cohort must NOT be gitignored — that is exactly how this "
        "result stopped being reproducible from a clean clone last time")
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", CSV],
                             cwd=ROOT, capture_output=True)
    assert tracked.returncode == 0, "the cohort file must be tracked by git"


def test_cohort_shape_matches_the_preregistered_requirements():
    rows = list(csv.DictReader(open(CSV)))
    assert len(rows) == 992
    fails = [r for r in rows if int(r["E"]) == 0]
    assert len(fails) == 750
    assert len(rows) - len(fails) == 242
    # the pre-registration required N>=1000 target with N_fail>=100 for a verdict
    assert len(fails) >= 100, "the failing region must be populated or the verdict is void"
    for col in ("repo", "stratum", "E", "U", "D_enc", "D_dec", "D", "tau_v",
                "tau_v_imputed", "stars", "archived"):
        assert col in rows[0], f"missing locked column {col}"


def test_spec_hash_binds_the_run_to_the_committed_script():
    """The CI run must have executed the pre-registration that is in the repo."""
    import ast
    doc = ast.get_docstring(ast.parse(open(SCRIPT).read()), clean=False)
    computed = hashlib.sha256(doc.encode()).hexdigest()
    claimed = json.load(open(SUMMARY))["spec_sha256"]
    assert computed == claimed, (
        "the spec that ran in CI is not the spec committed here — the "
        "pre-registration lock is broken")


def test_independent_reanalysis_reproduces_the_published_summary():
    """Recompute from raw rows. The summary is a claim; the CSV is the evidence."""
    out = subprocess.run(["python3", os.path.join(HERE, "verify_992.py")],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stdout + out.stderr
    res = json.load(open(os.path.join(HERE, "results_992_verification.json")))
    assert res["summary_reproduces"] is True
    assert res["n_total"] == 992 and res["n_fail"] == 750
    assert res["verdict_recomputed"] == res["verdict_claimed"] == "QUADRATIC_DISCONFIRMED"
    assert res["gate_pass"] is True


def test_the_gate_conditions_were_met_not_waived():
    res = json.load(open(os.path.join(HERE, "results_992_verification.json")))
    assert res["VIF"] < 5.0, "channel-intact gate"
    assert res["n_fail"] >= 100, "failing-region gate"
    assert res["dAIC_lin_minus_quad"] <= 0, (
        "DISCONFIRMED requires dAIC <= 0 under the locked decision rule")


def test_the_verdict_is_not_overstated():
    """DISCONFIRMED is about the quadratic. It does not prove the linear law."""
    src = open(os.path.join(HERE, "verify_992.py")).read()
    assert "does not upgrade" in src and "linear law to proven" in src


def test_audit_no_longer_claims_a_gap_its_own_ledger_has_closed():
    a = json.load(open(os.path.join(HERE, "results_audit.json")))
    assert a["C4_github_992_GAP"]["found_992_row_artifact"] is True
    assert a["C4_github_992_GAP"]["largest_committed_labelled_cohort"] == 992
    assert "NOT offline-reproducible" not in a["note"] or a["C6_integrity_ledger"]["not_offline_reproducible"]


def test_tau_v_imputation_is_disclosed_with_its_direction():
    s = json.load(open(SUMMARY))
    assert s["thirdlaw_imputed_frac_failed"] > 0
    assert s["thirdlaw_imputed_frac_survived"] >= 0
    src = open(os.path.join(HERE, "verify_992.py")).read()
    assert "understated, not inflated" in src, (
        "the direction of the imputation bias must be stated, not just the fraction")
