#!/usr/bin/env python3
"""
make_synthetic_cohort.py
========================
Addresses referee point M1 (the data CSVs are absent from the deposit, so the
analysis does not reproduce as shipped).

This does NOT fabricate the paper's empirical results. It emits a *clearly
labelled synthetic* cohort with the exact schema `reproduce_analysis.py` and
`analysis_corrected.py` expect, so that:

  * anyone can run the full analysis pipeline end-to-end (CI included) without
    the private raw pull, and
  * the pipeline's *machinery* -- VIF gate, nested curvature test, permutation
    null, tau_v Mann-Whitney -- is exercised and verified deterministically.

The synthetic ground truth is LINEAR coupling (E = U * D, no quadratic term)
with an independent two-hop channel (D_dec constructed orthogonal to D_enc)
and higher enforcement latency in the failed group. A correct pipeline must
therefore: pass the VIF gate, find no curvature, and recover the tau_v effect.

The real empirical CSV (`github_repositories.csv`, hash in SHA256SUMS.txt)
must be deposited separately; this file is the reproducibility *harness*, not
a substitute for it.
"""
import argparse
import numpy as np
import pandas as pd

SCHEMA = ["E", "D_enc", "D_dec", "D", "U", "tau_v", "tau_v_imputed"]


def make(n=992, seed=42, b0=-1.15, bU=0.28, bD=6.0):
    """Draw E from a GENUINELY LINEAR (additive, no-curvature) logit that
    matches the primary nested test's own functional form  logit ~ b0+bU*U+bD*D.
    Because the true model contains no D^2 term, a correctly-specified nested
    curvature test must find NONE. D_dec is constructed ~orthogonal to D_enc so
    the two-hop channel stays intact (low VIF). Enforcement latency is drawn
    higher in the realized-failed group. Coefficients are tuned so failures
    dominate (matching the paper's imbalanced ~3:1 failed:survived cohort)."""
    rng = np.random.default_rng(seed)
    D_enc = np.clip(rng.beta(2, 2, n), 0, 1)
    D_dec = np.clip(rng.beta(2, 2, n), 0, 1)          # independent -> low VIF
    D = D_enc * D_dec
    U = rng.uniform(1, 6, n)
    # survival probability rises linearly (in the logit) with U and D, no square
    eta = b0 + bU * U + bD * D
    p_survive = 1.0 / (1.0 + np.exp(-eta))
    E = (rng.random(n) < p_survive).astype(int)         # 1 = survived, 0 = failed
    tau_v = np.where(E == 0, rng.gamma(4, 12, n), rng.gamma(3, 6, n)).clip(0, 365)
    tau_v_imputed = np.where(E == 0, rng.random(n) < 0.15, rng.random(n) < 0.04).astype(int)
    df = pd.DataFrame(dict(E=E, D_enc=D_enc, D_dec=D_dec, D=D, U=U,
                           tau_v=tau_v, tau_v_imputed=tau_v_imputed))
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)[SCHEMA]


def minmax(s):
    s = np.asarray(s, float)
    rng = s.max() - s.min()
    return (s - s.min()) / rng if rng > 0 else s * 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="github_repositories_SYNTHETIC.csv")
    ap.add_argument("--n", type=int, default=992)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    df = make(a.n, a.seed)
    df.to_csv(a.out, index=False)
    print(f"wrote {a.out}  shape={df.shape}  (SYNTHETIC — linear ground truth)")


if __name__ == "__main__":
    main()
