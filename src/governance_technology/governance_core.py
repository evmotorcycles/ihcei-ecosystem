from src.nere.nere_core import NERECore

class GovernanceCore:
    """
    Core engine for Governance Technology.
    Integrates NERE for auditing content against Sovereign principles.
    """
    def __init__(self):
        self.nere = NERECore()

    def process_request(self, content: str) -> dict:
        """
        Processes a request by passing it through the NERE audit.
        """
        audit = self.nere.audit_decision(content)

        # Enforce the audit decision
        if audit["decision"] == "REJECTED":
            return {
                "status": "BLOCKED",
                "reason": audit["messages"],
                "audit_details": audit
            }

        return {
            "status": "PROCESSED",
            "audit": audit,
            # In a real system, further processing would happen here
            "result": "Content accepted for processing."
        }
