#!/usr/bin/env python3
"""The 24-model HF fixture at the metadata level, and two predictions that failed.

    python3 -m pytest -q plexus/test_hf_meta.py

Locked before anything was computed:
    hf_meta_preregistration.md
    sha256 335c8d01b501bd0da6778663eca866852249e8f7fbb822a99ae563b5f9f5e84d

TWO OF SIX PREDICTIONS FAILED (G1 and G5) and both are recorded below rather
than adjusted. The run also exposed a defect in press.js that made the FIRST set
of numbers invalid -- see test_the_node_collision_that_invalidated_the_first_run.
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

from spar.spar import Structure, bearings  # noqa: E402

PREREG = "335c8d01b501bd0da6778663eca866852249e8f7fbb822a99ae563b5f9f5e84d"


@pytest.fixture(scope="module")
def g():
    try:
        out = subprocess.run(["node", os.path.join(HERE, "hf_meta_dump.mjs")],
                             capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_predictions_were_locked_before_anything_was_computed():
    got = hashlib.sha256(open(os.path.join(HERE, "hf_meta_preregistration.md"),
                              "rb").read()).hexdigest()
    assert got == PREREG


# --------------------------------------------------------------- the defect --
def test_the_node_collision_that_invalidated_the_first_run(g):
    """Found by running press.js over real model lineage, not by reading it.

    thinkingmachines/Inkling is both a model in this cohort AND the declared
    base of unsloth/inkling-GGUF, so graph() added it once as a mark and once as
    an origin. bearings() keys nodes by name, so the two silently became one:
    35 parts went in and 34 were measured. Every dependence in that first run
    was computed on a graph nobody had described.

    This is not a corner case. On any lineage data a thing is routinely both a
    derivative and a base, so it is the normal case. One name registry now
    covers marks and origins together, and the mark is the side disambiguated
    because the origin is what is being pointed at.
    """
    assert g["structure"]["parts"] == 35, \
        "24 marks + 10 origins + the claim; if this is 34 the collision is back"
    assert g["origins"] == 10
    assert "thinkingmachines/Inkling (2)" in g["originList"], \
        "the disambiguated node must still be present and still readable"


def test_the_two_predictions_that_failed(g):
    """G1 and G5, reported as failures rather than adjusted.

    G1 predicted at least half the models would report evaluation results with
    no arXiv reference -- figures with no paper a third party can open. The
    measured share is 0.2917. The expectation was wrong.

    G5 predicted every model would settle below 1/24. The largest settles
    0.087366, twice the naive figure. The prediction assumed the single-origin
    shape; with ten origins a model alone on its own origin carries that whole
    route, so it settles MORE, not less. Wrong summary statistic, chosen before
    thinking the graph through.
    """
    assert abs(g["evalNoPaper"]["share"] - 7 / 24) < 1e-9
    assert g["evalNoPaper"]["share"] < 0.50, "G1 failed and this pins the failure"

    assert abs(g["maxSettles"] - 0.087366) < 1e-5
    assert g["maxSettles"] > g["naive"], "G5 failed and this pins the failure"


def test_the_predictions_that_held(g):
    """G2, G3, G4, G6."""
    assert g["withArxiv"]["share"] <= 0.35
    assert abs(g["withArxiv"]["share"] - 0.25) < 1e-9

    assert g["noBase"]["share"] >= 0.50
    assert g["noBase"]["n"] == 12

    assert g["origins"] < 24
    assert g["flagged"]["n"] >= 1 and g["flagged"]["n"] == 4


def test_declaring_no_origin_puts_you_in_the_biggest_pile(g):
    """The finding, once the arithmetic was run on a correct graph.

    Half the cohort declares no base model at all, so all twelve hang off the
    same unnamed node -- and each of those settles 0.00112, the least of
    anything here. A model alone on a named origin settles 0.087366, seventy
    times more. Declaring nothing does not keep a thing independent; it puts it
    in the largest undifferentiated pile, where checking any one of them
    establishes almost nothing about the rest.
    """
    by = g["byOrigin"]
    unnamed = by["an origin nobody named"]
    assert unnamed["n"] == 12
    assert abs(unnamed["settles"] - 0.00112) < 1e-5

    singles = [v["settles"] for v in by.values() if v["n"] == 1]
    assert singles and all(abs(s - 0.087366) < 1e-5 for s in singles)
    assert unnamed["settles"] < min(singles) / 50


def test_four_qwen_derivatives_share_one_base(g):
    """Real lineage, and the shape this repository keeps meeting: four separately
    published models, one thing underneath them."""
    by = g["byOrigin"]
    assert by["Qwen/Qwen3.6-27B"]["n"] == 4
    assert abs(by["Qwen/Qwen3.6-27B"]["settles"] - 0.008737) < 1e-5


def test_the_bearings_conserve_and_match_the_python_engine(g):
    st = g["structure"]
    assert st["conserved"] is True
    assert abs(st["totalBearing"] - st["expected"]) < 1e-9
    assert st["expected"] == 34

    lib = json.loads(subprocess.run(
        ["node", "-e",
         "globalThis.LMD=require('../smi/lmd.js');"
         "globalThis.PLEXUS=require('./engines.js');"
         "const P=require('./press.js');"
         "const f=JSON.parse(require('fs').readFileSync("
         "'../hf-cohort/data/hf_cohort_frozen.json','utf8'));"
         "const g=P.graph(f.models.map(m=>({kind:'source',name:m.id,"
         "origin:m.base_model||null})));"
         "process.stdout.write(JSON.stringify({parts:g.parts,links:g.links}))"],
        cwd=HERE, capture_output=True, text=True, timeout=120).stdout)
    assert len(set(lib["parts"])) == len(lib["parts"]), "duplicate part names are back"
    links = [(a, b, w) for a, b, w in lib["links"]]
    py = bearings(Structure(lib["parts"], links))
    assert abs(py["total"] - st["totalBearing"]) < 1e-9


def test_this_is_metadata_and_not_the_card_text_test(g):
    """NULL-G1. eval_results and arxiv are booleans on a hub listing: they say
    whether a field is populated, not whether an evaluation was sound. The
    card-text questions H1 to H7 remain unrun and their pre-registration stays
    locked."""
    src = open(os.path.join(HERE, "HF_NULL.md"), encoding="utf-8").read()
    assert "could not be run" in src
    assert g["provenance"]["fetched_at"] == "2026-07-22"
