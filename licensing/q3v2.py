"""
q3v2.py -- the Q3 arm re-run with a CORRECTED permutation control.

Spec d7184ef95c804eb896488099412fe11406c03d7890abc652968e27310c263efd, which supersedes the
Q3 arm of cd429dfa only. Q4 and Q5 are not re-run and their v1 results stand as reported.

v1's Q3_D failed because the runner bootstrapped ONE fixed permutation instead of drawing
many. That estimates the spread around whatever that single permutation landed on, not the
permutation null. The defect is mine; v1's 3/4 is published unchanged and is NOT re-scored.
Not one threshold moves here -- only the definition of the control.
"""
import csv
import hashlib
import json
import os
import random
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "d7184ef95c804eb896488099412fe11406c03d7890abc652968e27310c263efd"

SPEC = json.load(open(os.path.join(HERE, "prereg", "licensing_v2_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

MIN_N, MIN_EV, MARGIN, N_BOOT, N_PERM, SEED = 50, 10, 0.10, 2000, 2000, 20260803


def load():
    D = os.path.join(ROOT, "data", "interbank-2016")

    def num(row, key):
        try:
            return float(row[key])
        except (TypeError, ValueError, KeyError):
            return None
    nodes = {r["index"]: r for r in csv.DictReader(open(os.path.join(D, "nodes_2016Q1.csv")))}
    e1 = [(r["Sourceid"], r["Targetid"], float(r["Weights"]))
          for r in csv.DictReader(open(os.path.join(D, "edges_2016Q1.csv")))]
    e2 = [(r["Sourceid"], r["Targetid"], float(r["Weights"]))
          for r in csv.DictReader(open(os.path.join(D, "edges_2016Q2.csv")))]
    ins1, ins2, deg = defaultdict(float), defaultdict(float), defaultdict(int)
    for s, t, w in e1:
        ins1[t] += w
        deg[t] += 1
        deg[s] += 1
    for s, t, w in e2:
        ins2[t] += w
    elig = sorted(i for i in nodes
                  if ins1.get(i, 0.0) > 0 and (num(nodes[i], "Equity") or 0.0) > 0)
    lab = {i: ins2.get(i, 0.0) <= 0.5 * ins1[i] for i in elig}
    U = {i: (num(nodes[i], "Interbank_liabilities") or 0.0) / num(nodes[i], "Equity")
         for i in elig}
    qd = statistics.quantiles([deg[i] for i in elig], n=4)[2]
    qu = statistics.quantiles([U[i] for i in elig], n=4)[2]
    systemic = {i for i in elig if deg[i] >= qd and U[i] >= qu}
    return elig, lab, systemic, qd, qu


def main():
    elig, lab, systemic, qd, qu = load()
    sysl = [i for i in elig if i in systemic]
    rout = [i for i in elig if i not in systemic]
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    def diff(l, s=None, r=None):
        s, r = s or sysl, r or rout
        return sum(l[i] for i in s) / len(s) - sum(l[i] for i in r) / len(r)

    ev_s, ev_r = sum(lab[i] for i in sysl), sum(lab[i] for i in rout)
    gate("Q3v2_A_BOTH_CLASSES_ARE_POPULATED",
         len(sysl) >= MIN_N and len(rout) >= MIN_N and ev_s >= MIN_EV and ev_r >= MIN_EV,
         "SYSTEMIC n=%d events=%d; ROUTINE n=%d events=%d. Thresholds: degree >= %.0f and "
         "U >= %.4f." % (len(sysl), ev_s, len(rout), ev_r, qd, qu))

    obs = diff(lab)
    gate("Q3v2_B_PRIMARY_THE_CLASSES_DIFFER_IN_REALISED_RISK", obs >= MARGIN,
         "withdrawal rate SYSTEMIC %.4f minus ROUTINE %.4f = %+.4f (needs >= %+.2f)"
         % (ev_s / len(sysl), ev_r / len(rout), obs, MARGIN))

    rng = random.Random(SEED)
    bs = []
    for _ in range(N_BOOT):
        samp = [rng.choice(elig) for _ in elig]
        s = [i for i in samp if i in systemic]
        r = [i for i in samp if i not in systemic]
        if s and r:
            bs.append(diff(lab, s, r))
    bs.sort()
    blo, bhi = bs[int(0.05 * len(bs))], bs[int(0.95 * len(bs))]
    gate("Q3v2_C_THE_DIFFERENCE_IS_PRECISE_ENOUGH", not (blo <= 0.0 <= bhi),
         "90%% bootstrap CI = [%+.4f, %+.4f] and must EXCLUDE 0" % (blo, bhi))

    # THE CORRECTION: 2000 INDEPENDENT permutations, not one bootstrapped.
    prng = random.Random(SEED + 11)
    null = []
    for _ in range(N_PERM):
        pv = list(lab.values())
        prng.shuffle(pv)
        null.append(diff(dict(zip(elig, pv))))
    null.sort()
    nlo, nhi = null[int(0.05 * N_PERM)], null[int(0.95 * N_PERM)]
    contains0 = nlo <= 0.0 <= nhi
    outside = not (nlo <= obs <= nhi)
    p_one = sum(1 for v in null if v >= obs) / len(null)
    gate("Q3v2_D_THE_CORRECTED_PERMUTATION_NULL", contains0 and outside,
         "over %d INDEPENDENT permutations the null band is [%+.4f, %+.4f] (mean %+.5f). "
         "Contains 0: %s. Observed %+.4f falls outside it: %s. One-sided p = %.4f."
         % (N_PERM, nlo, nhi, statistics.fmean(null), contains0, obs, outside, p_one))

    gates.append({"id": "Q3v2_E_does_the_fixed_policy_ASSIGNMENT_improve_outcomes",
                  "met": None, "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. An intervention. Historical data cannot answer "
                            "it, and the only alternative substrate is the three-proposals "
                            "simulator we wrote ourselves, which is not evidence."})

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "Licensing Q3 - v2, corrected permutation control",
        "spec_sha256": LOCKED,
        "supersedes_the_Q3_arm_of": SPEC["supersedes"],
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet, "simulated_values": 0,
        "systemic": {"n": len(sysl), "events": ev_s, "rate": round(ev_s / len(sysl), 4)},
        "routine": {"n": len(rout), "events": ev_r, "rate": round(ev_r / len(rout), 4)},
        "rate_difference": round(obs, 4),
        "bootstrap_CI90": [round(blo, 4), round(bhi, 4)],
        "permutation_null": {"n": N_PERM, "mean": round(statistics.fmean(null), 5),
                             "band90": [round(nlo, 4), round(nhi, 4)],
                             "contains_zero": contains0,
                             "observed_outside_band": outside,
                             "one_sided_p": round(p_one, 4)},
        "post_run_disclosures": {
            "D1_v1_is_not_re_scored": {
                "note": "v1's Q3 arm stands at 3/4 with Q3_D FAILED and is published "
                        "unchanged. A defective control is corrected in a new specification, "
                        "never re-scored in place after the fact.",
            },
            "D2_only_the_control_definition_changed": {
                "note": "The classification rule, eligibility, outcome definition, the +0.10 "
                        "margin and the bootstrap-CI requirement are all carried over "
                        "unchanged. Not one threshold moved.",
            },
            "D3_what_this_does_not_license": {
                "note": "That the systemic and routine classes differ in realised risk is "
                        "NOT evidence that assigning different instruments to them helps "
                        "anyone. That is an intervention on one real network in one quarter, "
                        "and Q3v2_E records that it stays untestable here.",
            },
        },
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        "THE CLASSIFICATION SEPARATES REALISED RISK: %.4f against %.4f, a difference of "
        "%+.4f, with a permutation null centred on %+.5f and one-sided p = %.4f. It does NOT "
        "follow that the fixed-endpoint policy built on that classification improves anything."
        % (ev_s / len(sysl), ev_r / len(rout), obs, statistics.fmean(null), p_one)
        if not notmet else
        "Q3 v2 did not clear every gate: %s" % notmet)
    with open(os.path.join(HERE, "results_q3v2.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in ("score", "gates_not_met", "systemic", "routine",
                                          "rate_difference", "bootstrap_CI90",
                                          "permutation_null", "primary_verdict")}, indent=2))


if __name__ == "__main__":
    main()
