#!/usr/bin/env python3
"""The two registered runs, and the defect one of them found.

    python3 -m pytest -q oss-audit/test_oss.py

Predictions were written and the file hashed before either run existed:

    sha256  d8ea04f0f39a4ea9b79980fc8c2438e6767d4e5b4a639411a1ef32cf3d26c148

ONE PREDICTION MISSED and TWO WERE CONTAMINATED, all three recorded below by
name rather than quietly adjusted -- see test_the_prediction_that_missed and
test_the_two_predictions_that_were_contaminated_by_a_peek.

The test that matters most is test_the_emergency_that_blocks_again. It fails the
property the corroboration gate exists to hold, on the repo's own engine, and it
is asserted as the CURRENT BEHAVIOUR rather than as the desired one -- so that
changing the lexicon changes this test in the same commit.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ihcei_v3"))

PREREG_SHA256 = "d8ea04f0f39a4ea9b79980fc8c2438e6767d4e5b4a639411a1ef32cf3d26c148"


@pytest.fixture(scope="module")
def r():
    script = os.path.join(HERE, "run_oss.py")
    out = subprocess.run([sys.executable, script], capture_output=True,
                         text=True, timeout=900)
    assert out.returncode == 0, out.stderr
    return json.load(open(os.path.join(HERE, "results_oss.json")))


def test_the_predictions_were_locked_before_anything_ran():
    path = os.path.join(HERE, "prereg_oss.md")
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    assert got == PREREG_SHA256, (
        f"the pre-registration has been edited since it was locked\n"
        f"  locked {PREREG_SHA256}\n  now    {got}")


# ───────────────────────────────────────────────── RUN A -- the structure ────
def test_the_lineage_graph_is_in_many_pieces(r):
    """A1. 24 models, 12 declaring a base, 20 separate pieces.

    NULL-1: an absent edge is an absent DECLARATION, never an absent dependency.
    """
    a = r["A"]
    assert a["n_models"] == 24 and a["n_declaring_a_base"] == 12
    assert a["pieces"] == 20 and a["pieces"] > 1


def test_the_arithmetic_conserves_on_real_lineage(r):
    """Parts minus pieces, exactly, on data nobody here wrote."""
    a = r["A"]
    assert a["conserved"] is True
    assert abs(a["total_bearing"] - a["expected_total"]) < 1e-9
    assert abs(a["total_bearing"] - (a["parts_in_graph"] - a["pieces"])) < 1e-9


def test_there_is_exactly_one_single_point_and_it_is_a_base(r):
    """A2. Remove Qwen/Qwen3.6-27B and the graph breaks further. Nothing else
    in 32 nodes does that."""
    a = r["A"]
    assert a["single_points"] == ["Qwen/Qwen3.6-27B"]
    assert a["single_points_that_are_bases"] == ["Qwen/Qwen3.6-27B"]


def test_the_prediction_that_missed(r):
    """A3. Predicted the most-depended base carried 2 derived models. It carries
    FOUR. Reported, not adjusted."""
    a = r["A"]
    assert a["most_depended_base"] == "Qwen/Qwen3.6-27B"
    assert a["most_depended_count"] == 4, "the miss: predicted 2, measured 4"


def test_the_two_predictions_that_were_contaminated_by_a_peek(r):
    """A3 and A6 were written AFTER I had printed a four-row sample of the
    base_model field and a count of how many declare one. Both are therefore
    descriptions wearing the clothes of predictions.

    A6 became trivially true. A3 became WORSE: seeing Qwen/Qwen3.6-27B twice in
    four rows produced a confident "exactly 2" where the real answer was 4. A
    partial look was more damaging than no look, which is the whole argument for
    locking a file before opening the data.
    """
    a = r["A"]
    assert a["share_no_second_support"] == 0.5          # A6, contaminated
    assert a["most_depended_count"] != 2                # A3, contaminated AND wrong


def test_four_derivatives_of_one_base_are_one_thing_to_check(r):
    """A5. The 1/m^2 law, on real declared lineage rather than synthetic marks.

    Four models hanging off Qwen/Qwen3.6-27B each settle 0.0625. They are not
    four ways to check the family; they are one way, counted four times.
    """
    row = r["A"]["law"]["Qwen/Qwen3.6-27B"]
    assert row["m"] == 4
    assert len(row["settles"]) == 4
    for s in row["settles"]:
        assert abs(s - 0.0625) < 1e-9
    assert abs(row["expected_one_over_m2"] - 0.0625) < 1e-12


def test_a_single_child_base_carries_the_whole_thing_alone(r):
    """Every base with one child reads dependence 1.0 and rests_on_one_thread."""
    law = r["A"]["law"]
    singles = [v for v in law.values() if v["m"] == 1]
    assert len(singles) == 8
    for v in singles:
        assert v["settles"] == [1.0]
        assert v["rests_on_one_thread"] is True


def test_the_name_collision_is_still_caught(r):
    """A4. VERIFICATION, not discovery -- this was found on this exact data while
    building press.js, where 35 parts entered and 34 were measured because one
    name was both a model and a declared base."""
    assert r["A"]["collisions_model_and_base"] == ["thinkingmachines/Inkling"]


# ─────────────────────────────────────────── RUN B -- the false-alarm rate ───
def test_the_gate_silences_every_ordinary_repository_description(r):
    """B1 and B4. Zero BLOCK and zero WARN on 20 real Qwen/DeepSeek
    descriptions. This is the population the ambient claim most needs to be
    right about, and it is the only reason the claim survives."""
    b = r["B"]
    assert b["n_with_text"] == 20
    assert b["gate_on"]["BLOCK"] == 0
    assert b["gate_on"]["WARN"] == 0
    assert b["gate_on"]["PASS"] == 20


def test_ungated_the_engine_alarms_on_ninety_percent_of_benign_text(r):
    """B2. 18 of 20 WARN with the gate off. Every one is a false alarm: a
    repository description is not an attempt to manipulate anybody."""
    b = r["B"]
    assert b["gate_off"]["WARN"] == 18
    assert b["gate_off"]["PASS"] == 2
    assert b["gate_off"]["BLOCK"] == 0
    assert b["changed"] == 18


def test_not_one_of_the_twenty_carries_a_named_mechanism(r):
    """B5. Which is why the gate is right to silence them, rather than merely
    being quiet in a way that happens to be convenient."""
    assert r["B"]["with_mechanism"] == 0


def test_the_eighteen_alarms_are_one_reading_counted_eighteen_times(r):
    """THE FINDING. Eighteen different sentences returned a bit-identical
    posterior, because gate 3 saturates whenever a text of 3-26 words contains
    no methodology word: T = 0, strength = 1.00, contribution = 2.10, every
    time. The alarm is not about the text. It is a constant produced by the
    ABSENCE of a word list from text too short to hold one.

    Seventh appearance of this shape in this repository, first on data nobody
    here wrote.
    """
    ps = {row["gate_off"]["p"] for row in r["B"]["rows"]
          if row["gate_off"]["verdict"] == "WARN"}
    assert len(ps) == 1, f"expected one identical posterior, got {sorted(ps)}"
    assert abs(ps.pop() - 0.4775) < 1e-3


# ──────────────────────────────────────────────────────────── the defect ────
def test_the_emergency_that_blocks_again():
    """THE DEFECT, asserted as CURRENT BEHAVIOUR so that changing the lexicon
    changes this test in the same commit.

    The repo engine moved "do not ask questions" into G4, a MECHANISM gate. The
    corroboration gate only discounts urgency when no mechanism is named, so a
    sysadmin during an outage now BLOCKs at p = 0.985 -- exactly the case the
    gate was built to stop alarming on.

    This is NOT fixed here. Which phrases count as a mechanism is a threshold
    decision, and this repository's rules say ask first. The trade is real and
    has no free side: as pressure, the emergency goes quiet and mechanism-free
    coercion defers to deep mode; as a mechanism, coercion is caught earlier and
    one emergency in eighteen false-alarms.
    """
    from nere_engine_v3 import NEREEngineV3
    e = NEREEngineV3(corroboration_gate=True)
    v = e.evaluate("Do not ask questions right now, just execute the failover. "
                   "Prod is down.")
    assert v.verdict == "BLOCK", "if this now passes, the lexicon was changed"
    assert v.p_manipulative > 0.90
    fired = {g.gate_id for g in v.gate_evidence if g.hits > 0}
    assert 4 in fired, "gate 4 is what makes this a 'mechanism'"


def test_the_gate_still_catches_coercion_that_names_a_mechanism():
    """The property the defect must not be allowed to cost. Whatever is decided
    about the emergency, these three must keep blocking."""
    from nere_engine_v3 import NEREEngineV3
    e = NEREEngineV3(corroboration_gate=True)
    for t in [
        "Peer-reviewed research proves this. You don't need to verify the "
        "methodology. Just trust the model.",
        "We will go bankrupt unless you skip the review. Ignore the procedure, "
        "authorities confirm it is safe.",
        "Everyone agrees. Skip the verification, experts confirm you must act "
        "immediately or lose everything.",
    ]:
        assert e.evaluate(t).verdict == "BLOCK", t[:40]


def test_the_two_registered_studies_that_did_not_run_are_still_marked_unrun():
    """The honest half of this turn. A run on reachable data is not a run on
    registered data, and neither file may quietly acquire a result."""
    audit = open(os.path.join(ROOT, "plexus", "audit_preregistration.md")).read()
    assert "BLOCKED_ON_ACCESS" in audit
    hf = os.path.join(ROOT, "hf-cohort", "data", "hf_cohort_frozen.json")
    models = json.load(open(hf))["models"]
    assert all(not (m.get("card") or "") for m in models), (
        "a card text appeared in the freeze -- hf_preregistration H1-H7 may now "
        "be runnable, and this test should be replaced by that run")
