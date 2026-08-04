"""
test_qlex.py -- locks the Quran lexical-behaviour run: 5/6.

THE QUESTION. Do 'yahud' and 'nasara' behave in this text like PROPER NOUNS, or like
DEVERBAL DESCRIPTORS -- words built on something done? Those two readings predict different
textual behaviour, the text is fixed and public, and counting is mechanical.

WHAT THIS IS NOT, and both are gates rather than footnotes:
  V8  It does NOT establish what the words MEAN. Many ordinary ethnonyms are historically
      deverbal in every language, so a pass is CONSISTENT WITH a descriptor reading and
      does not select it.
  V9  It is NOT a claim about Jewish or Christian people, communities or beliefs. The units
      of analysis are Arabic word-forms in one text, and the result stops there.

THE NAIVE TEST FAILS, AND THE TEXT SUPPLIES ITS OWN COUNTEREXAMPLE. "The word shares a root
with a verb, therefore it is deverbal" is worthless. The tribe name 'Aad is surface-identical
to the verb 'aada (returned, root '-W-D, 2:275) and to 'aadin (transgressor, root '-D-W,
2:173). A shared-letters test would call a proper noun deverbal.

THE TEST ACTUALLY USED. Does the text DESIGNATE THE GROUP with a finite verb -- a relative
clause "those who [verb]" or a vocative "O you who [verb]" -- rather than only with a noun?
A proper noun cannot be conjugated to name its own bearers.

    yahud    noun 8 times   |  named by the finite verb 'hadu' 10 TIMES
                               including a direct vocative address at 62:6
    controls 7 proper nouns |  named by a finite verb 0 times  (Firawn, Thamud, 'Aad,
                               Israil, Majus, Rum, Quraysh)

The ablation held, so the behaviour discriminates rather than being an artefact.

AND V4 FAILED, WHICH IS THE MOST INFORMATIVE PART OF THE RUN. The pre-registered prediction
was that 'nasara' is never designated by a finite verb. The matcher found 2 hits, at 8:72
and 8:74 -- "wa alladhina aawaw wa NASARU", those who sheltered and helped.

Those designate the ANSAR, the helpers, a DIFFERENT GROUP from the nasara. The gate is
scored FAILED as measured, because the implementation cannot resolve referents and a gate
is not re-scored after the fact. But the substance is sharper than a pass would have been:

    the construction "those who helped" EXISTS in this text and is applied to a group --
    just never to the nasara. The nasara are named by a noun 14 times and by a verb 0 times,
    while the root supplies 82 finite verb tokens elsewhere.

SO THE TWO WORDS DO NOT BEHAVE THE SAME, and any single symmetric claim covering both is
not supported by this test. Reporting them together would hide the asymmetry that IS the
result.

TWO SPECIFIC LEXICAL CLAIMS WERE CHECKED AND BOTH HOLD.
  V6  Every finite verbal occurrence of the root M-L-L in the entire text falls in 2:282.
      Three tokens, one ayah.
  V7  2:120 does carry the SINGULAR 'millatahum' while naming both groups.

DISCLOSED WEAKNESS. V2's threshold of >= 5 was set after the benchmark count of 10 had been
seen during normalisation work, so V2 is a WEAK pre-registration and is labelled as such.
V3 and V4 were not informed that way, and they are what carry the run.

NORMALISATION MATTERED MORE THAN THE STATISTICS. Three decisions each changed the answer:
the dagger alif U+0670 is a long vowel and must become an alif; a dagger alif following
alif-maqsura is that letter's own vowel and is not an extra alif; and combining marks must
be removed by Unicode category, because a hand-written range missed U+064B-U+0652 and
silently corrupted every count in a first attempt.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "708ac80e3b14096c0eee90df0eae918596c565d78f005541c06b5dd1111fb6aa"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "qlex.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_qlex.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "quran_lexical_prereg.json"),
                          encoding="utf-8"))


def test_spec_locked():
    got = hashlib.sha256(json.dumps(_spec(), sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED


def test_the_spec_puts_both_limits_up_front_as_gates():
    w = _spec()["WHAT_THIS_IS_AND_IS_NOT"]
    assert "does not establish it" in w["WHAT_IT_CANNOT_DO"]
    assert "That limit is a gate (V8), not a footnote" in w["WHAT_IT_CANNOT_DO"]
    o = w["OUT_OF_SCOPE_BY_CONSTRUCTION"]
    assert "is a claim about Jewish or Christian people" in o and o.startswith("Nothing in this specification")
    assert "No gate references any living community" in o


def test_the_dataset_is_committed_and_intact():
    r = _r()
    assert r["n_ayahs"] == 6236
    assert "V1_integrity" not in r["gates_not_met"]
    c = r["counts"]
    assert (c["nasara_noun"], c["yahud_noun"], c["hadu_finite_verb"]) == (14, 8, 10), \
        "reproduces published benchmark counts"


def test_the_naive_root_sharing_test_is_refused_and_shown_why():
    r = _r()
    g = [x for x in r["gates"] if x["id"] == "V5_the_homograph_demonstration"][0]
    assert g["weight"] == "excluded" and g["met"] is None
    assert "surface-identical" in g["detail"]
    assert "would call 'Aad deverbal" in g["detail"]
    d = r["post_run_disclosures"]["D3_WHY_ROOT_SHARING_WAS_NOT_USED"]
    assert "false positive on a proper noun" in d["note"]


def test_YAHUD_IS_DESIGNATED_BY_A_FINITE_VERB():
    r = _r()
    assert "V2_PRIMARY_yahud_IS_designated_by_a_finite_verb" not in r["gates_not_met"]
    c = r["counts"]
    assert c["yahud_group_designated_by_verb"] == 10
    assert c["yahud_group_designated_by_verb"] > c["yahud_noun"], \
        "the verbal designation is MORE frequent than the noun"
    refs = {h["ref"] for h in r["yahud_verb_designations"]}
    assert "62:6" in refs, "including a direct vocative address"


def test_THE_ABLATION_HELD_so_the_behaviour_discriminates():
    r = _r()
    assert "V3_ABLATION_control_proper_nouns_are_NOT" not in r["gates_not_met"]
    ctrl = r["counts"]["control_group_designated_by_verb"]
    assert len(ctrl) == 7 and set(ctrl.values()) == {0}
    assert "V3 WAS MET" in r["primary_verdict"]


def test_V4_FAILED_AND_THE_FAILURE_IS_THE_SHARPEST_RESULT():
    """The 2 hits designate the Ansar, a different group. Scored failed anyway."""
    r = _r()
    assert "V4_THE_SPLIT_nasara_is_NOT_designated_by_a_finite_verb" in r["gates_not_met"]
    assert r["counts"]["nasara_group_designated_by_verb"] == 2
    g = [x for x in r["gates"]
         if x["id"] == "V4_THE_SPLIT_nasara_is_NOT_designated_by_a_finite_verb"][0]
    assert "8:72" in g["detail"] and "8:74" in g["detail"]


def test_the_two_words_do_not_behave_the_same():
    r = _r()
    c = r["counts"]
    assert c["nasara_noun"] > c["yahud_noun"], "nasara is the commoner noun"
    assert c["yahud_group_designated_by_verb"] > c["nasara_group_designated_by_verb"] * 4
    d = r["post_run_disclosures"]["D2_THE_TWO_WORDS_DO_NOT_BEHAVE_THE_SAME"]
    assert "single symmetric claim covering both words is NOT supported" in d["note"]
    assert "hide the asymmetry" in d["note"]


def test_the_root_supplies_plenty_of_verbs_that_are_simply_not_used_that_way():
    r = _r()
    assert r["counts"]["nsr_finite_verbs"] > 50
    assert r["counts"]["ansar_noun"] == 11


def test_the_M_L_L_claim_checks_out():
    r = _r()
    assert "V6_M_L_L_verbal_usage_is_confined_to_2_282" not in r["gates_not_met"]
    g = [x for x in r["gates"]
         if x["id"] == "V6_M_L_L_verbal_usage_is_confined_to_2_282"][0]
    assert "['2:282']" in g["detail"]


def test_the_2_120_singular_claim_checks_out():
    r = _r()
    assert "V7_2_120_uses_a_SINGULAR_millah_for_two_named_groups" not in r["gates_not_met"]


def test_the_weak_preregistration_is_admitted():
    r = _r()
    d = r["post_run_disclosures"]["D2b_THE_V2_THRESHOLD_WAS_INFORMED_BY_A_PRE_LOCK_COUNT"]
    assert "WEAK pre-registration" in d["note"]
    assert "V3 and V4 were NOT informed this way" in d["note"]


def test_no_meaning_and_no_community_claim_is_made():
    r = _r()
    ids = {g["id"]: g for g in r["gates"]}
    assert ids["V8_does_any_of_this_establish_what_the_words_MEAN"]["weight"] == "excluded"
    assert "UNTESTABLE-HERE" in ids["V8_does_any_of_this_establish_what_the_words_MEAN"]["detail"]
    v9 = ids["V9_claims_about_actual_communities"]
    assert v9["weight"] == "excluded" and "OUT OF SCOPE" in v9["detail"]
    assert "No meaning is established" in r["primary_verdict"]
    d = r["post_run_disclosures"]["D4_WHAT_IS_NOT_CLAIMED"]
    assert "Nothing here is a statement about Jewish or Christian people" in d["note"]


def test_score_is_five_of_six_and_nothing_simulated():
    r = _r()
    assert r["score"] == "5/6"
    assert r["gates_not_met"] == [
        "V4_THE_SPLIT_nasara_is_NOT_designated_by_a_finite_verb"]
    assert r["simulated_values"] == 0
