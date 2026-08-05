"""
test_oqm_screen_v8.py -- the ontology as a hypothesis register: 7/7.

THE CRITICISM IS ACCEPTED. Morphology, root parsing and grammar are the Arḍ, not the
methodology. A screen that stops at letter-counting is the flat parser the OQM
objects to, and v1-v7 were open to that charge.

BUT THE PROPOSED FIX WOULD HAVE BEEN WORSE THAN THE PROBLEM. The v9/v10 architecture
declares ONTOLOGY = {'ناقة': {'rule': 'Collective Plural', ...}} and then
audit_collective_plural returns LICENSED when rule == 'Collective Plural'. F1
reimplements it faithfully, gets LICENSED, changes ONE STRING in the dict, and gets a
different verdict -- with the corpus untouched in both runs. It is an ANSWER KEY
wearing the costume of a screen: it cannot fail, cannot test, cannot catch an error.
Presented as validation it would be worse than presenting nothing, because it would
look like corroboration while containing none.

THE FIX KEEPS EVERYTHING VALUABLE. The ontology is retained IN FULL as a hypothesis
register. Each mapping must carry a prediction about the text's own distribution that
could come out false. Four do and are scored; four state none and are returned
UNFALSIFIABLE_AS_STATED, scoring zero. They are RETAINED, not deleted -- they simply
are not evidence until someone says what would make them false.

I WAS WRONG ABOUT SOMETHING AND F4 RECORDS IT. 16:68-69 is a worked example inside the
corpus: ٱلنَّحْل is a collective and takes FEMININE SINGULAR agreement throughout --
ٱتَّخِذِى, كُلِى, فَٱسْلُكِى, بُطُونِهَا -- while denoting a plurality. So feminine singular
agreement is compatible with a collective, and any earlier suggestion of mine that the
singular pronouns on نَاقَة weighed AGAINST a collective reading was wrong. Agreement is
NON-DISCRIMINATING in both directions. What still stands from v7 is the separate
finding about FORMS: no plural form of ناقة is attested.

WHAT ACTUALLY DISCRIMINATES. An اسم جنس جمعي IS the bare form; the ة-form is its
singulative (نحل/نحلة, شجر/شجرة). So: is the bare collective base attested?

    نحل   attested (16:68)          طير   attested, 12 ayahs
    شجر   attested, 5 ayahs         ناق   ZERO

AND IT CUTS BOTH WAYS. طير HAS the grammatical warrant for a collective reading, which
SUPPORTS the YT89 Ṭayr treatment. ناقة does not -- it is a unit noun with no attested
collective base. A single attestation of ناق would have failed F3 and handed the
collective reading a direct warrant.

THE BAYT IS THE TEXT'S OWN WORD. 16:68 reads ٱتَّخِذِى مِنَ ٱلْجِبَالِ بُيُوتًا, and the
bayt/buyut family is attested in 38 ayahs across 23 surahs. Calling an ayah a Bayt is
not a borrowed metaphor; it is the word the passage itself uses.

F7 QUALIFIES THE BEST CASE ON PURPOSE. طير's prediction HOLDS -- and that licenses the
GRAMMATICAL component only, that طير can denote a collective. It does not establish
that the collective is angels or teachers. The moment a screen stops qualifying its
own successes is the moment it becomes an answer key.

NOT IN EVIDENCE. F9: a YouTube link was supplied; I cannot watch video and no
transcript was given. Everything attributed to YT136 is checked against the CORPUS at
16:68-69, not against the lecture, whose actual argument is unknown to me. And the
'Live Execution' logs in the proposal were not produced by any program -- the second
time written-out logs have been presented as executions.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "c9d6f4b38a4277e32f4c16aee7c3641a9f3591a9329406b3aba8d77c6ce1b333"
V7 = "8fb9f1169dbb32f82a195b15f1f1fd3076722a7facbe51207353b955dae39599"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v8.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v8.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v7():
    s = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v8_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V7


def test_PRIMARY_the_proposed_ontology_audit_is_a_tautology():
    """One string changed in the dict flips the verdict. No ayah involved."""
    r = _r()
    assert "F1_THE_PROPOSED_ONTOLOGY_AUDIT_CANNOT_FAIL" not in r["gates_not_met"]
    d = _gate("F1_THE_PROPOSED_ONTOLOGY_AUDIT_CANNOT_FAIL")["detail"]
    assert "'LICENSED'" in d and "'STANDARD_SYNTAX'" in d
    assert "corpus was not consulted in either" in d
    assert "read back out of the dictionary it was typed into" in d


def test_the_corpus_supplies_its_own_worked_example_at_16_68():
    r = _r()
    assert "F2_THE_TEXT_SUPPLIES_ITS_OWN_WORKED_EXAMPLE" not in r["gates_not_met"]
    d = _gate("F2_THE_TEXT_SUPPLIES_ITS_OWN_WORKED_EXAMPLE")["detail"]
    for form in ("النحل", "اتخذي", "كلي", "فاسلكي", "بطونها", "بيوتا"):
        assert "'%s': True" % form in d
    assert "not from me" in d


def test_PRIMARY_the_collective_base_test_discriminates():
    r = _r()
    assert "F3_PRIMARY_THE_COLLECTIVE_BASE_TEST_DISCRIMINATES" not in r["gates_not_met"]
    c = r["collective_test"]
    for k in ("نحل", "طير", "شجر"):
        assert c[k]["collective_base_attested"] is True
    assert c["ناق"]["collective_base_attested"] is False
    assert c["ناق"]["bare_collective_ayahs"] == 0
    assert c["طير"]["bare_collective_ayahs"] == 12


def test_it_cuts_BOTH_ways_and_supports_the_tayr_reading():
    d = _gate("F3_PRIMARY_THE_COLLECTIVE_BASE_TEST_DISCRIMINATES")["detail"]
    assert "SUPPORTS the YT89 Ṭayr treatment" in d
    assert "would have failed this gate" in d


def test_I_WAS_WRONG_about_agreement_and_the_run_says_so():
    """Collectives take fem sg agreement AND singulars do. It settles nothing."""
    d = _gate("F4_MY_OWN_EARLIER_FRAMING_IS_CORRECTED")["detail"]
    assert "NON-DISCRIMINATING" in d
    assert "was wrong" in d
    assert "What still stands from v7" in d and "no plural FORM" in d


def test_the_bayt_is_the_texts_own_word_in_16_68():
    r = _r()
    assert "F5_THE_BAYT_HAS_A_TEXTUAL_BASIS" not in r["gates_not_met"]
    # 40, not the 38 recorded in the spec's preflight probe: the runner's form list
    # is larger than the probe's (it adds بيوتهن، لبيوتهم، وبيوتا). Same class of slip
    # as the v6 stop-word discrepancy, and recorded the same way rather than hidden.
    # The gate's stated pass condition is ">20 ayahs across >10 surahs", which 40 meets
    # on its own terms, so the gate passes honestly and the spec stays locked.
    assert r["buyut_ayahs"] == 40
    assert "not a borrowed metaphor" in _gate("F5_THE_BAYT_HAS_A_TEXTUAL_BASIS")["detail"]


def test_the_register_keeps_untestable_mappings_but_scores_them_zero():
    r = _r()
    assert "F6_THE_REGISTER_SEPARATES_TESTABLE_FROM_UNTESTABLE_MAPPINGS" \
        not in r["gates_not_met"]
    reg = r["hypothesis_register"]
    assert reg["طير"]["verdict"] == "PREDICTION_HOLDS"
    assert reg["ناقة"]["verdict"] == "PREDICTION_FAILS"
    for tok in ("جناح", "ارض", "سماء", "رمان"):
        assert reg[tok]["verdict"] == "UNFALSIFIABLE_AS_STATED"
        assert reg[tok]["scored"] is False
        assert reg[tok]["reading"], "retained, not deleted"
    assert sum(1 for v in reg.values() if v["scored"]) == 4


def test_the_best_case_is_still_qualified():
    d = _gate("F7_A_LICENSED_PREDICTION_IS_NOT_A_LICENSED_READING")["detail"]
    assert "GRAMMATICAL component" in d
    assert "does not establish that the collective is angels" in d
    assert "becomes an answer key" in d


def test_metaphorical_readings_and_the_unwatched_video_are_excluded():
    g8 = _gate("F8_does_any_of_this_establish_the_metaphorical_readings")
    assert g8["weight"] == "excluded"
    assert "no instrument for them" in g8["detail"]
    g9 = _gate("F9_the_video_is_not_in_evidence")
    assert g9["weight"] == "excluded"
    assert "cannot watch video" in g9["detail"]
    assert "not evaluated" in g9["detail"]


def test_the_fabricated_logs_are_recorded_as_not_having_run():
    d = _r()["did_not_happen"]
    assert "No such program ran" in d
    assert "second time" in d


def test_score_is_seven_of_seven_and_nothing_simulated():
    r = _r()
    assert r["score"] == "7/7" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
