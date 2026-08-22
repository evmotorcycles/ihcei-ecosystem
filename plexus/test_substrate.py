#!/usr/bin/env python3
"""Two pictures of the same substrate, and a test that must not be run yet.

    python3 -m pytest -q plexus/test_substrate.py

Locked, and UNRUN:
    substrate_preregistration.md
    sha256 4874d7700c65fefd739886a376cb008dc87cbb51be74e91947ee5bfda25d4dcb

Nothing here tests the substrate claim. It cannot be tested from this container
and, more to the point, it cannot be pre-registered by anybody who already knows
what happened in May 2022 and March 2023. See DATA_ABSENT.md.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG = "4874d7700c65fefd739886a376cb008dc87cbb51be74e91947ee5bfda25d4dcb"


@pytest.fixture(scope="module")
def a():
    out = subprocess.run(
        ["node", "-e",
         "globalThis.LMD=require('../smi/lmd.js');"
         "globalThis.PLEXUS=require('./engines.js');"
         "const M=require('./metaphor.js'),S=require('./substratelib.js');"
         "process.stdout.write(JSON.stringify({"
         "audits:Object.fromEntries(S.metaphors.map(m=>[m.id,M.audit(m)])),"
         "tally:M.tally(S.metaphors)}))"],
        cwd=HERE, capture_output=True, text=True, timeout=180)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_forward_preregistration_is_locked():
    got = hashlib.sha256(open(os.path.join(HERE, "substrate_preregistration.md"),
                              "rb").read()).hexdigest()
    assert got == PREREG


def test_the_forward_preregistration_has_not_been_run():
    """It is for a shock nobody has seen yet. A results file for it appearing
    before such a shock would mean it had been run on the two events whose
    outcomes are already known, which is the one thing it forbids."""
    for name in ("results_substrate.json", "substrate_results.json"):
        assert not os.path.exists(os.path.join(HERE, name)), \
            f"{name} exists; the unrun pre-registration has been run"
    src = open(os.path.join(HERE, "substrate_preregistration.md"),
               encoding="utf-8").read()
    assert "LOCKED AND UNRUN" in src
    assert "must never be run on them" in src


def test_the_claim_as_received_passes_our_own_instrument(a):
    """Their picture is a LENS, by the same rule applied to MetaphorOS's pictures
    and to this stack's own. It predicts three things about how settlement assets
    behave under a shock, and nobody in this conversation can make any of them
    come true by editing their own work.

    That is a real pass and it is worth saying plainly: the press is sound. What
    is missing is the data and an analyst who does not already know the answer.
    """
    r = a["audits"]["bedrock-and-sand"]
    assert r["klass"] == "lens"
    assert r["uncontrolled"] == 3
    for p in r["predictions"]:
        assert p["presenterControls"] is False
        assert abs(p["settles"] - 1 / 9) < 1e-9


def test_the_rival_picture_admits_it_was_written_after_the_answer(a):
    """The pier picture is a better fit for March 2023 and that is exactly why it
    proves nothing about March 2023. Written knowing the outcome, so it is a
    rival for the next shock and not a retrodiction dressed as a prediction."""
    r = a["audits"]["one-pier-on-bedrock"]
    assert r["klass"] == "lens"
    assert "written AFTER March 2023 was known" in r["where"]
    assert "never been tested against a shock nobody had seen" in r["where"]


def test_fewer_sharper_predictions_settle_more_each(a):
    """1/m^2, on two rival pictures of one thing. Three predictions settle
    0.111 each; two settle 0.250 each. Fewer, sharper claims put more at stake
    per check -- which is a reason to prefer the narrower picture, and not a
    reason to think it is true."""
    three = a["audits"]["bedrock-and-sand"]["predictions"]
    two = a["audits"]["one-pier-on-bedrock"]["predictions"]
    assert len(three) == 3 and len(two) == 2
    assert abs(three[0]["settles"] - 1 / 9) < 1e-9
    assert abs(two[0]["settles"] - 0.25) < 1e-9
    assert two[0]["settles"] > three[0]["settles"]


def test_both_pictures_are_lenses_and_neither_is_thereby_true(a):
    assert a["tally"] == {"lens": 2, "self-referring": 0, "notation": 0}


def test_the_locked_metaphor_library_was_not_quietly_extended():
    """metaphorlib.js had its counts pre-registered at twelve entries, 5/4/3.
    These two pictures live in a separate file so that adding them cannot move a
    number somebody already committed to."""
    out = subprocess.run(
        ["node", "-e",
         "const L=require('./metaphorlib.js');"
         "process.stdout.write(String(L.metaphors.length))"],
        cwd=HERE, capture_output=True, text=True, timeout=60)
    assert out.stdout.strip() == "12", "the locked audit corpus has changed size"


def test_the_blocked_sources_are_named_exactly():
    """Checked with curl and confirmed against the proxy's own failure log, not
    recalled."""
    src = open(os.path.join(HERE, "DATA_ABSENT.md"), encoding="utf-8").read()
    for host in ("api.coingecko.com", "api.coinpaprika.com", "api.llama.fi",
                 "data.messari.io"):
        assert host in src, host
    assert "403 to CONNECT" in src
    assert "raw.githubusercontent.com" in src and "200" in src, \
        "the route that IS open must be named too"


def test_the_reason_deeper_than_the_data_is_stated_first_class():
    """The data gap is the smaller problem. The larger one is that the outcomes
    of both named shocks are already known, so no pre-registration about them
    can be honest."""
    src = open(os.path.join(HERE, "DATA_ABSENT.md"), encoding="utf-8").read()
    assert "cannot be pre-registered by me" in src
    assert "retrodiction" in src
    assert "$0.87" in src, "the known outcome must be stated, not alluded to"


def test_the_flagship_case_that_may_falsify_the_claim_is_named():
    """USDC is the Category A exemplar and it is the one that broke. Naming it is
    the difference between an audit and an advertisement."""
    import re
    # collapsed whitespace: HTML and markdown both wrap, and a test that fails
    # on a line break is a test about line lengths
    src = re.sub(r"\s+", " ", open(os.path.join(HERE, "DATA_ABSENT.md"),
                                    encoding="utf-8").read())
    assert "USDC is the one that broke" in src
    assert "one custodian is one origin" in src.lower()
