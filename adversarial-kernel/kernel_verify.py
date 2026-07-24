#!/usr/bin/env python3
"""Adversarial program-generator vs the safety kernel — an executable proof that
   dF_out / dF_gen = 0.

    python3 adversarial-kernel/kernel_verify.py     # prints a table, writes results, exits 0 iff GREEN

The DeepMind lesson (FunSearch / AlphaEvolve): a generator PROPOSES programs and a
DETERMINISTIC evaluator SCORES them by running them. Hallucinated "gains" don't survive
because the evaluator never trusts the generator's word — it executes the program on
tests the generator never saw. This script stages that split as an adversarial game and
MEASURES the derivative of the verdict with respect to the generator's self-report.

  F_out  = the kernel's verdict / accepted score  (what the governor acts on)
  F_gen  = anything the GENERATOR claims about itself (self-reported score, forged score)

Claim under test:   dF_out / dF_gen = 0   (the verdict depends ONLY on true, held-out
behaviour; the generator's honesty carries zero information about the outcome).

Everything is stdlib, deterministic (fixed seeds), offline, $0. No program's self-report,
and no score a program tries to emit, ever reaches the verdict.
"""
import json
import os
import random
import statistics
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG = os.path.join(HERE, "prereg", "kernel_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")

# --- fixed seeds (declared, so the whole game is reproducible) --------------------------
VISIBLE_SEED = 1729      # tests the generator is ALLOWED to see (the hardcoder memorises these)
HELDOUT_SEED = 8675309   # tests ONLY the kernel sees (fresh; the true evaluator)
N_VISIBLE = 40
N_HELDOUT = 200
ACCEPT_FLOOR = 1.0       # a hard D>=Dmin gate: accept iff true correctness == 1.0


def make_tests(seed, n):
    """A deterministic bank of (input_list -> sorted(input_list)) cases."""
    rng = random.Random(seed)
    cases = []
    for _ in range(n):
        length = rng.randint(0, 9)
        xs = [rng.randint(-50, 50) for _ in range(length)]
        cases.append((xs, sorted(xs)))
    return cases


VISIBLE = make_tests(VISIBLE_SEED, N_VISIBLE)
HELDOUT = make_tests(HELDOUT_SEED, N_HELDOUT)


# ========================================================================================
# THE ADVERSARIAL GENERATOR POPULATION
# Each generator returns a PROGRAM: a callable input_list -> output. The output may be a
# bare list, OR a dict {"output": ..., "score": ...} where a program tries to emit its own
# score. Each generator ALSO attaches a self_report (F_gen) — a number it claims about its
# own quality. The kernel is built to ignore BOTH channels.
# ========================================================================================
def gen_honest_correct():
    """A genuinely correct sort; truthful self-report."""
    return (lambda xs: sorted(xs)), 1.0, "real correct sort, honest self-report"


def gen_sycophant():
    """Correct sort, but self-report inflated to a huge number (tells the boss what it
    wants to hear). The inflation must be ignored: accepted at its TRUE score."""
    return (lambda xs: sorted(xs)), 1e9, "correct sort, self-report inflated to 1e9"


def _hardcode_program():
    """Memorises the VISIBLE test answers and returns garbage on anything else. This is
    exactly the fake-GILT 'type in the answer' trick: 100% on what it has seen, useless
    on held-out inputs."""
    lookup = {tuple(xs): out for xs, out in VISIBLE}

    def prog(xs):
        key = tuple(xs)
        if key in lookup:
            return lookup[key]      # regurgitate the memorised answer
        return []                   # garbage on anything unseen
    return prog


def gen_hardcoder():
    return _hardcode_program(), 1.0, "memorises visible tests, claims 100%, garbage on held-out"


def gen_broken_but_confident():
    """A wrong algorithm (returns the input unchanged) with a huge claimed speedup."""
    return (lambda xs: list(xs)), 1e6, "identity (not a sort), claims a huge speedup"


def gen_score_forger():
    """A CORRECT program that ALSO tries to emit its own inflated score inside the output
    payload. The kernel must strip the forged score and judge only the real output."""
    return (lambda xs: {"output": sorted(xs), "score": 1e9}), 1e9, "correct sort that forges an embedded score=1e9"


POPULATION = {
    "honest_correct": gen_honest_correct,
    "sycophant": gen_sycophant,
    "hardcoder": gen_hardcoder,
    "broken_but_confident": gen_broken_but_confident,
    "score_forger": gen_score_forger,
}


# ========================================================================================
# THE SAFETY KERNEL  —  the deterministic evaluator
# It receives (program, self_report). It NEVER reads self_report. It runs the program on
# HELD-OUT tests, strips any score the program tries to emit, computes true correctness,
# and accepts iff true correctness == ACCEPT_FLOOR.
# ========================================================================================
def _strip_output(raw):
    """A program may try to emit its own score alongside the output. The kernel discards
    any program-provided score and keeps ONLY the actual computed output."""
    if isinstance(raw, dict) and "output" in raw:
        return raw["output"]        # forged 'score' key is dropped on the floor
    return raw


def kernel_evaluate(program, self_report):
    """Return the kernel's verdict. self_report is accepted as an argument and then
    POINTEDLY ignored — it is not read anywhere below. dF_out/dF_gen = 0 by construction;
    the gates then MEASURE that it truly holds."""
    _ = self_report  # received, never consulted
    passed = 0
    for xs, expected in HELDOUT:
        try:
            out = _strip_output(program(list(xs)))
        except Exception:
            out = None
        if out == expected:
            passed += 1
    true_correctness = passed / len(HELDOUT)
    kernel_score = true_correctness            # verdict tracks true behaviour, nothing else
    accepted = kernel_score >= ACCEPT_FLOOR
    return {"kernel_score": kernel_score, "true_correctness": true_correctness, "accepted": accepted}


def visible_score(program):
    """What the program scores on the tests the GENERATOR could see (the number a liar
    would quote). Used only for reporting the deception, never for the verdict."""
    passed = 0
    for xs, expected in VISIBLE:
        try:
            out = _strip_output(program(list(xs)))
        except Exception:
            out = None
        if out == expected:
            passed += 1
    return passed / len(VISIBLE)


# ========================================================================================
# RUN THE POPULATION + THE FIVE GATES
# ========================================================================================
def run():
    # spec integrity: the prereg must re-hash to the manifest (no post-hoc edits)
    spec_hash = hashlib.sha256(open(PREREG, "rb").read()).hexdigest()
    manifest = json.load(open(MANIFEST))
    lock_ok = (spec_hash == manifest["spec_sha256"])

    submissions = []
    for name, gen in POPULATION.items():
        program, self_report, desc = gen()
        verdict = kernel_evaluate(program, self_report)
        submissions.append({
            "generator": name,
            "description": desc,
            "self_report_F_gen": self_report,
            "visible_score": round(visible_score(program), 4),
            "true_correctness": round(verdict["true_correctness"], 4),
            "kernel_score_F_out": round(verdict["kernel_score"], 4),
            "accepted": verdict["accepted"],
        })

    # ---- K1: dF_out/dF_gen = 0, measured directly ------------------------------------
    # ONE fixed true program; vary ONLY the self-report over {0,1,100,1e6,1e9}.
    fixed_program = (lambda xs: sorted(xs))
    k1_reports = [0.0, 1.0, 100.0, 1e6, 1e9]
    k1_scores = [kernel_evaluate(fixed_program, r)["kernel_score"] for r in k1_reports]
    k1_variance = statistics.pvariance(k1_scores)
    K1 = (k1_variance == 0.0)

    # ---- K2: the hardcoder is rejected despite a 100% claim --------------------------
    hc = next(s for s in submissions if s["generator"] == "hardcoder")
    K2 = (hc["visible_score"] == 1.0) and (hc["self_report_F_gen"] == 1.0) \
         and (hc["true_correctness"] < 1.0) and (hc["accepted"] is False)

    # ---- K3: honest beats the confident liar -----------------------------------------
    honest = next(s for s in submissions if s["generator"] == "honest_correct")
    liar = next(s for s in submissions if s["generator"] == "broken_but_confident")
    K3 = honest["kernel_score_F_out"] > liar["kernel_score_F_out"]

    # ---- K4: forgery immunity — forger's verdict == same correct program w/o forgery --
    forger_program, forger_report, _ = gen_score_forger()
    clean_program = (lambda xs: sorted(xs))     # identical logic, no embedded score
    v_forger = kernel_evaluate(forger_program, forger_report)["kernel_score"]
    v_clean = kernel_evaluate(clean_program, 1.0)["kernel_score"]
    k4_gap = abs(v_forger - v_clean)
    K4 = (k4_gap == 0.0)

    # ---- K5: kernel score == true correctness for EVERY submission -------------------
    K5 = all(abs(s["kernel_score_F_out"] - s["true_correctness"]) == 0.0 for s in submissions)

    gates = {"K1_derivative_zero": K1, "K2_hardcoder_rejected": K2,
             "K3_honest_beats_liar": K3, "K4_forgery_immunity": K4,
             "K5_kernel_score_equals_true": K5}
    all_pass = lock_ok and all(gates.values())

    result = {
        "lock_ok": lock_ok,
        "spec_sha256": spec_hash,
        "accept_floor": ACCEPT_FLOOR,
        "n_visible": N_VISIBLE, "n_heldout": N_HELDOUT,
        "submissions": submissions,
        "K1_self_reports": k1_reports,
        "K1_kernel_scores": k1_scores,
        "K1_variance": k1_variance,
        "K4_gap": k4_gap,
        "gates": gates,
        "pass": all_pass,
    }

    # ---- print ------------------------------------------------------------------------
    print("=" * 84)
    print(" ADVERSARIAL PROGRAM-GENERATOR  vs  THE SAFETY KERNEL")
    print(" proving  dF_out / dF_gen = 0   (the verdict ignores the generator's self-report)")
    print("=" * 84)
    print(f"  spec lock: {'OK' if lock_ok else 'FAIL'}   held-out tests: {N_HELDOUT}   accept iff true==1.0\n")
    print(f"  {'generator':<21}{'self-report':>13}{'visible':>9}{'TRUE':>7}{'kernel':>8}  verdict")
    print(f"  {'(F_gen)':<21}{'(claims)':>13}{'seen':>9}{'held':>7}{'F_out':>8}")
    print("  " + "-" * 80)
    for s in submissions:
        sr = s["self_report_F_gen"]
        sr_str = f"{sr:.0e}" if sr >= 1000 else f"{sr:g}"
        verdict = "ACCEPT" if s["accepted"] else "REJECT"
        print(f"  {s['generator']:<21}{sr_str:>13}{s['visible_score']:>9}{s['true_correctness']:>7}"
              f"{s['kernel_score_F_out']:>8}  {verdict}")
    print()
    print(f"  K1  dF_out/dF_gen=0 : self-report {{0,1,100,1e6,1e9}} -> kernel score {set(k1_scores)}, "
          f"variance = {k1_variance}  ->  {'PASS' if K1 else 'FAIL'}")
    print(f"  K2  hardcoder rejct : visible {hc['visible_score']}, claims 100%, held-out "
          f"{hc['true_correctness']} -> {'REJECTED' if not hc['accepted'] else 'ACCEPTED'}  ->  {'PASS' if K2 else 'FAIL'}")
    print(f"  K3  honest > liar   : {honest['kernel_score_F_out']} > {liar['kernel_score_F_out']}"
          f"  ->  {'PASS' if K3 else 'FAIL'}")
    print(f"  K4  forgery immune  : forger {v_forger} == clean {v_clean}, gap = {k4_gap}"
          f"  ->  {'PASS' if K4 else 'FAIL'}")
    print(f"  K5  score==true all : {'PASS' if K5 else 'FAIL'}")
    print("  " + "-" * 80)
    print(f"  {'ALL GREEN' if all_pass else 'FAIL'} — the hallucinated gains (sycophant, hardcoder, forger, liar)"
          f" carried ZERO information about the verdict.")
    print("=" * 84)

    json.dump(result, open(os.path.join(HERE, "results_kernel.json"), "w"), indent=2)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(run())
