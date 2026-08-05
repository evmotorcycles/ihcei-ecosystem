"""
test_oqm_screen_v6.py -- Bayt, Tafseel and Nested Interpretation as measurements: 8/8.

THREE OPERATIONS MADE MECHANICAL.
  BAYT     cluster a root's ayahs by shared CONTENT vocabulary (Jaccard >= 0.10,
           single-link). A multi-member cluster is a motif the text repeats.
  TAFSEEL  the number of distinct Buyut a root falls into. One zone = one setting;
           more than one = the root divaricates and a reading built on one branch
           has not accounted for the others.
  NESTED   the loop runs only if the root is attested INSIDE a narrative anchor and
           OUTSIDE it -- something to extract from, somewhere to nest into.

THE RISKY PREDICTION HELD. U4 required the vocabulary measure to join 27:8 with
28:30 -- the two Musa-at-the-fire passages -- from word overlap alone, with no
knowledge of what either says. It did. Other zones it found: {6:92, 6:155, 21:50,
38:29, 44:3} all kitab mubarak, and {17:1, 21:71, 21:81} all 'the land we blessed'.

TAFSEEL DISTINGUISHES ROOTS, WHICH IS THE ONLY THING THAT MAKES IT A MEASURE. s-l-l
splits into exactly 2 zones -- the creation-account sulalah {23:12, 32:8} against the
withdrawal verb {24:63} -- while b-r-k's largest single zone holds 5.

AL-ƐASR IS THE CLEANEST NESTED DEMONSTRATION. 3-s-r is attested inside the Yussuf
narrative at 12:36 and 12:49, where the sense is physically pressing, and at 103:1
outside any narrative. A definition can therefore be extracted from a story and
nested into 103:1 WITHOUT a dictionary -- precisely the operation N159 says is the
only legitimate one.

THE BAYT MEASURE DECLARES ITS OWN 58:11. Ayahs under 4 content words cannot cluster
on vocabulary. 103:1 وَٱلْعَصْرِ is two words, so its singleton status is MECHANICAL and
is not a finding about motifs. U8 flags it rather than reporting five ʿ-ṣ-r "motifs".

THREE CLAIMS PUT TO ME THAT DO NOT SURVIVE.

  1. نَاقَة is NOT root ن-ق-ي. Its skeleton is ن-ا-ق-ة; the alif is a long vowel, not
     a radical yaa, and the root is ن-و-ق (hollow). ن-ق-ي would give نَقِيَّة, a
     different word on a different template. And root ن-ق-ي is attested ZERO times --
     below even 58:11, which had one. This refutes the stated DERIVATION, which is a
     Layer 1 claim and is false. It does NOT refute the reading, which would simply
     need some other warrant.

  2. The screen did NOT prove the purifier reading. v5's negative control established
     exactly one thing: أعناقهم (root ع-ن-ق) is not نَاقَة -- a statement about two
     letter-strings. It evaluated no root ن-ق-ي and no semantic reading. Recorded
     because accepting credit for a measurement I did not make would corrupt the
     record more than any single wrong number.

  3. Root ع-ب-س occurs THREE times, not two: 74:22, 76:10, 80:1. The stated set
     missed 76:10 عَبُوسًا. This helps rather than hurts the inquiry -- three witnesses
     across three surahs clear both rules more comfortably -- but a nested
     interpretation built on two of three attestations left a third of its own
     evidence unexamined.

AND ONE ERROR OF MY OWN, IN THE PRE-REGISTRATION ITSELF. The locked spec's U5 CLAIM
text says b-r-k's largest zone holds 4 ayahs. It holds 5. The claim was written from
a probe run with a shorter stop-word list than the runner uses. The spec's stated
passes_if concerns s-l-l only and is met, so the gate passes honestly -- but the
claim text and the run disagree, and the runner says so in its own output rather
than quietly reconciling them.

WHAT IS EXCLUDED. U9: clustering establishes no MEANING -- that two ayahs share words
is a fact, that they share a metaphor is a reading. U10: the document grounds
cross-surah links in Bell-inequality violation and quantum entanglement. No physics
is measured here; shared vocabulary is ordinary co-occurrence requiring no
non-locality, and borrowing a physics result's authority for a text statistic is the
layer breach this repository exists to prevent.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "faa2f56ee9b346908070af055bdda0e084339f9cb0c264870a968c797d4ab4fc"
V5 = "5f43d480f2af1616f365b925a2ea887936cbffdccf337efd2d8452fec229719d"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v6.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v6.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v5():
    s = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v6_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V5


def test_PRIMARY_naqah_is_root_N_W_Q_and_N_Q_Y_is_absent_entirely():
    r = _r()
    assert "U1_ROOT_N_Q_Y_IS_ABSENT_FROM_THE_TEXT" not in r["gates_not_met"]
    d = _gate("U1_ROOT_N_Q_Y_IS_ABSENT_FROM_THE_TEXT")["detail"]
    assert "attestations: 0" in d
    assert "LONG VOWEL, not a radical" in d
    assert "below even 58:11" in d
    # the rejections are listed so a reader can check them
    for near in ("نقيبا", "نقيرا", "نقيض", "نقيم"):
        assert near in d


def test_refuting_the_derivation_is_not_refuting_the_reading():
    c = _r()["corrections"]["claim_1_naqah_is_root_N_Q_Y"]
    assert "It does not refute the READING" in c["what_this_does_and_does_not_settle"]
    assert "Layer 1 morphological claim and is false" in \
        c["what_this_does_and_does_not_settle"]


def test_the_screen_is_not_credited_with_a_result_it_did_not_produce():
    d = _gate("U2_THE_SCREEN_IS_NOT_CREDITED_WITH_A_RESULT_IT_DID_NOT_PRODUCE")["detail"]
    assert "a statement about two letter-strings" in d
    assert "evaluated no root" in d
    assert "corrupt the record" in d


def test_abas_has_three_attestations_not_two():
    r = _r()
    assert "U3_ABAS_HAS_THREE_ATTESTATIONS_NOT_TWO" not in r["gates_not_met"]
    assert r["abas_attestations"] == ["74:22", "76:10", "80:1"]
    assert "left a third of its own evidence unexamined" in \
        _gate("U3_ABAS_HAS_THREE_ATTESTATIONS_NOT_TWO")["detail"]


def test_RISKY_the_bayt_measure_joins_the_two_musa_at_the_fire_passages():
    """Predicted before running: 27:8 and 28:30 land in one zone, from words alone."""
    r = _r()
    assert "U4_BAYT_CLUSTERING_PRODUCES_REAL_MOTIFS" not in r["gates_not_met"]
    zones = r["narratives"]["N157_barakah"]["buyut"]
    musa = [g for g in zones if "27:8" in g]
    assert musa and "28:30" in musa[0]
    assert ["6:92", "6:155", "21:50", "38:29", "44:3"] in zones, "kitab mubarak"
    assert ["17:1", "21:71", "21:81"] in zones, "the land we blessed"


def test_tafseel_distinguishes_roots_or_it_is_vacuous():
    r = _r()
    assert "U5_TAFSEEL_DISTINGUISHES_ROOTS" not in r["gates_not_met"]
    sll = r["narratives"]["N167_sulalah"]
    assert sll["n_buyut"] == 2
    assert sll["buyut"] == [["23:12", "32:8"], ["24:63"]]
    brk = r["narratives"]["N157_barakah"]
    assert max(len(g) for g in brk["buyut"]) == 5


def test_MY_OWN_PREREGISTRATION_ERROR_IS_DISCLOSED_NOT_RECONCILED():
    """The spec's claim text says 4; the run gives 5. Recorded, not smoothed over."""
    d = _gate("U5_TAFSEEL_DISTINGUISHES_ROOTS")["detail"]
    assert "DISCLOSED" in d
    assert "the real figure is 5" in d
    assert "my pre-registration error" in d
    assert "quietly reconciled" in d


def test_nested_interpretation_is_runnable_for_all_three_narratives():
    r = _r()
    assert "U6_NESTED_INTERPRETATION_IS_RUNNABLE_FOR_ALL_THREE" not in r["gates_not_met"]
    for k in ("N157_barakah", "N182_al_asr", "N167_sulalah"):
        n = r["narratives"][k]
        assert n["nested_interpretation"] == "RUNNABLE"
        assert n["anchor_present"] and n["attested_outside_anchor"]
    assert "licenses the LOOP" in \
        _gate("U6_NESTED_INTERPRETATION_IS_RUNNABLE_FOR_ALL_THREE")["detail"]


def test_al_asr_is_the_cleanest_demonstration():
    r = _r()
    assert "U7_THE_CLEANEST_DEMONSTRATION_IS_AL_ASR" not in r["gates_not_met"]
    a = r["narratives"]["N182_al_asr"]["ayahs"]
    for ref in ("12:36", "12:49", "103:1"):
        assert ref in a
    assert "WITHOUT a dictionary" in \
        _gate("U7_THE_CLEANEST_DEMONSTRATION_IS_AL_ASR")["detail"]


def test_the_bayt_measure_declares_its_own_coverage_limit():
    r = _r()
    assert "U8_THE_BAYT_MEASURE_DECLARES_ITS_OWN_COVERAGE_LIMIT" not in r["gates_not_met"]
    assert "103:1" in r["narratives"]["N182_al_asr"]["short_ayah_singletons"]
    d = _gate("U8_THE_BAYT_MEASURE_DECLARES_ITS_OWN_COVERAGE_LIMIT")["detail"]
    assert "MECHANICAL" in d and "not a finding about motifs" in d
    assert "the Bayt measure's own 58:11" in d


def test_clustering_and_the_physics_framing_are_both_excluded():
    g9 = _gate("U9_does_clustering_establish_MEANING")
    assert g9["weight"] == "excluded"
    assert "that they share a metaphor" in g9["detail"]
    g10 = _gate("U10_the_entanglement_framing_is_not_evaluated")
    assert g10["weight"] == "excluded"
    assert "No physics is measured here" in g10["detail"]
    assert "layer breach" in g10["detail"]


def test_score_is_eight_of_eight_and_nothing_simulated():
    r = _r()
    assert r["score"] == "8/8" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
