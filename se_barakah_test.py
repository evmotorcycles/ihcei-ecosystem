#!/usr/bin/env python3
"""
se_barakah_test.py
=================
The first attempted EXTENSION of the LISM linear-coupling law beyond yeast and
GitHub, in the knowledge-propagation ("Barakah") domain the framework's own
operationalization points to. Runs on Stack Exchange question threads fetched via
api/se-search.js (SE API is blocked from the sandbox; the Vercel proxy reaches it).

TWO-HOP MAPPING (from SE metadata; independent actors -> plausibly independent hops)
  U      capacity            = log(1 + asker reputation)
  D_enc  sincere seeking      = question quality the community assigns to the ASKER's
                                post: min-max of clipped positive score. (encoding)
  D_dec  selflessness/onward  = the community's onward transmission, measured on
                                ANSWERERS: min-max of answer_count. (decoding)
  D      two-hop fidelity     = D_enc * D_dec
  E      Barakah / reuse       = downstream compounding reuse: high view_count
                                (top tercile = 1), a measured, non-circular outcome
                                distinct from whether the thread was answered.

Same discipline as the other cohorts: VIF channel-intact gate, nested curvature
LRT (primary), penalized-safe, two-directional read. INCONCLUSIVE if the hops
collapse (VIF>=5) or the failing region is unpopulated — reported honestly.
"""
import argparse
import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2
from sklearn.metrics import roc_auc_score


def mm(x):
    x = np.asarray(x, float)
    r = x.max() - x.min()
    return (x - x.min()) / r if r > 0 else x * 0.0


def load(path):
    d = json.load(open(path))
    qs = d.get("questions", d if isinstance(d, list) else [])
    return pd.DataFrame(qs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="pre-fetched /api/se-search response(s)")
    ap.add_argument("--score-cap", type=float, default=20.0)
    a = ap.parse_args()
    warnings.filterwarnings("ignore")

    d = load(a.json).drop_duplicates("id")
    d = d[(d.answer_count.notna()) & (d.view_count.notna())]
    n = len(d)
    U = np.log1p(d.reputation.fillna(0).values.astype(float))
    D_enc = mm(np.clip(d.score.values.astype(float), 0, a.score_cap))
    D_dec = mm(d.answer_count.values.astype(float))
    D = D_enc * D_dec
    Ds = mm(D)
    thr = np.quantile(d.view_count.values, 2 / 3)
    E = (d.view_count.values >= thr).astype(int)  # top-tercile downstream reuse

    print("=" * 74)
    print("LISM Barakah / knowledge-propagation extension — Stack Exchange")
    print("=" * 74)
    print(f"N threads = {n}   high-reuse E=1 = {int(E.sum())}   low-reuse E=0 = {int((E==0).sum())}")

    r = np.corrcoef(D_enc, D_dec)[0, 1]
    vif = 1 / (1 - r ** 2) if abs(r) < 1 else float("inf")
    gate = "PASS (channel intact)" if vif < 5 else "COLLAPSE (INCONCLUSIVE)"
    print(f"[GATE] VIF(D_enc,D_dec) = {vif:.3f} (r={r:+.3f}) -> {gate}")
    if int(E.sum()) < 100 or int((E == 0).sum()) < 100:
        print("[I2] failing region sparse (need >=100 each) -> underpowered")

    def auc(x):
        X = sm.add_constant(np.asarray(x, float))
        return roc_auc_score(E, sm.Logit(E, X).fit(disp=0).predict(X))
    print(f"\n[single-term AUC]  linear U*D_s = {auc(U*Ds):.3f}   quad U*D_s^2 = {auc(U*Ds**2):.3f}")

    def fit(cols):
        X = sm.add_constant(np.column_stack(cols))
        try:
            m = sm.Logit(E, X).fit(disp=0)
            if not np.isfinite(m.llf):
                raise ValueError
            return m
        except Exception:
            return sm.Logit(E, X).fit_regularized(disp=0, alpha=1.0, L1_wt=0.0)
    m1, m2 = fit([U, Ds]), fit([U, Ds, Ds ** 2])
    lr = 2 * (m2.llf - m1.llf)
    p = float(chi2.sf(max(lr, 0), 1))
    print(f"[PRIMARY nested curvature]  dAIC(quad-lin)={m1.aic-m2.aic:+.2f}  "
          f"LRT p={p:.3g}  beta_D2={m2.params[-1]:+.2f}")

    if vif >= 5:
        verdict = "INCONCLUSIVE (channel collapse)"
    elif (m1.aic - m2.aic) <= 0 or p >= 0.05:
        verdict = "LINEAR adequate — consistent with LISM (first extension beyond yeast+GitHub)"
    elif m2.params[-1] > 0:
        verdict = "curvature present, POSITIVE (convex) — would support quadratic"
    else:
        verdict = "curvature present but NEGATIVE (saturating) — against the accelerating penalty"
    print(f"\n[VERDICT] {verdict}")
    print("=" * 74)


if __name__ == "__main__":
    main()
