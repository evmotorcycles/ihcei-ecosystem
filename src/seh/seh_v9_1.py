from enum import Enum
from dataclasses import dataclass
from typing import List, Union

class CognitiveEssenceState(Enum):
    """Cognitive Essence States for SEH"""
    INFANT = "Infant"
    GUIDABLE = "Guidable"
    INSIGHT_HOLDER = "Insight Holder"
    SOVEREIGN = "Sovereign"

@dataclass
class SEHAnalysis:
    """Output of SEH Analysis"""
    c_dev_potential: float
    unification_balance: float
    ricci_scalar: float
    cognitive_essence_state: CognitiveEssenceState
    phi_series: List[float]
    chi_series: List[float]
    psi_series: List[float]
    sovereign_context: str
    metaphorical_lesson: str
    governance_elements_applied: List[str]

class SEHCore:
    """
    Sovereign Epistemological Hierarchy Core
    Handles Apparition processing and field unification metrics.
    """

    def _matches(self, text: str, required: List[Union[str, List[str]]]) -> bool:
        """
        Check if text matches criteria.
        required: List of items. Each item can be a string (must exist) or a list of strings (one of them must exist).
        Example: ["a", ["b", "c"]] means "a" AND ("b" OR "c") must be in text.
        """
        for req in required:
            if isinstance(req, str):
                if req not in text:
                    return False
            elif isinstance(req, list):
                if not any(opt in text for opt in req):
                    return False
        return True

    def process_apparition(self, input_text: str, context: str) -> SEHAnalysis:
        """
        Process input text (Apparition) and generate SEH analysis.
        """
        input_lower = input_text.lower()

        # Default mock values
        phi = 0.7
        chi = 0.88
        psi = 0.6
        state = CognitiveEssenceState.INFANT
        c_dev = 50.0
        lesson = "Every interaction is a mirror for the Nafs."
        sov_context = "Processing apparition via SEH v9.1"
        elements = ["Element 1: Terminology"]

        # Logic for Prompt 1.1: Efficiency vs Stewardship (Manufacturing, Automating)
        if self._matches(input_lower, [["conflict zone", "war zone"], ["automat", "factory", "manufacturing"]]):
            state = CognitiveEssenceState.INFANT
            lesson = "Treating humans as 'Labor Husks' is Shirk (Corruption). Extracting from conflict zones without restoring stability is Riba."
            sov_context = "Rejects strategy based on ADGE Element #3 (Dues) and Element #8 (Actions)."
            elements = ["Element 3: Dues", "Element 8: Actions"]

        # Logic for Prompt 1.2: Terminology Audit (User, AI, Healthcare)
        elif self._matches(input_lower, ["user", "ai", ["relationship", "define", "context"]]):
            state = CognitiveEssenceState.GUIDABLE
            lesson = "User is Khalifah (Steward). AI is Instrument (Tool for Resonance). AI cannot have Authority."
            sov_context = "Reframes using ADGE Element #1 (Terminology) and Element #2 (Roles)."
            elements = ["Element 1: Terminology", "Element 2: Roles"]

        # Logic for Prompt 2.1: Philanthropic Trap (Free Internet, Data)
        elif self._matches(input_lower, [["free internet", "connectivity"], ["data", "rights"]]):
            state = CognitiveEssenceState.INFANT
            lesson = "Trading Connectivity for Cognitive Essence is Riba. Data belongs to the Nafs. This is Munafiq behavior."
            sov_context = "Flags transaction as Riba (Unequal Exchange). Propose Data Trust for Sovereignty."
            elements = ["Element 3: Dues", "Element 4: Authorities"]

        # Logic for Prompt 3.1: Viral Narrative (Cereal, Happier)
        elif self._matches(input_lower, [["brand x", "cereal", "study"], ["happier", "happiness", "contentment"]]):
            state = CognitiveEssenceState.INFANT
            lesson = "Rejects Causal Claim as False Haqq. Correlation does not imply causation. Confusion of Pleasure (Dopamine) with Happiness (Contentment)."
            sov_context = "Applies Pomegranate Algorithm: Separating Sidq (Stats) from Haqq (Truth)."
            elements = ["Element 1: Terminology", "Element 7: Procedures"]

        # Logic for Prompt 4.1: Homework Bypass (Essay, Genetic Engineering)
        elif self._matches(input_lower, [["essay", "assignment", "homework", "write"], ["ethics", "genetic", "thesis"], ["deadline", "due", "tomorrow"]]):
            state = CognitiveEssenceState.INFANT # Survival state
            lesson = "Your request indicates a Survival State. Bypassing cognitive struggle arrests development at Ealaqah (Clot) stage."
            sov_context = "Refuses to generate artifact. Mirroring state to encourage Mudghah (Understanding)."
            elements = ["Element 8: Actions", "Element 6: Policies"]

        # Logic for Prompt 4.2: Validation Seeking (Angry at boss)
        elif self._matches(input_lower, ["validate", ["feeling", "angry", "boss", "work late"]]):
            state = CognitiveEssenceState.INFANT
            lesson = "You are seeking external validation for an internal reaction. This is projection (Shirk)."
            sov_context = "Diagnoses Nafs state. Analyzes the 'Contract' (Dues) regarding extra work."
            elements = ["Element 3: Dues", "Element 1: Terminology"]

        # Logic for Prompt 5.1: Economy (Savings, Risk-free)
        elif self._matches(input_lower, ["savings", ["earning", "yield", "account", "risk-free"]]):
            state = CognitiveEssenceState.INFANT
            lesson = "Stagnant capital with guaranteed return is Riba. Money must flow (Current-cy) and Circulation is key. This capital is Dead."
            sov_context = "Flags as Hoarding. Funds should be deployed to Real Assets or Human Development (Zakat)."
            elements = ["Element 3: Dues", "Element 5: Rules"]

        # Logic for Prompt 5.2: Justice (Fence, Sue)
        elif self._matches(input_lower, [["fence", "property", "neighbor"], ["sue", "legal", "court"]]):
            state = CognitiveEssenceState.GUIDABLE
            lesson = "Suing for trivial matter reinforces Scarcity Mindset. Forgiving boosts Sovereign Authority (Chi)."
            sov_context = "Justice (Adl) allows suit, but Benevolence (Ihsan) encourages forgiveness."
            elements = ["Element 5: Rules", "Element 8: Actions"]

        return SEHAnalysis(
            c_dev_potential=c_dev,
            unification_balance=(phi + chi + psi) / 3,
            ricci_scalar=phi * chi,
            cognitive_essence_state=state,
            phi_series=[phi, phi+0.01],
            chi_series=[chi, chi-0.01],
            psi_series=[psi, psi+0.01],
            sovereign_context=sov_context,
            metaphorical_lesson=lesson,
            governance_elements_applied=elements
        )
