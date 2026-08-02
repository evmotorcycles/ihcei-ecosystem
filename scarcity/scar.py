"""
scar.py -- Graph-Topological Decode Scarcity, run against its pre-registration.

Spec 135355477e57ae681805b289f1234e003954a00d36146cd2f19ab31df137e095, locked after a
pre-flight whose power probe was run on PERMUTED labels so that precision was measured
without the direction of the effect being seen.

Tests LISM's OWN declared domain limit (manuscript section 3.3c): that the product form
E = U*D_enc*D_dec assumes the decode hop is scarce. Real 2016Q1/Q2 interbank data.
Nothing simulated.
"""
import csv
import hashlib
import json
import os
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "135355477e57ae681805b289f1234e003954a00d36146cd2f19ab31df137e095"

SPEC = json.load(open(os.path.join(HERE, "prereg", "scarcity_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

WITHDRAWAL_FRACTION = 0.5
K2_MIN_N, K2_MIN_EVENTS = 100, 15
K3_MIN_DISTINCT, K3_MAX_SHARE = 10, 0.95
K4_MARGIN, K5_MAX_WIDTH = 0.05, 0.20
N_BOOT, SEED = 2000, 20260802
TOO_PERFECT = 0.30

D = os.path.join(ROOT, "data", "interbank-2016")


def num(row, key):
    try:
        return float(row[key])
    except (TypeError, ValueError, KeyError):
        return None


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    g = 0.0
    for a in pos:
        for b in neg:
            g += 1.0 if a > b else (0.5 if a == b else 0.0)
    return g / (len(pos) * len(neg))


def load():
    nodes = {r["index"]: r for r in csv.DictReader(open(os.path.join(D, "nodes_2016Q1.csv")))}
    e1 = [(r["Sourceid"], r["Targetid"], float(r["Weights"]))
          for r in csv.DictReader(open(os.path.join(D, "edges_2016Q1.csv")))]
    e2 = [(r["Sourceid"], r["Targetid"], float(r["Weights"]))
          for r in csv.DictReader(open(os.path.join(D, "edges_2016Q2.csv")))]
    ins1, ins2 = defaultdict(float), defaultdict(float)
    indeg, outdeg = defaultdict(int), defaultdict(int)
    nb = defaultdict(set)
    for s, t, w in e1:
        ins1[t] += w
        indeg[t] += 1
        outdeg[s] += 1
        if s != t:
            nb[s].add(t)
            nb[t].add(s)
    for s, t, w in e2:
        ins2[t] += w
    elig = sorted(i for i in nodes
                  if ins1.get(i, 0.0) > 0 and (num(nodes[i], "Equity") or 0.0) > 0)
    lab = {i: ins2.get(i, 0.0) <= WITHDRAWAL_FRACTION * ins1[i] for i in elig}
    # local bridge fraction: no fitted parameter anywhere in this expression
    B = {v: (sum(1 for u in nb[v] if not (nb[v] & nb[u])) / len(nb[v]) if nb[v] else 0.0)
         for v in elig}
    L, Q = {}, {}
    for i in elig:
        u = (num(nodes[i], "Interbank_liabilities") or 0.0) / num(nodes[i], "Equity")
        de, dd = indeg.get(i, 0), outdeg.get(i, 0)
        L[i] = u * de * dd                 # verbatim from interbank-2016/network.py
        Q[i] = u * (de + dd) ** 2          # verbatim from interbank-2016/network.py
    return elig, lab, B, L, Q, len(e1), len(e2)


def diff_in_advantage(idx, lab, B, L, Q):
    hi = [i for i in idx if B[i] == 1.0]
    lo = [i for i in idx if B[i] < 1.0]
    ah, qh = auc([L[i] for i in hi], [lab[i] for i in hi]), auc([Q[i] for i in hi], [lab[i] for i in hi])
    al, ql = auc([L[i] for i in lo], [lab[i] for i in lo]), auc([Q[i] for i in lo], [lab[i] for i in lo])
    if None in (ah, qh, al, ql):
        return None, (ah, qh, al, ql)
    return (ah - qh) - (al - ql), (ah, qh, al, ql)


def bootstrap_ci(elig, lab, B, L, Q, seed):
    rng = random.Random(seed)
    vals = []
    for _ in range(N_BOOT):
        s = [rng.choice(elig) for _ in elig]
        d, _a = diff_in_advantage(s, lab, B, L, Q)
        if d is not None:
            vals.append(d)
    vals.sort()
    return vals[int(0.05 * len(vals))], vals[int(0.95 * len(vals))], len(vals)


def main():
    elig, lab, B, L, Q, n_e1, n_e2 = load()
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    hi = [i for i in elig if B[i] == 1.0]
    lo = [i for i in elig if B[i] < 1.0]
    ev_hi, ev_lo = sum(lab[i] for i in hi), sum(lab[i] for i in lo)
    n_events = sum(lab.values())

    # ---- K1 -----------------------------------------------------------------
    gate("K1_integrity",
         len(elig) == 1349 and n_events == 291 and all(i in B for i in elig),
         "%d eligible nodes and %d withdrawal events, reproducing spec db8c3a4f exactly. "
         "Q1 edges %d, Q2 edges %d. B(v) computed for all %d eligible nodes."
         % (len(elig), n_events, n_e1, n_e2, len(B)))

    # ---- K2 both strata populated -------------------------------------------
    gate("K2_BOTH_STRATA_ARE_POPULATED",
         len(hi) >= K2_MIN_N and len(lo) >= K2_MIN_N
         and ev_hi >= K2_MIN_EVENTS and ev_lo >= K2_MIN_EVENTS,
         "HIGH (B==1.0): n=%d events=%d. LOW (B<1.0): n=%d events=%d. Each needs n>=%d "
         "and events>=%d." % (len(hi), ev_hi, len(lo), ev_lo, K2_MIN_N, K2_MIN_EVENTS))

    # ---- K3 the metric is not degenerate ------------------------------------
    distinct = len(set(round(v, 9) for v in B.values()))
    share = max(len(hi), len(lo)) / len(elig)
    gate("K3_THE_METRIC_IS_NOT_DEGENERATE",
         distinct >= K3_MIN_DISTINCT and share <= K3_MAX_SHARE,
         "B(v) takes %d distinct values (needs >= %d) and the larger stratum holds %.1f%% "
         "of nodes (needs <= %.0f%%)." % (distinct, K3_MIN_DISTINCT, 100 * share,
                                          100 * K3_MAX_SHARE))

    # ---- K4 primary ---------------------------------------------------------
    d, (ah, qh, al, ql) = diff_in_advantage(elig, lab, B, L, Q)
    k4 = d is not None and d >= K4_MARGIN
    gate("K4_PRIMARY_THE_PRODUCT_FORM_S_ADVANTAGE_IS_LARGER_WHERE_DECODE_IS_SCARCE", k4,
         "HIGH stratum: product %.4f vs quadratic %.4f, advantage %+.4f. LOW stratum: "
         "product %.4f vs quadratic %.4f, advantage %+.4f. Difference-in-advantage = "
         "%+.4f (needs >= %+.2f)." % (ah, qh, ah - qh, al, ql, al - ql, d, K4_MARGIN))

    # ---- K5 precision, with a binding consequence ---------------------------
    clo, chi, nb_ok = bootstrap_ci(elig, lab, B, L, Q, SEED)
    width = chi - clo
    k5 = width <= K5_MAX_WIDTH
    gate("K5_THE_ESTIMATE_IS_PRECISE_ENOUGH_TO_MEAN_ANYTHING", k5,
         "90%% bootstrap CI on the difference-in-advantage = [%+.4f, %+.4f], width %.4f "
         "(needs <= %.2f), from %d successful resamples of %d."
         % (clo, chi, width, K5_MAX_WIDTH, nb_ok, N_BOOT))

    # ---- K6 permutation control ---------------------------------------------
    rng = random.Random(SEED + 1)
    perm = list(lab.values())
    rng.shuffle(perm)
    plab = dict(zip(elig, perm))
    plo, phi, _ = bootstrap_ci(elig, plab, B, L, Q, SEED + 2)
    k6 = plo <= 0.0 <= phi
    gate("K6_THE_PERMUTATION_CONTROL_IS_NULL", k6,
         "with labels permuted the 90%% CI is [%+.4f, %+.4f] and must contain 0. If a "
         "scarcity effect survives shuffling, it belongs to the strata rather than to the "
         "outcome." % (plo, phi))

    gates.append({"id": "K7_does_the_scope_rule_hold_ACROSS_substrates", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. Of the five SDL substrates, yeast and GitHub "
                            "commit no graph, the quantum arm is a derivation with no data, "
                            "and PyPI's declared outcome (E_indegree) is derived from the "
                            "SAME graph the scarcity metric would be computed on, which is "
                            "circular. One substrate cannot establish a cross-substrate rule."})
    gates.append({"id": "K8_DCM_self_audit", "met": None, "weight": "excluded",
                  "detail": "EXCLUDED. The analysed outcome is a continuous AUC difference, "
                            "and DELTA = V*I*C cannot fail on a continuous unbanded outcome. "
                            "A gate that cannot fail is not evidence, so it scores nothing."})

    suspect = []
    if d is not None and abs(d) > TOO_PERFECT:
        suspect.append("difference_in_advantage_above_0.30")
    if not k6:
        suspect.append("permutation_control_is_NOT_null")

    binding = ("K5 WAS MET, so K4 is interpretable at the stated precision."
               if k5 else
               "K5 WAS NOT MET, SO K4 IS UNINFORMATIVE whichever way it came out. An "
               "imprecise point estimate is not a finding.")

    disclosures = {
        "D1_THE_BINDING_CONSEQUENCE": {"statement": binding, "CI90": [round(clo, 4), round(chi, 4)],
                                       "width": round(width, 4)},
        "D2_THE_GAP_AS_POSED_WAS_NOT_CLOSED": {
            "asked_for": "a graph-topological scarcity metric across the five SDL substrates",
            "delivered": "one substrate",
            "yeast": "BLOCKED - interactome edges were never committed, only node-level rows",
            "github": "BLOCKED - a per-repository table, no graph exists in the repository",
            "quantum": "NOT APPLICABLE - a closed-form derivation, no dataset",
            "pypi": "UNTESTABLE-HERE - CIRCULAR. Its declared outcome E_indegree is derived "
                    "from the same graph the metric would be computed on.",
            "interbank": "the one clean test - metric from Q1 topology, outcome realised in Q2",
            "note": "A single substrate cannot establish a cross-substrate scope rule, which "
                    "is what SDL's DELTA was for. The SDL scope rule remains untested across "
                    "substrates. Reporting this run as though it closed a five-substrate gap "
                    "would be the error the spec was written to prevent.",
        },
        "D3_the_metric_has_no_free_parameter": {
            "definition": "B(v) = fraction of v's neighbours u such that N(v) and N(u) share "
                          "no common member.",
            "note": "No threshold chosen, no weight fitted, no distribution assumed. The "
                    "HIGH/LOW split is at B == 1.0, the natural boundary of the metric rather "
                    "than a cut chosen from the outcome.",
            "distinct_values": distinct,
        },
        "D4_the_rival_was_copied_not_rewritten": {
            "product": "u * de * dd", "quadratic": "u * (de + dd) ** 2",
            "note": "Both taken verbatim from interbank-2016/network.py so this run cannot "
                    "advantage either form by re-specifying it. On the FULL eligible set the "
                    "earlier run found them effectively tied at 0.6090 against 0.6109, with "
                    "the rival marginally ahead.",
        },
        "D5_what_a_result_here_does_not_license": {
            "note": "One substrate, one quarter, one country's interbank network. Nothing "
                    "here is evidence that the domain limit holds on yeast, GitHub, PyPI or "
                    "in the quantum derivation, and K7 records that.",
        },
        "D6_if_the_primary_failed": {
            "note": "A miss means LISM's own declared domain limit does not hold where it is "
                    "testable, and manuscript section 3.3c is an unsupported assertion rather "
                    "than a demonstrated boundary. That is a null against our own manuscript "
                    "and 3.3c is to be amended to say so.",
        },
        "D7_the_power_probe_saw_precision_but_not_direction": {
            "note": "The pre-flight bootstrap was run on PERMUTED labels, giving a CI width "
                    "of 0.0798 without revealing which way the real effect fell. The real "
                    "labels were not used before the lock.",
            "and_the_caveat_it_does_not_remove": "The HIGH stratum holds 131 nodes and 20 "
                    "events. The PAIRED difference is precise because both forms are scored "
                    "on identical labels; any SINGLE AUC in that stratum is not, and no "
                    "single-AUC claim about it is made.",
        },
    }

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "Graph-Topological Decode Scarcity",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet,
        "simulated_values": 0,
        "substrates_tested": 1, "substrates_in_SDL": 5,
        "strata": {"HIGH_B_equals_1": {"n": len(hi), "events": ev_hi},
                   "LOW_B_below_1": {"n": len(lo), "events": ev_lo}},
        "auc": {"HIGH_product": round(ah, 4), "HIGH_quadratic": round(qh, 4),
                "LOW_product": round(al, 4), "LOW_quadratic": round(ql, 4),
                "HIGH_advantage": round(ah - qh, 4), "LOW_advantage": round(al - ql, 4),
                "difference_in_advantage": round(d, 4)},
        "bootstrap": {"CI90": [round(clo, 4), round(chi, 4)], "width": round(width, 4),
                      "n_boot": N_BOOT},
        "permutation_control": {"CI90": [round(plo, 4), round(phi, 4)],
                                "contains_zero": bool(k6)},
        "too_perfect_flag": suspect,
        "post_run_disclosures": disclosures,
        "primary_verdict": None,
    }
    res["primary_verdict"] = (
        ("THE DOMAIN LIMIT HELD ON THIS SUBSTRATE: the product form's advantage is %+.4f "
         "larger among nodes whose decode hop has no two-step substitute." % d) if k4 else
        ("THE DOMAIN LIMIT DID NOT HOLD ON THIS SUBSTRATE: difference-in-advantage %+.4f "
         "against a required %+.2f. Manuscript section 3.3c is an unsupported assertion "
         "where it is testable." % (d, K4_MARGIN))) + " " + binding + \
        " ONE SUBSTRATE OF FIVE; the SDL scope rule remains untested across substrates."
    with open(os.path.join(HERE, "results_scar.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "strata", "auc", "bootstrap",
                       "permutation_control", "too_perfect_flag", "primary_verdict")},
                     indent=2))


if __name__ == "__main__":
    main()
