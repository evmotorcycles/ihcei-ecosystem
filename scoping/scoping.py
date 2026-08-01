"""
scoping.py -- SDL, the Scope Declaration Law, run against its pre-registration.

Spec c025eb5170456d197c23259180b105e458720f0740ebc1d2f00eb38e134e646a, locked before any
substrate's winner was computed.

    R = modal share of the decode variable
    R > 0.5  -> predict the SINGLE-HOP form  U * D_enc
    R <= 0.5 -> predict the TWO-HOP form     U * D_enc * D_dec

R reads the decode column and nothing else. It never touches the outcome, U, D_enc, or
which form wins.
"""
import csv
import hashlib
import json
import math
import os
import statistics
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "c025eb5170456d197c23259180b105e458720f0740ebc1d2f00eb38e134e646a"

SPEC = json.load(open(os.path.join(HERE, "prereg", "scoping_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

SUB = SPEC["substrates"]
R_THRESHOLD = 0.5
TIE_BAND = 0.005
S3_MIN, S5_BEAT, S6_MIN = 4, 0.80, 0.20


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check(rel, want):
    got = sha256(os.path.join(ROOT, rel))
    if got != want:
        raise SystemExit("DATA CHANGED: %s %s != %s" % (rel, got, want))


# ------------------------------------------------------- the scope selector
def R_decode_redundancy(d_dec_values):
    """Modal share of the decode variable. Reads the decode column and nothing else."""
    c = Counter(round(v, 9) for v in d_dec_values)
    return c.most_common(1)[0][1] / len(d_dec_values)


# ------------------------------------------------------------- the harness
def auc(scores, labels):
    pairs = sorted(zip(scores, labels))
    ranks, i = [0.0] * len(pairs), 0
    while i < len(pairs):
        j = i
        while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        mr = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = mr
        i = j + 1
    npos = sum(1 for _, y in pairs if y)
    nneg = len(pairs) - npos
    if npos == 0 or nneg == 0:
        return None
    rsum = sum(r for r, (_, y) in zip(ranks, pairs) if y)
    return (rsum - npos * (npos + 1) / 2.0) / (npos * nneg)


def winner_binary(rows):
    """Which form better predicts this substrate's own outcome."""
    y = [r["E"] for r in rows]
    a_single = auc([r["U"] * r["D_enc"] for r in rows], y)
    a_two = auc([r["U"] * r["D_enc"] * r["D_dec"] for r in rows], y)
    if abs(a_single - a_two) < TIE_BAND:
        w = "TIED"
    else:
        w = "single_hop" if a_single > a_two else "two_hop"
    return w, {"auc_single_hop": round(a_single, 4), "auc_two_hop": round(a_two, 4)}


def num(s):
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(v) else v


def load_yeast():
    s = SUB["S_yeast"]
    check(s["file"], s["sha256"])
    rows = []
    for r in csv.DictReader(open(os.path.join(ROOT, s["file"]))):
        u, de, dd, e = (num(r["U"]), num(r["D_enc"]), num(r["D_dec"]),
                        num(r["E_essential"]))
        if None in (u, de, dd, e):
            continue
        rows.append({"U": u, "D_enc": de, "D_dec": dd, "E": int(e)})
    return rows


def load_github():
    s = SUB["S_github"]
    check(s["file"], s["sha256"])
    rows = []
    for r in csv.DictReader(open(os.path.join(ROOT, s["file"]))):
        rows.append({"U": float(r["U"]), "D_enc": float(r["D_enc"]),
                     "D_dec": float(r["D_dec"]), "E": int(r["E"])})
    return rows


def load_pypi():
    s = SUB["S_pypi"]
    check(s["file"], s["sha256"])
    raw = list(csv.DictReader(open(os.path.join(ROOT, s["file"]))))
    med = statistics.median(float(r["E_indegree"]) for r in raw)
    return [{"U": float(r["U_versions"]), "D_enc": float(r["D_enc_release_hygiene"]),
             "D_dec": float(r["D_dec_pin_clarity"]),
             "E": int(float(r["E_indegree"]) > med)} for r in raw]


def load_interbank():
    s = SUB["S_interbank"]
    check(s["files"][0], s["sha256_nodes"])
    check(s["files"][1], s["sha256_edges"])
    nodes = {int(r["index"]): r for r in
             csv.DictReader(open(os.path.join(ROOT, s["files"][0])))}
    e1 = [(int(r["Sourceid"]), int(r["Targetid"]), float(r["Weights"])) for r in
          csv.DictReader(open(os.path.join(ROOT, s["files"][1])))]
    e2 = [(int(r["Sourceid"]), int(r["Targetid"]), float(r["Weights"])) for r in
          csv.DictReader(open(os.path.join(ROOT, "data/interbank-2016/edges_2016Q2.csv")))]
    ins1, ins2, indeg, outdeg = {}, {}, {}, {}
    for a, b, w in e1:
        ins1[b] = ins1.get(b, 0.0) + w
        indeg[b] = indeg.get(b, 0) + 1
        outdeg[a] = outdeg.get(a, 0) + 1
    for a, b, w in e2:
        ins2[b] = ins2.get(b, 0.0) + w
    rows = []
    for i, r in nodes.items():
        eq = num(r["Equity"])
        if ins1.get(i, 0.0) <= 0 or eq is None or eq <= 0:
            continue
        rows.append({"U": (num(r["Interbank_liabilities"]) or 0.0) / eq,
                     "D_enc": float(indeg.get(i, 0)), "D_dec": float(outdeg.get(i, 0)),
                     "E": int(ins2.get(i, 0.0) <= 0.5 * ins1[i])})
    return rows


def quantum_substrate():
    """Winner ALREADY KNOWN from spec 6cb42dcd: single-hop, by 195x. Flagged, not excluded."""
    gamma, N = 0.1, 20
    return {"name": "quantum", "n": 95, "R": 1.0 - gamma,
            "winner": "single_hop",
            "detail": {"median_abs_error_single_hop": 0.0028,
                       "median_abs_error_two_hop": 0.5495,
                       "source_spec": "6cb42dcd"},
            "independent": False,
            "R_note": "each of the %d environment qubits plays an identical decoding role "
                      "with per-qubit overlap %.1f, so the decode channel repeats itself "
                      "almost completely" % (N, gamma)}


def main():
    substrates = []
    for name, loader in (("yeast", load_yeast), ("github", load_github),
                         ("pypi", load_pypi), ("interbank", load_interbank)):
        rows = loader()
        w, detail = winner_binary(rows)
        substrates.append({"name": name, "n": len(rows),
                           "R": R_decode_redundancy([r["D_dec"] for r in rows]),
                           "winner": w, "detail": detail, "independent": True})
    substrates.append(quantum_substrate())

    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    # ---- S1 integrity -------------------------------------------------------
    shapes = {s["name"]: s["n"] for s in substrates}
    ranges_ok = all(0.0 <= s["R"] <= 1.0 for s in substrates)
    s1 = (shapes["yeast"] == SUB["S_yeast"]["rows_declared"]
          and shapes["github"] == SUB["S_github"]["rows_declared"]
          and shapes["pypi"] == SUB["S_pypi"]["rows_declared"]
          and ranges_ok and len(substrates) == 5)
    gate("S1_integrity", s1, "rows %s, all R in [0,1]=%s, %d substrates"
         % (shapes, ranges_ok, len(substrates)))

    # ---- S2 not unanimous ---------------------------------------------------
    winners = [s["winner"] for s in substrates]
    unanimous = len(set(winners)) == 1
    gate("S2_the_substrates_do_not_all_agree", not unanimous,
         "winners: %s" % {s["name"]: s["winner"] for s in substrates})

    # ---- the locked rule ----------------------------------------------------
    def predict(R, t=R_THRESHOLD):
        return "single_hop" if R > t else "two_hop"

    for s in substrates:
        s["predicted"] = predict(s["R"])
        s["correct"] = s["predicted"] == s["winner"]
    n_correct = sum(s["correct"] for s in substrates)
    n_correct_independent = sum(s["correct"] for s in substrates if s["independent"])

    gate("S3_THE_PRE_DECLARED_RULE_ASSIGNS_THE_WINNER", n_correct >= S3_MIN,
         "correct in %d of %d (needs >= %d); %d of 4 among the INDEPENDENT substrates. %s"
         % (n_correct, len(substrates), S3_MIN, n_correct_independent,
            {s["name"]: "R=%.3f pred=%s actual=%s %s"
             % (s["R"], s["predicted"], s["winner"], "OK" if s["correct"] else "WRONG")
             for s in substrates}))

    # ---- S4 ablation against always-one-form -------------------------------
    base = {f: sum(1 for s in substrates if s["winner"] == f) for f in
            ("single_hop", "two_hop")}
    best_base = max(base.values())
    gate("S4_SCOPING_BEATS_THE_BEST_SINGLE_GLOBAL_FORM", n_correct > best_base,
         "scoping %d correct vs always-single-hop %d, always-two-hop %d (needs strictly "
         "greater than %d)" % (n_correct, base["single_hop"], base["two_hop"], best_base))

    # ---- S5 falsifiability of the threshold --------------------------------
    sweep = []
    for i in range(101):
        t = i / 100.0
        sweep.append((t, sum(1 for s in substrates if predict(s["R"], t) == s["winner"])))
    worse = sum(1 for t, c in sweep if c < n_correct)
    frac_beaten = worse / len(sweep)
    distinct = sorted(set(c for _, c in sweep))
    gate("S5_THE_LOCKED_THRESHOLD_IS_DOING_WORK", frac_beaten >= S5_BEAT,
         "the locked threshold 0.5 scores %d; it beats %.1f%% of the 101 alternative "
         "thresholds (needs >= %.0f%%). Distinct scores reachable by ANY threshold: %s"
         % (n_correct, 100 * frac_beaten, 100 * S5_BEAT, distinct))

    # ---- S6 DCM turned on this experiment ----------------------------------
    ys = [s["winner"] for s in substrates]
    labels = [1 if s["R"] > R_THRESHOLD else 0 for s in substrates]
    V = 1.0 - Counter(ys).most_common(1)[0][1] / len(ys)
    p = min(sum(labels), len(labels) - sum(labels)) / len(labels)
    I = 4.0 * p * (1.0 - p)
    C = min(1.0, len(set(ys)) / len(ys))
    DELTA = V * I * C
    s6 = DELTA >= S6_MIN
    gate("S6_DCM_SELF_AUDIT_OF_THIS_VERY_EXPERIMENT", s6,
         "DELTA = V %.4f * I %.4f * C %.4f = %.4f (needs >= %.2f) on n=%d substrates"
         % (V, I, C, DELTA, S6_MIN, len(substrates)))

    gates.append({"id": "S7_whether_domain_scoping_is_correct_in_general", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. Five substrates, four from this programme's "
                            "own collection, cannot settle whether a scoped family of "
                            "equations is the right architecture for science."})

    # ---- POST-RUN DISCLOSURES ----------------------------------------------
    binding = ("S6 WAS NOT MET, SO S3, S4 AND S5 ARE UNINFORMATIVE. The spec bound this in "
               "advance: DELTA = %.4f against a locked floor of 0.20 on five substrates. "
               "Whatever verdicts S3, S4 and S5 carry, NO CLAIM MAY BE MADE FOR OR AGAINST "
               "the scoping architecture on the strength of them." % DELTA) if not s6 else (
        "S6 was met at DELTA = %.4f, so S3, S4 and S5 are reportable on their own terms."
        % DELTA)

    disclosures = {
        "D1_THE_BINDING_CONSEQUENCE": {"delta": round(DELTA, 4), "floor": S6_MIN,
                                       "statement": binding},
        "D2_what_this_run_actually_establishes": {
            "does": "That the scope condition CAN be written down in advance and computed "
                    "from substrate structure alone. That is not nothing -- it is the "
                    "difference between an architecture that could be tested and one that "
                    "could not.",
            "does_not": "That the scope condition is CORRECT. Five substrates cannot "
                        "calibrate a threshold, and the falsifiability sweep shows how "
                        "few distinct answers a single threshold can even produce here.",
            "the_hole_is_still_open": "A family of equations plus a per-domain choice of "
                    "which applies remains unfalsifiable UNTIL the scope selector is tested "
                    "on substrates collected by people who were not testing it. This run "
                    "does not clear that bar and does not claim to.",
        },
        "D3_the_quantum_substrate_is_not_independent": {
            "note": "Its winner was known before the spec was written -- the single-hop "
                    "form by 195x, from spec 6cb42dcd. It is SCORED because dropping the "
                    "case that motivated the scope condition would flatter the rule, and "
                    "FLAGGED because counting it as confirmation would be circular.",
            "correct_among_independent_substrates_only": n_correct_independent,
            "independent_substrates": 4,
        },
        "D4_R_is_a_proxy_and_the_absence_it_exposes": {
            "note": "Redundancy in the quantum sense means many carriers EACH SUFFICIENT. "
                    "Modal share means many carriers holding the SAME VALUE. No single "
                    "first-principles redundancy measure exists across interactomes, "
                    "repositories, package graphs and environment qubits.",
            "why_that_matters_for_the_architecture": "If the scope selector must itself be "
                    "redefined per domain, the domain-scoping design has MOVED the "
                    "unfalsifiability rather than removed it. That is the sharpest open "
                    "question this run leaves behind.",
        },
        "D6_THE_INTERBANK_CASE_CONTRADICTS_THE_REDUNDANCY_STORY_DIRECTLY": {
            "R": round([s for s in substrates if s["name"] == "interbank"][0]["R"], 4),
            "predicted": "single_hop", "actual": "two_hop",
            "note": "The interbank network has the second-highest decode redundancy of the "
                    "five, so the rule predicted the single-hop form. The two-hop form won. "
                    "This is the sharpest single counter-case: high modal share in the "
                    "decode variable did NOT make the second hop redundant. Whatever makes "
                    "the decode hop scarce or not, modal share is not measuring it.",
        },
        "D7_THE_RULE_SCORED_1_OF_4_ON_INDEPENDENT_SUBSTRATES": {
            "correct_all_five": n_correct,
            "correct_independent_only": n_correct_independent,
            "of_independent": 4,
            "always_single_hop_baseline": base["single_hop"],
            "both_readings_stated": "Taken at face value the rule is worse than chance on "
                    "the substrates that could test it, and worse than always using the "
                    "single-hop form on all five. BUT THE BINDING RULE FORBIDS TAKING IT AT "
                    "FACE VALUE: S6 was pre-declared as the gate that decides whether S3 to "
                    "S5 mean anything, and it was not met. The honest status of this rule is "
                    "UNTESTED, not REFUTED.",
        },
        "D8_THE_FALSIFIABILITY_SWEEP_IS_THE_REAL_FINDING": {
            "distinct_scores_reachable_by_any_threshold": distinct,
            "locked_threshold_score": n_correct,
            "best_reachable_score": max(distinct),
            "note": "Across 101 candidate thresholds on R, only TWO distinct scores are "
                    "reachable at all: %s. A single threshold on a single number cannot "
                    "express more than a handful of partitions of five substrates, so the "
                    "sweep is not measuring how good the threshold is -- it is measuring "
                    "how little room there was to be wrong. THE LOCKED 0.5 LANDED ON THE "
                    "WORSE OF THE TWO AVAILABLE SCORES AND IS NOT BEING MOVED."
                    % (distinct,),
            "and_even_the_best_threshold_buys_nothing": "The best reachable score is %d, "
                    "which merely TIES the always-single-hop baseline of %d. Even with "
                    "hindsight and a free choice of threshold, scoping would not have beaten "
                    "using one form everywhere on these five substrates."
                    % (max(distinct), base["single_hop"]),
        },
        "D5_R_never_reads_the_outcome": {
            "note": "R is computed from the decode column alone. It does not read the "
                    "outcome, U, D_enc, or which form won. A test enforces this by scanning "
                    "the source of R_decode_redundancy.",
        },
    }

    scoring = [g for g in gates if g["weight"] == "full"]
    res = {
        "model": "SDL - the Scope Declaration Law",
        "spec_sha256": LOCKED,
        "score": "%d/%d" % (len(scoring) - len(notmet), len(scoring)),
        "gates": gates, "gates_not_met": notmet,
        "rule": "R > 0.5 -> single_hop ; R <= 0.5 -> two_hop",
        "substrates": substrates,
        "n_correct": n_correct, "n_correct_independent": n_correct_independent,
        "always_one_form_baselines": base,
        "threshold_sweep_distinct_scores": distinct,
        "threshold_sweep_fraction_beaten": round(frac_beaten, 4),
        "dcm_self_audit": {"V": round(V, 4), "I": round(I, 4), "C": round(C, 4),
                           "DELTA": round(DELTA, 4), "floor": S6_MIN,
                           "n_substrates": len(substrates)},
        "post_run_disclosures": disclosures,
        "primary_verdict": binding,
    }
    with open(os.path.join(HERE, "results_scoping.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in
                      ("score", "gates_not_met", "n_correct", "n_correct_independent",
                       "always_one_form_baselines", "threshold_sweep_distinct_scores",
                       "dcm_self_audit")}, indent=2))
    print("\n".join("  %-10s R=%.3f pred=%-10s actual=%-10s %s"
                    % (s["name"], s["R"], s["predicted"], s["winner"],
                       "OK" if s["correct"] else "WRONG") for s in substrates))


if __name__ == "__main__":
    main()
