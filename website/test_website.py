#!/usr/bin/env python3
"""Guards for the Novora website.

    python3 -m pytest -q website/test_website.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(HERE, "index.html")


def html():
    return open(PAGE, encoding="utf-8").read()


def flat():
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html()))


def test_no_network_no_tracking():
    src = html()
    for pat in (r'src\s*=\s*"https?://', r'href\s*=\s*"https?://', r"fetch\s*\(",
                r"XMLHttpRequest", r"gtag|analytics|googletagmanager|facebook",
                r"@import", r"navigator\.sendBeacon"):
        assert not re.search(pat, src, re.I), f"the site must stay self-contained; found {pat}"
    assert "{{" not in src, "unfilled template placeholder"


def test_the_live_demo_runs_the_real_audited_engine():
    src = html()
    assert "function assay(" in src, "the demo must run the real engine, not a mock"
    assert "does NOT understand language" in src, (
        "the engine's own disclaimer must survive inlining")


def test_every_app_link_points_at_a_file_that_exists():
    for rel in re.findall(r'href="(\.\./[^"#]+)"', html()):
        target = os.path.normpath(os.path.join(HERE, rel))
        assert os.path.exists(target), f"broken link: {rel}"


def test_the_limits_section_is_present_and_specific():
    f = flat()
    for phrase in [
        "Nothing here knows whether something is true",
        "These are screens , not judges".replace(" , ", ", "),
        "There is no vision model",
        "No video can be fetched",
        "Structure is not safety",
        "tamper-evident, not tamper-proof",
        "We make no claim about market size or valuation",
    ]:
        assert phrase in f, f"missing limit: {phrase!r}"


def test_the_failed_calibration_is_on_the_marketing_page():
    """The number we failed on belongs on the front page, not only in the repo."""
    f = flat()
    assert "0.3727" in f
    assert "0.15" in f
    assert "not moved" in f
    assert "We failed" in f


def test_measured_results_are_reported_with_their_caveats():
    f = flat()
    assert "confidence interval includes zero" in f, (
        "the learner's marginal result must keep its caveat on the public page")
    assert "magnitude marginal" in f
    assert "Only 7 instances exist" in f
    assert "Does not prove the linear law" in f


def test_button_colour_comes_from_a_token_not_a_media_query():
    """Regression lock. A colour override inside a media query outranked the
    component rule and painted the outline button near-white on light paper —
    an invisible call to action."""
    src = html()
    assert "--on-deep" in src
    assert src.count("--on-deep:") >= 3, "the token must be defined in all three theme states"
    assert not re.search(r"@media[^{]*\{[^{}]*\{[^{}]*\.btn\s*\{[^}]*color", src), (
        "no .btn colour may be defined only inside a media query")


def test_all_three_theme_states_are_defined():
    src = html()
    assert "prefers-color-scheme:dark" in src
    assert ':root[data-theme="dark"]' in src
    assert ':root:not([data-theme="light"])' in src
    assert re.search(r"body\{[^}]*background:var\(--paper\)", src), (
        "body must paint an explicit background or it borrows the host's ground")


def test_animation_respects_reduced_motion():
    src = html()
    assert "prefers-reduced-motion" in src
    assert "reduce" in src and "requestAnimationFrame" in src

def test_the_inlined_engine_is_byte_identical_to_the_audited_one():
    """The site ships a COPY of cairn/ei_engine.js. A copy nobody checks drifts.

    It drifted once already: the engine gained handle extraction and the site
    kept serving the previous build, so the demo on the front page and the app
    behind it stopped being the same thing.
    """
    import re as _re
    site = html()
    engine = open(os.path.join(ROOT, "cairn/ei_engine.js"), encoding="utf-8").read()
    m = _re.search(r"<script>(/\* ei_engine\.js.*?)</script>", site, _re.S)
    assert m, "the inlined engine block is missing from the page"
    assert m.group(1).strip() == engine.strip(), (
        "website/index.html is serving a stale copy of cairn/ei_engine.js — "
        "re-inline it")
