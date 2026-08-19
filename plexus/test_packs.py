#!/usr/bin/env python3
"""Packs: the structure arrives already built, so nobody has to draw it.

    python3 -m pytest -q plexus/test_packs.py

Predictions were written down and the file hashed before any of this ran:

    sha256  bc23a73a33c9261eec98c95bf0cea85bcbaf8a7fa9385c073168e96d9835a2a4

Two tests here matter more than the arithmetic. One asks whether a pack is
actually less work than building the same thing by hand -- if it is not, the
pack has no reason to exist. The other asks what happens to a field somebody
left empty, because software that turns a blank into a 0 has invented a number,
and inventing numbers is the precise thing this stack was built to catch.
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

from spar.spar import Structure, bearings, single_points  # noqa: E402

PREREG_SHA256 = "bc23a73a33c9261eec98c95bf0cea85bcbaf8a7fa9385c073168e96d9835a2a4"


@pytest.fixture(scope="module")
def k():
    script = os.path.join(HERE, "packs_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_predictions_were_locked_before_anything_ran():
    path = os.path.join(HERE, "packs_preregistration.md")
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    assert got == PREREG_SHA256, (
        f"the pre-registration has been edited since it was locked\n"
        f"  locked {PREREG_SHA256}\n  now    {got}"
    )


def test_every_pack_is_well_formed(k):
    for name in k["order"]:
        assert k["packs"][name]["why"] == [], f"{name}: {k['packs'][name]['why']}"


# ------------------------------------------------------------- arithmetic ---
def _rows(res):
    return {r["key"]: r["value"] for r in res["rows"]}


def test_the_metered_bill_that_prompted_this(k):
    """K1. Reading 70 against 58, at 5032 a unit, plus 1700 standing charge."""
    r = _rows(k["meter"])
    assert r["units"] == 12
    assert r["usage"] == 60384
    assert r["total"] == 62084
    v = k["meter"]["verdict"]
    assert v["difference"] == 0 and v["matches"] is True
    assert v["says"] == "The figure they printed follows from the numbers you typed."


def test_paying_more_than_they_asked_is_carried_forward(k):
    """K2. 65000 against 62084 leaves 2916, and it is a credit, not a gap."""
    r = _rows(k["meterPaid"])
    assert r["carried"] == 2916


def test_a_difference_is_named_and_nobody_is_accused(k):
    """K3. The arithmetic knows two numbers differ. It does not know who is
    right about the tariff, the reading or the law, and it must not imply that
    it does -- a person acting on 'they overcharged you' when the pack simply
    has the wrong tariff shape is worse off than before they opened it."""
    v = k["meterWrong"]["verdict"]
    assert v["difference"] == 916 and v["matches"] is False
    assert v["says"] == "The figure they printed is 916 more than these parts come to."

    low = k["meterShort"]["verdict"]
    assert low["says"] == "The figure they printed is 1084 less than these parts come to."

    for word in ("overcharge", "wrong", "error", "mistake", "owe", "fraud", "should pay"):
        assert word not in v["says"].lower(), f"the verdict accuses somebody: {word}"


def test_a_blank_field_stays_blank_and_never_becomes_zero(k):
    """K6. The one that would make this dangerous rather than merely useless.

    Leaving "what you actually paid" empty must make the carried-forward row
    VANISH. If it silently read 0, the pack would report a credit of -62084 and
    a person could act on it.
    """
    n = k["meterNoPaid"]
    assert n["hasCarried"] is False
    assert n["carriedInValues"] is False
    assert "carried" not in n["rowKeys"]


def test_a_missing_required_number_is_named_and_stops_the_chain(k):
    """Everything downstream of a gap is absent too. Units still computes,
    because both readings were given; nothing that needs the rate appears."""
    m = k["meterMissing"]
    assert set(m["missing"]) == {"Price per unit", "Fixed charge"}
    assert [r["key"] for r in m["rows"]] == ["units"]
    assert m["verdict"] is None, "no verdict can be given on numbers nobody typed"


def test_numbers_typed_the_way_people_type_them(k):
    """5,032 and 1 700 are what is printed on paper and what people copy."""
    assert k["meterMessy"]["verdict"]["matches"] is True
    assert k["meterNotANumber"]["refused"] == ["Price per unit is not a number"]


@pytest.mark.parametrize(
    "case,want",
    [
        ("payslip", {"taken": 840, "net": 3360}),          # K14
        ("invoice", {"tax": 216, "total": 1416}),          # K12
        ("deposit", {"taken": 275, "back": 1225}),         # K15
        ("split", {"each": 125}),
        ("instalments", {"instalments": 960, "paid": 1060, "extra": 160}),  # K13
    ],
)
def test_the_other_packs_come_out_where_they_were_predicted(k, case, want):
    r = _rows(k[case])
    for key, value in want.items():
        assert abs(r[key] - value) < 1e-9, f"{case}.{key}: {r[key]} not {value}"


def test_dividing_by_zero_is_refused_rather_than_shown_as_infinity(k):
    """K7. Nought people is a thing somebody will type."""
    z = k["splitByZero"]
    assert z["rows"] == []
    assert z["refused"] == [
        "Each person owes: that would divide by zero, and there is no answer to give"]


def test_a_pack_with_no_printed_figure_gives_no_verdict(k):
    """Splitting a bill and working out instalments compute something; there is
    no figure of theirs to check it against, and inventing a verdict would be
    claiming to have checked something nobody supplied."""
    assert k["split"]["verdict"] is None
    assert k["instalments"]["verdict"] is None


# -------------------------------------------------------------- structure ---
def test_the_metered_bill_structure_is_a_tree_with_no_second_way_anywhere(k):
    """K4, K5. Six parts, five links, every one of them a sole route."""
    s = k["packs"]["metered-bill"]["structure"]
    assert s["parts"] == 6 and len(s["links"]) == 5
    assert s["soleRoutes"] == 5
    for l in s["links"]:
        assert abs(l["bearing"] - 1.0) < 1e-9
    assert abs(s["totalBearing"] - 5.0) < 1e-9
    assert s["expected"] == 5 and s["pieces"] == 1 and s["conserved"] is True
    assert s["singlePoints"] == ["Units used", "What the bill should be"]


def test_every_pack_structure_conserves_and_matches_the_python_engine(k):
    lib = json.loads(subprocess.run(
        ["node", "-e",
         "const L=require('./packlib.js');"
         "process.stdout.write(JSON.stringify(L.packs.map(p=>({id:p.id,s:p.structure}))))"],
        cwd=HERE, capture_output=True, text=True, timeout=120).stdout)
    for row in lib:
        s = row["s"]
        links = [(a, b, w) for a, b, w in s["links"]]
        py = bearings(Structure(s["parts"], links))
        got = k["packs"][row["id"]]["structure"]
        assert abs(py["total"] - got["totalBearing"]) < 1e-9, row["id"]
        assert got["conserved"] is True, row["id"]
        pysp = sorted(x["part"] for x in single_points(Structure(s["parts"], links)))
        assert pysp == sorted(got["singlePoints"]), row["id"]


def test_the_reason_for_not_running_the_rest_on_reading_is_carried_as_data(k):
    """A bill is a conjunction and the rest-on reading assumes sources that
    stand in for one another. Running it here would report each meter reading
    at 0.0625 -- not merely unhelpful, backwards. The explanation travels with
    the result so a page cannot quietly stop printing it."""
    for name in k["order"]:
        why = k["packs"][name]["structure"]["whyNoRedundancyReading"]
        assert "conjunction" in why and "understate" in why


# --------------------------------------------------------------- friction ---
def test_a_pack_is_less_work_than_drawing_it_by_hand(k):
    """K10. The claim that justifies the whole thing, as arithmetic.

    If typing the numbers into a pack is not fewer actions than naming every
    part and drawing every link, the pack has no reason to exist and should be
    deleted rather than argued for.
    """
    for name in k["order"]:
        e = k["packs"][name]["effort"]
        assert e["lessWork"] is True, \
            f"{name}: {e['asks']} to type against {e['byHand']} to place by hand"
        assert e["saved"] > 0

    t = k["effortTotals"]
    assert t["allLessWork"] is True
    assert t["asks"] == 25 and t["byHand"] == 59
    assert t["asks"] < t["byHand"] / 2, "the saving should not be marginal"


def test_counting_what_is_typed_is_not_a_usability_measurement(k):
    """NULL-K1, kept where somebody reading the numbers above will see it.

    Nothing here measures whether a tired person at the end of a long day finds
    this easy. That needs people, and there are none in this repository. Fewer
    things to type is a proxy and this test exists so it stays labelled as one.
    """
    assert "asks" in k["effortTotals"] and "byHand" in k["effortTotals"]
    assert "usability" not in json.dumps(k).lower()
    assert "easy to use" not in json.dumps(k).lower()


# ------------------------------------------------------------- honesty ------
def test_every_pack_says_what_it_takes_for_granted(k):
    """K11. A pack that hides its assumptions is a mask with a form on it."""
    for name in k["order"]:
        p = k["packs"][name]
        assert p["assumes"], f"{name} declares no assumptions"
        assert p["goCheck"], f"{name} leaves the reader nowhere to go"
        for a in p["assumes"]:
            assert a.strip()

    flat = k["packs"]["metered-bill"]["assumes"]
    assert any("bands or steps" in a for a in flat), \
        "the flat-rate assumption is the whole reason a stepped tariff will not match"


def test_no_pack_carries_a_named_supplier_or_a_currency(k):
    """NULL-K2 and the currency rule, asserted by reading the library.

    A specific tariff I cannot verify would be worse than the blank canvas it
    replaces: a confidently wrong "what it should be" arrives at the moment a
    person is least able to notice. And these are used in places with different
    money, so the packs carry numbers and no symbols.
    """
    src = open(os.path.join(HERE, "packlib.js"), encoding="utf-8").read()
    for symbol in ("$", "£", "€", "₹", "¥", "UGX", "USD", "shilling", "Shilling",
                   "dollar", "Dollar"):
        assert symbol not in src, f"packlib.js carries a currency: {symbol}"
    for word in ("Ltd", "Inc", "Corporation", "plc", "GmbH"):
        assert word not in src, f"packlib.js names a company: {word}"


def test_the_refusals_come_back_as_reasons_not_exceptions(k):
    """K8, K9, K11. A malformed pack must not be able to take the page down."""
    r = k["refusals"]
    assert r["ok"] == []
    for key in ("noAssumes", "noGoCheck", "unknownKey", "selfReference",
                "badOperator", "duplicateKey", "noLabel", "badId", "threeWayMinus"):
        assert isinstance(r[key], list) and r[key], f"{key} was allowed through"
        for w in r[key]:
            assert not w.startswith("THREW"), f"{key} raised instead of refusing"
    assert any("derived from itself" in w for w in r["selfReference"])
    assert any("not a value in this pack" in w for w in r["unknownKey"])


def test_a_pack_is_data_and_data_does_not_run(k):
    """No eval, no Function, no parser. An expression is a prefix array of an
    operator and its operands, and there are exactly four operators. A pack that
    could run code would make the commons a way to ship code to strangers under
    the name of a shape."""
    src = open(os.path.join(HERE, "packs.js"), encoding="utf-8").read()
    body = src.split("*/", 1)[1]
    for banned in ("eval(", "new Function", "setTimeout(", "innerHTML"):
        assert banned not in body, f"packs.js can run what it was given: {banned}"
    lib = open(os.path.join(HERE, "packlib.js"), encoding="utf-8").read()
    assert "function" not in lib.split("*/", 1)[1].replace("(function (root)", "") \
        .replace("if (typeof module", ""), "packlib.js carries code, not data"


# ---------------------------------------------------------------- the page --
def test_the_shipped_packs_page_obeys_the_same_rules():
    import re
    page = os.path.join(HERE, "packs.html")
    assert os.path.exists(page), "packs.html was never rendered"
    raw = open(page, "rb").read()
    src = raw.decode("utf-8")
    assert b"\x00" not in raw
    assert not re.search(r"<script[^>]+\bsrc\s*=", src)
    assert "{{" not in src
    assert "min-height:44px" in src and "min-height:48px" in src
    assert 'href="index.html"' in src
    assert "Nothing leaves this device" in src


def test_the_page_says_what_a_matching_total_does_not_mean():
    """NULL-K4, printed where the person is rather than in a file.

    A green tick that a reader takes to mean "this bill is fair" is a mask, and
    it would be one built by the tool that names them.
    """
    src = open(os.path.join(HERE, "packs.html"), encoding="utf-8").read()
    assert "It does not mean the price is fair" in src
    assert "does not mean the reading is right" in src


def test_the_service_worker_caches_the_packs_page():
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    assert "./packs.html" in sw


def test_choosing_a_pack_does_not_destroy_the_button_you_pressed():
    """The sixth time this defect has been guarded against here."""
    tpl = open(os.path.join(HERE, "packs_template.html"), encoding="utf-8").read()
    i = tpl.index('function choose(')
    body = tpl[i:tpl.index("function fillIn(", i)]
    assert "#packs" not in body, \
        "rebuilding the pack list inside the handler destroys the button pressed"


def test_a_disputed_total_gives_two_carried_figures_not_one(k):
    """Found by driving the page, not by reading the code.

    With the printed total at 62084 the credit is 2916. Change the printed total
    to 63000 and a single "carried to next time" quietly becomes 2000 -- because
    it was measured against what they asked, not against what the parts come to.
    Both numbers are real and they mean different things, and which one a person
    is owed depends on who is right about the 916, which this page cannot know.

    So both are shown. They read identically whenever the bill matches, and they
    diverge by exactly the amount in dispute when it does not.
    """
    same = {r["key"]: r["value"] for r in k["meterPaid"]["rows"]}
    assert same["carried"] == 2916 and same["carriedIfParts"] == 2916, \
        "on a matching bill the two must agree"

    node = subprocess.run(
        ["node", "-e",
         "globalThis.LMD=require('../smi/lmd.js');"
         "globalThis.PLEXUS=require('./engines.js');"
         "const P=require('./packs.js'),L=require('./packlib.js');"
         "const p=L.packs.find(x=>x.id==='metered-bill');"
         "const r=P.fill(p,{now:70,before:58,rate:5032,fee:1700,printed:63000,paid:65000});"
         "process.stdout.write(JSON.stringify(r.rows.reduce((a,x)=>(a[x.key]=x.value,a),{})))"],
        cwd=HERE, capture_output=True, text=True, timeout=60)
    assert node.returncode == 0, node.stderr
    split = json.loads(node.stdout)
    assert split["carried"] == 2000, "against what they asked"
    assert split["carriedIfParts"] == 2916, "against what the parts come to"
    assert split["carriedIfParts"] - split["carried"] == 916, \
        "the gap between the two lines must be exactly the amount in dispute"
