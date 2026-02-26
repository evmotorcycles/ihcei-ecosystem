
import pytest
import numpy as np
from src.simulation.ugo import UnifiedGovernanceObject

def generate_historical_millat(noise_level: float) -> np.ndarray:
    """Helper duplicate for testing."""
    base_matrix = np.eye(10)
    if noise_level > 0.0:
        np.random.seed(42)
        noise = np.random.uniform(0, noise_level, (10, 10))
        base_matrix += noise
    return base_matrix

class TestFinancialCrisisAudit:
    def test_financial_crisis_collapse(self):
        """
        Verify that the 2008 Crisis parameters result in critical failure metrics.
        """
        historical_utility_u = 100000000000.0
        mulk_tensor_input = np.ones(10)
        millat_corruption_noise = 9.8 # High Semantic Drift

        millat_matrix = generate_historical_millat(millat_corruption_noise)

        ugo = UnifiedGovernanceObject(
            name="2008 Test",
            mulk_tensor=mulk_tensor_input,
            millat_matrix=millat_matrix,
            utility_u=historical_utility_u
        )

        metrics = ugo.compile_reality()

        # 1. Assert Discipline (D) is shattered (e.g., < 0.01)
        d_val = float(metrics["Discipline (D)"])
        assert d_val < 0.01

        # 2. Assert Essence (E) is wiped out relative to U
        e_val = float(metrics["Total Essence (E)"].replace(",", ""))
        u_val = float(metrics["Utility (U)"].replace(",", ""))
        # E should be a tiny fraction of U due to D^2
        # If D ~ 0.006, E ~ U * 0.000036
        assert e_val < (u_val * 0.0001)

        # 3. Assert Systemic Friction is "Infinite" (extremely high)
        friction_val = float(metrics["Systemic Friction (h_net)"].replace(",", ""))
        assert friction_val > 1e20 # Chunks of Darkness

        # 4. Assert Cognitive Development (C_dev) is zero
        c_dev_val = float(metrics["Cognitive Dev (C_dev)"])
        assert c_dev_val < 0.0001
