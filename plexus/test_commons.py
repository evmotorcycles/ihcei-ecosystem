#!/usr/bin/env python3
"""The structure commons: does a shape measured in one place hold in another?

    python3 -m pytest -q plexus/test_commons.py

Every number checked here was written down in plexus/commons_preregistration.md
and the file hashed BEFORE commons.js, library.js or this suite were run once:

    sha256  25e2df1112521cb353c5017429d51686dfeef53a48c74ab00ff1007f0d5885be

The hash is asserted below, so the predictions cannot be edited after the fact
without this suite failing. Most of the tests here are VERIFICATION -- the code
against arithmetic done by hand -- and are labelled as such. Exactly two could
kill the idea rather than the implementation, and they are marked THESIS.
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
from spar.spar import Structure, bearings  # noqa: E402

PREREG_SHA256 = "25e2df1112521cb353c5017429d51686dfeef53a48c74ab00ff1007f0d5885be"


@pytest.fixture(scope="module")
def c():
    script = os.path.join(HERE, "commons_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_the_predictions_were_locked_before_anything_ran():
    """If this fails, every other number in this file is worthless.

    Not because the arithmetic would be wrong, but because a prediction that can
    be edited after the result arrives is not a prediction. The suite refuses to
    stand behind results whose predictions moved.
    """
    path = os.path.join(HERE, "commons_preregistration.md")
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    assert got == PREREG_SHA256, (
        f"the pre-registration has been edited since it was locked\n"
        f"  locked {PREREG_SHA256}\n  now    {got}"
    )


# ------------------------------------------------------------ VERIFICATION ---
def test_every_seed_entry_is_well_formed(c):
    for name in c["order"]:
        e = c["entries"][name]
        assert e["ok"], f"{name} was refused: {e['why']}"


def test_fosters_theorem_holds_in_every_slot_of_every_entry(c):
    """P1. Sum of bearings equals parts minus pieces, or the graph was not
    measured -- it was scored."""
    for name in c["order"]:
        for slot in ("drawn", "actual", "remedy"):
            s = c["entries"][name][slot]
            if s is None:
                continue
            assert s["conserved"], f"{name}/{slot}: conservation failed"
            assert abs(s["totalBearing"] - s["expected"]) < 1e-9
            assert s["expected"] == s["parts"] - s["pieces"]


@pytest.mark.parametrize(
    "name,drawn,actual,remedy,blind",
    [
        ("sole-maintainer", 1 / 3, 1.0, 0.25, 2 / 3),                 # P2 P3 P4 P5
        ("three-audits-one-threat-model", 1 / 3, 1.0, 0.25, 2 / 3),
        ("inline-only-under-csp", 1 / 3, 1.0, 0.25, 2 / 3),
        ("atomic-install-list", 1 / 12, 1.0, 1 / 12, 11 / 12),        # P7 P8
        ("two-ways-into-the-vault", 1.0, 1.0, 0.25, 0.0),             # P10
        ("benchmark-contamination", 0.5, 1.0, 0.5, 0.5),              # P11
        ("one-mirror-many-packages", 0.025, 1.0, 0.25, 0.975),        # P12
        ("model-weights-one-host", 1 / 6, 1.0, 0.25, 5 / 6),          # P13
    ],
)
def test_the_predicted_numbers(c, name, drawn, actual, remedy, blind):
    """P2-P13. Hand arithmetic against the implementation, entry by entry."""
    e = c["entries"][name]
    assert abs(e["drawn"]["deepest"] - drawn) < 1e-9, "drawn"
    assert abs(e["actual"]["deepest"] - actual) < 1e-9, "actual"
    assert abs(e["remedy"]["deepest"] - remedy) < 1e-9, "remedy"
    assert abs(e["blindSpot"] - blind) < 1e-9, "blind spot"


def test_the_chain_is_a_chain_and_the_star_is_not(c):
    """P9. The conjunction drawn correctly: every link sole-route, and eleven
    parts whose removal breaks the graph in two."""
    a = c["entries"]["atomic-install-list"]["actual"]
    assert len(a["bearings"]) == 12
    for b in a["bearings"]:
        assert abs(b - 1.0) < 1e-12, "a link in a chain must carry the whole load"
    assert len(a["singlePoints"]) == 11

    # And the star, where SPAR and FATHOM disagree in the open. SPAR names the
    # centre -- remove "The app installs" and twelve assets sit in twelve
    # pieces. FATHOM, asked about the twelve leaves, says 0.083 each. Neither
    # is wrong; they answer different questions, and the star is the drawing
    # where believing only the second one costs you the install.
    d = c["entries"]["atomic-install-list"]["drawn"]
    assert d["singlePoints"] == ["The app installs"], \
        "the centre of a star is its single point, and none of the leaves is"


def test_the_mean_blind_spot_is_what_was_predicted(c):
    """P14. Predicted 0.653125 before running."""
    assert abs(c["meanBlindSpot"] - 0.653125) < 1e-9


def test_the_browser_engine_agrees_with_the_python_engine(c):
    """The port gets no private arithmetic here either.

    Every entry's `actual` slot is re-measured by spar/ and fathom/ and must
    agree to nine places. Without this, the library could be right about a
    shape and wrong about the number attached to it, which is worse than
    having no library.
    """
    lib = json.loads(subprocess.run(
        ["node", "-e",
         "const L=require('./library.js');"
         "process.stdout.write(JSON.stringify(L.entries.map(e=>({id:e.id,a:e.actual}))))"],
        cwd=HERE, capture_output=True, text=True, timeout=120).stdout)
    for row in lib:
        s = row["a"]
        links = [(l[0], l[1], l[2]) for l in s["links"]]
        bb = bearings(Structure(s["parts"], links))
        got = c["entries"][row["id"]]["actual"]
        assert abs(bb["total"] - got["totalBearing"]) < 1e-9, row["id"]
        py = sound(Claim(s["conclusion"], s["sources"], links))
        assert abs(py["deepest_dependence"] - got["deepest"]) < 1e-9, row["id"]


# ------------------------------------------------------------------ THESIS ---
def test_the_same_shape_in_three_domains_gives_the_same_numbers(c):
    """P6. THESIS. If this fails the library is worthless and should be deleted.

    A maintainer with three jobs, three audits from one threat model, and three
    script files under one policy directive share no word. The arithmetic never
    reads a word, so all three must return identical dependences and identical
    bearings -- not close, identical, to 1e-12. That property is the entire
    reason a contributed structure is worth anything to somebody who does not
    work in the domain it came from.
    """
    sig = c["signatures"]
    ids = ["sole-maintainer", "three-audits-one-threat-model", "inline-only-under-csp"]

    words = [set(w.lower() for w in sig[i]["words"]) for i in ids]
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            assert not (words[i] & words[j]), \
                f"{ids[i]} and {ids[j]} share a label, so this proves nothing"

    for slot in ("drawn", "actual", "remedy"):
        base = sig[ids[0]][slot]
        for other in ids[1:]:
            got = sig[other][slot]
            assert got["parts"] == base["parts"] and got["pieces"] == base["pieces"]
            assert len(got["deps"]) == len(base["deps"])
            for x, y in zip(base["deps"], got["deps"]):
                assert abs(x - y) < 1e-12, f"{slot}: transfer is a wording effect"
            for x, y in zip(base["bearings"], got["bearings"]):
                assert abs(x - y) < 1e-12, f"{slot}: transfer is a wording effect"


def test_a_structure_has_nowhere_to_put_personal_data(c):
    """P15. THESIS. The promise the commons makes rests entirely on this.

    A structure may carry parts, links, sources and a conclusion. Not a note,
    not a description, not a comment. Not because a fifth key is necessarily
    personal data, but because a free-text field on a shared record is where a
    name ends up, and then the commons is a database and non-possession is a
    slogan. There is nothing to sanitise because there is nowhere to put it.
    """
    r = c["refusals"]
    assert r["ok"] == []
    assert any("description" in w for w in r["freeTextField"]), \
        "a free-text field on a structure was allowed through"
    assert any("owner" in w for w in r["entryExtraKey"])
    for key in ("badLicence", "noProvenanceKind", "noProvenanceWhere", "badId",
                "selfSupport", "danglingLink", "negativeWeight", "selfLink",
                "noActual", "nulInAPart"):
        assert isinstance(r[key], list) and r[key], f"{key} was allowed through"
        for w in r[key]:
            assert not w.startswith("THREW"), f"{key} raised instead of refusing"


def test_a_structure_from_a_real_problem_is_labelled_as_one(c):
    """The epistemic firewall, pointed at the library itself.

    Every entry says whether its problem was measured in this repository or
    cited from a documented mechanism. Nothing may be stored without that word.
    After a hundred entries nobody will remember which was which, and a library
    that has forgotten where its shapes came from is a collection of opinions.
    """
    for name in c["order"]:
        e = c["entries"][name]
        assert e["provenanceKind"] in ("measured-here", "cited"), name
        assert e["licence"] == "CC0-1.0", \
            f"{name} cannot be redistributed in a commons"


# -------------------------------------------------------------------- NULL ---
def test_nothing_here_can_show_that_a_commons_raises_a_ceiling(c):
    """NULL-1, registered in advance and reported as a null.

    The commons is claimed to be the one pillar a fork cannot copy. The evidence
    for that claim is a contribution rate, and it is 0 -- not low, absent, because
    nothing has shipped. contributionRate() is written so it cannot return a
    number when there are no buyers, precisely so no later version can quietly
    substitute a measurement from this file for the number that actually matters.
    """
    r = c["contributionRate"]
    assert r["measurable"] is False
    assert r["rate"] is None
    assert "nothing has shipped" in r["why"]

    shipped = c["contributionRateIfShipped"]
    assert shipped["measurable"] is True
    assert abs(shipped["rate"] - 0.061) < 1e-12
    assert shipped["passesGate"] is True, "6.1% clears the 5% gate; the gate is 5%"


def test_eight_entries_written_by_one_person_is_not_a_commons(c):
    """NULL-2. A worked example, and the code says so rather than the README.

    Three of the eight share a shape. That is a fact about the arithmetic, and
    also a fact about me: I wrote all three. The recurrence is only evidence
    about the world once a shape arrives from somebody who did not read this
    file, and this test exists to make that sentence hard to delete.
    """
    fam = c["families"]
    biggest = fam[0]
    assert biggest["size"] == 3
    assert set(biggest["ids"]) == {"sole-maintainer", "three-audits-one-threat-model",
                                   "inline-only-under-csp"}
    assert len(c["order"]) == 8, \
        "if the library has grown, the claim above about who wrote it must be re-checked"


# ------------------------------------------------------------- SUGGESTIONS ---
def test_matching_a_shape_is_a_suggestion_and_says_so_in_its_numbers(c):
    """A defect found by running it, not by reading it.

    match() compared labels by substring first. "package 3" matched Package 30
    through Package 39, and three query terms scored 0.406 against a forty-part
    entry -- an entry that genuinely was the right answer, arrived at for a
    reason that would have ranked the wrong one just as high. Labels are now
    compared for equality after stripping a leading article.
    """
    top = c["match"][0]
    assert top["id"] == "one-mirror-many-packages"
    assert set(top["shared"]) == {"registry", "package 3", "build succeeds"}
    assert abs(top["score"] - 3 / 42) < 1e-12, \
        "a substring match is inflating the score again"


# ------------------------------------------------------------- the page -----
def test_the_shipped_shapes_page_obeys_the_same_rules():
    """Fifth page, same invariants."""
    import re
    page = os.path.join(HERE, "commons.html")
    assert os.path.exists(page), "commons.html was never rendered"
    raw = open(page, "rb").read()
    src = raw.decode("utf-8")
    assert b"\x00" not in raw, "commons.html contains a literal NUL"
    assert not re.search(r"<script[^>]+\bsrc\s*=", src), \
        "an external script cannot load under this CSP -- which is one of the " \
        "eight shapes in the library this page displays"
    assert "{{" not in src, "an unfilled placeholder was shipped"
    assert "min-height:44px" in src and "min-height:48px" in src
    assert 'href="index.html"' in src, "there is no way back to the simple view"
    assert "Nothing leaves this device" in src


def test_the_service_worker_caches_the_shapes_page():
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    assert "./commons.html" in sw, "commons.html ships and is never cached"


def test_no_measurement_is_typed_into_the_page():
    """Every number on the page is computed at load from library.js.

    A shipped figure next to a shape is a figure that can stop being true when
    the shape is edited, and nobody would notice: the two would disagree only
    for a reader who ran the arithmetic themselves. So the template carries no
    percentage and no dependence at all, and this test says so by looking.
    """
    import re
    tpl = open(os.path.join(HERE, "commons_template.html"), encoding="utf-8").read()
    body = tpl.split("<script>{{LMD}}</script>")[0]
    stray = re.findall(r"\b\d+\.\d+\b|\b\d{1,3}\.\d%|\b0\.\d{3}\b", body)
    stray = [s for s in stray if not re.match(r"^\d+\.\d+(rem|px|em)?$", s)]
    assert not stray, f"a number was typed into the markup: {stray}"
    assert "66.7" not in tpl and "0.111" not in tpl


def test_pressing_a_shape_does_not_destroy_the_shape_you_pressed():
    """The fifth time this defect has been guarded against in this codebase.

    Editor, manifold chips, topology sources, Flint lines -- each rebuilt a list
    inside a handler bound to one of that list's own children, destroying the
    element mid-gesture. The rule written into the source is: mutate the row,
    never the list.
    """
    tpl = open(os.path.join(HERE, "commons_template.html"), encoding="utf-8").read()
    i = tpl.index('head.addEventListener("click"')
    body = tpl[i:tpl.index("return e;", i)]
    assert 'setAttribute("aria-expanded"' in body, "the flag is not flipped in place"
    assert "appendChild" not in body and "innerHTML" not in body, \
        "rebuilding inside the handler destroys the card that was pressed"


def test_the_overlay_can_actually_be_hidden():
    """.void sets display:flex, and an author rule outranks the user agent's
    [hidden]{display:none}. Without the guard the "no shape uses those words"
    message stays painted across the results. Shipped once, on the manifold."""
    tpl = open(os.path.join(HERE, "commons_template.html"), encoding="utf-8").read()
    assert ".void[hidden]{display:none}" in tpl


def test_the_page_says_what_it_has_not_shown():
    """The null belongs on the page, not only in the pre-registration.

    A page that displays eight measured shapes and says nothing about what they
    do not establish is an advertisement. The gate is printed where the reader
    is, in the words agreed before any of it was run.
    """
    src = open(os.path.join(HERE, "commons.html"), encoding="utf-8").read()
    assert "5% within 60 days" in src, "the gate set in advance is not on the page"
    assert "not measurable yet" in src
    assert "worked example, not yet a commons" in src
    assert "CC0-1.0" in src
