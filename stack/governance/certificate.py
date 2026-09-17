"""The certificate schema. Four fields, and one of them is new.

    (readout, invariance_group, subject_hash, date)

WHY `subject_hash` WAS ADDED
============================
`stack/structure/` recorded 27 declared cut vertices, 18 stable. Adding `stack/`
to this repository moved that to 31 and 23 **without any certificate changing**,
because a certificate said what it held under and never said what it held
*about*. Two certificates over two different graphs could be intersected and the
result read as agreement.

`subject_hash` closes that. It hashes **the edge list actually audited, at audit
time**. A certificate whose subject hash differs from another's is a statement
about a different graph, and `require_same_subject` refuses to combine them.

WHY `date` WAS ADDED
====================
The subject grows. `156 -> 169` modules, `27 -> 31` cuts, inside one session. A
count without a date is an invariant claim the measurement cannot support.

WHAT A SUBJECT HASH IS NOT
==========================
  * NOT a content hash of the code. It hashes the DRAWING -- parts and declared
    links. Two different codebases with the same import graph hash identically,
    and the same codebase re-drawn by a different extractor does not.
  * NOT stable under renaming. Renaming a module changes the subject hash while
    changing nothing about the system. That is the correct behaviour for a
    field whose job is to refuse false comparisons, and it means a hash mismatch
    is a reason to look, not a finding.
  * NOT a trust anchor. Anyone can compute one over any graph they like.

LEGACY CERTIFICATES
===================
A certificate issued before this schema carries no subject hash, so nothing can
be said about what it was measured over. `mark_legacy` stamps it as such and
`require_schema` refuses it for anything but display. Legacy certificates are
not migrated by inventing a hash for them -- a hash computed today over today's
graph would attest to a subject the old certificate never saw.
"""

from __future__ import annotations

import hashlib
import re
from datetime import date as _date
from datetime import datetime, timezone

SCHEMA_VERSION = "cert/2"

#: Every certificate carries exactly these, beside whatever it measured.
CERT_FIELDS = ("readout", "invariance_group", "subject_hash", "date",
               "schema")

#: For a raw reading that has survived no transformation family at all. Naming
#: the absence is the point: an audit output is a READING, not a certificate,
#: and calling it one would claim a stability nobody measured.
GROUP_NONE = ("none measured: a raw reading, not a certificate; it has "
              "survived no family of transformations")

LEGACY_NOTE = ("legacy: issued before the subject was hashed, so what it was "
               "measured over is unrecorded and it is not comparable with any "
               "other certificate")

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class CertificateSchemaError(ValueError):
    """A certificate is missing a schema field, or carries a malformed one."""


class SubjectMismatchError(ValueError):
    """Two certificates describe different graphs and were about to be merged."""


# --------------------------------------------------------- the subject ----
def subject_hash(parts, links) -> str:
    """Hash the drawing: sorted parts and the sorted undirected edge list.

    Weights are deliberately excluded. The structural readouts these
    certificates cover -- cut vertices, reachability -- do not read weights, so
    including them would make the hash refuse comparisons the readout permits.
    `subject_hash_of_matrix` documents the one place weights do enter.
    """
    edges = sorted({(str(a), str(b)) if str(a) <= str(b) else (str(b), str(a))
                    for a, b, *_ in links})
    blob = "\n".join(["PARTS"] + sorted(str(p) for p in parts)
                     + ["LINKS"] + [f"{a}\t{b}" for a, b in edges])
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def subject_hash_of_matrix(C) -> str:
    """The audited edge list read off a conductance matrix, at audit time.

    Weights ARE included here, because the audit's readouts -- resistance and
    load -- move with them. Two matrices differing only in a weight are
    different subjects for this readout and the same subject for the other, and
    that is a real distinction rather than an inconsistency.
    """
    n = len(C)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            w = float(C[i][j])
            if w > 0.0:
                edges.append(f"{i}\t{j}\t{w!r}")
    blob = "\n".join([f"PARTS\t{n}", "LINKS"] + edges)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# ---------------------------------------------------------- the stamp ----
def stamp(readout: str, invariance_group: str, subject: str, at=None) -> dict:
    """The four schema fields, ready to merge into a readout dict."""
    if not readout or not isinstance(readout, str):
        raise CertificateSchemaError("a certificate must name its readout")
    if not invariance_group or not isinstance(invariance_group, str):
        raise CertificateSchemaError(
            "a certificate must name its invariance group, or GROUP_NONE if it "
            "has survived nothing")
    if not isinstance(subject, str) or len(subject) != 64:
        raise CertificateSchemaError(
            "subject_hash must be a sha256 hex digest of the audited edge list")
    when = at if at is not None else datetime.now(timezone.utc).date().isoformat()
    if isinstance(when, _date):
        when = when.isoformat()
    if not _ISO.match(when):
        raise CertificateSchemaError(f"date {when!r} is not ISO yyyy-mm-dd")
    return {"readout": readout, "invariance_group": invariance_group,
            "subject_hash": subject, "date": when, "schema": SCHEMA_VERSION}


def mark_legacy(cert: dict) -> dict:
    """Stamp a pre-schema certificate as legacy. No hash is invented for it."""
    out = dict(cert)
    out["schema"] = "legacy"
    out["subject_hash"] = None
    out["legacy_note"] = LEGACY_NOTE
    return out


def require_schema(cert: dict) -> None:
    for f in CERT_FIELDS:
        if f not in cert:
            raise CertificateSchemaError(
                f"certificate is missing {f!r}; the schema is {CERT_FIELDS}")
    if cert["schema"] == "legacy":
        raise CertificateSchemaError(
            f"{cert.get('readout')!r}: {LEGACY_NOTE}")
    if cert["schema"] != SCHEMA_VERSION:
        raise CertificateSchemaError(
            f"unknown schema {cert['schema']!r}; expected {SCHEMA_VERSION!r}")
    stamp(cert["readout"], cert["invariance_group"], cert["subject_hash"],
          at=cert["date"])


def require_same_subject(*certs) -> str:
    """Refuse to combine certificates measured over different graphs."""
    for c in certs:
        require_schema(c)
    subjects = {c["subject_hash"] for c in certs}
    if len(subjects) != 1:
        raise SubjectMismatchError(
            "these certificates were measured over different subjects "
            f"({sorted(s[:12] for s in subjects)}); intersecting them would "
            "read agreement off two different graphs")
    return subjects.pop()
