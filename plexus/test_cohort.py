#!/usr/bin/env python3
"""Twenty-two Qwen and DeepSeek projects are two origins, not twenty-two.

    python3 -m pytest -q plexus/test_cohort.py

Locked before the arithmetic ran:
    cohort_preregistration.md
    sha256 68682bef11da2a4d76bb02769c1f64f586952c1c9ac46eab02894a555bf3d7aa

The pre-registered Hugging Face card test is a DIFFERENT question and it could
not be run at all -- see HF_NULL.md. Its pre-registration stays locked and
unedited rather than being rewritten into something this environment can answer.
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

PREREG = "68682bef11da2a4d76bb02769c1f64f586952c1c9ac46eab02894a555bf3d7aa"
HF_PREREG = "ebe1366f4b999992f2b949a54daf806983d5af3b8d62e3549516c18ae65adf87"


@pytest.fixture(scope="module")
def c():
    try:
        out = subprocess.run(["node", os.path.join(HERE, "cohort_dump.mjs")],
                             capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_both_preregistrations_are_locked():
    for name, want in (("cohort_preregistration.md", PREREG),
                       ("hf_preregistration.md", HF_PREREG)):
        got = hashlib.sha256(open(os.path.join(HERE, name), "rb").read()).hexdigest()
        assert got == want, f"{name} has been edited since it was locked"


def test_the_unrunnable_test_is_recorded_as_unrunnable():
    """HF_NULL.md exists and says so plainly.

    The temptation was to rewrite hf_preregistration.md into a question this
    environment can answer. A prediction edited after meeting the data is not a
    prediction, so it stays locked and the block is written down instead.
    """
    src = open(os.path.join(HERE, "HF_NULL.md"), encoding="utf-8").read()
    assert "could not be run" in src
    assert "403" in src and "huggingface.co:443" in src
    assert "was not rewritten" in src
    for h in ("H1", "H7"):
        assert h in src


def test_twenty_two_repositories_are_two_organisations(c):
    """C1, C2. The count I was least sure of, and it held."""
    assert c["repos"] == 22
    assert set(c["origins"]) == {"deepseek-ai", "QwenLM"}
    assert c["orgs"] == {"deepseek-ai": 12, "QwenLM": 10}


def test_both_organisations_are_cut_points(c):
    """C3. Remove one and its repositories cannot reach the rest."""
    assert set(c["cutOrigins"]) == {"deepseek-ai", "QwenLM"}
    assert "The claim stands" not in c["cutOrigins"]


def test_each_repository_settles_far_less_than_a_naive_count_implies(c):
    """C5, C6, and C4 with the miss recorded.

    C4 predicted 0.003498 for a deepseek-ai repository. The measured value is
    0.003499. The exact value is 262/143 arithmetic giving 0.0034987, so the
    prediction was right to five places and wrong in the sixth because it was
    written down truncated rather than rounded. Recorded rather than tidied.
    """
    s = c["settlesByOrg"]
    assert abs(s["QwenLM"]["each"] - 0.004962) < 1e-6, "C5"
    assert abs(s["deepseek-ai"]["each"] - 0.0034987) < 1e-7, \
        "C4 to the exact value; the pre-registered figure was truncated"
    assert s["deepseek-ai"]["each"] != 0.003498, "the sixth-place miss is real"

    for org in s:
        assert s[org]["allSame"] is True
        assert s[org]["each"] < c["naive"], "C6"
    assert abs(c["naive"] - 1 / 22) < 1e-12


def test_the_bearings_conserve_and_match_the_python_engine(c):
    """C7."""
    st = c["structure"]
    assert st["conserved"] is True
    assert abs(st["totalBearing"] - st["expected"]) < 1e-9
    assert st["parts"] == 25 and st["expected"] == 24

    lib = json.loads(subprocess.run(
        ["node", "-e",
         "globalThis.LMD=require('../smi/lmd.js');"
         "globalThis.PLEXUS=require('./engines.js');"
         "const P=require('./press.js');"
         "const f=require('fs').readFileSync("
         "'../ei-dashboards/data/qwen_deepseek_frozen.json','utf8');"
         "const repos=JSON.parse(f).repos;"
         "const g=P.graph(repos.map(r=>({kind:'source',origin:r.org,name:r.full_name})));"
         "process.stdout.write(JSON.stringify({parts:g.parts,links:g.links}))"],
        cwd=HERE, capture_output=True, text=True, timeout=120).stdout)
    links = [(a, b, w) for a, b, w in lib["links"]]
    py = bearings(Structure(lib["parts"], links))
    assert abs(py["total"] - st["totalBearing"]) < 1e-9


def test_nothing_was_fetched_for_this(c):
    """NULL-C3. The frozen file's own provenance governs when it was taken, and
    this run added nothing to it."""
    p = c["provenance"]
    assert p["fetched_at"] == "2026-08-06"
    assert "Frozen for offline reproducibility" in p["note"]


def test_the_readout_does_not_fit_this_use_and_that_is_said_out_loud(c):
    """press.js was built for claims, and its sentence here reads "there are 22
    things here you can go and do" -- true, and beside the point for a cohort.

    Not a defect: it is a tool being pointed at something it was not shaped for,
    and the number it produces is still the right one. The sentence is not, so
    the sentence is not used in the write-up.
    """
    assert c["says"].startswith("There are 22 things here")
    assert c["sharedOrigin"] is False, "two origins, so the shared-origin line is off"
