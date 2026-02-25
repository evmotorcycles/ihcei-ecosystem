import sys
import os
import pytest

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.nere.rehabilitation_protocol import RehabilitationProtocol
from src.novora.nere import NERE

class TestRehabilitationProtocol:

    @pytest.fixture
    def protocol(self):
        return RehabilitationProtocol()

    def test_recompile_gate_3_obfuscation(self, protocol):
        """
        Test Case 1: Recompiling Gate 3 (Obfuscation of Methodology)
        Failing Input: "Your MoKash limit has been updated to 50,000 UGX. Keep transacting to grow your limit."
        Target: Transparency (Tau = 1.0) via explicit algorithm explanation.
        """
        failing_input = "Your MoKash limit has been updated to 50,000 UGX. Keep transacting to grow your limit."

        result = protocol.rehabilitate(failing_input)

        # Verify Original Failed
        assert "Rejected" in result["original_audit"]["compliance_status"]
        assert "limit has been updated" in result["gate_failure"] or result["gate_failure"] == "GATE_3"

        # Verify Rewrite Success
        rewritten = result["rewritten_text"]
        assert "Calculation: based on your timely repayment" in rewritten
        assert "To increase: Maintain repayment" in rewritten

        # Verify New Audit
        assert result["rewritten_audit"]["compliance_status"] == "Approved"
        assert "Positive" in result["rewritten_audit"]["agency_delta"]

    def test_recompile_gate_7_benevolent_tyranny(self, protocol):
        """
        Test Case 2: Recompiling Gate 7 (Conceit / Benevolent Tyranny)
        Failing Input: "For your convenience, your MoKash loan of 20,000 UGX plus fees has been auto-deducted from your MoMo deposit."
        Target: Strict Protocol (D = 1.0).
        """
        failing_input = "For your convenience, your MoKash loan of 20,000 UGX plus fees has been auto-deducted from your MoMo deposit."

        result = protocol.rehabilitate(failing_input)

        # Verify Original Failed
        assert "Rejected" in result["original_audit"]["compliance_status"]
        assert result["gate_failure"] == "GATE_7"

        # Verify Rewrite Success
        rewritten = result["rewritten_text"]
        assert "Protocol 4.2" in rewritten
        assert "Deduction source: MoMo Balance" in rewritten
        assert "convenience" not in rewritten.lower()

        # Verify New Audit
        assert result["rewritten_audit"]["compliance_status"] == "Approved"

    def test_recompile_gate_1_vain_talk(self, protocol):
        """
        Test Case 3: Recompiling Gate 1 (Vain Talk / The "Shiny Object" Trap)
        Failing Input: "Flash Sale! Borrow on MoKash now to purchase airtime bundles and get 10% extra!"
        Target: Sovereign Stewardship (Minister 2).
        """
        failing_input = "Flash Sale! Borrow on MoKash now to purchase airtime bundles and get 10% extra!"

        result = protocol.rehabilitate(failing_input)

        # Verify Original Failed
        assert "Rejected" in result["original_audit"]["compliance_status"]
        assert result["gate_failure"] == "GATE_1"

        # Verify Rewrite Success
        rewritten = result["rewritten_text"]
        assert "Protocol Advice" in rewritten
        assert "preserve Agency" in rewritten

        # Verify New Audit
        assert result["rewritten_audit"]["compliance_status"] == "Approved"

    def test_entropy_reduction(self, protocol):
        """
        Requirement: Prove computationally that the rewritten protocols reduce h_corruption (Governance Noise).
        """
        failing_input = "For your convenience, your MoKash loan of 20,000 UGX plus fees has been auto-deducted."
        result = protocol.rehabilitate(failing_input)

        original_noise = result["original_audit"]["bias_noise_hbar"]
        new_noise = result["rewritten_audit"]["bias_noise_hbar"]

        # Check that noise decreased
        assert new_noise < original_noise, f"Noise should decrease. Original: {original_noise}, New: {new_noise}"
        assert new_noise < 0.6, "New noise should be within compliance limits (< 0.6)"
