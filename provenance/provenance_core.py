#!/usr/bin/env python3
"""
provenance_core.py -- shared provenance/Merkle logic for the Novora/IHCEI stack.
================================================================================
PURPOSE (why this exists): this work is public and meant to be reproduced by
anyone -- partners, referees, independent reproducers (Jules), the world. We WANT
that. What we do NOT want is for a reproducer to be able to pass the origin off as
their own. Cryptographic provenance solves exactly that:

  * INTEGRITY   -- a SHA-256 of every frozen artifact; any change is detectable.
  * PRIORITY    -- a single Merkle ROOT over all pre-registration specs, corpora,
                   fixtures and manuscripts, committed on a dated commit. That root
                   is a public, tamper-evident proof that THIS content existed HERE
                   FIRST, under this author.
  * ATTRIBUTION -- anyone who faithfully reproduces recomputes the SAME root. A
                   faithful reproduction therefore cryptographically REFERENCES the
                   origin; a divergent one is detectable. Combined with the LICENSE
                   (legal) and CITATION.cff (norm), that is the real protection.

Honest scope: provenance/signing does NOT prevent copying of public code (nothing
can). What it does is make MISATTRIBUTION detectable and give the originator a
dated, checkable priority record. The right tool for public+reproducible work is
signatures + content hashes, NOT encryption (encryption would hide what we want
seen). See PROVENANCE.md.

The MANIFEST below lists the FROZEN artifacts (specs, corpora, fixtures,
manuscripts) -- deliberately NOT the results*.json files, which carry run
timestamps and change on every reproduction. Provenance protects the intellectual
record (what was stated, and when), which is exactly what priority is about.
"""
import glob
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Frozen-artifact selectors, resolved relative to the repo root. Globs are sorted
# deterministically before hashing so the Merkle root is reproducible everywhere.
GLOBS = [
    "**/prereg/*.json",          # every pre-registration spec + its SHA-256 manifest
    "**/corpora/*.json",         # authored, locked corpora
]
EXPLICIT = [
    "repro/data/se_fixture_barakah.json",   # offline knowledge-cohort fixture (Jules fix)
    "repro/tauv_cohort.json",               # tau_v cohort
    # manuscripts / frozen scientific record
    "LISM_manuscript_REVISED.md",
    "UNIFIED_TELEMETRY_WHITEPAPER.md",
    "SE_BARAKAH_RESULTS.md",
    "REPRODUCIBILITY.md",
    "physics-agency/PAPER_telemetric_metric.md",
    "physics-agency/lmd/README.md",
    "lism-cohorts/README.md",
    "validation-stages/README.md",
]
# NOTE: identity/citation files (CITATION.cff, zenodo_metadata.json, LICENSE*,
# NOTICE, PROVENANCE.lock.json) are the WRAPPER that points TO this record; they are
# intentionally NOT fingerprinted, so the citation can embed the root without a
# circular dependency (embedding the root would otherwise change the root).
# never fingerprint these (mutable / generated / vendored)
EXCLUDE_SUBSTR = ["node_modules/", "__pycache__/", "/results", "results.json"]


def _excluded(path):
    return any(s in path for s in EXCLUDE_SUBSTR)


def collect_files():
    """Return the sorted, de-duplicated list of repo-relative frozen artifacts."""
    found = set()
    for g in GLOBS:
        for p in glob.glob(os.path.join(ROOT, g), recursive=True):
            rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
            if os.path.isfile(p) and not _excluded(rel):
                found.add(rel)
    for rel in EXPLICIT:
        if os.path.isfile(os.path.join(ROOT, rel)) and not _excluded(rel):
            found.add(rel)
    return sorted(found)


def sha256_file(rel):
    h = hashlib.sha256()
    with open(os.path.join(ROOT, rel), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def merkle_root(leaf_hexes):
    """Binary Merkle root over the ordered leaf hashes (duplicate last if odd).
    Domain-separated: leaves prefixed 0x00, internal nodes 0x01."""
    if not leaf_hexes:
        return hashlib.sha256(b"").hexdigest()
    level = [hashlib.sha256(b"\x00" + bytes.fromhex(h)).hexdigest() for h in leaf_hexes]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        nxt = []
        for i in range(0, len(level), 2):
            pair = bytes.fromhex(level[i]) + bytes.fromhex(level[i + 1])
            nxt.append(hashlib.sha256(b"\x01" + pair).hexdigest())
        level = nxt
    return level[0]


def compute():
    """Return (files, {path: leaf_sha256}, merkle_root)."""
    files = collect_files()
    leaves = {rel: sha256_file(rel) for rel in files}
    root = merkle_root([leaves[rel] for rel in files])
    return files, leaves, root
