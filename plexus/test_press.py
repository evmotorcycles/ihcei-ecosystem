#!/usr/bin/env python3
"""The Lens algorithm: press a claim and see what runs out.

    python3 -m pytest -q plexus/test_press.py

Predictions were written down and the file hashed before any of this ran:

    sha256  a72e5d6950ae55db446479f40e472b288008068a7f0758ad6b3789c2bdfb48eb

ONE OF THEM MISSED, and it is recorded below rather than quietly adjusted --
see test_the_prediction_that_missed. The pre-registration is not edited; the
hash still checks; the miss is reported.

The test that matters most here is that a completely fabricated claim and a true
one of the same shape return IDENTICAL numbers. If they ever differ, the engine
has begun guessing about the world and should be stopped rather than improved.
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

from fathom.fathom import Claim, sound  # noqa: E402
from spar.spar import Structure, bearings, single_points  # noqa: E402

PREREG_SHA256 = "a72e5d6950ae55db446479f40e472b288008068a7f0758ad6b3789c2bdfb48eb"


@pytest.fixture(scope="module")
def p():
    script = os.path.join(HERE, "press_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_predictions_were_locked_before_anything_ran():
    path = os.path.join(HERE, "press_preregistration.md")
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    assert got == PREREG_SHA256, (
        f"the pre-registration has been edited since it was locked\n"
        f"  locked {PREREG_SHA256}\n  now    {got}"
    )


# ------------------------------------------------------------- the 1/m^2 law --
@pytest.mark.parametrize("m,want", [(1, 1.0), (2, 0.25), (3, 1 / 9),
                                    (4, 0.0625), (5, 0.04)])
def test_marks_on_one_origin_each_read_one_over_m_squared(p, m, want):
    """L3. The finding, and it is exact at every m.

    Five handles do not give you five ways to check. They give you one way to
    check, dressed as five, and each reads 0.040 because the graph is saying so.
    The reassuring number is the warning.
    """
    row = p["oneOrigin"][str(m)]
    assert len(row["settles"]) == m
    for s in row["settles"]:
        assert abs(s - want) < 1e-9, f"m={m}: {s} not {want}"


def test_the_check_graph_is_a_tree_and_conserves(p):
    """L1. Every link a sole route, total = parts - pieces."""
    for m in range(1, 6):
        s = p["oneOrigin"][str(m)]["structure"]
        assert s["parts"] == m + 2
        assert len(s["bearings"]) == m + 1
        for b in s["bearings"]:
            assert abs(b - 1.0) < 1e-9
        assert abs(s["totalBearing"] - (m + 1)) < 1e-9
        assert s["expected"] == m + 1 and s["pieces"] == 1 and s["conserved"] is True


def test_the_origin_is_the_thing_to_check_first(p):
    """L2. Computed by removal, never by a rank somebody assigned."""
    for m in range(1, 6):
        row = p["oneOrigin"][str(m)]
        assert row["singlePoints"] == ["the 2026 report"]
        assert row["firstCheck"]["origin"] == "the 2026 report"
        assert "Open the 2026 report" in row["firstCheck"]["instruction"]


def test_two_origins_make_every_check_matter_more(p):
    """L4, the half that held. Splitting four marks across two origins doubles
    what each single check settles, from 0.0625 to 0.125."""
    t = p["twoOrigins"]
    for s in t["settles"]:
        assert abs(s - 0.125) < 1e-9
    assert t["sharedOrigin"] is False
    assert set(t["origins"]) == {"the 2026 report", "the 2019 census"}


def test_the_prediction_that_missed(p):
    """L4, the half that did not hold -- reported, not quietly adjusted.

    Predicted: with two origins there would be two parts whose removal breaks
    the graph. There are THREE. With two origins hanging off it, the claim node
    is itself a cut vertex: remove it and the two halves cannot reach each
    other. The arithmetic is right and the hand calculation was wrong.

    It was not merely a wrong number. It was a defect: firstCheck took the first
    single point, so on any claim with two origins the tool told the reader to
    go and open "The claim stands". The claim node is now excluded from the
    candidates, and this test pins both the correction and the miss.
    """
    t = p["twoOrigins"]
    assert len(t["singlePoints"]) == 3, "the miss: predicted 2, measured 3"
    assert "The claim stands" in t["singlePoints"]
    assert set(t["singlePoints"]) == {"The claim stands", "the 2026 report",
                                      "the 2019 census"}


def test_nothing_that_is_not_a_check_is_ever_offered_as_one(p):
    """The correction above, asserted over every case in the dump."""
    for key in ("fabricated", "trueShaped", "unnamed", "pressedFabricated"):
        r = p[key]
        assert "The claim stands" not in r["cutOrigins"]
        if r["firstCheck"]:
            assert r["firstCheck"]["origin"] != "The claim stands"


# ------------------------------------------------------------------ THESIS ----
def test_a_fabricated_claim_reads_exactly_like_a_true_one(p):
    """L6. THESIS. If this ever fails, stop the engine rather than improve it.

    "A 2026 flow-rate audit proved 90% of meters overcharge by 12%" is invented.
    "The published tariff schedule gives 5032 per unit for domestic connections"
    is checkable and ordinary. They share no word. They must return identical
    numbers, because the arithmetic does not know anything about the world and
    the moment it appears to, it has become an oracle.

    A high reading means the claim has staked something and can be settled fast.
    It says nothing whatever about which way the settlement goes.
    """
    a, b = p["identical"]["settles"]
    assert p["identical"]["sharedWords"] == [], "they share an origin, so this proves nothing"
    assert len(a) == len(b) == 5
    for x, y in zip(a, b):
        assert abs(x - y) < 1e-12, "the engine has started guessing about the world"
    for x, y in zip(*p["identical"]["bearings"]):
        assert abs(x - y) < 1e-12

    for s in a:
        assert abs(s - 0.04) < 1e-9, "five marks on one origin read 1/25 each"


def test_fog_returns_no_number_at_all(p):
    """L5. Assigning a value to fog is the mask failure, committed by the tool
    built to name it.

    "Industry experts generally agree that our meters are highly accurate" has
    truthfulness -- it is fluent, professional and persuasive. Press it and
    nothing runs out. There is no number to give and the words say why.
    """
    for key in ("nothing", "onlyEmptyKinds", "pressedFog"):
        r = p[key]
        assert r["checkable"] is False, key
        assert r["checks"] == [] and r["firstCheck"] is None
        assert r["structure"] is None, "a number was produced for fog"
        assert "Nothing runs out" in r["says"]
        assert "not the same as false" in r["meaning"]


def test_an_origin_nobody_named_is_still_the_thing_to_check_first(p):
    """A figure with no source behind it is just a number. The unnamed origin is
    a real node and a real cut point, and the instruction changes to match."""
    u = p["unnamed"]
    assert u["checkable"] is True
    assert u["unnamedOrigin"] is True
    assert u["firstCheck"]["origin"] == "an origin nobody named"
    assert "Ask where this came from" in u["firstCheck"]["instruction"]
    for s in [c["settles"] for c in u["checks"]]:
        assert abs(s - 0.25) < 1e-9, "two marks on one origin read 1/4"


# ------------------------------------------------------------------ parity ----
def test_the_browser_engine_agrees_with_the_python(p):
    """L8. The port gets no private arithmetic here either."""
    lib = json.loads(subprocess.run(
        ["node", "-e",
         "globalThis.LMD=require('../smi/lmd.js');"
         "globalThis.PLEXUS=require('./engines.js');"
         "const P=require('./press.js');"
         "const out={};"
         "for(let m=1;m<=5;m++){const ms=P.fromKinds("
         "['source','figures','method','time','scope'].slice(0,m),'the 2026 report');"
         "const g=P.graph(ms);out[m]={parts:g.parts,links:g.links,marks:g.marks};}"
         "process.stdout.write(JSON.stringify(out))"],
        cwd=HERE, capture_output=True, text=True, timeout=120).stdout)

    for m in range(1, 6):
        g = lib[str(m)]
        links = [(a, b, w) for a, b, w in g["links"]]
        py = bearings(Structure(g["parts"], links))
        got = p["oneOrigin"][str(m)]["structure"]
        assert abs(py["total"] - got["totalBearing"]) < 1e-9, m

        pysp = sorted(x["part"] for x in single_points(Structure(g["parts"], links)))
        assert pysp == sorted(p["oneOrigin"][str(m)]["singlePoints"]), m

        pyf = sound(Claim("The claim stands", g["marks"], links))
        want = p["oneOrigin"][str(m)]["settles"][0]
        assert abs(pyf["deepest_dependence"] - want) < 1e-9, m


# ------------------------------------------------------- the lexical finder ---
def test_the_marks_come_from_the_one_implementation_that_already_exists(p):
    """cairn/ei_engine.js, not a private copy that drifts. Its regexes are the
    single definition of what a mark is, in this repository."""
    d = p["detected"]
    assert d["fog"]["hits"] == [], "fog must produce no marks"
    assert set(d["fabricated"]["hits"]) == {"figures", "method", "time", "scope"}
    assert d["plain"]["hits"] == ["time"]


def test_the_finder_misses_things_and_that_is_registered_not_hidden(p):
    """NULL-L2. It matches words; it does not read.

    The fabricated claim names a body and cites an audit, and the source signal
    still reads false -- neither "authority" nor "audit" is in the list of words
    the source pattern looks for. That is a real miss, and the honest response is
    to let a person add the mark rather than to keep widening a regex until it
    fires on everything.
    """
    d = p["detected"]["fabricated"]
    assert "source" not in d["hits"], \
        "if the source pattern now fires here, this note needs rewriting"
    assert d["handles"]["source_named"] is False
    assert d["handles"]["figures"] and d["handles"]["time"], \
        "the spans it did find must come back so a person can paste them"


def test_every_instruction_is_something_that_could_come_back_negative(p):
    """The property that makes a mark a check at all. An instruction that cannot
    fail is a reassurance with a verb in it."""
    for kind, text in p["instructions"].items():
        assert text.strip()
        first = text.split()[0].lower().rstrip(".,")
        assert first in ("open", "find", "ask", "check", "go", "confirm"), \
            f"{kind}: {text!r} does not start with something a person does"
    assert set(p["instructions"]) == {"source", "figures", "method", "time", "scope"}


def test_the_shared_origin_is_named_in_words_not_only_in_a_number(p):
    """0.040 means nothing to a person holding a letter. The sentence does."""
    s = p["fabricated"]["says"]
    assert "one way in, counted 5 times" in s
    assert p["fabricated"]["sharedOrigin"] is True
    assert p["twoOrigins"]["sharedOrigin"] is False


# ---------------------------------------------------------------- the page ----
def test_the_shipped_press_page_obeys_the_same_rules():
    import re
    page = os.path.join(HERE, "press.html")
    assert os.path.exists(page), "press.html was never rendered"
    raw = open(page, "rb").read()
    src = raw.decode("utf-8")
    assert b"\x00" not in raw
    assert not re.search(r"<script[^>]+\bsrc\s*=", src)
    assert "{{" not in src
    assert "min-height:44px" in src and "min-height:48px" in src
    assert 'href="index.html"' in src
    assert "Nothing leaves this device" in src


def _flat(s):
    """Collapse runs of whitespace: HTML collapses them when it renders, so a
    sentence wrapped over three source lines is one sentence on the screen.
    Comparing raw bytes would make this a test about line lengths."""
    import re
    return re.sub(r"\s+", " ", s)


def test_the_page_says_that_a_perfect_lie_scores_the_same_as_the_truth():
    """L7. The single most important sentence on the page.

    A reader who takes a high reading for "this is true" has been handed a mask
    by the tool built to name them.
    """
    src = _flat(open(os.path.join(HERE, "press.html"), encoding="utf-8").read())
    assert "A claim that is completely made up reads exactly like a true one" in src
    assert "This cannot be shown false" in src


def test_the_page_carries_no_terminology_from_the_source_it_borrowed_from():
    """The logic was taken; the vocabulary was not, deliberately and by
    instruction. A measuring page is not the place for it."""
    src = open(os.path.join(HERE, "press.html"), encoding="utf-8").read().lower()
    for word in ("quran", "qur'an", "surah", "surat", "ayah", "ayat", "allah",
                 "tafseer", "arabic", "islam"):
        assert word not in src, f"press.html carries terminology it should not: {word}"


def test_the_service_worker_caches_the_press_page():
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    assert "./press.html" in sw
