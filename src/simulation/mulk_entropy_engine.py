import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple

# --- Custom Exception ---
class SystemWideEntropyError(Exception):
    """Raised when Network Cognitive Development (C_dev) collapses due to excessive entropy."""
    pass

# --- 1. Lexicon Mapping (The 10-Element Mulk Tensor) ---
@dataclass
class MulkTensor:
    """
    Represents the Active 10-Element Governance Tensor (d_Theta_Deen).
    Values range from 0.0 (Corrupt) to 1.0 (Aligned).
    """
    terminology: float = 1.0
    roles: float = 1.0
    dues_responsibilities: float = 1.0
    authorities_domains: float = 1.0
    rules: float = 1.0
    policies: float = 1.0
    procedures: float = 1.0
    actions_implications: float = 1.0
    domains_application: float = 1.0
    exceptions: float = 1.0

    def to_array(self) -> np.ndarray:
        return np.array([
            self.terminology, self.roles, self.dues_responsibilities,
            self.authorities_domains, self.rules, self.policies,
            self.procedures, self.actions_implications,
            self.domains_application, self.exceptions
        ])

    def calculate_alignment(self) -> float:
        """Returns the mean alignment score of the tensor."""
        return np.mean(self.to_array())

# --- 2. ADGE Physics Engine Components ---

@dataclass
class Agent:
    """Represents a Conscious Agent (Nafs/Anfus)."""
    id: str
    utility_u: float  # Raw resources/capability
    governance_d: float  # Protocol adherence (0.0 to 1.0)
    knowledge_phi: float = 1.0  # Knowledge potential

    @property
    def essence_e(self) -> float:
        """
        Kitchen Protocol Calculation: E = U * D^2
        """
        return self.utility_u * (self.governance_d ** 2)

class NetworkADGE:
    """
    Simulates the network of Anfus and calculates systemic entropy.
    """
    def __init__(self, agents: List[Agent], governance_tensor: MulkTensor):
        self.agents = agents
        self.governance_tensor = governance_tensor
        self.h_network = 1.0  # Base cognitive noise/resistance (Ideal = 1.0)
        self.c_dev = 0.0
        self.g_ij_matrix = np.ones((len(agents), len(agents))) # Connectivity Tensor

    def update_connectivity(self):
        """
        Updates the G_ij Connectivity Tensor based on agent alignment.
        G_ij = D_i * D_j (Simplified interaction integrity)
        """
        for i, agent_i in enumerate(self.agents):
            for j, agent_j in enumerate(self.agents):
                if i != j:
                    self.g_ij_matrix[i, j] = agent_i.governance_d * agent_j.governance_d

    def calculate_c_dev(self) -> float:
        """
        Calculates Network Cognitive Development (C_dev).
        C_dev ~ (Sum(Phi_i * Phi_j * G_ij) * d_Theta_Deen_Avg) / h_network
        """
        self.update_connectivity()

        interaction_sum = 0.0
        for i, agent_i in enumerate(self.agents):
            for j, agent_j in enumerate(self.agents):
                if i != j:
                    # Flow of purified knowledge
                    flow = agent_i.knowledge_phi * agent_j.knowledge_phi * self.g_ij_matrix[i, j]
                    interaction_sum += flow

        # Governance Alignment Factor
        theta_alignment = self.governance_tensor.calculate_alignment()

        # Physics Calculation
        # C_dev is driven by interactions aligned with Mulk, resisted by h_network
        self.c_dev = (interaction_sum * theta_alignment) / self.h_network

        return self.c_dev

    def simulate_step(self):
        """Executes one simulation step."""
        # 3. Modeling the Failure (Pharaoh Model Check)
        # If Mulk is corrupted (alignment < 0.5), entropy spikes exponentially.
        alignment = self.governance_tensor.calculate_alignment()

        if alignment < 0.5:
            # Systemic Friction Spike (Gate 7: Benevolent Tyranny / Chaos)
            # h_network grows inversely to alignment
            friction_spike = 1.0 / (alignment + 1e-9)  # Avoid division by zero
            self.h_network += friction_spike * 10.0 # Rapid accumulation
        else:
            # Recovery
            self.h_network = max(1.0, self.h_network * 0.95)

        c_dev = self.calculate_c_dev()

        # Critical Threshold Check
        if c_dev < 1.0 and self.h_network > 100.0:
             raise SystemWideEntropyError(
                 f"CRITICAL FAILURE: C_dev collapsed to {c_dev:.4f}. "
                 f"Systemic Entropy (h_network) reached {self.h_network:.2f}."
             )
        return c_dev

# --- 4. Kitchen Protocol Verification ---
def verify_kitchen_protocol(u: float, d: float) -> float:
    """
    Verifies E = U * D^2
    """
    return u * (d ** 2)
