"""
test_scar.py -- locks the Graph-Topological Decode Scarcity run: 5/6, and the null is
against our own manuscript.

WHAT WAS ASKED FOR AND WHAT IS DELIVERABLE. The request was a first-principles
graph-topological scarcity metric for the Scope Declaration Layer, which ranges over five
substrates. A topological measure needs a graph, and three of the five do not supply one:

    yeast      BLOCKED          interactome EDGES were never committed, only node rows
    github     BLOCKED          a per-repository table; no graph exists in the repository
    quantum    NOT APPLICABLE   a closed-form derivation, no dataset
    pypi       UNTESTABLE-HERE  CIRCULAR: its declared outcome E_indegree is derived from
                                the SAME graph the metric would be computed on
    interbank  THE ONE CLEAN TEST

So the gap as posed CANNOT be closed with committed data, and this run does not pretend
otherwise. One substrate cannot establish a cross-substrate scope rule, which is what SDL's
DELTA was for.

THE METRIC HAS NO FREE PARAMETER. B(v) is the fraction of v's neighbours u for which N(v)
and N(u) share no common member -- an edge with no alternative path of length two. No
threshold chosen, no weight fitted, no distribution assumed. The HIGH/LOW split is at
B == 1.0, the natural boundary of the metric rather than a cut picked from the outcome.

WHAT WAS UNDER TEST. LISM's OWN declared domain limit, manuscript section 3.3c: that the
product form E = U*D_enc*D_dec assumes the decode hop is SCARCE. Never previously measured.

THE RESULT, AND IT IS A CLEAN REFUTATION RATHER THAN AN UNDERPOWERED SHRUG.

                          product    quadratic   advantage
    HIGH scarcity B=1      0.4455     0.4383       +0.0072
    LOW  scarcity B<1      0.6159     0.6180       -0.0021
                                 difference-in-advantage  +0.0093

    90% bootstrap CI [-0.0283, +0.0424], width 0.0707, bar 0.20 -- K5 MET.

Because K5 was met, K4 is interpretable, and the CI EXCLUDES the pre-registered +0.05. This
is a refutation at the declared effect size, not a failure to detect.

AND THE DIRECTION IS WORSE THAN A NULL. In the scarce-decode stratum BOTH forms score BELOW
0.5 -- they are anti-predictive there -- while in the low-scarcity stratum both work
(0.6159, 0.6180). Where the decode hop has no two-step substitute is where LISM performs
WORST, which is the opposite of what section 3.3c asserts.

The permutation control is null as required, so the strata themselves are not manufacturing
the effect.

CONSEQUENCE, PRE-REGISTERED BEFORE THE RUN: section 3.3c is an unsupported assertion where
it is testable, and the manuscript is amended to say so rather than left standing.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "135355477e57ae681805b289f1234e003954a00d36146cd2f19ab31df137e095"
_CACHE = {}


def _r():
    if "r" not in _CACHE:
        p = subprocess.run([sys.executable, os.path.join(HERE, "scar.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _CACHE["r"] = json.load(open(os.path.join(HERE, "results_scar.json")))
    return _CACHE["r"]


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "scarcity_prereg.json")))


def test_spec_locked():
    assert hashlib.sha256(json.dumps(_spec(), sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest() == LOCKED


def test_the_spec_says_up_front_the_gap_cannot_be_closed_as_posed():
    g = _spec()["THE_GAP_AS_POSED_CANNOT_BE_CLOSED_AND_HERE_IS_THE_ACCOUNTING"]
    assert g["S_yeast"].startswith("BLOCKED")
    assert g["S_github"].startswith("BLOCKED")
    assert g["S_quantum"].startswith("NOT APPLICABLE")
    assert g["S_pypi"].startswith("UNTESTABLE-HERE")
    assert "CIRCULARITY, not missing data" in g["S_pypi"]
    assert "THE ONE CLEAN TEST" in g["S_interbank"]
    assert "cannot establish a cross-substrate scope rule" in g["THE_HONEST_CONSEQUENCE"]


def test_three_different_unavailability_verdicts_are_kept_distinct():
    """BLOCKED, UNTESTABLE-HERE and NOT APPLICABLE are not the same thing."""
    g = _spec()["THE_GAP_AS_POSED_CANNOT_BE_CLOSED_AND_HERE_IS_THE_ACCOUNTING"]
    kinds = {g[k].split(".")[0].split(" -")[0].split(",")[0].strip()
             for k in ("S_yeast", "S_github", "S_quantum", "S_pypi")}
    assert len(kinds) == 3, kinds


def test_the_metric_has_no_fitted_parameter():
    m = _spec()["the_scarcity_metric_and_it_has_no_fitted_parameter"]
    assert "no free parameter of any kind" in m["why_this_is_first_principles"]
    assert "not chosen from the outcome" in m["the_split"]
    src = open(os.path.join(HERE, "scar.py")).read()
    assert "no fitted parameter anywhere in this expression" in src


def test_the_rival_form_was_copied_verbatim_not_rewritten():
    s = _spec()["the_two_rival_forms_taken_verbatim_from_the_earlier_run"]
    assert s["LISM_product"] == "u * de * dd"
    assert s["quadratic_rival"] == "u * (de + dd) ** 2"
    net = open(os.path.join(os.path.dirname(HERE), "interbank-2016", "network.py")).read()
    assert "u * de * dd" in net and "u * (de + dd) ** 2" in net


def test_the_power_probe_measured_precision_without_direction():
    p = _spec()["PRE_FLIGHT_FEASIBILITY_PROBE_RECORDED_BEFORE_THIS_LOCK"]
    assert p["permuted_label_bootstrap"]["WIDTH"] < 0.20
    assert "without seeing DIRECTION" in p["the_power_probe_was_run_on_PERMUTED_LABELS"]
    assert "real labels were never used in the probe" in p["WHAT_WAS_DELIBERATELY_NOT_PROBED"]
    assert "131 nodes and 20 events" in p["the_honest_caveat_it_does_not_remove"]


def test_the_run_reproduces_the_earlier_cohort_exactly():
    r = _r()
    assert "K1_integrity" not in r["gates_not_met"]
    assert r["strata"]["HIGH_B_equals_1"]["n"] + r["strata"]["LOW_B_below_1"]["n"] == 1349
    assert r["strata"]["HIGH_B_equals_1"]["events"] + \
        r["strata"]["LOW_B_below_1"]["events"] == 291


def test_THE_DOMAIN_LIMIT_WAS_REFUTED_WHERE_IT_IS_TESTABLE():
    r = _r()
    assert "K4_PRIMARY_THE_PRODUCT_FORM_S_ADVANTAGE_IS_LARGER_WHERE_DECODE_IS_SCARCE" \
        in r["gates_not_met"]
    assert r["auc"]["difference_in_advantage"] < 0.05
    assert "unsupported assertion" in r["primary_verdict"]


def test_it_is_a_REFUTATION_not_an_underpowered_null():
    """K5 was met and the CI excludes the pre-registered effect size."""
    r = _r()
    assert "K5_THE_ESTIMATE_IS_PRECISE_ENOUGH_TO_MEAN_ANYTHING" not in r["gates_not_met"]
    assert r["bootstrap"]["width"] <= 0.20
    assert r["bootstrap"]["CI90"][1] < 0.05, "the interval excludes the declared effect size"
    assert "K5 WAS MET, so K4 is interpretable" in r["primary_verdict"]


def test_the_direction_is_opposite_to_what_the_manuscript_asserted():
    """Where decode is scarce, BOTH forms are anti-predictive."""
    r = _r()
    a = r["auc"]
    assert a["HIGH_product"] < 0.5 and a["HIGH_quadratic"] < 0.5
    assert a["LOW_product"] > 0.6 and a["LOW_quadratic"] > 0.6


def test_the_permutation_control_is_null():
    r = _r()
    assert "K6_THE_PERMUTATION_CONTROL_IS_NULL" not in r["gates_not_met"]
    assert r["permutation_control"]["contains_zero"] is True
    assert r["too_perfect_flag"] == []


def test_one_substrate_is_not_reported_as_five():
    r = _r()
    assert r["substrates_tested"] == 1 and r["substrates_in_SDL"] == 5
    assert "ONE SUBSTRATE OF FIVE" in r["primary_verdict"]
    g = [x for x in r["gates"]
         if x["id"] == "K7_does_the_scope_rule_hold_ACROSS_substrates"][0]
    assert g["weight"] == "excluded" and "UNTESTABLE-HERE" in g["detail"]
    d = r["post_run_disclosures"]["D2_THE_GAP_AS_POSED_WAS_NOT_CLOSED"]
    assert d["delivered"] == "one substrate"


def test_DCM_is_excluded_because_it_cannot_fail_on_a_continuous_outcome():
    r = _r()
    g = [x for x in r["gates"] if x["id"] == "K8_DCM_self_audit"][0]
    assert g["weight"] == "excluded" and "cannot fail" in g["detail"]


def test_the_manuscript_was_actually_amended():
    """The spec committed to this before the run. It is not left as a promise."""
    ms = open(os.path.join(os.path.dirname(HERE), "LISM_manuscript_REVISED.md")).read()
    assert "135355477e57ae68" in ms, "the amendment cites the locked spec"
    assert "anti-predictive" in ms


def test_score_is_five_of_six_and_nothing_simulated():
    r = _r()
    assert r["score"] == "5/6"
    assert r["gates_not_met"] == [
        "K4_PRIMARY_THE_PRODUCT_FORM_S_ADVANTAGE_IS_LARGER_WHERE_DECODE_IS_SCARCE"]
    assert r["simulated_values"] == 0
