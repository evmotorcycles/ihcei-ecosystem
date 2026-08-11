#!/usr/bin/env python3
"""Guards for the layer split and the plain-language surfaces.

    python3 -m pytest -q test_layers.py

Two things are locked here:
  1. IHCEI and NERE are infrastructure. No browser page may present either as a
     tool a person operates, and neither name may appear in user-facing copy.
  2. The everyday-object GUIs stay free of jargon and of component codenames.
"""
import os
import re

import pytest

ROOT = os.path.dirname(os.path.abspath(__file__))

# every page a person is meant to open
SURFACES = ["cairn/desk.html", "cairn/plain.html",
            "novora-suite/desk.html", "novora-suite/suite.html",
            "website/index.html"]
# the two GUIs rebuilt around everyday objects
DESKS = ["cairn/desk.html", "novora-suite/desk.html"]

JARGON = re.compile(
    r"\b(epistemolog\w*|IHCEI|NERE|merkle|variance inflation|VIF|"
    r"expected calibration error|default-deny|reference-lock|two-hop)\b", re.I)
PRODUCT_CODES = re.compile(r"\b(PAGES|PULSE|WEIGH|LENS|VOICE|MARK|STAND|BRIDGE|RISE)\b")


def visible_text(path):
    """Everything a reader can actually see: strip script, style and tags."""
    s = open(os.path.join(ROOT, path), encoding="utf-8").read()
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<!--[\s\S]*?-->", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s)


def test_definitions_file_exists_and_is_explicit():
    txt = open(os.path.join(ROOT, "LAYERS.md")).read()
    assert "Integrated Human Epistemological Interface" in txt
    assert "Neural Epistemological Reasoning Engine" in txt
    assert txt.count("No — by design") == 2


def test_the_old_expansions_are_gone():
    bad = ["Integrated Human Cognitive Epistemological Interface",
           "Integrated Human-Centric Ethical Intelligence"]
    hits = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in ("node_modules", ".git", "__pycache__", ".pytest_cache")]
        for fn in filenames:
            if not fn.endswith((".md", ".py", ".mjs", ".js", ".html", ".json")):
                continue
            if fn == "test_layers.py":
                continue          # this file names the strings it searches for
            p = os.path.join(dirpath, fn)
            try:
                s = open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for b in bad:
                if b in s:
                    hits.append(os.path.relpath(p, ROOT))
    assert not hits, f"stale expansion still present in: {sorted(set(hits))}"


def test_no_page_presents_the_infrastructure_as_a_tool():
    """A layer that grows a user interface has stopped being a layer."""
    for rel in SURFACES:
        t = visible_text(rel)
        assert not re.search(r"\b(IHCEI|NERE)\b", t), (
            f"{rel} shows an infrastructure name to the user")


@pytest.mark.parametrize("rel", DESKS)
def test_the_everyday_guis_carry_no_jargon(rel):
    t = visible_text(rel)
    m = JARGON.search(t)
    assert not m, f"{rel} shows jargon to an ordinary person: {m.group(0)!r}"


@pytest.mark.parametrize("rel", DESKS)
def test_the_everyday_guis_hide_the_component_codenames(rel):
    t = visible_text(rel)
    m = PRODUCT_CODES.search(t)
    assert not m, f"{rel} shows an internal product code: {m.group(0)!r}"


def test_the_desks_are_named_for_the_object_or_the_worry():
    cairn = visible_text("cairn/desk.html")
    for name in ["The Label", "The Valet Key", "The Dashcam",
                 "The Confidence Meter", "The File Opener", "The Planner"]:
        assert name in cairn, f"missing everyday name: {name}"
    # Novora's nine names are rendered from a JS data array, so the stripped-text
    # view cannot see them. Assert against the file; the browser run confirms they
    # reach the screen.
    novora = open(os.path.join(ROOT, "novora-suite/desk.html"), encoding="utf-8").read()
    for q in ["Is this for real?", "What am I giving up?", "Was that decision fair?",
              "Is this message pressuring me?"]:
        assert q in novora, f"missing everyday question: {q}"


@pytest.mark.parametrize("rel", DESKS)
def test_the_desks_keep_their_limits(rel):
    t = visible_text(rel)
    assert "cannot" in t.lower() or "could not" in t.lower()
    if rel.startswith("cairn"):
        assert "None of them knows whether something is true" in t
        assert "There is no eyesight here" in t
    else:
        assert "screens" in t and "not judges" in t


@pytest.mark.parametrize("rel", DESKS)
def test_the_desks_are_self_contained(rel):
    s = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    for pat in (r'src\s*=\s*"https?://', r'href\s*=\s*"https?://', r"fetch\s*\(",
                r"XMLHttpRequest", r"api\.anthropic\.com"):
        assert not re.search(pat, s), f"{rel} must stay offline; found {pat}"
    assert "{{" not in s


@pytest.mark.parametrize("rel", DESKS)
def test_the_desks_define_all_three_theme_states(rel):
    s = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    assert "prefers-color-scheme:dark" in s
    assert ':root[data-theme="dark"]' in s
    assert ':root:not([data-theme="light"])' in s
