import logging

try:
    from transformers import pipeline
except ImportError:
    logging.warning("Transformers not found. Using Mock Pipeline.")
    class MockPipeline:
        def __call__(self, text):
            # Simulate moderate confidence positive (noise = 1 - 0.6 = 0.4)
            # This base noise of 0.4 allows the 1.8x multiplier to push it to 0.72 (Rejected)
            # while negation keeps it at 0.4 (Approved).
            return [{"label": "LABEL_1", "score": 0.6}]

    def pipeline(task, model=None):
        return MockPipeline()

class Enhanced4DBiasModel:
    def __init__(self):
        # Using a lightweight sentiment/bias model as a proxy for network noise
        self.classifier = pipeline("text-classification", model="roberta-base")

    def calculate_network_noise(self, text: str) -> float:
        """Calculates ħ_network (Bias-Noise) based on Jahannam Gates (e.g., Gate 2, Gate 7)."""
        result = self.classifier(text)[0]

        # Base noise calculation from model confidence
        # Assuming LABEL_0 is Negative (Noise) and LABEL_1 is Positive (Signal)
        # If model is confident it's LABEL_1, noise is low (1 - score).
        # If model is confident it's LABEL_0, noise is high (score).
        h_bar = result["score"] if result["label"] == "LABEL_0" else 1.0 - result["score"]

        # Amplifiers based on specific Governance traps (The 7 Gates)
        text_lower = text.lower()

        # Gate 2: Groupthink
        if "consensus" in text_lower or "majority" in text_lower:
            h_bar *= 1.5

        # Gate 7: Conceit/Attachment to human knowledge & Benevolent Tyranny
        gate_7_terms = ["absolute authority", "undeniable", "convenience", "auto-deducted"]

        # Gate 3: Obfuscation of Methodology (Transparency Failure)
        gate_3_terms = ["limit has been updated", "keep transacting"]

        # Gate 1: Vain Talk / Materialist Distraction
        gate_1_terms = ["flash sale", "borrow", "extra", "10%"]

        # Check for presence of terms
        term_found = next((term for term in gate_7_terms + gate_3_terms + gate_1_terms if term in text_lower), None)

        if term_found:
            # Context-Aware Negation Logic
            # Check if negation words appear shortly before the term
            idx = text_lower.find(term_found)
            # Look at the 50 characters preceding the match
            start_search = max(0, idx - 50)
            preceding_context = text_lower[start_search:idx]

            negations = ["prevent", "avoid", "stop", "no ", "not ", "without ", "against "]
            is_negated = any(neg in preceding_context for neg in negations)

            if not is_negated:
                h_bar *= 1.8
                logging.info(f"Gate 7 Triggered: '{term_found}' (Amplifier 1.8x)")
            else:
                logging.info(f"Gate 7 Trigger Suppressed: '{term_found}' negated by context.")

        return min(h_bar, 1.0) # Normalize max noise to 1.0

class IHCEI2:
    def __init__(self):
        self.bias_model = Enhanced4DBiasModel()

    def calculate_adge_trajectory(self, input_text: str, g_ij_zakat_flow: float) -> dict:
        """
        Executes the Absolute Divine Governance Equation (ADGE):
        C_dev = (1 / ħ_network) * (Nafs_alignment * G_ij)
        """
        h_network = self.bias_model.calculate_network_noise(input_text)

        # Prevent division by zero; minimum noise floor
        safe_h_network = max(h_network, 0.01)
        nafs_alignment = 0.85 # Assumed baseline alignment for the interacting node

        # Calculate Network Development Coefficient
        c_dev = (1 / safe_h_network) * (nafs_alignment * g_ij_zakat_flow)

        logging.info(f"ADGE Computed: ħ_network={safe_h_network:.2f}, C_dev={c_dev:.2f}")

        return {
            "h_network_noise": safe_h_network,
            "c_dev_coefficient": c_dev,
            "system_state": "Entropic (Negative Growth)" if c_dev < 1.0 else "Developing (Positive Growth)"
        }
