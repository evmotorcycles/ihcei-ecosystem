"""
test_con.py -- locks the diagnosis of the standing sign alarm on D: 4/4.

THE ALARM AS IT STOOD. rho(U, D) = +0.5695 on a real PyPI graph and -0.4702 on the real
GitHub cohort. Two committed substrates disagreeing on the SIGN, taken to mean D is an
unstable construct and every fidelity claim rests on sand.

THE PROPOSED FIX, AND WHY IT IS NOT WHAT WAS TESTED. The proposal was to normalise D_dec by
inbound demand, on the theory that GitHub popularity floods the issue queue. That is
BLOCKED, not refuted: the committed GitHub cohort carries no inbound issue or PR counts, and
no proxy was substituted. A prediction of that mechanism had already failed before this lock
-- queue congestion is a DECODE-side story, so the flip should sit in D_dec, and it does
not. BOTH hops flip: PyPI D_enc +0.5869 / D_dec +0.3496 against GitHub -0.2415 / -0.5154.
Those were computed before the spec was written, recorded in it as pre-flight observations,
and scored by nothing.

WHAT WAS TESTED INSTEAD. That D was never ONE quantity. The two definitions, verbatim from
committed code, share a name and nothing else:

    PyPI    D_enc = 1.0 / (1.0 + months_since_release / 12.0)     a recency decay
    GitHub  D_enc = TF-IDF cosine of commit messages to a fixed reference

THE RESULT IS EXACT, NOT APPROXIMATE.

    rho(U_versions, months_since_release)  =  -0.5869
    rho(U_versions, D_enc)                 =  +0.5869

Those are the same number with a sign flip, and necessarily so: D_enc is a strictly
DECREASING function of months, and Spearman is rank-based, so rho(U, D_enc) = -rho(U, months)
identically. PyPI's "fidelity correlation" is the statement that packages with more releases
have released more recently, restated. It carries ZERO independent information about fidelity.

THE COUNT-VS-INTENSITY RULE MADE IT WORSE, NOT BETTER. Converting U from a raw version COUNT
to an INTENSITY -- versions per month of age -- drove rho to +0.9418, because versions per
month is even more directly a function of recency. The usual remedy is a tautology here.

WHAT THIS DOES AND DOES NOT SETTLE. It disqualifies ONE of the two data points the alarm
rested on. With the PyPI number disqualified there is no longer a CONTRADICTION between
substrates -- there is one substrate with a negative correlation and one whose D was
mis-specified. The GitHub negative correlation is untouched by every gate here and stands
exactly as it was. D is NOT repaired, and E = U*D_enc*D_dec is NOT restored to universal
standing.

The alarm should therefore be RESTATED rather than retired: not "D is unstable across
substrates" but "D is a family of substrate-specific formulas, and at least one member of
that family was measuring release timing."

N3 declared an identity in advance -- rho(D_enc, months) = -1.0000 exactly -- and is
EXCLUDED from scoring, because a quantity that cannot come out otherwise is not evidence.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "b6a262ead56e56b532a3578185c6d505df45fbc9c58a5ba5864108bb194c53d8"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "con.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_con.json")))
    return _C["r"]


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "construct_prereg.json")))


def test_spec_locked():
    assert hashlib.sha256(json.dumps(_spec(), sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest() == LOCKED


def test_the_pre_lock_observations_are_marked_as_such_and_score_nothing():
    """Pre-registering something already seen would be theatre."""
    w = _spec()["WHY_THE_PROPOSED_FIX_IS_NOT_WHAT_IS_TESTED_HERE"]
    o = w["OBSERVED_BEFORE_THE_LOCK_AND_THEREFORE_NOT_SCORED"]
    assert o["pypi"]["rho_U_D_enc"] == 0.5869
    assert o["github_non_imputed"]["rho_U_D_dec"] == -0.5154
    assert "NO gate below scores them" in o["note"]
    r = _r()
    for g in r["gates"]:
        assert "0.5869" not in g["id"] and "pre_lock" not in g["id"]


def test_BOTH_hops_flip_so_a_decode_side_fix_cannot_explain_it():
    o = _spec()["WHY_THE_PROPOSED_FIX_IS_NOT_WHAT_IS_TESTED_HERE"][
        "OBSERVED_BEFORE_THE_LOCK_AND_THEREFORE_NOT_SCORED"]
    assert o["pypi"]["rho_U_D_enc"] > 0 and o["github_non_imputed"]["rho_U_D_enc"] < 0
    assert o["pypi"]["rho_U_D_dec"] > 0 and o["github_non_imputed"]["rho_U_D_dec"] < 0


def test_the_primary_was_not_probed_before_the_lock():
    p = _spec()["PRE_FLIGHT_FEASIBILITY_PROBE_RECORDED_BEFORE_THIS_LOCK"]
    assert "was NOT computed before this lock" in p["WHAT_WAS_DELIBERATELY_NOT_PROBED"]
    assert "direction is unknown at lock time" in p["WHAT_WAS_DELIBERATELY_NOT_PROBED"]


def test_THE_PYPI_CORRELATION_IS_EXACTLY_THE_RECENCY_CORRELATION():
    """Not approximately. The same number, sign-flipped, by algebra."""
    r = _r()
    m = r["measured"]
    assert abs(m["rho_U_versions_vs_months_since_release"]
               + m["pypi_baseline_rho_U_D_enc_from_spec"]) < 1e-9, \
        "rho(U, D_enc) = -rho(U, months) identically"
    assert "N2_PRIMARY_THE_PYPI_CORRELATION_IS_CONSTRUCTION_INDUCED" not in r["gates_not_met"]


def test_the_declared_identity_holds_and_scores_nothing():
    r = _r()
    m = r["measured"]
    assert m["rho_D_enc_vs_months_IDENTITY"] == -1.0
    g = [x for x in r["gates"] if x["id"] == "N3_the_pypi_D_enc_identity"][0]
    assert g["weight"] == "excluded" and g["met"] is None
    assert "not evidence" in g["detail"]
    assert "N3_identity_at_exactly_1.0_EXPECTED_and_declared_in_advance" in r["too_perfect_flag"]


def test_a_timing_free_fidelity_column_breaks_the_correlation():
    r = _r()
    m = r["measured"]
    assert "N4_DISCRIMINATING_A_TIMING_FREE_D_enc_BREAKS_THE_PYPI_CORRELATION" \
        not in r["gates_not_met"]
    assert abs(m["rho_U_versions_vs_pin_clarity_TIMING_FREE"]) < \
        m["pypi_baseline_rho_U_D_enc_from_spec"] - 0.20


def test_the_count_to_intensity_remedy_makes_it_WORSE():
    """The usual fix for a count is a tautology here."""
    r = _r()
    m = r["measured"]
    assert m["rho_U_intensity_vs_D_enc"] > m["pypi_baseline_rho_U_D_enc_from_spec"]
    assert m["rho_U_intensity_vs_D_enc"] > 0.90
    g = [x for x in r["gates"]
         if x["id"] == "N5_THE_COUNT_VS_INTENSITY_RULE_APPLIED_TO_U"][0]
    assert g["weight"] == "excluded" and "asserts disclosure" in g["detail"]


def test_the_permutation_control_is_null_on_both_substrates():
    r = _r()
    assert "N6_THE_PERMUTATION_CONTROL" not in r["gates_not_met"]
    p = r["measured"]["permutation_95th_abs_rho"]
    assert p["pypi"] <= 0.10 and p["github"] <= 0.10


def test_the_proposed_demand_normalisation_is_BLOCKED_not_refuted():
    r = _r()
    g = [x for x in r["gates"] if x["id"] == "N7_the_proposed_demand_normalisation"][0]
    assert g["weight"] == "excluded" and g["detail"].startswith("BLOCKED")
    assert "BLOCKED is not REFUTED" in g["detail"]
    assert "no proxy" in g["detail"].lower()
    d = r["post_run_disclosures"]["D3_the_proposed_demand_normalisation_is_BLOCKED_not_refuted"]
    assert "may well be correct" in d["note"]


def test_the_github_half_is_NOT_claimed_to_be_explained():
    r = _r()
    d = r["post_run_disclosures"]["D1_what_this_does_and_does_not_settle"]
    assert "no gate here touches" in d["does_NOT_settle"]
    assert "not repaired" in d["does_NOT_settle"]
    assert "not restored to universal standing" in d["does_NOT_settle"]


def test_the_remedy_is_a_rule_about_comparison_not_a_transformation():
    r = _r()
    d = r["post_run_disclosures"]["D2_the_two_definitions_share_a_name_and_nothing_else"]
    assert "recency decay" in d["pypi_D_enc"]
    assert "text-similarity" in d["github_D_enc"]
    assert "not a transformation applied to either" in d["note"]


def test_cross_substrate_repair_stays_untestable():
    r = _r()
    g = [x for x in r["gates"]
         if x["id"] == "N8_does_this_repair_D_for_cross_substrate_use"][0]
    assert g["weight"] == "excluded" and "UNTESTABLE-HERE" in g["detail"]
    assert "share no fidelity column" in g["detail"]


def test_score_is_four_of_four_and_nothing_simulated():
    r = _r()
    assert r["score"] == "4/4" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 4
