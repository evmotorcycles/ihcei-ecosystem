#!/usr/bin/env python3
"""
biomedical_VIF_simulator.py
===========================
Simulates a multi-hop cellular signaling pathway to demonstrate target
orthogonality (VIF) and how to design non-redundant combination therapies.

This models a signaling channel mapping to the LISM network construct:
  U     = target capacity / connectivity
  D_enc = local pathway signaling fidelity (e.g. receptor sorting)
  D_dec = global downstream pathway (e.g. transcription factor spread)

A high VIF (Variance Inflation Factor) indicates two targets are collinear
(redundant) - targeting both is capacity hoarding.
A low VIF (~1.0) indicates orthogonal (independent) targets, enabling
synergistic non-redundant combination therapy.
"""

import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

def simulate_signaling_targets(n_cells=1000, seed=42):
    """
    Simulate expression and signaling efficiency for N cells.
    Generates two orthogonal pathways and two collinear pathways.
    """
    rng = np.random.default_rng(seed)

    # Pathway A (e.g., MAPK-like)
    U_A = rng.uniform(0, 100, n_cells)
    D_enc_A = np.clip(rng.normal(0.6, 0.1, n_cells), 0, 1)
    D_dec_A = np.clip(rng.normal(0.6, 0.1, n_cells), 0, 1)

    # Pathway B (Orthogonal to Pathway A, e.g., PI3K-like)
    D_enc_B = np.clip(rng.normal(0.5, 0.15, n_cells), 0, 1)

    # Collinear/Redundant target to Pathway A
    # Shares 80% of variance with D_enc_A
    D_enc_A_redundant = 0.8 * D_enc_A + 0.2 * rng.normal(0.6, 0.1, n_cells)

    df = pd.DataFrame({
        'D_enc_PathwayA': D_enc_A,
        'D_dec_PathwayA': D_dec_A,
        'D_enc_PathwayB_Orthogonal': D_enc_B,
        'D_enc_PathwayA_Redundant': D_enc_A_redundant
    })

    return df

def calculate_vif(df, features):
    """Calculates VIF for a set of features in a DataFrame."""
    X = df[features]
    X = add_constant(X)
    vifs = [variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])]
    return dict(zip(features, vifs))

def main():
    print("="*60)
    print(" Biomedical Target Orthogonality Simulator (VIF) ")
    print("="*60)

    df = simulate_signaling_targets(n_cells=1000)

    # Test 1: Orthogonal Combination Therapy
    features_orthogonal = ['D_enc_PathwayA', 'D_enc_PathwayB_Orthogonal']
    vif_ortho = calculate_vif(df, features_orthogonal)

    print("\nTest 1: Orthogonal Targets (Combination Therapy Candidate)")
    print(f"Targets: {features_orthogonal}")
    for k, v in vif_ortho.items():
        print(f"  {k} VIF: {v:.4f}")

    avg_vif = np.mean(list(vif_ortho.values()))
    if avg_vif < 1.10:
        print("-> SUCCESS: Targets are independent (VIF ~ 1.0). "
              "Synergistic combination therapy is viable.")
    else:
        print("-> FAILURE: Targets show unexpected collinearity.")

    # Test 2: Redundant Targets (Capacity Hoarding)
    features_redundant = ['D_enc_PathwayA', 'D_enc_PathwayA_Redundant']
    vif_red = calculate_vif(df, features_redundant)

    print("\nTest 2: Redundant Targets (Capacity Hoarding)")
    print(f"Targets: {features_redundant}")
    for k, v in vif_red.items():
        print(f"  {k} VIF: {v:.4f}")

    avg_vif_red = np.mean(list(vif_red.values()))
    if avg_vif_red >= 1.10:
        print(f"-> SUCCESS (Simulation): Targets are correctly identified as redundant (VIF {avg_vif_red:.2f} > 1.10). "
              "Combination therapy would waste resources.")
    else:
        print("-> FAILURE: Redundant targets not detected.")

    print("="*60)

if __name__ == "__main__":
    main()
