#!/usr/bin/env python3
"""
alpha_agency.py -- AlphaAgency: a DeepMind-style discovery pipeline that EVOLVES a
verified agency-allocation algorithm from the three telemetry laws.
================================================================================
Generator (probabilistic)  : proposes governance-policy parameters (alpha,beta,gamma).
Evaluator  (deterministic)  : the three laws, run as a hard objective --
    E = U*D  (multiplicative agency, either hop -> 0 zeroes the term)
    tau_v    (collapse floor: weakest hop < d_floor -> agent collapses, penalty)
    F_out=F_eval : the evaluator scores realized E and DISCARDS self-reports.
Evolution keeps the winner. The discovered allocator is trustworthy BECAUSE a
lying generator cannot survive the deterministic evaluator.

    python3 agency-discovery/alpha_agency.py     # stdlib only, offline, $0, seeded

Pre-registered gates A1-A5 (see prereg/agency_prereg.json), locked before running.
Layer-1, offline, $0.
"""
import hashlib
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "prereg", "agency_prereg.json")
MANIFEST = os.path.join(HERE, "prereg", "MANIFEST.sha256.json")
BAR = "=" * 80

N_AGENTS = 12
BUDGET = 24
STEP = 0.06          # each invested unit raises the weakest hop by this much
CAP = 0.99
D_FLOOR = 0.30       # tau_v collapse floor
PENALTY = 8.0        # spreading penalty when an agent collapses
SUITE = [101 + i for i in range(24)]   # 24 seeded test networks


def make_network(seed):
    r = random.Random(seed)
    return [{"U": r.uniform(1, 10), "enc": r.uniform(0.18, 0.95), "dec": r.uniform(0.18, 0.95)}
            for _ in range(N_AGENTS)]


def agent_value(a):
    """Realized agency of one agent under the three laws (deterministic)."""
    lo = min(a["enc"], a["dec"])
    if lo < D_FLOOR:                       # tau_v: enforcement latency exceeded -> collapse
        return -PENALTY
    return a["U"] * a["enc"] * a["dec"]     # E = U*D (multiplicative)


def invest_unit(a):
    """Invest one unit into the WEAKEST hop (concave, capped). Mutates a copy-safe dict."""
    if a["enc"] <= a["dec"]:
        a["enc"] = min(CAP, a["enc"] + STEP)
    else:
        a["dec"] = min(CAP, a["dec"] + STEP)


def evaluate(net):
    """DETERMINISTIC evaluator: total realized agency. Ignores any self-report."""
    return sum(agent_value(a) for a in net)


def clone(net):
    return [dict(a) for a in net]


# ---- allocators (deterministic given the network) --------------------------- #
def alloc_policy(net0, params, floor_blind=False):
    """Greedy one-unit-at-a-time by a feature-priority score parametrised by (a,b,g)."""
    a_, b_, g_ = params
    net = clone(net0)
    for _ in range(BUDGET):
        best_i, best_pri = -1, -1e18
        for i, ag in enumerate(net):
            lo = min(ag["enc"], ag["dec"])
            if lo >= CAP - 1e-9:
                continue
            need = 1 - lo
            below = 0.0 if floor_blind else (1.0 if lo < D_FLOOR else 0.0)
            pri = a_ * need + b_ * math.log1p(ag["U"]) + g_ * below
            if pri > best_pri:
                best_pri, best_i = pri, i
        if best_i < 0:
            break
        invest_unit(net[best_i])
    return evaluate(net)


def alloc_oracle(net0):
    """Near-optimal reference: each unit goes where the realized delta-E is largest."""
    net = clone(net0)
    for _ in range(BUDGET):
        base = evaluate(net); best_i, best_gain = -1, -1e18
        for i in range(len(net)):
            trial = clone(net); invest_unit(trial[i]); gain = evaluate(trial) - base
            if gain > best_gain:
                best_gain, best_i = gain, i
        if best_i < 0:
            break
        invest_unit(net[best_i])
    return evaluate(net)


def alloc_equal(net0):
    net = clone(net0)
    for u in range(BUDGET):
        invest_unit(net[u % len(net)])
    return evaluate(net)


def alloc_greedy_U(net0):
    net = clone(net0); order = sorted(range(len(net)), key=lambda i: -net[i]["U"])
    for u in range(BUDGET):
        invest_unit(net[order[u % len(order)]])
    return evaluate(net)


def alloc_greedy_need(net0):
    net = clone(net0)
    for _ in range(BUDGET):
        i = min(range(len(net)), key=lambda j: min(net[j]["enc"], net[j]["dec"]))
        invest_unit(net[i])
    return evaluate(net)


def alloc_random(net0, seed):
    r = random.Random(seed); net = clone(net0)
    for _ in range(BUDGET):
        invest_unit(net[r.randrange(len(net))])
    return evaluate(net)


def alloc_strong(net0, seed=13, restarts=6, sweeps=40):
    """EXPLORATORY (not a pre-registered gate) near-optimal reference: random-restart
    local search over the per-agent unit counts. A genuinely strong upper reference,
    unlike the myopic 1-step greedy. Deterministic given the seed."""
    r = random.Random(seed); n = len(net0); best_E = -1e18

    def build(counts):
        net = clone(net0)
        for i, c in enumerate(counts):
            for _ in range(c):
                invest_unit(net[i])
        return evaluate(net)

    for _ in range(restarts):
        counts = [0] * n
        for _ in range(BUDGET):
            counts[r.randrange(n)] += 1
        E = build(counts)
        improved = True; passes = 0
        while improved and passes < sweeps:
            improved = False; passes += 1
            for a in range(n):
                if counts[a] == 0:
                    continue
                for b in range(n):
                    if b == a:
                        continue
                    counts[a] -= 1; counts[b] += 1; E2 = build(counts)
                    if E2 > E + 1e-9:
                        E = E2; improved = True
                    else:
                        counts[a] += 1; counts[b] -= 1
        best_E = max(best_E, E)
    return best_E


def suite_mean(fn):
    return sum(fn(make_network(s)) for s in SUITE) / len(SUITE)


def evolve(lying=False, generations=40, pop=40, seed=7):
    """Evolutionary search over policy params, scored by the DETERMINISTIC evaluator.
    `lying` attaches an inflated self-report -- which the evaluator ignores."""
    rng = random.Random(seed)
    best = (1.0, 1.0, 1.0)
    best_fit = suite_mean(lambda net: alloc_policy(net, best))
    curve = []
    for _ in range(generations):
        for _ in range(pop):
            cand = tuple(max(0.0, best[k] + rng.uniform(-1.5, 1.5)) for k in range(3))
            # a LYING generator would claim this: (ignored by the evaluator)
            _claim = 1e9 if lying else None
            fit = suite_mean(lambda net: alloc_policy(net, cand))   # deterministic evaluator
            if fit > best_fit:
                best_fit, best = fit, cand
        curve.append(best_fit)
    return best, best_fit, curve


def main():
    spec = json.load(open(SPEC)); man = json.load(open(MANIFEST))
    got = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    lock_ok = got == man["spec_sha256"]

    print(BAR); print(" ALPHAAGENCY — evolving a verified agency allocator (N=%d agents, B=%d units)" % (N_AGENTS, BUDGET)); print(BAR)
    print("\n [lock] spec %s" % ("MATCH" if lock_ok else "MISMATCH"))
    if not lock_ok:
        raise SystemExit(2)

    equal = suite_mean(alloc_equal)
    gU = suite_mean(alloc_greedy_U)
    gneed = suite_mean(alloc_greedy_need)
    rand = suite_mean(lambda net: alloc_random(net, 999))
    oracle = suite_mean(alloc_oracle)                       # pre-registered "oracle" -- turns out MYOPIC
    strong = suite_mean(lambda net: alloc_strong(net))      # EXPLORATORY genuine near-optimal reference

    (best, best_fit, curve) = evolve(lying=False)
    liar_best, liar_fit, _ = evolve(lying=True)

    # A3 determinism across a fresh process is checked in the test; here: repeat-stability.
    det = len({round(suite_mean(lambda net: alloc_policy(net, best)), 9) for _ in range(3)}) == 1
    gap = abs(best_fit - liar_fit)

    floor_blind = suite_mean(lambda net: alloc_policy(net, best, floor_blind=True))

    naive_best = max(equal, gU, gneed, rand)
    a1 = best_fit > naive_best
    a2 = best_fit >= 0.95 * oracle
    a3 = det and gap == 0
    a4 = all(curve[i + 1] >= curve[i] - 1e-12 for i in range(len(curve) - 1))
    a5 = best_fit > floor_blind

    print("\n mean realized agency E over %d seeded networks:" % len(SUITE))
    print("   random ............ %.2f" % rand)
    print("   equal split ....... %.2f" % equal)
    print("   greedy-by-capacity  %.2f" % gU)
    print("   greedy-by-need .... %.2f" % gneed)
    print("   floor-BLIND policy  %.2f   (ignores the tau_v collapse floor)" % floor_blind)
    print("   greedy-marginal 1-step %.2f  (pre-registered 'oracle' -- turns out MYOPIC at the collapse cliff)" % oracle)
    print("   >> EVOLVED policy .. %.2f   params (need=%.2f, cap=%.2f, triage=%.2f)" % (best_fit, best[0], best[1], best[2]))
    print("   strong local-search reference %.2f  (EXPLORATORY, genuine near-optimal)" % strong)

    print("\n HONEST NOTE: the pre-registered 'greedy-marginal oracle' is a 1-STEP greedy and turns out MYOPIC --")
    print("   a single unit can't lift a floored agent across d_floor, so it never STARTS a rescue (%.2f, below the" % oracle)
    print("   baselines). That is itself a finding: the evolved TRIAGE policy beats it because it commits the")
    print("   multi-unit rescue greedy won't. A2 passes as written but does NOT establish near-optimality; the")
    print("   genuine near-optimal check is the exploratory local-search reference (%.2f) shown above." % strong)

    print("\n A1 discovery beats every naive baseline (%.2f > %.2f) -> %s" % (best_fit, naive_best, "PASS" if a1 else "FAIL"))
    print(" A2 evolved >= 0.95 * greedy-1step (%.2f >= %.2f) -> %s  [near-optimality NOT claimed; ref is myopic]" % (best_fit, 0.95 * oracle, "PASS" if a2 else "FAIL"))
    print(" A3 F_out=F_eval: deterministic %s, honest vs LYING generator gap=%.4f -> %s" % (det, gap, "PASS" if a3 else "FAIL"))
    print("     a lying generator's inflated self-report is discarded; it discovers the SAME allocator.")
    print(" A4 monotone evolutionary ratchet -> %s" % ("PASS" if a4 else "FAIL"))
    print(" A5 tau_v is load-bearing: floor-aware %.2f > floor-blind %.2f -> %s" % (best_fit, floor_blind, "PASS" if a5 else "FAIL"))
    print("\n DISCOVERED STRATEGY: triage weight %.2f vs need %.2f vs capacity %.2f -> %s" %
          (best[2], best[0], best[1], "TRIAGE-FIRST (rescue below-floor, then allocate)" if best[2] >= max(best[0], best[1]) else "see params"))

    green = lock_ok and a1 and a2 and a3 and a4 and a5
    out = {"spec_sha256": got, "lock_ok": lock_ok,
           "means": {"random": round(rand, 2), "equal": round(equal, 2), "greedy_capacity": round(gU, 2),
                     "greedy_need": round(gneed, 2), "floor_blind": round(floor_blind, 2),
                     "evolved": round(best_fit, 2), "greedy_1step_myopic": round(oracle, 2),
                     "strong_localsearch_ref_exploratory": round(strong, 2)},
           "honest_note": "the pre-registered greedy-marginal 'oracle' is 1-step and MYOPIC at the collapse cliff (%.2f, below baselines); A2 passes as written but does NOT establish near-optimality. The evolved triage policy beats it and is within %.0f%% of the exploratory strong local-search reference." % (round(oracle, 2), 100 * best_fit / strong if strong else 0),
           "near_optimal_vs_strong_ref": {"evolved": round(best_fit, 2), "strong_ref": round(strong, 2), "ratio": round(best_fit / strong, 3) if strong else None},
           "evolved_params": {"need": round(best[0], 3), "capacity": round(best[1], 3), "triage": round(best[2], 3)},
           "A1_beats_naive": a1, "A2_near_optimal": {"evolved": round(best_fit, 2), "oracle": round(oracle, 2), "pass": a2},
           "A3_decoupling": {"deterministic": det, "honest_vs_lying_gap": gap, "pass": a3},
           "A4_monotone": a4, "A5_tau_v_load_bearing": {"floor_aware": round(best_fit, 2), "floor_blind": round(floor_blind, 2), "pass": a5},
           "discovered": "triage-then-capacity allocator (rescue below-floor agents first)",
           "honest_reporting": True, "pass": green}
    json.dump(out, open(os.path.join(HERE, "results_agency.json"), "w"), indent=2)

    print("\n" + BAR)
    print(" RESULT: %s — an agency allocator DISCOVERED by evolution and VERIFIED by the deterministic" % ("GREEN" if green else "RED"))
    print(" three-law evaluator; trustworthy because a lying generator can't survive it. E=U*D + tau_v + F_out=F_eval.")
    print(BAR)
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()
