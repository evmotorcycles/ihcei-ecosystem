"""
test_oqm_screen_v4.py -- locks the four-narrative licensing run: 6/7, W2 NOT MET.

WHAT v4 ASKS. v3 extracted two rules from the OQM documents -- the Janah two-witness
rule (YT89 on 6:38) and the 58:11 coverage rule (N159). v4 puts one question to the
central root of four narratives: is a nested interpretation of this root
METHODOLOGICALLY LICENSED under OQM's own rules? That is, is the root attested widely
enough that the QURAN can define it internally, rather than a dictionary defining it
from outside? N159 shows OQM failing exactly this test on purpose at 58:11 and calling
the result an unsupported opinion, so it is a rule that can fail.

ALL FOUR ARE LICENSED.
    N157 Barakah   b-r-k   32 ayahs / 22 surahs   includes 27:8 بُورِكَ
    N182 al-Ɛasr   3-s-r    5 ayahs /  4 surahs
    N167 Sulalah   s-l-l    3 ayahs /  3 surahs   EXACTLY 23:12, 24:63, 32:8
    Iqra           q-r-'   79 ayahs / 42 surahs

W5 IS THE RISKY ONE AND IT HELD. N167 states a linguistic basis for س-ل-ل and builds
it from three ayahs. The screen was required to find EXACTLY those three -- no more,
no fewer. Had N167 cited an ayah the root does not occur in, or missed one it does,
this fails. It did not.

WHY THIS RUN SCORES 6/7 AND IS PUBLISHED THAT WAY. W2 requires that accepted plus
rejected exactly exhaust the mechanically generated candidate set, so that no surface
form is silently dropped. It FAILED on one character: the locked spec lists the
rejected form as بركنهۥ (U+06E5 SMALL WAW) where the corpus has بركنهۦ (U+06E6 SMALL
YEH). My transcription, caught by my own gate.

The spec was NOT edited to make it pass. Editing a locked spec so a gate clears is the
immunisation this whole framework exists to prevent, and a reconciliation gate that
gets relaxed the first time it fires was never a check. The substantive results are
unaffected and that is verified below rather than asserted: 51:39 بِرُكْنِهِۦ is root
r-k-n and is excluded under EITHER spelling, so the accepted set, the ayah counts and
all four licensing verdicts stand.

THE INSTRUMENT HAD TO BE FIXED BEFORE ANY OF THIS COULD BE MEASURED. v3's automatic
proclitic rule strips a leading و/ف/ب/ك/ل run. On b-r-k, whose FIRST RADICAL is ب, it
ate the radical -- rejecting 27:8 بُورِكَ, the single ayah N157's entire segment is
built on, and 17:1 بَٰرَكْنَا -- while ACCEPTING أخباركم (kh-b-r) and صبرك (s-b-r),
where a -kum/-ka suffix leaves ب-ر-ك spuriously contiguous. On this root the rule did
not merely miss, it INVERTED the answer. W1 reproduces that failure rather than
describing it. v3 is not re-scored: its gates concerned f-s-h and j-l-s, where waṣla
rescues the stem and the first radical is not a proclitic letter.

WHAT LICENSED DOES NOT MEAN. It does not mean any reading is correct -- it means the
evidence needed to argue is present. W8 and W9 are weight:excluded and say so: nothing
here tests E = U*D, the cascade product, revocation latency, a Bayesian engine, or
Al-Mizan, none of which is measured anywhere in this repository against Quranic text.
The 'Iqra from a pregnant she-camel' etymology is likewise NOT tested -- it comes from
traditional lexicography, precisely the source N159 rules out as yielding 'only a
plausible opinion'.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "de629189f2e6712688e6602b1d1ae7da7ed071353a4972c546129a492058645e"
V3 = "b5eaa3051ebe499b7751ac72c477204061a5414ff4f0613e21414c02e940c669"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v4.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v4.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v4_prereg.json"),
                          encoding="utf-8"))


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v3():
    s = _spec()
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V3


def test_PRIMARY_the_v3_rule_inverted_the_answer_on_b_r_k():
    """Not described -- reproduced."""
    r = _r()
    assert "W1_THE_V3_RULE_IS_SHOWN_TO_FAIL_ON_B_R_K" not in r["gates_not_met"]
    d = _gate("W1_THE_V3_RULE_IS_SHOWN_TO_FAIL_ON_B_R_K")["detail"]
    assert "27:8" in d and "inverted the answer" in d


def test_THE_RECONCILIATION_GATE_FAILED_AND_THE_SPEC_WAS_NOT_EDITED():
    """One character. The gate caught it and the spec stays locked."""
    r = _r()
    assert "W2_EVERY_CANDIDATE_IS_ADJUDICATED_AND_PRINTED" in r["gates_not_met"]
    assert r["narratives"]["N157_barakah"]["unadjudicated"] == ["بركنهۦ"]
    assert r["narratives"]["N157_barakah"]["phantom_forms_not_in_corpus"] == ["بركنهۥ"]
    for k in ("N182_al_asr", "N167_sulalah", "IQRA_quran"):
        assert r["narratives"][k]["unadjudicated"] == []
        assert r["narratives"][k]["phantom_forms_not_in_corpus"] == []


def test_the_typo_does_not_touch_a_single_substantive_result():
    """Verified, not asserted: 51:39 is r-k-n and is out under either spelling."""
    r = _r()
    b = r["narratives"]["N157_barakah"]
    assert "51:39" not in b["ayahs"]
    assert b["n_ayahs"] == 32 and b["n_surahs"] == 22
    assert all(v["licensed"] for v in r["narratives"].values())


def test_all_four_narratives_are_licensed_under_OQMs_own_rules():
    r = _r()
    for k in ("N157_barakah", "N182_al_asr", "N167_sulalah", "IQRA_quran"):
        n = r["narratives"][k]
        assert n["coverage_rule"] == "screenable"
        assert n["janah_rule"] == "CLEARS"
        assert n["licensed"] is True
        assert n["n_surahs"] >= 2


def test_N157_includes_the_ayah_v3_wrongly_rejected():
    r = _r()
    assert "W6_N157_IS_LICENSED_ONCE_THE_INSTRUMENT_IS_FIXED" not in r["gates_not_met"]
    assert "27:8" in r["narratives"]["N157_barakah"]["ayahs"]


def test_RISKY_N167_cited_exactly_the_ayahs_the_root_occurs_in():
    """No more, no fewer. Had N167 cited a fourth, or missed one, this fails."""
    r = _r()
    assert "W5_N167_IS_LICENSED_AND_USED_ITS_OWN_WITNESSES" not in r["gates_not_met"]
    assert r["narratives"]["N167_sulalah"]["ayahs"] == ["23:12", "24:63", "32:8"]


def test_the_rejections_are_real_other_roots_not_padding():
    r = _r()
    assert "W3_THE_REJECTIONS_ARE_REAL_OTHER_ROOTS" not in r["gates_not_met"]
    adj = r["narratives"]["IQRA_quran"]["adjudication"]
    assert adj["اقرب"].startswith("REJECTED") and "q-r-b" in adj["اقرب"]
    assert "f-q-r" in adj["الفقراء"]
    bk = r["narratives"]["N157_barakah"]["adjudication"]
    assert "b-r-'" in bk["باريكم"], "بارئكم is your Maker, hamza not kaf"


def test_iqra_distribution_is_reported_whichever_way_it_cuts():
    d = _r()["narratives"]["IQRA_quran"]["distribution"]
    assert d["nominal_ayah_count"] > d["verbal_ayah_count"]
    assert "قروء" in d["nominal_forms"]
    assert "one ayah is ONE_WING under the Janah rule and settles nothing" in d["note"]


def test_the_she_camel_etymology_is_not_tested_and_gets_no_support():
    c = _r()["corrections"]["iqra_from_a_pregnant_she_camel"]
    assert "not tested here" in c and "no support" in c
    assert "only a plausible opinion" in c


def test_the_claims_put_to_me_are_corrected_in_the_record():
    c = _r()["corrections"]
    assert "There is no such ratio" in c["the_268_to_1_ratio"]
    assert "It was never MUTABLE" in c["islam_collapsed_from_MUTABLE"]
    assert "Layer 3 naming, not a result" in \
        c["the_screen_is_the_first_implementation_of_Al_Mizan"]


def test_licensing_does_not_make_a_reading_correct():
    assert _gate("W8_does_a_LICENSED_root_make_the_reading_correct")["weight"] \
        == "excluded"
    g = _gate("W9_does_this_run_support_the_quantitative_models")
    assert g["weight"] == "excluded"
    assert "not measured here or anywhere in this repository" in g["detail"]


def test_score_is_six_of_seven_and_nothing_simulated():
    r = _r()
    assert r["score"] == "6/7"
    assert r["gates_not_met"] == ["W2_EVERY_CANDIDATE_IS_ADJUDICATED_AND_PRINTED"]
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
