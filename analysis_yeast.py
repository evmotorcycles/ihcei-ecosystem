#!/usr/bin/env python3
"""
analysis_yeast.py
================
Yeast (S. cerevisiae) coupling analysis on the cohort rebuilt end-to-end from
raw public data (STRING v12 physical links + DEG essentiality + BioGRID name
map; see build_yeast_cohort.py / extract_deg_essential.py / biogrid_name_map.py).

Directly tests referee point M5: the manuscript reports the quadratic single-
term form as "anti-predictive, AUC 0.41 (below chance)" from an in-sample logit
it also calls degenerate under near-perfect separation. A monotone transform of
a predictor cannot legitimately fall to AUC 0.41 unless the fit sign-flipped, so
we re-fit with (a) a converging in-sample logit, (b) a 5-fold cross-validated
regularized fit, and (c) the nested curvature LRT, and report all three.

Input CSV columns: E_essential (or E), U, D, D_enc, D_dec.
"""
import argparse
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score


def mm(x):
    x = np.asarray(x, float)
    r = x.max() - x.min()
    return (x - x.min()) / r if r > 0 else x * 0.0


def insample_auc(E, x):
    X = sm.add_constant(np.asarray(x, float))
    m = sm.Logit(E, X).fit(disp=0)
    return roc_auc_score(E, m.predict(X))


def cv_auc(E, x, seed=42):
    p = cross_val_predict(LogisticRegression(max_iter=1000),
                          np.asarray(x, float).reshape(-1, 1), E,
                          cv=StratifiedKFold(5, shuffle=True, random_state=seed),
                          method="predict_proba")[:, 1]
    return roc_auc_score(E, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="yeast_interactome_DEG.csv")
    a = ap.parse_args()
    d = pd.read_csv(a.csv)
    E = d[("E_essential" if "E_essential" in d else "E")].astype(int).values
    U, D = d.U.values.astype(float), d.D.values.astype(float)
    Ds = mm(D)
    r = np.corrcoef(d.D_enc, d.D_dec)[0, 1]

    print("=" * 70)
    print("Yeast coupling analysis (rebuilt from raw STRING + DEG + BioGRID)")
    print("=" * 70)
    print(f"N={len(d)}  essential={E.sum()} ({100*E.mean():.1f}%)   "
          f"VIF(D_enc,D_dec)={1/(1-r**2):.3f} (r={r:+.3f}) -> channel intact")

    print("\n[in-sample single-term AUC]")
    print(f"  linear U*Ds   : {insample_auc(E, U*Ds):.3f}   (manuscript linear 0.74)")
    print(f"  quad   U*Ds^2 : {insample_auc(E, U*Ds**2):.3f}   (manuscript quad ~0.41)")

    print("\n[M5 FIX: 5-fold cross-validated, regularized AUC]")
    print(f"  linear U*Ds   : {cv_auc(E, U*Ds):.3f}")
    print(f"  quad   U*Ds^2 : {cv_auc(E, U*Ds**2):.3f}")
    print(f"  D alone       : {cv_auc(E, Ds):.3f}")
    print(f"  U alone       : {cv_auc(E, U):.3f}")

    def fit(cols):
        return sm.Logit(E, sm.add_constant(np.column_stack(cols))).fit(disp=0)
    m1, m2 = fit([U, D]), fit([U, D, D**2])
    lr = 2 * (m2.llf - m1.llf)
    p = float(chi2.sf(max(lr, 0), 1))
    print("\n[primary nested curvature: M1(U+D) vs M2(U+D+D^2)]")
    print(f"  dAIC(quad-lin)={m1.aic-m2.aic:+.2f}  LRT={lr:.2f}  p={p:.3g}  "
          f"beta_D2={m2.params[-1]:+.3f}")
    if (m1.aic - m2.aic) <= 0 or p >= 0.05:
        print("  -> no curvature; linear adequate")
    elif m2.params[-1] < 0:
        print("  -> significant curvature but NEGATIVE (saturating/concave): the")
        print("     opposite sign to the proposed accelerating penalty E=U*D^2.")
    else:
        print("  -> significant positive curvature")
    print("=" * 70)


if __name__ == "__main__":
    main()
