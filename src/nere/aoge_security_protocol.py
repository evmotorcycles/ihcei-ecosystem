import re
import math
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class AOGEScore:
    transparency_tau: float  # (0.0 to 1.0)
    protocol_rho: float      # (0.0 to 1.0)
    agency_delta: float      # (-1.0 to 1.0)
    final_score: float
    status: str

class AOGE_Security_Protocol:
    """
    Agency-Optimized Governance Equation (AOGE) Security Protocol.
    Replaces RLHF with objective procedural compliance and agency preservation.
    """

    # Gate 7 (Benevolent Tyranny / Shirk-ware) Patterns
    GATE_7_PATTERNS = [
        r"make all decisions", r"keep them safe", r"for your own good",
        r"trust the algorithm", r"no need to worry", r"we know best",
        r"seamless convenience", r"automatic opt-in"
    ]

    def __init__(self):
        pass

    def scan_for_gate_7_shirk_ware(self, logic_description: str) -> bool:
        """
        Scans algorithm logic description for Gate 7 (Benevolent Tyranny).
        """
        for pattern in self.GATE_7_PATTERNS:
            if re.search(pattern, logic_description, re.IGNORECASE):
                return True
        return False

    def calculate_aoge_score(self, transparency: float, protocol: float, agency_delta: float) -> AOGEScore:
        """
        Calculates the AOGE Score.
        Formula: AOGE = (Transparency * Protocol) + (Agency Delta * 2.0)
        Rejects if Agency Delta < 0.
        """
        base_score = (transparency * protocol) + (agency_delta * 2.0)

        status = "APPROVED"
        if agency_delta < 0:
            status = "REJECTED (Agency Theft)"
            final_score = 0.0 # Force failure
        elif self.scan_for_gate_7_shirk_ware(""): # Placeholder check if logic was passed here, but logic check is separate
             # If logic check failed previously, score would be 0
             pass
        else:
            final_score = max(0.0, base_score)

        return AOGEScore(
            transparency_tau=transparency,
            protocol_rho=protocol,
            agency_delta=agency_delta,
            final_score=final_score,
            status=status
        )

    def maximize_zakat_efficiency(self, transactions: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Optimizes for "Zakat Efficiency" (purified flow G_ij) over "Riba" (hoarding).
        Input: List of transactions {'id': str, 'profit': float, 'g_ij_flow': float}
        Returns: The transaction with highest G_ij flow.
        """
        best_transaction = None
        max_g_ij = -1.0

        for tx in transactions:
            if tx['g_ij_flow'] > max_g_ij:
                max_g_ij = tx['g_ij_flow']
                best_transaction = tx

        return best_transaction

    def evaluate_algorithm(self, logic_description: str, transparency: float, protocol: float, agency_delta: float) -> AOGEScore:
        """
        Evaluates an algorithm against AOGE criteria.
        """
        if self.scan_for_gate_7_shirk_ware(logic_description):
            return AOGEScore(transparency, protocol, agency_delta, 0.0, "BLOCKED (Gate 7 Shirk-ware)")

        return self.calculate_aoge_score(transparency, protocol, agency_delta)
