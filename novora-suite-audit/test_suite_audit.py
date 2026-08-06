"""
test_suite_audit.py -- cross-component audit of the Novora stack: 5/5.

THIS RUN EXISTS TO CORRECT ME AND TO DRAW A BOUNDARY.

N1 — I WAS WRONG IN THE PREVIOUS REPORT. I said six components (pages, page-code,
agency-net, echo, novora-helm, novora-suite) have "no tests at all". There are 27
.test.mjs suites in the tree and every one of those six ships at least one. My sweep
counted only Python test_*.py, so it was blind to the entire Node runtime — including
hf-cohort/hf.test.mjs and cross-stack/github_pilot.test.mjs, Hugging Face and GitHub
cohort tests that already existed. Same class of error the OQM blind-spot audit named:
a true count with a false implication. reproduce_all.sh runs BOTH runtimes and is the
only complete measure of this repo.

N2 — THE LIVE FETCH IS BLOCKED AND IS NOT FAKED. api.github.com returns 403 and
huggingface.co returns 000. The agent proxy's own status endpoint logs
connect_rejected for huggingface.co:443, detail "gateway answered 403 to CONNECT
(policy denial or upstream failure)". The environment rule is to report policy denials
rather than retry or work around them. No live Qwen or DeepSeek data was fetched and
none is claimed.

N3 — THE COMMITTED DATA CANNOT CARRY THE REQUESTED COMPARISON EITHER. Across 992
GitHub repositories and 24 Hugging Face models, DeepSeek appears EXACTLY ONCE:
deepseek-ai/DeepSeek-V3. Zero DeepSeek on HF, zero Qwen repos on GitHub. One witness
is ONE_WING under the rule used throughout this repository, so a Qwen-versus-DeepSeek
comparison cannot be run at the strength the request implies. A second independent
DeepSeek record would change that, and the gate says so.

N4 — AND THE QWEN HITS ARE DERIVATIVES. Six of the seven carry a base_model beginning
"Qwen/" while their own id belongs to a different org — community fine-tunes such as
prism-ml/Ternary-Bonsai-27B-gguf, not Qwen's own releases. Calling them "Qwen models"
would overstate what the cohort holds.

N5 — THE STACK DOES REPRODUCE IN ONE OFFLINE COMMAND. 47 suite lines, 47 passing, 0
failing. Note the trap the gate had to avoid: two suite NAMES contain the word FAIL
because they describe a prediction the suite FALSIFIED, not a harness failure. A naive
grep would have reported failures that do not exist.

WHAT A GREEN HARNESS DOES NOT MEAN — N7, weight:excluded. Several suites pass while
recording falsified central predictions: sovereign-bank's portfolio advantage
collapsed to a TIE and its prescriptive floor ANTI-SELECTS, submesh pooling's k=20
prediction was wrong, knowledge-breakthroughs' thesis was FALSIFIED, central-tail-risk's
credit-creation explanation was REFUTED. Green means the bookkeeping is honest. It
does not mean the theories are confirmed, and conflating the two is the error this
repository exists to prevent.

AND N6, weight:excluded — nothing here evaluates Qwen's or DeepSeek's outputs, safety,
quality or governance behaviour. A test that was never run cannot be scored.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "c6f599ac8c81fd5fee866bb348881fb56d479486ef0ca1ef028aab34c3585d07"
_C = {}


def _r():
    if "r" not in _C:
        p = subprocess.run([sys.executable, os.path.join(HERE, "audit.py")],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        _C["r"] = json.load(open(os.path.join(HERE, "results_suite_audit.json"),
                                 encoding="utf-8"))
    return _C["r"]


def _gate(gid):
    return {g["id"]: g for g in _r()["gates"]}[gid]


def test_spec_is_locked():
    s = json.load(open(os.path.join(HERE, "prereg", "suite_audit_prereg.json"),
                       encoding="utf-8"))
    got = hashlib.sha256(json.dumps(s, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False).encode("utf-8")).hexdigest()
    assert got == LOCKED


def test_PRIMARY_my_previous_no_tests_claim_was_wrong():
    r = _r()
    assert r["node_suites"] == 27
    for c in ("pages", "page-code", "agency-net", "echo", "novora-helm",
              "novora-suite"):
        assert r["node_suites_per_component"][c], "%s ships a Node suite" % c
    d = _gate("N1_THE_NODE_SUITES_EXIST_AND_MY_EARLIER_COUNT_WAS_WRONG")["detail"]
    assert "CONFIRMS MY OWN ERROR" in d
    assert "true count with a false implication" in d


def test_the_correction_is_recorded_in_the_spec_itself():
    c = _r()["correction"]
    assert "no tests at all" in c["what_I_said"]
    assert "blind to the entire Node runtime" in c["why_it_was_wrong"] or \
        "pytest cannot see" in c["why_it_was_wrong"]


def test_PRIMARY_the_network_is_blocked_and_nothing_live_is_claimed():
    r = _r()
    assert r["network"]["api.github.com"] == "403"
    assert r["network"]["huggingface.co"] not in ("200", "301", "302")
    d = _gate("N2_THE_LIVE_FETCH_IS_BLOCKED_AND_NOT_FAKED")["detail"]
    assert "policy denial" in d
    assert "would be fabricated" in d


def test_PRIMARY_deepseek_is_one_witness_so_the_comparison_cannot_run():
    r = _r()
    c = r["cohorts"]
    assert c["github_deepseek"] == ["deepseek-ai/DeepSeek-V3"]
    assert c["hf_deepseek"] == 0
    assert c["github_qwen"] == 0
    d = _gate("N3_DEEPSEEK_IS_ONE_WING_IN_THE_COMMITTED_DATA")["detail"]
    assert "ONE_WING" in d and "CANNOT BE RUN" in d
    assert "would change that" in d


def test_the_qwen_entries_are_community_derivatives():
    r = _r()
    assert r["cohorts"]["hf_qwen_derived"] >= 5
    d = _gate("N4_THE_QWEN_ENTRIES_ARE_DERIVATIVES_NOT_QWEN_RELEASES")["detail"]
    assert "not Qwen's own releases" in d
    assert "would overstate" in d


def test_the_harness_is_green_and_the_FAIL_named_suites_are_not_failures():
    r = _r()
    h = r["harness"]
    assert h["log_present"] and h["failing"] == []
    assert h["passing"] == h["suite_lines"] and h["suite_lines"] >= 40
    assert len(h["names_mentioning_FAIL_but_passing"]) >= 2, \
        "a naive grep would have reported failures that do not exist"


def test_a_green_harness_does_not_validate_the_theories():
    g = _gate("N7_does_a_green_harness_validate_the_stack_s_CLAIMS")
    assert g["weight"] == "excluded"
    assert "collapsed to a tie" in g["detail"] and "ANTI-SELECTS" in g["detail"]
    assert "not a validated theory" in g["detail"]


def test_no_model_behaviour_was_evaluated():
    g = _gate("N6_does_this_audit_test_QWEN_or_DEEPSEEK_BEHAVIOUR")
    assert g["weight"] == "excluded"
    assert "Nothing here evaluates either model" in g["detail"]
    assert "what the network permits" in g["detail"]


def test_score_is_five_of_five_and_nothing_simulated():
    r = _r()
    assert r["score"] == "5/5" and r["gates_not_met"] == []
    assert r["simulated_values"] == 0
