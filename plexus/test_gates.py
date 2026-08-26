#!/usr/bin/env python3
"""Do a pre-registration's gates cover every outcome?

    python3 -m pytest -q plexus/test_gates.py

A locked file removes judgement after the data arrives only if its gates
partition the whole outcome space. A gap between them is where a decision gets
made afterwards, wearing the locked file's authority.
"""
from __future__ import annotations

import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def _cov(spec):
    out = subprocess.run(
        ["node", "-e",
         "const G=require('./gates.js');"
         "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>"
         "process.stdout.write(JSON.stringify(G.coverage(JSON.parse(s)))))"],
        cwd=HERE, input=json.dumps(spec), capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_real_defect_this_was_built_from():
    """H2 claimed >= 20%. Its gate failed it at < 10%. A measured 15% got no
    verdict at all -- and 15% is where a real result is most likely to land."""
    r = _cov({"id": "H2", "supportsIf": ">= 0.20", "failsIf": "< 0.10"})
    assert r["partitions"] is False
    assert len(r["gaps"]) == 1
    assert abs(r["gaps"][0]["from"] - 0.10) < 1e-6
    assert 0.199 < r["gaps"][0]["to"] < 0.200
    assert abs(r["uncoveredShare"] - 0.09995) < 1e-4
    assert "no verdict" in r["says"]


def test_the_repair_partitions_cleanly():
    """The fix is to make the failure condition the complement of the claim."""
    r = _cov({"id": "H2 repaired", "supportsIf": ">= 0.20", "failsIf": "< 0.20"})
    assert r["partitions"] is True
    assert r["gaps"] == [] and r["uncoveredWidth"] == 0
    assert r["says"] == "Every outcome has a verdict."


def test_overlapping_conditions_are_caught_as_a_contradiction():
    """A gate that both supports and fails the same outcome is worse than a
    gap: it licenses either verdict from one number."""
    r = _cov({"id": "overlap", "supportsIf": ">= 0.10", "failsIf": "< 0.20"})
    assert r["contradicts"] is True
    assert r["partitions"] is False
    assert "contradicts the hypothesis" in r["says"]


def test_a_condition_that_cannot_be_read_is_refused():
    r = _cov({"id": "bad", "supportsIf": "quite high", "failsIf": "< 0.10"})
    assert r["ok"] is False
    assert any("'>= 0.20'" in w for w in r["why"])


def test_the_checker_declares_what_it_cannot_do():
    """It checks numeric coverage. It cannot check whether the gate measures the
    thing the hypothesis is about -- a gate can partition perfectly and still be
    pointed at the wrong quantity. That is exactly defect 2 in the protocol, and
    no interval arithmetic would have found it."""
    # Strip the leading `*` of each comment line BEFORE collapsing whitespace.
    # Collapsing alone leaves "needs a * reader" -- the marker survives and the
    # sentence does not. A test that fails on comment formatting is a test about
    # comment formatting.
    raw = open(os.path.join(HERE, "gates.js"), encoding="utf-8").read()
    src = re.sub(r"\s+", " ", re.sub(r"(?m)^\s*\*", " ", raw))
    assert "It cannot check whether the gate measures the thing" in src
    assert "needs a reader" in src


def test_the_blockers_and_defects_are_written_down():
    flat = re.sub(r"\s+", " ", open(os.path.join(HERE, "AUDIT_PROTOCOL_DEFECTS.md"),
                                    encoding="utf-8").read())
    for fact in ("gh` CLI | **absent**", "403", "scoped to **two**"):
        assert fact.replace("**", "") in flat.replace("**", ""), fact
    assert "Layer 2 contradicts Layer 3" in flat
    assert "Running a test suite **is** executing".replace("**", "") in flat.replace("**", "")
    assert "What is right, and should not be lost in the fixing" in flat
