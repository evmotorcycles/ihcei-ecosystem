from src.nere.nere_core import NERECore
from src.seh.seh_v9_1 import SEHCore

class GovernanceCore:
    def __init__(self):
        self.nere = NERECore()
        self.seh = SEHCore()

    def process_request(self, content: str) -> dict:
        """
        Main pipeline:
        1. Audit via NERE (check for Iblees/Gates).
        2. If passed, map to SEH (optional context).
        """
        audit_result = self.nere.audit_decision(content)

        response = {
            "audit": audit_result,
            "status": audit_result["status"]
        }

        return response
