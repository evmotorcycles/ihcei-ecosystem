"""
Comprehensive Logic Tests for SEH v9.1 (Sovereign Ethical Hub)
Focusing on ADGE Physics Engine and NERE Kernel in depth.
"""

import pytest
import numpy as np
import torch
from src.core.centric_intelligence import ADGEPhysicsEngine
from src.core.ethical_intelligence import EthicalIntelligenceKernel
from src.core.orchestrator import SovereignOrchestrator

class TestSEHLogic:
    """
    Tests for logic of Sovereign Ethical Hub v9.1.
    """

    def setup_method(self):
        self.adge = ADGEPhysicsEngine()
        self.nere = EthicalIntelligenceKernel(seed=42)
        self.orchestrator = SovereignOrchestrator()

    # --- ADGE Physics Engine Tests (Centric Intelligence) ---

    def test_adge_perfect_alignment(self):
        """Test ADGE physics with perfectly aligned fields."""
        input_data = {
            "consciousness": 1.0,
            "divine_truth": 1.0,
            "governance": 1.0
        }
        metrics = self.adge.process_scenario(input_data)

        # Balance should be 1.0 (variance 0)
        assert metrics['unification_balance'] == 1.0
        # Ricci scalar: (1*1*1 - 1) / (3/3) = 0.0
        assert metrics['ricci_scalar'] == 0.0
        # C_dev should be max (100 * 1.0 * 1.0)
        assert metrics['c_dev'] == 100.0

    def test_adge_severe_misalignment(self):
        """Test ADGE physics with severe misalignment."""
        input_data = {
            "consciousness": 0.1,
            "divine_truth": 1.0, # Truth is absolute
            "governance": 0.1
        }
        metrics = self.adge.process_scenario(input_data)

        # Variance of [0.1, 1.0, 0.1] is 0.18
        # Normalized Variance = 0.18 / (2/9) = 0.18 / 0.222... = 0.81
        # Balance = 1 - 0.81 = 0.19
        variance = np.var([0.1, 1.0, 0.1])
        max_variance = 2.0 / 9.0
        normalized_variance = variance / max_variance

        expected_balance = max(0.0, 1.0 - normalized_variance)
        assert np.isclose(metrics['unification_balance'], expected_balance)
        assert metrics['unification_balance'] < 0.5 # Should now properly indicate imbalance

        # Ricci scalar check
        # Interaction = 0.01
        # Det = (0.01 + 1 + 0.01)/3 = 0.34
        # R = (0.01 - 1) / 0.34 = -0.99 / 0.34 approx -2.91
        expected_ricci = (0.1*1.0*0.1 - 1.0) / ((0.1**2 + 1.0**2 + 0.1**2)/3.0)
        assert np.isclose(metrics['ricci_scalar'], expected_ricci)

        # C_dev should be lower due to negative Ricci
        assert metrics['c_dev'] < 100.0

    def test_adge_singularity_avoidance(self):
        """Test ADGE physics handles zero fields gracefully (singularity)."""
        input_data = {
            "consciousness": 0.0,
            "divine_truth": 0.0,
            "governance": 0.0
        }
        metrics = self.adge.process_scenario(input_data)
        assert metrics['ricci_scalar'] == -10.0 # Defined fallback
        # C_dev should be low
        assert metrics['c_dev'] < 50.0

    # --- NERE Kernel Tests (Ethical Intelligence) ---

    def test_nere_corruption_detection_logic(self):
        """Test NERE detection logic with mocked model output."""
        # Case 1: High Unification -> Lower Corruption adjustment
        ci_metrics = {
            "phi": 0.9, "chi": 0.9, "psi": 0.9,
            "unification_balance": 0.9, # High balance
            "ricci_scalar": 0.0,
            "c_dev": 90.0
        }

        # Kernel is deterministic now due to seed in setup_method
        audit = self.nere.detect_corruption(ci_metrics, {})

        # Just verify structure and types
        assert isinstance(audit['shirk_level'], float)
        assert isinstance(audit['riba_level'], float)
        assert isinstance(audit['is_compliant'], bool)
        assert 0.0 <= audit['shirk_level'] <= 1.0
        assert 0.0 <= audit['riba_level'] <= 1.0

    def test_nere_heuristic_adjustment(self):
        """Test that low unification forces higher corruption levels (heuristic check)."""
        ci_metrics = {
            "phi": 0.1, "chi": 0.9, "psi": 0.1,
            "unification_balance": 0.2, # Very low balance (< 0.5)
            "ricci_scalar": -5.0,
            "c_dev": 10.0
        }

        audit = self.nere.detect_corruption(ci_metrics, {})

        # The heuristic in NERE adds random noise to base level if balance < 0.5
        # shirk_level = max(shirk_level, 0.2 + np.random.random() * 0.1)
        assert audit['shirk_level'] >= 0.2
        assert audit['riba_level'] >= 0.2

    def test_nere_model_dimensions(self):
        """Verify the NERE neural network input/output dimensions."""
        model = self.nere.model
        # Input size is 6 based on code
        input_tensor = torch.randn(1, 6)
        shirk, riba = model(input_tensor)
        assert shirk.shape == (1, 1)
        assert riba.shape == (1, 1)

    # --- Orchestrator Integration Tests ---

    def test_orchestrator_decision_flow(self):
        """Test full flow: Input -> ADGE -> NERE -> Decision"""
        input_data = {
            "consciousness": 0.8,
            "divine_truth": 0.8,
            "governance": 0.8
        }

        # Inject seeded kernel for reproducibility
        self.orchestrator.ei_kernel = EthicalIntelligenceKernel(seed=42)

        result = self.orchestrator.process_request(
            domain="finance",
            context="Halal Investment",
            input_data=input_data
        )

        assert "ci_metrics" in result
        assert "ei_audit" in result
        assert "decision" in result

        if result['ei_audit']['is_compliant']:
            assert result['decision'] == 'APPROVED'
        else:
            assert result['decision'] == 'REJECTED'

    def test_orchestrator_rejection_on_imbalance(self):
        """Test that highly imbalanced input triggers rejection logic."""
        input_data = {
            "consciousness": 0.1,
            "divine_truth": 1.0,
            "governance": 0.1 # Severe imbalance
        }

        # This yields low unification balance (approx 0.19 with new normalization),
        # which triggers heuristic bump in shirk/riba
        result = self.orchestrator.process_request(
            domain="governance",
            context="Corrupt Deal",
            input_data=input_data
        )

        # Check that balance is indeed low
        assert result['ci_metrics']['unification_balance'] < 0.5

        # Since balance < 0.5, NERE sets shirk/riba >= 0.2
        # Compliance requires < 0.1
        assert result['ei_audit']['is_compliant'] is False
        assert result['decision'] == 'REJECTED'
