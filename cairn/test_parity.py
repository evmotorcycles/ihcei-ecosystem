#!/usr/bin/env python3
"""Parity guard: the browser engine must agree with the audited Python engine.

    python3 -m pytest -q cairn/test_parity.py

The plain-language browser app ships a JS port of ei_llm.py so it can run with no
server and no network. A port is a liability unless it is checked: if the two
drift, the audited behaviour and the shipped behaviour stop being the same thing,
and every claim made about the Python engine silently stops applying to what
users actually touch. This test fails on any divergence.
"""
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
import sys  # noqa: E402
sys.path.insert(0, HERE)
from ei_llm import EVIDENCE, IMMOBILE, assay  # noqa: E402

CASES = json.load(open(os.path.join(HERE, "parity_cases.json")))


@pytest.fixture(scope="module")
def js():
    try:
        out = subprocess.run(["node", os.path.join(HERE, "parity_dump.mjs")],
                             capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_case_list_is_covered(js):
    assert len(js) == len(CASES) >= 20


@pytest.mark.parametrize("i", range(len(CASES)))
def test_js_matches_python(js, i):
    text = CASES[i]
    p = assay(text, "slate")
    j = js[i]
    label = repr(text[:60])
    assert j["verdict"] == p["verdict"], f"verdict differs for {label}"
    assert j["claim_type"] == p["claim_type"], f"claim type differs for {label}"
    assert j["confidence"] == p["confidence"], f"confidence differs for {label}"
    assert j["band"] == p["band"], f"band differs for {label}"
    assert j["evidence_hits"] == p["evidence_hits"], f"evidence count differs for {label}"
    assert j["domain_flags"] == p["domain_flags"], f"domain flags differ for {label}"
    assert j["ambiguous"] == p["ambiguity"]["ambiguous"], f"ambiguity differs for {label}"
    assert j["implausible"] == bool(p["implausible"]), f"plausibility differs for {label}"
    assert j["next_steps"] == p["next_steps"], f"next steps differ for {label}"


def test_shared_constants_did_not_drift(js):
    src = open(os.path.join(HERE, "ei_engine.js")).read()
    for noun in IMMOBILE:
        assert f'"{noun}"' in src, f"lexicon noun {noun!r} missing from the JS port"
    assert src.count("EVIDENCE = [") == 1
    assert len(EVIDENCE) == 5


def test_js_port_restates_the_limits():
    src = open(os.path.join(HERE, "ei_engine.js")).read()
    assert "does NOT understand language" in src, (
        "the port must carry the same disclaimer as the Python engine, so nobody "
        "reads a re-implementation as an upgrade")
    assert "hand-written list" in src
