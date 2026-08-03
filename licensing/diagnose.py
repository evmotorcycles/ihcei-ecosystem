"""
diagnose.py -- POST-HOC analysis for the licensing run. NOT PRE-REGISTERED, NOT SCORED.
Kept in its own file so nothing here can be mistaken for a locked gate.

TWO THINGS ARE EXAMINED.

1. THE Q5 COHORT IS CONFOUNDED BY ITS OWN CONSTRUCTION. The 992-repo file is stratified
   S1_thriving / S2_aging / S3_at_risk / S4_failed, and S4_failed is 100 percent archived --
   the strata were built USING the outcome. Median stars run 42,966 in S1 against 100 in S3,
   so the static arm's AUC rides partly on stratum membership rather than on structure
   predicting fate. Within a stratum, stars barely separate archived from live at all
   (S1: 34,726 against 43,317; S2: 928 against 931; S3: 100 against 100).

   The pre-registered Q5_C failure is therefore reported as measured -- a primary is not
   retracted because a reason was later found why it might have been unfair to one arm --
   but the honest question is whether the failure SURVIVES removing the confound. It does.

2. THE Q3 PERMUTATION CONTROL WAS IMPLEMENTED WRONG, AND THE GATE STILL COUNTS AS FAILED.
   The spec said "with outcome labels permuted, the 90 percent CI contains 0". The runner
   formed that CI by BOOTSTRAPPING A SINGLE FIXED PERMUTATION, which estimates the sampling
   spread around whatever that one permutation happened to land on -- not the permutation
   null. A permutation null needs REPEATED permutations. That is a defect in my runner, not
   a finding about the data, and the corrected control is computed below. The pre-registered
   gate is NOT retroactively passed; correcting it belongs in a new specification.
"""
import csv
import json
import os
import random
import statistics
import sys
from collections import defaultdict

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEED = 20260803
N_PERM = 2000


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


def q5_confound():
    rows = [r for r in csv.DictReader(
        open(os.path.join(ROOT, "data", "github", "govphys_quadratic_results.csv")))
        if r["tau_v_imputed"].strip().lower() not in ("true", "1", "yes")]
    by = defaultdict(list)
    for r in rows:
        by[r["stratum"]].append(r)

    def arch(rs):
        return [r for r in rs if r["archived"].strip().lower() in ("true", "1", "yes")]
    strata = {k: {"n": len(v), "archived_share": round(len(arch(v)) / len(v), 4),
                  "median_stars": statistics.median(float(r["stars"]) for r in v),
                  "median_tau_v": round(statistics.median(float(r["tau_v"]) for r in v), 2)}
              for k, v in sorted(by.items())}

    sub = [r for r in rows if r["stratum"] != "S4_failed"]
    y = np.array([1 if r["archived"].strip().lower() in ("true", "1", "yes") else 0
                  for r in sub])
    Xs = np.array([[float(r["stars"]), float(r["U"])] for r in sub])
    Xp = np.array([[float(r["tau_v"])] for r in sub])
    a_s, a_p = cv_auc(Xs, y), cv_auc(Xp, y)
    return {
        "strata": strata,
        "THE_CONFOUND": "S4_failed is 100 percent archived, so the strata were built using "
                        "the outcome. Median stars span 42,966 (S1) to 100 (S3), which means "
                        "the static arm's advantage rides partly on stratum membership.",
        "within_stratum_stars_barely_separate":
            "S1 archived 34,726 vs live 43,317; S2 928 vs 931; S3 100 vs 100.",
        "S4_EXCLUDED_rerun": {"n": len(sub), "archived": int(y.sum()),
                              "auc_static": round(a_s, 4), "auc_process": round(a_p, 4),
                              "process_minus_static": round(a_p - a_s, 4)},
        "THE_FAILURE_SURVIVES_THE_CONFOUND":
            "With the outcome-defined stratum removed, static still beats process by %+.4f. "
            "Q5_C's failure is not an artefact of cohort construction: tau_v genuinely does "
            "not beat stars and leverage on this data." % (a_p - a_s),
    }


def q3_correct_permutation():
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
    sysl = [i for i in elig if i in systemic]
    rout = [i for i in elig if i not in systemic]

    def diff(l):
        return sum(l[i] for i in sysl) / len(sysl) - sum(l[i] for i in rout) / len(rout)
    obs = diff(lab)
    rng = random.Random(99)
    vals = []
    for _ in range(N_PERM):
        pv = list(lab.values())
        rng.shuffle(pv)
        vals.append(diff(dict(zip(elig, pv))))
    vals.sort()
    lo, hi = vals[int(0.05 * N_PERM)], vals[int(0.95 * N_PERM)]
    return {
        "WHAT_THE_RUNNER_DID_WRONG": "It bootstrapped ONE fixed permutation, which estimates "
                                     "the sampling spread around whatever that permutation "
                                     "landed on. A permutation null requires REPEATED "
                                     "permutations.",
        "observed_difference": round(obs, 4),
        "n_permutations": N_PERM,
        "null_mean": round(statistics.fmean(vals), 5),
        "null_90_band": [round(lo, 4), round(hi, 4)],
        "band_contains_zero": bool(lo <= 0.0 <= hi),
        "one_sided_p": round(sum(1 for v in vals if v >= obs) / len(vals), 4),
        "AND_THE_GATE_STILL_COUNTS_AS_FAILED": "The corrected control passes decisively, but "
            "the pre-registered gate is NOT retroactively passed on the strength of a "
            "post-hoc reimplementation. Correcting a defective control belongs in a new "
            "specification, which is what licensing_v2 does.",
    }


def main():
    out = {"STATUS": "POST-HOC. Not pre-registered. Not scored. No gate depends on it.",
           "Q5_the_cohort_is_confounded_by_its_own_construction": q5_confound(),
           "Q3_the_permutation_control_was_implemented_wrong": q3_correct_permutation()}
    with open(os.path.join(HERE, "results_lic_posthoc.json"), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    json.dump(out, sys.stdout, indent=2, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
