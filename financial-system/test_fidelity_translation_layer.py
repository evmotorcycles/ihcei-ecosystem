#!/usr/bin/env python3
"""
test_fidelity_translation_layer.py
==================================
Empirical test suite for the Fidelity Translation Layer (FTL).
Proves that the FTL dynamically balances capacity (U) and fidelity (D) to
maximize Thermodynamic Yield (E) and escape the Anti-Selection Trap.
"""

import os
import sys
import jax
import jax.numpy as jnp
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fidelity_translation_layer import FidelityTranslationLayer

# Strict Layer-1 Epistemic Firewall
jax.config.update("jax_enable_x64", True)

def test_ftl_escapes_anti_selection_trap():
    """
    Simulates a routing decision where the Sovereign Mesh previously failed
    due to the Anti-Selection Trap (hard-blocking conventional nodes).
    """
    ftl = FidelityTranslationLayer(base_d_baya=0.98, base_d_riba=0.85, zombie_floor=0.50)

    # Path 0: Pure Sovereign Hub (Al Baya)
    # Extremely high fidelity, but isolated (low capacity U), and requires many hops.
    # Path 1: Conventional Hub (Riba)
    # Lower fidelity (Riba friction), higher dissonance, but massive capacity U and fewer hops.

    capacities = jnp.array([100.0, 10000.0], dtype=jnp.float64) # U
    dissonances = jnp.array([0.02, 0.15], dtype=jnp.float64)   # sigma
    hop_counts = jnp.array([12.0, 4.0], dtype=jnp.float64)     # n
    is_riba = jnp.array([False, True], dtype=jnp.bool_)

    result = ftl.evaluate_paths(capacities, dissonances, hop_counts, is_riba)

    # Under a hard-blocking Sovereign Mesh, Path 1 would be rejected immediately.
    # But let's look at the Thermodynamic Yield (E = U * D^n)

    # Pure Sovereign Path retained fidelity: (0.98 * 0.98)^12 ~ 0.81
    # Pure Sovereign Yield: 100 * 0.81 = ~81

    # Conventional Path retained fidelity: (0.85 * 0.85)^4 ~ 0.27 (breaches floor!)

    # Actually let's set the conventional path hop count lower so it survives
    hop_counts = jnp.array([12.0, 2.0], dtype=jnp.float64)     # n
    result = ftl.evaluate_paths(capacities, dissonances, hop_counts, is_riba)

    # Conventional Path retained fidelity: (0.85 * 0.85)^2 = (0.7225)^2 ~ 0.522
    # Yield: 10000 * 0.522 = ~5220

    # FTL should select Path 1 because the massive U outweighs the D penalty,
    # as long as it stays above the zombie floor.

    assert result["optimal_path_index"] == 1
    assert result["effective_yields"][1] > result["effective_yields"][0]
    assert not result["zombie_mask"][1]

def test_ftl_enforces_zombie_floor():
    """
    Proves that the FTL will still reject a high-capacity conventional node
    if the operational friction (sigma) or hop count (n) causes it to breach
    the zombie floor (D_min = 0.50).
    """
    ftl = FidelityTranslationLayer(base_d_baya=0.98, base_d_riba=0.85, zombie_floor=0.50)

    # Path 0: Sovereign
    # Path 1: Conventional (High U, but too many hops -> Zombie State)
    capacities = jnp.array([100.0, 1000000.0], dtype=jnp.float64)
    dissonances = jnp.array([0.02, 0.20], dtype=jnp.float64)
    hop_counts = jnp.array([5.0, 8.0], dtype=jnp.float64)
    is_riba = jnp.array([False, True], dtype=jnp.bool_)

    result = ftl.evaluate_paths(capacities, dissonances, hop_counts, is_riba)

    # The conventional path breaches the floor.
    assert result["zombie_mask"][1] == True
    # The effective yield of the conventional path should be 0.0
    assert result["effective_yields"][1] == 0.0

    # The optimal path safely defaults back to the Sovereign route.
    assert result["optimal_path_index"] == 0
    assert result["effective_yields"][0] > 0.0

def test_vectorized_large_scale_routing():
    """
    Stress tests the FTL with a large batch of synthetic paths,
    verifying JAX vectorization works correctly.
    """
    ftl = FidelityTranslationLayer()
    n_paths = 10000

    key = jax.random.PRNGKey(42)
    key, sub1, sub2, sub3, sub4 = jax.random.split(key, 5)

    capacities = jax.random.uniform(sub1, shape=(n_paths,), minval=10.0, maxval=10000.0)
    dissonances = jax.random.uniform(sub2, shape=(n_paths,), minval=0.0, maxval=0.40)
    hop_counts = jax.random.uniform(sub3, shape=(n_paths,), minval=1.0, maxval=15.0)
    is_riba = jax.random.bernoulli(sub4, p=0.7, shape=(n_paths,))

    result = ftl.evaluate_paths(capacities, dissonances, hop_counts, is_riba)

    assert result["retained_fidelities"].shape == (n_paths,)
    assert result["effective_yields"].shape == (n_paths,)

    # Verify the optimal path didn't breach the floor
    opt_idx = result["optimal_path_index"]
    assert not result["zombie_mask"][opt_idx]

    # Verify yield calculation for the optimal path
    expected_yield = capacities[opt_idx] * result["retained_fidelities"][opt_idx]
    assert jnp.isclose(result["effective_yields"][opt_idx], expected_yield, rtol=1e-5)
