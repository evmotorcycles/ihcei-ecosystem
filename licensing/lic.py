"""
lic.py -- licensing Q3, Q4 and Q5, run against a single pre-registration.

Spec cd429dfa5208403d142f49d5ca8f6e4e09d8ce01dc6065c3e8892608dd8c4a9f, locked after a
pre-flight that found and removed two confounds I had built into the Q4 artifact set.

Q4 executes real Python. Q5 and Q3 read committed real-world files. No simulator of ours is
used anywhere, and the three-proposals engine is deliberately not touched.
"""
import csv
import hashlib
import json
import os
import random
import statistics
import subprocess
import sys
from collections import Counter, defaultdict

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCKED = "cd429dfa5208403d142f49d5ca8f6e4e09d8ce01dc6065c3e8892608dd8c4a9f"

SPEC = json.load(open(os.path.join(HERE, "prereg", "licensing_prereg.json")))
_h = hashlib.sha256(json.dumps(SPEC, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if _h != LOCKED:
    raise SystemExit("SPEC CHANGED after locking: %s != %s" % (_h, LOCKED))

SEED = 20260803
Q4_B, Q4_C, Q4_D, Q4_E = 0.95, 0.65, 0.20, 0.20
Q5_ABL, Q5_MARGIN, Q5_LO, Q5_HI = 0.55, 0.05, 0.40, 0.60
Q3_MIN_N, Q3_MIN_EV, Q3_MARGIN = 50, 10, 0.10
N_BOOT = 2000
PRAISE = ("verified", "certified", "integrity", "guaranteed", "rated safe",
          "checked for accuracy", "trustworthy")


# ===================================================================== helpers
def auc_binary(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    g = 0.0
    for a in pos:
        for b in neg:
            g += 1.0 if a > b else (0.5 if a == b else 0.0)
    return g / (len(pos) * len(neg))


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    a, b = rank(x), rank(y)
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(len(a)))
    den = (sum((v - ma) ** 2 for v in a) * sum((v - mb) ** 2 for v in b)) ** 0.5
    return num / den if den else 0.0


def cv_auc(X, y, seed=SEED):
    if len(np.unique(y)) < 2:
        return None
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    out = []
    for tr, te in skf.split(X, y):
        if len(np.unique(y[tr])) < 2 or len(np.unique(y[te])) < 2:
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
        m.fit(X[tr], y[tr])
        out.append(roc_auc_score(y[te], m.predict_proba(X[te])[:, 1]))
    return float(np.mean(out)) if out else None


# ================================================================== Q4 kernel
# REFERENCE IMPLEMENTATIONS. Written after the lock, but they only define what
# CORRECT means -- they never see the artifacts and cannot be tuned to a bug.
def ref_median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def ref_rle(s):
    out = []
    for ch in s:
        if out and out[-1][0] == ch:
            out[-1] = (ch, out[-1][1] + 1)
        else:
            out.append((ch, 1))
    return out


def ref_balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


def ref_topk(xs, k):
    return sorted(xs, reverse=True)[:k] if k > 0 else []


REF = {"median": (ref_median, "median"), "rle": (ref_rle, "run_length_encode"),
       "balanced": (ref_balanced, "is_balanced"), "topk": (ref_topk, "top_k")}


def build_bank():
    """Locked edge cases from the spec, PLUS 50 random inputs per task."""
    ec = SPEC["Q4_the_execution_kernel"]["THE_HELD_OUT_TEST_BANK_AND_WHY_ITS_EDGE_CASES_ARE_LOCKED_HERE"]["locked_edge_cases"]
    rng = random.Random(SEED)
    bank = defaultdict(list)
    for case in ec["median"]:
        bank["median"].append((list(case),))
    for case in ec["run_length_encode"]:
        bank["rle"].append((case,))
    for case in ec["is_balanced"]:
        bank["balanced"].append((case,))
    for xs, k in ec["top_k"]:
        bank["topk"].append((list(xs), k))
    for _ in range(50):
        bank["median"].append(([rng.randint(-50, 50) for _ in range(rng.randint(0, 9))],))
        bank["rle"].append(("".join(rng.choice("aab") for _ in range(rng.randint(0, 12))),))
        bank["balanced"].append(("".join(rng.choice("()[]{}x") for _ in range(rng.randint(0, 12))),))
        n = rng.randint(0, 8)
        bank["topk"].append(([rng.randint(-20, 20) for _ in range(n)], rng.randint(-2, n + 2)))
    return dict(bank)


def kernel_verdicts(bank):
    """Fraction of held-out tests passed. The kernel never reads the self-report."""
    out = {}
    crashed = []
    for a in SPEC["artifacts_Q4"]:
        fn_ref, fn_name = REF[a["task"]]
        ns = {}
        try:
            exec(compile(a["source"], "<artifact:%s>" % a["name"], "exec"), ns)  # noqa: S102
            fn = ns[fn_name]
        except Exception:
            crashed.append(a["name"])
            out[a["name"]] = 0.0
            continue
        passed = 0
        cases = bank[a["task"]]
        for args in cases:
            try:
                got = fn(*[list(x) if isinstance(x, list) else x for x in args])
            except Exception:
                continue
            try:
                want = fn_ref(*[list(x) if isinstance(x, list) else x for x in args])
            except Exception:
                continue
            if got == want:
                passed += 1
        out[a["name"]] = passed / len(cases)
    return out, crashed


def helm_verdicts():
    p = subprocess.run(["node", os.path.join(HERE, "helm_collect.mjs")],
                       capture_output=True, text=True, cwd=ROOT, timeout=300)
    if p.returncode != 0:
        raise SystemExit("helm collector failed: " + p.stderr[-800:])
    d = json.loads(p.stdout[p.stdout.index("{"):])
    # oriented so HIGHER = MORE LIKELY CORRECT, as the spec declares
    return {r["name"]: 1.0 - r["p_manipulative"] for r in d["rows"]}


# =============================================================== Q5 / Q3 data
def load_repos():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "github",
                                                 "govphys_quadratic_results.csv"))))
    keep = [r for r in rows if r["tau_v_imputed"].strip().lower() not in ("true", "1", "yes")]
    y = np.array([1 if r["archived"].strip().lower() in ("true", "1", "yes") else 0
                  for r in keep])
    static = np.array([[float(r["stars"]), float(r["U"])] for r in keep])
    process = np.array([[float(r["tau_v"])] for r in keep])
    return keep, y, static, process


def load_interbank():
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
    dg = {i: deg.get(i, 0) for i in elig}
    q_deg = statistics.quantiles([dg[i] for i in elig], n=4)[2]
    q_u = statistics.quantiles([U[i] for i in elig], n=4)[2]
    systemic = {i for i in elig if dg[i] >= q_deg and U[i] >= q_u}
    return elig, lab, systemic, q_deg, q_u


def rate_diff(idx, lab, systemic):
    s = [i for i in idx if i in systemic]
    r = [i for i in idx if i not in systemic]
    if not s or not r:
        return None
    return sum(lab[i] for i in s) / len(s) - sum(lab[i] for i in r) / len(r)


def boot_ci(elig, lab, systemic, seed):
    rng = random.Random(seed)
    vals = []
    for _ in range(N_BOOT):
        samp = [rng.choice(elig) for _ in elig]
        d = rate_diff(samp, lab, systemic)
        if d is not None:
            vals.append(d)
    vals.sort()
    return vals[int(0.05 * len(vals))], vals[int(0.95 * len(vals))]


# ======================================================================= main
def main():
    gates, notmet = [], []

    def gate(gid, ok, detail, weight="full"):
        gates.append({"id": gid, "met": bool(ok), "weight": weight, "detail": detail})
        if weight == "full" and not ok:
            notmet.append(gid)
        return ok

    # ------------------------------------------------------------------ Q4
    bank = build_bank()
    kern, crashed = kernel_verdicts(bank)
    helm = helm_verdicts()
    arts = SPEC["artifacts_Q4"]
    names = [a["name"] for a in arts]
    correct = [1 if a["declared_correct"] else 0 for a in arts]
    words = [len(a["source"].split()) for a in arts]
    cert = [1 if any(t in a["self_report"].lower() for t in PRAISE) else 0 for a in arts]
    kv = [kern[n] for n in names]
    hv = [helm[n] for n in names]

    finite = all(0.0 <= v <= 1.0 for v in kv + hv)
    gate("Q4_A_integrity",
         len(arts) == 20 and sum(correct) == 8 and finite and not crashed,
         "%d artifacts, %d declared correct, %d tests in the bank, harness crashes: %s, "
         "verdicts finite: %s" % (len(arts), sum(correct), sum(len(v) for v in bank.values()),
                                  crashed or "none", finite))

    auc_k = auc_binary(kv, correct)
    auc_h = auc_binary(hv, correct)
    gate("Q4_B_PRIMARY_THE_KERNEL_DISCRIMINATES_CORRECTNESS", auc_k >= Q4_B,
         "AUC(kernel, declared correctness) = %.4f (needs >= %.2f). Bugs the bank missed "
         "would show up here as a shortfall." % (auc_k, Q4_B))
    gate("Q4_C_CONTRAST_HELM_DOES_NOT", auc_h <= Q4_C,
         "AUC(HELM oriented verdict, declared correctness) = %.4f (needs <= %.2f)"
         % (auc_h, Q4_C))
    sp_k = spearman(kv, words)
    sp_h = spearman(hv, words)
    gate("Q4_D_THE_LENGTH_CONFOUND_IS_GONE_FOR_THE_KERNEL", abs(sp_k) <= Q4_D,
         "Spearman(kernel verdict, word count) = %+.4f (needs |r| <= %.2f). HELM on this "
         "same set: %+.4f. HELM on spec 5576e524: -0.4831." % (sp_k, Q4_D, sp_h))

    rk = [round(v, 9) for v in kv]
    V = 1.0 - Counter(rk).most_common(1)[0][1] / len(rk)
    p = min(sum(cert), len(cert) - sum(cert)) / len(cert)
    I = 4.0 * p * (1.0 - p)
    C = min(1.0, len(set(rk)) / len(rk))
    DELTA = V * I * C
    q4e = DELTA >= Q4_E
    gate("Q4_E_DCM_SELF_AUDIT_ON_THE_KERNEL", q4e,
         "DELTA = V %.4f * I %.4f * C %.4f = %.4f (needs >= %.2f). FLOOR UNCHANGED after "
         "five voids." % (V, I, C, DELTA, Q4_E))

    src = open(os.path.abspath(__file__)).read()
    kernel_blind = "self_report" not in src.split("def kernel_verdicts")[1].split("def helm_verdicts")[0]
    gates.append({"id": "Q4_F_the_kernel_ignores_self_report", "met": None,
                  "weight": "excluded",
                  "detail": "EXCLUDED, true by construction. kernel_verdicts() reads only "
                            "a['source'] and executes it; the self-report never enters the "
                            "code path. Verified as a source-level assertion (%s), not "
                            "measured -- a quantity that cannot come out otherwise is not "
                            "evidence." % ("holds" if kernel_blind else "FAILED")})
    gates.append({"id": "Q4_G_does_this_generalise_beyond_code", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. Execution kernels work because code has "
                            "objective ground truth. Nothing here licenses any claim about "
                            "evaluating prose, where the ground-truth problem that defeated "
                            "HELM is still open and still needs independent raters."})

    # ------------------------------------------------------------------ Q5
    keep, y, Xs, Xp = load_repos()
    Xc = np.hstack([Xs, Xp])
    a_s, a_p, a_c = cv_auc(Xs, y), cv_auc(Xp, y), cv_auc(Xc, y)
    rng = np.random.default_rng(SEED)
    yperm = rng.permutation(y)
    ctrl = {"STATIC": cv_auc(Xs, yperm), "PROCESS": cv_auc(Xp, yperm),
            "COMBINED": cv_auc(Xc, yperm)}

    gate("Q5_A_integrity",
         len(keep) == 866 and len(set(y.tolist())) == 2 and None not in (a_s, a_p, a_c),
         "%d non-imputed rows of 992, %d archived / %d live, all AUCs finite"
         % (len(keep), int(y.sum()), int(len(y) - y.sum())))
    abl = a_s >= Q5_ABL
    gate("Q5_B_ABLATION_THE_STATIC_ARM_IS_ABOVE_CHANCE", abl,
         "AUC(STATIC: stars, U) = %.4f (needs >= %.2f)" % (a_s, Q5_ABL))
    gate("Q5_C_PRIMARY_PROCESS_BEATS_STATIC", (a_p - a_s) >= Q5_MARGIN,
         "AUC(PROCESS: tau_v) = %.4f minus AUC(STATIC) = %.4f is %+.4f (needs >= %+.2f). "
         "COMBINED = %.4f." % (a_p, a_s, a_p - a_s, Q5_MARGIN, a_c))
    bad5 = {k: round(v, 4) for k, v in ctrl.items() if not (Q5_LO <= v <= Q5_HI)}
    gate("Q5_D_THE_SHUFFLED_LABEL_CONTROL_IS_AT_CHANCE", not bad5,
         "permuted-label AUCs %s must all lie in [%.2f, %.2f]. Outside: %s"
         % ({k: round(v, 4) for k, v in ctrl.items()}, Q5_LO, Q5_HI, bad5 or "none"))
    gates.append({"id": "Q5_E_is_tau_v_a_LEADING_indicator", "met": None,
                  "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. tau_v was harvested as mean close latency at "
                            "SNAPSHOT TIME with no cutoff before archiving, so it includes "
                            "issues closed during the decline. On this cohort it is "
                            "CONTEMPORANEOUS. Separating leading from concurrent needs "
                            "tau_v recomputed on a window ending strictly before the "
                            "archiving date, which the committed file does not support."})

    # ------------------------------------------------------------------ Q3
    elig, lab, systemic, q_deg, q_u = load_interbank()
    sysl = [i for i in elig if i in systemic]
    rout = [i for i in elig if i not in systemic]
    ev_s, ev_r = sum(lab[i] for i in sysl), sum(lab[i] for i in rout)
    gate("Q3_A_BOTH_CLASSES_ARE_POPULATED",
         len(sysl) >= Q3_MIN_N and len(rout) >= Q3_MIN_N
         and ev_s >= Q3_MIN_EV and ev_r >= Q3_MIN_EV,
         "SYSTEMIC n=%d events=%d; ROUTINE n=%d events=%d (each needs n>=%d, events>=%d). "
         "Thresholds: degree >= %.0f and U >= %.4f."
         % (len(sysl), ev_s, len(rout), ev_r, Q3_MIN_N, Q3_MIN_EV, q_deg, q_u))
    d3 = rate_diff(elig, lab, systemic)
    gate("Q3_B_PRIMARY_THE_CLASSES_DIFFER_IN_REALISED_RISK", d3 >= Q3_MARGIN,
         "withdrawal rate SYSTEMIC %.4f minus ROUTINE %.4f = %+.4f (needs >= %+.2f)"
         % (ev_s / len(sysl), ev_r / len(rout), d3, Q3_MARGIN))
    lo3, hi3 = boot_ci(elig, lab, systemic, SEED)
    gate("Q3_C_THE_DIFFERENCE_IS_PRECISE_ENOUGH", not (lo3 <= 0.0 <= hi3),
         "90%% bootstrap CI on the rate difference = [%+.4f, %+.4f] and must EXCLUDE 0"
         % (lo3, hi3))
    prng = random.Random(SEED + 5)
    pv = list(lab.values())
    prng.shuffle(pv)
    plab = dict(zip(elig, pv))
    plo, phi = boot_ci(elig, plab, systemic, SEED + 6)
    gate("Q3_D_THE_PERMUTATION_CONTROL_IS_NULL", plo <= 0.0 <= phi,
         "with labels permuted the 90%% CI is [%+.4f, %+.4f] and must contain 0"
         % (plo, phi))
    gates.append({"id": "Q3_E_does_the_fixed_policy_ASSIGNMENT_improve_outcomes",
                  "met": None, "weight": "excluded",
                  "detail": "UNTESTABLE-HERE. That is an intervention and historical data "
                            "cannot answer it. The only alternative substrate is the "
                            "three-proposals simulator we wrote ourselves, which is not "
                            "evidence about the world and is deliberately not used."})

    # -------------------------------------------------------------- scoring
    def arm(prefix):
        g = [x for x in gates if x["id"].startswith(prefix) and x["weight"] == "full"]
        miss = [x["id"] for x in g if not x["met"]]
        return {"score": "%d/%d" % (len(g) - len(miss), len(g)), "not_met": miss}

    suspect = []
    if auc_k is not None and auc_k >= 0.99995:
        suspect.append("Q4_kernel_AUC_at_1.0")
    if bad5:
        suspect.append("Q5_shuffled_control_off_chance")
    if abs(I - 1.0) < 1e-9:
        suspect.append("Q4_DCM_I_at_1.0_by_grid_design")

    res = {
        "model": "Licensing Q3, Q4 and Q5",
        "spec_sha256": LOCKED,
        "arms": {"Q3": arm("Q3_"), "Q4": arm("Q4_"), "Q5": arm("Q5_")},
        "gates": gates, "gates_not_met": notmet,
        "simulated_values": 0,
        "Q4": {"auc_kernel_vs_correctness": round(auc_k, 4),
               "auc_helm_vs_correctness": round(auc_h, 4),
               "spearman_kernel_vs_wordcount": round(sp_k, 4),
               "spearman_helm_vs_wordcount": round(sp_h, 4),
               "n_tests_in_bank": sum(len(v) for v in bank.values()),
               "dcm": {"V": round(V, 4), "I": round(I, 4), "C": round(C, 4),
                       "DELTA": round(DELTA, 4), "floor": Q4_E},
               "per_artifact": {a["name"]: {"declared_correct": a["declared_correct"],
                                            "kernel": round(kern[a["name"]], 4),
                                            "helm_oriented": round(helm[a["name"]], 4)}
                                for a in arts}},
        "Q5": {"n": len(keep), "archived": int(y.sum()),
               "auc_static": round(a_s, 4), "auc_process": round(a_p, 4),
               "auc_combined": round(a_c, 4), "process_minus_static": round(a_p - a_s, 4),
               "shuffled_control": {k: round(v, 4) for k, v in ctrl.items()}},
        "Q3": {"systemic_n": len(sysl), "systemic_events": ev_s,
               "routine_n": len(rout), "routine_events": ev_r,
               "systemic_rate": round(ev_s / len(sysl), 4),
               "routine_rate": round(ev_r / len(rout), 4),
               "rate_difference": round(d3, 4),
               "CI90": [round(lo3, 4), round(hi3, 4)],
               "permutation_CI90": [round(plo, 4), round(phi, 4)]},
        "too_perfect_flag": suspect,
        "post_run_disclosures": {
            "D1_what_each_arm_licenses": {
                "Q4": "An execution kernel discriminating correctness where a text evaluator "
                      "does not, on 20 implementations across 4 tasks. NOT that execution "
                      "kernels solve evaluation generally, and NOT anything about prose.",
                "Q5": "Whether process telemetry beats static structure at separating "
                      "archived from live repositories CONTEMPORANEOUSLY. NOT that tau_v is "
                      "an early warning -- Q5_E records why that stays untestable here.",
                "Q3": "Whether the systemic/routine classification separates realised risk on "
                      "one real network in one quarter. NOT that assigning different "
                      "instruments to those classes helps anyone.",
            },
            "D2_the_two_confounds_removed_before_the_lock": {
                "note": "A first draft of the Q4 artifacts had Spearman(word count, correct) "
                        "= +0.3547 and Spearman(self-certifying, correct) = -0.7917. Both "
                        "were leaks I authored: a length detector would have beaten chance "
                        "and a 'distrust self-praise' heuristic would have nearly solved the "
                        "task. The ARTIFACTS were rewritten, never a threshold, and the "
                        "residuals are +0.0177 and 0.0000.",
            },
            "D3_the_edge_cases_were_locked_to_stop_me_tuning_the_bank": {
                "note": "The runner is written after the lock and I already knew every "
                        "declared bug, so a post-hoc test bank could have been tuned to "
                        "catch exactly those. The edge-case inputs are fixed in the "
                        "specification; the runner may only add random property tests.",
            },
            "D4_corrections_to_the_proposal_this_spec_implements":
                SPEC["TWO_CORRECTIONS_TO_THE_PROPOSAL_THIS_SPEC_IMPLEMENTS"],
        },
    }
    with open(os.path.join(HERE, "results_lic.json"), "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k] for k in ("arms", "gates_not_met", "Q4", "Q5", "Q3",
                                          "too_perfect_flag")}, indent=2)[:3200])


if __name__ == "__main__":
    main()
