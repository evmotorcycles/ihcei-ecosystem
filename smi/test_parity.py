#!/usr/bin/env python3
"""The browser engine must agree with the JAX engine.

    python3 -m pytest -q smi/test_parity.py

SMI ships a JavaScript port of the metric so it runs on a phone with no server.
A port nobody checks drifts, and then the thing under test and the thing people
touch stop being the same thing. Both engines are run over the same fourteen
graphs -- rings, paths, stars, a complete graph, weighted mixes, random graphs,
a split ring, a three-piece graph, a dead mesh -- and any disagreement fails.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from smi.lmd import mesh_metric  # noqa: E402

GRAPHS = json.load(open(os.path.join(HERE, "fixtures", "parity_graphs.json"), encoding="utf-8"))
TOL = 1e-9


@pytest.fixture(scope="module")
def js():
    try:
        out = subprocess.run(["node", os.path.join(HERE, "parity_dump.mjs")],
                             capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_fixture_covers_more_than_one_kind_of_graph(js):
    assert len(GRAPHS) == len(js) >= 14
    names = " ".join(g["name"] for g in GRAPHS)
    for kind in ("ring", "path", "star", "complete", "random", "split", "dead"):
        assert kind in names, f"no {kind} graph in the parity set"


@pytest.mark.parametrize("i", range(len(GRAPHS)))
def test_every_distance_agrees(js, i):
    name = GRAPHS[i]["name"]
    D_py, lab_py, dead_py = mesh_metric(np.array(GRAPHS[i]["L"], dtype=float))
    j = js[i]
    assert j["name"] == name
    assert bool(j["dead"]) == bool(dead_py), f"{name}: disagree on whether the mesh is dead"

    D_js = np.array([[np.inf if v is None else v for v in row] for row in j["D"]], dtype=float)
    assert D_js.shape == D_py.shape

    both_inf = ~np.isfinite(D_py) & ~np.isfinite(D_js)
    assert (~np.isfinite(D_py) == ~np.isfinite(D_js)).all(), \
        f"{name}: the two engines disagree about which pairs have no path"
    finite = np.isfinite(D_py) & ~both_inf
    if finite.any():
        worst = float(np.max(np.abs(D_py[finite] - D_js[finite])))
        assert worst < TOL, f"{name}: worst distance disagreement {worst:.3e}"


@pytest.mark.parametrize("i", range(len(GRAPHS)))
def test_the_component_split_agrees(js, i):
    _, lab_py, _ = mesh_metric(np.array(GRAPHS[i]["L"], dtype=float))
    lab_js = js[i]["labels"]
    # labels are arbitrary integers; what must match is the PARTITION
    py = {frozenset(np.nonzero(lab_py == v)[0].tolist()) for v in set(lab_py.tolist())}
    jsp = {frozenset(k for k, v in enumerate(lab_js) if v == g) for g in set(lab_js)}
    assert py == jsp, f"{GRAPHS[i]['name']}: different pieces"


def test_the_split_ring_really_does_have_an_unreachable_pair(js):
    """Otherwise the infinity comparison above would be vacuous."""
    k = next(i for i, g in enumerate(GRAPHS) if g["name"] == "split ring N=8")
    D = js[k]["D"]
    assert any(v is None for row in D for v in row), "no infinite entries to compare"


def test_the_js_engine_ships_no_second_set_of_rules():
    """The port may reimplement the ARITHMETIC. It must not invent policy."""
    src = open(os.path.join(HERE, "lmd.js"), encoding="utf-8").read()
    assert "DEAD_MESH_EPS = 1e-12" in src, "the dead-mesh threshold must match the Python"
    for banned in ("fetch(", "XMLHttpRequest", "import(", "require('http"):
        assert banned not in src, f"the browser engine reaches out: {banned}"
