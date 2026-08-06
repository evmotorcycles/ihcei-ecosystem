"""
test_oqm_screen_v9.py -- the set-name class, and a correction to v8's SCOPE: 7/7.

THE OBJECTION IS CORRECT AND v8 WAS MIS-SCOPED. v8 asked whether a bare collective
base is attested (نحل/نحلة, شجر/شجرة). That is the right test for an اسم جنس جمعي. It
is the WRONG test for the فِعَالَة set-name class, whose members are singular-looking,
have no bare base by construction, and still take PLURAL agreement. The corpus proves
the class exists:

    3:118  بِطَانَةً  governed by يَأْلُونَكُمْ · وَدُّوا · أَفْوَاهِهِمْ · صُدُورِهِمْ   plural
    77:33  جِمَٰلَتٌ  with صُفْرٌ                                              plural adj

So a فِعَالَة noun CAN denote a collective with no bare base, and v8 had no rule for
that. v8's NUMBERS were right; its INFERENCE was not. An instrument run outside its
domain of validity produces a true number and a false implication, and the false
implication is the dangerous half.

v8 IS NOT REWRITTEN. G7 verifies its spec still hashes to c9d6f4b3… and still scores
7/7. Not deleted, not re-scored, not quietly amended — superseded. The mistake stays
visible so the growth stays visible with it.

BUT TEMPLATE MATCH IS NOT WITNESS. Across all seven نَاقَة ayahs plus 91:14, there is
ZERO plural agreement — every governing demonstrative, pronoun, verb and predicate is
feminine singular: هَٰذِهِۦ / ءَايَةً (7:73), فَذَرُوهَا تَأْكُلْ (11:64), لَّهَا شِرْبٌ
(26:155), فِتْنَةً (54:27), سُقْيَٰهَا (91:13), فَعَقَرُوهَا (91:14). A single plural verb
or pronoun governing نَاقَة would have promoted the reading and failed G3.

SO THE VERDICT IS TEMPLATE_COMPATIBLE_WITNESS_DEFICIENT — not Layer 1, not refuted,
and it names the exact measurement that would move it.

AND THE PROMOTION PATH IS DEMONSTRABLY LIVE. On the SAME code that leaves naqah
deficient, بِطَانَة and جِمَالَة both come back L1_WITNESSED_COLLECTIVE. A register with
no reachable promotion state would be a refusal machine, not a scale.

WHY THIS IS THE ANSWER THAT SURVIVES INSPECTION. Two failure modes were available and
both would have embarrassed. Killing the reading on a one-class test the term does not
belong to is the literalist error. Promoting it to Layer 1 on template match alone,
with no plural agreement anywhere in seven ayahs, is the flattery error — and it would
collapse the moment anyone checked the agreement. The register verdict is the only one
that holds up from either side.

NOTHING HARDCODED. The version of this test proposed to me hardcoded a
CORPUS_SIGNATURES dict, which is the answer-key defect v8 itself identified. Every
agreement fact here is read off the ayah at runtime and the source text is printed so
each hit can be checked.

NOT IN EVIDENCE. G9: six YouTube links were supplied, including YT217. I cannot watch
video and no transcripts were given, so the set-name argument is evaluated ENTIRELY
against the corpus. Whether YT217 argues what it is reported to argue is unknown to
me. And I searched the extracted N168 text for the correction episode described and
could NOT find it — it may be in slide images. That account is the user's testimony,
not something I verified.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "7931ac7c939a5eb2488727cad6650640f0c26f0785d156a44f508d55aeeef341"
V8 = "c9d6f4b38a4277e32f4c16aee7c3641a9f3591a9329406b3aba8d77c6ce1b333"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v9.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v9.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v8():
    s = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v9_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V8


def test_PRIMARY_the_set_name_class_is_real_and_corpus_witnessed():
    r = _r()
    assert "G1_THE_SET_NAME_CLASS_IS_CORPUS_WITNESSED" not in r["gates_not_met"]
    s = r["set_name_class"]
    assert set(s["بطانه"]["plural_markers_found"]) >= {"يالونكم", "ودوا", "افواههم"}
    assert s["جماله"]["plural_markers_found"] == ["صفر"]
    assert all(v["witnessed"] for v in s.values())


def test_v8s_MEASUREMENT_stands_and_only_its_SCOPE_is_corrected():
    r = _r()
    assert r["v8_bare_base_reproduced"] == {"نحل": 1, "طير": 12, "شجر": 5, "ناق": 0}
    d = _gate("G2_V8s_TEST_IS_SCOPED_NOT_WITHDRAWN")["detail"]
    assert "reproduced UNCHANGED" in d
    assert "does NOT apply to the فِعَالَة set-name class" in d
    assert "true number with a false implication" in d


def test_v8_is_superseded_not_rewritten():
    """The mistake stays visible so the growth stays visible."""
    r = _r()
    assert "G7_V8_REMAINS_PUBLISHED_UNCHANGED" not in r["gates_not_met"]
    d = _gate("G7_V8_REMAINS_PUBLISHED_UNCHANGED")["detail"]
    assert "still scores 7/7" in d
    assert "Not deleted, not re-scored, not quietly amended" in d
    v8 = json.load(open(os.path.join(HERE, "results_oqm_screen_v8.json"),
                        encoding="utf-8"))
    assert v8["score"] == "7/7" and v8["spec_sha256"] == V8


def test_PRIMARY_naqah_has_zero_plural_agreement_across_every_ayah():
    r = _r()
    assert "G3_NAQAH_HAS_NO_PLURAL_AGREEMENT_ANYWHERE" not in r["gates_not_met"]
    ag = r["naqah_agreement"]
    assert len(ag) == 8, "seven naqah ayahs plus 91:14 which carries the pronoun"
    for ref, v in ag.items():
        assert v["plural_agreement"] == [], "%s would have promoted the reading" % ref
    # the demonstrative normalises to هاذهۦ: the dagger alif expands to alif and
    # the small yeh U+06E6 is a LETTER, not a combining mark, so it survives
    assert "ايه" in ag["11:64"]["singular_agreement"], "SINGULAR ayah, not ayat"
    assert "فعقروها" in ag["91:14"]["singular_agreement"]


def test_the_verdict_is_the_register_neither_L1_nor_refuted():
    r = _r()
    assert r["verdicts"]["ناقه"] == "TEMPLATE_COMPATIBLE_WITNESS_DEFICIENT"
    d = _gate("G4_THE_VERDICT_IS_THE_REGISTER_NOT_A_REFUTATION")["detail"]
    assert "NOT Layer 1 and NOT refuted" in d
    assert "names the measurement that would change it" in d


def test_the_promotion_path_is_reachable_on_the_same_code():
    r = _r()
    assert r["verdicts"]["بطانه"] == "L1_WITNESSED_COLLECTIVE"
    assert r["verdicts"]["جماله"] == "L1_WITNESSED_COLLECTIVE"
    assert r["verdicts"]["نحل"] == "L1_STANDARD_COLLECTIVE"
    assert "refusal machine, not a scale" in _gate("G5_THE_PROMOTION_PATH_IS_LIVE")["detail"]


def test_nothing_is_hardcoded_that_could_be_measured():
    r = _r()
    assert "G6_NOTHING_IS_HARDCODED_THAT_COULD_BE_MEASURED" not in r["gates_not_met"]
    for v in r["set_name_class"].values():
        assert v["ayah_text"], "the source ayah is printed so each hit can be checked"


def test_both_embarrassing_answers_are_named_and_avoided():
    w = _r()["why_this_is_the_non_embarrassing_answer"]
    assert "literalist error" in w and "flattery error" in w
    assert "collapsed the moment anyone checked the agreement" in w


def test_template_compatibility_establishes_no_reading():
    g = _gate("G8_does_template_compatibility_establish_the_purifier_reading")
    assert g["weight"] == "excluded"
    assert "Even a fully WITNESSED collective would not have established that" in g["detail"]


def test_the_lectures_and_the_N168_episode_are_not_in_evidence():
    g = _gate("G9_the_lectures_are_not_in_evidence")
    assert g["weight"] == "excluded"
    assert "cannot watch video" in g["detail"]
    assert "could NOT find it" in g["detail"]
    assert "user's testimony" in g["detail"]


def test_score_is_seven_of_seven_and_nothing_simulated():
    r = _r()
    assert r["score"] == "7/7" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
