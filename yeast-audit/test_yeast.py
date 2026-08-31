#!/usr/bin/env python3
"""The real yeast interactome, against a claim of zero cut vertices.

    python3 -m pytest -q yeast-audit/test_yeast.py

Predictions locked before the graph was built:

    sha256  f8134f12f5223e736ce4c1dc3a76528d904c148d7f907039131c72e0ab1623d6
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

PREREG_SHA256 = "f8134f12f5223e736ce4c1dc3a76528d904c148d7f907039131c72e0ab1623d6"


@pytest.fixture(scope="module")
def r():
    out = subprocess.run([sys.executable, os.path.join(HERE, "run_yeast.py")],
                         capture_output=True, text=True, timeout=900)
    assert out.returncode == 0, out.stderr
    return json.load(open(os.path.join(HERE, "results_yeast.json")))


def test_the_predictions_were_locked_before_the_graph_was_built():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_yeast.md"), "rb")
                         .read()).hexdigest()
    assert got == PREREG_SHA256


def test_the_interactome_has_437_cut_vertices_not_zero(r):
    """Y1. The claim under test was 'Cut Vertices: 0'. Measured on the real
    STRING v12 physical-links graph: 437.

    593 proteins have exactly one interaction at this threshold. Every one of
    those makes its single neighbour a cut vertex. Zero would require
    2-connectivity everywhere, which no biological network of this size has.
    """
    assert r["n_cut_vertices"] == 437
    assert r["n_cut_vertices"] >= 100
    assert r["claimed_by_the_pasted_audit"]["n_cut_vertices"] == 0
    assert r["degree_one_nodes"] == 593


def test_the_edge_count_is_70201_not_15400(r):
    """Y2. A second divergence, and it is not a rounding difference: the
    published figure is 22% of the real one."""
    assert r["n_edges"] == 70201
    assert r["claimed_by_the_pasted_audit"]["n_edges"] == 15400


def test_the_graph_is_in_26_pieces(r):
    """Y3. The network is not one connected object. 4,772 of 4,825 proteins are
    in the largest component; the rest sit in 25 small islands."""
    assert r["n_pieces"] == 26
    assert r["largest_component"] == 4772


def test_the_largest_component_still_carries_every_cut_vertex(r):
    """Y4. Restricting to the giant component does not rescue the claim — all
    437 are inside it."""
    assert r["cut_vertices_in_largest_component"] == 437


def test_it_is_the_real_committed_string_file(r):
    """The reading is only worth anything if it is the real data. This is the
    file already committed here and already hashed by build_yeast_features.py.
    """
    assert r["n_nodes"] == 4825
    assert "STRING v12" in r["source"]
    frozen = json.load(open(os.path.join(
        ROOT, "biomedical-agency", "data", "yeast_channel_frozen.json")))
    assert frozen["_provenance"]["n_nodes"] == r["n_nodes"]
    assert frozen["_provenance"]["n_edges"] == r["n_edges"]


def test_the_category_error_is_recorded_as_an_argument_not_a_result():
    """The pasted audit concludes that zero cut vertices 'mathematically
    validates' Noble's pacemaker experiments. That inference does not hold in
    either direction, and 437 does not refute him either.

    A cut vertex is a fact about CONNECTIVITY: remove the node, the graph falls
    apart. Noble's result is about FUNCTIONAL redundancy: remove 80% of a
    current and the cell keeps time, because it re-routes dynamically. A protein
    can be a cut vertex and non-essential; a protein can be deeply embedded and
    lethal to lose.

    This repository's rule is that different quantities are never fused, and
    this is that rule applied to somebody else's conclusion. The paragraph is
    Layer 3 reasoning and is marked as such in the pre-registration rather than
    being presented as something the run established.
    """
    import re as _re
    # Whitespace collapsed first: the phrase is line-wrapped as "does not\n
    # measure the thing...", and a literal substring search misses it. Third
    # time this trap has been hit in this session alone.
    txt = _re.sub(r"\s+", " ", open(os.path.join(HERE, "prereg_yeast.md")).read())
    assert "category error" in txt.lower()
    assert "Layer 3 reasoning, not a result" in txt
    assert "does not measure the thing its conclusion is about" in txt
