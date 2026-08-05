"""
test_oqm_screen_v5.py -- witness independence: 7/7.

THE SKILL v5 ADDS. The Janah is not straightforward, and v3/v4 pretended it was. They
counted one wing per DISTINCT SURAH. That proxy is wrong in BOTH directions:

  too LOOSE   one fixed formula repeated across four surahs is one piece of evidence
              wearing four hats, and a surah counter cannot see it
  too TIGHT   two unrelated passages seventeen ayahs apart inside one surah are two
              genuine contexts, and a surah counter merges them

A wing is now an independent CONTEXT: witnesses merge if their ayahs are >= 0.50
Jaccard-similar (J1, formulaic, EVEN ACROSS SURAHS) or sit within 3 ayahs of each
other in one surah (J2, same passage). Both thresholds were fixed before anything was
re-adjudicated.

IT MUST BE ABLE TO TAKE A VERDICT AWAY, AND IT CAN. A claim resting only on 2:136 and
3:84 CLEARS under the surah rule -- two surahs -- and is WITHHELD as ONE_WING under
J1, because the two ayahs are 0.6774 similar. One formula, two surahs, one wing.

AND IT MOSTLY RELAXES, WHICH IS REPORTED BECAUSE IT IS TRUE. Across the five
re-adjudicated sets the corrected rule relaxes three and changes none in the other
direction. A stricter rule would have sounded more rigorous. Accuracy beat severity,
and the direction of every change is in the output.

THE MOST INSTRUCTIVE CASE CHANGES ITS COUNT BY NOTHING. N159's nufarriq set scores 3
under both rules -- but for different reasons, and only one of them is right. The old
rule merged 2:136 with 2:285 because they share surah 2, though they say different
things. The new rule merges 2:136 with 3:84, which are the same formula in different
surahs. Same number, right grouping.

J4 -- A JANAH MUST BE TEXTUAL. It was put to me that An-Naqah (YT127) and As-Saah
(YT133) together supply the second wing establishing Iqra as a two-hop channel
initialisation. A link BETWEEN TERMS requires the terms to meet somewhere. Measured
across all 6,236 ayahs, every pairwise intersection is EMPTY: naqah&q-r-', saah&q-r-',
naqah&saah. Not one ayah contains any two of the three.

AND SCARCITY DOES NOT EXPLAIN IT. As-Saah is in 43 ayahs across 26 surahs and q-r-' in
81. Both are abundant. They never meet, which is a far stronger statement than rare.

WHAT THAT DOES AND DOES NOT MEAN. V8 is weight:excluded and says so: NO_TEXTUAL_LINK
does not refute the reading. It places it outside the class of claims OQM's own
evidence rule can support -- precisely what N159 says about a dictionary opinion. The
reading may be true. It is not ESTABLISHED by a Janah, because there is no Janah.

WHAT I HAVE NOT READ. V9 is weight:excluded: YT127 and YT133 were NOT among the
sixteen documents supplied. Every characterisation of them here comes from the prompt,
not from a source. This run does not test whether An-Naqah means a purifier cohort or
As-Saah means irrigators. It tests only whether the terms meet in the text.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "5f43d480f2af1616f365b925a2ea887936cbffdccf337efd2d8452fec229719d"
V4 = "de629189f2e6712688e6602b1d1ae7da7ed071353a4972c546129a492058645e"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v5.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v5.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v4():
    s = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v5_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V4


def test_PRIMARY_the_new_rule_can_withhold_a_verdict_the_old_one_granted():
    """2:136 + 3:84 -- one formula, two surahs, one wing. Otherwise it is decoration."""
    r = _r()
    assert "V2_FORMULAIC_COLLAPSE_CAN_WITHHOLD_A_VERDICT_THE_OLD_RULE_GRANTED" \
        not in r["gates_not_met"]
    d = _gate("V2_FORMULAIC_COLLAPSE_CAN_WITHHOLD_A_VERDICT_THE_OLD_RULE_GRANTED")
    assert "-> CLEARS" in d["detail"] and "-> ONE_WING" in d["detail"]
    assert "0.6774" in d["detail"]


def test_the_correction_mostly_RELAXES_and_that_is_reported():
    """A stricter rule would flatter the correction. This one is just more accurate."""
    r = _r()
    dirs = [v["direction"] for v in r["re_adjudication"].values()]
    assert dirs.count("RELAXED") == 3
    assert "TIGHTENED" not in dirs
    assert "over-merging" in _gate(
        "V1_THE_RULE_MOVES_IN_BOTH_DIRECTIONS_AND_BOTH_ARE_REPORTED")["detail"]


def test_nufarriq_keeps_its_count_but_by_the_RIGHT_grouping():
    """Old merged 2:136+2:285 (same surah). New merges 2:136+3:84 (same formula)."""
    n = _r()["re_adjudication"]["N159_nufarriq"]
    assert n["old_rule_surahs"] == 3 and n["new_rule_wings"] == 3
    assert n["direction"] == "UNCHANGED"
    assert n["merges"] == [{"a": "2:136", "b": "3:84", "jaccard": 0.6774,
                            "reason": "J1_formulaic"}]
    assert n["wing_groups"] == [["2:136", "3:84"], ["2:285"], ["4:152"]]


def test_passage_adjacency_merges_96_1_with_96_3():
    r = _r()
    assert "V3_PASSAGE_ADJACENCY_FIRES" not in r["gates_not_met"]
    d = _gate("V3_PASSAGE_ADJACENCY_FIRES")["detail"]
    assert "['96:1', '96:3']" in d and "-> 2 wings" in d


def test_N167_survives_the_stricter_rule_on_genuinely_independent_contexts():
    n = _r()["re_adjudication"]["N167_sulala"]
    assert n["new_rule_wings"] == 3 and n["new_verdict"] == "CLEARS"
    assert n["merges"] == [], "no two of the three s-l-l witnesses are formulaic"


def test_PRIMARY_the_naqah_saah_iqra_link_has_no_textual_janah():
    r = _r()
    assert "V5_PRIMARY_THE_NAQAH_SAAH_IQRA_LINK_HAS_NO_TEXTUAL_JANAH" \
        not in r["gates_not_met"]
    c = r["the_claim_put_to_me"]
    assert c["intersections"] == {"naqah_and_qr": [], "saah_and_qr": [],
                                  "naqah_and_saah": []}
    assert c["verdict"] == "NO_TEXTUAL_LINK"


def test_the_empty_intersections_are_not_explained_by_scarcity():
    c = _r()["the_claim_put_to_me"]
    assert c["saah_ayah_count"] == 43 and c["qr_ayah_count"] > 70
    assert "far stronger than rare" in _gate(
        "V7_THE_FINDING_IS_NOT_THE_TERMS_ARE_RARE".replace(
            "THE_TERMS", "THAT_THE_TERMS"))["detail"]


def test_the_naqah_matcher_rejects_their_necks():
    r = _r()
    assert "V6_THE_NAQAH_MATCHER_REJECTS_THE_NECKS" not in r["gates_not_met"]
    assert r["the_claim_put_to_me"]["naqah_ayahs"] == [
        "7:73", "7:77", "11:64", "17:59", "26:155", "54:27", "91:13"]
    assert "3-n-q" in _gate("V6_THE_NAQAH_MATCHER_REJECTS_THE_NECKS")["detail"]


def test_no_textual_link_is_not_a_refutation():
    g = _gate("V8_does_NO_TEXTUAL_LINK_refute_the_reading")
    assert g["weight"] == "excluded"
    assert "It does not" in g["detail"]
    assert "not ESTABLISHED by a Janah" in g["detail"]


def test_the_unread_videos_are_declared_unread():
    g = _gate("V9_the_source_videos_are_not_in_evidence")
    assert g["weight"] == "excluded"
    assert "have not" in g["detail"] and "read them" in g["detail"]
    assert "comes from the prompt, not from a source" in g["detail"]


def test_the_caption_argument_and_the_models_are_not_tested():
    nt = _r()["not_tested"]
    assert "a transcription tool, not about the Quran" in nt["the_caption_argument"]
    assert "simulator rule forbids" in nt["the_quantitative_models"]
    assert "None is measured here or anywhere in this repository" in \
        nt["the_quantitative_models"]


def test_placement_in_the_novora_initiative_is_recorded():
    p = _r()["placement"]
    assert "LISM" in p and "DCM" in p and "licensing" in p
    assert "weight:excluded" in p


def test_score_is_seven_of_seven_and_nothing_simulated():
    r = _r()
    assert r["score"] == "7/7" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
