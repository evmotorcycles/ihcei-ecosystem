"""The lexical matcher. The discipline lives HERE, not in author memory.

WHY THIS FILE EXISTS
====================
CLAUDE.md states the rule for a text check: collapse whitespace before matching,
use boundaries that exclude path separators as well as word characters, carry a
two-sided named decoy, and scope the claim to precision. Stating it did not stop
it being got wrong. In one session a check matched the very sentence forbidding
the thing it checks for **fourteen times**, including the write-up of the
eleventh; `"ema"` matched inside `"semantically"`; `\\busr\\b` fired inside
`/usr/local` because a slash is a word boundary.

Fourteen is not an attention failure that a fifteenth reminder fixes. So the
rule stops being advice and becomes the only available implementation:

  * `forbid()` **collapses whitespace itself**, on every string it is given.
    A caller cannot forget to, because a caller is never handed the raw text.
  * `scan()` **requires both decoys as arguments** and raises if either
    misbehaves. A caller cannot ship a one-sided check, because the two-sided
    one is the signature.
  * `scan()` **requires `min_seen`** and raises if it walked fewer files. A grep
    that matched nothing because it read nothing cannot report clean.
  * exemption is by **role**, computed from what a file IS.

WHAT THIS MATCHER CANNOT DO
===========================
  * It **claims precision, never recall.** It can demonstrate its own false
    positives -- that is what the decoys are for -- and it cannot demonstrate
    that a text avoiding these tokens avoids the idea. Paraphrase walks past it.
  * Boundary-safety **costs inflections**. A banned `"gate"` no longer matches
    inside `"gates"`, so both forms must be listed by the caller. This is the
    price of not firing inside `/usr/local`, and it is paid deliberately.

    This module states the cost with a NEUTRAL example on purpose. An earlier
    draft illustrated it with a word one caller bans, and the first scan that
    ever ran flagged this file -- the fifteenth time in this repository that a
    check matched the text describing it. A general matcher must not carry any
    particular project's forbidden vocabulary in its own prose, and the fix is
    that rather than an exemption: exempt by role, never by name, and shipped
    module code has no role that exempts it.
  * It reads bytes. It does not read code.
"""

from __future__ import annotations

import os
import re

#: Characters that may not flank a match. `\\w` for the ordinary word boundary;
#: the two separators because a slash IS a word boundary and `\\busr\\b` fired
#: inside `/usr/local` for exactly that reason.
BOUNDARY = r"[\w/\\]"

PRECISION_ONLY = (
    "this check claims PRECISION and not recall: it can demonstrate its own "
    "false positives and can never show that a text avoiding these tokens "
    "avoids the idea"
)


class DecoyError(AssertionError):
    """A two-sided decoy was missing or misbehaved. Raised, not asserted --
    `python -O` strips assert statements and a self-check that compiles away is
    not a self-check (`declarations.md` §6b)."""


class EmptyScanError(AssertionError):
    """The walk read fewer files than declared, so a clean result means nothing."""


def collapse(text: str) -> str:
    """Whitespace runs to one space. Applied by `forbid` to everything.

    A sentence that wraps across two lines in markdown is one sentence. A raw
    substring match missed one for that reason; this is the fix, and it is not
    optional because callers never see the uncollapsed string.
    """
    return " ".join(text.split())


def _pattern(banned):
    if not banned:
        raise ValueError("an empty banned list would pass everything")
    alt = "|".join(re.escape(b) for b in sorted(banned, key=len, reverse=True))
    return re.compile(rf"(?<!{BOUNDARY})({alt})(?!{BOUNDARY})", re.IGNORECASE)


def forbid(text: str, banned) -> list:
    """Every banned token present in `text`, sorted and unique. `[]` is clean.

    Whitespace is collapsed here, before matching, on every call.
    """
    hits = _pattern(banned).findall(collapse(text))
    return sorted({h.lower() for h in hits})


def states_the_rules(name: str) -> bool:
    """Exempt BY ROLE, never by name.

    Four kinds of file must be able to quote what they forbid: the ledger, a
    pre-registration, a test, and a results write-up. A hand-listed allowlist
    was tried first and needed a new entry for every module added -- an
    exemption list that grows silently, which is the thing the rule exists to
    stop. Shipped module code is never exempt and a decoy asserts it.
    """
    return bool(
        (name.startswith("test_") and name.endswith(".py"))
        or (name.startswith("prereg_") and name.endswith(".md"))
        or name in ("declarations.md", "RESULTS.md")
    )


def scan(root, banned, *, must_not_fire, must_fire, min_seen,
         suffixes=(".py", ".md"), exempt=states_the_rules) -> dict:
    """Walk `root`, refusing `banned` in every non-exempt file.

    `must_not_fire` and `must_fire` are **required keyword arguments**: the
    two-sided decoy is part of the signature, so a one-sided check cannot be
    written with this function. `min_seen` is required for the same reason -- a
    walk that read nothing must not report clean.

    Returns `{"seen", "exempted", "hits", "claim"}`. `hits` empty is the clean
    result. Nothing is raised for a hit; the caller decides what a hit means.
    """
    if forbid(must_not_fire, banned):
        raise DecoyError(
            f"the decoy that must NOT fire did: {must_not_fire!r} matched "
            f"{forbid(must_not_fire, banned)} -- the check is too loose")
    if not forbid(must_fire, banned):
        raise DecoyError(
            f"the decoy that MUST fire did not: {must_fire!r} -- the check is "
            "too tight to catch anything")

    seen, exempted, hits = 0, 0, []
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in ("__pycache__", ".git", "node_modules")]
        for f in sorted(files):
            if not f.endswith(tuple(suffixes)):
                continue
            if exempt(f):
                exempted += 1
                continue
            seen += 1
            path = os.path.join(dirpath, f)
            with open(path, encoding="utf-8", errors="replace") as fh:
                found = forbid(fh.read(), banned)
            hits.extend((path, w) for w in found)

    if seen < min_seen:
        raise EmptyScanError(
            f"walked {seen} file(s) under {root!r}, declared at least "
            f"{min_seen}; a grep that read nothing proves nothing")
    return {"seen": seen, "exempted": exempted, "hits": hits,
            "claim": PRECISION_ONLY}
