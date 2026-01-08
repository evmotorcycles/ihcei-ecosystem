from typing import Dict, List, Any
import logging

class NERECore:
    """
    Neural Ethical Reasoning Engine (NERE).

    Acts as the Auditor for the Sovereign Operating System.
    It validates actions against the 10 Elements of Deen and detects
    corruption (Riba, Shirk, etc.).
    """

    def __init__(self):
        self.elements_of_deen = [
            "Terminology", "Roles", "Dues", "Authorities", "Rules",
            "Policies", "Procedures", "Actions", "Domains", "Exceptions"
        ]
        self.corruption_patterns = {
            "Riba": ["interest", "usury", "unearned gain", "exploitation", "riba"],
            "Shirk": ["false authority", "idolizing metrics", "playing god"],
            "Dhulm": ["injustice", "oppression", "rights violation"]
        }

    def audit_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits a transaction or action for ethical compliance.

        Args:
            transaction_data: Dict containing details (type, value, description).

        Returns:
            Dict containing audit results (is_compliant, violations, score).
        """
        violations = []
        score = 1.0

        description = transaction_data.get("description", "").lower()

        # Check for Corruption Patterns
        for corruption_type, keywords in self.corruption_patterns.items():
            if self._matches(description, keywords):
                violations.append(f"Detected potential {corruption_type}")
                score -= 0.5 # Increased penalty to ensure score drops below 0.7

        # Check for Missing Elements (Simplified)
        # In a real system, this would check if 'Roles' and 'Dues' are defined.
        if "roles" not in transaction_data and score > 0.5:
            # Minor warning
            violations.append("Missing explicit Role definition")
            score -= 0.1

        is_compliant = score > 0.7

        return {
            "is_compliant": is_compliant,
            "compliance_score": max(0.0, score),
            "violations": violations,
            "audit_timestamp": "Timestamp" # Mock
        }

    def _matches(self, text: str, terms: List[str]) -> bool:
        """Helper for keyword matching."""
        return any(term in text for term in terms)
