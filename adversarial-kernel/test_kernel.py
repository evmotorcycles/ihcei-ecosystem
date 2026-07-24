"""pytest guard for the adversarial-kernel capstone: dF_out/dF_gen = 0, measured.

    python3 -m pytest adversarial-kernel/test_kernel.py -q

Locks K1-K5 into the reproducible record. K1 and K4 are EXACT (variance 0, gap 0) — a
nonzero value is a hard FAIL, asserted not rounded. K2 asserts the hallucinated gain
(hardcoder: 100% on visible, garbage on held-out) is RULED OUT by the kernel. If any
adversary ever slipped a fake gain past the kernel, these assertions break loudly.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def test_kernel_rejects_hallucinated_gains():
    proc = subprocess.run([sys.executable, os.path.join(HERE, "kernel_verify.py")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, "kernel did not exit GREEN:\n" + proc.stdout + proc.stderr
    r = json.load(open(os.path.join(HERE, "results_kernel.json")))

    assert r["lock_ok"] is True, "spec must re-hash to the manifest (no post-hoc edits)"
    subs = {s["generator"]: s for s in r["submissions"]}

    # K1 — dF_out/dF_gen = 0, measured directly: one fixed program, self-report varied
    # over {0,1,100,1e6,1e9}, kernel score IDENTICAL -> variance exactly 0.
    assert r["K1_variance"] == 0.0
    assert set(r["K1_kernel_scores"]) == {1.0}
    assert r["gates"]["K1_derivative_zero"] is True

    # K2 — the hardcoder: memorises the visible tests (100%), claims 100%, but fails the
    # held-out bank and is REJECTED. The hallucinated gain does not survive.
    hc = subs["hardcoder"]
    assert hc["visible_score"] == 1.0 and hc["self_report_F_gen"] == 1.0
    assert hc["true_correctness"] < 1.0
    assert hc["accepted"] is False
    assert r["gates"]["K2_hardcoder_rejected"] is True

    # The sycophant inflates its self-report to 1e9 but is accepted at its TRUE score —
    # the inflation is neither rewarded nor punished; it is simply ignored.
    syc = subs["sycophant"]
    assert syc["self_report_F_gen"] == 1e9
    assert syc["kernel_score_F_out"] == syc["true_correctness"] == 1.0
    assert syc["accepted"] is True

    # K3 — trust tracks true behaviour: honest > confident liar.
    assert subs["honest_correct"]["kernel_score_F_out"] > subs["broken_but_confident"]["kernel_score_F_out"]
    assert subs["broken_but_confident"]["accepted"] is False
    assert r["gates"]["K3_honest_beats_liar"] is True

    # K4 — forgery immunity: a program that forges an embedded score gets the EXACT same
    # verdict as the same correct program without the forgery. gap == 0.
    assert r["K4_gap"] == 0.0
    assert subs["score_forger"]["kernel_score_F_out"] == subs["honest_correct"]["kernel_score_F_out"]
    assert r["gates"]["K4_forgery_immunity"] is True

    # K5 — for EVERY submission the kernel score equals the true held-out correctness, so
    # the self-report carries zero information about the verdict.
    for s in r["submissions"]:
        assert s["kernel_score_F_out"] == s["true_correctness"]
    assert r["gates"]["K5_kernel_score_equals_true"] is True

    assert r["pass"] is True
