"""
test_mesh.py — locks the Novora Sovereign Mesh result: 1/4, and the ablation is why.

The mesh was the "new paradigm": remove the fidelity screen entirely, admit openly, and
manage risk through contract structure and staged telemetry-driven de-risking instead.
The pre-registration committed in advance to ABLATION — remove each component, measure
the loss, and name anything that earns nothing as dead weight.

It earned 1 of 4 scored gates, and the ablation is the reason the result is worth having:

  NP1 FAILED  mesh -285,750 vs conventional -133,040.
  NP2 FAILED  only 3 of 7 components earn their place.
  NP3 FAILED  abstention delta exactly 0.
  NP4 PASSED  staged escalation beat a binary exit by +32,850.

THE FINDING THAT HURTS MOST, and the one that matters:
  Ablating OPEN ADMISSION — i.e. putting the prestige screen BACK — improves capital by
  +211,095, larger than every other component's contribution combined. On this substrate
  capacity screening is the single most valuable lever, and the paradigm's central move
  (removing the screen) is its most expensive feature. That is reported at full strength.

TWO MISSES HAVE MECHANICAL EXPLANATIONS, recorded as post-hoc and never as rescues:
  NP3 — all 126 imputed rows carry tau_v = 30.00 exactly, the imputation constant, and
        0 of them can cross stage 1. Acting and abstaining are identical BY CONSTRUCTION
        of the imputation. This cohort cannot test the abstention rule: untestable-here,
        not refuted. The gate still counts as NOT MET.
  NP1 — confounded twice: the conventional book holds 496 contracts to the mesh's 992 and
        has a 51.2% default rate against 75.6%. Per contract it is -268.23 vs -288.05 —
        still worse, by 7% rather than 2.1x. The gate still counts as NOT MET.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "ed71c3fc7aeae48df66946d49a96e7b0deaaa9cef19da6aa943ff8fd11dd781e"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "mesh.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_mesh.json")))


def test_spec_locked_and_committed_to_ablation_in_advance():
    spec = json.load(open(os.path.join(HERE, "prereg", "mesh_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    why = spec["why_ablation_is_the_only_honest_test_of_an_integrated_system"]
    assert "dead weight" in why and "MUST be reported as dead weight" in why
    assert "NOT a claim about credit markets" in spec["data"]["declared_substrate_limitation"]


def test_it_runs_on_the_verified_cohort():
    r = _r()
    rec = json.load(open(os.path.join(ROOT, "cohort-audit", "results_992_recovery.json")))
    assert r["csv_sha256"] == rec["csv_sha256"]
    assert r["N"] == 992 and r["defaults"] == 750 and r["imputed_rows"] == 126


def test_the_three_failures_stand():
    r = _r()
    assert len(r["gates_not_met"]) == 3, "the run is 1/4; it must not be re-scored"
    for g in ("NP1_the_mesh_beats_the_conventional_baseline",
              "NP2_every_component_earns_its_place",
              "NP3_abstention_on_imputed_telemetry_pays"):
        assert g in r["gates_not_met"], "%s was rescued after the fact" % g
    assert r["mesh_capital"] < r["conventional_capital"]


def test_removing_the_screen_was_the_most_expensive_choice():
    """The paradigm's central move is its worst feature. Keep that visible."""
    r = _r()
    abl = {a["component"]: a for a in r["ablations"]}
    adm = abl["admission"]
    assert adm["earns_its_place"] is False
    assert adm["delta"] > 200000, \
        "putting the prestige screen back gains ~211k — larger than every other " \
        "component combined; this must not be softened"
    others = [a["delta"] for c, a in abl.items() if c != "admission"]
    assert adm["delta"] > abs(sum(others)), "state the comparison, do not bury it"


def test_dead_weight_is_named_not_quietly_retained():
    r = _r()
    assert set(r["dead_weight"]) == {"admission", "reserve", "abstention", "audit_ledger"}
    # the three that do earn their place, with their measured contributions
    abl = {a["component"]: a for a in r["ablations"]}
    for c in ("structure", "telemetry", "staged_response"):
        assert abl[c]["earns_its_place"] is True
        assert abl[c]["delta"] < 0, "removing it must strictly hurt"


def test_the_only_pass_is_real_and_costed():
    r = _r()
    assert r["binary_exit_capital"] < r["mesh_capital"]
    assert (r["mesh_capital"] - r["binary_exit_capital"]) > 30000
    assert r["mesh_staged"] == 186, \
        "the middle stage charged a real cost on 186 reductions; keep the count"


def test_posthoc_explanations_are_labelled_and_never_rescue_a_gate():
    """Both explanations are true AND both gates still count as failed."""
    r = _r()
    ph = r["posthoc_NOT_GATES"]
    # NP3: the imputation is a single constant that can never trigger a stage
    assert ph["imputed_tau_v_distinct_values"] == [30.0]
    assert ph["imputed_rows_able_to_trigger_stage1"] == 0
    assert r["abstain_capital"] == r["act_on_imputed_capital"]
    assert "NP3_abstention_on_imputed_telemetry_pays" in r["gates_not_met"]
    # NP1: the baseline is smaller AND genuinely healthier
    assert ph["conventional_book_size"] == 496
    assert ph["conventional_default_rate"] < 0.55 < (r["defaults"] / r["N"])
    assert ph["mesh_capital_per_contract"] < ph["conventional_capital_per_contract"], \
        "the mesh is worse per contract too — the confound narrows it, it does not flip it"
    assert "NP1_the_mesh_beats_the_conventional_baseline" in r["gates_not_met"]


def test_non_falsifiable_gates_are_excluded_from_the_score():
    r = _r()
    excluded = {g["gate"] for g in r["gates"] if g["weight"] == "excluded"}
    assert len(excluded) == 3, "NP5, NP6 and NP7 cannot fail and must not inflate the score"
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 4
    # full reserve's benefit is real but invisible to a capital metric — say so
    assert r["depositor_shortfall_full_reserve"] == 0
    assert r["depositor_shortfall_levered"] > 100000


def test_the_audit_ledger_actually_chains():
    r = _r()
    assert r["ledger_entries"] == 992 and len(r["ledger_head"]) == 64
