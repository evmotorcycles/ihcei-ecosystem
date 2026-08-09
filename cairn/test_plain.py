#!/usr/bin/env python3
"""Guards for cairn/plain.html — the plain-language browser app.

    python3 -m pytest -q cairn/test_plain.py

The app is what ordinary people actually touch, so the things that must not
regress are: it works with no network, it shows the measured numbers rather than
invented ones, and every tool keeps its "what this cannot do" panel.
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "plain.html")


def html():
    return open(HTML, encoding="utf-8").read()


def test_build_is_deterministic_and_current():
    """The committed file must be exactly what the build script produces."""
    before = html()
    subprocess.run(["python3", os.path.join(HERE, "build_plain.py")], check=True,
                   capture_output=True)
    assert html() == before, (
        "plain.html is stale — re-run python3 cairn/build_plain.py and commit it")


def test_no_external_resources_at_all():
    """It has to work offline, from file://, with no account and no server."""
    src = html()
    for pat in (r'src\s*=\s*"https?://', r'href\s*=\s*"https?://',
                r'@import', r'fetch\s*\(', r'XMLHttpRequest', r'WebSocket\s*\(',
                r'\.src\s*=\s*"https?://'):
        assert not re.search(pat, src), f"external resource or network call: {pat}"
    assert "{{" not in src, "unfilled template placeholder"


def test_engine_is_inlined_not_linked():
    src = html()
    assert "ei_engine.js" not in re.findall(r'<script[^>]*src="([^"]*)"', src) or True
    assert 'function assay(' in src, "the claim-checker must be inlined"
    assert not re.search(r'<script[^>]+src=', src), "no external script tags"


def test_measured_numbers_come_from_results_not_invented():
    ci = json.load(open(os.path.join(HERE, "results_ci.json")))
    src = html()
    assert str(ci["C1_calibration"]["ece"]) in src
    assert str(ci["cohort_n"]) in src
    assert ci["C1_calibration"]["user_consequence"] in src
    assert ci["C1_calibration"]["diagnosis"] in src


def test_the_failed_calibration_is_shown_not_buried():
    """We failed this gate. The app must say so on the face of the page."""
    src = html()
    assert "We failed our own test" in src
    assert "did not move the limit" in src or "not changed afterwards" in src


def test_every_tool_keeps_its_limits_panel():
    src = html()
    assert src.count('class="honest"') >= 4, (
        "each tool must keep its 'what this cannot do' panel")
    # normalise whitespace and strip inline markup so the assertions test the
    # sentence a reader sees, not how it happens to be wrapped in the source
    flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", src))
    for phrase in [
        "None of them knows whether something is true",              # home
        "It does not stop an app misusing what you did allow",       # page code
        "It does not make tampering impossible",                     # helm
        "still be wrong",                                            # home
    ]:
        assert phrase in flat, f"missing honesty statement: {phrase!r}"


def test_domain_risk_warning_is_present_for_ordinary_users():
    src = html()
    assert "still be unsafe" in src
    assert "ask a" in src and "qualified person" in src


def test_default_deny_is_stated_in_plain_words():
    src = html()
    assert "Everything else" in src
    assert "refused automatically" in src


def test_navigation_cannot_strand_the_user():
    """Regression lock: setting display='' fell back to the stylesheet's
    display:none, so the back button never appeared and there was no way out of
    a tool except the browser's own controls."""
    src = html()
    assert 'display = id==="home" ? "none" : "inline-block"' in src
    assert "hashchange" in src, "browser Back must work"


def test_dark_theme_tokens_are_defined_in_both_places():
    src = html()
    assert "prefers-color-scheme:dark" in src
    assert ':root[data-theme="dark"]' in src
    assert ':root:not([data-theme="light"])' in src
