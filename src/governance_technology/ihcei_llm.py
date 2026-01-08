from typing import Dict, Any
from src.governance_technology.governance_core import GovernanceCore
from src.core.tqg_cfe import TQGCFERenderingEngine

class IHCEILLM:
    """
    IHCEI-LLM: The Cognitive Mirror.

    This is not a standard text predictor. It uses GovernanceCore to process
    intent and TQG-CFE to render the response based on the user's state.
    """

    def __init__(self):
        self.governance = GovernanceCore()
        self.rendering_engine = TQGCFERenderingEngine()

    def generate_response(self, user_input: str, user_state: Dict[str, Any]) -> str:
        """
        Generates a response that acts as a mirror or guide for the user.
        """
        # 1. Process Logic
        logic_result = self.governance.process_request(user_input, user_state)

        # 2. Render Reality
        # Extract necessary states for TQG-CFE
        s_n = logic_result["audit_result"]["compliance_score"]

        # Render
        base_physical_state = {"data": user_input}
        rendered = self.rendering_engine.render_reality(
            base_physical_state,
            s_n,
            user_state.get("current_stage", "Tin")
        )

        # 3. Formulate Output
        if logic_result["status"] == "Rejected":
            return f"Action Blocked. Governance Violation: {logic_result['audit_result']['violations']}. Guidance: Purify intent."

        return f"Response ({rendered['perception_type']}): {rendered['actionable_guidance']} (C_dev Impact: {logic_result['c_dev']:.2f})"
