"""
test_qvif.py -- locks the VIF run: 1/3, and the primary failed on purpose-built evidence.

THE CLAIM UNDER TEST. A VIF of 1.000073 between a Salat track and a Zakat track has been
quoted as showing the text handles 'seeking' and 'sharing' as independent channel legs --
the same orthogonality gate that returned 1.0026 on yeast and 1.0203 on GitHub.

THE PRIOR QUESTION THIS RUN ASKS. On this substrate, does a near-1.0 VIF distinguish
anything at all? VIF = 1/(1-r^2), and across 6,236 ayahs almost every word is absent from
almost every ayah, so two rare tracks are both nearly all zeros and r is near 0 whatever the
words mean.

THE ANSWER, AND IT IS NOT CLOSE.

    99.8% of 1,200 frequency-matched RANDOM unrelated word pairs clear VIF < 1.05
    null median VIF                                                  1.000032
    measured VIF(SALAT, ZAKAT)                                       1.000028
    ... which sits at the 46th percentile of that null

So 54% of arbitrary unrelated word pairs are MORE 'orthogonal' than Salat and Zakat. The
quoted figure is what sparse count data produces for any two rare words. It supports no
claim about how the text handles anything.

AND THE FULL MATRIX MAKES IT VISUAL: 28 of 28 pairs among the eight declared tracks clear
the bar -- INCLUDING IMAN and MUMIN, which share a root, and MILLAH and NASARA, which
co-occur in the very ayah the framework builds on. A metric that calls same-root words
orthogonal is not measuring independence here.

THE CATEGORY DIFFERENCE THAT MATTERS (W6). Yeast 1.0026 and GitHub 1.0203 were computed on
CONTINUOUS PER-NODE FEATURES, where every unit has a real value on both axes and
collinearity is a live possibility. Per-ayah word counts are overwhelmingly zero. Quoting a
word-count VIF beside them implies a comparability that does not exist.

W5 ALSO FAILED, AND ITS FAILURE IS A REAL DISTRIBUTIONAL FINDING. Using the SAME designation
matcher that scored 7 of 7 control proper nouns at zero in spec 708ac80e:

    "those who believed"  (alladhina amanu, root A-M-N)      268 times
    "those who submitted" (alladhina aslamu, root S-L-M)       1 time   (5:44)

The verb aslama exists and is used, but this text designates a GROUP by that act exactly
once. The group-by-action designation attaches overwhelmingly to iman, not to islam. The
gate required >= 5 for each root and is reported FAILED.

W1 CAUGHT A REAL BUG ON THE FIRST RUN. Three track regexes did not match the dataset's
orthography: hamza-on-waw (U+0624) decomposes under NFD to waw plus a combining mark, so
'mumin' is مومن and not مءمن, and zakat is written with a waw. The integrity gate failed,
the regexes were corrected, and the run was repeated. W2's result is unchanged by that fix
because the null never depended on the track definitions.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "af27d2c9c9398ca4f99a4772e6769a23cf4ab8198542067f453971c83e6c09b3"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "qvif.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_qvif.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _spec():
    return json.load(open(os.path.join(HERE, "prereg", "quran_vif_prereg.json"),
                          encoding="utf-8"))


def test_spec_locked():
    got = hashlib.sha256(json.dumps(_spec(), sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED


def test_the_probe_measured_the_null_only_and_says_so():
    p = _spec()["PRE_FLIGHT_PROBE_RECORDED_BEFORE_THIS_LOCK"]
    assert "The NULL ONLY" in p["what_was_probed"]
    assert "were NOT touched" in p["what_was_probed"]
    assert "does NOT contain the primary quantity" in p["what_it_establishes"]


def test_THE_VIF_GATE_DOES_NOT_DISCRIMINATE_HERE():
    r = _r()
    assert "W2_PRIMARY_DOES_THE_VIF_GATE_DISCRIMINATE_ON_THIS_SUBSTRATE" in r["gates_not_met"]
    assert r["null"]["fraction_clearing_1.05"] > 0.95, \
        "essentially every random pair clears the orthogonality bar"
    assert r["null"]["n_pairs"] >= 1000


def test_the_measured_value_is_unremarkable_against_its_own_null():
    r = _r()
    sz = r["salat_zakat"]
    assert sz["VIF"] < 1.001
    assert 20 <= sz["percentile_in_null"] <= 80, \
        "sits in the middle of the null -- most random pairs look just like it"


def test_EVERY_PAIR_LOOKS_ORTHOGONAL_INCLUDING_SAME_ROOT_WORDS():
    """A metric that calls IMAN and MUMIN independent is not measuring independence."""
    r = _r()
    m = r["pairwise_matrix"]
    assert len(m) == 28
    assert all(v < 1.05 for v in m.values() if v is not None)
    assert m["IMAN|MUMIN"] < 1.05, "same root, still 'orthogonal'"
    assert m["MILLAH|NASARA"] < 1.05, "co-occur in 2:120, still 'orthogonal'"


def test_the_quoted_figure_is_explicitly_disqualified():
    r = _r()
    d = r["post_run_disclosures"]["D1_THE_QUOTED_FIGURE_IS_NOT_EVIDENCE"]
    assert d["quoted"] == 1.000073
    assert d["fraction_of_random_pairs_clearing_the_bar"] > 0.95
    assert "supports no claim" in d["note"]


def test_the_category_difference_from_yeast_and_github_is_recorded():
    r = _r()
    g = [x for x in r["gates"]
         if x["id"] == "W6_is_a_text_count_VIF_the_same_quantity_as_a_node_feature_VIF"][0]
    assert g["weight"] == "excluded"
    assert "CONTINUOUS PER-NODE FEATURES" in g["detail"]
    assert "does not make the quantities comparable" in g["detail"]


def test_W5_FAILED_and_the_asymmetry_is_the_finding():
    """'Those who believed' 268 times. 'Those who submitted' once."""
    r = _r()
    assert "W5_THE_DESIGNATION_TEST_EXTENDED_TO_muslim_AND_mumin" in r["gates_not_met"]
    d = r["designation"]
    assert d["A_M_N"] > 200
    assert d["S_L_M"] == 1 and d["S_L_M_refs"] == ["5:44"]


def test_the_designation_test_is_the_one_that_survives():
    r = _r()
    d = r["post_run_disclosures"]["D2_WHAT_SURVIVES_AND_IT_IS_NOT_THE_VIF"]
    assert "7 of 7 control proper nouns at zero" in d["note"]
    assert "the VIF is not" in d["note"]


def test_integrity_passed_after_the_orthography_bug_was_fixed():
    r = _r()
    assert "W1_integrity" not in r["gates_not_met"]
    assert all(v > 0 for v in r["track_token_totals"].values())
    assert r["track_token_totals"]["MUMIN"] > 0, "the regex that returned 0 on the first run"
    src = open(os.path.join(HERE, "qvif.py"), encoding="utf-8").read()
    assert "caught by the W1 integrity gate on the first run" in src


def test_no_meaning_no_communities_and_no_design_claim():
    r = _r()
    g = [x for x in r["gates"] if x["id"] == "W7_meaning_and_communities"][0]
    assert g["weight"] == "excluded" and "OUT OF SCOPE" in g["detail"]
    d = r["post_run_disclosures"]["D4_what_none_of_this_licenses"]
    assert "not be evidence of authorial architecture" in d["note"]


def test_score_is_one_of_three_and_nothing_simulated():
    r = _r()
    assert r["score"] == "1/3"
    assert sorted(r["gates_not_met"]) == [
        "W2_PRIMARY_DOES_THE_VIF_GATE_DISCRIMINATE_ON_THIS_SUBSTRATE",
        "W5_THE_DESIGNATION_TEST_EXTENDED_TO_muslim_AND_mumin",
    ]
    assert r["simulated_values"] == 0
