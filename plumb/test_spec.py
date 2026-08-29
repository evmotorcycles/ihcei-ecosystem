#!/usr/bin/env python3
"""Plumb as a language a machine can be asked to write, and Page Code's audit
run through it.

    python3 -m pytest -q plumb/test_spec.py

The test that matters most is test_a_model_gets_a_repair_not_just_a_refusal.
A language that refuses without saying what to write is a language a model
cannot use, however correct its refusals are.
"""
from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from plumb.spec import GRAMMAR, KEYWORDS, lint, ok, repairs, VERSION  # noqa: E402
from plumb.emit import PROGRAM, audit_as_plumb, records_from_audit    # noqa: E402

GOOD = '''plumb "t" {
  capacity U from field "stars"
  encode Denc from field "open_issues" inverse
  decode Ddec from ratio "forks"/"stars"
  floor 0.02
  blind "description"
  handles
  receipt
}'''


# ─────────────────────────────────── the thing that makes it AI-writable ────
def test_a_model_gets_a_repair_not_just_a_refusal():
    """`threshold` is the word a model reaches for. The parser would only say
    "unknown statement". lint says which word to use and what to write."""
    src = GOOD.replace("floor 0.02", "threshold 0.02")
    ps = lint(src)
    hit = [p for p in ps if p.kind == "not-a-keyword"]
    assert hit, "a near-miss keyword produced no repairable problem"
    assert hit[0].fix and "floor" in hit[0].fix
    assert "floor 0.02" in hit[0].fix
    assert hit[0].line is not None, "a repair with no line number is hard to apply"


def test_the_words_a_model_reaches_for_from_python_are_all_named():
    """`return`, `score`, `assert`, `if` are what a model trained on Python
    writes first. Each gets told why there is no such thing here."""
    for w in ("return", "score", "assert", "if", "weight", "confidence"):
        src = GOOD.replace("floor 0.02", f"{w} 0.5")
        ps = [p for p in lint(src) if p.kind == "not-a-keyword"]
        assert ps, f"{w} produced no guidance"
        assert ps[0].says


def test_a_missing_required_clause_says_exactly_what_to_add():
    src = 'plumb "t" {\n  floor 0.1\n}'
    ps = lint(src)
    parse_problems = [p for p in ps if p.kind == "parse"]
    assert parse_problems
    assert parse_problems[0].fix and "capacity" in parse_problems[0].fix
    assert "encode" in parse_problems[0].fix and "decode" in parse_problems[0].fix


def test_an_unclosed_program_says_so():
    ps = lint('plumb "t" {\n  capacity U from field "a"\n')
    assert any(p.fix and "closing" in p.fix for p in ps)


def test_a_clean_program_lints_clean():
    assert lint(GOOD) == []
    assert ok(GOOD)
    assert "carries every obligation" in repairs(GOOD)


def test_the_obligations_are_reported_even_when_the_program_parses():
    """handles/receipt/blind are optional to the PARSER and are what make a
    verdict usable by somebody who was not in the room, so lint names them."""
    thin = 'plumb "t" {\n  capacity U from field "a"\n' \
           '  encode E from field "b"\n  decode D from ratio "c"/"a"\n}'
    kinds = {p.kind for p in lint(thin)}
    assert kinds == {"unnamed-count", "no-receipt", "nothing-blinded"}
    assert ok(thin), "these are obligations, not syntax errors"


def test_the_grammar_card_is_small_enough_to_put_in_a_prompt():
    assert len(GRAMMAR) < 1800, "a language a model must be taught at length"
    for kw in KEYWORDS:
        assert kw in GRAMMAR, f"{kw} is accepted but not on the card"


def test_the_card_teaches_nothing_the_parser_rejects():
    """Every example on the card must actually parse. A card that teaches a
    program the interpreter refuses is worse than no card."""
    for example in KEYWORDS.values():
        src = 'plumb "t" {\n  capacity U from field "a"\n' \
              '  encode E from field "b"\n  decode D from ratio "c"/"a"\n' \
              f"  {example}\n}}"
        assert ok(src), f"the card teaches an unparseable line: {example}"


# ──────────────────────────────────────── Page Code, running through Plumb ──
@pytest.fixture(scope="module")
def r():
    return audit_as_plumb()


def test_page_codes_own_program_carries_every_obligation(r):
    assert r["lint"] == [], f"Page Code emits a program with problems: {r['lint']}"


def test_popularity_is_physically_deleted_not_ignored(r):
    """38 values stripped across 19 records. `blind` is the difference between
    a field that cannot reach the answer and a field somebody remembered not to
    read."""
    a = r["audit"]
    assert set(a["blind_fields"]) == {"stars", "downloads", "description"}
    assert a["blind_values_stripped"] == 38
    assert a["records"] == 19


def test_a_project_that_does_not_exist_is_not_a_record(r):
    """trig is ABSENT in the audit and must not enter as a row of zeros."""
    names = {v["name"] for v in r["verdicts"]}
    assert "trig" not in names
    assert len(records_from_audit()) == 19


def test_the_two_legs_were_checked_for_independence(r):
    """VIF 4.2587 — under the 5.0 halt, and close enough to it to be worth
    printing rather than assuming."""
    a = r["audit"]
    assert a["independence"] == "VERIFIED_INDEPENDENT"
    assert a["vif"] < 5.0
    assert a["vif"] > 4.0, "if this drifts far the legs stopped being distinct"


def test_no_verdict_is_a_bare_number(r):
    for v in r["verdicts"]:
        assert "verdict" in v
        assert "receipt" in v or v["verdict"] == "ABSTAIN"
        if v["verdict"] != "ABSTAIN":
            assert v.get("confidence") is not None


def test_the_emitted_program_states_its_own_mapping_as_a_choice():
    """capacity = files_scanned is a judgement Plumb cannot check. It is
    written down in the module so a reader can disagree with it."""
    src = open(os.path.join(HERE, "emit.py")).read()
    assert "is a judgement, not a measurement" in src
    assert "CANNOT check" in src


def test_the_floor_is_documented_as_a_preference_not_a_prediction():
    """A hard fidelity gate that CLAIMED to predict failure was retired at
    p = 0.735. It must not return through a program's floor."""
    import re as _re
    for path in ("spec.py", "emit.py"):
        # collapse whitespace first: in emit.py the phrase is line-wrapped as
        # "It is not a\nprediction that", and a literal substring search misses
        # it. Same trap this repository has hit on verbatim page assertions.
        src = _re.sub(r"\s+", " ", open(os.path.join(HERE, path)).read()).lower()
        assert "0.735" in src
        assert "not a prediction" in src


# ────────────────────────────────────────────── the conflict this surfaced ──
def test_plumb_emits_a_word_this_repository_bans():
    """FOUND BY JOINING THE TWO, and recorded rather than silently renamed.

    CLAUDE.md: "`checked`, `verified`, `supported` are past participles and
    claim the errand was done ... the last three are banned."

    Plumb's verdict band is the literal word SUPPORTED. Every row Page Code
    produces through it now carries a word the repository's own vocabulary rule
    forbids.

    NOT FIXED HERE. Renaming a verdict band changes a tested language with 41
    guard tests and is a vocabulary decision, which this repository's rules say
    to ask about first. Asserted as CURRENT BEHAVIOUR so that changing it
    changes this test in the same commit.
    """
    r = audit_as_plumb()
    bands = {v["verdict"] for v in r["verdicts"]}
    assert "SUPPORTED" in bands, "if this passes now, the band was renamed"
    claude = open(os.path.join(ROOT, "CLAUDE.md")).read()
    assert "supported" in claude and "banned" in claude
