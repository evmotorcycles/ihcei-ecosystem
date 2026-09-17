"""Commit 5 — the serial-fidelity sentry. P10, P11, P12.

Every prediction asserted here was written into `prereg_sentry.md` and hashed
before `lism_sentry.py` existed. The hash is asserted below.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (ROOT, os.path.join(ROOT, "lintel"), os.path.join(ROOT, "page-code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from lintel import cuts                                            # noqa: E402
from stack.swarm import fixtures                                   # noqa: E402
from stack.swarm.lism_sentry import (  # noqa: E402
    BYPASS_NOTE, FLOOR_FORM, SCOPE, NoRouteError, RetentionError,
    absolute_floor_trip_depth, routes, running_ratios, sentry,
    serial_fidelity, trip_depth)

PREREG_SHA = "9e45f3b272faff4389e1126e6c71034a955fd480a3e112eeed3702d18ec964df"
FLOOR = 0.6


def test_the_preregistration_is_the_one_that_was_locked():
    blob = open(os.path.join(HERE, "prereg_sentry.md"), "rb").read()
    assert hashlib.sha256(blob).hexdigest() == PREREG_SHA


# ============================================================== P10 ==========
def test_p10a_the_ratio_is_an_identity_and_the_prereg_says_so():
    """`E/U = prod D_k` is the definition with U divided out. NOT a result.

    Kept as a harness self-check in the same role Foster's theorem plays in
    `stack/audit/`: true of every chain, so it prefers none of them.
    """
    ds = [0.9, 0.5, 0.7, 0.99]
    assert serial_fidelity(ds) == pytest.approx(
        serial_fidelity(list(reversed(ds))), abs=1e-15)
    text = " ".join(open(os.path.join(HERE, "prereg_sentry.md"),
                         encoding="utf-8").read().split())
    assert "P10a is an IDENTITY, NOT A RESULT" in text


def test_p10b_the_five_hop_chain_hits_the_registered_ratios():
    parts, links, ret = fixtures.chain(6)
    r = sentry(1.0, parts, links, ret, "a0", "a5", FLOOR)
    assert r["route_count"] == 1
    assert r["depth_best"] == 5
    assert r["ratio_best"] == pytest.approx(0.59049, abs=1e-12)
    assert r["ratio_best"] == r["ratio_worst"]
    ds = [0.9] * 5
    for got, want in zip(running_ratios(ds),
                         [0.9, 0.81, 0.729, 0.6561, 0.59049]):
        assert got == pytest.approx(want, abs=1e-12)


def test_p10b_the_ratio_floor_is_blind_to_U_and_the_absolute_floor_is_not():
    """The registered divergence: depth 5 either way at U = 1, 5 against 71 at
    U = 1000. This is the entire argument for `FLOOR_FORM`."""
    ds = [0.9] * 200
    assert trip_depth(ds, FLOOR) == 5
    parts, links, ret = fixtures.chain(6)
    at_1 = sentry(1.0, parts, links, ret, "a0", "a5", FLOOR)
    at_1000 = sentry(1000.0, parts, links, ret, "a0", "a5", FLOOR)
    assert at_1["trips_best"] is at_1000["trips_best"] is True
    assert at_1["ratio_best"] == at_1000["ratio_best"]

    assert absolute_floor_trip_depth(1.0, ds, FLOOR) == 5
    assert absolute_floor_trip_depth(1000.0, ds, FLOOR) == 71
    assert FLOOR_FORM == "ratio-of-U"


def test_the_absolute_floor_form_is_called_by_nothing_that_ships():
    src = open(os.path.join(HERE, "lism_sentry.py"), encoding="utf-8").read()
    body = src.split("def absolute_floor_trip_depth", 1)[1]
    after = body.split("\ndef ", 1)[1] if "\ndef " in body else ""
    assert "absolute_floor_trip_depth(" not in after


def test_min_ratio_is_required_and_has_no_default():
    import inspect
    for fn in (trip_depth, sentry):
        p = inspect.signature(fn).parameters["min_ratio"]
        assert p.default is inspect.Parameter.empty, fn.__name__


# ============================================================== P11 ==========
def test_p11a_subdivision_padding_moves_the_ratio_AGAINST_the_attacker():
    parts, links, ret = fixtures.subdivided_chain(6, hop=2)
    r = sentry(1.0, parts, links, ret, "a0", "a5", FLOOR)
    assert r["route_count"] == 1
    assert r["depth_best"] == 6
    assert r["ratio_best"] == pytest.approx(0.531441, abs=1e-12)
    assert r["ratio_best"] < 0.59049            # fell
    assert r["trips_best"] and r["trips_worst"]


def test_p11b_bypass_padding_DEFEATS_the_best_route_reading():
    """The registered bad news, reported as a defeat and not softened.

    `stack/audit/` measured declared padding beating both structural sensors:
    cuts 3 -> 0, maximum load 0.5714 -> 0.3088. Serial fidelity read on the
    best route is a THIRD sensor the same attack beats -- 0.59049 -> 0.729,
    clearing a floor the unpadded chain breached. Only `ratio_worst` and
    deepest dependence survive it.
    """
    parts, links, ret = fixtures.bypass_chain(6, 1, 4)
    r = sentry(1.0, parts, links, ret, "a0", "a5", FLOOR)
    assert r["route_count"] == 2
    assert r["depth_best"] == 3
    assert r["ratio_best"] == pytest.approx(0.729, abs=1e-12)
    assert r["ratio_best"] > 0.59049            # rose
    assert r["trips_best"] is False             # defeated
    assert r["depth_worst"] == 5
    assert r["ratio_worst"] == pytest.approx(0.59049, abs=1e-12)
    assert r["trips_worst"] is True             # survived


def test_p11_the_two_padding_forms_move_in_OPPOSITE_directions():
    plain = sentry(1.0, *fixtures.chain(6), "a0", "a5", FLOOR)
    sub = sentry(1.0, *fixtures.subdivided_chain(6, hop=2), "a0", "a5", FLOOR)
    byp = sentry(1.0, *fixtures.bypass_chain(6, 1, 4), "a0", "a5", FLOOR)
    assert sub["ratio_best"] < plain["ratio_best"] < byp["ratio_best"]


def test_the_defeat_is_stated_in_the_module_not_only_in_the_suite():
    from stack.swarm import lism_sentry
    doc = " ".join(lism_sentry.__doc__.split())
    assert "cannot see a bypass" in doc
    assert "third sensor the declared-padding attack defeats" in doc
    assert "must never be read alone" in BYPASS_NOTE


# ============================================================== P12 ==========
def test_p12a_structure_trips_where_fidelity_does_not():
    parts, links, ret = fixtures.star(4)
    assert len(cuts(parts, links)) == 1          # the hub
    r = sentry(1.0, parts, links, ret, "leaf0", "leaf1", FLOOR)
    assert r["depth_best"] == 2
    assert r["ratio_best"] == pytest.approx(0.81, abs=1e-12)
    assert r["trips_best"] is False and r["trips_worst"] is False


def test_p12b_fidelity_trips_where_structure_does_not():
    parts, links, ret = fixtures.ring(12)
    assert len(cuts(parts, links)) == 0          # a ring is 2-connected
    r = sentry(1.0, parts, links, ret, "a0", "a6", FLOOR)
    assert r["route_count"] == 2
    assert r["depth_best"] == 6 and r["depth_worst"] == 6
    assert r["ratio_best"] == pytest.approx(0.531441, abs=1e-12)
    assert r["ratio_worst"] == pytest.approx(0.531441, abs=1e-12)
    assert r["trips_best"] is True


def test_p12_the_or_gate_is_earned_because_each_sensor_misses_something():
    star_p, star_l, star_r = fixtures.star(4)
    ring_p, ring_l, ring_r = fixtures.ring(12)
    s = sentry(1.0, star_p, star_l, star_r, "leaf0", "leaf1", FLOOR)
    g = sentry(1.0, ring_p, ring_l, ring_r, "a0", "a6", FLOOR)
    struct = (len(cuts(star_p, star_l)) > 0, len(cuts(ring_p, ring_l)) > 0)
    fidel = (s["trips_best"], g["trips_best"])
    assert struct == (True, False)
    assert fidel == (False, True)
    # neither sensor alone catches both fixtures; the OR does
    assert all(a or b for a, b in zip(struct, fidel))


# ------------------------------------------------- refusals and vocabulary ----
def test_a_disconnected_pair_refuses_and_does_not_return_zero():
    parts = ["a0", "a1", "b0", "b1"]
    links = [("a0", "a1"), ("b0", "b1")]
    ret = {("a0", "a1"): 0.9, ("b0", "b1"): 0.9}
    with pytest.raises(NoRouteError, match="refusal, not a fidelity of zero"):
        sentry(1.0, parts, links, ret, "a0", "b1", FLOOR)


def test_a_retention_outside_the_unit_interval_is_refused():
    for bad in (0.0, -0.1, 1.5):
        with pytest.raises(RetentionError):
            serial_fidelity([0.9, bad])


def test_the_module_borrows_no_physics_vocabulary():
    """`declarations.md` §3: the law is a fidelity product and the word is not
    to appear in the module.

    Two-sided decoy, per CLAUDE.md. Whitespace is collapsed by the matcher
    itself, boundaries exclude path separators as well as word characters, and
    the check is scoped to PRECISION: it demonstrates its false positives and
    claims no recall. This file and `prereg_sentry.md` are exempt BY ROLE --
    a test and a pre-registration must be able to quote what they forbid.
    """
    from stack.governance.matcher import forbid

    banned = ("entropy", "thermodynamic", "thermodynamics", "enthalpy",
              "dissipation", "heat", "temperature")
    src = open(os.path.join(HERE, "lism_sentry.py"), encoding="utf-8").read()
    hits = forbid(src, banned)
    assert hits == [], hits

    # MUST NOT fire: a substring inside a longer word is not the word.
    assert forbid("the reheated cached page; wheat prices; antisymmetry",
                  banned) == []
    # MUST fire: the word itself, even split across a line wrap.
    assert forbid("this is not\nthermodynamic  entropy", banned) == [
        "entropy", "thermodynamic"]


def test_every_reading_carries_its_scope_sentence():
    r = sentry(1.0, *fixtures.chain(6), "a0", "a5", FLOOR)
    assert r["scope"] == SCOPE
    for phrase in ("synthetic bounds only", "no real handoff telemetry",
                   "DOOR1_STATUS.md", "DOOR2_STATUS.md"):
        assert phrase in SCOPE


def test_routes_are_walked_from_the_graph_not_hand_written():
    parts, links, _ = fixtures.bypass_chain(6, 1, 4)
    rs = routes(parts, links, "a0", "a5")
    assert rs == [("a0", "a1", "a4", "a5"),
                  ("a0", "a1", "a2", "a3", "a4", "a5")]
    # Scoped to the EXECUTABLE body. The module docstring must quote 0.59049
    # and 0.729 -- CLAUDE.md requires a tool to state what it cannot do in the
    # same size type as what it does, and the bypass defeat is the headline
    # limitation. The rule being enforced here is that no measured number is
    # hand-written into the arithmetic, not that the numbers go unmentioned.
    src = open(os.path.join(HERE, "lism_sentry.py"), encoding="utf-8").read()
    body = src.split('"""', 2)[2]
    assert "0.59049" not in body and "0.729" not in body
    assert "0.59049" in src, "the limitation must still be stated in the docstring"


def test_no_preregistration_here_locks_a_door_two_prediction():
    """Door 2 stays shut. Asserted by ROLE -- every `prereg_*.md` in this
    package -- not by one hard-coded filename, which would pass the moment a
    second pre-registration appeared under a different name.
    """
    for name in os.listdir(HERE):
        if not (name.startswith("prereg_") and name.endswith(".md")):
            continue
        text = open(os.path.join(HERE, name), encoding="utf-8").read()
        for pid in ("P24", "P25", "P26"):
            assert not re.search(rf"{pid}\s*[-—:]\s*\S", text), (name, pid)
