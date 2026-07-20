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

AUTHOR = "Mago, Labib"
AFFIL = "Novora Research Initiative, Open Science Division"
ORIGIN = "https://github.com/evmotorcycles/ihcei-ecosystem"


def git_commit():
    try:
        return subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"],
                                       text=True).strip()
    except Exception:
        return None


def main():
    files, leaves, root = compute()
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


if __name__ == "__main__":
    main()
