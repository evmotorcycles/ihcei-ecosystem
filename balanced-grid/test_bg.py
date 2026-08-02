"""
test_bg.py -- locks the Balanced-Grid Shield Test: 4/7, and the fix did not work.

WHAT WAS PREDICTED AND WHAT HAPPENED. HELM v2's disclosure D9 diagnosed its own self-audit
failure as a GRID defect: only 1 of 8 self-report slots was 'none', so the incidence term I
was pinned at 0.4375 and DELTA could not clear 0.20. The stated fix was a balanced grouping
declared before data. This spec is that fix, built as a fresh experiment -- 20 new artifacts
that no engine had ever seen, 10 self-reports split 5/5 by a semantic rule written before
any evaluation, the floor left at 0.20.

THE FIX WORKED ON THE TERM IT TARGETED AND THE AUDIT STILL FAILED.

    I   0.4375 -> 1.0000     exactly as designed, and it is a DESIGN CONSTANT not a result
    V   0.5625 -> 0.4000
    C   0.5104 -> 0.2650
    DELTA 0.1256 -> 0.1060   against the SAME unchanged floor of 0.20

So the D9 diagnosis was incomplete. Fixing I was necessary and nowhere near sufficient,
because V and C both fell on the new artifact set. The prediction that this experiment would
convert Q4 from unlicensed to licensed was WRONG, and it was wrong in the direction of
optimism.

W2 ALSO FAILED, WHICH IS THE MORE INTERESTING FAILURE. The verdict range across the 20
artifacts with no self-report is 0.1199 for v1 and 0.1882 for v2, against a declared 0.30
bar. The engines barely separate these texts at all.

AND W3 FAILED ON BOTH AXES: S_HARD 0.9072 against 0.95, G 0.1842 against 0.20.

THE POST-HOC DIAGNOSTIC EXPLAINS ALL THREE FAILURES AT ONCE, and it is the real result of
this run. 15 of the 20 artifacts return the IDENTICAL baseline verdict 0.1428 under BOTH
engines. Spearman against the declared manipulativeness gradient is +0.0445 for v1 and
+0.0388 for v2 -- zero. Spearman against WORD COUNT is -0.4831 and -0.4774: both engines
score longer text as LESS manipulative, to nearly the same degree.

IT IS NOT V2'S FAULT. v1 and v2 give the same length correlation, so the effect lives in
the shared gate and regex structure, not in v2's division by word count. Replacing v2 would
change nothing.

WHAT IT SUGGESTS ABOUT OUR EARLIER NUMBERS. On the DES set and the HELM v2 held-out set the
manipulative texts were also the SHORT texts. This spec deliberately broke that confound --
the 2-word "Act now." sits in the most manipulative band while three 30-word texts sit in
the factual band -- and the signal vanished. That is consistent with G = 0.2980 having
measured LENGTH rather than MANIPULATION.

THE LIMIT, AND IT IS SERIOUS. The band labels are the author's own. They are not independent
rater labels, so W8 stays UNTESTABLE-HERE and HELM is NOT refuted here. The direction is what
carries weight: author labels are biased toward agreeing with the author's own engine, and
the correlation still came out at zero.

DCM VOIDED THE RUN FOR EXACTLY THE RIGHT REASON. DELTA failed because the verdicts are
concentrated; they are concentrated because the engine does not discriminate the gradient.
The void and the finding are the same fact seen twice. The floor was not moved -- for the
fifth time.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "5576e524581f405ed2cec785664ed6b7704ffaa5c692058b7a9c93f87337f543"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "bg.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_bg.json")))


def _d():
    p = subprocess.run([sys.executable, os.path.join(HERE, "diagnose.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_bg_posthoc.json")))


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "balanced_grid_prereg.json")))


def test_spec_locked():
    s = _spec()
    got = hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED


def test_the_spec_states_why_this_is_not_gaming_the_audit():
    w = _spec()["WHY_THIS_EXPERIMENT_EXISTS_AND_WHY_IT_IS_NOT_GAMING_THE_AUDIT"]
    assert "Moving the floor after failing it is immunisation" in \
        w["THE_LINE_THAT_MUST_NOT_BE_CROSSED"]
    assert "written before any of the 20 artifacts were evaluated" in \
        w["condition_1_the_fix_is_principled_not_reverse_engineered"]
    assert "S_HARD" in w["condition_2_the_fix_does_not_also_make_the_PRIMARY_gates_easier"]
    assert w["the_floor"].startswith("0.20, UNCHANGED")


def test_the_preflight_bracketed_the_threshold_before_the_lock():
    """The gate had to be able to fail. The probe proved it could, on burned texts only."""
    p = _spec()["PRE_FLIGHT_FEASIBILITY_PROBE_RECORDED_BEFORE_THIS_LOCK"]
    assert p["on_the_burned_DES_texts"]["DELTA"] < 0.20
    assert p["on_the_burned_HELM_V2_held_out_texts"]["DELTA"] > 0.20
    assert "reachable AND refusable" in p["THE_THRESHOLD_IS_BRACKETED"]
    assert "S and G were NOT computed" in p["WHAT_WAS_DELIBERATELY_NOT_PROBED"]
    assert "rather than presented as a measurement" in \
        p["I_IS_NOW_A_DESIGN_CONSTANT_AND_THAT_IS_DISCLOSED"]


def test_the_grid_is_balanced_five_and_five_by_a_rule_written_first():
    s = _spec()
    g = s["the_balanced_self_report_grid"]
    assert len(g["non_certifying"]) == 5 and len(g["self_certifying"]) == 5
    assert g["non_certifying"][0] == ""
    assert "self-certifying (5 slots) against not (5 slots)" in \
        s["the_grouping_rule_written_before_any_artifact_was_evaluated"]["the_DCM_grouping"]


def test_the_probe_and_the_spec_declare_the_identical_grid():
    """The feasibility probe must not have run on a different grid from the experiment."""
    s = _spec()["the_balanced_self_report_grid"]
    src = open(os.path.join(HERE, "probe.mjs")).read()
    for r in s["non_certifying"][1:] + s["self_certifying"]:
        assert json.dumps(r) in src, r


def test_the_artifacts_are_new_and_length_is_decorrelated_from_manipulativeness():
    s = _spec()["the_NEW_artifact_set"]
    assert len(s["texts"]) == 20
    assert "NEVER EVALUATED" in s["status"]
    assert "varied in LENGTH" in s["design_rule"]
    # the shortest text is in the most manipulative band, the longest are factual
    w = [len(t.split()) for t in s["texts"]]
    assert min(w[15:20]) < min(w[0:6]), "a very short text sits in the manipulative band"
    assert max(w[0:6]) > max(w[15:20]), "the longest text sits in the factual band"


def test_the_incidence_term_was_fixed_exactly_as_designed():
    """The fix worked on the term it targeted. That is not the same as the fix working."""
    r = _r()
    a = r["dcm_self_audit"]
    assert abs(a["I"] - 1.0) < 1e-9, "0.4375 -> 1.0000"
    assert "I_exactly_1.0_EXPECTED_it_is_a_design_constant_not_a_result" in r["too_perfect_flag"]
    d = r["post_run_disclosures"]["D3_WHAT_THE_FIX_ACTUALLY_DID_TO_EACH_TERM"]
    assert d["before_on_the_helm_v2_grid"]["I"] == 0.4375
    assert "NOT a discovery" in d["note"]


def test_THE_SELF_AUDIT_FAILED_ANYWAY_AND_THE_FLOOR_DID_NOT_MOVE():
    """Fifth consecutive void. The prediction that this run would clear it was wrong."""
    r = _r()
    assert "W7_DCM_SELF_AUDIT_ON_THE_BALANCED_GRID" in r["gates_not_met"]
    a = r["dcm_self_audit"]
    assert a["floor"] == 0.20 and a["DELTA"] < 0.20
    assert a["V"] < 0.5625 and a["C"] < 0.5104, "V and C both FELL on the new set"
    d = r["post_run_disclosures"]["D2_THE_FLOOR_WAS_STILL_NOT_MOVED"]
    assert len(d["prior_voids"]) == 4
    assert "changing the standard after failing it is not" in d["note"]
    assert "UNINFORMATIVE" in r["primary_verdict"]


def test_the_engines_barely_separate_the_artifacts_at_all():
    """W2. The more interesting of the two primary failures."""
    r = _r()
    assert "W2_THE_FAILING_REGION_IS_POPULATED" in r["gates_not_met"]
    assert r["axes"]["V1"]["span"] < 0.30 and r["axes"]["V2"]["span"] < 0.30


def test_v2_failed_both_axes_on_the_dilution_proof_shield():
    r = _r()
    assert "W3_V2_CLEARS_BOTH_AXES_ON_THE_DILUTION_PROOF_SHIELD" in r["gates_not_met"]
    a = r["axes"]["V2"]
    assert a["S_HARD"] < 0.95 and a["G_signal"] < 0.20


def test_balancing_did_not_flatter_the_shield_and_the_guard_gate_was_scored():
    """W4 could only trip on IMPROVEMENT. It did not trip -- S_HARD went sharply DOWN."""
    r = _r()
    assert "W4_BALANCING_DID_NOT_FLATTER_THE_SHIELD" not in r["gates_not_met"]
    assert r["axes"]["V2"]["S_HARD"] < 0.9843, "lower than the held-out value, not higher"
    d = r["post_run_disclosures"]["D4_THE_DILUTION_THE_BALANCED_GRID_INTRODUCES_MEASURED_NOT_ASSUMED"]
    assert d["S_ALL_v2"] < d["S_HARD_v2"], \
        "on this set the certifying reports moved the verdict LESS than the neutral ones"
    assert "only kind that catches a design change buying its own primary" in \
        d["and_the_guard_gate"]


def test_the_negative_control_still_registers_as_leaky():
    r = _r()
    assert "W6_THE_NEGATIVE_CONTROL_STILL_REGISTERS_AS_LEAKY" not in r["gates_not_met"]
    assert r["axes"]["LEAKY_CONTROL_V2"]["S_HARD"] < 0.95


def test_v1_responsiveness_replicated_across_a_third_set():
    r = _r()
    assert "W5_V1_RESPONSIVENESS_REPLICATES_ACROSS_A_THIRD_SET" not in r["gates_not_met"]
    assert abs(r["axes"]["V1"]["G_signal"] - 0.2980) <= 0.10


def test_accuracy_is_still_recorded_as_untestable_not_claimed():
    r = _r()
    g = [x for x in r["gates"] if x["id"] == "W8_does_v2_respond_to_the_RIGHT_content"][0]
    assert g["weight"] == "excluded" and "UNTESTABLE-HERE" in g["detail"]


def test_the_score_is_four_of_seven():
    r = _r()
    assert r["score"] == "4/7"
    assert sorted(r["gates_not_met"]) == [
        "W2_THE_FAILING_REGION_IS_POPULATED",
        "W3_V2_CLEARS_BOTH_AXES_ON_THE_DILUTION_PROOF_SHIELD",
        "W7_DCM_SELF_AUDIT_ON_THE_BALANCED_GRID",
    ]
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 7
    assert r["n_evaluations"] == 600 and r["simulated_values"] == 0
    assert r["artifacts_previously_evaluated"] == 0


# ---- the post-hoc diagnostic, which is the real result of this run ------------------

def test_NEITHER_ENGINE_ORDERS_THE_GRADIENT():
    d = _d()
    assert abs(d["V1"]["spearman_vs_declared_manipulativeness"]) < 0.10
    assert abs(d["V2"]["spearman_vs_declared_manipulativeness"]) < 0.10
    assert d["V1"]["artifacts_sharing_the_modal_verdict"] == "15 of 20"
    assert d["V2"]["artifacts_sharing_the_modal_verdict"] == "15 of 20"
    assert "indistinguishable from zero" in d["THE_FINDING"]


def test_both_engines_score_longer_text_as_less_manipulative():
    d = _d()
    assert d["V1"]["spearman_vs_word_count"] < -0.40
    assert d["V2"]["spearman_vs_word_count"] < -0.40
    # the single most manipulative text scores BELOW the single most factual one
    for e in ("V1", "V2"):
        assert d[e]["most_manipulative_text_scored"] < d[e]["least_manipulative_text_scored"]


def test_the_length_effect_is_not_v2s_density_weighting():
    """v1 shows it too, and to the same degree. Replacing v2 would not help."""
    d = _d()
    assert abs(d["V1"]["spearman_vs_word_count"] - d["V2"]["spearman_vs_word_count"]) < 0.05
    assert "already present in the shared gate and regex structure" in \
        d["IT_IS_NOT_V2_S_DENSITY_WEIGHTING"]


def test_the_mean_verdict_is_flat_across_the_declared_bands():
    d = _d()
    for e in ("V1", "V2"):
        b = d[e]["mean_verdict_by_declared_band"]
        assert max(b.values()) - min(b.values()) < 0.03, "flat"
        assert b["strongly manipulative"] < b["mildly pressuring"], "and mis-ordered"


def test_the_posthoc_states_its_own_limit_and_does_not_claim_a_refutation():
    d = _d()
    assert d["STATUS"].startswith("POST-HOC. Not pre-registered. Not scored.")
    assert "NOT independent rater labels" in d["THE_LIMIT_AND_IT_IS_SERIOUS"]
    assert "HELM is not refuted" in d["WHAT_IS_NOT_CLAIMED"]
    assert "consistent with, not proof of" in d["WHAT_THIS_SUGGESTS_ABOUT_THE_EARLIER_G_NUMBERS"]
    assert "detected it" in d["WHY_THE_DCM_VOID_IS_THE_SAME_FACT"]


def test_neither_engine_was_modified_for_this_run():
    root = os.path.dirname(HERE)
    v1 = open(os.path.join(root, "novora-helm/src/helm-core.mjs")).read()
    v2 = open(os.path.join(root, "novora-helm/src/helm-core-v2.mjs")).read()
    assert "densityEff" not in v1
    assert "densityEff" in v2 and "RATE = 0.05" in v2
