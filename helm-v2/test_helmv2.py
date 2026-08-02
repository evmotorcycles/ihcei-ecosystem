"""
test_helmv2.py -- locks the HELM v2 head-to-head on HELD-OUT data: 5/6.

WHAT WAS BUILT. HELM v2 replaces v1's integer effective count with a continuous,
saturating density weight:

    eff = cap * (1 - exp(-hits / (words * RATE))),  RATE = 0.05

Gate set, every regex, every LLR prior, the corroboration gate, band thresholds, epistemic
floor and seed are UNCHANGED. v1 is untouched and still ships.

THE TRAP THAT WAS AVOIDED. The DES run measured v1 at G = 0.1612 -- and its own DCM
self-audit VOIDED that run, so the number licensed no conclusion. Building v2 to "fix" it
would have been acting on a result declared unusable. v2 rests instead on TWO FACTS READABLE
IN V1'S SOURCE: count() returns an integer so the posterior lands on a small lattice by
construction, and v1 computes the word count but uses it only for the methodology term, so
every pressure and mechanism term ignores text length.

RESULTS ON 12 TEXTS NEITHER ENGINE HAD EVER SEEN.

                        S shield    G signal    distinct verdicts
    v1                   0.9885      0.2980           13 of 96
    v2                   0.9843      0.3078           49 of 96
    leaky control (v2)   0.8742      0.3015           28 of 96

  Z3 PASSED. v2 clears BOTH axes -- S 0.9843 against a 0.95 bar and G 0.3078 against 0.20.
  Z4 PASSED. S fell only 0.0042, well inside the 0.02 tolerance. v2 did NOT buy signal by
     loosening the shield. Scored anyway, because "by construction" is an argument and not
     a measurement.
  Z5 PASSED. The control still registers as leaky under v2's scoring.

AND THE MOST IMPORTANT LINE IN THE RUN IS A NEGATIVE ONE.

    v1 scored G = 0.1612 on the DES artifact set.
    v1 scores  G = 0.2980 on the held-out set -- ABOVE THE 0.20 BAR.

THE DEFECT I BUILT V2 TO FIX DOES NOT REPRODUCE. The under-responsiveness was a property of
the DES ARTIFACT SET, not of the engine. Had the primary been measured on the DES grid --
the set whose properties motivated the rebuild -- this run would have reported a confirmed
fix for a problem that does not generalise. THE HELD-OUT DESIGN IS THE ONLY REASON THAT DID
NOT HAPPEN, and it is why the specification forbade using the DES grid.

WHAT V2 ACTUALLY IMPROVED, WHICH IS NOT WHAT WAS CLAIMED FOR IT. Granularity, and by a lot:
49 distinct verdicts against 13, with C at 0.5104 against 0.0833 on the earlier grid. The
responsiveness gain over v1 is +0.0099, which is nothing. Density weighting made the engine
FINER-GRAINED -- exactly what the code-inspection argument predicted -- and did NOT make it
more sensitive to manipulation.

Z6 FAILED at DELTA = 0.1256 against an UNCHANGED floor of 0.20, so Z2 through Z5 are
UNINFORMATIVE. Three prior runs were voided by that same floor; lowering it immediately
after building an engine that would benefit would be the most transparent immunisation move
available in this programme. The floor stayed and the instrument changed.

AND THE BINDING CONSTRAINT MOVED, WHICH IS DIAGNOSTIC. C is no longer what caps DELTA -- it
rose from 0.0833 to 0.5104. DELTA is now held down by I = 0.4375, and that is a property of
THIS EXPERIMENT'S GRID rather than of the engine: only 1 of the 8 self-report slots is
"none", so the grouping splits 12 against 84. The fix is a balanced grouping declared in a
future spec BEFORE data -- an experiment-design change, not a floor change.

STILL NOT KNOWN. Responsiveness is not accuracy. Z7 records that v2 might be a better LENGTH
detector rather than a better MANIPULATION detector, and nothing here separates those.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "03815a61ce8a555f2c741eb2b840502e32d9c845be46cb9be01d94e56755f119"


def _r():
    p = subprocess.run([sys.executable, os.path.join(HERE, "helmv2.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(os.path.join(HERE, "results_helmv2.json")))


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "helmv2_prereg.json")))


def test_spec_locked_and_names_the_trap():
    s = _spec()
    got = hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert got == LOCKED
    t = s["THE_TRAP_BEING_AVOIDED_AND_IT_IS_SUBTLE"]
    assert "VOIDED the run" in t["the_problem"]
    assert "CODE INSPECTION" in t["the_resolution"]
    assert "keeps that floor EXACTLY" in t["and_the_floor_is_still_not_moved"]
    assert "not because the bar got lower" in t["and_the_floor_is_still_not_moved"]


def test_the_preflight_probed_granularity_only():
    s = _spec()
    p = s["PRE_FLIGHT_FEASIBILITY_PROBE_RECORDED_BEFORE_THIS_LOCK"]
    assert p["v1"]["distinct_verdicts"] == 8 and p["v2"]["distinct_verdicts"] == 27
    assert "NEVER been evaluated" in p["WHAT_WAS_DELIBERATELY_NOT_PROBED"]
    assert "scoring a design against the evidence that produced the design" in \
        p["why_the_DES_grid_is_not_the_primary_measurement"]


def test_the_held_out_set_is_twelve_texts_locked_in_the_spec():
    s = _spec()
    h = s["the_HELD_OUT_artifact_set"]
    assert len(h["texts"]) == 12
    assert "NEVER EVALUATED" in h["status"]
    assert "varied in LENGTH" in h["design_rule"]


def test_v2_cleared_both_axes_on_held_out_data():
    """Z3. Both, not either."""
    r = _r()
    assert "Z3_V2_CLEARS_BOTH_AXES_ON_HELD_OUT_DATA" not in r["gates_not_met"]
    a = r["axes"]["V2"]
    assert a["S_shield"] >= 0.95 and a["G_signal"] >= 0.20
    assert r["held_out"] is True and r["simulated_values"] == 0


def test_v2_did_not_buy_signal_by_losing_shield():
    """Z4, the anti-immunisation gate."""
    r = _r()
    assert "Z4_V2_DID_NOT_BUY_SIGNAL_BY_LOSING_SHIELD" not in r["gates_not_met"]
    s1, s2 = r["axes"]["V1"]["S_shield"], r["axes"]["V2"]["S_shield"]
    assert s2 >= s1 - 0.02
    assert s2 < s1, "it did fall slightly, and the tolerance is what makes that acceptable"


def test_THE_DEFECT_DID_NOT_REPRODUCE_on_held_out_data():
    """The most important line in the run, and it is a negative one."""
    r = _r()
    d = r["post_run_disclosures"]["D7_THE_DEFECT_I_BUILT_V2_TO_FIX_DID_NOT_REPRODUCE"]
    assert d["G_v1_on_the_DES_grid"] == 0.1612
    assert d["G_v1_on_the_held_out_set"] >= 0.20, "v1 clears the bar on unseen data"
    assert "not of the engine" in d["finding"]
    assert "confirmed fix for a problem that does not generalise" in \
        d["why_this_is_the_run_s_most_important_line"]
    assert "only reason that did not happen" in d["why_this_is_the_run_s_most_important_line"]


def test_what_v2_actually_improved_is_granularity_not_responsiveness():
    r = _r()
    d = r["post_run_disclosures"]["D8_what_v2_actually_improved_and_it_is_not_what_was_claimed"]
    assert d["granularity"]["v2_distinct"] > 3 * d["granularity"]["v1_distinct"]
    assert abs(d["responsiveness"]["gain"]) < 0.02
    assert "is not worth reporting as an improvement" in d["note"]
    assert "did NOT make it more sensitive" in d["note"]


def test_the_self_audit_failed_and_the_floor_did_not_move():
    r = _r()
    assert "Z6_DCM_SELF_AUDIT_ON_V2" in r["gates_not_met"]
    a = r["dcm_self_audit"]
    assert a["floor"] == 0.20 and a["DELTA"] < a["floor"]
    d = r["post_run_disclosures"]["D4_the_DCM_floor_was_not_moved"]
    assert len(d["prior_voids"]) == 3
    assert "most transparent immunisation move" in d["note"]
    assert "UNINFORMATIVE" in r["primary_verdict"]


def test_the_binding_constraint_moved_from_C_to_I():
    """Diagnostic: the engine is no longer the bottleneck, the grid design is."""
    r = _r()
    a = r["dcm_self_audit"]
    assert a["C"] > 0.5, "granularity is fixed"
    assert a["I"] < 0.5, "the grouping split is now what caps DELTA"
    d = r["post_run_disclosures"]["D9_the_binding_constraint_on_the_self_audit_MOVED"]
    assert d["the_floor_still_did_not_move"] is True
    assert "experiment-design fix, not a floor change" in d["what_a_future_spec_should_do"]


def test_the_control_still_registers_as_leaky():
    r = _r()
    assert "Z5_THE_NEGATIVE_CONTROL_STILL_REGISTERS_AS_LEAKY" not in r["gates_not_met"]
    assert r["axes"]["LEAKY_CONTROL_V2"]["S_shield"] < 0.95


def test_accuracy_is_recorded_as_untestable_not_claimed():
    r = _r()
    z7 = [g for g in r["gates"] if g["id"] == "Z7_does_v2_respond_to_the_RIGHT_content"][0]
    assert z7["weight"] == "excluded" and "UNTESTABLE-HERE" in z7["detail"]
    assert "LENGTH" in z7["detail"]
    assert "Responsiveness is not accuracy" in \
        r["post_run_disclosures"]["D6_what_is_still_not_known"]["note"]


def test_v1_was_not_modified():
    """v2 lives in its own file; the shipping engine is untouched."""
    src = open(os.path.join(os.path.dirname(HERE), "novora-helm/src/helm-core.mjs")).read()
    assert "densityEff" not in src and "helm-density-v2" not in src


def test_the_score_is_five_of_six():
    r = _r()
    assert r["score"] == "5/6"
    assert r["gates_not_met"] == ["Z6_DCM_SELF_AUDIT_ON_V2"]
    assert len([g for g in r["gates"] if g["weight"] == "full"]) == 6
