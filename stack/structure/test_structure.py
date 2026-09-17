"""Commit 4, the certificate layer over root lintel/. P7-P9, plus the schema.

`stack/structure/lintel.py` is a **wrapper**, by recorded decision, so no
regression against the engine ships here in any form: there is one
implementation and nothing can drift from itself. What is asserted instead is
the CERTIFICATE layer -- the invariance group, the subject hash, the date, and
the dispute residue -- and every assertion about the residue is a RELATIONSHIP,
because the repository is its own subject and it grows.
"""

from __future__ import annotations

import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (ROOT, os.path.join(ROOT, "lintel"), os.path.join(ROOT, "page-code"),
           os.path.join(ROOT, "invisible-edges")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lintel as root_lintel                                      # noqa: E402
from blueprint import blueprint, modules                          # noqa: E402
from candidates import find_candidates                            # noqa: E402
from stack.structure.lintel import (  # noqa: E402
    COUNTS_ARE_UNTRUSTED, GROUP_OMISSION, GROUP_REWRITE, GROUPS,
    InvarianceGroupError, combined_report, cuts, insert_shim,
    omission_certificate, rewrite_certificate, split_module,
    subject_hash)


@pytest.fixture(scope="module")
def graph():
    bp = blueprint(ROOT, "repo")
    p = bp["project"]
    parts, links = p["parts"], [tuple(e) for e in p["links"]]
    idx = modules(ROOT)
    paths = {rel: meta["path"] for rel, meta in idx.items()}
    declared = {(a, b) if a < b else (b, a) for a, b, *_ in links}
    cands = find_candidates(parts, paths, declared)
    return {"parts": parts, "links": links,
            "cands": [(c["from"], c["to"], 1.0) for c in cands],
            "raw": cuts(parts, links)}


# -------------------------------------- the recorded decision: WRAPPER ----
def test_the_module_is_a_wrapper_which_is_why_it_ships_no_engine_regression():
    """Option (a) was chosen and recorded. This asserts the CONSTRUCTION.

    Not a regression, and not an identity check standing in for one. It
    establishes that there is exactly one implementation, which is the licence
    for this package having no engine regression at all. An earlier draft did
    ship one, labelled "a tautology, recorded rather than claimed" -- but a
    reader skimming a green suite counts it, so it was deleted rather than
    annotated. Option (b), a vendored copy, would have carried the opposite
    obligation: a frozen fixture snapshot external to both copies, with drift a
    real and testable failure.
    """
    from stack.structure import lintel as ported
    assert ported.IS_A_WRAPPER is True
    assert ported.cuts is root_lintel.cuts
    assert ported.insert_shim is root_lintel.insert_shim
    assert ported.survivors is root_lintel.survivors
    src = open(os.path.join(HERE, "lintel.py"), encoding="utf-8").read()
    assert "articulation" not in src, "the wrapper must not carry its own engine"
    assert "impossible by construction" in ported.DRIFT_NOTE


def test_the_decision_is_recorded_in_the_module_and_in_the_ledger():
    from stack.structure import lintel as ported
    doc = " ".join(ported.__doc__.split())
    assert "THE DECISION, RECORDED: THIS MODULE IS A WRAPPER" in doc
    assert "Drift between this module and the engine is impossible" in doc
    assert "In neither case does an identity check ship labelled as evidence" in doc
    ledger = " ".join(open(os.path.join(ROOT, "stack", "governance",
                                        "declarations.md"),
                           encoding="utf-8").read().split())
    assert "wrapper, not a vendored copy" in ledger


def test_no_test_in_this_package_compares_the_engine_to_itself():
    """The deleted check, asserted deleted. Otherwise it drifts back in.

    Instance SIXTEEN of a check matching the text that describes it: the first
    draft grepped its own source for the deleted function's name, and the name
    was right there in the assertion. The fix is not a cleverer string -- it is
    to stop matching text at all and read the DEFINED FUNCTIONS out of the
    parse tree, which is what the rule was always about.
    """
    import ast
    tree = ast.parse(open(os.path.join(HERE, "test_structure.py"),
                          encoding="utf-8").read())
    names = {n.name for n in ast.walk(tree)
             if isinstance(n, ast.FunctionDef)}
    assert names, "the parse found no tests, so it proved nothing"
    assert not any(n.startswith("test_the_engine_regression") for n in names)


# ------------------------------------------- P7: the rewrite certificate ----
def test_p7_the_rewrite_certificate_names_its_group_and_keeps_the_names(graph):
    parts, links = graph["parts"], graph["links"]
    br = root_lintel.bridges(parts, links)
    both = [c for c in sorted(graph["raw"])
            if any(l[1] == c for l in links) and any(l[0] == c for l in links)]
    rw = [("INSERT", lambda p, l: insert_shim(p, l, br[0])),
          ("SPLIT", lambda p, l: split_module(p, l, both[0]))]
    cert = rewrite_certificate(parts, links, rw)
    assert cert["invariance_group"] == GROUP_REWRITE
    # all of them survive, whatever the current count is -- the repo grows
    assert len(cert["stable_names"]) == len(graph["raw"])
    assert cert["casualties"] == []


def test_p7_the_counts_are_emitted_and_marked_untrusted(graph):
    parts, links = graph["parts"], graph["links"]
    br = root_lintel.bridges(parts, links)
    cert = rewrite_certificate(
        parts, links, [("INSERT", lambda p, l: insert_shim(p, l, br[0]))])
    assert cert["counts_trusted"] is False
    assert "NOT comparable" in cert["counts_note"]
    assert cert["counts"][1] > cert["counts"][0]      # a shim inflated it
    assert COUNTS_ARE_UNTRUSTED in cert["certificate"]


# ------------------------------------------ P8: the omission certificate ----
def test_p8_the_omission_certificate_holds_as_a_RELATIONSHIP_not_a_number(graph):
    """The frozen numbers from invisible-edges/RESULTS.md CANNOT be asserted.

    That file recorded 27 declared cut vertices, 18 stable, 9 lost, 4 gained.
    Adding `stack/` to this repository changed the graph it audits: now 31
    declared, 23 stable, 8 lost, 6 gained. **The repository is its own subject
    and it grew.**

    This is the same defect `page-code/` hit when `files_scanned == 401` broke
    to 402 the moment its own test file was added. The fix is the same: assert
    the relationships that carry the finding, never the frozen count. It is
    also the counts-are-untrusted rule turning up in a place I did not expect
    it -- the number of NAMES moves too, because the subject moves.
    """
    cert = omission_certificate(graph["parts"], graph["links"], graph["cands"])
    assert cert["invariance_group"] == GROUP_OMISSION

    # recompute the completed reading here, so the relationships are asserted
    # against the graph and not against the certificate's own bookkeeping
    widened = sorted(set(graph["links"]) | set(graph["cands"]))
    wparts = sorted(set(graph["parts"]) | {a for a, _, _ in graph["cands"]}
                    | {b for _, b, _ in graph["cands"]})
    declared, completed = set(graph["raw"]), set(cuts(wparts, widened))

    stable = set(cert["stable_names"])
    lost = {d["name"] for d in cert["disputes"] if d["status"] == "lost"}
    gained = {d["name"] for d in cert["disputes"] if d["status"] == "gained"}

    # RELATIONSHIPS ONLY. Not one frozen count, and not a frozen ratio either:
    # a band like `0.5 < stable/raw < 0.95` is a count wearing a disguise and
    # would need renegotiating every time the repository grows.
    assert stable <= declared                    # stable is a SUBSET
    assert stable == declared & completed        # exactly the intersection
    assert lost | gained == declared ^ completed  # disputes ARE the symdiff
    assert lost == declared - completed
    assert gained == completed - declared
    assert stable | lost == declared             # the residue completes it
    assert lost and gained                       # the sets are not nested
    assert stable                                # and not everything is lost


def test_p8_a_declared_only_graph_has_an_empty_residue(graph):
    """The control: with no candidates, nothing is disputed."""
    cert = omission_certificate(graph["parts"], graph["links"], [])
    assert cert["disputes"] == []
    assert len(cert["stable_names"]) == len(graph["raw"])


def test_p8_disputes_are_named_disputed_not_wrong(graph):
    cert = omission_certificate(graph["parts"], graph["links"], graph["cands"])
    assert "disputed, not wrong" in cert["certificate"]
    for d in cert["disputes"]:
        assert d["status"] in ("lost", "gained")
        assert "wrong" not in d["status"]


# ------------------------------------------------- P9: the two together ----
def test_p9_the_two_certificates_are_reported_side_by_side_not_fused(graph):
    parts, links = graph["parts"], graph["links"]
    br = root_lintel.bridges(parts, links)
    rw = rewrite_certificate(
        parts, links, [("INSERT", lambda p, l: insert_shim(p, l, br[0]))])
    om = omission_certificate(parts, links, graph["cands"])
    out = combined_report(rw, om)
    assert set(out) == {"rewrite", "omission", "act_on", "disputed", "note",
                        "subject_hash"}
    # no scalar anywhere that merges the two
    for k in out:
        assert not any(w in k for w in ("score", "index", "integrity", "health"))
    assert out["act_on"] == sorted(set(rw["stable_names"]) & set(om["stable_names"]))
    assert 0 < len(out["act_on"]) < len(rw["stable_names"])


# ------------------------------- the schema: subject_hash and date ----
def test_every_certificate_carries_the_four_schema_fields(graph):
    from stack.governance.certificate import SCHEMA_VERSION, require_schema
    parts, links = graph["parts"], graph["links"]
    br = root_lintel.bridges(parts, links)
    for cert in (rewrite_certificate(
                     parts, links,
                     [("INSERT", lambda p, l: insert_shim(p, l, br[0]))]),
                 omission_certificate(parts, links, graph["cands"])):
        require_schema(cert)                 # raises if any field is missing
        assert cert["readout"] == "cut-vertex names"
        assert len(cert["subject_hash"]) == 64
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", cert["date"])
        assert cert["schema"] == SCHEMA_VERSION


def test_both_certificates_hash_the_SAME_declared_subject(graph):
    """Which is what makes intersecting them legitimate at all."""
    parts, links = graph["parts"], graph["links"]
    br = root_lintel.bridges(parts, links)
    rw = rewrite_certificate(
        parts, links, [("INSERT", lambda p, l: insert_shim(p, l, br[0]))])
    om = omission_certificate(parts, links, graph["cands"])
    assert rw["subject_hash"] == om["subject_hash"]
    # and the completion is a DIFFERENT graph, recorded separately
    assert om["completed_subject_hash"] != om["subject_hash"]


def test_the_subject_hash_moves_when_the_drawing_moves(graph):
    """Relationship, not a frozen digest. `27 -> 31` happened with no
    certificate changing; this is the field that would have caught it."""
    from stack.structure.lintel import subject_hash
    parts, links = graph["parts"], graph["links"]
    base = subject_hash(parts, links)
    assert subject_hash(list(reversed(parts)), list(links)) == base  # order-free
    assert subject_hash(parts + ["a/module/added/later.py"], links) != base
    assert subject_hash(parts, list(links) + [(parts[0], parts[-1])]) != base


def test_two_certificates_over_different_subjects_refuse_to_combine(graph):
    """The teeth. Without this the schema is decoration."""
    from stack.governance.certificate import SubjectMismatchError
    parts, links = graph["parts"], graph["links"]
    br = root_lintel.bridges(parts, links)
    rw = rewrite_certificate(
        parts, links, [("INSERT", lambda p, l: insert_shim(p, l, br[0]))])
    om = omission_certificate(parts, links, graph["cands"])
    grown = dict(om)
    grown["subject_hash"] = "0" * 64          # a different graph entirely
    with pytest.raises(SubjectMismatchError, match="different subjects"):
        combined_report(rw, grown)


def test_a_legacy_certificate_is_marked_not_back_dated(graph):
    """No hash is invented for a certificate issued before the schema.

    A hash computed today over today's graph would attest to a subject the old
    certificate never saw, which is worse than having no hash at all.
    """
    from stack.governance.certificate import (CertificateSchemaError,
                                              mark_legacy, require_schema)
    om = omission_certificate(graph["parts"], graph["links"], graph["cands"])
    old = mark_legacy(om)
    assert old["subject_hash"] is None
    assert "not comparable" in old["legacy_note"]
    with pytest.raises(CertificateSchemaError, match="legacy"):
        require_schema(old)


def test_p9_an_unnamed_invariance_group_is_refused(graph):
    om = omission_certificate(graph["parts"], graph["links"], graph["cands"])
    bad = dict(om)
    bad["invariance_group"] = "survives everything"
    with pytest.raises(InvarianceGroupError, match="must name its invariance"):
        combined_report(bad, om)
    assert len(GROUPS) == 2, "a third group needs its own measurement first"


def test_the_two_groups_genuinely_disagree(graph):
    """Otherwise naming the group would be ceremony.

    27/27 under rewrites, 18/27 under omissions -- the certificate has to say
    which, because the answer differs.
    """
    parts, links = graph["parts"], graph["links"]
    br = root_lintel.bridges(parts, links)
    rw = rewrite_certificate(
        parts, links, [("INSERT", lambda p, l: insert_shim(p, l, br[0]))])
    om = omission_certificate(parts, links, graph["cands"])
    assert len(rw["stable_names"]) != len(om["stable_names"])
    assert len(om["stable_names"]) < len(rw["stable_names"])


# --------------------------------------------------------- no overclaim ----
def test_the_recorded_numbers_are_cited_as_of_a_date_not_as_invariants():
    """Because the subject grows, a write-up must date its counts."""
    doc = " ".join(open(os.path.join(HERE, "lintel.py"), encoding="utf-8")
                   .read().split())
    assert "27/27" in doc and "18/27" in doc
    assert "Measured on this repository's import graph" in doc
    results = os.path.join(ROOT, "stack", "structure", "RESULTS.md")
    assert os.path.exists(results), "the write-up must exist to be checked"
    # collapse whitespace first: the sentence wraps across lines in the markdown
    # and a raw substring match missed it. CLAUDE.md's own lexical rule.
    text = " ".join(open(results, encoding="utf-8").read().split()).lower()
    assert "the repository is its own subject" in text
    assert "169" in text and "156" in text, "the write-up must date its counts"


def test_the_module_states_what_a_certificate_is_not():
    from stack.structure import lintel as ported
    doc = " ".join(ported.__doc__.split())
    assert "NOT a claim that a finding is true" in doc
    assert "stable finding can be a stable mistake" in doc
    assert "NOT transferable between families" in doc
    assert "NOT a breach detector" in doc


def test_door_two_is_recorded_shut_before_any_swarm_code_exists():
    status = os.path.join(ROOT, "stack", "swarm", "DOOR2_STATUS.md")
    assert os.path.exists(status)
    text = " ".join(open(status, encoding="utf-8").read().split())
    assert "Branch B" in text
    assert "egress-blocked from this container" in text
    assert "P24, P25 and P26 are **unwritten**" in text
    # and no predictions were smuggled in anyway
    assert not os.path.exists(os.path.join(ROOT, "stack", "swarm",
                                           "prereg_swarm.md"))
