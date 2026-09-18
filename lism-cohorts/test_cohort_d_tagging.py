"""Every surface naming Cohort D or the 39-hop decay must carry its provenance.

WHY THIS TEST EXISTS
====================
`text-channel/PREREG.md` — a LOCKED, hashed pre-registration — already said the
right thing:

    "Cohort D is the sharpest case. It is a seeded simulation that reproduces
     itself... Presenting its 39-hop fidelity decay as evidence about real agent
     swarms would repeat exactly the error that the N=793 retraction was issued
     for."

And the root `README.md` claimed "real 39-hop telemetry" anyway, for months.

**A prohibition in a locked file does not propagate to surfaces that never read
it.** That is knowledge air-gapped from enforcement — the same defect class as
the 45 orphaned suites in `declarations.md` §13, where the frozen count and the
air gap turned out to be one defect rather than two.

Mechanism, not memory. This converts "the locked file knew" into "the pipeline
enforces". It is ONE test and deliberately not a general tagging regime: it
watches one claim family, the one that was actually got wrong.

WHAT IT CANNOT DO
=================
  * It matches TEXT. A surface can satisfy it and still mislead in a sentence
    the regex cannot read.
  * It claims **precision, not recall**: it demonstrates its own false
    positives through the decoys below, and can never show that an untagged
    mention elsewhere does not exist under different wording.
  * It does not check that the tag is *true*, only that it is present.
"""

from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

#: A mention of the cohort or of its headline number.
MENTION = re.compile(r"\bcohort[ _-]?D\b|\b39[ -]?hop", re.IGNORECASE)

#: The provenance tag that makes a mention honest.
SIMULATED = re.compile(r"seeded|simulat(?:ed|ion)|SIMULATED_REPRODUCIBLE",
                       re.IGNORECASE)

#: Lines of context either side that may carry the tag instead of the line.
WINDOW = 2

SUFFIXES = (".md", ".py", ".mjs", ".js", ".json")
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".pytest_cache", "reports"}


def states_the_rules(name: str) -> bool:
    """Exempt BY ROLE, never by name — `declarations.md` §7.

    Four kinds of file must be able to quote what they forbid. The ledger in
    particular HOLDS the retired wording of H5, so it must be able to reproduce
    the untagged sentence verbatim in order to record that it was retired.
    """
    return bool(
        (name.startswith("test_") and name.endswith(".py"))
        or (name.startswith("prereg_") and name.endswith(".md"))
        or name in ("declarations.md", "RESULTS.md", "PREREG.md")
    )


def untagged_mentions(root=ROOT):
    """Every mention whose line, or its ±WINDOW neighbourhood, lacks the tag."""
    out, scanned = [], 0
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in sorted(files):
            if not f.endswith(SUFFIXES) or states_the_rules(f):
                continue
            path = os.path.join(dirpath, f)
            try:
                lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
            except OSError:
                continue
            scanned += 1
            for i, line in enumerate(lines):
                if not MENTION.search(line):
                    continue
                lo, hi = max(0, i - WINDOW), min(len(lines), i + WINDOW + 1)
                if not SIMULATED.search(" ".join(lines[lo:hi])):
                    out.append((os.path.relpath(path, root), i + 1, line.strip()[:90]))
    return out, scanned


# ------------------------------------------------------------- the decoys ----
def test_the_check_has_a_two_sided_decoy():
    """CLAUDE.md: a lexical check carries one string it must NOT fire on and
    one it MUST, and is scoped to precision."""
    tagged = ["# Cohort D, a seeded simulation", "value = 0.84  # 39-hop decay"]
    untagged = ["# Cohort D telemetry", "value = 0.84  # 39-hop decay"]

    def probe(lines):
        hits = []
        for i, line in enumerate(lines):
            if MENTION.search(line):
                lo, hi = max(0, i - WINDOW), min(len(lines), i + WINDOW + 1)
                if not SIMULATED.search(" ".join(lines[lo:hi])):
                    hits.append(i)
        return hits

    assert probe(tagged) == [], "the decoy that must NOT fire did; too strict"
    assert probe(untagged), "the decoy that MUST fire did not; too loose"


def test_the_mention_pattern_does_not_fire_on_unrelated_words():
    """`cohort.?d` matched 'cohort data' in the first draft. Word boundaries."""
    for benign in ("the cohort data was fetched", "a 4-cohort meta-analysis",
                   "139 hopper nodes", "cohorts and doses"):
        assert not MENTION.search(benign), benign
    for must in ("Cohort D", "cohort_d", "39-hop", "39 hop"):
        assert MENTION.search(must), must


# --------------------------------------------------------------- the rule ----
def test_every_surface_naming_cohort_d_carries_its_provenance():
    """The enforcement. H5 would have failed this the moment it was written."""
    hits, scanned = untagged_mentions()
    assert scanned >= 50, f"walked only {scanned} files; a scan that read little proves little"
    assert hits == [], (
        "untagged mention(s) of Cohort D or the 39-hop decay — each must carry "
        "the seeded/simulation tag within ±2 lines, or live in a file that is "
        "exempt by role (the ledger, a prereg, a test, a RESULTS write-up):\n"
        + "\n".join(f"  {p}:{n}  {t}" for p, n, t in hits))


def test_the_ledger_is_exempt_by_role_and_still_records_the_retirement():
    """The exemption is not a hole: the ledger must still carry H5."""
    text = " ".join(open(os.path.join(ROOT, "stack", "governance",
                                      "declarations.md"),
                         encoding="utf-8").read().split())
    assert states_the_rules("declarations.md")
    assert "RETIRED 2026-09-18" in text
    assert "cohort_D_swarm(seed=20260719, N=500)" in text
    assert "does not propagate to the surfaces that never read it" in text


def test_shipped_module_code_is_never_exempt():
    for decoy in ("questions.py", "meta_lism.py", "circuit_breaker.py",
                  "README.md", "PROPOSAL_PACKAGE.md"):
        assert not states_the_rules(decoy), decoy
