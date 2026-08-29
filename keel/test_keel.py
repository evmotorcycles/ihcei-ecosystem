#!/usr/bin/env python3
"""KEEL — the survey, its contract, and the defect running it found.

    python3 -m pytest -q keel/test_keel.py

Predictions locked before run_keel.py existed:

    sha256  5378d4ec236671e7fbc9c80c6ef17faecb6f2da0cee8c96f35e6519109978444

The test that matters most is test_an_ai_plan_and_a_model_family_read_the_same.
If those two ever diverge, the survey has started knowing something about the
subject matter and should be stopped rather than improved.
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

from keel.keel import survey, validate, Refused, CANNOT, GO_CHECK  # noqa: E402

PREREG_SHA256 = "5378d4ec236671e7fbc9c80c6ef17faecb6f2da0cee8c96f35e6519109978444"


@pytest.fixture(scope="module")
def r():
    out = subprocess.run([sys.executable, os.path.join(HERE, "run_keel.py")],
                         capture_output=True, text=True, timeout=900)
    assert out.returncode == 0, out.stderr
    return json.load(open(os.path.join(HERE, "results_keel.json")))


def test_the_predictions_were_locked_before_anything_ran():
    got = hashlib.sha256(open(os.path.join(HERE, "prereg_keel.md"), "rb")
                         .read()).hexdigest()
    assert got == PREREG_SHA256


# ───────────────────────────────────────────────────────── the contract ─────
def test_L3_a_field_with_nowhere_to_go_is_refused_not_ignored(r):
    """Blinding is PHYSICAL. Popularity cannot change a reading because there
    is nowhere to put it -- not because the code politely declines to look."""
    assert r["_contract"]["L3_refuses_unaccepted_field"] is True
    with pytest.raises(Refused):
        validate({"name": "x", "parts": ["a"], "stars": 104122})
    with pytest.raises(Refused):
        validate({"name": "x", "parts": ["a"], "downloads": 2200000})


def test_L4_the_independence_gate_halts_instead_of_reporting_a_smaller_number(r):
    """K2. Four derivatives of one base do not become 'one of four'. The count
    STOPS, because any count would be a number about a thing that is not four.
    """
    c = r["one_fibre"]["counted_twice"]
    assert c["status"] == "HALTED"
    assert c["detail"]["claimed"] == 4
    assert c["detail"]["distinct_origins"] == 1
    assert c["detail"]["the_one_origin"] == "Qwen/Qwen3.6-27B"
    assert abs(c["detail"]["each_settles"] - 0.0625) < 1e-12


def test_L6_a_survey_will_not_read_its_own_output_back_in(r):
    assert r["_contract"]["L6_refuses_its_own_output"] is True


def test_L5_every_readout_carries_its_own_reason(r):
    for key, row in r.items():
        if key.startswith("_"):
            continue
        for kind in ("sole_routes", "counted_twice", "latency"):
            assert row[kind]["says"].strip(), f"{key}/{kind} returned bare"
            assert row[kind]["status"] in ("READ", "ABSTAINED", "HALTED")


def test_the_three_readouts_are_never_fused(r):
    """Structure, repetition and latency are different kinds of quantity. A
    single project-health number would be the mask this stack is against."""
    assert r["_contract"]["L9_no_fused_field"] is True
    blob = json.dumps(r).lower()
    for w in ("health_score", "overall_score", "project_score", "grade",
              "out of 10", "/10"):
        assert w not in blob, f"a fused or graded field appeared: {w}"


# ─────────────────────────────────────────────────────────── the readings ───
def test_the_engines_agree_with_the_earlier_run(r):
    """K1, CONTAMINATED and marked as such -- this was already measured in
    oss-audit RUN A. It is here to confirm two code paths agree, not to
    discover anything."""
    assert r["hf_lineage"]["sole_routes"]["detail"]["single_points"] == \
        ["Qwen/Qwen3.6-27B"]


def test_four_separate_origins_read_as_four(r):
    """K3. The survey is not simply pessimistic: give it genuinely independent
    supports and it says so."""
    c = r["four_fibres"]["counted_twice"]
    assert c["status"] == "READ"
    assert c["detail"]["distinct_origins"] == 4
    assert c["detail"]["rests_on_one_thread"] is False


def test_the_org_structure_reads_two_and_two(r):
    """K4. 22 repositories under 2 organisations: two pieces, two cut points."""
    d = r["orgs"]["sole_routes"]["detail"]
    assert d["pieces"] == 2
    assert sorted(d["single_points"]) == ["QwenLM", "deepseek-ai"]


def test_an_ai_plan_and_a_model_family_read_the_same(r):
    """THE FINDING, and the reason the service is worth anything.

    "Four confident supports in an assistant's reply" and "four open-weight
    models derived from one base" share no word, no domain and no author. The
    survey returns the SAME reading for both -- HALTED, each settling 0.0625 --
    because the arithmetic knows nothing about machine learning or launch plans
    and is measuring the one thing they have in common: four things that look
    independent and are not.

    If these two ever diverge, the survey has begun guessing about subject
    matter and should be stopped rather than improved.
    """
    a = r["assistant_plan"]["counted_twice"]
    b = r["one_fibre"]["counted_twice"]
    assert a["status"] == b["status"] == "HALTED"
    assert a["detail"]["claimed"] == b["detail"]["claimed"] == 4
    assert a["detail"]["each_settles"] == b["detail"]["each_settles"] == 0.0625


# ──────────────────────────────────────────── the prediction against us ─────
def test_the_best_reading_is_the_one_nobody_can_feed(r):
    """K5, registered in advance as a prediction AGAINST the product.

    tau_v is the strongest signal in this stack -- failed 50.6 d vs surviving
    19.8 d, Mann-Whitney p ~ 1e-31 at N = 992. It abstains on every real cohort
    this repository holds, because none of them carries per-item open/close
    timestamps: the tau_v cohort itself stores an AGGREGATE per repository.

    That is a fact about the product's reach, not about any project surveyed,
    and it was registered before the run rather than explained after it.
    """
    assert r["_contract"]["latency_abstained_on_real_cohorts"] is True
    assert r["tauv_cohort"]["_cohort"]["has_per_item_timestamps"] is False
    assert "tau_v" in r["tauv_cohort"]["_cohort"]["fields"]
    assert "opened_at" not in r["tauv_cohort"]["_cohort"]["fields"]


def test_the_engine_does_read_latency_when_it_is_actually_fed(r):
    """K10. On a SYNTHETIC monotone-rising stream the reading is ALERT, so the
    abstentions above are about missing data and not a broken sensor.

    NULL-K4: this says nothing about real projects."""
    assert r["synthetic_rising"]["latency"]["status"] == "READ"
    assert r["_contract"]["synthetic_latency_band"] == "ALERT"


def test_it_declines_more_than_it_answers(r):
    """K6. Abstain rate 0.6667 across 21 readouts, against the L1 gate of 0.10
    measured on the 992 cohort.

    NULL-K3 applies and is the honest half: L2 on that cohort measured whether
    declining actually pays, and found 0.8571 vs 0.8493 with a bootstrap 95% CI
    of [-0.0163, 0.0338] -- INCLUDING ZERO. Abstention is done here because
    answering out of range is dishonest, not because it was shown to help.
    """
    assert r["_contract"]["abstain_rate"] >= 0.10
    assert r["_contract"]["readouts_read"] == 7
    assert r["_contract"]["readouts_total"] == 21


def test_the_key_collision_that_running_it_found():
    """THE DEFECT. The first version of run_keel.py spread each readout's
    `detail` into the same dict as its `status`. The latency detail carries its
    own `status` (OK/WATCH/ALERT), so the nested key silently overwrote the
    readout's -- a READ latency serialised as "ALERT" and the abstain count was
    wrong by one (0.7143 reported, 0.6667 true).

    Same shape as the node-name collision in press.js: two different things
    sharing a key, one vanishing without a word. Detail is now nested.
    """
    src = open(os.path.join(HERE, "run_keel.py")).read()
    assert "**s.sole_routes.detail" not in src
    assert "**s.latency.detail" not in src
    assert '"detail": r.detail' in src


# ──────────────────────────────────────────────────────────── the limits ────
def test_it_says_what_it_cannot_do_and_where_to_go_next(r):
    assert len(CANNOT) >= 4 and len(GO_CHECK) >= 3
    assert any("never about what is true" in c for c in CANNOT)
    assert any("never says a project is healthy" in c for c in CANNOT)
    for g in GO_CHECK:
        assert g.strip().endswith(".")


def test_an_empty_project_abstains_rather_than_reporting_nothing_wrong(r):
    """Empty is not false. A project with no links has no structure to read,
    which is not the same as a structure with nothing wrong with it."""
    s = survey({"name": "nothing yet", "parts": ["one part"]})
    assert s.sole_routes.status == "ABSTAINED"
    assert "not the same as" in s.sole_routes.says
    with pytest.raises(Refused):
        survey({"name": "no parts", "parts": []})
