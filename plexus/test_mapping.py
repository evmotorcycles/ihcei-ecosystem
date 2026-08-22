#!/usr/bin/env python3
"""Does the five map onto the ten? Measured under three readings.

    python3 -m pytest -q plexus/test_mapping.py

Locked before the graph was built:
    mapping_preregistration.md
    sha256 62c43800c3fbd9ce21f018851bf66bc203770500af1c0cc392c8e5b404a2615c

M1 to M4 and M6 held. HALF OF M5 MISSED and is recorded rather than adjusted.
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

PREREG = "62c43800c3fbd9ce21f018851bf66bc203770500af1c0cc392c8e5b404a2615c"


@pytest.fixture(scope="module")
def m():
    out = subprocess.run(["node", os.path.join(HERE, "mapping_dump.mjs")],
                         capture_output=True, text=True, timeout=180)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def _row(m, name):
    return [r for r in m["rows"] if r["name"] == name][0]


def test_the_prediction_was_locked_before_the_graph_was_built():
    got = hashlib.sha256(open(os.path.join(HERE, "mapping_preregistration.md"),
                              "rb").read()).hexdigest()
    assert got == PREREG


def test_my_own_assignment_came_out_where_i_said_it_would(m):
    """M1, M2, M3. Five covered, five not, and the five uncovered are exactly
    the ones named in advance."""
    r = _row(m, "mine")
    assert r["coveredN"] == 5
    assert r["uncoveredN"] == 5
    assert set(r["uncovered"]) == {"terminology", "roles", "dues",
                                   "policies", "exceptions"}


def test_the_graph_is_in_pieces(m):
    """M4. Elements no signal reaches are not weakly connected -- they are not
    connected at all. Ten separate pieces on my reading."""
    for name in ("mine", "theirs", "third"):
        r = _row(m, name)
        assert r["pieces"] > 1, name
        assert r["conserved"] is True
    assert _row(m, "mine")["pieces"] == 10


def test_the_count_moves_with_whoever_assigns_the_links(m):
    """M5, first half, and the finding.

    Three careful readings of the same two lists give 2, 5 and 6 covered. A
    derivation has one answer. This has as many answers as it has readers, which
    is a stronger statement against it being a derivation than any single count.
    """
    counts = sorted(r["coveredN"] for r in m["rows"])
    assert counts == [2, 5, 6]
    assert m["countsDiffer"] is True


def test_only_one_element_survives_all_three_readings(m):
    """The sharpest number here, and it was not predicted.

    Seven of the ten are claimed by at least one reading. Exactly ONE --
    domains of application -- is claimed by all three. The mapping is almost
    entirely a matter of who is assigning it.
    """
    assert m["coveredAgreedByAll"] == ["domains"]
    assert len(m["coveredClaimedByAny"]) == 7


def test_the_half_of_m5_that_missed(m):
    """M5, second half. Predicted: the covered count would be unstable but the
    UNCOVERED set would be largely stable. It is not.

    Only three of ten -- dues, policies, roles -- are uncovered on every
    reading. The rest move too. The uncovered set is assignment-dependent as
    well, just less wildly than the covered one, and "largely stable" was too
    strong. Recorded rather than softened.
    """
    assert set(m["uncoveredAgreedByAll"]) == {"dues", "policies", "roles"}
    assert len(m["uncoveredAgreedByAll"]) == 3, \
        "the miss: predicted a largely stable uncovered set, measured 3 of 10"


def test_my_count_disagrees_with_the_exchange_and_the_conclusion_holds_anyway(m):
    """M6. The exchange said 2 of 10; on my links it is 5. The count was low.

    The conclusion it was used to support -- that this is the shape of a
    derivation without being one -- survives the correction, and is better
    supported by the instability than by either count.
    """
    assert _row(m, "theirs")["coveredN"] == 2
    assert _row(m, "mine")["coveredN"] == 5
    assert _row(m, "mine")["coveredN"] != _row(m, "theirs")["coveredN"]


def test_the_python_engine_agrees(m):
    signals, ten = m["signals"], m["ten"]
    node = json.loads(subprocess.run(
        ["node", "-e",
         "globalThis.LMD=require('../smi/lmd.js');"
         "globalThis.PLEXUS=require('./engines.js');"
         "const s=require('fs').readFileSync('mapping_dump.mjs','utf8');"
         "process.stdout.write('[]')"],
        cwd=HERE, capture_output=True, text=True, timeout=60).stdout)
    assert node == []
    # re-measure the one assignment written in the pre-registration
    links = [("method", "procedures", 1.0), ("scope", "domains", 1.0),
             ("figures", "rules", 1.0), ("figures", "results", 1.0),
             ("source", "authorities", 1.0)]
    py = bearings(Structure(signals + ten, links))
    got = _row(m, "mine")
    assert abs(py["total"] - got["totalBearing"]) < 1e-9
    assert py["pieces"] == got["pieces"]


def test_the_links_are_declared_as_a_reading_not_a_measurement():
    """NULL-M1. The arithmetic is only as good as the links, and the links are
    opinions with reasons attached. The pre-registration says so and names mine
    before they were used."""
    src = open(os.path.join(HERE, "mapping_preregistration.md"),
               encoding="utf-8").read()
    assert "The links are a judgement" in src
    assert "no more authoritative than theirs" in src
    for pair in ("method | procedures", "scope | domains of application"):
        assert pair in src
