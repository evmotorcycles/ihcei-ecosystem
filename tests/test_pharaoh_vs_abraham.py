
import pytest
import numpy as np
from src.simulation.ugo import UnifiedGovernanceObject
from src.simulation.pharaoh_vs_abraham_sim import generate_millat_matrix

class TestUnifiedGovernanceObject:
    def test_ugo_initialization(self):
        """
        Verify that UGO initializes and stores input parameters correctly.
        """
        name = "Test Model"
        mulk = np.ones(10)
        millat = np.eye(10)
        utility = 500.0

        ugo = UnifiedGovernanceObject(name, mulk, millat, utility)

        assert ugo.name == name
        assert np.array_equal(ugo.mulk_tensor, mulk)
        assert np.array_equal(ugo.millat_matrix, millat)
        assert ugo.U == utility
        assert ugo.base_friction == 1.0 # Default

    def test_abraham_logic_pure_millat(self):
        """
        Verify the Abraham Model (Pure Millat/Identity Matrix).
        Expected: Zero Distortion, D=1.0, Low Friction, E=U.
        """
        mulk = np.ones(10)
        millat = generate_millat_matrix(is_corrupted=False) # Identity

        ugo = UnifiedGovernanceObject("Abraham", mulk, millat, utility_u=1000.0)
        metrics = ugo.compile_reality()

        # Verify Distortion is 0 (Identity matrix * ones vector = ones vector)
        assert float(metrics["Lexicon Distortion"]) == 0.0

        # Verify D (Discipline) is 1.0
        assert float(metrics["Discipline (D)"]) == 1.0

        # Verify Essence (E) = U * D^2 = 1000 * 1^2 = 1000
        # Parsing comma-formatted string back to float
        e_value = float(metrics["Total Essence (E)"].replace(",", ""))
        assert e_value == 1000.0

    def test_pharaoh_logic_corrupted_millat(self):
        """
        Verify the Pharaoh Model (Corrupted Millat).
        Expected: High Distortion, Low D, Infinite Friction, E << U.
        """
        mulk = np.ones(10)
        millat = generate_millat_matrix(is_corrupted=True, noise_level=8.0)

        ugo = UnifiedGovernanceObject("Pharaoh", mulk, millat, utility_u=1_000_000_000.0)
        metrics = ugo.compile_reality()

        # Verify Distortion is significant (> 0)
        distortion = float(metrics["Lexicon Distortion"])
        assert distortion > 10.0

        # Verify D (Discipline) is shattered (<< 1.0)
        d_value = float(metrics["Discipline (D)"])
        assert d_value < 0.1

        # Verify Essence (E) is collapsed relative to U
        e_value = float(metrics["Total Essence (E)"].replace(",", ""))
        u_value = float(metrics["Utility (U)"].replace(",", ""))

        assert e_value < u_value
        # Even with 1B utility, Essence should be relatively small
        assert e_value < (u_value * 0.01) # E is less than 1% of U

    def test_systemic_friction_exponential(self):
        """
        Verify that Systemic Friction grows exponentially with distortion.
        h_network = base * exp(distortion)
        """
        mulk = np.ones(10)

        # Case A: Low Corruption
        millat_a = generate_millat_matrix(is_corrupted=True, noise_level=0.1)
        ugo_a = UnifiedGovernanceObject("Low Noise", mulk, millat_a, 100.0)
        m_a = ugo_a.compile_reality()
        friction_a = float(m_a["Systemic Friction (h_net)"].replace(",", ""))

        # Case B: High Corruption
        millat_b = generate_millat_matrix(is_corrupted=True, noise_level=5.0)
        ugo_b = UnifiedGovernanceObject("High Noise", mulk, millat_b, 100.0)
        m_b = ugo_b.compile_reality()
        friction_b = float(m_b["Systemic Friction (h_net)"].replace(",", ""))

        # Friction B should be massively larger than Friction A
        assert friction_b > (friction_a * 100)
