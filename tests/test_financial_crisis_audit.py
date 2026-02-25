import sys
import os
import pytest
import numpy as np

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.simulation.financial_crisis_2008_audit import FinancialAgent, FinancialNetwork

class TestFinancialCrisisAudit:

    def test_kitchen_protocol(self):
        """
        Test 1: Kitchen Protocol (E = U * D^2)
        Verify that for a Bank agent with high U and D -> 0, E -> 0.
        """
        # Bank: High U (100), Low D (0.01)
        bank = FinancialAgent(agent_id=1, agent_type="Bank", U=100.0, D=0.01, tau=0.1, rho=0.1)
        essence = bank.calculate_essence()

        # Expected: 100 * (0.01)^2 = 100 * 0.0001 = 0.01
        assert essence == pytest.approx(0.01, abs=1e-5)
        assert essence < 1.0, "Essence should be collapsed (near zero)"

    def test_entropy_explosion(self):
        """
        Test 2: Entropy Explosion
        Verify that increasing h_corruption leads to a decrease in C_dev.
        """
        network = FinancialNetwork(num_agents=2)
        # Add two agents with fixed rho
        network.add_agent(FinancialAgent(0, "Bank", U=100, D=0.1, tau=0.1, rho=0.5))
        network.add_agent(FinancialAgent(1, "RatingAgency", U=50, D=0.1, tau=0.1, rho=0.5))

        # Initial C_dev with base h_corruption = 1.0
        c_dev_initial = network.calculate_network_c_dev()

        # Increase corruption (simulate toxic asset proliferation)
        network.h_corruption = 10.0
        c_dev_corrupt = network.calculate_network_c_dev()

        assert c_dev_corrupt < c_dev_initial, "C_dev should decrease as entropy increases"
        # Since h_corruption increased by 10x, C_dev should decrease by 10x approximately
        assert c_dev_corrupt == pytest.approx(c_dev_initial / 10.0, rel=1e-3)

    def test_connectivity_tensor_trust_evaporation(self):
        """
        Test 3: Connectivity Tensor (G_ij)
        Verify matrix operations and ensure no division by zero when trust is low.
        """
        network = FinancialNetwork(num_agents=2)
        network.add_agent(FinancialAgent(0, "A", 10, 0.1, 0.1, 0.1))
        network.add_agent(FinancialAgent(1, "B", 10, 0.1, 0.1, 0.1))

        # Manually set G_ij to zero (trust evaporation)
        network.G_ij = np.zeros((2, 2))

        # Calculate C_dev
        # Should be 0, not throw error
        c_dev = network.calculate_network_c_dev()
        assert c_dev == 0.0

    def test_nere_integration_toxic_asset(self):
        """
        Test 4: NERE API Integration
        Feed historical loan agreements (toxic assets) and ensure 'agency_delta': 'RED' flag (or negative).
        """
        network = FinancialNetwork(num_agents=1)
        # Toxic document with keywords
        toxic_doc = "This subprime mortgage bundle includes loans with no verification of income and adjustable rates."

        # We need to ensure NERE detects this.
        # Note: The current NERE implementation might need updates to detect 'subprime' or 'no verification'.
        # If this test fails, it indicates the need for patching NERE (as part of the audit).

        result = network.audit_transaction(toxic_doc)

        # Check if agency_delta is negative or flagged
        # Based on current NERE implementation which returns a string description
        assert "Negative" in result["agency_delta"] or "RED" in result["agency_delta"], \
            f"Expected Negative agency_delta for toxic asset, got: {result['agency_delta']}"
