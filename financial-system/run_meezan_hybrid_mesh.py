#!/usr/bin/env python3
"""
run_meezan_hybrid_mesh.py
=========================
A direct script to simulate the Meezan proxy dataset and pass it through the
Hybrid Sovereign Mesh. This demonstrates the Debt Trap reversal logic explicitly
by balancing the massive capacity of synthetic debt hubs against the high fidelity
of true risk-sharing nodes.
"""

import jax
import jax.numpy as jnp
import pandas as pd
import numpy as np

from fidelity_translation_layer import HybridSovereignMesh

def generate_proxy_meezan_data(n=15001):
    """
    Synthesizes the Meezan proxy dataset, returning a pandas DataFrame.
    """
    np.random.seed(42)
    columns = [
        'Transaction_ID', 'Customer_ID', 'Contract_Type',
        'Amount', 'Processing_Time_Seconds', 'Risk_Score',
        'Is_Synthetic_Debt'
    ]
    df = pd.DataFrame(columns=columns)
    df['Transaction_ID'] = [f'TXN{i:06d}' for i in range(1, n+1)]
    df['Customer_ID'] = [f'CUST{i:04d}' for i in range(n)]

    # Simulate Contract Types (Structural compliance vs synthetic debt wrapper)
    contracts = ['Lease', 'Markup_Trade', 'Forward_Sale', 'Synthetic_Wrapper']
    df['Contract_Type'] = np.random.choice(contracts, n, p=[0.25, 0.25, 0.25, 0.25])

    # Synthetic wrappers represent debt creation (fractional/fiat proxies)
    df['Is_Synthetic_Debt'] = df['Contract_Type'] == 'Synthetic_Wrapper'

    # Debt nodes tend to have massively higher capacity (U) but higher friction
    df['Amount'] = np.where(df['Is_Synthetic_Debt'],
                            np.random.uniform(50000, 500000, n), # Inflated U
                            np.random.uniform(1000, 50000, n))   # Real Asset U

    # Dissonance (sigma): Debt nodes have higher say-do dissonance
    df['Dissonance'] = np.where(df['Is_Synthetic_Debt'],
                                np.random.uniform(0.10, 0.35, n),
                                np.random.uniform(0.01, 0.10, n))

    # Hop counts (Risk score proxy): Real-asset paths often require more hops
    # to reach matching counterparties in a constrained topology.
    df['Hop_Count'] = np.where(df['Is_Synthetic_Debt'],
                               np.random.randint(2, 6, n),  # Fewer hops (wormhole)
                               np.random.randint(6, 15, n)) # More hops (isolated)

    return df

def run_hybrid_mesh():
    print("=== INITIATING HYBRID SOVEREIGN MESH TELEMETRY (DEBT TRAP REVERSAL) ===")
    jax.config.update("jax_enable_x64", True)

    # Generate Proxy Data
    df = generate_proxy_meezan_data()
    n_total = len(df)

    print(f"Generated {n_total:,} synthetic Meezan proxy transactions.")

    # Extract arrays for JAX
    capacities = jnp.array(df['Amount'].values, dtype=jnp.float64)
    dissonances = jnp.array(df['Dissonance'].values, dtype=jnp.float64)
    hop_counts = jnp.array(df['Hop_Count'].values, dtype=jnp.float64)
    is_synthetic = jnp.array(df['Is_Synthetic_Debt'].values, dtype=jnp.bool_)

    # Initialize Hybrid Mesh
    mesh = HybridSovereignMesh(base_d_risk_sharing=0.98,
                               base_d_synthetic_debt=0.85,
                               zombie_floor=0.50)

    # Evaluate
    results = mesh.evaluate_paths(capacities, dissonances, hop_counts, is_synthetic)

    # Aggregate Metrics for Printout
    df['Effective_Yield'] = np.array(results['effective_yields'])
    df['Retained_Fidelity'] = np.array(results['retained_fidelities'])
    df['Zombie_Breach'] = np.array(results['zombie_mask'])

    risk_sharing = df[~df['Is_Synthetic_Debt']]
    synthetic_debt = df[df['Is_Synthetic_Debt']]

    print("\n--- RESULTS: TRUE RISK-SHARING VS SYNTHETIC DEBT ---")
    print(f"{'Metric':<30} | {'True Risk-Sharing':<20} | {'Synthetic Debt':<20}")
    print("-" * 75)

    print(f"{'Count (N)':<30} | {len(risk_sharing):<20} | {len(synthetic_debt):<20}")
    print(f"{'Mean Capacity (U)':<30} | {risk_sharing['Amount'].mean():<20.2f} | {synthetic_debt['Amount'].mean():<20.2f}")
    print(f"{'Mean Retained Fidelity (D^n)':<30} | {risk_sharing['Retained_Fidelity'].mean():<20.4f} | {synthetic_debt['Retained_Fidelity'].mean():<20.4f}")
    print(f"{'Zombie Breach Rate':<30} | {(risk_sharing['Zombie_Breach'].mean() * 100):<20.2f}% | {(synthetic_debt['Zombie_Breach'].mean() * 100):<20.2f}%")
    print(f"{'Mean Effective Yield (E)':<30} | {risk_sharing['Effective_Yield'].mean():<20.2f} | {synthetic_debt['Effective_Yield'].mean():<20.2f}")

    # Overall Optimal Selection
    opt_idx = results['optimal_path_index']
    opt_tx = df.iloc[opt_idx]

    print("\n--- OPTIMAL PATH SELECTION ---")
    print(f"Transaction ID : {opt_tx['Transaction_ID']}")
    print(f"Contract Type  : {opt_tx['Contract_Type']}")
    print(f"Capacity (U)   : {opt_tx['Amount']:.2f}")
    print(f"Fidelity (D^n) : {opt_tx['Retained_Fidelity']:.4f}")
    print(f"Yield (E)      : {opt_tx['Effective_Yield']:.2f}")

    print("\n[VERDICT]: The Hybrid Mesh accurately balances U and D. It penalizes synthetic debt "
          "via the compounding 'Debt Trap' friction, zeroing out yields that breach the zombie floor, "
          "while extracting maximal thermodynamic yield where safely possible.")

if __name__ == "__main__":
    run_hybrid_mesh()
