"""
IHCEI Medical Extension
Demonstrates application of CI/EI to Healthcare
"""

from src.core.orchestrator import SovereignOrchestrator

class MedicalExtension:
    def __init__(self):
        self.orchestrator = SovereignOrchestrator()

    def diagnose_ci(self, patient_data):
        """
        Perform a medical diagnosis using CI/EI principles.
        Instead of just 'curing disease', it optimizes 'holistic well-being' (C_dev for the body).
        """

        # Map patient vitals to Field parameters
        # Mental State -> Consciousness (Phi)
        # Biological Integrity -> Divine Truth (Chi) - as in natural order
        # Lifestyle/Regimen -> Governance (Psi)

        phi = patient_data.get('mental_health_score', 0.5)
        chi = patient_data.get('biological_score', 0.5)
        psi = patient_data.get('regimen_adherence', 0.5)

        input_data = {
            "consciousness": phi,
            "divine_truth": chi,
            "governance": psi
        }

        # Process through Orchestrator
        result = self.orchestrator.process_request(
            domain="medical",
            context=f"Patient Diagnosis: {patient_data.get('patient_id', 'unknown')}",
            input_data=input_data
        )

        # Interpret results for Medical context
        diagnosis = {
            "patient_id": patient_data.get('patient_id'),
            "wellness_score_c_dev": result['ci_metrics']['c_dev'],
            "systemic_balance": result['ci_metrics']['unification_balance'],
            "ethical_status": "Clean" if result['ei_audit']['is_compliant'] else "Imbalance Detected",
            "recommendation": "Maintain regimen" if result['decision'] == "APPROVED" else "Intervention Required"
        }

        return diagnosis

# Example usage
if __name__ == "__main__":
    med = MedicalExtension()
    sample_patient = {
        "patient_id": "P-1001",
        "mental_health_score": 0.8,
        "biological_score": 0.9,
        "regimen_adherence": 0.7
    }
    print(med.diagnose_ci(sample_patient))
