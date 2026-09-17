"""Certificates over the measurements in root `lintel/` and `invisible-edges/`.

THIS IS A PORT THAT IMPORTS, NOT ONE THAT REIMPLEMENTS
======================================================
The engine is root `lintel/`. Nothing here recomputes a cut vertex, a rewrite or
a candidate edge -- CLAUDE.md: measure the structure, never hand-write the
number. What is new is the CERTIFICATE layer: naming the invariance group a
finding survived, marking counts untrusted, and emitting the dispute residue.

**A "bit-identical regression" on a port that imports its engine is a
tautology.** It compares a function to itself. `test_organization.py` had a real
regression to run because the original arithmetic lived in a separate file and
could have drifted; here there is nothing to drift from. The regression that
means something is over the CERTIFICATE layer, against the numbers root
`lintel/RESULTS.md` and `invisible-edges/RESULTS.md` already recorded, and that
is what the suite asserts.

WHAT A CERTIFICATE IS NOT, in the same size type as what it is
==============================================================
  * NOT a claim that a finding is true. It says a finding SURVIVED a named
    family of transformations. A stable finding can be a stable mistake.
  * NOT transferable between families. Measured on this repository's import
    graph: names survive **27/27** under rewrites of the drawing and only
    **18/27** under completion of what the drawing omits. A certificate that
    does not name its group is worthless.
  * NOT about counts. The count is inflatable at will -- 27 -> 39 -> 46 under
    re-export shims that change no behaviour -- so it is emitted marked
    untrusted and must never be compared between projects or across time.
  * NOT a breach detector. Candidate edges are not real edges, and 31 of 92
    candidates on this repository sat only in comments or docstrings. Disputes
    are disputed, not wrong.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (ROOT, os.path.join(ROOT, "lintel"), os.path.join(ROOT, "invisible-edges")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# the engine, imported. Not reimplemented.
from lintel import (bridges, collapse_passthrough, cuts,        # noqa: E402,F401
                    insert_shim, merge_pair, pieces, split_module, survivors)

#: the two invariance groups measured so far. A certificate names exactly one.
GROUP_REWRITE = ("behaviour-preserving rewrites of the drawing "
                 "(shims, splits, merges)")
GROUP_OMISSION = ("completion of what the drawing omits "
                  "(candidate edges; candidates are not real edges)")
GROUPS = (GROUP_REWRITE, GROUP_OMISSION)

COUNTS_ARE_UNTRUSTED = (
    "counts NOT comparable: inflatable by re-export shims that change no "
    "behaviour, so this number partly measures how finely code is split "
    "into files")


class InvarianceGroupError(ValueError):
    """A certificate was asked for without naming which group it holds under."""


def rewrite_certificate(parts, links, rewrites) -> dict:
    """Which names survive every rewrite. Counts emitted, marked untrusted."""
    res = survivors(parts, links, rewrites)
    counts = [len(cuts(parts, links))] + [r["cuts_after"] for r in res["per_rewrite"]]
    return {
        "invariance_group": GROUP_REWRITE,
        "stable_names": res["survivors"],
        "casualties": res["casualties"],
        "counts": counts,
        "counts_trusted": False,
        "counts_note": COUNTS_ARE_UNTRUSTED,
        "certificate": (f"stable under: {GROUP_REWRITE}; "
                        f"{COUNTS_ARE_UNTRUSTED} "
                        f"({' -> '.join(map(str, counts))})"),
    }


def omission_certificate(parts, declared_links, candidate_links) -> dict:
    """Intersect the declared reading with the completed one. Residue named.

    A name in the residue is DISPUTED, not wrong: a candidate edge is not a
    real edge, and no static pass can tell a dependency from a mention.
    """
    widened = sorted(set(declared_links) | set(candidate_links))
    wparts = sorted(set(parts) | {a for a, _, _ in candidate_links}
                    | {b for _, b, _ in candidate_links})
    dec, comp = cuts(parts, declared_links), cuts(wparts, widened)
    disputes = [{"name": m,
                 "status": "lost" if m in dec else "gained"}
                for m in sorted(dec ^ comp)]
    return {
        "invariance_group": GROUP_OMISSION,
        "stable_names": sorted(dec & comp),
        "disputes": disputes,
        "counts": [len(dec), len(comp)],
        "counts_trusted": False,
        "counts_note": COUNTS_ARE_UNTRUSTED,
        "certificate": (f"stable under: {GROUP_OMISSION}; "
                        f"{len(disputes)} name(s) disputed, not wrong"),
    }


def combined_report(rewrite_cert: dict, omission_cert: dict) -> dict:
    """Both certificates, side by side. NOT fused.

    The intersection of the two stable sets is reported as `act_on`, which is a
    set operation on two named groups -- not a score, not a grade, and not a
    combination of different kinds of quantity.
    """
    for cert in (rewrite_cert, omission_cert):
        if cert.get("invariance_group") not in GROUPS:
            raise InvarianceGroupError(
                "a certificate must name its invariance group; an unnamed one "
                "claims to hold under transformations nobody measured")
    a = set(rewrite_cert["stable_names"])
    b = set(omission_cert["stable_names"])
    return {
        "rewrite": rewrite_cert,
        "omission": omission_cert,
        "act_on": sorted(a & b),
        "disputed": sorted(a ^ b),
        "note": ("act_on survived BOTH named groups. disputed survived one and "
                 "not the other, which makes it disputed, not wrong."),
    }
