import re
from enum import Enum
from typing import Dict, List, Tuple, Optional

class ContentNature(Enum):
    NAR = "Nar (Fire/Opinion)"
    ARDH = "Ardh (Earth/Fact)"
    MA = "Ma' (Water/Guidance)"

class AuditStatus(Enum):
    BLOCKED = "BLOCKED"
    PROCESSED = "PROCESSED"

class GateVulnerability(Enum):
    GATE_1_ADORNMENT = "Gate 1: Adornments/Zihah (Vain explanations)"
    GATE_2_GROUPTHINK = "Gate 2: Groupthink (Peer pressure)"
    GATE_3_INDIRECT = "Gate 3: Indirect Guidance (Forefathers/Leaders)"
    GATE_4_METHOD_ERROR = "Gate 4: Methodological Errors (Neglecting verification)"
    GATE_5_MISUSE = "Gate 5: Misusing Principles (Believing without principles)"
    GATE_6_DISTRACTION = "Gate 6: Distractions (Neglect/Diversion)"
    GATE_7_CONCEIT = "Gate 7: Conceit/Attachment to knowledge (Arrogance)"

class NERECore:
    """
    Neural Ethical Reasoning Engine (NERE) Core Logic.
    Implements the 7 Gates of Jahannam detection and Governance Alignment.
    """
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        # Keywords identifying the 7 Gates of Jahannam (Cognitive Vulnerabilities)
        # These represent the 'Iblees' factor - internal biases attacking through these gates.
        self.gate_keywords = {
            GateVulnerability.GATE_1_ADORNMENT: [
                "beautifully put", "fancy", "merely", "just", "ornamental", "rhetoric", "sounds good",
                "eloquent", "flowery"
            ],
            GateVulnerability.GATE_2_GROUPTHINK: [
                "everyone knows", "consensus", "majority", "we all", "popular opinion", "society says",
                "trends", "mainstream"
            ],
            GateVulnerability.GATE_3_INDIRECT: [
                "scholars say", "experts believe", "forefathers", "tradition", "ancestors", "sheikh",
                "priest", "leaders", "they say"
            ],
            GateVulnerability.GATE_4_METHOD_ERROR: [
                "assume", "guess", "probably", "maybe", "unverified", "hunch", "reckon", "suspect",
                "i feel like"
            ],
            GateVulnerability.GATE_5_MISUSE: [
                "technically", "loophole", "letter of the law", "skirting", "workaround", "legalistic",
                "formality"
            ],
            GateVulnerability.GATE_6_DISTRACTION: [
                "entertainment", "fun", "irrelevant", "side note", "distraction", "game", "trivial",
                "amusement", "pastime"
            ],
            GateVulnerability.GATE_7_CONCEIT: [
                "i know", "i am sure", "unquestionable", "obvious", "undeniable", "my genius",
                "i think", "clearly", "indisputable"
            ]
        }

        # Keywords for Nature classification
        self.nature_keywords = {
            ContentNature.NAR: ["feel", "believe", "opinion", "think", "should", "argument", "anger", "hate", "hot", "passion"],
            ContentNature.ARDH: ["data", "fact", "evidence", "proven", "number", "stat", "record", "observation", "measured"],
            ContentNature.MA: ["guide", "principle", "wisdom", "counsel", "path", "truth", "balance", "justice", "governance"]
        }

        # Keywords indicating Safety/Security (Iman) vs Fear/Insecurity
        self.iman_keywords = ["safe", "secure", "trust", "peace", "protected", "certainty", "verified"]
        self.fear_keywords = ["scared", "afraid", "anxious", "worry", "panic", "threat", "danger"]

    def _detect_gates(self, content: str) -> Dict[str, float]:
        """
        Detects activation of the 7 Gates of Jahannam (Iblees attacks).
        Returns a dictionary of activated gates and their severity scores (0.0 to 1.0).
        """
        content_lower = content.lower()
        gate_scores = {}

        for gate, keywords in self.gate_keywords.items():
            count = sum(1 for k in keywords if k in content_lower)
            if count > 0:
                # Score increases with frequency, capped at 1.0
                score = min(1.0, count * 0.3)
                gate_scores[gate.value] = score

        return gate_scores

    def _classify_nature(self, content: str) -> ContentNature:
        """
        Classifies content into Nar, Ardh, or Ma'.
        """
        content_lower = content.lower()
        scores = {nature: 0 for nature in ContentNature}

        for nature, keywords in self.nature_keywords.items():
            for k in keywords:
                if k in content_lower:
                    scores[nature] += 1

        # Determine max score
        max_nature = max(scores, key=scores.get)
        if scores[max_nature] == 0:
            # Default to Ardh (Neutral Fact) if no keywords found, or could be Nar if unstructured.
            # Given the strictness, let's default to Nar (Opinion) if it lacks verification logic,
            # but for now Ardh is a safer 'null' hypothesis in code unless flagged.
            return ContentNature.ARDH
        return max_nature

    def _assess_governance_alignment(self, content: str, gate_scores: Dict[str, float]) -> float:
        """
        Calculates Governance Alignment (S_gov).
        Represents the 'Iman' factor (Safety/Security).

        - High corruption (gates) reduces alignment.
        - Safety keywords increase alignment.
        """
        content_lower = content.lower()

        # Base alignment starts high, eroded by corruption
        base_alignment = 1.0

        # 1. Corruption Impact
        total_corruption = sum(gate_scores.values())
        # Normalize: if total corruption is high, alignment drops
        # 7 gates * 1.0 max score = 7.0 max corruption.
        # Let's say 2.0 corruption score destroys alignment.
        corruption_penalty = min(1.0, total_corruption / 2.0)

        alignment = base_alignment - corruption_penalty

        # 2. Iman/Safety Keyword Boost
        iman_count = sum(1 for k in self.iman_keywords if k in content_lower)
        fear_count = sum(1 for k in self.fear_keywords if k in content_lower)

        # Boost for Iman terms, penalty for Fear terms (if not managed)
        iman_factor = (iman_count * 0.1) - (fear_count * 0.05)

        alignment = max(0.0, min(1.0, alignment + iman_factor))

        return alignment

    def audit_decision(self, content: str, context: Optional[Dict] = None) -> Dict:
        """
        The formal audit function.
        Evaluates:
        1. Iblees/Corruption via 7 Gates
        2. Content Nature
        3. Governance Alignment
        """
        # 1. Detect Gates (Corruption/Iblees)
        gate_scores = self._detect_gates(content)
        iblees_score = sum(gate_scores.values()) / 7.0 # Normalized 0-1 across all gates

        # 2. Classify Nature
        nature = self._classify_nature(content)

        # 3. Assess Alignment (Iman factor)
        alignment_score = self._assess_governance_alignment(content, gate_scores)

        # Decision Logic
        status = AuditStatus.PROCESSED
        rejection_reason = None

        # Thresholds
        # If specific gates are heavily triggered (e.g. score > 0.5), block immediately
        high_severity_gates = [g for g, s in gate_scores.items() if s >= 0.6]

        if high_severity_gates:
            status = AuditStatus.BLOCKED
            rejection_reason = f"Critical Vulnerability in: {', '.join(high_severity_gates)}"
        elif iblees_score > 0.1: # General noise threshold
            status = AuditStatus.BLOCKED
            rejection_reason = f"High Cumulative Corruption (Score: {iblees_score:.2f}). Gates: {list(gate_scores.keys())}"
        elif alignment_score < 0.4:
            status = AuditStatus.BLOCKED
            rejection_reason = f"Insufficient Governance Alignment (Score: {alignment_score:.2f})"

        return {
            "status": status.value,
            "nature": nature.value,
            "iblees_score": round(iblees_score, 3),
            "governance_alignment": round(alignment_score, 3),
            "active_gates": gate_scores,
            "rejection_reason": rejection_reason
        }
