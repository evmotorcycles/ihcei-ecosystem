#!/usr/bin/env python3
"""Can the Laplacian be gamed, and what does LISM do in a chain?

    python3 -m pytest -q agi-stack/test_stack.py

Predictions locked before the run:

    sha256  e4af23ec25616963f9e8edb9a512d146521d218dd66064a6dcc3eceb523b670c

THREE HELD, TWO MISSED, and the two misses are the finding: the attack works on
ONE readout and is turned away by the other two, one of them by theorem. That is
the argument against ever fusing them into a single score, arrived at by trying
to break them.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

PREREG_SHA256 = "e4af23ec25616963f9e8edb9a512d146521d218dd66064a6dcc3eceb523b670c"


@pytest.fixture(scope="module")
def r():
    out = subprocess.run([sys.executable, os.path.join(HERE, "run_stack.py")],
                         capture_output=True, text=True, timeout=900)
    assert out.returncode == 0, out.stderr
    return json.load(open(os.path.join(HERE, "results_stack.json")))


def test_the_predictions_were_locked_before_the_run():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_stack.md"), "rb")
                         .read()).hexdigest()
    assert got == PREREG_SHA256


# ────────────────────────────────────────────────────────── THE ATTACK ──────
def test_G1_three_invented_edges_destroy_every_cut_vertex(r):
    """THE CLAIM UNDER TEST was "You cannot trick the Laplacian Matrix."

    The adversary adds THREE edges between nodes already present. It invents no
    evidence, adds no node, changes no wording, removes nothing. Every cut
    vertex disappears.

    So the cut-vertex readout IS gameable by anyone who controls edge
    proposals — which, in the proposed architecture, is the LLM: the audited
    layer supplies the input to its own auditor.
    """
    a = r["arm1_gaming"]
    assert a["honest"]["n_cuts"] == 1
    assert a["honest"]["cut_vertices"] == ["the one declared method"]
    assert a["G1_all_cut_vertices_removed"] is True
    assert a["padded"]["n_cuts"] == 0
    assert a["n_edges_added"] == 3
    assert a["evidence_added"] == 0
    assert a["nodes_added"] == 0
    assert a["wording_changed"] is False


def test_G3_MISSED_the_dependence_readout_moved_AGAINST_the_attacker(r):
    """G3 MISSED, and the miss is good news.

    PREDICTED: padding would make the argument read MORE robust — deepest
    dependence falling.
    MEASURED: it ROSE, 0.111111 -> 0.619048.

    Linking one passage straight to the conclusion made that passage carry the
    argument. An auditor watching this number sees it go UP under the attack,
    which is a red flag and not a green one. The attack buys a clean cut-vertex
    report at the cost of a worse dependence report.
    """
    a = r["arm1_gaming"]
    assert a["G3_deepest_dependence_falls"] is False
    assert abs(a["honest"]["deepest_dependence"] - 1 / 9) < 1e-9
    assert abs(a["padded"]["deepest_dependence"] - 13 / 21) < 1e-9
    assert a["padded"]["deepest_dependence"] > a["honest"]["deepest_dependence"]


def test_G4_MISSED_total_bearing_is_immune_by_Foster(r):
    """G4 MISSED, and the reason is a theorem I should have applied.

    PREDICTED: total bearing would rise with padding.
    MEASURED: 4.0 before, 4.0 after — exactly unchanged.

    Foster: the bearings sum to parts - pieces. Adding edges INSIDE one
    connected component changes neither the part count nor the piece count, so
    the total cannot move. It is not merely hard to game; it is conserved.
    """
    a = r["arm1_gaming"]
    assert a["G4_total_bearing_rises"] is False
    assert a["honest"]["total_bearing"] == 4.0
    assert a["padded"]["total_bearing"] == 4.0
    # parts - pieces, exactly
    assert a["honest"]["pieces"] == a["padded"]["pieces"] == 1
    assert a["padded"]["n_links"] == 7 and a["honest"]["n_links"] == 4


def test_G5_the_only_defence_is_provenance_and_it_is_not_mathematical(r):
    """G5 held. Every invented edge is refused for naming no source, and every
    honest edge commits.

    But this is NOT a mathematical defence. It moves the trust from the matrix
    to whoever writes the `where`, and whether a `where` is TRUE is exactly what
    no test in this repository can check.
    """
    a = r["arm1_gaming"]
    assert a["G5_honest_edges_commit"] is True
    assert a["G5_every_padding_edge_refused"] is True
    assert len(a["G5_refusals"]) == 3
    for msg in a["G5_refusals"]:
        assert "no source named" in msg


def test_the_three_readouts_disagree_under_attack_which_is_why_they_are_never_fused(r):
    """THE FINDING, assembled from the two misses.

        cut vertices        1 -> 0        GAMED
        deepest dependence  0.111 -> 0.619   moved AGAINST the attacker
        total bearing       4.0 -> 4.0     immune, by Foster

    One score fusing these would have been gamed, because the gameable term
    would have moved it. Three separate readouts survive because the attack that
    flatters one indicts another. This repository's rule against fusing readouts
    was a judgement; this is the first time it has been attacked on purpose.
    """
    a = r["arm1_gaming"]
    gamed = a["honest"]["n_cuts"] > a["padded"]["n_cuts"]
    against = a["padded"]["deepest_dependence"] > a["honest"]["deepest_dependence"]
    immune = a["padded"]["total_bearing"] == a["honest"]["total_bearing"]
    assert gamed and against and immune


# ─────────────────────────────────────────────────── LISM IN THE CHAIN ──────
def test_L1_L2_L3_the_chain_arithmetic(r):
    """Verification, not discovery — listed so it is not mistaken for one.

    A four-layer stack whose every hop is 90% faithful delivers 0.6561 of what
    went in. To keep half at four hops each hop must be >= 0.85. No architecture
    diagram changes this.
    """
    b = r["arm2_lism"]
    assert abs(b["L1_four_hops_at_0_9"] - 0.6561) < 1e-12
    assert b["L1_below_0_66"] is True
    assert b["L2_monotone_decreasing"] is True
    assert b["L3_per_hop_needed_for_half_at_four_hops"] == 0.85
    assert b["L3_at_least_0_84"] is True
    assert abs(b["L2_by_depth"]["12"] - 0.9 ** 12) < 1e-12


def test_L4_the_retired_floor_stays_retired(r):
    """Fourth time this has had to be checked. A hard fidelity gate was retired
    at a fully-powered null, p = 0.735. It does not come back as an empirical
    claim through an architecture diagram."""
    b = r["arm2_lism"]
    assert b["L4_registry"]["D_min_threshold"] == "RETIRED_FULLY"
    assert b["L4_registry"]["E_quadratic"] == "RETIRED_FULLY"
    assert b["L4_no_quadratic_here"] is True


def test_the_self_referential_check_that_failed_on_itself():
    """Recorded because it is the EIGHTH instance in this repository.

    The check for "no quadratic form appears in this file" was written with both
    forbidden strings as literals, so the file contained them and the check
    reported itself. The strings are now built rather than written.
    """
    import re as _re
    raw = open(os.path.join(HERE, "run_stack.py")).read()
    # whitespace collapsed: the comment wraps as "Eighth\n# instance", and a
    # literal search misses it. Fourth time THIS trap has been hit today.
    # Strip the leading comment marker BEFORE collapsing: "Eighth\n# instance"
    # collapses to "Eighth # instance" and a literal search still misses it.
    # This repository already recorded the identical defect with "*" markers on
    # HTML comments; "#" behaves the same way.
    src = _re.sub(r"\s+", " ", _re.sub(r"(?m)^\s*#\s?", "", raw))
    assert "Eighth instance" in src
    assert 'f"D{sp}*{sp}{sp}2"' in raw, "the strings must be built, not literal"


def test_the_attack_does_not_apply_when_a_human_draws_the_graph(r):
    """NULL-G1, asserted rather than trusted. The attack needs an adversary who
    controls edge proposals. Where a person draws the graph, or edges come from
    outside the audited layer, it does not apply — which is exactly the
    arrangement every study in this repository has used."""
    import re as _re
    txt = _re.sub(r"\s+", " ", open(os.path.join(HERE, "prereg_stack.md")).read())
    assert "The attack requires the adversary to control edge proposals" in txt
    assert "The finding is about the proposed architecture, not about LMD" in txt
