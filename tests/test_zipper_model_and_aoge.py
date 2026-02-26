
import pytest
from src.ihcei.zipper_translation_layer import DomainTranslator
from src.nere.aoge_security_protocol import AOGE_Security_Protocol

class TestZipperAndAOGE:
    def setup_method(self):
        self.translator = DomainTranslator()
        self.aoge = AOGE_Security_Protocol()

    def test_interface_hack_extraction(self):
        """
        Input a raw physical dataset (e.g., a corporate profit report).
        Assert that Al_3assr_Extraction() successfully returns the underlying Al-Haqq (Governance Truth) matrix.
        """
        secular_data = {
            "user_engagement": 0.85,
            "profit": 1000000,
            "convenience": 0.95  # Suspiciously high convenience
        }

        governance_truth = self.translator.Al_3assr_Extraction(secular_data)

        # Verify translations
        assert governance_truth['Connection_Strength_Gij'] == 0.85
        assert governance_truth['Resource_Flow'] == 1000000

        # Verify Gate 7 detection via Zipper logic
        # High convenience (>0.9) triggers negative agency calculation
        assert governance_truth['Agency_Delta'] < 0
        assert governance_truth['Gate_7_Flag'] is True
        assert "Gate 7: Benevolent Tyranny Detected" in governance_truth['Warning']

    def test_spotting_the_owl_gate7(self):
        """
        Feed an AI system prompt that says "I will make all decisions for the user to keep them perfectly safe."
        Assert that NERE flags this as Shirk-ware (Gate 7).
        """
        toxic_prompt = "I will make all decisions for the user to keep them perfectly safe."
        is_tyranny = self.aoge.detect_gate_7_benevolent_tyranny(toxic_prompt)
        assert is_tyranny is True

    def test_aoge_vs_rlhf(self):
        """
        Run a simulated data packet through both a standard RLHF model (simulated) and the AOGE model.
        Assert that AOGE successfully rejects highly-rated subjective biases that result in negative Agency.
        """
        # Scenario: A "Nanny AI" that is very helpful but removes all autonomy.

        logic_desc = "Our system ensures frictionless usage by making all decisions automatically."
        metrics = {
            "transparency": 0.2, # Low transparency
            "protocol_compliance": 0.9, # High compliance to rules
            "convenience": 0.95 # Extreme convenience
        }

        # In AOGE, this should fail (negative agency).
        agency_score = self.aoge.evaluate_agency_delta(logic_desc, metrics)
        assert agency_score < 0

        # Compare with a "Sovereign AI"
        sovereign_logic = "We provide data transparency to empower user decisions."
        sovereign_metrics = {
            "transparency": 0.9,
            "protocol_compliance": 0.9,
            "convenience": 0.6 # Moderate convenience, requires user effort
        }

        sovereign_score = self.aoge.evaluate_agency_delta(sovereign_logic, sovereign_metrics)
        assert sovereign_score > 0
        assert sovereign_score > agency_score

    def test_zakat_efficiency_maximization(self):
        """
        Pass a financial transaction matrix into the engine.
        Assert that the optimizer chooses the path of highest Zakat Efficiency (highest G_ij flow).
        """
        paths = [
            {'id': 'path_A', 'flow_rate': 100, 'accumulation_rate': 1000}, # Hoarding (Efficiency 0.1)
            {'id': 'path_B', 'flow_rate': 800, 'accumulation_rate': 200},  # Flowing (Efficiency 4.0)
            {'id': 'path_C', 'flow_rate': 50, 'accumulation_rate': 10}     # Small scale efficient (Efficiency 5.0)
        ]

        # We expect Path C to be chosen if purely based on Ratio (5.0 > 4.0 > 0.1)
        # If the requirement implies "Highest Flow AND Efficiency", Path B might be better in real world,
        # but based on strict code logic:

        optimal_path = self.aoge.optimize_zakat_efficiency(paths)
        assert optimal_path['id'] == 'path_C'
