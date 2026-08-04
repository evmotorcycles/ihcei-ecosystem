"""
test_oqm_screen_v2.py -- locks the two-axis screen: 6/6.

WHY v2 EXISTS, AND IT IS A DEFECT IN THE INSTRUMENT RATHER THAN IN THE READING. v1 printed
the class name 'LABEL'. That is a GRAMMATICAL fact -- the text names this group with a noun
rather than a finite verb -- but 'label' also names a SEMANTIC register: a birthright or
sectarian identity. One word for both invites exactly the conflation the reading is trying
to avoid, and the ambiguity was in the OUTPUT VOCABULARY. Classes are now
VERBAL / MIXED / NOMINAL, which describe how a group is named and imply nothing about what
the naming means. Renaming altered no count v1 produced and v1 is not re-scored.

WHAT IS NOT CONCEDED. That a NOMINAL verdict supports the governance-state reading. It is
EQUALLY COMPATIBLE with a governance-state reading and with a birthright-identity reading
and adjudicates NEITHER, because neither reading is a morphological claim. Gate Y6 requires
that sentence to appear verbatim in the output.

A CORRECTION TO HOW v1 WAS DESCRIBED. X6 was said to have "forced" the instrument to reject
a symmetry assumption. It did not. X6 is a CAPABILITY CHECK -- can the screen return a
non-verbal verdict at all. The five non-verbal results came from the data. Had the data
returned none, X6 would have FAILED and the correct report would have been "this screen is
broken", not "the framework is refuted". A gate that manufactured its own answer would be
worthless.

THE SECOND AXIS IS THE ACTUAL EXTENSION. Morphology cannot reach the question the governance
reading turns on: can the state be ENTERED and LEFT? A birthright identity cannot; a
state-variable can. Measured by two tight constructions -- 'after' immediately followed by a
possessed state-noun, and an explicit R-D-D reversion verb within three tokens -- with its
own negative control, because one does not become or cease to be Thamud.

    axis 1, grammar      VERBAL  amanu 268 | ittaqaw 27
                         MIXED   hadu 10 | ashraku 9 | sabaru 6
                         NOMINAL nasara 2 | munafiqun 2 | muslim 1 | hawariyyun 0
    axis 2, mutability   MUTABLE iman 8
                         FIXED   islam 1  (the single attestation is 9:74)
                         FIXED   nasr 0
    both negative controls   0 across all seven proper nouns

Y5 PASSED: the axes disagree on ittaqaw_muttaqin, which is VERBAL on grammar and FIXED on
mutability. Had they agreed everywhere, the second axis would add nothing and the honest
move would have been to drop it rather than report it.

AND A LIMIT FOUND AFTER THE RUN, RECORDED RATHER THAN SMOOTHED OVER. The primary axis-2
construction needs a POSSESSED STATE-NOUN. For five of the ten terms -- taqwa-hum, hud-hum,
shirk-hum, nifaq-hum, sabr-hum -- that form does not occur in the text at all, so their
score of 0 means THE MEASUREMENT COULD NOT FIRE, not that no mutability exists. Axis 2 is
interpretable only for islam, iman and nasr. Reporting munafiqun as FIXED would overclaim,
and the runner says so in its own disclosures.

SO THE ANSWER TO THE CORRECTION IS A MEASUREMENT, NOT AN AGREEMENT. Where axis 2 can fire,
iman shows the entry-and-exit pattern a state-variable reading predicts (8), and islam shows
it once -- 9:74, "they disbelieved after their islam" -- which is real but below the bar of
2 fixed before scoring. For munafiqun the measurement could not fire at all, so nothing is
claimed either way.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "d8243d3a42e45fe359582df1cad347547f6fab450c785193beeb1b25257fd0f3"
V1 = "8257dfcca40d0be024bac323e45137eba27277200243b3c1a7893d6f08349204"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v2.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v2.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v2_prereg.json"),
                          encoding="utf-8"))


def test_spec_locked_and_supersedes_v1():
    s = _spec()
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V1


def test_the_rename_is_admitted_as_an_instrument_defect():
    w = _spec()["WHY_V2_EXISTS_AND_IT_IS_A_DEFECT_IN_THE_INSTRUMENT_NOT_THE_READING"]
    assert "the ambiguity is in MY output vocabulary" in w["the_complaint_and_it_is_correct"]
    assert "VERBAL / MIXED / NOMINAL" in w["the_fix"]
    r = _r()
    d = r["post_run_disclosures"]["D2_WHY_THE_CLASSES_WERE_RENAMED"]
    assert "renaming altered no count v1 produced" in d["note"]


def test_WHAT_IS_NOT_CONCEDED_a_nominal_verdict_supports_neither_reading():
    w = _spec()["WHY_V2_EXISTS_AND_IT_IS_A_DEFECT_IN_THE_INSTRUMENT_NOT_THE_READING"]
    n = w["WHAT_IS_NOT_CONCEDED"]
    assert "EQUALLY COMPATIBLE" in n
    assert "does not support it and does not undermine it" in n


def test_the_register_firewall_is_carried_in_the_output():
    r = _r()
    assert "Y6_THE_REGISTER_FIREWALL_IS_STATED_IN_THE_OUTPUT" not in r["gates_not_met"]
    f = r["post_run_disclosures"]["D1_THE_REGISTER_FIREWALL"]["statement"]
    assert "EQUALLY COMPATIBLE" in f and "adjudicates NEITHER" in f
    assert "neither reading is a morphological claim" in f.lower()


def test_the_v1_description_is_corrected_X6_did_not_force_anything():
    r = _r()
    d = r["post_run_disclosures"]["D3_A_CORRECTION_TO_HOW_V1_WAS_DESCRIBED"]
    assert "It did not" in d["note"]
    assert "CAPABILITY CHECK" in d["note"]
    assert "this screen is broken" in d["note"]


def test_both_negative_controls_hold():
    r = _r()
    assert "Y2_AXIS1_NEGATIVE_CONTROL" not in r["gates_not_met"]
    assert "Y4_AXIS2_NEGATIVE_CONTROL" not in r["gates_not_met"]
    assert set(r["axis1_grammatical"]["negative_controls"].values()) == {0}
    assert all(v <= 1 for v in r["axis2_mutability"]["negative_controls"].values())


def test_the_positive_control_holds():
    r = _r()
    assert "Y3_AXIS1_POSITIVE_CONTROL" not in r["gates_not_met"]
    assert all(v >= 20 for v in r["axis1_grammatical"]["positive_controls"].values())


def test_PRIMARY_THE_TWO_AXES_ARE_DIFFERENT_MEASUREMENTS():
    r = _r()
    assert "Y5_PRIMARY_THE_TWO_AXES_ARE_NOT_THE_SAME_MEASUREMENT" not in r["gates_not_met"]
    assert r["axes_disagree_on"], "if they never disagreed the second axis adds nothing"
    assert "ittaqaw_muttaqin" in r["axes_disagree_on"]
    g = r["axis1_grammatical"]["classes"]["ittaqaw_muttaqin"]
    m = r["axis2_mutability"]["classes"]["ittaqaw_muttaqin"]
    assert g == "VERBAL" and m == "FIXED"


def test_the_classes_no_longer_use_the_ambiguous_word_label():
    r = _r()
    assert set(r["axis1_grammatical"]["classes"].values()) <= {"VERBAL", "MIXED", "NOMINAL"}
    assert "LABEL" not in set(r["axis1_grammatical"]["classes"].values())


def test_AXIS2_IS_ONLY_INTERPRETABLE_WHERE_THE_STATE_NOUN_IS_ATTESTED():
    """Five terms score 0 because the measurement could not fire, not because it did."""
    r = _r()
    assert r["axis2_interpretable_for"] == ["aslamu_muslim", "amanu_mumin", "nasara"]
    d = r["post_run_disclosures"]["D3b_A_LIMIT_ON_AXIS_2_FOUND_AFTER_THE_RUN"]
    assert "THE MEASUREMENT COULD NOT FIRE" in d["note"]
    assert "reporting them as FIXED would overclaim" in d["note"]
    assert len(d["not_attested"]) == 5


def test_where_axis2_CAN_fire_iman_is_mutable_and_islam_is_attested_once():
    r = _r()
    t = r["axis2_mutability"]["terms"]
    assert t["amanu_mumin"] >= 2 and r["axis2_mutability"]["classes"]["amanu_mumin"] == "MUTABLE"
    assert t["aslamu_muslim"] == 1, "9:74, real but below the bar fixed before scoring"
    assert r["axis2_mutability"]["classes"]["aslamu_muslim"] == "FIXED"
    assert "9:74" in r["primary_verdict"]


def test_a_mutable_verdict_does_not_establish_a_governance_state_variable():
    r = _r()
    d = r["post_run_disclosures"]["D4_WHAT_THE_SECOND_AXIS_DOES_AND_DOES_NOT_SHOW"]
    assert "does NOT establish that a term denotes a governance state-variable" in d["note"]


def test_neither_axis_establishes_meaning_or_touches_communities():
    r = _r()
    ids = {g["id"]: g for g in r["gates"]}
    assert ids["Y7_does_either_axis_establish_MEANING"]["weight"] == "excluded"
    assert "neither selects between competing readings" in \
        ids["Y7_does_either_axis_establish_MEANING"]["detail"]
    assert ids["Y8_claims_about_living_communities"]["weight"] == "excluded"


def test_score_is_six_of_six_and_nothing_simulated():
    r = _r()
    assert r["score"] == "6/6" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
