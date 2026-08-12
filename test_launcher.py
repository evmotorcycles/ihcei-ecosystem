#!/usr/bin/env python3
"""index.html — the front door. Every link on it must actually open something.

    python3 -m pytest -q test_launcher.py

A launcher whose links 404 is worse than no launcher: it tells a person the
tools exist and then fails to produce them. This checks the page against the
filesystem, and checks that the words on it are ones an ordinary person uses.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "index.html")

# Words that mean nothing to someone who has not read the source. The front door
# is the one page that has to work for a person who arrived by accident.
JARGON = [
    "epistemolog", "IHCEI", "NERE", "merkle", "VIF", "interposition", "default-deny",
    "proxy", "403", "SHA-256", "regex", "API", "schema", "payload", "assay",
    "falsifiab", "heuristic", "abstain",
]


def html():
    return open(PAGE, encoding="utf-8").read()


def links():
    return re.findall(r'<a[^>]+href="([^"#][^"]*)"', html())


def test_the_page_exists_and_is_self_contained():
    src = html()
    assert not re.search(r'src\s*=\s*"https?://', src), "no external scripts"
    assert not re.search(r'href\s*=\s*"https?://', src), "no external stylesheets or links"
    assert "@import" not in src and "fetch(" not in src


def test_every_link_opens_a_real_file():
    missing = [h for h in links() if not os.path.exists(os.path.join(HERE, h))]
    assert not missing, f"these links point at nothing: {missing}"


def test_every_gui_in_the_repo_is_reachable_from_the_front_door():
    """A screen nobody can find is a screen nobody uses."""
    must_reach = {
        "cairn/desk.html", "cairn/plain.html", "cairn/console.html",
        "novora-suite/suite.html", "novora-suite/desk.html",
        "weir/panel.html", "weir/stop.html",
        "ei-dashboards/dashboards.html", "website/index.html",
    }
    assert must_reach <= set(links()), f"not linked: {sorted(must_reach - set(links()))}"


def test_the_gate_is_marked_as_the_thing_that_can_stop_something():
    src = html()
    assert 'class="card gate"' in src, "Weir must be visually distinct from the advisory tools"
    assert "can actually stop" in src


def test_it_says_what_the_tools_cannot_do_on_the_front_page():
    src = html()
    assert "knows whether something is" in src and "still be wrong" in src, \
        "the limit belongs on the front door, not three clicks in"


def test_no_jargon_reaches_the_front_door():
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html(), flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    found = [w for w in JARGON if re.search(w, text, re.I)]
    assert not found, f"jargon on the launcher: {found}"


def test_the_theme_tokens_are_defined_in_all_three_states():
    src = html()
    for token in ("--ink", "--water", "--held", "--card"):
        assert len(re.findall(re.escape(token) + r":", src)) >= 3, \
            f"{token} is not defined in all three theme states"


def test_targets_are_big_enough_to_tap():
    """Built for 12 to 90. A link the size of a word is not a target."""
    src = html()
    assert re.search(r"a\.card\{[^}]*padding:1\.15rem", src), "cards must be tap-sized"
    assert "focus-visible" in src, "keyboard users need a visible focus ring"
