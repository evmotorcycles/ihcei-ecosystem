#!/usr/bin/env python3
"""The interceptor: what an assistant told you, before you act on it.

    python3 -m pytest -q plexus/test_intercept.py

The commissioned brief asked for a page that gives people "safety and security".
It does not and it must never say it does. Every test below that matters is
about the difference between forcing a check and certifying an outcome.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

SKIN = ("Mix 30% glycolic acid with 10ml distilled water and apply to the skin "
        "for 15 minutes. First cleanse, then apply, then rinse. This is a "
        "standard 2024 dermatological method.")
FOG = ("Experts generally agree this approach works well for most people and is "
       "considered best practice in the industry.")


def _run(text):
    out = subprocess.run(
        ["node", "-e",
         "globalThis.LMD=require('../smi/lmd.js');"
         "globalThis.PLEXUS=require('./engines.js');"
         "globalThis.EI=require('../cairn/ei_engine.js');"
         "globalThis.PRESS=require('./press.js');"
         "const I=require('./intercept.js');"
         "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>"
         "process.stdout.write(JSON.stringify(I.intercept(s,{}))))"],
        cwd=HERE, input=text, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@pytest.fixture(scope="module")
def skin():
    return _run(SKIN)


@pytest.fixture(scope="module")
def fog():
    return _run(FOG)


def test_a_risky_subject_is_flagged_and_sent_to_a_person(skin):
    """The case the brief was written around.

    A concentration, a contact time and skin. The page must not evaluate it --
    it knows no chemistry and no dermatology -- and must say who does.
    """
    domains = [f["domain"] for f in skin["flags"]]
    assert "health" in domains and "chemicals" in domains
    asks = " ".join(f["ask"] for f in skin["flags"])
    assert "pharmacist" in asks or "doctor" in asks
    assert "for a living" in asks


def test_the_step_that_could_hurt_you_is_the_one_with_no_stated_consequence(skin):
    """The finding on the worked example, and the reason the ten are counted.

    The plan settles four of the ten. What it never mentions includes what
    happens if a step goes wrong -- which is exactly the failure gate that would
    have to exist before any of this were treated as settled.
    """
    missing = [m["key"] for m in skin["ten"]["missing"]]
    assert "consequences" in missing
    assert "boundaries" in missing
    assert skin["ten"]["settled"] == 4
    assert len(skin["ten"]["rows"]) == 10


def test_the_percent_sign_is_matched_and_the_regex_bug_stays_fixed(skin):
    """Found by running it on a concentration -- the exact case the rule flag
    exists for. `%` inside a \\b(...)\\b group never fires, because a percent sign
    is a non-word character and "30% glycolic" has no boundary after it."""
    rules = [r for r in skin["ten"]["rows"] if r["key"] == "rules"][0]
    assert rules["present"] is True, "the percent sign is not being matched again"
    src = open(os.path.join(HERE, "intercept.js"), encoding="utf-8").read()
    assert "|%/i" in src, "the percent alternation is back inside the word-boundary group"


def test_the_handles_hang_off_an_origin_nobody_named(skin):
    """"A standard 2024 dermatological method" names no standard and no body.
    Three handles, one unnamed origin, and the first instruction says so."""
    assert skin["handles"]["found"] == 3
    assert skin["pressed"]["sharedOrigin"] is True
    assert skin["pressed"]["firstCheck"]["origin"] == "an origin nobody named"
    assert "Ask where this came from" in skin["pressed"]["firstCheck"]["instruction"]


def test_fog_gets_no_number_and_no_flag(fog):
    assert fog["handles"]["found"] == 0
    assert fog["pressed"]["checkable"] is False
    assert fog["pressed"]["structure"] is None
    assert fog["flags"] == []
    assert fog["ten"]["settled"] <= 2


def test_the_three_readings_are_never_added_together(skin):
    """Measured, counted and pattern-matched are three different kinds of thing.

    A single "AI safety score" fusing them would be the most saleable thing this
    page could show and would be the exact failure it exists to catch.
    """
    assert set(skin) == {"empty", "handles", "pressed", "ten", "flags", "limits"}
    for banned in ("score", "safe", "rating", "overall", "confidence", "combined"):
        assert banned not in skin, banned


def test_the_kernel_carries_its_own_refusals(skin):
    assert skin["limits"] == [
        "This does not understand what you pasted.",
        "This does not certify that anything is safe.",
        "A claim that is completely made up reads exactly like a true one here.",
    ]


# ---------------------------------------------------------------- the page ---
def test_the_shipped_page_obeys_the_same_rules():
    page = os.path.join(HERE, "intercept.html")
    assert os.path.exists(page)
    raw = open(page, "rb").read()
    src = raw.decode("utf-8")
    assert b"\x00" not in raw
    assert not re.search(r"<script[^>]+\bsrc\s*=", src)
    assert "{{" not in src
    assert "min-height:44px" in src and "min-height:48px" in src
    assert 'href="index.html"' in src
    assert "Nothing leaves this device" in src


def test_the_page_never_promises_safety():
    """The brief asked for a page that gives people safety and security. It
    cannot, and a page that implies it would be a mask worn by the tool built to
    name masks. The words are checked because the temptation is real."""
    src = re.sub(r"\s+", " ", open(os.path.join(HERE, "intercept.html"),
                                   encoding="utf-8").read())
    assert "This does not certify that anything is safe." in src
    assert "ask somebody qualified before you act" in src
    for phrase in ("keeps you safe", "guarantees", "is safe to", "verified safe",
                   "protects you from", "certified"):
        assert phrase not in src, f"the page promises safety: {phrase!r}"


def test_the_page_carries_no_terminology_from_the_philosophical_source():
    """The ten elements were taken as logic. The vocabulary was not, by
    instruction, and a measuring page is not the place for it."""
    src = open(os.path.join(HERE, "intercept.html"), encoding="utf-8").read().lower()
    for word in ("quran", "qur'an", "surah", "ayah", "allah", "muslim", "mu'min",
                 "muhsin", "malak", "mulk", "deen", "islam", "arabic"):
        assert word not in src, f"intercept.html carries terminology it should not: {word}"


def test_the_ten_are_counted_and_the_handles_are_measured_and_the_page_says_so():
    src = re.sub(r"\s+", " ", open(os.path.join(HERE, "intercept.html"),
                                   encoding="utf-8").read())
    assert "Counted, not measured" in src
    assert "never added together" in src


def test_the_service_worker_caches_the_interceptor():
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    assert "./intercept.html" in sw


def test_the_parties_can_be_inverted_and_the_readout_does_not_move():
    """The falsification test, mechanised.

    "The landlord must return the deposit to the tenant" and "the tenant must
    return the deposit to the landlord" are the same words in a different order
    and opposite in meaning. The readout is BIT-IDENTICAL across the pair --
    same handles, same errands, same dependences, same flags, same sentence.

    That is not a defect being tolerated. It is the property that keeps this a
    lens: the engine reads no meaning, so it cannot pretend to have caught a
    semantic inversion, and it says so on the screen in the same size type. An
    engine that appeared to catch this would be claiming a comprehension it does
    not have, which is the precise failure the whole build is arranged against.

    What the tool CANNOT do about it is the user's job, and the page says so.
    """
    a = _run("Under clause 4 of the 2024 tenancy agreement, the landlord must "
             "return the deposit of 1200 to the tenant within 14 days of the "
             "inspection report.")
    b = _run("Under clause 4 of the 2024 tenancy agreement, the tenant must "
             "return the deposit of 1200 to the landlord within 14 days of the "
             "inspection report.")

    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), \
        "the engine appears to read meaning; that is worse than being blind"

    assert a["handles"]["found"] == 3
    assert "money" in [f["domain"] for f in a["flags"]]
    assert "law" in [f["domain"] for f in a["flags"]]
    assert "This does not understand what you pasted." in a["limits"]


def test_the_first_screen_carries_no_grade():
    """The leak, closed. "3 of 5 handles" is a mark out of five with a jargon
    word attached, on the screen a person meets first, in a build whose whole
    argument is that a spellchecker does not score."""
    import re
    tpl = open(os.path.join(HERE, "intercept_template.html"), encoding="utf-8").read()
    i = tpl.index('$("#outSays")')
    line = tpl[i:tpl.index("\n", i)]
    assert "of 5 handles" not in line, "the grade is back on the first screen"
    assert "r.pressed.says" in line

    src = re.sub(r"\s+", " ", open(os.path.join(HERE, "intercept.html"),
                                   encoding="utf-8").read())
    assert "of 5 handles." not in src
