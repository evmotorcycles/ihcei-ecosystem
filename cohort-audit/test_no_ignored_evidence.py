"""
test_no_ignored_evidence.py — the root-cause guard.

Twice now, a claim was reported as reproducible while its data sat in .gitignore:

  1. the yeast essentiality labels (scer_essential_orfs.txt) — local runs passed,
     a clean checkout had nothing, and CI caught it;
  2. the GitHub N=992 cohort — CI run 74994532125 DID compute it and DID write
     `govphys_quadratic_results.csv` (N=992, uploaded as a 59,283-byte artifact),
     but that exact filename is in .gitignore, so it could never enter the repo.
     The CI artifact has since expired, so the cohort is now unrecoverable.

Neither was a scientific failure. Both were the same PACKAGING failure: evidence
produced, evidence discarded. This suite makes that class of bug loud.

Rule: any file that a result depends on must either be COMMITTED, or be explicitly
listed below as a known-open gap with a reason. Silently ignoring evidence fails.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Evidence artifacts that are KNOWN to be missing, each with a declared reason.
# Adding a name here is a deliberate, reviewable act — not a silent ignore.
DECLARED_OPEN_GAPS = {
    "govphys_quadratic_results.csv":
        "N=992 per-repo rows. Produced by CI run 74994532125 and uploaded as an "
        "artifact, but the filename was gitignored so it never entered the repo; the "
        "artifact has since expired. Cohort is NOT offline-reproducible. To close: "
        "re-run the pre-registered fetch and commit the CSV.",
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


def test_the_992_gap_has_a_stated_cause_and_a_stated_fix():
    """The 992 gap must keep its diagnosis attached wherever it is cited."""
    reason = DECLARED_OPEN_GAPS["govphys_quadratic_results.csv"]
    assert "gitignored" in reason and "NOT offline-reproducible" in reason
    assert "To close:" in reason, "a declared gap must carry its remedy"


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

    The 992 rows are unrecoverable. The gap stays open. This test makes any future
    attempt to close it with generated data fail loudly.
    """
    reason = DECLARED_OPEN_GAPS["govphys_quadratic_results.csv"]
    assert "NOT offline-reproducible" in reason

    # the real, logged value — any 'restoration' reporting something else is not it
    log = os.path.join(ROOT, "repro", "ci_logs", "run_74994532125_full_step5.txt")
    if os.path.exists(log):
        text = open(log, errors="ignore").read()
        assert "dAIC(quad-lin)=-3.48" in text
        assert "QUADRATIC_DISCONFIRMED" in text

    # a committed 992-row cohort must not appear without the gap being formally retired
    for rel in ("govphys_quadratic_results.csv",
                "data/github/govphys_quadratic_results.csv"):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            n = sum(1 for _ in open(p, errors="ignore")) - 1
            assert n != 992, (
                "a 992-row cohort file appeared at %s while the gap is still declared "
                "open. If this is a genuine re-fetch, retire the DECLARED_OPEN_GAPS "
                "entry deliberately. If it is generated, it is not evidence." % rel)


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
