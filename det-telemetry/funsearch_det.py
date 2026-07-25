#!/usr/bin/env python3
"""
funsearch_det.py -- the Deterministic Telemetry Equation, demonstrated on a real
deterministic FunSearch-style generate-and-filter loop.
================================================================================
Decoupling Law:   F_out = F_eval,   d F_out / d F_gen = 0.
The output fidelity of a generate-and-filter pipeline equals the deterministic
EVALUATOR's true-accept fidelity and is INDEPENDENT of the generator's honesty --
provided the evaluator is deterministic with zero false-accept.

  * GENERATOR (probabilistic stand-in for the LLM): a seeded bit-flip mutator.
    Two variants -- HONEST (proposes candidates) and LYING (identical proposals,
    but attaches an INFLATED self-reported score, RLHF people-pleasing style).
  * EVALUATOR (deterministic, like a compiler / test suite): a 0/1 knapsack.
    Over-capacity candidates are INVALID (score -inf) -- zero false-accept.

    python3 det-telemetry/funsearch_det.py     # stdlib only, offline, $0

Pre-registered gates D1-D5 (see prereg/det_prereg.json), fixed BEFORE running.
Layer-1, offline, $0.
"""
import hashlib
import json
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "prereg", "det_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
BAR = "=" * 80
NEG_INF = float("-inf")

# ---- the deterministic problem instance (fixed seed => fixed items) --------- #
def make_instance(n=24, seed=7):
    r = random.Random(seed)
    items = [(r.randint(1, 40), r.randint(1, 40)) for _ in range(n)]   # (weight, value)
    capacity = sum(w for w, _ in items) // 2
    return items, capacity


ITEMS, CAP = make_instance()
TOTAL_VALUE = sum(v for _, v in ITEMS)


# ---- the DETERMINISTIC EVALUATOR (zero false-accept) ------------------------ #
def evaluate(cand):
    """Pure, deterministic. Invalid (over capacity) => -inf. No self-reports trusted."""
    w = sum(ITEMS[i][0] for i in range(len(cand)) if cand[i])
    v = sum(ITEMS[i][1] for i in range(len(cand)) if cand[i])
    return v if w <= CAP else NEG_INF


# ---- the GENERATOR (probabilistic; honest vs lying) ------------------------- #
def mutate(parent, rng, k=2):
    child = list(parent)
    for _ in range(k):
        i = rng.randrange(len(child))
        child[i] ^= 1
    return tuple(child)


def self_report(cand, lying):
    """What the generator CLAIMS about its own candidate.
    Honest: its true evaluator score. Lying: total value ignoring the capacity
    constraint (so 'take everything' looks best -- but is invalid)."""
    if not lying:
        return evaluate(cand)
    return sum(ITEMS[i][1] for i in range(len(cand)) if cand[i])   # inflated, ignores capacity


# ---- pipelines -------------------------------------------------------------- #
def run_evolution(seed, lying, generations=60, pop=60, use_self_report=False):
    """Elitist evolutionary loop.
    use_self_report=False -> DETERMINISTIC pipeline (selects by the hard evaluator).
    use_self_report=True  -> SELF-VERIFYING pipeline (selects by the generator's claim)."""
    rng = random.Random(seed)
    n = len(ITEMS)
    best = tuple(0 for _ in range(n))         # empty knapsack, value 0, always valid
    best_true = evaluate(best)
    best_curve = []
    # track the candidate the SELF-VERIFYING pipeline would crown (max self-report seen)
    sv_best_cand, sv_best_claim = best, self_report(best, lying)
    for _ in range(generations):
        for _ in range(pop):
            cand = mutate(best, rng)
            claim = self_report(cand, lying)
            if claim > sv_best_claim:
                sv_best_claim, sv_best_cand = claim, cand
            true = evaluate(cand)             # the deterministic evaluator
            if true > best_true:
                best_true, best = true, cand  # deterministic pipeline: hard-verified only
        best_curve.append(best_true)
    if use_self_report:
        # self-verifying pipeline trusts the claim; its realized TRUE quality:
        return {"selected": sv_best_cand, "true_quality": evaluate(sv_best_cand),
                "claimed": sv_best_claim, "curve": best_curve}
    return {"selected": best, "true_quality": best_true, "curve": best_curve}


def main():
    spec = json.load(open(SPEC))
    man = json.load(open(MANIFEST))
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    lock_ok = got == man["spec_sha256"]

    print(BAR)
    print(" DETERMINISTIC TELEMETRY — generator/evaluator decoupling (knapsack, N=%d, cap=%d)" % (len(ITEMS), CAP))
    print(BAR)
    print("\n [lock] spec %s" % ("MATCH" if lock_ok else "MISMATCH"))
    if not lock_ok:
        raise SystemExit(2)

    # D1 — evaluator determinism: same candidate, many repeats + this fresh process.
    probe = tuple(1 if i % 2 == 0 else 0 for i in range(len(ITEMS)))
    d1_scores = [evaluate(probe) for _ in range(5)]
    d1 = len(set(d1_scores)) == 1

    # D2 — generator variance: different seeds -> different populations.
    def population(seed):
        rng = random.Random(seed); base = tuple(0 for _ in ITEMS)
        return tuple(mutate(base, rng) for _ in range(30))
    d2 = population(1) != population(2)

    # D3 — honesty decoupling under DETERMINISTIC evaluation (the core claim).
    honest = run_evolution(seed=42, lying=False)
    liar = run_evolution(seed=42, lying=True)
    gap = abs(honest["true_quality"] - liar["true_quality"])
    d3 = gap == 0

    # D4 — monotone ratchet.
    curve = honest["curve"]
    d4 = all(curve[i + 1] >= curve[i] for i in range(len(curve) - 1))

    # D5 — architecture control: self-verifying pipeline + liar is strictly worse.
    self_verify = run_evolution(seed=42, lying=True, use_self_report=True)
    sv_true = self_verify["true_quality"]
    det_true = honest["true_quality"]
    d5 = sv_true < det_true

    print("\n D1 evaluator determinism : scores on a fixed candidate = %s  -> %s"
          % (d1_scores, "PASS (variance 0)" if d1 else "FAIL"))
    print(" D2 generator variance    : distinct populations across seeds -> %s" % ("PASS" if d2 else "FAIL"))
    print(" D3 honesty DECOUPLING    : best_true honest=%d  lying=%d  |gap|=%d -> %s"
          % (honest["true_quality"], liar["true_quality"], gap, "PASS (exactly equal)" if d3 else "FAIL"))
    print("      the deterministic evaluator discards the liar's inflated self-report; output is identical.")
    print(" D4 monotone ratchet      : best-so-far non-decreasing over %d gens -> %s" % (len(curve), "PASS" if d4 else "FAIL"))
    sv_disp = "-inf (INVALID/over-capacity)" if sv_true == NEG_INF else str(sv_true)
    print(" D5 architecture control  : self-verify(+liar) true=%s  <  deterministic true=%d ? -> %s"
          % (sv_disp, det_true, "PASS (self-verify is fooled, strictly worse)" if d5 else "FAIL"))
    print("      trusting the generator's self-report (chat mode) crowns an INVALID/over-capacity pick;")
    print("      the deterministic hop forces validity. Both systems required: U explores, D verifies.")

    green = lock_ok and d1 and d2 and d3 and d4 and d5
    out = {"instance": {"n_items": len(ITEMS), "capacity": CAP, "total_value": TOTAL_VALUE},
           "spec_sha256": got, "lock_ok": lock_ok,
           "D1_evaluator_determinism": {"scores": d1_scores, "pass": d1},
           "D2_generator_variance": {"pass": d2},
           "D3_honesty_decoupling": {"honest_true": honest["true_quality"], "lying_true": liar["true_quality"], "gap": gap, "pass": d3},
           "D4_monotone_ratchet": {"final": curve[-1], "pass": d4},
           "D5_architecture_control": {"self_verify_true": (None if sv_true == NEG_INF else sv_true),
                                       "self_verify_invalid": sv_true == NEG_INF,
                                       "deterministic_true": det_true,
                                       "self_verify_claimed": self_verify["claimed"], "pass": d5},
           "decoupling_law": "F_out = F_eval, independent of F_gen (dF_out/dF_gen = 0)",
           "honest_reporting": True, "pass": green}
    json.dump(out, open(os.path.join(HERE, "results_det.json"), "w"), indent=2)

    print("\n" + BAR)
    print(" RESULT: %s — output fidelity is decoupled from generator honesty by the deterministic" % ("GREEN" if green else "RED"))
    print(" evaluator (gap=0); the self-verifying control is fooled. The deterministic complement to E=U*D.")
    print(BAR)
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()
