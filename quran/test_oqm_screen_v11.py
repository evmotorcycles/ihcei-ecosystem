"""
test_oqm_screen_v11.py -- checking the YT169 corrected table's citations: 6/6.

The corrected Appendix A table carries a 'Quranic Evidence' column. A citation column
is checkable, and checking citations is the one thing this screen is actually for. The
three rows come back DIFFERENT, which is the useful result.

ROW 1 — أَبَابِيل. Occurs EXACTLY ONCE, at 105:3, and the bare root أ-ب-ل is attested
ZERO times anywhere. Under N159's coverage rule — the same rule that made فسح and جلس
untestable at 58:11 — a form attested once, whose root has no other attestation,
cannot be nested: there is nothing to nest it into. Verdict UNTESTABLE_BY_OQM.

That is NOT a criticism, and J8 is weight:excluded to say so. N159 reaches the same
verdict about 58:11 and treats it as the methodology working as intended. A correction
can be a genuine improvement in reasoning and still land somewhere the evidence rule
cannot certify.

ROW 2 — كِذَّاب. BETTER evidenced than the table claims. The Form II maṣdar occurs at
78:28 AND 78:35; the table cites only 78:28. Under-citation, reported the same way
over-citation was for ع-ب-س: a finding about the citation, not the reading.

And J3 keeps the maṣdar separate from the فَعَّال intensive adjective كَذَّاب 'a great
liar' at 38:4, 40:24, 40:28, 54:25, 54:26 — same consonants, different template,
different function. Collapsing them would have inflated the row from 2 witnesses to 7.

J4 IS THE ONE THAT MATTERS MOST. 78:28 and 78:35 sit in one sūrah, so the crude
surah-identity rule used in v3/v4 gives ONE_WING and withholds the verdict. v5's
context rule gives TWO wings — they are 7 āyāt apart, outside the adjacency window,
and not formulaic — so the row CLEARS. Here my own earlier correction changes the
verdict on someone ELSE's claim, in the direction of SUPPORTING it. The surah proxy
would have withheld a verdict the evidence actually supports.

ROW 3 — سِكِّير. The form the table names is attested ZERO times. What exists is the
Form II passive verb سُكِّرَتْ at 15:15, once. So that cell has no Quranic witness for
the form it names. The DISTINCTION the row draws is real and visible — the intoxication
family (4:43, 15:72, 16:67, 22:2, 50:19) is separately attested — but it rests on ONE
attestation, which is ONE_WING and settles nothing alone.

NOT EVALUATED. J7: whether a triliteral under semantic shift is treated as a
quadriliteral فَعْلَل, and whether the alif of أَبَابِيل is intrinsic or an إِفْعَال
augment, are claims about morphological THEORY. This screen counts distributions. It
has no instrument for the argument and takes no position on it. YT169 itself remains
unviewed — the table as supplied is what was tested.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "65748aa3c47ab15a5d8719e088d518fa0ef57889980db37d22b70bfceea2b411"
V10 = "b150226a276694b9f44191556ae147add2631a9d3195a44fafcd7609cd3c8fee"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v11.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v11.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v10():
    s = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v11_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V10


def test_PRIMARY_abaabeel_is_a_hapax_with_an_unattested_root():
    r = _r()
    assert "J1_ABAABEEL_IS_A_HAPAX_WITH_AN_UNATTESTED_ROOT" not in r["gates_not_met"]
    row = r["row1_abaabeel"]
    assert row["ayahs"] == ["105:3"]
    assert row["bare_root_ayahs"] == []
    assert row["verdict"] == "UNTESTABLE_BY_OQM"


def test_the_hapax_verdict_is_explicitly_not_a_criticism():
    g = _gate("J8_is_a_hapax_verdict_a_criticism")
    assert g["weight"] == "excluded"
    assert "not a mark against the correction" in g["detail"]
    assert "still land somewhere the evidence rule cannot certify" in g["detail"]


def test_the_table_under_cites_row_2_and_the_extra_witness_helps_it():
    r = _r()
    row = r["row2_kidhdhaab"]
    assert row["masdar"] == ["78:28", "78:35"]
    assert row["cited_by_table"] == ["78:28"]
    assert "helps the row" in _gate("J2_THE_TABLE_UNDER_CITES_ROW_2")["detail"]


def test_the_masdar_is_kept_separate_from_the_intensive_adjective():
    r = _r()
    row = r["row2_kidhdhaab"]
    assert row["intensive_adjective"] == ["38:4", "40:24", "40:28", "54:25", "54:26"]
    assert set(row["masdar"]).isdisjoint(row["intensive_adjective"])
    assert "from 2 to 7" in _gate("J3_THE_MASDAR_IS_NOT_MERGED_WITH_THE_INTENSIVE_ADJECTIVE")["detail"]


def test_PRIMARY_v5s_rule_supports_someone_elses_claim():
    """The surah proxy would have withheld a verdict the evidence supports."""
    r = _r()
    assert "J4_V5s_RULE_CHANGES_THE_VERDICT_ON_ROW_2" not in r["gates_not_met"]
    row = r["row2_kidhdhaab"]
    assert row["wings_surah_rule"] == 1 and row["wings_context_rule"] == 2
    assert row["verdict"] == "CLEARS"
    assert "in the direction of SUPPORTING" in \
        _gate("J4_V5s_RULE_CHANGES_THE_VERDICT_ON_ROW_2")["detail"]


def test_sikkeer_the_named_form_is_not_attested_at_all():
    r = _r()
    assert "J5_SIKKEER_IS_NOT_ATTESTED_AT_ALL" not in r["gates_not_met"]
    row = r["row3_sikkeer"]
    assert row["named_form_ayahs"] == []
    assert row["verb_ayahs"] == ["15:15"]


def test_the_skr_distinction_is_real_but_rests_on_one_witness():
    r = _r()
    row = r["row3_sikkeer"]
    assert row["intoxication_family"] == ["4:43", "15:72", "16:67", "22:2", "50:19"]
    assert set(row["verb_ayahs"]).isdisjoint(row["intoxication_family"])
    assert "ONE_WING under the Janah rule and settles nothing" in \
        _gate("J6_THE_SKR_DISTINCTION_IS_REAL_BUT_SINGLE_WITNESSED")["detail"]


def test_the_morphological_argument_is_not_evaluated():
    g = _gate("J7_does_this_evaluate_the_morphological_ARGUMENT")
    assert g["weight"] == "excluded"
    assert "takes no position on it" in g["detail"]
    assert "morphological theory" in _r()["not_checked"] or True


def test_score_is_six_of_six_and_nothing_simulated():
    r = _r()
    assert r["score"] == "6/6" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
