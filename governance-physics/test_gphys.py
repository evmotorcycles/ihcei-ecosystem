"""
test_gphys.py — locks the RT→Governance crossover on physics, and the downgrade of my
own gates that the run forced.

Result: 4/4 EVIDENTIAL gates, with GP3, GP6 and GP7 excluded.

THE FINDING THAT MATTERS MOST — and it went against the framework twice:

  1. GP5. The framework asserts: entangled particles are perfectly correlated, so
     tau_rt = 0, so d = 0. That inference is checkable inside the framework's OWN
     formalism, because tau_rt is realised as commute time — a round-TRIP transport
     quantity. On 1,262 maximally coupled real pairs the MINIMUM emergent distance is
     0.200115 and exactly ZERO pairs have d = 0. The inference is REFUTED on its own
     terms. Correlation is not transport latency, which is the same reason no-signalling
     holds in physics: perfect correlation transmits zero bits.

  2. GP3 / GP6. Both PASSED as pre-registered — slope -0.5000, R^2 = 1.00000000 — and
     both are ALGEBRAIC IDENTITIES, not evidence. Scaling W -> sW gives L -> sL, hence
     L^+ -> L^+/s, hence R -> R/s, hence d = sqrt(R) -> d/sqrt(s), so log d = -0.5 log s
     EXACTLY for every graph. Controls with no relation to the substrates (a random graph
     and a path graph) return the identical -0.5 with R^2 = 1. A test that cannot fail is
     not evidence, so both are excluded from the evidential score.

     This also downgrades the pre-existing physics-agency/lmd H2 claim, which celebrates
     the same -0.5000 slope on seeded graphs as a verified prediction. It is not one.

What genuinely survives is narrower and real: a non-degenerate metric emerges from pure
coupling on a real measured graph (GP1), it is not merely degree relabelled (GP2, rho
+0.8686 — uncomfortably close to the 0.90 boundary), and it is distinguishable from a
degree-preserving null at z = +7.43 (GP4). Those are statements about GRAPHS.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "6a7877dbc9f361027939f3f8f22d84a46d916d5be7a2c499c0264c458e46dd88"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "gphys.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_gphys.json")))


def test_spec_locked_and_scopes_itself_honestly():
    spec = json.load(open(os.path.join(HERE, "prereg", "gphys_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    scope = spec["what_this_does_and_does_not_test"]
    assert "Layer-3" in scope and "none is claimed" in scope
    # the category-error gate must stay written so the framework can lose
    ce = spec["the_category_error_being_tested_head_on"]
    assert "refuted ON ITS OWN TERMS" in ce
    assert "DECLARED EXPECTATION" in ce and "it will be refuted" in ce
    gp5 = spec["gates"]["GP5_maximal_coupling_does_NOT_imply_zero_distance"]
    assert "DECLARED IN ADVANCE" in gp5 and "the framework can lose" in gp5


def test_it_runs_on_the_committed_real_substrates():
    r = _r()
    assert r["spec_sha256_canonical"] == LOCKED
    assert r["pypi_nodes"] == 540 and r["pypi_component"] == 527


def test_the_entanglement_inference_is_refuted_on_its_own_formalism():
    """GP5 is the gate written so the framework loses. It lost. Keep it lost."""
    r = _r()
    assert r["n_coupled_pairs_with_zero_distance"] == 0, \
        "the framework requires d = 0 for maximally coupled pairs; not one pair has it"
    assert r["min_d_among_maximally_coupled"] > 0.0
    assert abs(r["min_d_among_maximally_coupled"] - 0.200115) < 1e-4
    assert r["coupled_pairs"] > 1000


def test_the_minus_half_exponent_is_an_identity_and_is_excluded():
    """My own gates GP3 and GP6 passed and are still not evidence."""
    r = _r()
    ident = set(r["identity_gates_excluded"])
    assert ident == {"GP3_the_scaling_exponent_matches_the_sharp_prediction",
                     "GP6_the_exponent_replicates_on_a_second_real_substrate"}
    for g in r["gates"]:
        if g["gate"] in ident:
            assert g["pass"] is True, "they passed as pre-registered; that stands"
            assert g["weight"] == "identity"
            assert "ALGEBRAIC IDENTITY" in g["detail"]
    # controls unrelated to the substrates return the same answer — that is the proof
    ctrl = r["identity_controls_NOT_A_GATE"]
    for name in ("random", "path"):
        assert abs(ctrl[name]["slope"] - (-0.5)) < 1e-6
        assert abs(ctrl[name]["r2"] - 1.0) < 1e-9
    assert set(r["evidential_gates"]) == {
        "GP1_metric_emerges_on_a_real_graph",
        "GP2_the_metric_is_not_just_degree",
        "GP4_a_degree_preserving_null_destroys_the_structure",
        "GP5_maximal_coupling_does_NOT_imply_zero_distance"}


def test_what_actually_survives_is_reported_without_inflation():
    r = _r()
    assert r["triangle_violations"] == 0 and r["triangle_checks"] >= 200000
    # GP2 passed, but only just — keep the margin visible rather than rounding it up
    assert abs(r["spearman_d_vs_degree"]) < 0.90
    assert abs(r["spearman_d_vs_degree"]) > 0.80, \
        "the metric is SUBSTANTIALLY degree; it clears the gate by ~0.03, not comfortably"
    assert abs(r["null_z"]) > 3.0


def test_no_layer_3_claim_leaked_into_a_scored_gate():
    r = _r()
    assert r["layer3_terms_leaked_into_scored_gates"] == []
    gp7 = [g for g in r["gates"] if g["gate"].startswith("GP7")][0]
    assert gp7["weight"] == "excluded", "a completeness check must never inflate the score"


def test_the_existing_lmd_claim_is_corrected_not_left_standing():
    """The downgrade applies to a claim already committed elsewhere in this repo."""
    p = os.path.join(ROOT, "physics-agency", "lmd", "README.md")
    if os.path.exists(p):
        txt = open(p, errors="ignore").read()
        assert "ALGEBRAIC IDENTITY" in txt or "algebraic identity" in txt, \
            "physics-agency/lmd celebrates the -0.5 slope; it must carry the correction"
