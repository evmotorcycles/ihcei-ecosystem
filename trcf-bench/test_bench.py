"""
test_bench.py -- the TRCF bench: 6/6, one family executed, F7 FIRED.

WHAT WAS ASKED AND WHAT WAS DONE. The six-family bench (T0–T5, B, D) with falsifiers
F1'–F8 is LOCKED in full — pre-registration is worth most precisely before data exists.
Execution is a separate question, and exactly ONE family could run in this container.

T0 RAN. F7 FIRED.

    independence gate   VIF  logU 1.269 · D_enc 1.055 · D_dec 1.231   all < 5
    outcome             295 archived of 992                            populated
    product             AUC 0.4855   ← AT CHANCE
    additive            AUC 0.6530
    saturated           AUC 0.7023
    product − additive  −0.1675      margin 0.01
    product − saturated −0.2168      margin 0.01

The multiplicative axiom A2 (E = U·D_enc·D_dec) is DISCONFIRMED on this cohort. The
product specification does not merely lose — it sits at chance, and loses in the wrong
direction by more than an order of magnitude beyond the pre-registered margin. That
margin was fixed before the run and was not moved after seeing the numbers.

THE ORDER OF OPERATIONS MATTERED. S1 runs the VIF gate on FEATURES ONLY. Had it failed,
the run stops and proxies are redesigned WITHOUT the outcome ever being touched. That is
the difference between an independence gate and a post-hoc excuse.

THE DOMAIN SUBSTITUTION IS DECLARED IN THE VERDICT, NOT BURIED. The bench specified
SME/mortgage loan panels. None exist here and outbound fetch is policy-blocked, so 992
GitHub repositories were used. Two things are true at once: this is the HOME GROUND
where E = U·D_enc·D_dec was defined in this project, so it is a friendly test rather
than a hostile one — and it settles NOTHING about lending. A defender who says "repos
are not loans" is correct, and S8 records that A2 could still hold on loan panels.

THE SEVEN THAT DID NOT RUN ARE DECLARED, NOT IMPLIED.
    T1 substrate · T2 bend-vs-stagger · T3 circulation · T4 hardship · T5 tether
        DATA_ABSENT — each names the exact artefact that would unblock it
    B  the ABM      NOT_BUILT_BY_CHOICE — it was buildable and was deliberately not
        built. It calibrates to T1/T5 moments that do not exist, so it would have
        produced impressive numbers calibrated to nothing.
    D  the pilot    CANNOT_RUN — 24 months and 200 real members; compute does not
        substitute for elapsed time.

None is reported as pending or partially complete. A locked design is a promise, and
reporting a promise as an outcome is the failure this repository exists to prevent.

TWO THINGS F7 DOES NOT MEAN — both weight:excluded.
  S7  It does not refute the pressed reading of 2:275. F7 concerns a FUNCTIONAL FORM
      chosen at step 3 of the N182 pipeline — one operationalisation among many. The
      step-2 schema predicted COUPLING, not multiplication specifically. A2 is an axiom
      someone wrote down; the aya is not.
  S8  It does not settle A2 universally. One cohort, one domain.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "916beaf4f4b094b612510ec89bb62d4f1713e9621390f0e7ac51f1ea7c70b76a"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "bench.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_trcf_bench.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_is_locked():
    s = json.load(open(os.path.join(HERE, "prereg", "trcf_bench_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED


def test_the_independence_gate_ran_on_FEATURES_ONLY_first():
    r = _r()
    assert "S1_THE_INDEPENDENCE_GATE_IS_CHECKED_BEFORE_ANY_OUTCOME" not in r["gates_not_met"]
    for v in r["T0"]["vif"].values():
        assert v < 5
    d = _gate("S1_THE_INDEPENDENCE_GATE_IS_CHECKED_BEFORE_ANY_OUTCOME")["detail"]
    assert "WITHOUT ever touching" in d


def test_the_fail_region_is_populated():
    t = _r()["T0"]
    assert t["n"] == 992 and t["archived"] == 295


def test_PRIMARY_F7_FIRED_and_the_product_is_at_chance():
    r = _r()
    t = r["T0"]
    assert t["F7"] == "FIRED"
    assert t["race"]["product"]["mean_auc"] < 0.55, "at chance"
    assert t["race"]["additive"]["mean_auc"] > t["race"]["product"]["mean_auc"]
    assert t["race"]["saturated"]["mean_auc"] > t["race"]["product"]["mean_auc"]
    assert t["product_minus_additive"] < -0.01
    assert t["product_minus_saturated"] < -0.01


def test_the_margin_was_not_moved_after_seeing_the_result():
    t = _r()["T0"]
    assert t["margin"] == 0.01
    assert "NOT moved after seeing these" in _gate("S4_F7_IS_ADJUDICATED_EXPLICITLY")["detail"]


def test_the_race_gate_is_about_reporting_not_winning():
    d = _gate("S3_PRIMARY_THE_FUNCTIONAL_FORM_RACE_IS_RUN_AND_REPORTED_EITHER_WAY")["detail"]
    assert "REPORTING, not about the product winning" in d


def test_all_seven_unrun_families_carry_a_status_and_a_remedy():
    r = _r()
    assert "S5_THE_SEVEN_UNRUN_FAMILIES_ARE_DECLARED_NOT_IMPLIED" not in r["gates_not_met"]
    u = r["unrun_detail"]
    assert len(u) == 7
    for k, v in u.items():
        assert v["status"] in ("DATA_ABSENT", "NOT_BUILT_BY_CHOICE", "CANNOT_RUN")
        assert "needs" in v or "reason" in v, "%s must name what would unblock it" % k
        assert "pending" not in json.dumps(v).lower()


def test_the_ABM_was_buildable_and_deliberately_not_built():
    u = _r()["unrun_detail"]["B_the_ABM"]
    assert u["status"] == "NOT_BUILT_BY_CHOICE"
    assert "calibrated to nothing" in u["reason"]
    assert "deferred, not skipped" in u["reason"]


def test_the_domain_substitution_is_in_the_verdict_itself():
    v = _r()["primary_verdict"]
    assert "DOMAIN SUBSTITUTION" in v
    assert "settles NOTHING about lending" in v
    assert "repos are not loans" in v, "the objection is stated before it is raised"


def test_F7_firing_does_not_refute_the_reading_of_2_275():
    g = _gate("S7_does_F7_firing_refute_the_pressed_reading_of_2_275")
    assert g["weight"] == "excluded"
    assert "predicted COUPLING, not multiplication specifically" in g["detail"]
    assert "an axiom someone wrote down; the aya is not" in g["detail"]


def test_one_cohort_does_not_settle_A2_universally():
    g = _gate("S8_does_T0_alone_settle_A2")
    assert g["weight"] == "excluded"
    assert "could still hold on loan panels" in g["detail"]


def test_score_is_six_of_six_and_nothing_simulated():
    r = _r()
    assert r["score"] == "6/6" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0
