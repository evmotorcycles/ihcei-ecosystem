#!/usr/bin/env python3
"""spec.py — Plumb as a language a machine can be asked to write.

WHY THIS FILE EXISTS
====================
Plumb already refuses bad programs. That is enough for a person, who can read
the error and think. It is NOT enough for a model, which needs to know what to
WRITE NEXT. An error that says "unknown statement 'threshold'" ends the
attempt; an error that says "there is no `threshold`; the word is `floor`, and
it takes one number" continues it.

So this file adds two things and no new power:

  GRAMMAR   the whole language on one card, small enough to put in a prompt
  lint()    every problem in a program, each with the exact text that fixes it

THE POINT, WHICH IS NOT SYNTAX
==============================
A model writing Python can emit

    return 0.8

and nothing in the language objects. The number has no provenance, no floor, no
record of what was excluded, and downstream it is indistinguishable from a
measurement. That is not a failure of the model's care. It is that Python has
nowhere to put the obligation.

A model writing Plumb CANNOT do this. `capacity`, `encode` and `decode` are
required by the parser; a verdict without `handles` names no signals; without
`receipt` there is no record. The failure mode is not discouraged, it is
unavailable. That is the whole reason to give a model this language instead of
a style guide asking it to be careful.

WHAT THIS DOES NOT DO
=====================
Plumb cannot check that a field means what its name says. `capacity U from field
"stars"` is well-formed whether or not stars measure capacity for your question.
The language enforces that you SAID where every number came from. It cannot
enforce that you were right, and no version of it will.

A `floor` is a DECLARED PREFERENCE, not a prediction. It is the same kind of
object as a spending cap: writing `floor 0.02` says what you have decided to
stop at, and says nothing about what is likely to go wrong. A hard fidelity gate
that CLAIMED to predict failure was retired from this stack at p = 0.735
(FLOOR_RETIREMENT.md) and must not come back through this door.
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from plumb.plumb import parse, PlumbError   # noqa: E402

VERSION = "plumb-1"

# ── the card. Small on purpose: a language a model must be taught in 2000 words
#    is a language a model will get wrong. ───────────────────────────────────
GRAMMAR = """\
PLUMB — a rule language whose interpreter cannot return an unqualified answer.

  plumb "name" {
    capacity  <alias> from field "<column>"
    encode    <alias> from field "<column>" [inverse]
    decode    <alias> from ratio "<a>"/"<b>"
    floor     <number>
    blind     "<column>"
    independent encode decode
    require   evidence <k> of <n>
    handles
    receipt
  }

REQUIRED, or the program is refused: capacity, encode, decode.
  capacity  what there is to work with. Reach, size, attention.
  encode    can information get IN. `inverse` makes a big backlog a small number.
  decode    can information get OUT and be reused by somebody else.
            `from ratio "a"/"b"` divides one column by another.

OPTIONAL, and each one buys a specific refusal:
  floor       a number YOU choose to stop at. Not a prediction of failure.
  blind       delete a column before evaluation. Not ignore -- delete. Use it on
              anything the subject wrote about itself.
  independent check the two legs are not the same column wearing two names.
  require     abstain unless k of n signals are present.
  handles     the verdict must NAME which signals fired, not just count them.
  receipt     the verdict carries a hash of what produced it.

Comments start with #. Every string is double-quoted.
"""

# every keyword the parser accepts, with the repair text for getting it wrong
KEYWORDS = {
    "capacity": 'capacity U from field "<column>"',
    "encode": 'encode Denc from field "<column>" inverse',
    "decode": 'decode Ddec from ratio "<a>"/"<b>"',
    "floor": "floor 0.02",
    "blind": 'blind "<column>"',
    "independent": "independent encode decode",
    "require": "require evidence 3 of 5",
    "handles": "handles",
    "receipt": "receipt",
}

# words a model reaches for that are not in the language, and what to use
NEAR_MISSES = {
    "threshold": "floor", "limit": "floor", "cutoff": "floor", "min": "floor",
    "exclude": "blind", "ignore": "blind", "drop": "blind", "hide": "blind",
    "input": "encode", "output": "decode", "utility": "capacity",
    "size": "capacity", "reach": "capacity", "score": None, "return": None,
    "assert": None, "if": None, "weight": None, "confidence": None,
}


class Problem:
    """One reason a program is refused, and the text that fixes it.

    `fix` is the whole point. A model handed "unknown statement 'threshold'"
    stops; a model handed "write: floor 0.02" continues.
    """

    def __init__(self, kind, says, fix=None, line=None):
        self.kind, self.says, self.fix, self.line = kind, says, fix, line

    def as_dict(self):
        return {"kind": self.kind, "says": self.says, "fix": self.fix,
                "line": self.line}

    def __repr__(self):
        return f"<{self.kind}: {self.says}>"


def _line_of(src, word):
    for i, ln in enumerate(src.splitlines(), 1):
        if re.search(rf"\b{re.escape(word)}\b", ln.split("#")[0]):
            return i
    return None


def lint(src: str) -> list:
    """Every problem, each with its repair. An empty list means the program
    parses -- NOT that it asks a sensible question."""
    problems = []

    # near-misses first: these produce the most useful repair and the parser
    # would only say "unknown statement"
    body = "\n".join(ln.split("#")[0] for ln in src.splitlines())
    for bad, good in NEAR_MISSES.items():
        if re.search(rf"^\s*{bad}\b", body, re.M):
            problems.append(Problem(
                "not-a-keyword",
                f"`{bad}` is not part of this language.",
                (f"use `{good}` instead — write: {KEYWORDS[good]}" if good else
                 f"there is no `{bad}` in Plumb. A verdict is produced by "
                 f"declaring capacity, encode and decode; it is not returned, "
                 f"asserted or scored."),
                _line_of(src, bad)))

    try:
        prog = parse(src)
    except PlumbError as e:
        msg = str(e)
        fix = None
        m = re.search(r"unknown statement '(\w+)'", msg)
        if m and m.group(1) in NEAR_MISSES:
            g = NEAR_MISSES[m.group(1)]
            fix = f"write: {KEYWORDS[g]}" if g else None
        elif "must declare capacity, encode and decode" in msg:
            fix = ('add the three required lines, for example:\n'
                   '  capacity U from field "stars"\n'
                   '  encode Denc from field "open_issues" inverse\n'
                   '  decode Ddec from ratio "forks"/"stars"')
        elif "unexpected end" in msg:
            fix = "the program is missing its closing `}`"
        problems.append(Problem("parse", msg, fix))
        return problems

    # parsed. Now the obligations that are optional to the parser but are what
    # make a verdict usable by somebody who was not in the room.
    if not prog.handles:
        problems.append(Problem(
            "unnamed-count",
            "This verdict will report how many signals fired and not which. A "
            "reader cannot go and check a number.",
            "add a line: handles"))
    if not prog.receipt:
        problems.append(Problem(
            "no-receipt",
            "Nothing records what produced this verdict.",
            "add a line: receipt"))
    if not prog.blind:
        problems.append(Problem(
            "nothing-blinded",
            "No column is deleted before evaluation, so anything the subject "
            "wrote about itself can reach the answer.",
            'add a line, for example: blind "description"'))
    return problems


def ok(src: str) -> bool:
    return not [p for p in lint(src) if p.kind == "parse"]


def repairs(src: str) -> str:
    """Everything a model needs to fix a program, as plain text to hand back."""
    ps = lint(src)
    if not ps:
        return "This program parses and carries every obligation."
    out = []
    for p in ps:
        line = f" (line {p.line})" if p.line else ""
        out.append(f"- {p.says}{line}" + (f"\n  {p.fix}" if p.fix else ""))
    return "\n".join(out)
