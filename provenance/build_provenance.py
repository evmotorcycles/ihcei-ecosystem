#!/usr/bin/env python3
"""
build_provenance.py -- fingerprint the frozen scientific record and write the
cryptographic origin lock: PROVENANCE.lock.json.
================================================================================
Run this at a release (or whenever the frozen specs/corpora/manuscripts change):

    python3 provenance/build_provenance.py

It computes a SHA-256 for every frozen artifact and a single Merkle ROOT over all
of them, then writes ../PROVENANCE.lock.json with the author, canonical origin
URL, the ordered file list, per-file leaf hashes, and the root. Anyone reproducing
runs `verify_provenance.py`, which recomputes the root from their checkout and
confirms it equals this locked root -- binding their reproduction to THIS origin.
"""
import json
import os
import subprocess

from provenance_core import ROOT, compute

OUT = os.path.join(ROOT, "PROVENANCE.lock.json")

# ---------------------------------------------------------------- supersession
# A lock that can never be re-issued after a correction penalises honesty. A lock
# that can be silently re-rooted whenever a test goes red attests to nothing.
# The honest form is the one the ledger already uses for retirements: the old
# state is not deleted, its SUPERSESSION is recorded.
#
# APPEND-ONLY. Each entry is a root that was retired, and why. The builder
# REFUSES to write a new root unless the root it is replacing appears here --
# so a silent re-root is impossible by construction, not merely discouraged.
SUPERSESSIONS = [
    {
        "root": "f12680a76156420066ca319b4542d24d34cb02d5360750bd20305d6794e2b640",
        "superseded_on": "2026-09-18",
        "reason": ("H5 retirement (declarations.md §15): lism-cohorts/README.md "
                   "corrected 'live re-simulation, seeded' to 'seeded simulation "
                   "re-run here (not observed)'. Cohort D is a seeded simulation "
                   "and the frozen record said otherwise. One file of 77 changed; "
                   "nothing was added or removed."),
    },
]


class UndeclaredResubmission(RuntimeError):
    """The computed root differs from the locked one and nobody said why."""


AUTHOR = "Mago, Labib"
AFFIL = "Novora Research Initiative, Open Science Division"
ORIGIN = "https://github.com/evmotorcycles/ihcei-ecosystem"


def git_commit():
    try:
        return subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"],
                                       text=True).strip()
    except Exception:
        return None


def check_supersession(new_root):
    """Refuse to re-root silently. Returns the chain to record."""
    if not os.path.exists(OUT):
        return None, []
    prev = json.load(open(OUT))
    prev_root = prev.get("merkle_root")
    if prev_root == new_root:
        return prev.get("supersedes"), prev.get("supersession_chain", [])
    declared = [e for e in SUPERSESSIONS if e["root"] == prev_root]
    if not declared:
        raise UndeclaredResubmission(
            "the frozen record has changed (%s -> %s) and the root being "
            "replaced is not declared in SUPERSESSIONS.\n\n"
            "This is not a build failure to work around. Either a frozen "
            "artifact changed by accident -- in which case investigate rather "
            "than re-issue -- or the change is a recorded correction, in which "
            "case add the retired root, the date, and the REASON to "
            "SUPERSESSIONS and run again.\n\n"
            "A lock that can be silently re-rooted attests to nothing."
            % (prev_root[:16], new_root[:16]))
    return prev_root, [e for e in SUPERSESSIONS]


def main():
    files, leaves, root = compute()
    supersedes, chain = check_supersession(root)
    lock = {
        "schema": "novora-provenance/1",
        "title": "Novora / IHCEI — cryptographic origin lock",
        "author": AUTHOR,
        "affiliation": AFFIL,
        "origin": ORIGIN,
        "license": {"code": "MIT", "docs_and_data": "CC-BY-4.0",
                    "attribution_required": True},
        "algorithm": "SHA-256 leaves (0x00-prefixed) -> binary Merkle (0x01-prefixed internal), files sorted by path",
        "merkle_root": root,
        "supersedes": supersedes,
        "supersession_chain": chain,
        "supersession_note": (
            "This lock SUPERSEDES the root above; it does not replace it. The "
            "attribution, affiliation and origin are unchanged -- only the "
            "snapshot moved, and the reason it moved is recorded in the chain. "
            "Misattribution stays detectable: the chain is the audit trail back "
            "to the first-published root." if supersedes else
            "First issue. No prior root."),
        "git_commit": git_commit(),
        "file_count": len(files),
        "covers": ("All pre-registration specs + manifests, authored corpora, the offline "
                   "knowledge fixture, and the manuscripts/READMEs for LISM, LMD, the four "
                   "cohorts (yeast 4825 / GitHub 992 / knowledge 793 / digital swarm), the "
                   "three validation stages, Hinton & Russell tests, benchmark-governance, "
                   "and the tau_v cohort. Passed, NULL, and NEGATIVE results alike."),
        "attribution_statement": (
            "This artifact set originates from %s (%s), %s. If you reproduce, extend, or "
            "build upon it — including reproducing its null or negative results — you must "
            "retain this attribution and cite the origin. A faithful reproduction recomputes "
            "the merkle_root below; that root is the cryptographic reference back to this "
            "source. Do not represent this work, or reproductions of it, as your own origin."
        ) % (AUTHOR, AFFIL, ORIGIN),
        "how_to_verify": "python3 provenance/verify_provenance.py",
        "note_on_scope": ("Provenance proves integrity + priority + attribution; it does not "
                          "prevent copying (nothing can). It makes MISATTRIBUTION detectable and "
                          "gives the originator a dated, checkable first-publication record. "
                          "results*.json are intentionally excluded (they carry run timestamps)."),
        "leaves": {rel: leaves[rel] for rel in files},
    }
    with open(OUT, "w") as f:
        json.dump(lock, f, indent=2)
        f.write("\n")
    print("wrote %s" % OUT)
    print("  files fingerprinted : %d" % len(files))
    print("  merkle_root         : %s" % root)
    print("  git_commit          : %s" % (lock["git_commit"] or "n/a"))
    if supersedes:
        print("  SUPERSEDES          : %s" % supersedes[:16])
        print("  chain length        : %d retired root(s)" % len(chain))


if __name__ == "__main__":
    main()
