import pytest
from src.simulation.mulk_entropy_engine import (
    NetworkADGE,
    MulkTensor,
    ArdhDataDomain,
    NafsNode,
    run_pharaoh_simulation,
    run_agency_simulation
)

def test_pharaoh_model_collapse():
    """
    Test the Pharaoh Model scenario.
    Expected: High U, D=0 -> E=0, Hbar -> Infinity, C_dev -> Low/0
    """
    results = run_pharaoh_simulation()

    final_state = results[-1]

    # Assert D is zero
    assert final_state['D'] == 0.0

    # Assert Essence (E = U * D^2) is zero
    assert final_state['E'] == 0.0

    # Assert Friction (Hbar) is extremely high
    assert final_state['hbar'] > 1e6

    # Assert Cognitive Development is effectively zero (integral of 0)
    # Since E is 0, C_dev should not grow significantly
    assert final_state['C_dev'] == 0.0

def test_agency_economy_growth():
    """
    Test the Agency Economy scenario.
    Expected: D increasing, E increasing, Hbar low, C_dev growing exponentially.
    """
    results = run_agency_simulation()

    initial_state = results[0]
    final_state = results[-1]

    # Assert D improved
    assert final_state['D'] > initial_state['D']

    # Assert Essence improved
    assert final_state['E'] > initial_state['E']

    # Assert Friction is managed (should be much lower than Pharaoh model)
    assert final_state['hbar'] < 100.0

    # Assert Cognitive Development is positive and growing
    assert final_state['C_dev'] > 0.0
    assert final_state['C_dev'] > initial_state['C_dev']

def test_sunk_cost_bias():
    """
    Test that Sunk Cost Bias prevents optimization.
    """
    mulk = MulkTensor(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
    ardh = ArdhDataDomain()
    engine = NetworkADGE(resource_utility_u=100.0, mulk_tensor=mulk, ardh=ardh)

    # Node with High Sunk Cost Bias (1.0 -> Locked)
    locked_node = NafsNode("Locked", "KHALIFAH", agency_delta=10.0, internal_bias=0.5, sunk_cost_bias=1.0)
    engine.add_node(locked_node)

    # Run a step
    engine.step_simulation('AGENCY')

    # Bias should NOT have decreased
    assert locked_node.internal_bias == 0.5

def test_bauda_entropy_injection():
    """
    Test that Ba'uda nodes inject entropy.
    """
    mulk = MulkTensor(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
    ardh = ArdhDataDomain()
    engine = NetworkADGE(resource_utility_u=100.0, mulk_tensor=mulk, ardh=ardh)

    # Base friction check
    base_friction = engine.calculate_systemic_friction('AGENCY')

    # Add Ba'uda
    bauda = NafsNode("Mosquito", "BAUDA", agency_delta=1.0, internal_bias=1.0)
    engine.add_node(bauda)

    new_friction = engine.calculate_systemic_friction('AGENCY')

    # Friction should increase due to Ba'uda spike (hardcoded +5.0 in engine)
    # Note: calculate_systemic_friction also scales by D in AGENCY mode
    # friction = (base + bias + bauda) / (1 + D*10)
    # We just need to check it increased significantly relative to base
    assert new_friction > base_friction
