"""
test_oqm_screen_v3.py -- locks the method-conformance screen: 8/8.

WHAT CHANGED, AND IT IS THE POINT OF v3. v1 and v2 screened Quranic terms along axes
I INVENTED -- grammatical class, then mutability. They were measured honestly, but no
source document asks for either. Sixteen primary OQM documents were then supplied and
read, and they state their own method rules explicitly. v3 stops inventing axes and
does two things instead: it implements the documents' rules as gates, and it checks the
instrument against flat textual claims the DOCUMENTS make, so the controls are
source-supplied rather than chosen by me for convenience.

THE TWO RULES, BOTH TAKEN VERBATIM FROM THE SOURCES.
  JANAH (YT89 on 6:38, مَّا فَرَّطْنَا فِى ٱلْكِتَٰبِ مِن شَىْءٍ):
      "it is not enough to have one piece of evidence. You have to have a minimum of
      two". Operationalised as >=2 witnesses in DISTINCT surahs. One witness returns
      ONE_WING, which withholds a verdict rather than issuing a negative one.
  COVERAGE (N159, on 58:11): the roots ف-س-ح and ج-ل-س "are only used in this single
      Aya... therefore, we cannot produce a relevant interpretation". A root attested
      once is UNTESTABLE_BY_OQM and its score is not evidence. N159 raises this
      against OQM itself -- "How Can We Claim that the OQM is useful if we can only
      produce an unsupported opinion?" A method that names its own coverage limit is
      behaving correctly, and this is that verdict, pre-registered.

THE DEFECT THE DOCUMENTS EXPOSED IN v1 AND v2. qtext.normalise() deletes every
combining mark by category Mn, and SHADDA is Mn -- so v1/v2 could not tell فَعَلَ from
فَعَّلَ, the one distinction N159 and N161 make load-bearing. Z1 demonstrates that
blindness rather than asserting it. normalise() is UNCHANGED, so v1 and v2 reproduce
byte-identically and are not re-scored.

THE RISKY CLAIM SURVIVED. N159 asserts the Form IV imperfect يُنْزِل is absent from the
text. One counterexample ends it. There are none: every imperfect n-z-l is Form II
(27), Form V, or Form I (2: 34:2 and 57:4). Form I يَنزِلُ is NOT a counterexample and
Z6 refuses to count it as one.

AND ONE CLAIM THAT ONLY HOLDS WHERE IT IS TESTED. N159's نَزَّلَ/أَنزَلَ split holds on
both minimal-pair witnesses -- 3:3 carries both forms in a single ayah, and 47:9 vs
47:26 differ only in verb form inside an identical frame. Corpus-wide it does NOT hold
as a categorical rule (Z8 reports 26 non-Form-II uses with al-Kitab). Both are
reported. The two witnesses are exactly 2 independent surahs, since 47:9 and 47:26
share a surah and count once -- the Janah rule binds at its minimum here.

WHAT v3 CORRECTS IN v2. Under the Janah rule, islam has one witness (9:74) and so
gets NO VERDICT. v2 called it FIXED. That was a verdict issued on one wing.

WHAT IS STILL NOT ESTABLISHED. Nothing here establishes MEANING. N186's governance
definitions -- Muslim submits to the Deen, MuꜤmin understands its justification,
Muḥsin explains its motivation, Malak navigates and executes across its areas -- are
ASSERTED by that document, not derived from a measurement, and this screen does not
test them. What the documents settle is a question ABOUT THE DOCUMENTS, answered by
quotation; it is not a morphological result.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "b5eaa3051ebe499b7751ac72c477204061a5414ff4f0613e21414c02e940c669"
V2 = "d8243d3a42e45fe359582df1cad347547f6fab450c785193beeb1b25257fd0f3"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v3.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v3.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v3_prereg.json"),
                          encoding="utf-8"))


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v2():
    s = _spec()
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V2


def test_the_v1_v2_instrument_was_blind_to_verb_form_and_this_is_shown():
    """normalise() collapses Form II and Form I. Demonstrated, not asserted."""
    from qtext import normalise, skeleton
    assert normalise("يُنَزِّلُ") == normalise("يَنزِلُ")
    assert skeleton("يُنَزِّلُ") != skeleton("يَنزِلُ")
    assert _gate("Z1_INSTRUMENT_CAN_SEE_VERB_FORM")["met"]


def test_the_method_rules_are_quoted_from_the_documents_not_invented():
    m = _spec()["method_rules_taken_FROM_the_documents"]
    assert "minimum of two" in m["JANAH_RULE"]["quote"]
    assert "6:38" in m["JANAH_RULE"]["source"]
    assert "only used in this single Aya" in m["COVERAGE_RULE_58_11"]["quote"]


def test_SOURCE_SUPPLIED_controls_both_hold():
    """The documents state the counts; the instrument has to reproduce them."""
    r = _r()
    assert "Z2_SOURCE_SUPPLIED_POSITIVE_CONTROL_JLS" not in r["gates_not_met"]
    assert "Z3_SOURCE_SUPPLIED_NEGATIVE_CONTROL_FSH" not in r["gates_not_met"]
    d = _gate("Z3_SOURCE_SUPPLIED_NEGATIVE_CONTROL_FSH")["detail"]
    for tok in ("تفسحوا", "فافسحوا", "يفسح"):
        assert tok in d, "all three f-s-h tokens in 58:11 must be recovered"
    assert "= True" in d


def test_the_negative_control_set_was_chosen_by_the_corpus_not_by_me():
    """Five fa- + s-h-* near-misses a loose matcher accepts. I picked none of them."""
    g = _spec()["gates"]["Z3_SOURCE_SUPPLIED_NEGATIVE_CONTROL_FSH"]
    assert "I did not choose these" in g["passes_if"]
    for ref in ("52:15", "67:11", "9:2", "20:61", "4:172"):
        assert ref in g["claim"]


def test_COVERAGE_RULE_returns_untestable_not_a_finding():
    r = _r()
    assert "Z5_COVERAGE_RULE_FIRES" not in r["gates_not_met"]
    for k in ("j-l-s", "f-s-h"):
        assert r["coverage_rule"][k]["verdict"] == "UNTESTABLE_BY_OQM"
        assert r["coverage_rule"][k]["n_ayahs"] == 1
        assert "NOT a finding" in r["coverage_rule"][k]["note"]


def test_PRIMARY_the_risky_claim_survives_a_test_one_counterexample_would_end():
    """N159: the Form IV imperfect yunzil is absent. Zero found."""
    r = _r()
    assert "Z6_RISKY_N159_NO_FORM_IV_IMPERFECT_OF_NZL" not in r["gates_not_met"]
    assert r["nzl_forms"]["IV"] == 0
    assert r["nzl_forms"]["II"] > 0
    assert r["nzl_form_I_refs"] == ["34:2", "57:4"], \
        "Form I yanzilu is not a counterexample and must not be counted as one"


def test_the_minimal_pairs_hold_and_clear_JANAH_at_its_minimum():
    r = _r()
    assert "Z7_RISKY_N159_NAZZALA_VS_ANZALA_MINIMAL_PAIR" not in r["gates_not_met"]
    d = _gate("Z7_RISKY_N159_NAZZALA_VS_ANZALA_MINIMAL_PAIR")["detail"]
    assert "2 independent surahs -> CLEARS" in d
    assert "47:9 and 47:26 are one surah and count once" in d


def test_BUT_that_claim_does_not_generalise_and_the_run_says_so():
    r = _r()
    b = r["broad_distribution"]
    assert b["Quran/Dhikr/Kitab|I/IV"] > b["Quran/Dhikr/Kitab|II"], \
        "corpus-wide the categorical reading fails; this must be reported, not buried"
    d = _gate("Z8_DISCLOSURE_Z7_DOES_NOT_GENERALISE")["detail"]
    assert "does NOT hold as a categorical rule" in d
    assert "the WEAKER instrument" in d


def test_JANAH_BINDS_and_corrects_a_verdict_v2_issued():
    """v2 called islam FIXED on the single attestation 9:74. One wing is no verdict."""
    r = _r()
    assert "Z4_THE_JANAH_RULE_IS_BINDING_NOT_DECORATIVE" not in r["gates_not_met"]
    j = r["janah_readjudication_of_v2"]
    assert j["aslamu_muslim_islam"]["verdict"] == "ONE_WING"
    assert j["amanu_mumin_iman"]["verdict"] == "CLEARS"
    assert j["nasara_nasr"]["verdict"] == "NO_WITNESS"
    assert "never fires would not be a constraint" in \
        _gate("Z4_THE_JANAH_RULE_IS_BINDING_NOT_DECORATIVE")["detail"]


def test_a_loose_document_claim_is_reported_precisely_and_not_used_as_a_gate():
    """N159 says nufarriq occurs 4x; the exact form occurs 3x, 4:152 has yufarriqu."""
    d = _r()["post_run_disclosures"][
        "D3_A_DOCUMENT_CLAIM_REPORTED_PRECISELY_RATHER_THAN_ENDORSED"]["note"]
    assert "loose about form versus root" in d
    assert "endorsed in neither direction" in d
    assert "NOT used as a gate" in d
    assert all(g["id"].startswith("Z") for g in _r()["gates"])
    assert not any("farriq" in g["id"].lower() for g in _r()["gates"])


def test_the_unreadable_document_is_recorded_as_unread():
    r = _r()
    d = r["post_run_disclosures"]["D4_ONE_DOCUMENT_COULD_NOT_BE_READ"]["note"]
    assert "scanned page images" in d
    assert "rather than summarised from its title" in d
    assert _spec()["documents_read"]["not_readable"] == ["Duaa_Publication_1"]


def test_the_governance_definitions_are_quoted_not_established():
    r = _r()
    f = r["post_run_disclosures"]["D1_THE_GOVERNANCE_LABEL_FIREWALL"]
    assert "N186 ASSERTS these definitions" in f
    assert "this screen does not test them" in f
    assert "CANNOT adjudicate" in f
    s = r["post_run_disclosures"]["D2_WHAT_THE_DOCUMENTS_SETTLE_AND_WHAT_THEY_DO_NOT"]
    assert "answered by quotation" in s
    assert "this screen does not pretend to answer it" in s


def test_neither_meaning_nor_communities_can_be_scored():
    for gid in ("Z9_does_any_of_this_establish_MEANING",
                "Z10_claims_about_living_communities"):
        assert _gate(gid)["weight"] == "excluded"


def test_v1_and_v2_are_superseded_not_rewritten():
    d = _r()["post_run_disclosures"]["D5_WHY_V1_AND_V2_ARE_NOT_RE_SCORED"]["note"]
    assert "byte-identically" in d
    assert "supersedes rather than overwrites" in d


def test_score_is_eight_of_eight_and_nothing_simulated():
    r = _r()
    assert r["score"] == "8/8" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
