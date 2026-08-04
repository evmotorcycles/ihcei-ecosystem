"""
test_oqm_screen.py -- locks the OQM Lexical Screen: 4/5.

WHAT THIS IS. Not another reading. An INSTRUMENT for questions of the shape "is this word a
label or an act?", built to be applied uniformly to a whole vocabulary, with a decision
boundary fixed before any term was scored, and required by a gate to be capable of
returning NO.

A framework becomes more comprehensive by acquiring ways to SETTLE questions, not by
accumulating answers to them.

IT IS BUILT FROM THE TEST THAT WORKED AND EXCLUDES THE ONE THAT DID NOT.
  kept       designation -- 7 of 7 control proper nouns scored zero      (spec 708ac80e)
  discarded  VIF on word counts -- 99.8% of RANDOM unrelated pairs
             cleared its bar, so it separated nothing                    (spec af27d2c9)

CALIBRATED AT BOTH ENDS, which is the part that makes it an instrument rather than an
opinion. A screen with only a negative control can be blind; one with only a positive
control can be indiscriminate. Only both together show it returns different answers to
different inputs.

    negative controls   Firawn, Thamud, 'Aad, Israil, Majus, Rum, Quraysh    all 0
    positive controls   kafaru 171 | 'amilu 58 | zalamu 33                   all >= 20
    separation                                                              33

THE CLASSIFICATION OF THE OQM VOCABULARY.

    ACTION      amanu / mumin        268
                ittaqaw / muttaqin    27
    AMBIGUOUS   hadu / yahud          10
                ashraku / mushrikun    9
                sabaru / sabirun       6
    LABEL       nasara                 2
                nafaqu / munafiqun     2
                aslamu / muslim        1
                hawariyyun             0
                sabiin                 0   <- see below, this one is NOT a label

X6 PASSED, AND IT IS THE GATE THAT MATTERS. Five of ten terms classify as LABEL. A screen
that certified every term the framework favours would be agreeing rather than screening, and
X6 exists to record that as broken instead of as confirmation. It disagrees with the
framework on muslim, munafiqun, nasara and hawariyyun.

X1 FAILED, AND THE FAILURE IS A SCOPE CONDITION WORTH HAVING. The screen has a PRECONDITION:
the root must supply an attested finite verb somewhere in the text. Sabiin does not -- the
S-B-A root yields no finite verb at all -- so that term is UNTESTABLE-HERE by this
instrument, which is a DIFFERENT verdict from LABEL. Filing "the root has verbs but the text
never uses them for this group" (nasara, hawariyyun) together with "the root has no verbs at
all" (sabiin) would merge two findings this programme keeps apart.

THREE TOKENISATION DEFECTS WERE CAUGHT BY THE CALIBRATION GATES, NOT BY INSPECTION.
  1. base() strips a leading kaf as the 'like/as' proclitic, turning kafaru into faru. The
     commonest verbal designation in the text scored 3 instead of 171. X3 caught it.
  2. The declared hawariyyun forms missed the attested yuhawiruhu. X1 caught it.
  3. 'and they did' is written wa-'amilu as ONE token, so 'amilu scored 8 instead of 58.
     X3 caught it, and the fix is a UNIFORM proclitic rule applied identically to every
     term and every control -- not a patch to one word list.
Each fix changed the instrument, never a threshold, and the boundary set before scoring
stands unmoved.

WHAT AN ACTION CLASSIFICATION DOES NOT BUY. It does not vindicate any reading. It
establishes that the text uses a verbal group-designation, which is a far smaller fact than
a reading, and it says nothing about what any word means (X7) or about any living community
(X8).
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "8257dfcca40d0be024bac323e45137eba27277200243b3c1a7893d6f08349204"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "oqm_screen_prereg.json"),
                          encoding="utf-8"))


def test_spec_locked():
    got = hashlib.sha256(json.dumps(_spec(), sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED


def test_the_spec_says_an_instrument_not_more_readings():
    w = _spec()["WHY_AN_INSTRUMENT_RATHER_THAN_MORE_READINGS"]
    assert "not by accumulating answers" in w["what_would_NOT_do_that"]
    assert "capacity to classify a term the framework favours as a LABEL" in w["what_this_supplies"]


def test_it_is_built_from_the_test_that_discriminated():
    w = _spec()["WHY_AN_INSTRUMENT_RATHER_THAN_MORE_READINGS"]["the_lesson_it_is_built_on"]
    assert "7 of 7 control proper nouns scored zero" in w
    assert "99.8 percent of random unrelated word pairs cleared its bar" in w
    r = _r()
    d = r["post_run_disclosures"]["D2_IT_IS_BUILT_FROM_THE_TEST_THAT_WORKED"]
    assert "708ac80e" in d["kept"] and "af27d2c9" in d["discarded"]


def test_the_boundary_was_fixed_before_any_term_was_scored():
    b = _spec()["THE_SCREEN"]["the_decision_boundary_fixed_before_any_term_was_scored"]
    assert b["LABEL"].startswith("fewer than 5")
    assert b["ACTION"].startswith("20 or more")
    src = open(os.path.join(HERE, "oqm_screen.py"), encoding="utf-8").read()
    assert "LABEL_MAX, ACTION_MIN, X4_GAP, X6_MIN_LABELS = 5, 20, 20, 2" in src


def test_THE_NEGATIVE_CONTROL_HOLDS():
    r = _r()
    assert "X2_NEGATIVE_CONTROL" not in r["gates_not_met"]
    assert set(r["negative_controls"].values()) == {0}
    assert len(r["negative_controls"]) == 7


def test_THE_POSITIVE_CONTROL_HOLDS():
    r = _r()
    assert "X3_POSITIVE_CONTROL" not in r["gates_not_met"]
    assert all(v >= 20 for v in r["positive_controls"].values())
    assert r["positive_controls"]["kafaru"] > 100


def test_THE_SCREEN_HAS_A_CLEAN_DECISION_BOUNDARY():
    """Both calibrators, separated by more than the ambiguous band."""
    r = _r()
    assert "X4_PRIMARY_THE_SCREEN_HAS_A_CLEAN_DECISION_BOUNDARY" not in r["gates_not_met"]
    assert r["separation"] >= 20
    assert r["separation"] == min(r["positive_controls"].values()) - \
        max(r["negative_controls"].values())


def test_X6_THE_SCREEN_SAYS_NO_TO_HALF_THE_VOCABULARY():
    """The gate that catches an instrument flattering its author."""
    r = _r()
    assert "X6_ANTI_RUBBER_STAMP_THE_SCREEN_MUST_BE_ABLE_TO_SAY_NO" not in r["gates_not_met"]
    labels = [k for k, c in r["classes"].items() if c == "LABEL"]
    assert len(labels) >= 2
    assert "aslamu_muslim" in labels, "it disagrees with the framework on muslim"
    assert "nasara" in labels


def test_the_classification_is_differentiated_not_uniform():
    r = _r()
    cls = set(r["classes"].values())
    assert cls == {"ACTION", "AMBIGUOUS", "LABEL"}, "all three classes are populated"
    assert r["classes"]["amanu_mumin"] == "ACTION"
    assert r["under_test"]["amanu_mumin"] > 200


def test_X1_FAILED_and_it_is_a_scope_condition_not_a_bug():
    """sabiin has no attested finite verb: UNTESTABLE-HERE, not LABEL."""
    r = _r()
    assert "X1_integrity" in r["gates_not_met"]
    assert r["attested_forms"]["sabiin"] == []
    assert r["attested_forms"]["hawariyyun"] != [], \
        "hawariyyun DOES have attested verbs and still scores 0 -- a real LABEL"
    d = r["post_run_disclosures"]["D3b_ONE_TERM_CANNOT_BE_SCREENED_AT_ALL_AND_THAT_IS_NOT_A_LABEL"]
    assert "different verdict from LABEL" in d["note"]
    assert "PRECONDITION" in d["note"]


def test_the_uniform_proclitic_rule_is_applied_to_controls_too():
    src = open(os.path.join(HERE, "oqm_screen.py"), encoding="utf-8").read()
    assert "UNIFORM proclitic rule, applied identically to every term and every control" in src
    assert "never on the clitic-stripped base" in src


def test_no_meaning_and_no_community_claims():
    r = _r()
    ids = {g["id"]: g for g in r["gates"]}
    assert ids["X7_does_a_classification_establish_MEANING"]["weight"] == "excluded"
    assert "UNTESTABLE-HERE" in ids["X7_does_a_classification_establish_MEANING"]["detail"]
    assert ids["X8_claims_about_living_communities"]["weight"] == "excluded"
    d = r["post_run_disclosures"]["D4_WHAT_AN_ACTION_CLASSIFICATION_DOES_NOT_BUY"]
    assert "does not vindicate any reading" in d["note"]


def test_score_is_four_of_five_and_nothing_simulated():
    r = _r()
    assert r["score"] == "4/5"
    assert r["gates_not_met"] == ["X1_integrity"]
    assert r["simulated_values"] == 0
    assert r["n_ayahs"] == 6236
