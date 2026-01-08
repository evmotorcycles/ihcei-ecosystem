from typing import Dict, Any
from src.seh.seh_v9_1 import SEHCore
from src.nere.nere_core import NERECore
from src.core.adge import ADGEPhysicsEngine

class GovernanceCore:
    """
    Core Governance Technology module.
    Integrates SEH, NERE, and ADGE to process requests.
    """

    def __init__(self):
        self.seh = SEHCore()
        self.nere = NERECore()
        self.adge = ADGEPhysicsEngine()

    def process_request(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes a user request through the full Sovereign OS pipeline.

        1. SEH Pressing (Tin -> Lahm)
        2. NERE Auditing (Check Lahm output)
        3. ADGE Calculation (Calculate C_dev impact)
        """
        # 1. SEH Pressing
        seh_result = self.seh.press_data(input_text, context)
        lahm_content = seh_result["final_output"]["content"]

        # 2. NERE Audit
        # Convert Lahm content to transaction-like dict for audit
        audit_input = {
            "description": str(lahm_content),
            "context": context
        }
        audit_result = self.nere.audit_transaction(audit_input)

        # 3. ADGE Calculation
        # Assume some mock values for now
        phi_nafs = context.get("phi_nafs", 0.5) if context else 0.5
        connectivity = 0.8 # Hypothesized efficiency
        governance = audit_result["compliance_score"]

        c_dev = self.adge.calculate_c_dev(phi_nafs, connectivity, governance)

        return {
            "seh_result": seh_result,
            "audit_result": audit_result,
            "c_dev": c_dev,
            "status": "Approved" if audit_result["is_compliant"] else "Rejected"
        }
