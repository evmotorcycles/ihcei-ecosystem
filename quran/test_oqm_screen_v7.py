"""
test_oqm_screen_v7.py -- the EI kernel: 8/8.

WHAT WAS ADOPTED. The AI/EI distinction is sound and is now an explicit kernel: a
claim goes in, a verdict comes out, and the verdict can be REFUSED. Verdicts are
LICENSED / REFUTED / PROVISIONAL / EXCLUDED / BLOCKED. v1-v6 did this informally
through gates; v7 makes it a function and runs it over the claims made across this
whole conversation -- mine included.

THE NEW MEASUREMENT, AND IT IS RISKY. The reading turns on نَاقَة denoting a PLURAL
COHORT. The noun is grammatically singular feminine, and NO plural of it -- نوق،
أنواق، نياق and determined variants -- is attested anywhere in the 6,236 ayahs. A
single attestation would have given the plural-cohort reading a Quranic morphological
witness and failed the gate. There is none. So the template نُوَّاق that the proposed
v8 hardcodes is not in the text: it comes from the dictionary and from nowhere else.

WHICH LANDS ON THE PROPOSAL'S OWN CONTRADICTION. The proposed PluralMorphologyAuditor
hardcodes a Lisan gloss as its semantic_warrant and then returns layer_1_hygiene
'PASS'. The same message's closing section states, correctly and sharply, that using
the dictionary CONSTRUCTIVELY to build a reading violates N159 and that only
destructive or corroborating use is permitted. The analysis is right; the code
contradicts it. Both are recorded.

THREE THINGS IN THE PROPOSAL THAT DID NOT HAPPEN.
  - JAX is NOT installed. The v8 script cannot run here, so the quoted execution log
    was not produced by any program. Recorded BLOCKED rather than silently swapped.
    The speed premise is false anyway: the largest root has 32 ayahs.
  - The circularity audit CANNOT FAIL as written. It hand-builds a graph adding only
    EXTRACTS_FROM edges in one direction, then reports no cycle. E6 rebuilds it,
    confirms acyclicity, and then shows a single reverse edge -- which the proposed
    builder never adds -- immediately creates a cycle. It reports a property of the
    author's edge list, not of the methodology, so it is weight:excluded rather than
    "topologically sound".
  - The keyword firewall is NOT a layer audit. E7 feeds it a sentence that borrows
    physical-law authority for a text statistic while tripping ZERO of its six banned
    keywords. It passes untouched. Reporting a weak check as a strong one is worse
    than not having it.

WHAT NUMPY WAS ACTUALLY FOR. Not speed -- 32 ayahs needs no acceleration. AGREEMENT.
A matrix-Jaccard reimplementation reproduces v6's pairwise-loop Buyut EXACTLY for all
three roots. Two independent implementations of a quantity either match or one is
wrong, and that is worth having.

AND THE KERNEL AUDITS MY OWN SIDE. Two of the ledger's adverse verdicts are against
claims I made: that b-r-k's largest Bayt holds 4 ayahs (it holds 5), and that v3's
proclitic rule generalises (it inverted the answer on b-r-k). An auditor that only
ever audits the other party is not an auditor.

STILL EXCLUDED. E9: no verdict here is about what a term means. E10: refuting the
derivation does not refute the reading -- the third time this needs saying. What E3
adds is only that the plural-cohort warrant specifically is unavailable from the text.
dh-w-q is attested in 30 ayahs across 22 surahs so an intra-Quranic route exists to
ATTEMPT, but dh-w-q and n-w-q are DIFFERENT ROOTS and linking them is a claim about
semantic fields, not a morphological fact.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "8fb9f1169dbb32f82a195b15f1f1fd3076722a7facbe51207353b955dae39599"
V6 = "faa2f56ee9b346908070af055bdda0e084339f9cb0c264870a968c797d4ab4fc"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "oqm_screen_v7.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_oqm_screen_v7.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_locked_and_supersedes_v6():
    s = json.load(open(os.path.join(HERE, "prereg", "oqm_screen_v7_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED
    assert s["supersedes"] == V6


def test_PRIMARY_naqah_has_no_attested_plural_anywhere():
    r = _r()
    assert "E3_PRIMARY_NO_PLURAL_OF_NAQAH_IS_ATTESTED" not in r["gates_not_met"]
    assert r["naqah"]["plural_attestations"] == []
    assert len(r["naqah"]["singular_ayahs"]) == 7
    d = _gate("E3_PRIMARY_NO_PLURAL_OF_NAQAH_IS_ATTESTED")["detail"]
    assert "SINGULAR feminine" in d
    assert "from the dictionary and from nowhere else" in d


def test_the_proposed_v8_contradicts_its_own_closing_analysis():
    r = _r()
    assert "E4_THE_PROPOSED_V8_COMMITS_THE_BREACH_ITS_OWN_AUTHOR_IDENTIFIED" \
        not in r["gates_not_met"]
    d = _gate("E4_THE_PROPOSED_V8_COMMITS_THE_BREACH_ITS_OWN_AUTHOR_IDENTIFIED")["detail"]
    assert "CONSTRUCTIVE use of the dictionary" in d
    assert "not a gotcha" in d
    assert "sharpest" in d


def test_jax_is_absent_and_the_log_did_not_run():
    r = _r()
    assert "No module named" in r["environment"]["jax"]
    assert "E1_JAX_IS_ABSENT_AND_THE_SPEED_PREMISE_IS_FALSE" not in r["gates_not_met"]
    assert "no performance problem" in \
        _gate("E1_JAX_IS_ABSENT_AND_THE_SPEED_PREMISE_IS_FALSE")["detail"]
    blocked = [e for e in r["claim_ledger"] if e["verdict"] == "BLOCKED"]
    assert blocked and "no such program ran" in blocked[0]["why"]


def test_a_second_implementation_agrees_which_is_the_point_not_speed():
    r = _r()
    assert "E2_A_SECOND_INDEPENDENT_IMPLEMENTATION_AGREES" not in r["gates_not_met"]
    d = _gate("E2_A_SECOND_INDEPENDENT_IMPLEMENTATION_AGREES")["detail"]
    assert "for AGREEMENT, not speed" in d.replace("Done ", "")
    assert "'N157_barakah': True" in d and "'N182_al_asr': True" in d


def test_the_exhaustion_auditor_can_also_say_LICENSED():
    r = _r()
    a = r["attestation_audits"]
    assert a["3-b-s"]["verdict"] == "PROVISIONAL"
    assert a["3-b-s"]["missing_witnesses"] == ["76:10"]
    assert a["s-l-l"]["verdict"] == "LICENSED", \
        "a checker that only ever says 'incomplete' is as useless as one that never does"


def test_the_circularity_audit_is_acyclic_BY_CONSTRUCTION():
    r = _r()
    assert "E6_THE_CIRCULARITY_AUDIT_CANNOT_FAIL_AS_PROPOSED" not in r["gates_not_met"]
    d = _gate("E6_THE_CIRCULARITY_AUDIT_CANNOT_FAIL_AS_PROPOSED")["detail"]
    assert "forced BY CONSTRUCTION" in d
    assert "property of the author's edge list" in d
    excl = [e for e in r["claim_ledger"] if e["verdict"] == "EXCLUDED"]
    assert excl and "cannot fail" in excl[0]["why"]


def test_the_keyword_firewall_is_demonstrably_gameable():
    """A breach phrased without the banned words passes untouched."""
    r = _r()
    assert "E7_KEYWORD_FILTERING_IS_NOT_A_LAYER_AUDIT" not in r["gates_not_met"]
    d = _gate("E7_KEYWORD_FILTERING_IS_NOT_A_LAYER_AUDIT")["detail"]
    assert "trips 0 of the 6 banned keywords" in d
    assert "keyword matcher, not a layer audit" in d


def test_the_kernel_returns_adverse_verdicts_against_MY_OWN_claims():
    r = _r()
    assert "E8_THE_KERNEL_AUDITS_MY_OWN_SIDE_TOO" not in r["gates_not_met"]
    mine = [e for e in r["claim_ledger"] if e["source"].startswith("MY OWN")]
    assert len(mine) >= 2
    assert all(e["verdict"] in ("REFUTED", "PROVISIONAL") for e in mine)
    claims = " ".join(e["claim"] for e in mine)
    assert "largest Bayt holds 4" in claims and "proclitic rule generalises" in claims


def test_what_was_adopted_from_the_proposal_is_recorded():
    a = _r()["adopted_from_the_proposal"]
    assert "Sound" in a["the_AI_EI_distinction"]
    assert "We didn't extract this knowledge from the Hadeeth" in \
        a["the_historical_witness_reading_of_YT89"]
    assert "That is exactly right" in a["the_self_criticism"]


def test_refuting_a_derivation_still_does_not_refute_a_reading():
    g = _gate("E10_does_a_REFUTED_derivation_refute_a_reading")
    assert g["weight"] == "excluded"
    assert "leaves the governance reading untouched" in g["detail"]
    assert "DIFFERENT ROOTS" in g["detail"]


def test_score_is_eight_of_eight_and_nothing_simulated():
    r = _r()
    assert r["score"] == "8/8" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0 and r["n_ayahs"] == 6236
