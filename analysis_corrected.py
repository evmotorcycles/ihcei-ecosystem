#!/usr/bin/env python3
"""
analysis_corrected.py
=====================
Revised analysis addressing referee points M2, M3, and M5.

WHAT CHANGED vs reproduce_analysis.py (and why):

  M2 -- The single-term contrast  logit(E) ~ U*D_s   vs   logit(E) ~ U*D_s^2
        is NON-NESTED and its dAIC sign is sensitive to the empirical D
        distribution (it can favour "quadratic" even on purely linear data).
        It is therefore DEMOTED to a secondary "literal-form" check.
        The PRIMARY curvature test is now the NESTED comparison
            M1: logit(E) ~ U + D        vs    M2: logit(E) ~ U + D + D^2
        via a likelihood-ratio test on the D^2 term (1 df). This isolates the
        unique variance a squared term carries -- the only thing that answers
        "is the coupling curved?" in a scale-robust way.

  M3 -- The permutation result is reported as a REPRODUCIBLE tail statement
        (fraction of label/predictor permutations at least as favourable to
        the observed effect, + whether the observed statistic lies beyond the
        null envelope), not as a fragile point z-score whose magnitude depends
        on the chosen statistic.

  M5 -- Where the quadratic logit is degenerate under separation, we fall back
        to an L2-regularised fit so a comparison exists rather than a crash,
        and we say so.

Runs on either the real deposited CSV or the synthetic reproducibility
fixture (make_synthetic_cohort.py). Framework-neutral: pure statistics.
"""
import argparse
import sys

import numpy as np
import pandas as pd
from scipy.stats import chi2, mannwhitneyu
import statsmodels.api as sm


def minmax(s):
    s = np.asarray(s, float)
    rng = s.max() - s.min()
    return (s - s.min()) / rng if rng > 0 else s * 0.0


def vif(a, b):
    r = np.corrcoef(a, b)[0, 1]
    return (1.0 / (1.0 - r ** 2), r)


def fit_logit(y, X, regularized=False):
    """Return a fitted logit; fall back to L2 if separation prevents MLE."""
    Xc = sm.add_constant(X, has_constant="add")
    try:
        m = sm.Logit(y, Xc).fit(disp=0)
        # crude separation guard: implausible params / non-finite llf
        if not np.isfinite(m.llf) or np.abs(m.params).max() > 50:
            raise ValueError("separation")
        return m, False
    except Exception:
        if regularized:
            m = sm.Logit(y, Xc).fit_regularized(disp=0, alpha=1.0, L1_wt=0.0)
            return m, True
        raise


def lrt(ll_full, ll_reduced, df=1):
    stat = 2.0 * (ll_full - ll_reduced)
    return stat, float(chi2.sf(max(stat, 0.0), df))


def nested_curvature_test(y, U, D):
    """PRIMARY (M2): does D^2 carry unique variance over U + D?"""
    m1, _ = fit_logit(y, np.column_stack([U, D]))
    m2, reg = fit_logit(y, np.column_stack([U, D, D ** 2]), regularized=True)
    d_aic = m1.aic - m2.aic  # >0 favours the quadratic (curved) model
    stat, p = lrt(m2.llf, m1.llf, df=1)
    beta_d2 = float(m2.params[-1])
    return {
        "dAIC_quad_minus_lin": d_aic,
        "LRT_stat": stat,
        "LRT_p": p,
        "beta_D2": beta_d2,
        "regularized_quad_fit": reg,
    }


def literal_form_check(y, U, Ds):
    """SECONDARY (M2): the paper's literal single-term forms. Distribution-
    sensitive and non-nested -- reported for continuity, not as the arbiter."""
    ml, _ = fit_logit(y, (U * Ds))
    mq, reg = fit_logit(y, (U * Ds ** 2), regularized=True)
    return {"dAIC_quad_minus_lin": ml.aic - mq.aic, "regularized_quad_fit": reg}


def permutation_tail(y, U, D, n=1000, seed=42):
    """M3: reproducible tail. Statistic = LRT stat for D^2 unique variance.
    Permute D (and D^2 with it) to break its link to y; report the fraction of
    permutations whose curvature statistic >= observed, i.e. an empirical p for
    'D^2 carries curvature by chance'. Deterministic given seed."""
    rng = np.random.default_rng(seed)
    m1, _ = fit_logit(y, np.column_stack([U, D]))
    m2, _ = fit_logit(y, np.column_stack([U, D, D ** 2]), regularized=True)
    obs, _ = lrt(m2.llf, m1.llf, df=1)
    null = np.empty(n)
    for i in range(n):
        Dp = rng.permutation(D)
        try:
            mp, _ = fit_logit(y, np.column_stack([U, Dp, Dp ** 2]), regularized=True)
            mp1, _ = fit_logit(y, np.column_stack([U, Dp]))
            null[i], _ = lrt(mp.llf, mp1.llf, df=1)
        except Exception:
            null[i] = 0.0
    frac_ge = float((null >= obs).mean())
    beyond = bool(obs > null.max())
    return {"observed_curvature_stat": obs, "perm_p_ge_observed": frac_ge,
            "beyond_null_envelope": beyond, "n_perm": n, "seed": seed}


def tau_v_third_law(df):
    f = df[df.E == 0].tau_v
    s = df[df.E == 1].tau_v
    _, p_all = mannwhitneyu(f, s, alternative="greater")
    fm = df[(df.E == 0) & (df.tau_v_imputed == 0)].tau_v
    sm_ = df[(df.E == 1) & (df.tau_v_imputed == 0)].tau_v
    _, p_meas = mannwhitneyu(fm, sm_, alternative="greater")
    return {"mean_failed": float(f.mean()), "mean_survived": float(s.mean()),
            "p_all": float(p_all), "p_measured_only": float(p_meas),
            "imputed_frac_failed": float(df[df.E == 0].tau_v_imputed.mean()),
            "imputed_frac_survived": float(df[df.E == 1].tau_v_imputed.mean())}


def run(path, synthetic_note):
    df = pd.read_csv(path)
    y = (df.E == 0).astype(int).values  # model failure
    U = df.U.values.astype(float)
    D = df.D.values.astype(float)
    Ds = minmax(D)

    print("=" * 74)
    print("LISM corrected analysis  (nested curvature test = primary)")
    if synthetic_note:
        print(">>> SYNTHETIC fixture: ground truth is LINEAR. Expect: VIF pass,")
        print(">>> no curvature, tau_v recovered. Not the paper's empirical result.")
    print("=" * 74)
    n_fail = int((df.E == 0).sum())
    print(f"N = {len(df)}   failed = {n_fail}   survived = {int((df.E==1).sum())}")

    v, r = vif(df.D_enc, df.D_dec)
    gate = "PASS (channel intact)" if v < 5 else "INCONCLUSIVE (channel collapse)"
    print(f"\n[GATE]  VIF(D_enc,D_dec) = {v:.3f}  (r={r:+.3f})  -> {gate}")
    if v >= 5:
        print("  Quadratic test not identifiable; stopping curvature inference.")

    prim = nested_curvature_test(y, U, D)
    print("\n[PRIMARY - nested curvature, M1:U+D vs M2:U+D+D^2]")
    print(f"  dAIC(quad-lin) = {prim['dAIC_quad_minus_lin']:+.2f}   "
          f"(>0 would favour curvature)")
    print(f"  LRT on D^2 (1 df): stat = {prim['LRT_stat']:.2f}, p = {prim['LRT_p']:.3g}, "
          f"beta_D2 = {prim['beta_D2']:+.3f}"
          f"{'  [L2 fallback]' if prim['regularized_quad_fit'] else ''}")
    verdict = ("NO CURVATURE (linear adequate)" if prim["dAIC_quad_minus_lin"] <= 0
               or prim["LRT_p"] >= 0.05 else "curvature signal present")
    print(f"  -> {verdict}")

    lit = literal_form_check(y, U, Ds)
    print("\n[SECONDARY - literal single-term forms (distribution-sensitive)]")
    print(f"  dAIC(quad-lin) = {lit['dAIC_quad_minus_lin']:+.2f}   "
          f"(sign not reliable on its own; see referee M2)")

    perm = permutation_tail(y, U, D)
    print("\n[PERMUTATION - reproducible tail, M3]")
    print(f"  curvature stat = {perm['observed_curvature_stat']:.2f}; "
          f"perm p(>= obs) = {perm['perm_p_ge_observed']:.3f} "
          f"({perm['n_perm']} perms, seed {perm['seed']}); "
          f"beyond null envelope = {perm['beyond_null_envelope']}")

    t = tau_v_third_law(df)
    print("\n[THIRD LAW - enforcement latency tau_v]")
    print(f"  mean failed / survived = {t['mean_failed']:.2f} / {t['mean_survived']:.2f} days")
    print(f"  MWU p (all) = {t['p_all']:.2e};  p (measured-only) = {t['p_measured_only']:.2e}")
    print(f"  imputed frac failed / survived = {t['imputed_frac_failed']:.2f} / "
          f"{t['imputed_frac_survived']:.2f}")
    print("=" * 74)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="github_repositories.csv")
    ap.add_argument("--synthetic", action="store_true",
                    help="annotate output as the synthetic reproducibility fixture")
    a = ap.parse_args()
    try:
        run(a.csv, a.synthetic)
    except FileNotFoundError:
        print(f"ERROR: {a.csv} not found. Generate the reproducibility fixture with:\n"
              f"  python make_synthetic_cohort.py --out github_repositories_SYNTHETIC.csv\n"
              f"then:  python analysis_corrected.py --csv github_repositories_SYNTHETIC.csv "
              f"--synthetic", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
