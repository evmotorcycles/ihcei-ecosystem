import pytest
import numpy as np
from src.simulation.mulk_entropy_engine import (
    MulkTensor, Agent, NetworkADGE, SystemWideEntropyError, verify_kitchen_protocol
)

# --- Test Suites ---

def test_kitchen_protocol_essence():
    """
    Check 4: Kitchen Protocol Verification (E = U * D^2).
    Prove: U=1,000,000, D=0 => E=0.
    """
    utility = 1_000_000
    governance = 0.0
    essence = verify_kitchen_protocol(utility, governance)
    assert essence == 0.0, f"Essence should be 0.0, got {essence}"

def test_healthy_network_physics():
    """
    Check 2: ADGE Physics Engine (C_dev Calculation) - Healthy State.
    Verify C_dev remains high and stable when Mulk is aligned (1.0).
    """
    tensor = MulkTensor(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    # Agents with knowledge_phi=5.0 to generate sufficient flow
    agents = [Agent(f"A{i}", utility_u=100, governance_d=1.0, knowledge_phi=5.0) for i in range(5)]
    network = NetworkADGE(agents, tensor)

    # Run simulation steps
    for _ in range(10):
        c_dev = network.simulate_step()

    # Max Flow = 5 agents * 4 peers * (5.0*5.0) = 20 * 25 = 500.0
    assert c_dev > 400.0, f"Healthy network C_dev too low: {c_dev}"
    assert network.h_network <= 2.0, "Cognitive noise (h_network) should be minimal."

def test_pharaoh_model_collapse():
    """
    Check 3: Modeling the Failure (The Pharaoh Model & Gate 7).
    Simulate 'Benevolent Tyranny' (Corrupt Mulk).
    Verify h_network spikes and C_dev collapses, raising SystemWideEntropyError.
    """
    # Create corrupted governance (Pharaoh Model: Alignment ~ 0.1)
    # E.g., Rules manipulated (0.0), Roles usurped (0.0), etc.
    corrupt_tensor = MulkTensor(
        terminology=0.1, roles=0.0, dues_responsibilities=0.1,
        authorities_domains=0.0, rules=0.0, policies=0.1,
        procedures=0.1, actions_implications=0.1,
        domains_application=0.0, exceptions=0.0
    )

    # Agents might still have high utility (resources) but corrupted D.
    agents = [Agent(f"P{i}", utility_u=1_000_000, governance_d=0.1) for i in range(5)]

    network = NetworkADGE(agents, corrupt_tensor)

    with pytest.raises(SystemWideEntropyError):
        # Run until collapse
        for step in range(50):
            network.simulate_step()

    # Post-mortem check (optional logic, but captured via exception)
    assert network.h_network > 100.0, "Systemic friction (h_network) must have spiked."
