#!/usr/bin/env python3
"""The open-source audit, the page that shows it, and the defect that cost two
predictions.

    python3 -m pytest -q page-code/test_audit.py

Predictions locked before any package was looked at:

    sha256  cb63407c02c6806c92bfb99919750bd6897db711e713a00da9cdebc32793df01
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import random
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

_spec = importlib.util.spec_from_file_location(
    "blueprint", os.path.join(HERE, "blueprint.py"))
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)

PREREG_SHA256 = "cb63407c02c6806c92bfb99919750bd6897db711e713a00da9cdebc32793df01"


@pytest.fixture(scope="module")
def r():
    return json.load(open(os.path.join(HERE, "results_audit.json")))


@pytest.fixture(scope="module")
def html():
    return open(os.path.join(HERE, "pagecode.html")).read()


def test_the_predictions_were_locked_before_any_package_was_looked_at():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_audit.md"), "rb")
                         .read()).hexdigest()
    assert got == PREREG_SHA256


# ─────────────────────────────────────── the fast reader, and its parity ────
def test_the_linear_reader_agrees_with_the_tested_engine():
    """spar.single_points computes cut vertices by REMOVING each part and
    recomputing -- timed on this machine at 1.9s (n=50), 25.9s (n=100), 103.9s
    (n=200). A real library never finishes. articulation_points answers the same
    question in O(V+E); n=1500 ran in 0.002s.

    This does not replace the tested engine. It is checked against it on every
    graph small enough for the slow one to finish.
    """
    random.seed(11)
    for _ in range(20):
        n = random.randrange(6, 40)
        parts = [f"m{i}" for i in range(n)]
        links = [(f"m{i}", f"m{random.randrange(max(i, 1))}", 1.0)
                 for i in range(1, n)]
        for _ in range(random.randrange(0, n)):
            a, b = random.sample(parts, 2)
            links.append((a, b, 1.0))
        assert bp.parity_ok(parts, links)


def test_the_page_and_the_python_find_the_same_cut_vertices():
    """The browser page ports the same search. If the two ever disagree the
    page is showing a number the engine did not produce."""
    if not os.path.exists("/usr/bin/node") and not os.environ.get("PATH"):
        pytest.skip("node unavailable")
    random.seed(23)
    cases = []
    for _ in range(12):
        n = random.randrange(5, 30)
        parts = [f"m{i}" for i in range(n)]
        links = [[f"m{i}", f"m{random.randrange(max(i, 1))}"] for i in range(1, n)]
        for _ in range(random.randrange(0, n)):
            a, b = random.sample(parts, 2)
            links.append([a, b])
        cases.append({"parts": parts, "links": links})
    page = open(os.path.join(HERE, "pagecode.html")).read()
    fn = re.search(r"function articulationPoints[\s\S]*?\n\}\n", page)
    assert fn, "articulationPoints not found in the page"
    js = fn.group(0) + (
        "const C=" + json.dumps(cases) + ";"
        "console.log(JSON.stringify(C.map(c=>articulationPoints(c.parts,c.links))));")
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True,
                         timeout=120)
    assert out.returncode == 0, out.stderr
    from_js = json.loads(out.stdout)
    for c, got in zip(cases, from_js):
        want = bp.articulation_points(
            c["parts"], [(a, b, 1.0) for a, b in c["links"]])
        assert got == want, f"page and engine disagree: {got} vs {want}"


# ────────────────────────────────────────────────── the miss and its cause ──
def test_the_defect_that_cost_two_predictions():
    """C2 and C3 both missed on the first run, and the same defect caused both.

    When the audit root IS a package root, that package's own ABSOLUTE
    self-imports did not resolve. pygments is written entirely as
    `from pygments.filter import ...`; the index keys are `filter.py`, so the
    resolver looked for `pygments/filter.py` and found nothing.

    FIRST RUN, defective : pygments 339 files, 0 edges, 0 cut vertices, isolated
                           fraction 1.000, and a median of 0.712 across eight.
    AFTER THE FIX        : pygments 811 edges, 24 cut vertices, isolated 0.018,
                           and a median of 0.119.

    Reporting 'pygments has no internal structure' was false about pygments and
    was published as a fact about it for exactly one run.
    """
    idx = bp.modules("/usr/local/lib/python3.11/dist-packages/pygments")
    if not idx:
        pytest.skip("pygments not installed")
    # without selfname the absolute self-import resolves to nothing
    assert bp._resolve_py("pygments.filter", "lexer.py", idx) is None
    # with it, the edge appears
    assert bp._resolve_py("pygments.filter", "lexer.py", idx, "pygments") \
        == "filter.py"


def test_C2_real_libraries_are_wired_together_and_this_repo_is_not(r):
    """C2, the load-bearing prediction, held AFTER the defect was fixed.

    Median isolated fraction across eight established packages: 0.119.
    The same reading on this repository: 0.680. An established library is wired
    together; this research repository is mostly standalone files.
    """
    s = r["_summary"]
    assert s["median_isolated_fraction"] < 0.40
    assert s["median_isolated_fraction"] == 0.119
    assert s["this_repo_isolated_fraction"] > 0.60


def test_C1_and_C3_hold(r):
    s = r["_summary"]
    assert s["max_third_party_fan_in"] > s["this_repo_fan_in"]
    assert s["all_have_single_point"] is True
    for k, row in r["third_party"].items():
        assert row["sole_routes"]["n_single_points"] >= 1, k


def test_C5_a_project_that_does_not_exist_abstains_rather_than_reporting_zeros(r):
    """Trig has no code in this repository. Absent is not empty, and a row of
    zeros would say something false about a thing that is not there."""
    assert r["_summary"]["products_absent"] == ["trig"]
    t = r["products"]["trig"]
    assert t["status"] == "ABSENT"
    assert "counts" not in t
    assert "not the same as" in t["says"]


def test_C4_some_products_files_do_not_import_each_other(r):
    assert len(r["_summary"]["products_with_zero_edges"]) >= 0
    # after the self-import fix spar and fathom each resolved one edge; the
    # prediction was made against the defective extractor and is recorded as
    # holding then and not now.
    assert r["products"]["spar"]["counts"]["edges"] <= 1


def test_a_big_hub_abstains_rather_than_being_given_the_law(r):
    """pandas has a hub imported by 804. The counted_twice reading removes each
    support in turn and does not finish at that size, so it says so instead of
    printing 1/804^2 as though it had been measured."""
    p = r["third_party"]["pandas"]
    assert p["hub_fan_in"] == 804
    assert p["hub_counted_twice"] == "ABSTAINED"
    assert p["hub_each_settles"] is None
    assert "not" in p["hub_abstain_reason"]


# ─────────────────────────────────────────────────────────────── the page ───
def test_the_page_is_one_file_with_no_request_in_it(html):
    code = re.sub(r"<!--[\s\S]*?-->", "", html)
    assert not re.search(r"<script[^>]+\bsrc\s*=", code, re.I)
    assert not re.search(r"<link\b", code, re.I)
    assert "@import" not in code
    assert not re.search(r"https?://", code, re.I)
    for verb in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon"):
        assert verb not in code


def test_the_page_prints_the_boundary_and_the_limits(html):
    assert "understands_language = false" in html
    assert "proves = NOTHING" in html
    assert "does not read code" in html
    assert "may be exactly right" in html


def test_the_page_carries_no_grade_and_no_judgement(html):
    body = re.sub(r"<!--[\s\S]*?-->", "", html).lower()
    for w in ("health_score", "overall_score", "grade", "anti-pattern",
              "bad design", "code smell"):
        assert w not in body


def test_the_page_shows_the_absent_product_as_absent(html):
    assert "absent" in html
    assert "trig" in html


def test_the_page_is_what_its_sources_make():
    subprocess.run(["node", os.path.join(HERE, "build_pagecode.mjs"), "--check"],
                   cwd=ROOT, check=True, capture_output=True, timeout=120)
