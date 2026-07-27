#!/usr/bin/env python3
"""
test_sovereign_mesh_telemetry.py
================================
Pytest suite verifying the Sovereign Mesh telemetry using JAX and float64 precision.
Evaluates shock vulnerability, structural risk-sharing ratios, and epistemic
demand index against the generated sovereign mesh datasets.
"""

import os
import sys
import jax
import jax.numpy as jnp
import pandas as pd
import numpy as np
import pytest

# Add current directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Strict Layer-1 Epistemic Firewall
jax.config.update("jax_enable_x64", True)
np.seterr(all='raise')

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'financial-system')

def safe_masked_mean(mask: jnp.ndarray, values: jnp.ndarray) -> float:
    """JAX-vectorized mean computation that prevents division by zero."""
    count = jnp.sum(mask)
    return float(jnp.sum(jnp.where(mask, values, 0.0)) / jnp.maximum(count, 1))

def test_banking_dataset_shock_vulnerability():
    """
    Exp 1: Evaluate banking dataset shock vulnerability.
    Checks the proportion of high-risk debits (>30% of account balance).
    """
    filepath = os.path.join(DATA_DIR, 'banking_dataset.xlsx')
    assert os.path.exists(filepath), f"Missing dataset: {filepath}"

    df_banking = pd.read_excel(filepath)
    df_debits = df_banking[df_banking['Transaction Type'] == 'Debit'].dropna(subset=['Transaction Amount', 'Account Balance'])
    df_debits = df_debits[df_debits['Account Balance'] > 0]

    debit_amounts = jnp.array(df_debits['Transaction Amount'].values, dtype=jnp.float64)
    balances = jnp.array(df_debits['Account Balance'].values, dtype=jnp.float64)

    risk_ratios = debit_amounts / balances
    high_risk_mask = risk_ratios > 0.30

    total_debits = len(debit_amounts)
    high_risk_debits = int(jnp.sum(high_risk_mask))
    rate = (high_risk_debits / total_debits) * 100.0 if total_debits > 0 else 0.0

    # Assert that some vulnerability is detected, proving the engine works
    assert high_risk_debits > 0
    assert rate > 5.0 # We generated about 400 high risk out of ~4900 debits

def test_ifsb_financial_statements_risk_sharing():
    """
    Exp 2: Evaluate IFSB financial statements (Risk-Sharing vs Derivative).
    """
    filepath = os.path.join(DATA_DIR, 'DETAILED_FINANCIAL_STATEMENTS_202508040700.xlsx')
    assert os.path.exists(filepath), f"Missing dataset: {filepath}"

    ifsb_df = pd.read_excel(filepath, header=None)
    desc_str = ifsb_df[6].astype(str).str.lower()

    musharakah_mask = desc_str.str.contains('mudarabah|musharakah', na=False)
    derivative_mask = desc_str.str.contains('derivative', na=False)

    ifsb_df[9] = pd.to_numeric(ifsb_df[9], errors='coerce').fillna(0.0)
    ifsb_df[10] = pd.to_numeric(ifsb_df[10], errors='coerce').fillna(0.0)

    jnp_data_9 = jnp.array(ifsb_df[9].values, dtype=jnp.float64)
    jnp_data_10 = jnp.array(ifsb_df[10].values, dtype=jnp.float64)
    jnp_musharakah_mask = jnp.array(musharakah_mask.values, dtype=jnp.bool_)
    jnp_derivative_mask = jnp.array(derivative_mask.values, dtype=jnp.bool_)

    jnp_values = jnp.stack([jnp_data_9, jnp_data_10], axis=1)

    musharakah_funding = float(jnp.sum(jnp.where(jnp_musharakah_mask[:, None], jnp_values, 0.0)))
    derivative_exposures = float(jnp.sum(jnp.where(jnp_derivative_mask[:, None], jnp_values, 0.0)))

    risk_sharing_ratio = musharakah_funding / derivative_exposures if derivative_exposures != 0 else 0.0

    # The generation script ensures some representation of both
    assert musharakah_funding > 0
    assert derivative_exposures > 0
    assert risk_sharing_ratio > 0

def test_kenya_microfinance_epistemic_demand():
    """
    Exp 3: Evaluate Kenya microfinance epistemic demand index.
    """
    filepath = os.path.join(DATA_DIR, 'Islamic microfinance services feasibility study-Kenya.xlsx')
    assert os.path.exists(filepath), f"Missing dataset: {filepath}"

    df_kenya = pd.read_excel(filepath, header=None)
    df_kenya_str = df_kenya.astype(str).apply(lambda x: ' '.join(x), axis=1).str.lower()
    total_responses = len(df_kenya)

    demand_mask = df_kenya_str.str.contains('interest-free|interest free|religious compliance|no interest', na=False)
    jnp_demand_mask = jnp.array(demand_mask.values, dtype=jnp.bool_)
    interest_free_demand = int(jnp.sum(jnp_demand_mask))

    epistemic_demand_index = (interest_free_demand / total_responses) * 100.0 if total_responses > 0 else 0.0

    assert total_responses == 507
    assert interest_free_demand == 55
    assert abs(epistemic_demand_index - 10.848) < 0.1

def test_meezan_dataset_lism_telemetry():
    """
    Exp 4 & LISM Proof: Evaluate Meezan dataset topological efficiency
    and counterfactual simulation.
    """
    filepath = os.path.join(DATA_DIR, 'meezan_international_transactions (1).csv')
    assert os.path.exists(filepath), f"Missing dataset: {filepath}"

    df = pd.read_csv(filepath)
    df = df.rename(columns={
        'Contract_Type': 'Contract_Type',
        'Processing_Time_Seconds': 'Processing_Time',
        'Risk_Score': 'HOPS',
        'Fee_Charged': 'Fee'
    })

    valid_contracts = ['Ijara', 'Murabaha', 'Salam']
    df_mesh = df[df['Contract_Type'].isin(valid_contracts)].dropna(subset=['HOPS', 'Processing_Time', 'Fee']).copy()

    mesh_hops = jnp.array(df_mesh['HOPS'].values, dtype=jnp.float64)
    mesh_time = jnp.array(df_mesh['Processing_Time'].values, dtype=jnp.float64)
    mesh_fee = jnp.array(df_mesh['Fee'].values, dtype=jnp.float64)

    D = 0.95
    D_min = 0.50

    mesh_fidelity = D ** mesh_hops
    mesh_breach = int(jnp.sum(mesh_fidelity < D_min))
    mesh_breach_rate = float((mesh_breach / len(mesh_hops)) * 100.0)

    # Generate deterministic synthetic conventional counterfactual
    key = jax.random.PRNGKey(42)
    n_synthetic = len(mesh_hops)
    key, subkey_hops = jax.random.split(key)
    normal_samples = jax.random.normal(subkey_hops, shape=(n_synthetic,)) * 0.7 + 1.6
    synth_hops = jnp.clip(jnp.round(jnp.exp(normal_samples)), 1, 40).astype(jnp.float64)

    key, subkey_time = jax.random.split(key)
    synth_time = jnp.clip(62.5 + (synth_hops * 12.0) + jax.random.normal(subkey_time, shape=(n_synthetic,)) * 5.0, 10.0, None)

    synth_fidelity = D ** synth_hops
    synth_breach = int(jnp.sum(synth_fidelity < D_min))
    synth_breach_rate = float((synth_breach / n_synthetic) * 100.0)

    assert len(mesh_hops) > 0
    assert jnp.mean(mesh_hops) > 0
    assert mesh_breach_rate > 0
    assert synth_breach_rate > 0
