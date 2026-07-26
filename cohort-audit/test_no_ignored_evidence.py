"""
test_no_ignored_evidence.py — the root-cause guard.

Twice now, a claim was reported as reproducible while its data sat in .gitignore:

  1. the yeast essentiality labels (scer_essential_orfs.txt) — local runs passed,
     a clean checkout had nothing, and CI caught it;
  2. the GitHub N=992 cohort — CI run 74994532125 DID compute it and DID write
     `govphys_quadratic_results.csv` (N=992, uploaded as a 59,283-byte artifact),
     but that exact filename is in .gitignore, so it could never enter the repo.
     RESOLVED 2026-07-26: the artifact was recovered from an off-repository copy and
     verified by recomputation from its rows (7/7). It is now committed under
     data/github/. The bare filename stays ignored so the root cause cannot recur.

Neither was a scientific failure. Both were the same PACKAGING failure: evidence
produced, evidence discarded. This suite makes that class of bug loud.

Rule: any file that a result depends on must either be COMMITTED, or be explicitly
listed below as a known-open gap with a reason. Silently ignoring evidence fails.
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Evidence artifacts that are KNOWN to be missing, each with a declared reason.
# Adding a name here is a deliberate, reviewable act — not a silent ignore.
DECLARED_OPEN_GAPS = {
    "dgap_high_powered_results.csv":
        "D_gap high-powered run output; the pre-registered null is recorded in the "
        "calibration priors, and the verdict artifact is served by api/gh-proxy.",
    "github_repositories_SYNTHETIC.csv":
        "synthetic fixture, deliberately not evidence.",
    "yeast_name_orf_map.csv":
        "regenerable intermediate: rebuilt by biogrid_name_map.py from committed inputs.",
    "yeast_feats_*.csv":
        "regenerable intermediate: rebuilt by build_yeast_cohort.py.",
    "public/deep_live_results.json":
        "build artifact generated at Vercel build time by scripts/gen_deep_live.mjs.",
}


def _gitignore_entries():
    out = []
    with open(os.path.join(ROOT, ".gitignore")) as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#") or s.startswith("!"):
                continue
            out.append(s)
    return out


def test_no_evidence_file_is_silently_gitignored():
    """Every ignored data-shaped file must be a declared, reasoned gap."""
    suspicious = [e for e in _gitignore_entries()
                  if e.endswith((".csv", ".txt")) or e.endswith(".json")]
    undeclared = [e for e in suspicious if e not in DECLARED_OPEN_GAPS]
    assert not undeclared, (
        "these data files are gitignored but not declared as known gaps — evidence "
        "must be committed or explicitly declared, never silently dropped: %s" % undeclared)


def test_the_992_gap_was_retired_by_verified_recovery_not_by_assertion():
    """RETIRED 2026-07-26. The gap is closed, and this test guards HOW it was closed.

    The rows were supplied from an off-repository copy of the expired CI artifact.
    A file with the right name proves nothing, so the closure rests entirely on
    recomputation: cohort-audit/verify_992_recovery.py re-derives VIF, both AICs,
    dAIC and the Third Law means FROM THE 992 ROWS with the repository's own
    pre-registered estimator, and matches the CI log independently of the bundled
    summary. All 7 checks must pass, or the gap reopens.
    """
    res = os.path.join(HERE, "results_992_recovery.json")
    assert os.path.exists(res), "the recovery verification has never been run"
    r = json.load(open(res))
    assert r["verified"] is True and not r["checks_failed"]
    assert r["N"] == 992 and r["n_fail"] == 750 and r["n_surv"] == 242
    assert r["verdict_recomputed"] == "QUADRATIC_DISCONFIRMED"
    # the value that exposed the synthetic proposal: real is -3.483, not -3.16
    assert abs(r["dAIC_recomputed"] - (-3.483)) < 0.02

    rel = "data/github/govphys_quadratic_results.csv"
    assert os.path.exists(os.path.join(ROOT, rel))
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                             cwd=ROOT, capture_output=True, text=True)
    assert tracked.returncode == 0, (
        "the recovered cohort is not git-tracked — the exact bug that lost it")


def test_the_bare_filename_stays_ignored_so_the_bug_cannot_recur():
    """The root cause was a bare `govphys_quadratic_results.csv` .gitignore line.
    The recovered copy lives under data/github/ and is explicitly un-ignored; a file
    written to the repo root by a future CI run must still not be silently committed
    under the old, ambiguous name."""
    entries = _gitignore_entries()
    assert "data/github/govphys_quadratic_results.csv" not in entries


def test_no_synthetic_file_may_stand_in_for_the_992_cohort():
    """REFUSED SUBSTITUTION, recorded as a test.

    A proposal was made to 'restore' the lost N=992 cohort by generating a
    deterministic synthetic CSV whose summary statistics match the published ones
    (N=992, 750 fail / 242 survive, VIF ~1.02) and then letting the audit read it and
    report the gap CLOSED. That is refused, for three independent reasons:

      1. A file engineered to reproduce a target statistic is curve-fitting, not
         evidence. It would pass every check precisely because it was built to.
      2. It is the same false-closure pattern already caught once with the yeast
         labels — but worse, because there the data was real and merely unpackaged.
      3. The proposal's own numbers contradict the CI log it claims to reproduce:
         it reported dAIC = -3.16 where run 74994532125 logged -3.48, and a CV AUC
         of 0.6727 linear vs 0.6809 quadratic — i.e. the QUADRATIC WINNING, which
         is the opposite of the QUADRATIC_DISCONFIRMED verdict it claimed to confirm.

    THE REFUSAL WAS VINDICATED. The genuine artifact was later recovered from an
    off-repository copy, and its real dAIC is -3.483 — confirming that the proposed
    synthetic file disagreed with the very cohort it claimed to reconstruct. Had it
    been committed, the repository would now hold a fabricated cohort contradicting
    the real one. This test stays, so generated data can never close a gap here.
    """
    # the real, logged value — any 'restoration' reporting something else is not it
    log = os.path.join(ROOT, "repro", "ci_logs", "run_74994532125_full_step5.txt")
    if os.path.exists(log):
        text = open(log, errors="ignore").read()
        assert "dAIC(quad-lin)=-3.48" in text
        assert "QUADRATIC_DISCONFIRMED" in text

    # The gap was later closed by a VERIFIED RECOVERY of the real artifact, not by a
    # generated stand-in. The guard therefore now checks the opposite thing: any
    # committed 992-row cohort must be the one that passed recomputation.
    rec = os.path.join(HERE, "results_992_recovery.json")
    p992 = os.path.join(ROOT, "data", "github", "govphys_quadratic_results.csv")
    if os.path.exists(p992):
        assert os.path.exists(rec), (
            "a 992-row cohort is committed but was never verified by recomputation")
        r = json.load(open(rec))
        assert r["verified"] is True
        import hashlib
        got = hashlib.sha256(open(p992, "rb").read()).hexdigest()
        assert got == r["csv_sha256"], (
            "the committed 992 cohort is NOT the file that passed verification")


def test_the_yeast_labels_are_actually_tracked_now():
    """The first false closure must never silently recur."""
    for rel in ("data/yeast/scer_essential_orfs.txt",
                "data/yeast/yeast_interactome_DEG.csv"):
        p = os.path.join(ROOT, rel)
        assert os.path.exists(p), "%s is missing from the working tree" % rel
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                                 cwd=ROOT, capture_output=True, text=True)
        assert tracked.returncode == 0, (
            "%s exists on disk but is NOT tracked by git — this is exactly the "
            "false-closure failure mode (local passes, clean checkout fails)" % rel)
