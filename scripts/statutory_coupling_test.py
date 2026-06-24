#!/usr/bin/env python3
"""
statutory_coupling_test.py
==========================
Replication script for the GT v18.0 Statutory Coupling Test.

Domain: US public laws (104th-114th Congress, 1995-2015)
N: 365 usable enacted laws with resolved USC citations and classified durability outcomes
Verdict: QUADRATIC DISCONFIRMED (ΔAIC = -10.03, VIF = 1.002)

LOCKED OPERATIONALIZATION (declared before any model was fitted):
  D_enc = log1p(n_distinct_USC_sections_cited), min-max normalized [0,1]
  D_dec = log1p(n_SCOTUS_cases + n_noncommemorative_EOs per congress × pap_majortopic),
          min-max normalized [0,1]
  U = 1 (constant; enacted laws conditioned on enactment)
  D_s = D_enc × D_dec, then min-max scaled [0,1]
  M_lin:  logit(P(durable)) = b0 + b1 * D_s
  M_quad: logit(P(durable)) = b0 + b1 * D_s²
  VIF = 1/(1-r²), r = Pearson(D_enc, D_dec); gate: VIF < 5
  ΔAIC = AIC(M_lin) - AIC(M_quad)  [>0 favors quad; ≤0 favors linear]
  Permutation: 1000 shuffles of D_s, seed 42

DECISION RULE (pre-committed, two-directional):
  QUADRATIC SUPPORTED:      ΔAIC > 10 AND permutation z > 3
  QUADRATIC DISCONFIRMED:   ΔAIC ≤ 0
  INCONCLUSIVE:             VIF ≥ 5, or 0 < ΔAIC ≤ 10

DATA SOURCES (US Policy Agendas Project / Comparative Agendas):
  - Congressional Bills (CBP): bill_id, plaw_no, outcome classification
  - Public Laws: public_law_no, congress, pap_majortopic
  - Supreme Court Cases: congress, pap_majortopic (10,236 cases)
  - Executive Orders: congress, pap_majortopic, commemorative flag (4,831 orders)
  - USC repeal table: constructed from nickvido/us-code GitHub repo
"""

import re
import sys
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss


# ─── Data loading helpers ────────────────────────────────────────────────────

def norm_id(s):
    return re.sub(r'[^A-Z0-9]', '', str(s).upper())

def dash_to_int(s):
    """Convert '104-110' to 104110 to match public_law_no integer format."""
    parts = str(s).split('-')
    if len(parts) == 2:
        try:
            return int(parts[0]) * 1000 + int(parts[1])
        except ValueError:
            return None
    return None


def load_sample(bills_csv, laws_csv, usc_repeal_json, outcome_records_json):
    """
    Build the 365-law sample with:
      - n_citations: number of distinct USC sections cited (for D_enc)
      - E: durability outcome (1=durable, 0=repealed within 10yr window)
      - plaw_int: public_law_no integer for joining to downstream datasets
      - congress, pap_majortopic: for joining SCOTUS/EO counts

    See FALSIFIABILITY_LEDGER.md §Statutory for full provenance.
    """
    import json

    bills = pd.read_csv(bills_csv, low_memory=False)
    bills['bid_norm'] = bills['bill_id'].apply(norm_id)
    plawno_map = dict(zip(bills['bid_norm'], bills['plaw_no']))

    pl = pd.read_csv(laws_csv, low_memory=False, encoding='latin1')
    pl['plaw_int'] = pd.to_numeric(pl['public_law_no'], errors='coerce').astype('Int64')

    with open(outcome_records_json) as f:
        records = json.load(f)

    df = pd.DataFrame(records)
    df['plaw_no'] = df['bid_norm'].map(plawno_map)
    df['plaw_int'] = df['plaw_no'].apply(dash_to_int)

    df = df.merge(
        pl[['plaw_int', 'congress', 'pap_majortopic']],
        on='plaw_int', how='left'
    )
    return df


def attach_downstream_signals(df, scotus_csv, eo_csv):
    """
    Compute D_dec signals:
      n_scotus: SCOTUS cases per congress × pap_majortopic
      n_eo:     non-commemorative EOs per congress × pap_majortopic
    """
    sc = pd.read_csv(scotus_csv, low_memory=False, encoding='latin1')
    eo = pd.read_csv(eo_csv, low_memory=False, encoding='latin1')

    sc_counts = (sc.groupby(['congress', 'pap_majortopic'])
                   .size().reset_index(name='n_scotus'))

    eo_sub = eo[eo['commemorative'].fillna(0) == 0].copy()
    eo_counts = (eo_sub.groupby(['congress', 'pap_majortopic'])
                        .size().reset_index(name='n_eo'))

    for df_counts in (sc_counts, eo_counts):
        df_counts['congress'] = pd.to_numeric(df_counts['congress'], errors='coerce')
        df_counts['pap_majortopic'] = pd.to_numeric(df_counts['pap_majortopic'], errors='coerce')

    df['congress_int'] = pd.to_numeric(df['congress'], errors='coerce')
    df['topic_int'] = pd.to_numeric(df['pap_majortopic'], errors='coerce')

    df = df.merge(sc_counts, left_on=['congress_int', 'topic_int'],
                  right_on=['congress', 'pap_majortopic'], how='left',
                  suffixes=('', '_sc'))
    df = df.merge(eo_counts, left_on=['congress_int', 'topic_int'],
                  right_on=['congress', 'pap_majortopic'], how='left',
                  suffixes=('', '_eo'))

    df['n_scotus'] = df['n_scotus'].fillna(0)
    df['n_eo'] = df['n_eo'].fillna(0)
    return df


# ─── Core pipeline ───────────────────────────────────────────────────────────

def operationalize(df):
    """Compute normalized D_enc, D_dec, D_s."""
    df = df.copy()

    raw_enc = np.log1p(df['n_citations'].values)
    df['D_enc'] = (raw_enc - raw_enc.min()) / (raw_enc.max() - raw_enc.min() + 1e-12)

    raw_dec = np.log1p(df['n_scotus'].values + df['n_eo'].values)
    df['D_dec'] = (raw_dec - raw_dec.min()) / (raw_dec.max() - raw_dec.min() + 1e-12)

    raw_ds = df['D_enc'].values * df['D_dec'].values
    df['D_s'] = (raw_ds - raw_ds.min()) / (raw_ds.max() - raw_ds.min() + 1e-12)

    return df


def vif_gate(D_enc, D_dec):
    r, p = pearsonr(D_enc, D_dec)
    vif = 1 / (1 - r**2)
    return r, p, vif


def aic_comparison(D_s, E, seed=42, n_perm=1000):
    D_lin  = D_s.reshape(-1, 1)
    D_quad = (D_s ** 2).reshape(-1, 1)

    kw = dict(C=1e9, max_iter=2000, solver='lbfgs')
    lr_lin  = LogisticRegression(**kw).fit(D_lin,  E)
    lr_quad = LogisticRegression(**kw).fit(D_quad, E)

    ll_lin  = -log_loss(E, lr_lin.predict_proba(D_lin),   normalize=False)
    ll_quad = -log_loss(E, lr_quad.predict_proba(D_quad), normalize=False)

    aic_lin  = -2 * ll_lin  + 2 * 2
    aic_quad = -2 * ll_quad + 2 * 2
    delta = aic_lin - aic_quad  # >0 favors quad; ≤0 favors linear

    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_perm):
        Dp = rng.permutation(D_s)
        lr_pl = LogisticRegression(**kw).fit(Dp.reshape(-1, 1), E)
        lr_pq = LogisticRegression(**kw).fit((Dp**2).reshape(-1, 1), E)
        ll_pl = -log_loss(E, lr_pl.predict_proba(Dp.reshape(-1, 1)), normalize=False)
        ll_pq = -log_loss(E, lr_pq.predict_proba((Dp**2).reshape(-1, 1)), normalize=False)
        null.append((-2*ll_pl + 4) - (-2*ll_pq + 4))
    null = np.array(null)
    z = (delta - null.mean()) / null.std()
    p_val = (null >= delta).mean()

    return aic_lin, aic_quad, delta, z, p_val


def apply_verdict(vif, delta_aic, perm_z):
    if vif >= 5:
        return 'INCONCLUSIVE', f'VIF={vif:.3f} ≥ 5 — channel collapsed'
    if delta_aic > 10 and perm_z > 3:
        return 'QUADRATIC SUPPORTED', f'ΔAIC={delta_aic:.2f} > 10, z={perm_z:.2f} > 3'
    if delta_aic <= 0:
        return 'QUADRATIC DISCONFIRMED', f'ΔAIC={delta_aic:.2f} ≤ 0 — linear wins'
    return 'INCONCLUSIVE', f'ΔAIC={delta_aic:.2f} in grey zone (0, 10]'


# ─── Main ────────────────────────────────────────────────────────────────────

def run(bills_csv, laws_csv, scotus_csv, eo_csv,
        usc_repeal_json='data/usc_repeal_table.json',
        outcome_records_json='data/FINAL_records.json'):

    print('=' * 66)
    print('GT v18.0 Statutory Coupling Test — Replication Run')
    print('=' * 66)

    df = load_sample(bills_csv, laws_csv, usc_repeal_json, outcome_records_json)
    df = attach_downstream_signals(df, scotus_csv, eo_csv)
    df = operationalize(df)

    E = df['E'].values.astype(int)
    n_fail = (E == 0).sum()
    print(f'N = {len(df)}  |  E=1 (durable): {E.sum()}  |  E=0 (repealed): {n_fail}')

    if n_fail < 100:
        print(f'N_fail gate not cleared ({n_fail} < 100). INCONCLUSIVE.')
        return

    # VIF gate
    r, p_r, vif = vif_gate(df['D_enc'].values, df['D_dec'].values)
    print(f'\nVIF gate: r={r:.4f}  p={p_r:.4f}  VIF={vif:.4f}  '
          f'=> {"PASS" if vif < 5 else "FAIL"}')

    if vif >= 5:
        print('VERDICT: INCONCLUSIVE (channel collapsed)')
        return

    # AIC comparison
    aic_lin, aic_quad, delta, z, p_perm = aic_comparison(df['D_s'].values, E)
    print(f'\nAIC(M_lin)  = {aic_lin:.2f}')
    print(f'AIC(M_quad) = {aic_quad:.2f}')
    print(f'ΔAIC        = {delta:.2f}')
    print(f'Permutation z = {z:.2f}  p = {p_perm:.3f}')

    verdict, reason = apply_verdict(vif, delta, z)
    print(f'\n{"=" * 66}')
    print(f'VERDICT: {verdict}')
    print(f'Reason:  {reason}')
    print('=' * 66)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bills',  default='data/congressional_bills.csv')
    parser.add_argument('--laws',   default='data/public_laws.csv')
    parser.add_argument('--scotus', default='data/supreme_court_cases.csv')
    parser.add_argument('--eo',     default='data/executive_orders.csv')
    args = parser.parse_args()
    run(args.bills, args.laws, args.scotus, args.eo)