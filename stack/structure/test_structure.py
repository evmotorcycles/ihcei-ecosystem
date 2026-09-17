"""Commit 4, the certificate layer over root lintel/. P7-P9.

The regression that matters is over the CERTIFICATES, against the numbers root
lintel/RESULTS.md and invisible-edges/RESULTS.md already recorded. A
bit-identical regression on an engine this module IMPORTS would compare a
function to itself, and `test_the_engine_regression_is_a_tautology_and_says_so`
records that rather than shipping it as if it meant something.
"""

from __future__ import annotations

import os
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
    omission_certificate, rewrite_certificate, split_module)


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


# ------------------------------------------------- the port is a port ----
def test_the_engine_is_imported_not_reimplemented():
    """Nothing here recomputes a cut vertex."""
    from stack.structure import lintel as ported
    assert ported.cuts is root_lintel.cuts
    assert ported.insert_shim is root_lintel.insert_shim
    assert ported.survivors is root_lintel.survivors
    src = open(os.path.join(HERE, "lintel.py"), encoding="utf-8").read()
    assert "articulation" not in src, "the port must not carry its own engine"


def test_the_engine_regression_is_a_tautology_and_says_so():
    """A bit-identical check on an imported engine compares a function to itself.

    Recorded rather than shipped as meaningful. `stack/organization/` had a real
    regression to run because the pre-rename arithmetic lived in a separate file
    and could have drifted; here there is nothing to drift from.
    """
    from stack.structure import lintel as ported
    assert ported.cuts is root_lintel.cuts          # the "regression", entire
    doc = " ".join(ported.__doc__.split())
    assert "is a tautology" in doc
    assert "compares a function to itself" in doc


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

    stable, raw = len(cert["stable_names"]), len(graph["raw"])
    lost = [d for d in cert["disputes"] if d["status"] == "lost"]
    gained = [d for d in cert["disputes"] if d["status"] == "gained"]

    assert 0 < stable < raw, (stable, raw)          # some survive, not all
    assert len(lost) >= 1 and len(gained) >= 1      # the sets are not nested
    assert stable + len(lost) == raw                # the residue accounts fully
    # and the recorded proportion still holds roughly: a clear majority survive
    assert 0.5 < stable / raw < 0.95, stable / raw


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
    assert set(out) == {"rewrite", "omission", "act_on", "disputed", "note"}
    # no scalar anywhere that merges the two
    for k in out:
        assert not any(w in k for w in ("score", "index", "integrity", "health"))
    assert out["act_on"] == sorted(set(rw["stable_names"]) & set(om["stable_names"]))
    assert 0 < len(out["act_on"]) < len(rw["stable_names"])


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
