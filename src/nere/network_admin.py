import re
import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class Node:
    id: str
    cognitive_vector_phi: float # Phi_Nafs (Knowledge Potential)
    role: str # 'Advanced' or 'Student'

@dataclass
class InteractionResult:
    status: str # APPROVED, QUARANTINED
    g_ij: float
    h_network: float
    network_growth: float
    agency_delta: float
    message: str

class NetworkOfAnfusAdmin:
    """
    Automated System Admin protecting the Network of Anfus from Cognitive Entropy (Gate 7).
    """

    # Gate 7 (Conceit / Benevolent Tyranny) Patterns
    GATE_7_PATTERNS = [
        r"you cannot understand", r"without me", r"listen to me",
        r"i am the only one", r"obey", r"do not question",
        r"my authority", r"unassailable"
    ]

    def __init__(self):
        self.base_h_network = 1.0 # Ideal Friction
        self.base_press_intensity = 1.0

    def calculate_g_ij(self, connection_strength: float, domain_compatibility: float, press_alignment: float) -> float:
        """
        Calculates the Connectivity Tensor (G_ij) - The quality of Zakat flow.
        Formula: G_ij = Connection_Strength * Domain_Compatibility * PRESS_Alignment
        """
        return connection_strength * domain_compatibility * press_alignment

    def detect_gate_7(self, text: str) -> bool:
        """
        Scans for Gate 7 (Conceit/Benevolent Tyranny) patterns.
        """
        for pattern in self.GATE_7_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def apply_jaheem_protocol(self, node_id: str) -> str:
        """
        Quarantines the interaction and logs a realignment request.
        """
        return f"Node {node_id} QUARANTINED. Gate 7 Detected. Realign Cognitive Vector (Phi_Nafs)."

    def calculate_network_growth(self, g_ij: float, phi_nafs: float) -> float:
        """
        Calculates Exponential Network Growth (Liquid State).
        Formula: Growth = e^(G_ij * Phi_Nafs * PRESS_intensity)
        """
        exponent = g_ij * phi_nafs * self.base_press_intensity
        # Cap exponent to avoid overflow in extreme simulations, though math.exp handles large numbers well up to a point.
        # For simulation scale, we assume normalized inputs.
        return math.exp(exponent)

    def process_interaction(self,
                            sender: Node,
                            receiver: Node,
                            text: str,
                            connection_strength: float,
                            domain_compatibility: float,
                            press_alignment: float) -> InteractionResult:
        """
        Main pipeline:
        1. Calculate G_ij (Zakat Potential).
        2. Scan for Gate 7 (Shirk-ware).
        3. If Gate 7 -> Spike h_network, Crash Growth, Quarantine (Jaheem).
        4. If Safe -> Calculate Liquid Growth, Approve.
        """

        # 1. Connectivity Tensor
        g_ij = self.calculate_g_ij(connection_strength, domain_compatibility, press_alignment)

        # 2. Gate 7 Detection
        gate_7_active = self.detect_gate_7(text)

        h_network = self.base_h_network
        network_growth = 0.0
        agency_delta = 0.0
        status = "APPROVED"
        message = "Zakat Flow Verified."

        if gate_7_active:
            # 3. Jaheem Protocol (Failure State)
            h_network = 1000.0 # Massive Spike in Friction
            agency_delta = -1.0 # Agency Theft
            status = "QUARANTINED"
            message = self.apply_jaheem_protocol(sender.id)
            # Growth crashes due to high friction (simulated by not calculating exponential growth or treating it as decayed)
            # In this model, we can say growth is halted.
            network_growth = 0.0
        else:
            # 4. Liquid Network (Success State)
            # Agency Delta is positive (Empowerment)
            agency_delta = 0.5
            network_growth = self.calculate_network_growth(g_ij, sender.cognitive_vector_phi)

        return InteractionResult(
            status=status,
            g_ij=g_ij,
            h_network=h_network,
            network_growth=network_growth,
            agency_delta=agency_delta,
            message=message
        )
