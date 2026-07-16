#!/usr/bin/env python3
# ======================================================================
# gt_bger_test.py  —  E = U * D^k  on the Swiss Federal Supreme Court
# ----------------------------------------------------------------------
# Tests the GT exponent on D: is realized output better described by
#   linear   E = U * D   (k=1, the yeast/GitHub pattern)      vs
#   quadratic E = U * D^2 (k=2, the imposed engineering form)?
#
# HONEST SCOPE — read before trusting any number this prints:
#  * ONE-HOP.  This file has no opinion text, so D_enc is NOT computable;
#    D here is D_dec only (from `outcome`). This is NOT the two-hop D =
#    D_enc*D_dec test. For that you need the full-text SCALE / Swiss-
#    Judgment-Prediction corpus and a text-similarity D_enc.
#  * E is DERIVED.  Citation in-degree is built by inverting the outgoing
#    `cited_bger` lists over the whole corpus. It is a downstream-
#    influence proxy, weakly coupled to D (r~-0.16) and U (r~+0.39).
#  * D is COARSE (3 levels) and its POLARITY is a modelling choice. The
#    script sweeps both the granted-floor value and the U proxy so you
#    can see how sensitive k_hat is. Treat this as EXPLORATORY, not a
#    clean confirmatory third domain.
#
# Colab:  !python gt_bger_test.py /content/bger-2023-4.csv
# ======================================================================
import sys, re
import numpy as np, pandas as pd
import statsmodels.api as sm
from collections import Counter

PATH = sys.argv[1] if len(sys.argv) > 1 else "bger-2023-4.csv"

# ---------- load ----------
cols = ['docref','cited_bger','outcome','length','n_judges']
B = pd.read_csv(PATH, usecols=lambda c: c in cols, low_memory=False)
n0 = len(B)

# ---------- E: incoming citation in-degree (invert outgoing lists) ----------
def refs(x):
    return [] if not isinstance(x, str) or not x.strip() \
           else [t.strip() for t in re.split(r'[;,|]', x) if t.strip()]
indeg = Counter()
for lst in B['cited_bger'].map(refs):
    for r in lst: indeg[r] += 1
B['E'] = B['docref'].astype(str).map(lambda d: indeg.get(d, 0)).astype(float)

# ---------- D_dec from outcome (faithful decode = lower court upheld) ----------
# granted_floor is swept below; rejected/inadmissible = upheld = high fidelity.
def make_D(granted_floor):
    return B['outcome'].map({'rejected':1.0, 'inadmissible':1.0,
                             'partly granted':(1.0+granted_floor)/2,
                             'granted':granted_floor,
                             'writeoff':np.nan})

def fit_once(U_col, granted_floor, flip=False):
    D = make_D(granted_floor)
    if flip: D = 1.0 + granted_floor - D           # reverse polarity as a check
    U = pd.to_numeric(B[U_col], errors='coerce')
    df = pd.DataFrame({'E':B['E'], 'U':U, 'D':D}).dropna()
    df = df[(df['E'] > 0) & (df['U'] > 0) & (df['D'] > 0)]         # logs need >0
    df['U'] = df['U'] / df['U'].median()                          # scale U (k invariant)
    y  = np.log(df['E'])
    lU = np.log(df['U']); lD = np.log(df['D'])

    # (a) free-exponent OLS:  log E = a*log U + k*log D + c
    Xf = sm.add_constant(pd.DataFrame({'logU':lU, 'logD':lD}))
    mf = sm.OLS(y, Xf).fit()
    k_hat = mf.params['logD']; k_ci = mf.conf_int().loc['logD'].tolist()
    u_exp = mf.params['logU']

    # (b) constrained (U-exponent := 1):  y - logU = k*logD + c  -> AIC(k=1) vs AIC(k=2)
    yo = y - lU
    def aic_fixed(k):
        resid = yo - k*lD
        c = resid.mean(); rss = float(((resid - c)**2).sum()); nn = len(resid)
        return nn*np.log(rss/nn) + 2*1                    # +1 param (the intercept c)
    aic1, aic2 = aic_fixed(1.0), aic_fixed(2.0)
    return dict(U=U_col, floor=granted_floor, flip=flip, n=len(df),
                k_hat=k_hat, k_lo=k_ci[0], k_hi=k_ci[1], u_exp=u_exp,
                aic_lin=aic1, aic_quad=aic2, dAIC=aic2-aic1)

# ---------- sweep U proxy x granted-floor x polarity ----------
rows = []
for U_col in ['length','n_judges']:
    for gf in [0.10, 0.25]:
        rows.append(fit_once(U_col, gf, flip=False))
rows.append(fit_once('length', 0.10, flip=True))   # polarity sanity check
R = pd.DataFrame(rows)

pd.set_option('display.width', 170)
print("="*78)
print("E = U * D^k   |   Swiss Federal Supreme Court (BGer)   |   ONE-HOP (D=D_dec)")
print(f"rows loaded={n0:,}   E=citation in-degree   D from `outcome`   U as shown")
print("="*78)
show = R.copy()
for c in ['k_hat','k_lo','k_hi','u_exp','dAIC']: show[c]=show[c].round(2)
print(show[['U','floor','flip','n','k_hat','k_lo','k_hi','u_exp','dAIC']].to_string(index=False))

print("\nREADING:")
print(" k_hat = fitted exponent on D.  k~1 => linear E=U*D ;  k~2 => quadratic E=U*D^2.")
print(" u_exp = fitted exponent on U (want ~1 if the multiplicative-in-U form holds).")
print(" dAIC  = AIC(quadratic) - AIC(linear).  >0 favors LINEAR, <0 favors QUADRATIC.")

main = R[(R.U=='length') & (R.floor==0.10) & (~R.flip)].iloc[0]
lo, hi, ue = main['k_lo'], main['k_hi'], main['u_exp']
if lo <= 1 <= hi and not (lo <= 2 <= hi):
    verdict = "consistent with LINEAR  E = U*D"
elif lo <= 2 <= hi and not (lo <= 1 <= hi):
    verdict = "consistent with QUADRATIC  E = U*D^2"
elif hi < 0.5:
    verdict = ("NEITHER — D-exponent ~ 0: D_dec does not scale output here, so the "
               "multiplicative form E = U*D^k is NOT supported in this one-hop spec")
else:
    verdict = "INTERMEDIATE / INCONCLUSIVE exponent"
form = "" if 0.8 <= ue <= 1.2 else \
       f"\n     [also: U-exponent = {ue:.2f} != 1, so the U*(.) multiplicative form itself is not clean here]"
print(f"\nPRIMARY SPEC (U=length, granted_floor=0.10): "
      f"k_hat={main['k_hat']:.2f} [{lo:.2f},{hi:.2f}]  u_exp={ue:.2f}  dAIC={main['dAIC']:+.1f}")
print("  ->  " + verdict + form)
print("  NB: dAIC only compares k=1 vs k=2; when k_hat sits far from both, that horse-race")
print("      is the wrong question — read k_hat and its CI, not the dAIC label.")

print("\nCAVEATS (do not drop these when you write this up):")
print(" * ONE-HOP: no D_enc in this file, so this tests the exponent on D_dec only,")
print("   not the two-hop D=D_enc*D_dec. Get the full-text corpus for the real test.")
print(" * D has 3 levels; k_hat is identified only by across-outcome contrasts, so its")
print("   resolution is coarse — read the CI, and check the sweep rows for stability.")
print(" * E (in-degree) is a derived influence proxy, weakly coupled to D and U; the")
print("   polarity-flip row shows how much the D-definition drives the result.")
print(" * A LINEAR result extends the yeast/GitHub pattern; a QUADRATIC one would be")
print("   your first quadratic-favoring domain and would need the two-hop test to trust.")
print("="*78)
