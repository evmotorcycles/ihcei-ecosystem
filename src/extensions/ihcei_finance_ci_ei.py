"""
IHCEI Finance Extension
Demonstrates application of CI/EI to Sovereign Finance (Islamic Finance/Ethical Economics).
Real World Application of SEH v9.1.
"""

from src.core.orchestrator import SovereignOrchestrator

class FinanceExtension:
    def __init__(self):
        self.orchestrator = SovereignOrchestrator()
        # Ensure name is registered if orchestrator requires it, though usually passed in method
        self.domain = "finance"

    def audit_transaction(self, transaction_data):
        """
        Audits a financial transaction using CI/EI principles.
        Maps financial metrics to ADGE Fields to detect Riba (Usury/Imbalance) and Shirk (Corruption).

        Mapping Logic:
        - Transparency/Disclosure -> Consciousness (Phi)
        - Equity/Fairness/Asset-Backing -> Divine Truth (Chi) (The 'Reality' of the value)
        - Contractual Clarity/Regulation -> Governance (Psi)
        """

        # 1. Map Real World Data to Fields

        # Transparency: 0.0 (Opaque) to 1.0 (Full Disclosure)
        phi = transaction_data.get('transparency_score', 0.5)

        # Fairness:
        # If interest_rate > 0 (Riba), Divine Truth drops significantly.
        # If profit_sharing (Musharakah), Divine Truth is high.
        is_interest_based = transaction_data.get('interest_rate', 0.0) > 0.0
        is_asset_backed = transaction_data.get('is_asset_backed', False)

        if is_interest_based:
            chi = 0.2 # Low truth (artificial growth)
        elif is_asset_backed:
            chi = 0.9 # High truth (real value)
        else:
            chi = 0.5 # Neutral

        # Governance: Adherence to contracts/law
        psi = transaction_data.get('regulatory_compliance', 0.5)

        input_data = {
            "consciousness": phi,
            "divine_truth": chi,
            "governance": psi
        }

        # 2. Process through Sovereign Orchestrator
        result = self.orchestrator.process_request(
            domain=self.domain,
            context=f"Transaction Audit: {transaction_data.get('transaction_id', 'unknown')}",
            input_data=input_data
        )

        # 3. Interpret Results for Finance Domain
        audit_report = {
            "transaction_id": transaction_data.get('transaction_id'),
            "type": transaction_data.get('type', 'General'),
            "adge_metrics": {
                "systemic_stability": result['ci_metrics']['ricci_scalar'],
                "unification_balance": result['ci_metrics']['unification_balance']
            },
            "nere_audit": {
                "shirk_risk": result['ei_audit']['shirk_level'],
                "riba_risk": result['ei_audit']['riba_level'],
                "is_compliant": result['ei_audit']['is_compliant']
            },
            "final_decision": result['decision'],
            "explanation": self._generate_explanation(result)
        }

        return audit_report

    def _generate_explanation(self, result):
        """Generates a human-readable explanation based on metrics."""
        if result['decision'] == "APPROVED":
            return "Transaction aligns with Sovereign Ethical principles. Fields are unified."
        else:
            reasons = []
            if result['ei_audit']['riba_level'] > 0.1:
                reasons.append("High Riba (Imbalance) detected")
            if result['ei_audit']['shirk_level'] > 0.1:
                reasons.append("High Corruption risk detected")
            if result['ci_metrics']['unification_balance'] < 0.5:
                reasons.append("Severe Field Misalignment (Systemic Instability)")

            return f"Transaction REJECTED: {', '.join(reasons)}."
