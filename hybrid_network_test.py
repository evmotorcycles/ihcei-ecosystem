#!/usr/bin/env python3
"""
hybrid_network_test.py
======================
Locked analysis for the Human-AI Hybrid Network Coupling Test (see
PREREGISTRATION_hybrid.md). Reads one CSV of human-AI task instances and returns a
verdict on H1 (coupling form) and H2 (binding-constraint / ceiling), under a VIF
gate, by a decision rule fixed in advance. This docstring is the analysis lock; the
script prints its SHA-256 at runtime.

>>> SPECULATIVE / NEW HYPOTHESIS. Not implied by the yeast or GitHub results. The
>>> test can confirm, disconfirm, or come back inconclusive; all are reportable.

INPUT CSV columns (one row per human-AI task instance):
    unit_id        identifier
    E              outcome 1=accepted & survived, 0=rejected/failed/reverted
    U              AI capability score for the model used (>=3 distinct tiers)
    D_enc_human    human encoding fidelity in [0,1]  (prompt specificity, INPUT side)
    D_dec_ai       AI decoding fidelity in [0,1]     (output retention, OUTPUT side)

GATE (channel-intact): VIF(D_enc_human, D_dec_ai) = 1/(1-r^2). If VIF >= 5 the two
hops are redundant -> BOTH H1 and H2 are INCONCLUSIVE.

H1 (coupling form): D_align = D_enc_human*D_dec_ai, min-max scaled to D_s.
    M_lin : logit(E)=b0+b1(U*D_s)   ;  M_quad: logit(E)=b0+b1(U*D_s^2)
    dAIC = AIC_lin - AIC_quad (>0 favours quadratic); permutation z on D_s (seed 42).
    Secondary nested on natural D_align: M0:U ; M1:U+D_align ; M2:U+D_align+D_align^2.

H2 (binding constraint): logit(E)=b0+b1*U+b2*D_align+b3*(U*D_align). Stratify by
D_align tercile; estimate the U->E slope (logit(E)~U) per tercile.

DECISION RULE (locked). Requires N>=500, minority class>=100, VIF<5.
  H1: QUADRATIC SUPPORTED iff dAIC>10 and z>3 ; LINEAR iff dAIC<=0 ; else INCONCLUSIVE.
  H2: BINDING-CONSTRAINT SUPPORTED iff the U*D_align interaction is positive and
      significant (b3>0, p<0.01) AND the high-D_align-tercile U-slope is positive (CI
      excludes 0) AND steeper than the low-tercile slope. REJECTED iff the interaction
      is not positive-significant AND U-slope is positive (CI excludes 0) in both
      terciles (capacity helps regardless of interface). Else INCONCLUSIVE.
"""

import sys, json, hashlib
import numpy as np
import pandas as pd
import statsmodels.api as sm

np.seterr(all="ignore")
SEED = 42
N_MIN, MINORITY_MIN, VIF_MAX = 500, 100, 5.0
T_DAIC, T_Z, T_INTERACTION_P = 10.0, 3.0, 0.01


def spec_hash():
    return hashlib.sha256(__doc__.encode()).hexdigest()


def aic(y, X):
    Xc = sm.add_constant(X, has_constant="add")
    try:
        return float(sm.Logit(y, Xc).fit(disp=0, maxiter=200).aic)
    except Exception:
        return float("nan")


def slope_ci(y, x):
    """U->E logistic slope and 95% CI within a stratum."""
    Xc = sm.add_constant(x, has_constant="add")
    try:
        m = sm.Logit(y, Xc).fit(disp=0, maxiter=200)
        ci = m.conf_int(alpha=0.05)
        return float(m.params[1]), float(ci[1][0]), float(ci[1][1])
    except Exception:
        return float("nan"), float("nan"), float("nan")


def run(csv_path):
    df = pd.read_csv(csv_path)
    need = {"E", "U", "D_enc_human", "D_dec_ai"}
    if not need.issubset(df.columns):
        sys.exit(f"CSV must contain columns {need}; got {list(df.columns)}")

    E = df["E"].astype(int).values
    U = df["U"].astype(float).values
    Dh = df["D_enc_human"].astype(float).values
    Da = df["D_dec_ai"].astype(float).values
    Dalign = Dh * Da
    n = len(df); minority = int(min(E.sum(), (1 - E).sum()))

    # ---- VIF gate ----
    r = float(np.corrcoef(Dh, Da)[0, 1]) if n > 2 else 0.0
    vif = 1.0 / (1.0 - r ** 2) if abs(r) < 0.9999 else float("inf")
    gate_ok = (n >= N_MIN) and (minority >= MINORITY_MIN) and (vif < VIF_MAX)

    # ---- H1: coupling form ----
    rng = Dalign.max() - Dalign.min()
    Ds = (Dalign - Dalign.min()) / rng if rng > 0 else Dalign * 0
    a_lin = aic(E, (U * Ds).reshape(-1, 1))
    a_quad = aic(E, (U * Ds ** 2).reshape(-1, 1))
    dAIC = a_lin - a_quad
    rg = np.random.default_rng(SEED); null = []
    for _ in range(1000):
        Dp = rg.permutation(Ds)
        al, aq = aic(E, (U * Dp).reshape(-1, 1)), aic(E, (U * Dp ** 2).reshape(-1, 1))
        if np.isfinite(al) and np.isfinite(aq):
            null.append(al - aq)
    z = float((dAIC - np.mean(null)) / max(np.std(null), 1e-9)) if null else 0.0
    a0 = aic(E, U.reshape(-1, 1))
    a1 = aic(E, np.column_stack([U, Dalign]))
    a2 = aic(E, np.column_stack([U, Dalign, Dalign ** 2]))

    if not gate_ok:
        h1 = "INCONCLUSIVE"; h1_why = (f"gate not met (N={n}>={N_MIN}? "
                                       f"minority={minority}>={MINORITY_MIN}? VIF={vif:.2f}<{VIF_MAX}?)")
    elif dAIC > T_DAIC and z > T_Z:
        h1 = "QUADRATIC_SUPPORTED"; h1_why = f"dAIC={dAIC:.2f}>10 and z={z:.2f}>3"
    elif dAIC <= 0:
        h1 = "LINEAR_quadratic_disconfirmed"; h1_why = f"dAIC={dAIC:.2f}<=0"
    else:
        h1 = "INCONCLUSIVE"; h1_why = f"weak: 0<dAIC={dAIC:.2f}<=10 or z={z:.2f}<=3"

    # ---- H2: binding constraint / ceiling ----
    # Primary signal = the U x D_align interaction: does U's marginal effect GROW with
    # interface fidelity? Stratified U-slopes (low vs high D_align tercile) illustrate it.
    inter = np.column_stack([U, Dalign, U * Dalign])
    Xc = sm.add_constant(inter, has_constant="add")
    try:
        mi = sm.Logit(E, Xc).fit(disp=0, maxiter=200)
        b3 = float(mi.params[3]); p_inter = float(mi.pvalues[3])
    except Exception:
        b3 = float("nan"); p_inter = float("nan")
    terc = pd.qcut(Dalign, 3, labels=["low", "mid", "high"], duplicates="drop")
    def stratum_slope(lab):
        m = (terc == lab)
        if m.sum() > 20 and 0 < E[m].mean() < 1:
            return slope_ci(E[m], U[m])
        return (float("nan"),) * 3
    lo, hi = stratum_slope("low"), stratum_slope("high")
    hi_pos = np.isfinite(hi[1]) and hi[1] > 0          # high-tercile U-slope CI excludes 0
    lo_pos = np.isfinite(lo[1]) and lo[1] > 0          # low-tercile  U-slope CI excludes 0
    ordered = np.isfinite(hi[0]) and np.isfinite(lo[0]) and hi[0] > lo[0]
    inter_pos_sig = np.isfinite(p_inter) and p_inter < T_INTERACTION_P and b3 > 0
    if not gate_ok:
        h2 = "INCONCLUSIVE"; h2_why = "gate not met"
    elif inter_pos_sig and hi_pos and ordered:
        h2 = "BINDING_CONSTRAINT_SUPPORTED"
        h2_why = (f"U×D_align interaction positive & significant (b3={b3:.2f}, p={p_inter:.3g}); "
                  f"U-slope steeper at high interface fidelity ({hi[0]:.2f}) than low ({lo[0]:.2f})")
    elif (not inter_pos_sig) and lo_pos and hi_pos:
        h2 = "BINDING_CONSTRAINT_REJECTED"
        h2_why = (f"interaction not positive-significant (b3={b3:.2f}, p={p_inter:.3g}); U-slope "
                  f"positive across low ({lo[0]:.2f}) and high ({hi[0]:.2f}) terciles — capacity helps regardless")
    else:
        h2 = "INCONCLUSIVE"; h2_why = f"interaction b3={b3:.2f} p={p_inter:.3g}; slopes low={lo[0]:.2f} high={hi[0]:.2f}"

    summary = {
        "spec_sha256": spec_hash(), "seed": SEED,
        "n": n, "minority": minority, "VIF": round(vif, 4), "pearson_Dh_Da": round(r, 4),
        "H1_dAIC_quad_minus_lin": round(dAIC, 3), "H1_permutation_z": round(z, 3),
        "H1_nested_dAIC_quad_vs_lin": round(a1 - a2, 3),
        "H1_verdict": h1, "H1_reason": h1_why,
        "H2_interaction_b3": (round(b3, 4) if np.isfinite(b3) else None),
        "H2_interaction_p": (round(p_inter, 5) if np.isfinite(p_inter) else None),
        "H2_U_slope_low_tercile": [round(v, 4) if np.isfinite(v) else None for v in lo],
        "H2_U_slope_high_tercile": [round(v, 4) if np.isfinite(v) else None for v in hi],
        "H2_verdict": h2, "H2_reason": h2_why,
    }
    summary["certificate_id"] = "HYBRID-" + hashlib.sha256(
        (spec_hash() + json.dumps(summary, sort_keys=True)).encode()).hexdigest()[:12].upper()

    print("=" * 68)
    print("Human-AI Hybrid Network Coupling Test")
    print(f"Spec SHA-256: {spec_hash()}")
    print("=" * 68)
    print(f"N={n}  minority={minority}  VIF(D_enc_human,D_dec_ai)={vif:.2f} (gate <{VIF_MAX})")
    print(f"H1 dAIC(quad-lin)={dAIC:+.2f}  z={z:+.2f}  nested dAIC={a1-a2:+.2f}")
    print(f"   H1 VERDICT: {h1}  ({h1_why})")
    print(f"H2 interaction b3={b3:+.2f} p={p_inter:.3g}  U-slope low={lo[0]:.2f} high={hi[0]:.2f}")
    print(f"   H2 VERDICT: {h2}  ({h2_why})")
    print(f"Certificate: {summary['certificate_id']}")
    with open("hybrid_network_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Summary -> hybrid_network_summary.json")
    print("=" * 68)
    return summary


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python hybrid_network_test.py <hybrid_tasks.csv>")
        print(f"\nlocked spec SHA-256: {spec_hash()}")
        print("required columns: unit_id, E, U, D_enc_human, D_dec_ai")
        sys.exit(0)
    run(sys.argv[1])
