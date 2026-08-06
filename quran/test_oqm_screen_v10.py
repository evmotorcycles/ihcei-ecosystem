"""
test_oqm_screen_v10.py -- the Iqra run, and a homograph that reverses my own count: 6/6.

THE HOMOGRAPH. After normalisation قري is AMBIGUOUS between two roots: قُرِئَ 'it was
recited' (q-r-', 7:204 and 84:21) and قُرًى 'towns' (q-r-y, 34:18 and 59:14). Both
reduce to the same token, so a form list containing قري silently absorbs two ayahs
about fortified villages into a study of recitation. The disambiguator is the hamza
carrier in the RAW token — the signal is in the source text, like the waṣla rule in v3.

WHAT THAT DOES TO MY OWN RECORD.
  v4 published 79 and is CORRECT — but by ACCIDENT. Its candidate generator happened
     to require a hamza carrier, so it excluded 34:18 and 59:14 without ever knowing
     why. Its published accepted_forms list still contains the ambiguous form.
  v7 reused that list WITHOUT the filter and published 81. THAT IS THE ERROR, and it
     is corrected here to 79.

A count that is right for the wrong reason is not safe. The moment the accidental
filter was dropped the error surfaced — and it surfaced only because two of my own
runs disagreed and the disagreement was chased rather than averaged away. H6 verifies
v7 still hashes to its locked value and still reads 81, so the wrong number stays on
the record with a correction attached rather than being edited out.

THE INDEPENDENCE RULE BITES HARDEST ON THE LARGEST ROOT. 79 attestations are only 66
independent contexts. Sūrah 54's refrain وَلَقَدْ يَسَّرْنَا ٱلْقُرْءَانَ لِلذِّكْرِ appears at
54:17, 54:22, 54:32 and 54:40 at Jaccard 1.0 — IDENTICAL. Four attestations, ONE wing.
A raw count would have called that four witnesses, which is the whole reason the rule
exists.

THE BAYT MEASURE RECOVERS REAL MOTIFS FROM SHARED VOCABULARY ALONE.
  qur'ānan ʿarabiyyan   12:2 · 20:113 · 39:28 · 41:3 · 41:44 · 42:7 · 43:3
  the oath + epithet    15:87 · 36:2 · 38:1 · 50:1
  reading one's record  17:71 · 69:19
The oath group is the risky half of H4: four different sūrahs sharing only the oath
frame, found with no structural hint.

DISTRIBUTION. 16 verbal against 63 nominal. 2:228 قُرُوٓءٍ is present — same root, no
reciting sense — and is ONE_WING on its own, settling nothing.

EXCLUDED. H7: none of this says what iqraʾ MEANS; wings, zones and distributions count
contexts and shared words, and the she-camel etymology remains untested lexicography.
H8: seven YouTube links have now been supplied, including YT169 with the Ṭayran
Abābīl correction and the quotation about backing up and reassessing. I cannot watch
video and no transcripts were given, so that account is the user's testimony and is
not verified here.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "b150226a276694b9f44191556ae147add2631a9d3195a44fafcd7609cd3c8fee"
V9 = "7931ac7c939a5eb2488727cad6650640f0c26f0785d156a44f508d55aeeef341"
V7 = "8fb9f1169dbb32f82a195b15f1f1fd3076722a7facbe51207353b955dae39599"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v10.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v10.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v9():
    s = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v10_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V9


def test_PRIMARY_the_homograph_partitions_on_the_hamza_carrier():
    r = _r()
    assert "H1_THE_HOMOGRAPH_IS_DEMONSTRATED" not in r["gates_not_met"]
    h = r["homograph"]
    assert len(h) == 4
    assert {v["normalised"] for v in h.values()} == {"قري"}, "one token, two roots"
    assert h["7:204"]["root"] == "q-r-'" and h["84:21"]["root"] == "q-r-'"
    assert h["34:18"]["root"] == "q-r-y" and h["59:14"]["root"] == "q-r-y"
    assert h["34:18"]["has_hamza"] is False


def test_PRIMARY_my_own_v7_count_of_81_is_wrong_and_79_is_right():
    r = _r()
    assert "H2_MY_OWN_V7_COUNT_IS_CORRECTED" not in r["gates_not_met"]
    assert r["qr_ayahs"] == 79 and r["qr_surahs"] == 42
    d = _gate("H2_MY_OWN_V7_COUNT_IS_CORRECTED")["detail"]
    assert "v7 published 81" in d
    assert "ACCIDENTALLY so" in d
    assert "right for the wrong reason is not safe" in d


def test_v7_is_superseded_not_rewritten_and_still_reads_81():
    r = _r()
    assert "H6_V7_IS_SUPERSEDED_NOT_REWRITTEN" not in r["gates_not_met"]
    v7 = json.load(open(os.path.join(HERE, "results_oqm_screen_v7.json"),
                        encoding="utf-8"))
    assert v7["score"] == "8/8" and v7["spec_sha256"] == V7
    assert "stays visible with a correction attached" in \
        _gate("H6_V7_IS_SUPERSEDED_NOT_REWRITTEN")["detail"]


def test_79_attestations_are_only_66_independent_wings():
    r = _r()
    assert "H3_THE_INDEPENDENCE_RULE_BITES_HARDEST_ON_THE_LARGEST_ROOT" \
        not in r["gates_not_met"]
    assert r["independent_wings"] == 66
    s54 = [m for m in r["merges"]
           if m["a"].startswith("54:") and m["b"].startswith("54:")]
    assert len(s54) == 3
    assert all(m["jaccard"] == 1.0 for m in s54), "the refrain is identical"
    assert all(m["reason"] == "J1_formulaic" for m in s54)


def test_RISKY_the_oath_group_is_found_across_four_surahs_from_words_alone():
    r = _r()
    assert "H4_THE_BAYT_MEASURE_FINDS_RECOGNISABLE_MOTIFS" not in r["gates_not_met"]
    z = r["buyut"]
    assert ["15:87", "36:2", "38:1", "50:1"] in z, "oath with an epithet"
    assert ["12:2", "20:113", "39:28", "41:3", "41:44", "42:7", "43:3"] in z
    assert ["17:71", "69:19"] in z, "reading one's own record"


def test_the_distribution_and_the_outlier():
    r = _r()
    assert r["verbal_ayahs"] == 16 and r["nominal_ayahs"] == 63
    assert "ONE_WING on its own, settling nothing" in \
        _gate("H5_THE_DISTRIBUTION_IS_REPORTED")["detail"]


def test_none_of_it_says_what_iqra_means():
    g = _gate("H7_does_any_of_this_say_what_IQRA_MEANS")
    assert g["weight"] == "excluded"
    assert "she-camel etymology remains untested lexicography" in g["detail"]


def test_the_lectures_including_YT169_remain_unviewed():
    g = _gate("H8_the_lectures_remain_unviewed")
    assert g["weight"] == "excluded"
    assert "YT169" in g["detail"]
    assert "user's testimony and is not verified here" in g["detail"]


def test_score_is_six_of_six_and_nothing_simulated():
    r = _r()
    assert r["score"] == "6/6" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
