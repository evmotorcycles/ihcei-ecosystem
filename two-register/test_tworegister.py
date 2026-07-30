"""
test_tworegister.py — locks the Two-Register result: 0/5. The ROUTING claim is dead,
and it died the way the pre-registration said it would.

THE MODEL. Six prior runs converged on two registers. A RECOVERY register holds fixed
claims that survive a shock, so later inflows still reach the holder — this minimises
claimant value shortfall. A CONTAINMENT register holds participation claims that absorb
loss without a hard default event, so it does not propagate — but they EXTINGUISH, which
forecloses recovery. Continuous distribution of inflows runs in both.

THE CLAIM TESTED was not "mixing helps" (the spec calls N1 the weak gate and writes it
off in advance). It was that ROUTING claims to registers by a contagion-risk signal beats
assigning the same share AT RANDOM.

  N2  targeted J 3.7219   random assignment, 20 draws: mean 2.5692, min 1.5690,
      max 4.1542. TARGETED SITS AT THE 90TH PERCENTILE OF RANDOM — 18 of 20 coin-flip
      assignments at the same share BEAT it. (Two random draws are worse, so it is not
      literally last; the claim is that routing is reliably beaten by chance, not that
      it is the single worst possible allocation.)

  N4  AUC(out-degree -> cascade involvement) = 0.4447 — BELOW 0.5. The routing signal
      is mildly ANTI-predictive. Spearman rho vs node size is -0.0333, so it is not a
      size proxy either; it is simply wrong. This explains N2 exactly: routing on an
      anti-predictive signal puts participation on the wrong nodes, and a coin flip
      does better.

This is the FIFTH falsified selection rule in this programme, and the spec predicted it
in writing before the run: "EXPECTED TO FAIL... four selection rules have been falsified,
one of them with an INVERTED sign."

THE MODEL THEREFORE SHIPS WITHOUT THE ROUTING CLAIM — as a fixed policy mix requiring no
scoring apparatus at all. That is cheaper and more robust than what was proposed.

A DEFECT IN MY OWN PRE-REGISTERED OBJECTIVE, DISCLOSED AND NOT REPAIRED. J was locked
with equal 0.5/0.5 weights, but on this substrate the shortfall term spans 18.17 while
the cascade term spans 0.20 — the shortfall term dominates 90x, so J is effectively a
shortfall metric despite its weights. Nothing was re-scored and no threshold was moved.
The consequence is reported honestly: N1, N3 and N5 largely restate "shortfall favours
fixed claims". Under a post-hoc RANGE-BALANCED version of the same two objectives an
interior optimum DOES appear at share 0.60 (J' 0.3167 against 0.5000 at both endpoints).
So "the two-register idea is refuted" would be too strong. What is refuted is ROUTING —
N2 and N4 are same-share comparisons and are untouched by the normaliser.

WHAT THE ABLATION SAYS (under the locked, shortfall-dominated J)
    remove continuous distribution   +194.5048   overwhelmingly the dominant element
    remove recovery register           +6.2620
    remove local pooling               +0.5305
    remove containment register        -2.7219   removal IMPROVES it — dead weight here
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "ed80430a7349da34ab6a76fcc5d60ecd30999cc1f857389b7acbe3a62a94c539"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "tworegister.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_tworegister.json")))


def test_spec_locked_and_predicted_its_own_primary_failure():
    spec = json.load(open(os.path.join(HERE, "prereg", "tworegister_prereg.json")))
    got = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    assert "EXPECTED TO FAIL" in spec["predictions_recorded_in_advance"]["N2"]
    assert "SELECTION RULE" in spec["why_this_specific_gate_is_expected_to_fail"]
    assert "NINTH appearance" in spec["the_simulation_trap_being_avoided_again"]
    # the supplied worked scenario is explicitly excluded from evidence
    assert "ILLUSTRATIVE ARITHMETIC" in spec["an_illustration_is_not_a_measurement"]
    # the two-objective trap had to be closed BEFORE the run
    assert "0.5*(shortfall" in spec["the_two_objective_trap_named_in_advance"]


def test_the_name_is_plain_english_and_borrows_no_tradition():
    r = _r()
    assert r["model_name"] == "Two-Register Settlement Network"
    banned = ("khalifa", "sharia", "riba", "murabaha", "musharakah", "mudarabah",
              "tawarruq", "islamic", "zakat", "salat", "barakah", "deen")
    blob = json.dumps(r).lower()
    for b in banned:
        assert b not in blob, "the model name and results must carry no borrowed prestige"


def test_targeted_routing_is_beaten_by_most_random_assignments():
    """N2, the primary gate. The fifth falsified selection rule."""
    r = _r()
    assert "N2_TARGETED_ROUTING_BEATS_RANDOM_AT_THE_SAME_SHARE" in r["gates_not_met"]
    rc = r["random_control"]
    assert r["targeted_J"] > rc["mean"], "targeted is worse than the random mean"
    assert r["targeted_J"] > rc["min"], "targeted is worse than the best random draw"
    beaten_by = sum(1 for d in rc["draws"] if d < r["targeted_J"])
    assert beaten_by >= 0.75 * len(rc["draws"]), \
        "routing must be beaten by most random draws for the stated finding to hold"
    assert beaten_by == 18 and len(rc["draws"]) == 20, \
        "18 of 20 random assignments beat the targeted rule — the 90th percentile"


def test_the_routing_signal_is_anti_predictive_and_that_explains_it():
    """N4 diagnoses N2: AUC below 0.5, and not merely a size proxy."""
    r = _r()
    assert "N4_the_routing_signal_actually_predicts_CASCADE_and_is_non_circular" \
        in r["gates_not_met"]
    assert r["routing_auc"] < 0.50, "the signal is anti-predictive, not merely weak"
    assert abs(r["routing_rho_vs_size"]) < 0.10, \
        "it is not a restatement of node size — it is simply wrong"


def test_the_objective_defect_is_disclosed_not_repaired():
    r = _r()
    d = r["objective_defect_disclosed"]
    assert d["shortfall_dominance_factor"] > 50, \
        "the locked equal weights are not equal in effect"
    assert "effectively a shortfall metric" in d["note"]
    # the post-hoc sensitivity finds an interior optimum, and changes no gate
    assert 0.0 < d["posthoc_best_share"] < 1.0
    assert "N3_an_interior_optimum_exists" in r["gates_not_met"], \
        "the sensitivity must NOT rescue the gate"


def test_continuous_distribution_dominates_every_other_element():
    """The sleeper component — and it was not in the proposal as a named part."""
    r = _r()
    a = r["ablation"]
    base = r["targeted_J"]
    deltas = {k: v - base for k, v in a.items()}
    assert deltas["continuous_distribution"] > 100, \
        "removing distribution is catastrophic — it is the dominant element"
    assert deltas["continuous_distribution"] > 10 * abs(deltas["recovery_register"])
    assert r["dead_weight"] == ["containment_register"]


def test_no_share_of_containment_beats_pure_recovery_on_the_locked_objective():
    r = _r()
    assert r["best"]["share"] == 0.0
    assert abs(r["J_all_recovery"] - 1.0) < 1e-9, "the normaliser is the all-recovery arm"
    assert r["J_all_containment"] > r["J_all_recovery"]


def test_the_score_is_zero_of_five_and_is_not_softened():
    r = _r()
    assert r["score"] == "0/5"
    assert len(r["gates_not_met"]) == 5
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 5
    assert len([g for g in r["gates"] if g["weight"] == "excluded"]) == 2
