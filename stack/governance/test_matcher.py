"""The matcher's own suite. Every failure this rule was earned by, as a case.

Each test below corresponds to a real defect committed in this repository. They
are kept as cases rather than as prose so that reintroducing one fails a build
instead of needing to be remembered.
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stack.governance.matcher import (  # noqa: E402
    BOUNDARY, PRECISION_ONLY, DecoyError, EmptyScanError, collapse, forbid,
    scan, states_the_rules)


# ------------------------------------------- the defect: word-in-word ----
def test_a_banned_token_does_not_fire_inside_a_longer_word():
    """`"ema"` matched inside `"semantically"`."""
    assert forbid("this is semantically fine", ["ema"]) == []
    assert forbid("the ema of the loss", ["ema"]) == ["ema"]


def test_a_banned_token_does_not_fire_inside_a_path():
    """`\\busr\\b` fired inside `/usr/local`, because a slash IS a word boundary."""
    assert forbid("the /usr/local path, usr/bin, and usher", ["usr"]) == []
    assert forbid("a bare usr token", ["usr"]) == ["usr"]
    assert "/" in BOUNDARY and "\\\\" in BOUNDARY.replace("\\w", "")


# ------------------------------------ the defect: the sentence that wrapped ----
def test_the_matcher_collapses_whitespace_itself_and_the_caller_cannot_forget():
    """A sentence wrapping across two lines in markdown is one sentence.

    A raw substring match missed one exactly this way. The fix is not that
    authors remember to collapse -- it is that `forbid` is the only entry point
    and it collapses every string it is handed.
    """
    wrapped = "this is not\n    thermodynamic\n    entropy at all"
    assert collapse(wrapped) == "this is not thermodynamic entropy at all"
    assert forbid(wrapped, ["thermodynamic entropy"]) == ["thermodynamic entropy"]
    assert forbid(wrapped, ["entropy", "thermodynamic"]) == [
        "entropy", "thermodynamic"]


# --------------------------------------------- the cost, stated not hidden ----
def test_boundary_safety_costs_inflections_and_the_module_says_so():
    """A banned `"gate"` no longer matches inside `"gates"`.

    That is a real loss of recall bought to stop firing inside `/usr/local`.
    Both forms must be listed by the caller, and the module states the trade
    rather than leaving it to be discovered.
    """
    assert forbid("two gates and a floor", ["gate"]) == []
    assert forbid("two gates and a floor", ["gate", "gates"]) == ["gates"]
    from stack.governance import matcher
    doc = collapse(matcher.__doc__)
    assert "costs inflections" in doc
    assert "claims precision, never recall" in doc


def test_the_matcher_does_not_carry_a_callers_banned_vocabulary_in_its_prose():
    """Instance fifteen, kept as a case.

    The first scan ever run with this module flagged the module itself: its
    docstring illustrated the inflection cost with a word one caller bans. The
    fix was to neutralise the example, NOT to exempt the file -- shipped module
    code has no role that exempts it, and an allowlist entry here would have
    been the exemption-by-name this repository keeps proving it cannot afford.
    """
    from stack.governance import matcher
    src = open(matcher.__file__, encoding="utf-8").read()
    assert forbid(src, ["thermodynamic", "thermodynamics", "entropy"]) == []
    assert not states_the_rules(os.path.basename(matcher.__file__))
    assert "NEUTRAL example on purpose" in collapse(matcher.__doc__)


def test_the_claim_is_scoped_to_precision():
    assert "PRECISION and not recall" in PRECISION_ONLY
    assert "can never show" in PRECISION_ONLY


# ---------------------------------------- the two-sided decoy is mechanism ----
def test_scan_refuses_a_check_whose_loose_decoy_fires():
    with pytest.raises(DecoyError, match="too loose"):
        scan(HERE, ["usr"], must_not_fire="a bare usr token",
             must_fire="a bare usr token", min_seen=1)


def test_scan_refuses_a_check_too_tight_to_catch_anything():
    with pytest.raises(DecoyError, match="too tight"):
        scan(HERE, ["usr"], must_not_fire="/usr/local",
             must_fire="/usr/local", min_seen=1)


def test_the_decoys_are_required_keyword_arguments_not_a_convention():
    """A one-sided check cannot be written with this function."""
    import inspect
    sig = inspect.signature(scan)
    for name in ("must_not_fire", "must_fire", "min_seen"):
        p = sig.parameters[name]
        assert p.kind is inspect.Parameter.KEYWORD_ONLY, name
        assert p.default is inspect.Parameter.empty, name


def test_a_walk_that_read_nothing_cannot_report_clean():
    with pytest.raises(EmptyScanError, match="proves nothing"):
        scan(HERE, ["zzz" + "notpresent"], must_not_fire="clean text",
             must_fire="a zzznotpresent token", min_seen=10_000)


# ------------------------------------------------------ exempt by ROLE ----
def test_the_four_roles_are_exempt_and_shipped_code_is_not():
    for name in ("test_matcher.py", "prereg_sentry.md", "declarations.md",
                 "RESULTS.md"):
        assert states_the_rules(name), name
    for decoy in ("lism_sentry.py", "matcher.py", "adg_cfe.py", "lintel.py",
                  "ARCHITECTURE.md", "DOOR1_STATUS.md"):
        assert not states_the_rules(decoy), f"shipped file {decoy} must not be exempt"


def test_the_exemption_is_computed_from_the_role_not_from_a_list():
    """A file that did not exist when this was written is still classified."""
    assert states_the_rules("test_a_module_invented_tomorrow.py")
    assert states_the_rules("prereg_a_study_not_yet_designed.md")
    assert not states_the_rules("a_module_invented_tomorrow.py")


def test_scan_reports_what_it_exempted_so_the_hole_is_visible():
    out = scan(os.path.join(ROOT, "stack"), ["zzz" + "absent"],
               must_not_fire="clean text", must_fire="a zzzabsent token",
               min_seen=5)
    assert out["hits"] == []
    assert out["seen"] >= 5 and out["exempted"] >= 1
    assert out["claim"] == PRECISION_ONLY


def test_an_empty_banned_list_is_refused_rather_than_passing_everything():
    with pytest.raises(ValueError, match="pass everything"):
        forbid("anything at all", [])
