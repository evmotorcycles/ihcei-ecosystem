#!/usr/bin/env python3
"""Cairn, and the two infrastructure layers under it.

    python3 -m pytest -q plexus/test_cairn.py

NOT A PARITY SUITE. The shipped ihcei_v3 stack (nere_engine_v3,
gt_probabilistic, ihcei_kernel_v3) is not in this repository, so nere.js and
ihcei.js were written from the BEHAVIOUR documented in nere_experiment/ and are
checked against that description and against themselves. No claim is made that
their numbers match the shipped engines. Where a number here is checked against
spar/ or fathom/, it is because Cairn is calling those engines directly.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from fathom.fathom import Claim, sound  # noqa: E402


@pytest.fixture(scope="module")
def c():
    script = os.path.join(HERE, "cairn_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


# --------------------------------------------------------------- structure ---
def test_the_worked_example_lands_where_it_should(c):
    """An article whose figure and expert both trace back to one blog post
    rests entirely on that blog post -- and Cairn says so with a number, not a
    paragraph. Checked against the Python FATHOM, because Cairn is calling it."""
    s = c["oneBlog"]["structure"]
    assert s["restsOnOneThread"] is True
    assert abs(s["deepest"] - 1.0) < 1e-9

    py = sound(Claim("The policy raises your taxes", ["A blog post from 2021"],
                     [("The policy raises your taxes", "Quoted figure", 4.0),
                      ("The policy raises your taxes", "Quoted expert", 4.0),
                      ("Quoted figure", "A blog post from 2021", 6.0),
                      ("Quoted expert", "A blog post from 2021", 6.0)]))
    assert abs(py["deepest_dependence"] - s["deepest"]) < 1e-9


def test_two_real_sources_do_not_read_as_one(c):
    s = c["twoSources"]["structure"]
    assert s["restsOnOneThread"] is False
    assert abs(s["deepest"] - 0.5) < 1e-9


# ---------------------------------------------------------------- firewall ---
def test_structure_and_rhetoric_can_point_opposite_ways(c):
    """The pair that proves they are not secretly the same number.

    A structurally sound claim written in pressure language, and a claim resting
    on one thread written politely. If a single "credibility score" were ever
    fused out of these two, this pair is what it would get wrong -- in both
    directions at once.
    """
    pushy, polite = c["soundButPushy"], c["shakyButPolite"]
    assert abs(pushy["structure"]["deepest"] - 0.5) < 1e-9
    assert pushy["rhetoric"]["band"] == "leans on the reader"
    assert abs(polite["structure"]["deepest"] - 1.0) < 1e-9
    assert polite["rhetoric"]["band"] == "hands judgement back"


def test_no_combined_score_is_ever_emitted(c):
    """The most saleable field this engine could produce, and the most
    dishonest. Its absence is load-bearing, so it is asserted."""
    for key in ("oneBlog", "twoSources", "soundButPushy", "shakyButPolite"):
        payload = c[key]
        assert "firewall" in payload
        for banned in ("combined", "score", "credibility", "trustScore", "verdict"):
            assert banned not in payload, f"{key} emitted a fused {banned}"


# -------------------------------------------------------------------- NERE ---
def test_text_with_no_markers_is_unscreened_not_passed(c):
    """Most careful writing carries none of these phrases. Reporting that as
    'passed' would turn silence into endorsement."""
    n = c["screens"]["neutral"]
    assert n["band"] == "unscreened" and n["screened"] is False
    assert c["screens"]["empty"]["band"] == "unscreened"
    assert c["screens"]["pressure"]["band"] == "leans on the reader"
    assert c["screens"]["disciplined"]["band"] == "hands judgement back"


def test_the_screen_is_a_ratio_so_length_is_not_guilt(c):
    p = c["screens"]["pressure"]
    assert -1.0 <= p["balance"] <= 1.0
    assert p["pressure"] and not p["discipline"]


def test_the_screen_is_fooled_by_a_marker_inside_a_negation(c):
    """A known, deliberate weakness, recorded so no one has to rediscover it.

    The screen matches substrings and does not read grammar. "You can verify"
    inside "you can verify nothing here" counts as handing judgement back. The
    first version scored the phrase "you don't need to verify the METHODOLOGY"
    as carrying a discipline marker, because "methodology" was on the list; bare
    topic nouns were removed for that reason, but the underlying flaw is not
    fixed and cannot be fixed by a word list. This test asserts the wrong
    answer on purpose: it is documentation with teeth, and it will fail the day
    someone makes the screen cleverer, which is when this note needs rereading.
    """
    fooled = c["screens"]["fooled"]
    assert "you can verify" in fooled["discipline"], \
        "if this no longer matches, the screen has changed and the limits moved"
    assert fooled["band"] != "leans on the reader", \
        "the negation is not detected -- that is the point of this test"


# ------------------------------------------------------------------- IHCEI ---
def test_the_coupling_is_linear_and_the_quadratic_stays_retired(c):
    """E = U*D. E = U*D^2 was retired; a law that comes back quietly is how a
    disconfirmed result gets resurrected."""
    for row in c["essence"]:
        assert abs(row["e"] - row["u"] * row["d"]) < 1e-12
        if row["d"] != 1:
            assert abs(row["e"] - row["squared"]) > 1e-9, "D is being squared"
    src = open(os.path.join(HERE, "ihcei.js"), encoding="utf-8").read()
    assert "D * D" not in src and "Math.pow(D" not in src


def test_extreme_evidence_widens_the_interval_instead_of_flipping_it(c):
    """The floor, and the whole reason this layer exists.

    Against a prior that actually asserts something, evidence that contradicts
    it hard must make the system LESS sure rather than confidently opposite.
    With the floor switched off the same evidence gives a narrow interval and a
    committed verdict; with it on, the interval widens and the band stays
    inconclusive.
    """
    on, off = c["informative"], c["unfloored"]
    quiet = on[0]
    assert quiet["widened"] is False, "no surprise should mean no widening"

    for a, b in zip(on[1:], off[1:]):
        assert a["widened"] is True, f"surprise {a['surprise']:.2f} did not widen"
        assert a["width"] > b["width"], "the floor did not widen the interval"
        assert a["band"] == "inconclusive", \
            "extreme evidence flipped the verdict instead of widening"
    # and without the floor it WOULD have committed, or this proves nothing
    assert any(r["band"] != "inconclusive" for r in off[1:]), \
        "the floor-off control never commits, so the test is vacuous"


def test_the_floor_cannot_fire_against_a_uniform_prior(c):
    """A limitation, stated rather than discovered later.

    Beta(1,1) has sd = sqrt(1/12), and no rate can sit further from its mean
    than 0.5, so the largest possible surprise is 0.5/sqrt(1/12) = sqrt(3),
    which is 1.732 -- below the tolerance of 2. Cairn's DEFAULT prior is
    uniform, so on an arbitrary pasted page the floor is inert by construction
    and the band is driven by evidence alone. That is the correct behaviour --
    you cannot be surprised if you asserted nothing -- but it means the floor
    protects informative channels, not anonymous ones.
    """
    assert abs(0.5 / math.sqrt(1 / 12) - math.sqrt(3)) < 1e-12
    assert math.sqrt(3) < 2
    for row in c["floor"]:
        assert row["widened"] is False
        assert row["surprise"] <= math.sqrt(3) + 1e-9


# ------------------------------------------------------------ the labelling --
def test_the_layers_say_plainly_that_they_are_not_ports():
    """The stack they describe is not in this repository. Anyone reading these
    files must not come away believing they were checked against it."""
    for name in ("nere.js", "ihcei.js"):
        src = open(os.path.join(HERE, name), encoding="utf-8").read()
        assert "NOT A PORT" in src
        assert "parity-checked" in src, "the file must say it was not parity-checked"
        assert "ihcei_stack" in src, "it must name the stack it is NOT a port of"


def test_cairn_states_what_it_cannot_do():
    src = open(os.path.join(HERE, "cairn.js"), encoding="utf-8").read()
    assert "cannot tell you a claim is true" in src
    assert "secretly share an origin" in src


def test_the_engine_has_no_interface_and_reaches_no_network():
    """Infrastructure. These three have no page, and nothing in them dials out."""
    for name in ("nere.js", "ihcei.js", "cairn.js"):
        src = open(os.path.join(HERE, name), encoding="utf-8").read()
        for banned in ("fetch(", "XMLHttpRequest", "WebSocket", "document.",
                       "window.addEventListener", "innerHTML"):
            assert banned not in src, f"{name} reaches into a page or a network: {banned}"


def test_the_line_splitter_is_dumb_on_purpose(c):
    """It breaks text where a reader would and decides nothing. Anything
    cleverer would be choosing what counts as a claim on the person's behalf."""
    assert c["lines"] == ["One claim here.", "Another there!",
                          "A third on its own line."]


# ------------------------------------------------------------ the Flint page --
def test_the_flint_page_obeys_the_same_rules():
    import re
    page = os.path.join(HERE, "flint.html")
    assert os.path.exists(page), "flint.html was never rendered"
    raw = open(page, "rb").read()
    src = raw.decode("utf-8")
    assert b"\x00" not in raw
    assert not re.search(r"<script[^>]+\bsrc\s*=", src), \
        "an external script cannot load under this CSP"
    assert "{{" not in src
    # The blanket network ban that stood here is RETIRED with
    # test_the_page_reaches_no_network (see test_plexus.py for why).
    # Replaced by two stronger rules: the measuring kernel can never reach
    # the network, and a page may not promise that nothing leaves the device
    # while reaching out. Third-party origins stay blocked by connect-src.
    assert "min-height:44px" in src and "min-height:48px" in src


def test_flint_shows_the_two_measurements_apart_and_never_fuses_them():
    """Flint is where a combined score would be most tempting: two panels, side
    by side, one number each. The page must keep them apart in what it says as
    well as in what it computes."""
    src = open(os.path.join(HERE, "flint.html"), encoding="utf-8").read()
    assert 'data-k="struct"' in src and 'data-k="rhet"' in src
    assert "Two measurements, never one" in src
    flat = " ".join(src.split())
    assert "There is no combined score here and there will not be one." in flat
    assert "A careful liar scores clean" in flat


def test_flint_says_that_no_marked_phrasing_is_not_a_pass():
    """Silence from a word list is not endorsement, and the page has to say so
    where a person will actually read it."""
    src = open(os.path.join(HERE, "flint.html"), encoding="utf-8").read()
    assert "That is not a pass" in src
    assert "most careful writing looks like this" in src


def test_flint_mutates_the_row_and_never_rebuilds_the_list():
    """The fourth appearance of one defect in this app.

    Rebuilding a list inside its own click handler replaces the element that was
    just tapped: keyboard focus drops to the top of the page and a run of taps
    registers only the first. Driven here, seven taps produced one included line.
    Fixed in the editor, the manifold, the topology sources, and now here.
    """
    src = open(os.path.join(HERE, "flint_template.html"), encoding="utf-8").read()
    i = src.index('$("#lines").addEventListener')
    body = src[i:src.index('$("#joins").addEventListener', i)]
    assert "paintRow(" in body, "the row is not updated in place"
    assert "drawLines()" not in body, "rebuilding the list destroys the tapped row"


def test_every_shipped_page_is_in_the_service_worker_cache_list():
    """caches.addAll is atomic. A page that ships and is not cached vanishes
    offline; a page cached and not shipped rejects the install and takes offline
    down with it. Checked as an invariant over whatever pages exist, rather than
    as a hardcoded version string that has to be edited in two places and was
    already stale once."""
    import re
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    assert re.search(r'var CACHE = "plexus-v\d+"', sw), "no versioned cache name"
    listed = set(re.findall(r'"\./([a-z0-9_-]+\.html)"', sw))
    built = {f for f in os.listdir(HERE)
             if f.endswith(".html") and not f.endswith("_template.html")
             and f not in ("app.html",)}
    assert built <= listed, f"shipped but never cached: {sorted(built - listed)}"
    for f in listed:
        assert os.path.exists(os.path.join(HERE, f)), \
            f"{f} is cached and does not exist -- caches.addAll would reject"
