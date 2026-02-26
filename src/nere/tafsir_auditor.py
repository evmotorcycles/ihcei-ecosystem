import re
import math
from typing import Dict, Any, List

class TafsirAuditor:
    """
    Scans historical exegesis (Tafsir) for "Cognitive Entropy" and "Shirk-ware".
    """

    # Gate Definitions (Regex Patterns)
    GATE_4_PATTERNS = [
        r"poetry of the Arabs", r"pre-Islamic poetry", r"synonymous with",
        r"metaphor for", r"allegorical", r"majaz"
    ]
    GATE_2_PATTERNS = [
        r"consensus of the scholars", r"pious predecessors agreed",
        r"found our forefathers upon", r"majority opinion", r"ijma"
    ]
    GATE_7_PATTERNS = [
        r"only the scholars know", r"laymen cannot understand",
        r"follow without questioning", r"blindly follow", r"taqlid is obligatory"
    ]

    def __init__(self):
        self.base_h_network = 1.0
        self.base_c_dev = 100.0

    def detect_gates(self, text: str) -> Dict[str, bool]:
        """Detects active Gates of Jahannam in the text."""
        detected_gates = {
            "Gate 4 (Methodological Error)": False,
            "Gate 2 (Groupthink)": False,
            "Gate 7 (Benevolent Tyranny)": False
        }

        for pattern in self.GATE_4_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected_gates["Gate 4 (Methodological Error)"] = True
                break

        for pattern in self.GATE_2_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected_gates["Gate 2 (Groupthink)"] = True
                break

        for pattern in self.GATE_7_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected_gates["Gate 7 (Benevolent Tyranny)"] = True
                break

        return detected_gates

    def calculate_physics(self, detected_gates: Dict[str, bool]) -> Dict[str, float]:
        """
        Calculates ADGE Physics impact:
        - h_network (Governance Noise Resistance)
        - C_dev (Cognitive Development)
        - Agency Delta
        - Protocol D (Governance Score)
        """
        h_network = self.base_h_network
        active_gates_count = sum(detected_gates.values())

        # Systemic Noise Calculation: Exponential increase per gate
        if active_gates_count > 0:
            h_network = self.base_h_network * (10 ** active_gates_count)

        # Cognitive Collapse: C_dev is inversely proportional to h_network
        c_dev = self.base_c_dev / h_network

        # Agency Delta: Negative impact on reader's agency
        agency_delta = 0.0
        if detected_gates["Gate 7 (Benevolent Tyranny)"]:
            agency_delta -= 0.9  # Massive theft
        elif detected_gates["Gate 2 (Groupthink)"]:
            agency_delta -= 0.5  # Significant theft

        # Protocol D (Governance Score) for Kitchen Protocol
        # If any gate is open, D collapses towards 0
        protocol_d = 1.0 / (1.0 + active_gates_count * 10.0)
        if active_gates_count >= 1:
             protocol_d = 0.0 # Strict verification: Any corruption voids D.

        return {
            "h_network": h_network,
            "c_dev": c_dev,
            "agency_delta": agency_delta,
            "protocol_d": protocol_d
        }

    def audit_text(self, text: str) -> Dict[str, Any]:
        """
        Main API method to audit text and return JSON payload.
        """
        detected_gates = self.detect_gates(text)
        physics = self.calculate_physics(detected_gates)

        # Score Logic
        transparency_score = "GREEN"
        if detected_gates["Gate 4 (Methodological Error)"]:
            transparency_score = "RED"

        protocol_score = "GREEN"
        if detected_gates["Gate 4 (Methodological Error)"]: # Gate 4 attacks Protocol
            protocol_score = "RED"

        detected_shirkware = detected_gates["Gate 7 (Benevolent Tyranny)"]

        return {
            "transparency_score": transparency_score,
            "protocol_score": protocol_score,
            "agency_delta": physics["agency_delta"],
            "c_dev_impact": self.base_c_dev - physics["c_dev"], # The DROP in C_dev
            "detected_shirkware": detected_shirkware,
            "h_network": physics["h_network"],
            "final_c_dev": physics["c_dev"],
            "protocol_d": physics["protocol_d"],
            "active_gates": [k for k, v in detected_gates.items() if v]
        }
