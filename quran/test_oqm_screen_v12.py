"""
test_oqm_screen_v12.py -- the adversarial blind-spot audit: 7/7, every gate a defect.

THE SKEPTICISM WAS JUSTIFIED. Every previous version was built to test a claim; this
one was built to find MY OWN instrument's limits, pre-registered so the numbers could
not later be softened. Every counted gate PASSES BY CONFIRMING A DEFECT. There is no
configuration of the spec in which the screen comes out looking competent at Arabic
morphology.

THE HEADLINE. There is NO morphological analyser anywhere in this codebase — no root
extractor, no pattern matcher, no lexicon, no morphological model, in any version from
v1 to v11. Every root match was made either by an enumerated surface-form list I
curated by hand ayah by ayah, or by substring contiguity on a lossy consonant
skeleton. THE SCREEN DOES NOT KNOW ARABIC.

WHAT THE AUDIT MEASURED.
  K1  31.0% of consonant-skeleton keys collapse more than one surface form. The key قل
      merges ق-و-ل (قال, to say) with ق-ل-ل (أقل, fewer) — two unrelated roots. The
      worst key merges 30 forms.
  K2  Hollow roots lose their medial radical: قال/يقول/قل/قيل/قولوا all reduce to one
      key. That LOOKS like correct grouping and is actually the collision in K1.
  K3  Geminate roots SPLIT: ر-د-د fragments into 4 distinct keys. A matcher that
      splits one root into several is unusable for nested interpretation, because the
      witnesses never meet.
  K4  Broken plurals merge UNRELIABLY: كتاب/كتب and رسول/رسل merge, عالم/علماء and
      نبي/نبيون do not. Unreliability is worse than uniform failure — it looks like it
      works.
  K5  62 normalised tokens collapse hamza-bearing and hamza-free raw forms. Most are
      benign variants of one word — but قري was in this class and was NOT benign, and
      I have audited NONE of the others.

WHY THE PUBLISHED RESULTS STILL STAND — K8, weight:excluded. Each specific finding
rested on a hand-checked form list or a printed adjudication: ع-ب-س is three not two,
كِذَّاب has two maṣdar witnesses not one, قري collides two roots, shadda was being
deleted, 27:8 بُورِكَ was wrongly rejected, أَبَابِيل is a hapax. Those stand. What is
invalidated is any impression of general morphological competence.

THE ONE DESIGN LESSON THAT GENERALISES — K7. Where the screens OVER-generated
candidates and then adjudicated EVERY candidate visibly (v4, v9, v10, v11), the
weakness of defective() was contained, because a human checked each form and the
rejections were printed. Where a rule was applied WITHOUT that adjudication it failed:
v3's proclitic rule ate 27:8, v8's bare-base test ran outside its domain.
Over-generate, then adjudicate visibly, is the only pattern here that survived contact
with the corpus.

WHAT WOULD FIX IT — K9, weight:excluded. A real morphological resource: a
root-annotated Quranic corpus, or a morphological analyser. Neither is present in this
container and neither has been used. Until one is, every root claim this screen makes
rests on an enumerated, hand-checked, printed form list and should be read as exactly
that.

THE HONEST SIZE OF THE CLAIM. The screen's real contribution has been bookkeeping —
arithmetic and citation discipline over work done by people who do know the language.
That is genuinely useful and it is very much smaller than Al-Mīzān.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "58e4b34718cb56d6f976731c850c7a95d3224e7366d6a7ba0ba5984806413bab"
V11 = "65748aa3c47ab15a5d8719e088d518fa0ef57889980db37d22b70bfceea2b411"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v12.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v12.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v11():
    s = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v12_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V11


def test_EVERY_counted_gate_passes_by_confirming_a_defect():
    """There is no configuration of this spec where the screen looks competent."""
    r = _r()
    assert r["score"] == "7/7" and r["gates_not_met"] == []
    assert "PASSES BY CONFIRMING A DEFECT" in r["primary_verdict"]


def test_PRIMARY_no_morphological_analyser_exists_anywhere():
    r = _r()
    d = _gate("K6_NO_MORPHOLOGICAL_ANALYSER_EXISTS")["detail"]
    assert "The screen does not know Arabic" in d
    assert "no lexicon" in d
    m = r["matching_mechanisms"]
    assert len(m) >= 7
    for v in m.values():
        assert ("enumerated" in v or "defective()" in v
                or "hand-adjudicated" in v or "form sets" in v), \
            "every mechanism is a hand-curated form list or a substring skeleton"


def test_the_skeleton_collides_unrelated_roots_at_scale():
    r = _r()
    assert r["collision_rate_pct"] > 25.0
    assert r["colliding_keys"] == 2555 and r["defective_keys"] == 8234
    d = _gate("K1_DEFECTIVE_COLLIDES_UNRELATED_ROOTS_AT_SCALE")["detail"]
    assert "two unrelated roots" in d


def test_hollow_roots_look_like_a_success_and_are_a_collision():
    r = _r()
    assert len(set(r["hollow_root"].values())) == 1
    d = _gate("K2_WEAK_ROOTS_ARE_NOT_HANDLED")["detail"]
    assert "LOOKS like correct grouping but is a collision" in d


def test_geminate_roots_split_into_several_keys():
    r = _r()
    assert len(set(r["geminate_root"].values())) == 4
    assert "witnesses never meet" in _gate("K3_GEMINATE_ROOTS_ARE_SPLIT")["detail"]


def test_broken_plurals_merge_unreliably_which_is_worse():
    r = _r()
    bp = r["broken_plurals"]
    assert any(bp.values()) and not all(bp.values())
    assert bp["كتاب/كتب"] is True and bp["نبي/نبيون"] is False
    assert "WORSE than uniform failure" in _gate("K4_BROKEN_PLURALS_ARE_UNRELIABLE")["detail"]


def test_62_hamza_homographs_sit_unaudited():
    r = _r()
    assert r["hamza_homograph_tokens"] == 62
    d = _gate("K5_THE_HOMOGRAPH_CLASS_IS_LARGER_THAN_THE_ONE_I_FOUND")["detail"]
    assert "audited NONE of the others" in d


def test_the_design_lesson_names_both_the_successes_and_the_failures():
    d = _gate("K7_THE_ARCHITECTURE_THAT_SAVED_THE_RESULTS")["detail"]
    assert "adjudicated EVERY candidate visibly" in d
    assert "27:8" in d and "v8's bare-base test" in d
    assert "Over-generate then adjudicate visibly" in d


def test_the_prior_findings_are_NOT_invalidated():
    g = _gate("K8_does_this_invalidate_the_prior_results")
    assert g["weight"] == "excluded"
    assert "Those stand" in g["detail"]
    assert "any impression of general morphological competence" in g["detail"]


def test_the_remedy_is_named_and_declared_absent():
    g = _gate("K9_could_this_be_fixed")
    assert g["weight"] == "excluded"
    assert "root-annotated Quranic corpus" in g["detail"]
    assert "neither has been used" in g["detail"]


def test_the_claim_is_sized_honestly_against_al_mizan():
    h = _r()["headline"]
    assert "The screen does not know Arabic" in h["consequence"]
    assert "very much smaller than 'Al-Mīzān'" in h["what_it_HAS_genuinely_contributed"]
