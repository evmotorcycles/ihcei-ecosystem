"""Invisible edges, the quotient, and two JEPA cards, against locked predictions.

Nine hit, one missed. The miss is Q3, and it is the reason the quotient does
not ship as a repaired count.

One instrument defect is kept as evidence: J2 first read MISS because "ema"
matched inside "semantically".
"""

import hashlib
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (HERE, ROOT, os.path.join(ROOT, "page-code"), os.path.join(ROOT, "lintel")):
    sys.path.insert(0, p)

import run_invisible as R                                        # noqa: E402
from candidates import (KIND_COMMENT, find_candidates,           # noqa: E402
                        indirection_nodes, quotient)
from lintel import cuts, insert_shim, merge_pair                 # noqa: E402

PREREG_SHA = "1f3455944c51ef2f306bf2d50041e046438a8077ee2124c34c716b5d9f23edc9"
CARDS = os.path.join(HERE, "cards")


@pytest.fixture(scope="module")
def g():
    parts, links, paths = R.base_graph()
    declared = {(a, b) if a < b else (b, a) for a, b, *_ in links}
    cands = find_candidates(parts, paths, declared)
    widened = sorted(set(links) | {(c["from"], c["to"], 1.0) for c in cands})
    return {"parts": parts, "links": links, "paths": paths,
            "cands": cands, "raw": cuts(parts, links),
            "wide": cuts(parts, widened), "widened": widened}


# ------------------------------------------------------------- the lock ----
def test_the_preregistration_is_the_one_that_was_hashed():
    with open(os.path.join(HERE, "prereg_invisible.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == PREREG_SHA


def test_the_run_declares_the_same_hash():
    assert PREREG_SHA in open(os.path.join(HERE, "run_invisible.py")).read()


# ------------------------------------------ arm 1: the answer to the ask ----
def test_i1_candidate_invisible_edges_exist(g):
    assert len(g["cands"]) >= 20


def test_i2_static_analysis_cannot_tell_a_dependency_from_a_mention(g):
    """The load-bearing finding. A filename in prose looks like a call site."""
    prose = [c for c in g["cands"] if c["kind"] == KIND_COMMENT]
    assert len(prose) >= 1
    # and the detector says so in its own words rather than pretending
    import candidates
    doc = " ".join(candidates.__doc__.split())
    assert "A CANDIDATE IS NEVER AN EDGE" in doc
    assert "can say nothing about its recall" in doc


def test_i3_and_i4_adding_candidates_both_removes_and_creates_cut_vertices(g):
    lost = g["raw"] - g["wide"]
    new = g["wide"] - g["raw"]
    assert len(lost) >= 1
    assert len(new) >= 1


def test_i5_the_two_readings_are_not_nested(g):
    assert not (g["raw"] <= g["wide"])
    assert not (g["wide"] <= g["raw"])


def test_i6_the_names_do_not_survive_invisible_edges(g):
    """LINTEL's certificate is narrower than it looked.

    Stable under how the code is DRAWN. Not stable under what the drawing
    LEAVES OUT. Those are different invariance groups and only the first was
    measured in lintel/.
    """
    survived = g["raw"] & g["wide"]
    assert len(survived) < len(g["raw"])
    assert len(survived) >= 1        # not a total collapse either


def test_the_shipped_advice_is_intersect_not_replace(g):
    """The answer: run it twice and report what is in both, naming the disputed.

    Candidates must never go straight into the Laplacian -- I2 shows they
    cannot be cleaned first.
    """
    agreed = g["raw"] & g["wide"]
    disputed = (g["raw"] | g["wide"]) - agreed
    assert agreed and disputed
    assert len(agreed) + len(disputed) == len(g["raw"] | g["wide"])


# ------------------------------------------------------ arm 2: quotient ----
def _cols(g, n_shims, seed=0):
    import random
    rng = random.Random(seed)
    edges = sorted({(a, b) for a, b, *_ in g["links"]})
    p, l = list(g["parts"]), list(g["links"])
    for k, e in enumerate(rng.sample(edges, n_shims)):
        p, l = insert_shim(p, l, e, tag=f"#{k}")
    qp, ql, removed = quotient(p, l)
    return {"cuts": len(cuts(p, l)), "qcuts": len(cuts(qp, ql)),
            "removed": removed,
            "edges": sorted((a, b) for a, b, *_ in ql)}


def test_q1_the_quotient_count_is_identical_across_shim_counts(g):
    a, b, c = _cols(g, 0), _cols(g, 20), _cols(g, 40)
    assert a["qcuts"] == b["qcuts"] == c["qcuts"]
    assert a["cuts"] < b["cuts"] < c["cuts"]      # the raw count did move


def test_q2_the_quotient_edge_sets_are_identical(g):
    a, b, c = _cols(g, 0), _cols(g, 20), _cols(g, 40)
    assert a["edges"] == b["edges"] == c["edges"]


def test_the_prediction_that_missed(g):
    """Q3. The quotient is NOT the identity on the un-shimmed graph.

    It collapses every one-in one-out node, and this repository has real
    modules with that shape which are not indirection at all. So the quotient
    count is not a repaired reading of the original graph -- it is a correct
    reading of a DIFFERENT graph, one with real modules deleted.

    That is why the quotient does not upgrade LINTEL to a trustworthy scalar,
    and the shipped advice stays: trust the list, never the count.
    """
    zero = _cols(g, 0)
    assert len(zero["removed"]) > 0
    real = indirection_nodes(g["parts"], g["links"])
    assert real
    for n in zero["removed"]:
        assert "→shim→" not in n, "it erased a real module, not a shim"


def test_q4_merging_a_cut_vertex_deflates_the_count(g):
    """So the count is two-sided: inflatable by shims, deflatable by merges."""
    pairs = [(a, b) for a, b, *_ in g["links"]
             if b in g["raw"]
             and {x for x, y, *_ in g["links"] if y == b} == {a}]
    assert pairs
    a, b = pairs[0]
    mp, ml = merge_pair(g["parts"], g["links"], a, b)
    assert len(cuts(mp, ml)) < len(g["raw"])


# --------------------------------------------------- arm 3: JEPA cards ----
def _cards():
    return {fn: open(os.path.join(CARDS, fn), encoding="utf-8").read().lower()
            for fn in sorted(os.listdir(CARDS))}


def test_the_cards_are_the_ones_that_were_fetched():
    c = _cards()
    assert len(c) == 2
    ij = next(t for f, t in c.items() if "ijepa" in f)
    assert "arxiv:2301.08243" in ij or "2301.08243" in ij
    vj = next(t for f, t in c.items() if "vjepa2" in f)
    assert "v-jepa 2" in vj


def test_j1_neither_card_mentions_representation_collapse():
    for fn, txt in _cards().items():
        assert "collapse" not in txt, fn
        assert "collapsing" not in txt, fn


def test_j2_neither_card_names_the_mechanism():
    """Not a criticism. A model card is not a paper.

    The mechanism that does all the work in jepa-probe is one sentence of
    arXiv:2301.08243 section 2 and zero sentences of what a practitioner
    downloads.
    """
    phrases = ("stop-gradient", "stop gradient", "stopgrad",
               "exponential moving average", "moving average",
               "target encoder", "target-encoder")
    for fn, txt in _cards().items():
        for p in phrases:
            assert p not in txt, f"{fn}: {p}"
        assert not re.search(r"\bema\b", txt), fn


def test_the_instrument_defect_that_made_j2_look_like_a_miss():
    """J2 first read MISS. "ema" was matched as a SUBSTRING.

    It occurs inside "semantically", which is ordinary English in a card about
    semantic representations. The acronym needs word boundaries; the phrases do
    not. Second instrument defect in two turns, after the bridge-direction bug
    in lintel.
    """
    ij = next(t for f, t in _cards().items() if "ijepa" in f)
    assert "ema" in ij                       # the substring really is there
    assert "semantically" in ij              # and this is where it lives
    assert not re.search(r"\bema\b", ij)     # the fixed test does not fire


def test_j3_the_ijepa_card_does_state_what_it_avoids():
    """So the absence in J1/J2 is not a card that says nothing."""
    ij = next(t for f, t in _cards().items() if "ijepa" in f)
    assert "hand-crafted" in ij
    assert "pixel-level details" in ij


def test_the_fixture_records_that_the_cards_came_back_whole():
    import json
    m = json.load(open(os.path.join(HERE, "jepa_cards_frozen.json")))
    assert m["_provenance"]["fetched_at"] == "2026-09-15"
    assert "attested manual step" in m["_provenance"]["note"]
    for entry in m["models"]:
        assert entry["truncated"] is False


# --------------------------------------------------------- no overclaim ----
def test_the_results_do_not_claim_the_detector_is_complete():
    r = open(os.path.join(HERE, "RESULTS.md"), encoding="utf-8").read()
    assert "recall" in r.lower()
    assert "What this cannot do" in r
    low = r.lower()
    for banned in ("finds every hidden dependency", "complete list of",
                   "all invisible edges"):
        assert banned not in low, banned
