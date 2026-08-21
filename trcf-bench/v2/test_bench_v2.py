"""
test_bench_v2.py -- the v2 bench: 6/6, V2a FIRED, and the sunset already expired.

TWO GENUINELY NEW RESULTS, BOTH EXECUTABLE IN-CONTAINER.

V2a — THE VETO FORM WINS. T0 never computed min(U, D_enc, D_dec). It does now:

    minimum   0.6807   <- WINS
    additive  0.5925
    product   0.5037   <- at chance, reproducing T0

    additive - minimum = -0.0882, far below MARGIN 0.01, so V2a FIRES.

Single index, NO fitting, so no overfitting and no fold reuse — the cleanest new look
available on this cohort. Direction-free AUC (max of a, 1-a) is used because an index
may point either way and pre-committing to a sign is a hidden researcher degree of
freedom; it is applied IDENTICALLY to all three forms so it cannot favour one.

What it says: viability on this cohort is governed by the WEAKEST factor — not by a
sum, and not by a product.

THE SUNSET HAS EXPIRED AND THE DEMOTION IS EXECUTED. SUNSET was 2026-06-30; today is
2026-08-21. V2b is still CONDITIONAL because the cohort has no pre-outcome shock marker
(no dep_shock / maintainer_loss / issue_spike field exists). So the tail lemma drops to
a weight-zero prior and the branch stands on cascade alone — fired by DATE, not by
mood, and fired AGAINST the carrier. That is the seatbelt working.

THE DOUBLE-DIP IS LOGGED, NOT COUNTED. product-vs-additive is T0's look. It appears
labelled CONFIRMATORY ONLY with counted_toward_score = False and no gate depends on it.

THREE PATHS IN THE SUPPLIED MODULE DO NOT EXIST HERE. lism-cohorts/repos992.json,
lism-cohorts/repo_deps.json, and every temporal/shock field. A real dependency graph
DOES exist at data/pypi/dep_graph_edges.csv (1287 edges, 540 nodes) — but it is PyPI
packages overlapping these GitHub repos by only 27 names, it carries no failure events
and no absorber variable, and it is NOT substituted for the missing edge file.

V6 DRY-RUN PROVES THE LOGIC BEFORE IT IS NEEDED. The inward knife reclassifies a
fixed/unbacked canary as RIBA-STRUCTURE, a state-contingent control comes back COUPLED
(so the classifier is not a constant), and an F3 fire removes L2 leaving [L0, L1, L3,
L4]. Proving invocation logic before it fires is the only time proving it is cheap.

AN OWN-GOAL, DISCLOSED. W5's first implementation scanned each entry for the substring
"pending" and tripped on the V1 note that uses the word to DENY it ("it is not
'pending'"). The spec's condition is that no test is DESCRIBED AS pending, which means
the STATUS field. The check was corrected to read the status against a declared
vocabulary; the spec was not touched.

WHAT V2a DOES NOT DO — W7, weight:excluded. A2 AS WRITTEN claims a PRODUCT. That stays
refuted; the product is still at chance. A2's stated INTUITION — "a zero in any factor
zeroes the claim" — is veto semantics, which is what min() encodes and which wins here.
So the idea may survive while the published formalisation does not. That is not a
rescue, and reinterpreting a refuted formalisation after seeing the result is exactly
what the anti-immunisation rule forbids counting.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "37812580b45a216b598ef00837ef0e741279413bcdf1597feac476961e731458"
V1_SPEC = "916beaf4f4b094b612510ec89bb62d4f1713e9621390f0e7ac51f1ea7c70b76a"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "bench_v2.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_v2.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v1_bench():
    s = json.load(open(os.path.join(HERE, "prereg", "v2_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V1_SPEC


def test_the_independence_gate_was_REPEATED_not_inherited():
    r = _r()
    assert "W1_INDEPENDENCE_GATE_REPEATED_PRE_OUTCOME" not in r["gates_not_met"]
    for v in r["vif"].values():
        assert v < 5
    assert "a gate you assume is not a gate" in \
        _gate("W1_INDEPENDENCE_GATE_REPEATED_PRE_OUTCOME")["detail"]


def test_PRIMARY_V2a_fired_and_the_VETO_form_wins():
    r = _r()
    v = r["V2a"]
    assert v["fired"] is True
    assert v["winner"] == "minimum"
    a = v["direction_free_auc"]
    assert a["minimum"] > a["additive"] > a["product"]
    assert v["additive_minus_minimum"] < v["margin"]
    assert a["product"] < 0.55, "product still at chance, reproducing T0"


def test_the_veto_race_used_no_fitting_so_there_is_no_overfit():
    d = _gate("W2_PRIMARY_V2a_THE_VETO_FORM_RACE")["detail"]
    assert "NO fitting" in d and "no fold reuse" in d
    assert "reporting, not about any particular form winning" in d


def test_the_double_dip_is_logged_and_counts_toward_nothing():
    r = _r()
    c = r["confirmatory_only"]
    assert c["counted_toward_score"] is False
    d = _gate("W3_THE_DOUBLE_DIP_IS_LOGGED_NOT_COUNTED")["detail"]
    assert "CONFIRMATORY ONLY" in d
    assert "counting one look twice is the double-dip" in d


def test_PRIMARY_the_sunset_expired_and_the_demotion_is_EXECUTED():
    r = _r()
    s = r["sunset"]
    assert s["date"] == "2026-06-30"
    assert s["expired"] is True
    assert s["v2b_conditional"] is True
    assert s["demotion_executed"] is True
    d = _gate("W4_THE_SUNSET_FIRES_BY_DATE")["detail"]
    assert "DEMOTION IS EXECUTED" in d
    assert "by date, not by mood" in d
    assert "AGAINST the carrier" in d


def test_all_seven_unrun_tests_carry_a_status_from_the_vocabulary():
    r = _r()
    assert "W5_EVERY_UNRUN_TEST_CARRIES_A_STATUS_AND_A_REMEDY" not in r["gates_not_met"]
    vocab = {"AWAITING_EXTERNAL", "CONDITIONAL_SUNSET_EXPIRED", "DATA_ABSENT",
             "NOT_BUILT_BY_CHOICE", "CANNOT_RUN"}
    u = r["unrun"]
    assert len(u) == 7
    for k, v in u.items():
        assert v["status"] in vocab, "%s carries a declared status" % k
        assert v["needs"], "%s names what would unblock it" % k


def test_the_W5_own_goal_is_disclosed():
    """The first check scanned for 'pending' and tripped on a note denying it."""
    d = _gate("W5_EVERY_UNRUN_TEST_CARRIES_A_STATUS_AND_A_REMEDY")["detail"]
    assert "DISCLOSED" in d
    assert "tripped on the V1 note that uses the word to DENY it" in d
    assert "the spec's condition was not touched" in d


def test_the_missing_edge_file_is_NOT_substituted_with_the_pypi_graph():
    u = _r()["unrun"]["V3b_cascade_analogue"]
    assert u["status"] == "DATA_ABSENT"
    assert "only 27 names overlap" in u["needs"]
    assert "is not substituted for one" in u["needs"].lower() or \
        "not substituted" in u["needs"]
    assert "would be simulated" in u["needs"]


def test_V6_dry_run_proves_knife_and_seatbelt_before_they_are_needed():
    r = _r()
    assert "W6_V6_DRY_RUN_PROVES_THE_KNIFE_AND_THE_SEATBELT" not in r["gates_not_met"]
    d = _gate("W6_V6_DRY_RUN_PROVES_THE_KNIFE_AND_THE_SEATBELT")["detail"]
    assert "RIBA-STRUCTURE" in d and "COUPLED" in d
    assert "not a constant" in d
    assert "'L0', 'L1', 'L3', 'L4'" in d, "F3 removes L2"


def test_V2a_does_not_rescue_A2_as_written():
    g = _gate("W7_does_V2a_firing_rescue_A2")
    assert g["weight"] == "excluded"
    assert "That is NOT a rescue of the published form" in g["detail"]
    assert "anti-immunisation rule forbids counting" in g["detail"]


def test_nothing_here_touches_the_reading_of_2_275():
    g = _gate("W8_does_any_of_this_touch_the_reading_of_2_275")
    assert g["weight"] == "excluded"
    assert "The aya is not a functional form" in g["detail"]


def test_score_is_six_of_six_with_a_receipt():
    r = _r()
    assert r["score"] == "6/6" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0
    assert len(r["receipt"]) == 16
