#!/usr/bin/env python3
"""The firewall, enforced.

    python3 -m pytest -q ncu/test_ncu.py

A firewall written only in prose is a promise. These are the four rules from
FIREWALL.md, each as a test that fails if the rule is broken.
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from ncu.metaphor import CANNOT, FUNCTION_FIGURES, NAFS, STAMP, build, render  # noqa: E402

#: philosophy-layer vocabulary. None of it may appear in a measurement module.
NCU_TERMS = ["nafs", "salat", "zakat", "ncu", "aakhirah", "dunya"]

#: the modules that measure things. Layer 1.
LAYER1 = ["smi", "swarm-lmd", "keel", "weir", "cairn", "plumb", "page-code",
          "novora-suite", "hf-cohort", "governance-os"]


def _py_files(rel):
    out = []
    for dirpath, dirnames, files in os.walk(os.path.join(ROOT, rel)):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", "node_modules")]
        for f in files:
            if f.endswith((".py", ".mjs", ".js")):
                out.append(os.path.join(dirpath, f))
    return out


# ---- rule 1: the vocabulary does not migrate down ---------------------------
def test_no_ncu_term_appears_in_any_measurement_module():
    """'they can't move from layer 2 and 1' — checked, not promised."""
    hits = []
    for rel in LAYER1:
        d = os.path.join(ROOT, rel)
        if not os.path.isdir(d):
            continue
        for path in _py_files(rel):
            text = open(path, encoding="utf-8", errors="ignore").read().lower()
            for term in NCU_TERMS:
                if re.search(r"\b" + re.escape(term) + r"\b", text):
                    hits.append(f"{os.path.relpath(path, ROOT)}: {term}")
    assert not hits, "philosophy vocabulary found in measurement code:\n  " + "\n  ".join(hits)


def test_the_terms_really_are_present_here():
    """Otherwise rule 1 would pass by the vocabulary not existing at all."""
    src = open(os.path.join(HERE, "metaphor.py"), encoding="utf-8").read().lower()
    for term in ("nafs", "salat", "zakat"):
        assert term in src


# ---- rule 2: every metaphor cites a real measured number --------------------
@pytest.mark.parametrize("i", range(len(build())))
def test_every_abstraction_cites_a_number_that_is_really_there(i):
    a = build()[i]
    path = os.path.join(ROOT, a.source)
    assert os.path.exists(path), f"{a.source} does not exist"
    data = json.load(open(path, encoding="utf-8"))
    cur = data
    for key in a.field.split("."):
        cur = cur[int(key)] if isinstance(cur, list) else cur[key]
    assert cur == a.value, f"{a.source}::{a.field} moved; the metaphor is quoting a stale number"


def test_an_abstraction_cannot_cite_a_field_that_does_not_exist():
    """The citation check must be capable of failing."""
    from ncu.metaphor import _read
    with pytest.raises(KeyError, match="may not"):
        _read("smi/results_smi.json", "phase2_test.no_such_field")


def test_the_abstractions_draw_on_more_than_one_measurement_source():
    sources = {a.source for a in build()}
    assert len(sources) >= 2, "a single source dressed several ways is not abstraction"


# ---- rule 3: nothing comes back ---------------------------------------------
def test_no_measurement_module_imports_this_package():
    """One direction. If layer 1 could import a metaphor, it could be tuned to it."""
    offenders = []
    for rel in LAYER1:
        if not os.path.isdir(os.path.join(ROOT, rel)):
            continue
        for path in _py_files(rel):
            text = open(path, encoding="utf-8", errors="ignore").read()
            if re.search(r"\b(from|import)\s+ncu\b", text):
                offenders.append(os.path.relpath(path, ROOT))
    assert not offenders, f"layer-1 code imports the metaphor package: {offenders}"


def test_this_package_computes_nothing():
    """It reads numbers and quotes them. No arithmetic, no fitting, no gates.

    Prose is allowed to use operators -- "=" * 78 draws a rule and "a" + "b"
    joins a sentence -- so an operand that is a string constant is not
    arithmetic. Anything else is.
    """
    tree = ast.parse(open(os.path.join(HERE, "metaphor.py"), encoding="utf-8").read())
    def is_text(n):
        return isinstance(n, ast.Constant) and isinstance(n.value, str)
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(
                node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)):
            if not (is_text(node.left) or is_text(node.right)):
                pytest.fail(f"arithmetic on a value in the metaphor package "
                            f"(line {node.lineno})")


def test_it_imports_nothing_from_the_measurement_engines():
    src = open(os.path.join(HERE, "metaphor.py"), encoding="utf-8").read()
    for banned in ("from smi", "import smi", "import jax", "import numpy",
                   "from swarm", "sklearn"):
        assert banned not in src, f"the metaphor package reaches into layer 1: {banned}"


# ---- rule 4: the stamp travels with the data --------------------------------
def test_every_abstraction_carries_the_stamp_in_the_data():
    for a in build():
        assert a.proves == STAMP
        assert a.as_dict()["proves"] == STAMP


def test_every_function_figure_carries_the_stamp_and_a_disclaimer():
    for f in FUNCTION_FIGURES:
        assert f["proves"] == STAMP
        assert f["not"].startswith("This does not define, model, measure or evidence")


def test_the_rendering_says_no_simulation_can_prove_it():
    r = render()
    assert "No dataset and no computer simulation can prove NCU" in r["cannot"]
    assert r["firewall"].endswith("Nothing returns.")


def test_the_stamp_cannot_be_quietly_changed():
    from ncu.metaphor import Abstraction
    a = Abstraction(measured="m", source="s", field="f", value=1,
                    figure="g", illustrates="i", proves="PROVES: SOMETHING")
    with pytest.raises(AssertionError):
        a.as_dict()


# ---- the philosophy layer, as given -----------------------------------------
def test_the_nafs_is_recorded_as_stated():
    assert NAFS["what"] == "a cognitive essence"
    assert NAFS["primary_functions"] == ["Salat", "Zakat"]


def test_the_firewall_document_quotes_the_instruction_verbatim():
    """The instruction said 'don't misquote me'. The quote is checked as text,
    with markdown blockquote markers and line wrapping flattened out, so a
    paraphrase cannot slip through as a reformatting."""
    src = open(os.path.join(HERE, "FIREWALL.md"), encoding="utf-8").read()
    flat = re.sub(r"\s+", " ", re.sub(r"^\s*>\s?", "", src, flags=re.M))
    for quote in (
        "Note NCU terminology are Governce philosophy prior terminology they "
        "can't move from layer 2 and 1",
        "Note their is no Dataset or computer simulation that can prove NCU",
        "I repeat what can be done is abstracting computational telemetry in to "
        "metaphorical representation to illustrate Governce philosophy",
        "Nafs is a cognitive essence it's primary functions are Salat and Zakat",
    ):
        assert quote in flat, f"not quoted as given: {quote[:60]!r}…"
