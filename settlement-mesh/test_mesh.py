"""
test_mesh.py — locks the Reciprocal Settlement Mesh result: 2/5, and it lost where it counts.

The mesh was built from scratch because the legacy datasets contain no such system. It was
then tested by the only methods available before deployment: invariant proof, adversarial
attack, shared-shock replay against a centralised comparator, and ablation.

WHAT HELD
  M1  the full-reserve invariant survived 200,000 randomised operations including
      deliberate over-issuance attempts — zero states where pledged exceeded reserves.
      This is a theorem about the mechanism, not an observation about the world.
  M2  all six named attacks blocked, with zero false positives on 50 honest issuances.

WHAT FAILED, and these are real
  M3  the mesh recorded 2,458 failed settlements against the centralised comparator's 0,
      on the identical 4,886-shock sequence with no architecture-specific constants.
      POOLING WINS routine shock absorption. A centralised book holds every issuer's
      reserves and can meet obligations no individual node could. The mesh has no pool
      and genuinely loses this contest.
  M4  contagion: 2.95 counterparties impaired per node failure, against 0.00.
  M5  the VERIFIER QUORUM is DEAD WEIGHT — removing it changes failed settlements by
      exactly 0 while costing 3.20 independent verifications per claim. The full-reserve
      check at issuance already catches everything the quorum was meant to catch.

THREE HARNESS DEFECTS WERE FOUND AND FIXED, each disclosed in the source:
  * the cycle attack was written as a disjunction whose second term was an honest,
    fully-backed issuance by a different solvent node — it "succeeded" for reasons
    unrelated to the attack;
  * the contagion metric compared obligations to reserves AFTER settle() had already
    written them down, returning 0.00 for both arms and measuring nothing;
  * the terminology scan was scanning the file that defines the banned-term list.
Fixing a broken measurement is not moving a threshold. No fix converted a mechanism
failure into a pass: M3, M4 and M5 failed before the fixes and fail after them.

DECLARED LIMITATION, recorded as a post-hoc and never as a gate: M3 counts ROUTINE failed
settlements, and no locked gate tests catastrophic centre failure. Single-point dependence
is 0.0086 for the mesh against 1.0000 for the centralised arm. That asymmetry is real and
is exactly what the locked metric cannot see — but it is NOT a result here, because no
test of it was pre-registered. Building it is the named next step.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "a5f49a6e4a6728f64f3668cc40925d472f930da3e929eedef36f8b1769c9b436"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "mesh.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_mesh.json")))


def test_spec_locked_and_refuses_the_simulation_trap_in_writing():
    spec = json.load(open(os.path.join(HERE, "prereg", "mesh_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    trap = spec["the_simulation_trap_being_avoided"]
    assert "fifth appearance" in trap and "exp(-0.005*U)" in trap
    assert "NO architecture-specific constant may differ between arms" in trap
    honest = spec["what_can_honestly_be_established_about_a_system_that_does_not_yet_exist"]
    assert "Not empirical support" in honest


def test_the_shock_source_is_real_and_committed():
    r = _r()
    assert r["n_shocks"] == 4886, "the 4,886 real recorded debits, not a fitted distribution"
    rel = "data/colab-audit/banking_dataset.xlsx"
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                             cwd=ROOT, capture_output=True, text=True)
    assert tracked.returncode == 0


def test_the_invariant_and_the_attacks_held():
    r = _r()
    assert r["M1_operations"] >= 200000 and r["M1_violations"] == 0
    assert all(a["blocked"] for a in r["M2_attacks"]), \
        "every named attack must be blocked; a single miss fails the gate"
    assert len(r["M2_attacks"]) == 6
    assert r["M2_honest_success"] == 50, "and zero false positives on honest issuance"


def test_pooling_beat_the_mesh_and_that_stands():
    """M3 is the result the design most needs to hear. Do not soften it."""
    r = _r()
    assert "M3_shared_shock_replay" in r["gates_not_met"]
    assert r["M3_mesh_failed"] > r["M3_central_failed"]
    assert r["M3_mesh_failed"] == 2458 and r["M3_central_failed"] == 0
    assert "M4_contagion_is_bounded" in r["gates_not_met"]
    assert r["M4_mesh_contagion"] > r["M4_central_contagion"]


def test_the_verifier_quorum_is_named_as_dead_weight():
    r = _r()
    assert r["M5_dead_weight"] == ["verifier_quorum"]
    abl = {a["component"]: a for a in r["M5_ablation"]}
    assert abl["verifier_quorum"]["delta"] == 0, \
        "removing it changes nothing — while costing 3.20 verifications per claim"
    assert abl["verifier_quorum"]["earns_its_place"] is False
    # the two that do earn their place, with their measured contributions
    assert abl["multilateral_netting"]["delta"] > 0
    assert abl["latency_covenant"]["delta"] > 0
    assert r["M6_verifications_per_claim"] > 3.0, "the dead component is not even free"


def test_no_architecture_specific_constant_differs():
    """The gate the published JAX cell would fail."""
    r = _r()
    assert r["M7_differing_constants"] == {}


def test_the_terminology_directive_is_enforced():
    r = _r()
    assert r["M8_banned_terms_found"] == []


def test_the_posthoc_limitation_is_recorded_and_never_scored():
    r = _r()
    ph = r["posthoc_NOT_A_GATE"]
    assert ph["mesh_max_single_point_dependence"] < 0.05
    assert ph["central_max_single_point_dependence"] == 1.0
    assert "NOT claimed here" in ph["note"]
    # it must not have been promoted into the gate list
    assert all(not g["gate"].lower().startswith("posthoc") for g in r["gates"])
    assert len(r["gates_not_met"]) == 3, "the run is 2/5; it must not be re-scored"


def test_non_falsifiable_gates_are_excluded_from_the_score():
    r = _r()
    excluded = {g["gate"] for g in r["gates"] if g["weight"] == "excluded"}
    assert len(excluded) == 3, "M6, M7 and M8 cannot fail and must not inflate the score"
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 5
