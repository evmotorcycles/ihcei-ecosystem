"""Certificates over the measurements in root `lintel/` and `invisible-edges/`.

THE DECISION, RECORDED: THIS MODULE IS A WRAPPER
================================================
Two options were on the table. **(a)** a wrapper that imports root `lintel/`, or
**(b)** a vendored copy regression-tested against a frozen fixture snapshot
external to both. **(a) was chosen**, and the consequences are taken in full:

  * Every engine symbol below is a **rebinding**, not a reimplementation.
    `stack.structure.lintel.cuts is lintel.cuts` -- the same function object.
  * **Drift between this module and the engine is impossible by construction.**
    There is one implementation. Nothing can diverge from itself.
  * **Therefore no regression against the engine ships here, in any form.** An
    earlier draft shipped one labelled "a tautology, recorded rather than
    claimed". That was still an identity check occupying a slot where evidence
    is expected, and a reader skimming a green suite counts it. It has been
    deleted. What the suite asserts instead is that the module IS a wrapper --
    a statement about construction, which is the licence for having no
    regression at all.
  * Had **(b)** been chosen, the obligation would have been the opposite: a
    frozen fixture snapshot living outside both copies, with drift as a real
    and testable failure. In neither case does an identity check ship labelled
    as evidence.

What is genuinely new here is the CERTIFICATE layer: naming the invariance
group a finding survived, hashing the subject it was measured over, dating it,
marking counts untrusted, and emitting the dispute residue.

WHAT A CERTIFICATE IS NOT, in the same size type as what it is
==============================================================
  * NOT a claim that a finding is true. It says a finding SURVIVED a named
    family of transformations. A stable finding can be a stable mistake.
  * NOT transferable between families. Measured on this repository's import
    graph: names survive **27/27** under rewrites of the drawing and only
    **18/27** under completion of what the drawing omits. A certificate that
    does not name its group is worthless.
  * NOT transferable between SUBJECTS. Those two figures were measured on
    2026-07-17. Adding `stack/` moved them to 31 and 23 with no certificate
    changing, which is why every certificate now carries a `subject_hash` over
    the edge list audited at audit time, and why `combined_report` refuses two
    certificates whose subjects differ.
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

# the engine, imported. Not reimplemented. See THE DECISION, above.
from lintel import (bridges, collapse_passthrough, cuts,        # noqa: E402,F401
                    insert_shim, merge_pair, pieces, split_module, survivors)
from stack.governance.certificate import (  # noqa: E402
    GROUP_NONE, require_same_subject, stamp, subject_hash)

#: This module rebinds the engine; it does not copy it. Asserted by the suite.
IS_A_WRAPPER = True
DRIFT_NOTE = ("drift from the engine is impossible by construction: these are "
              "the same function objects, so no regression against the engine "
              "ships here in any form")

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


def rewrite_certificate(parts, links, rewrites, at=None) -> dict:
    """Which names survive every rewrite. Counts emitted, marked untrusted.

    The subject hashed is the graph **as handed in** -- the drawing the
    rewrites were applied to, not any rewritten intermediate.
    """
    res = survivors(parts, links, rewrites)
    counts = [len(cuts(parts, links))] + [r["cuts_after"] for r in res["per_rewrite"]]
    return {
        **stamp("cut-vertex names", GROUP_REWRITE,
                subject_hash(parts, links), at=at),
        "stable_names": res["survivors"],
        "casualties": res["casualties"],
        "counts": counts,
        "counts_trusted": False,
        "counts_note": COUNTS_ARE_UNTRUSTED,
        "certificate": (f"stable under: {GROUP_REWRITE}; "
                        f"{COUNTS_ARE_UNTRUSTED} "
                        f"({' -> '.join(map(str, counts))})"),
    }


def omission_certificate(parts, declared_links, candidate_links, at=None) -> dict:
    """Intersect the declared reading with the completed one. Residue named.

    A name in the residue is DISPUTED, not wrong: a candidate edge is not a
    real edge, and no static pass can tell a dependency from a mention.

    `subject_hash` is over the **declared** graph, so this certificate is
    comparable with a rewrite certificate on the same drawing. The completion
    is a second graph and gets its own field rather than being folded in.
    """
    widened = sorted(set(declared_links) | set(candidate_links))
    wparts = sorted(set(parts) | {a for a, _, _ in candidate_links}
                    | {b for _, b, _ in candidate_links})
    dec, comp = cuts(parts, declared_links), cuts(wparts, widened)
    disputes = [{"name": m,
                 "status": "lost" if m in dec else "gained"}
                for m in sorted(dec ^ comp)]
    return {
        **stamp("cut-vertex names", GROUP_OMISSION,
                subject_hash(parts, declared_links), at=at),
        "completed_subject_hash": subject_hash(wparts, widened),
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
    # Both must be about the SAME drawing. Intersecting two certificates over
    # different subjects reads agreement off two different graphs, which is the
    # failure `subject_hash` was added to stop. Raises on a mismatch.
    subject = require_same_subject(rewrite_cert, omission_cert)
    a = set(rewrite_cert["stable_names"])
    b = set(omission_cert["stable_names"])
    return {
        "rewrite": rewrite_cert,
        "omission": omission_cert,
        "subject_hash": subject,
        "act_on": sorted(a & b),
        "disputed": sorted(a ^ b),
        "note": ("act_on survived BOTH named groups. disputed survived one and "
                 "not the other, which makes it disputed, not wrong."),
    }
