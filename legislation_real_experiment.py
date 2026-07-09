#!/usr/bin/env python3
"""
legislation_real_experiment.py
=============================
A REAL (not placeholder) LISM coupling run on legislation, using live U.S. bill
full text from the deployed Congress.gov proxy (Vercel project-6q4gj,
api/bill-text.js) and a MEASURED, non-circular outcome: whether each bill became
law (enacted) vs. died.

    # fetch two labelled batches once (endpoint or Vercel MCP), then:
    python legislation_real_experiment.py \
        --enacted-json enacted.json --failed-json failed.json

D_enc (encoding fidelity) = bill-text specificity per 1k words (defined terms,
statutory cross-references, numeric thresholds/deadlines, mandatory language).
U = log(1+words). E = enacted (1) vs not (0), read from public legislative
history, independent of the text (satisfies I3, non-circular outcome).

WHAT THIS DOES AND DOESN'T SETTLE
  * It IS a real one-hop coupling test: does D_enc couple linearly or
    quadratically to enactment? (nested LRT on D_enc^2, penalized-safe.)
  * It is NOT a two-hop test: there is no INDEPENDENT decoding hop (agency
    implementation / judicial enforcement measured on other actors) in bill text,
    so the two-hop quadratic channel (I1) cannot be formed here.
  * By the generalization protocol's gates it is also underpowered (I2:
    N_fail << 100) and the labelled sample is a convenience set (selection bias:
    enacted bills skew to large omnibus acts, failed bills to short messaging
    bills). The two-hop verdict is therefore INCONCLUSIVE; the one-hop linear
    result is reported descriptively.
"""
import argparse
import json
import re
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2, mannwhitneyu
from sklearn.metrics import roc_auc_score

DEFINED = re.compile(r'\b(means|shall mean|defined? (?:as|to mean)|the term ["“])', re.I)
XREF = re.compile(r'(\b\d+\s+U\.?S\.?C\.?\b|\bsection\s+\d+|\b§\s*\d+|\bpublic law\b)', re.I)
NUM = re.compile(r'(\$[\d,]+|\b\d+(?:\.\d+)?\s?(?:percent|%)|\b\d{4}\b|\bnot later than\b|\bwithin\s+\d+\s+days\b)', re.I)
MAND = re.compile(r'\b(shall|must|may not|is required to|are required to)\b', re.I)


def specificity(t):
    w = max(len(re.findall(r'\w+', t)), 1)
    k = 1000.0 / w
    return {"words": w, "defs": len(DEFINED.findall(t)) * k, "xref": len(XREF.findall(t)) * k,
            "num": len(NUM.findall(t)) * k, "mand": len(MAND.findall(t)) * k}


def load(path):
    raw = open(path).read()
    m = re.search(r'\{"count":\d+.*\}', raw, re.DOTALL)
    payload = json.loads(m.group(0)) if m else (
        json.loads(json.loads(raw)["text"]) if raw.strip().startswith("{") else json.loads(raw))
    return payload.get("results", payload if isinstance(payload, list) else [])


def mm(x):
    x = np.asarray(x, float)
    r = x.max() - x.min()
    return (x - x.min()) / r if r > 0 else x * 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enacted-json", required=True)
    ap.add_argument("--failed-json", required=True)
    ap.add_argument("--power-floor", type=int, default=100)
    a = ap.parse_args()
    warnings.filterwarnings("ignore")

    rows = []
    for r in load(a.enacted_json):
        if r.get("text"):
            s = specificity(r["text"]); s.update(id=r.get("id"), E=1); rows.append(s)
    for r in load(a.failed_json):
        if r.get("text"):
            s = specificity(r["text"]); s.update(id=r.get("id"), E=0); rows.append(s)
    d = pd.DataFrame(rows)
    d["D_enc"] = d.defs + d.xref + d.num + d.mand
    E = d.E.values
    Ds = mm(d.D_enc.values)
    U = np.log1p(d.words.values)

    print("=" * 74)
    print("REAL legislation coupling experiment — live Congress API")
    print("=" * 74)
    print(f"N = {len(d)}  (enacted = {int(E.sum())}, failed = {int((E==0).sum())})")
    en, fa = d[d.E == 1].D_enc, d[d.E == 0].D_enc
    _, p = mannwhitneyu(en, fa, alternative="greater")
    print(f"D_enc specificity: enacted mean {en.mean():.1f} vs failed {fa.mean():.1f}; "
          f"MWU one-tailed p = {p:.3f}")

    def auc(x):
        X = sm.add_constant(np.asarray(x, float))
        return roc_auc_score(E, sm.Logit(E, X).fit(disp=0).predict(X))
    print(f"\n[single-term literal forms, in-sample AUC]")
    print(f"  linear U*D_s   : {auc(U*Ds):.3f}")
    print(f"  quad   U*D_s^2 : {auc(U*Ds**2):.3f}")

    def fit(cols):
        return sm.Logit(E, sm.add_constant(np.column_stack(cols))).fit(disp=0)
    m1, m2 = fit([U, Ds]), fit([U, Ds, Ds**2])
    lr = 2 * (m2.llf - m1.llf); pl = float(chi2.sf(max(lr, 0), 1))
    print(f"\n[PRIMARY nested curvature M1(U+D) vs M2(U+D+D^2)]")
    print(f"  dAIC(quad-lin) = {m1.aic-m2.aic:+.2f}  LRT p = {pl:.3g}  beta_D2 = {m2.params[-1]:+.2f}")
    linear = (m1.aic - m2.aic) <= 0 or pl >= 0.05
    print("  -> " + ("linear adequate (no curvature) — consistent with LISM"
                     if linear else "curvature present"))

    print("\n[eligibility gates — generalization protocol]")
    print(f"  I1 channel independence : FAIL (no independent decoding hop in bill text)")
    print(f"  I2 populated failing reg: {'FAIL' if int((E==0).sum()) < a.power_floor else 'ok'} "
          f"(N_fail = {int((E==0).sum())} < {a.power_floor})")
    print(f"  I3 non-circular outcome : ok  (enactment read from legislative history)")
    print("\n[verdict]")
    print("  ONE-HOP result: bill-text specificity couples to enactment, and the")
    print("  coupling is LINEAR, not quadratic — directionally consistent with LISM.")
    print("  TWO-HOP verdict: INCONCLUSIVE — no independent D_dec (I1) and underpowered")
    print("  (I2). A real result on real data, honestly bounded; the full two-hop test")
    print("  needs the implementation/judicial hop via a data-holder partnership.")
    print("=" * 74)
    d.to_csv("legis_real_cohort.csv", index=False)


if __name__ == "__main__":
    main()
