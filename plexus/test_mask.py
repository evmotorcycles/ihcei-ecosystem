#!/usr/bin/env python3
"""Label-blind masking: Stage 1, the part that needs no data.

    python3 -m pytest -q plexus/test_mask.py

Locked before this file was written:
    mask_preregistration.md
    sha256 bf95bc4411cb9651f375e3fd500d3b9380622fda1a4b016bed62b2c24987b2c0
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG = "bf95bc4411cb9651f375e3fd500d3b9380622fda1a4b016bed62b2c24987b2c0"

SPEC = {
    "id": "synthetic-cost-plus-01", "serial": 1,
    "parts": ["Murabaha cost price", "Profit Rate", "Deferred Instalment",
              "Total Repayable", "Late Penalty"],
    "links": [["Murabaha cost price", "Total Repayable", 1.0],
              ["Profit Rate", "Total Repayable", 1.0],
              ["Total Repayable", "Deferred Instalment", 1.0],
              ["Late Penalty", "Total Repayable", 1.0]],
    "sources": ["Murabaha cost price", "Profit Rate"],
    "conclusion": "Total Repayable",
    "provenance": {"kind": "synthetic",
                   "where": "written by hand to exercise the masker; not a real contract"},
}
TERMS = ["Murabaha", "Profit Rate", "Interest", "Late Penalty", "Deferred"]


def _node(expr, payload):
    out = subprocess.run(
        ["node", "-e",
         "globalThis.LMD=require('../smi/lmd.js');"
         "globalThis.PLEXUS=require('./engines.js');"
         "const M=require('./mask.js');"
         "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{"
         "const a=JSON.parse(s);"
         f"process.stdout.write(JSON.stringify({expr}))" "})"],
        cwd=HERE, input=json.dumps(payload), capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@pytest.fixture(scope="module")
def masked():
    return _node("M.mask(a.spec,a.terms)", {"spec": SPEC, "terms": TERMS})


@pytest.fixture(scope="module")
def check():
    return _node("M.unchanged(a.spec,a.terms)", {"spec": SPEC, "terms": TERMS})


def test_the_predictions_were_locked_first():
    got = hashlib.sha256(open(os.path.join(HERE, "mask_preregistration.md"),
                              "rb").read()).hexdigest()
    assert got == PREREG


def test_nothing_named_survives_the_mask(masked):
    """K1. Every part becomes a neutral token and the id goes too -- an id like
    'murabaha-07' is a label wearing a different hat."""
    assert masked["ok"] is True
    assert masked["parts"] == ["part 1", "part 2", "part 3", "part 4", "part 5"]
    assert masked["id"] == "contract 1"
    blob = json.dumps({k: masked[k] for k in
                       ("id", "parts", "links", "sources", "conclusion")}).lower()
    for t in TERMS:
        assert t.lower() not in blob, f"the mask leaks {t!r}"


def test_the_key_is_kept_apart_from_the_masked_artefact(masked):
    """The map back exists -- a study that cannot unmask afterwards cannot
    report anything -- but it is a separate field, to be held by whoever runs
    the study and not handed to the coder."""
    assert masked["key"]["part 1"] == "Murabaha cost price"
    assert set(masked["key"].values()) == set(SPEC["parts"])


def test_masking_changes_no_measurement_to_tolerance(check):
    """K2, K4."""
    assert check["leaked"] == []
    assert check["sameToTolerance"] is True
    assert check["worstDifference"] < 1e-12
    assert check["structureUnchanged"] is True


def test_masking_is_not_bit_identical_and_that_is_the_finding(check):
    """K3, and it was worth running to find out.

    The engine sorts node names internally, so renaming changes the ORDER of
    the floating-point operations in the eigendecomposition. The answers differ
    at 5.55e-16. The labels do enter the computation -- not as information, but
    as sort keys.

    A study validating its masker with exact equality would fail here
    spuriously, and might then "fix" it by weakening the mask. The property to
    assert is agreement to tolerance.
    """
    assert check["bitIdentical"] is False
    assert 0 < check["worstDifference"] < 1e-14
    assert abs(check["before"]["deepest"] - 0.5) < 1e-9
    assert abs(check["after"]["deepest"] - 0.5) < 1e-9


def test_a_spec_carrying_its_own_classification_is_refused():
    """K5. A classification arriving with the file is the coder reading the
    answer off it. It is filled in afterwards, by somebody who cannot see the key."""
    spec = dict(SPEC, classification={"deltaU": 0})
    why = _node("M.problems(a.spec)", {"spec": spec, "terms": TERMS})
    assert any("must not arrive carrying its own classification" in w for w in why)


def test_a_spec_that_will_not_say_whether_it_is_real_is_refused():
    """K6. A made-up contract and a real one must never be stored the same way.
    The same rule the Shapes commons already applies to provenance."""
    spec = dict(SPEC, provenance={"kind": "plausible", "where": "somewhere"})
    why = _node("M.problems(a.spec)", {"spec": spec, "terms": TERMS})
    assert any("'real' or 'synthetic'" in w for w in why)

    spec2 = dict(SPEC, provenance={"kind": "real", "where": "   "})
    why2 = _node("M.problems(a.spec)", {"spec": spec2, "terms": TERMS})
    assert any("where this contract text came from" in w for w in why2)


def test_the_worked_spec_is_labelled_synthetic_and_no_result_rests_on_it():
    """There are no contracts. The one in this file exists to exercise the code
    and is marked synthetic, so that nothing downstream can mistake it for
    evidence about any instrument."""
    assert SPEC["provenance"]["kind"] == "synthetic"
    assert "not a real contract" in SPEC["provenance"]["where"]


# ------------------------------------------------------------ the answer ----
def test_the_missing_data_is_written_down_rather_than_worked_around():
    src = open(os.path.join(HERE, "NO_DATA.md"), encoding="utf-8").read()
    assert "there are none" in src
    assert "np.random.seed(42)" in src, "the synthetic generator must be named"
    assert "p = 0.735" in src, "the retired floor must be cited, not alluded to"
    assert "can only pass" in src


def test_the_gates_were_rewritten_so_each_can_lose():
    """A gate phrased "definitively proving" is not a gate. Each of F1 to F4 now
    has a stated losing side, including F4, which was written as a formality and
    is the sharpest of the four."""
    src = re.sub(r"\s+", " ", open(os.path.join(HERE, "mask_preregistration.md"),
                                   encoding="utf-8").read())
    assert "The hypothesis dies if the structural class does not beat" in src
    assert "The threshold is struck." in src
    assert "F4 failing is informative" in src
    assert "p = 0.735" in src
