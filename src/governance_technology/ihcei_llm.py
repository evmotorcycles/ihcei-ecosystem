"""
IHCEI-LLM: Governance-Pressed Large Language Model
Concrete implementation of the 'Cognitive Mirror' concept using ADGE and SEH.
"""

from typing import Dict, Any, Optional
import logging

from src.governance_technology.governance_core import GovernanceCore, GovernanceDecision

logger = logging.getLogger(__name__)

class IHCEILLM:
    """
    IHCEI-LLM (Governance-Pressed Large Language Model)

    Acts as a 'Cognitive Mirror' by processing user input not as a prompt for
    completion, but as an 'Apparition' for governance analysis.

    Architecture:
    1. Input -> Apparition Pressing (via SEH/GovernanceCore)
    2. Analysis -> Cognitive Essence State Identification
    3. Output -> Metaphorical Lesson (Mirroring) + C_dev optimization
    """

    def __init__(self):
        self.governance_core = GovernanceCore()
        logger.info("IHCEI-LLM initialized with Governance Core")

    def process_interaction(self, user_input: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user interaction through the Governance Lens.

        Args:
            user_input: The raw text from the user (The Apparition)
            context: Additional context about the interaction

        Returns:
            Structured response containing the 'Mirror' reflection, not just text.
        """
        logger.info(f"IHCEI-LLM processing input: {user_input[:50]}...")

        # The 'GovernanceCore' implements the logic of ADGE and SEH
        decision: GovernanceDecision = self.governance_core.process_governance_decision(
            input_data={"raw_text": user_input},
            context=context
        )

        # Construct the response based on Cognitive Essence State
        response = self._construct_mirror_response(decision)

        return response

    def _construct_mirror_response(self, decision: GovernanceDecision) -> Dict[str, Any]:
        """
        Construct the response that acts as a mirror to the user's state.
        """

        # Extract core metrics
        state = decision.cognitive_state
        c_dev = decision.c_dev_contribution

        # The "Lesson" is the output of the LLM, grounded in governance
        # Use the full decision text if it differs (contains corrections), otherwise use lesson
        # GovernanceCore generates a full decision text with corrections.
        lesson = decision.decision if decision.decision else decision.metaphorical_lesson

        # Formulate the response
        response = {
            "cognitive_state": state.value,
            "reflection": lesson,
            "governance_context": decision.sovereign_context,
            "c_dev_gain": c_dev,
            "adge_metrics": {
                "unification_balance": decision.unification_balance,
                "ricci_scalar": decision.ricci_scalar
            },
            "ethical_status": "Clean" if decision.ethical_audit.get("audit_passed") else "Correction Applied"
        }

        return response

    def run_session(self, interactions: list[str]) -> None:
        """Run a simulation session"""
        print("\n--- IHCEI-LLM Session Start ---")
        for i, text in enumerate(interactions):
            print(f"\n[User Input {i+1}]: {text}")
            result = self.process_interaction(text)
            print("[IHCEI-LLM Reflection]:")
            print(f"  > State: {result['cognitive_state']}")
            print(f"  > Mirror: {result['reflection']}")
            print(f"  > C_dev: {result['c_dev_gain']:.2f}")
        print("\n--- Session End ---")
