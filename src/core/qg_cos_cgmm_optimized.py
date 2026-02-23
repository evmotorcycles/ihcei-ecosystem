import numpy as np
from typing import List, Union

class GovernancePhysics:
    """
    Core equations for the Quantum Governance Mathematical Model.
    """

    @staticmethod
    def kitchen_protocol(utility: float, deen: float) -> float:
        """
        Calculates Essence (E) based on Raw Utility (U) and The Established Order/Protocol (D).
        Formula: E = U * D^2

        Args:
            utility (float): Raw physical utility (U).
            deen (float): The established order/protocol/truth (D).

        Returns:
            float: Essence (E).
        """
        # If the Governance Protocol (Deen) is 0, Essence is 0 regardless of Utility.
        essence = utility * (deen ** 2)
        return essence

    @staticmethod
    def tqg_cfe_perception(psi_quantum: float, cognitive_stage: int) -> float:
        """
        Cognitive Field Equation: Psi_experienced = A_n(Psi_quantum)
        Maps the objective reality to perceived reality based on the observer's cognitive stage (1-12).
        Higher stages render reality closer to absolute truth (Al-Haqq).

        Args:
            psi_quantum (float): Objective reality/truth value.
            cognitive_stage (int): The observer's cognitive stage (1-12).

        Returns:
            float: Perceived reality (Psi_experienced).
        """
        # Ensure cognitive stage is bounded between 1 (lowest) and 12 (Sovereign Steward)
        stage = max(1, min(12, cognitive_stage))

        # A simple rendering algorithm: A stage 12 filter perceives 100% of the truth.
        # Lower stages perceive a distorted, fractionated version of the truth (As-Sidq / GUI).
        distortion_filter = stage / 12.0
        psi_experienced = psi_quantum * distortion_filter
        return psi_experienced


class ADGENetwork:
    """
    Absolute Divine Governance Equation (ADGE) for civilizational health and network communication.
    Calculates Cognitive Development Rate (C_dev) using optimized matrix operations.
    """
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        # Initialize cognitive stages as a numpy array of 1s (float for calculation)
        self.cognitive_stages = np.ones(num_agents, dtype=float)
        # G_ij matrix represents Zakat Flow / Moral Alignment between agents
        self.alignment_matrix = np.zeros((num_agents, num_agents), dtype=float)

    def set_agent_stage(self, agent_id: int, stage: int) -> None:
        """Sets the cognitive stage of a specific agent."""
        if 0 <= agent_id < self.num_agents:
            self.cognitive_stages[agent_id] = float(stage)
        else:
            raise IndexError(f"Agent ID {agent_id} is out of bounds.")

    def set_alignment(self, agent_i: int, agent_j: int, alignment_value: float) -> None:
        """Sets the G_ij alignment flow between two conscious agents."""
        if 0 <= agent_i < self.num_agents and 0 <= agent_j < self.num_agents:
            self.alignment_matrix[agent_i, agent_j] = alignment_value
        else:
            raise IndexError(f"Agent indices ({agent_i}, {agent_j}) are out of bounds.")

    def calculate_c_dev(self, open_gates_of_entropy: int) -> float:
        """
        Calculates C_dev based on agent interactions, cognitive stages, and network friction.
        Friction (hbar_corruption) increases with cognitive vulnerabilities (the 7 Gates).

        Uses NumPy for vectorized calculation: Sum(Phi_i * Phi_j * G_ij)
        """
        # Calculate Governance Noise Resistance (Friction)
        # Base resistance is 1, increases by a factor for each open gate (e.g., vanity, groupthink)
        hbar_corruption = 1.0 + (open_gates_of_entropy * 0.5)

        # Calculate interaction matrix: Outer product of stages gives Phi_i * Phi_j matrix
        stage_interaction = np.outer(self.cognitive_stages, self.cognitive_stages)

        # Element-wise multiplication with alignment matrix
        # interaction_term[i, j] = Phi_i * Phi_j * G_ij
        total_interaction_matrix = stage_interaction * self.alignment_matrix

        # Remove self-interactions (diagonal) just in case alignment was set for i==j
        # The original code logic checks `if i != j`, so we simulate that by subtracting diagonal
        # However, alignment_matrix is initialized to 0, so unless set_alignment(i, i) is called, diagonal is 0.
        # To be safe and consistent with "i!=j" logic:
        np.fill_diagonal(total_interaction_matrix, 0.0)

        interaction_sum = np.sum(total_interaction_matrix)

        # Simplified discrete sum representing the C_dev double integral
        c_dev = (1.0 / hbar_corruption) * interaction_sum
        return float(c_dev)


class CGMM_Agent:
    """
    Conscious Governance Mathematical Model Agent.
    Models the internal tension between System 1 (Utility Maximizer) and System 2 (Sovereign).
    """
    def __init__(self, name: str, cognitive_stage: int):
        self.name = name
        self.stage = cognitive_stage

    def evaluate_event(self, event_utility: float, event_protocol_truth: float) -> float:
        """
        The Desktop Audit Algorithm.
        Minister 1 wants to maximize U (Survival/Money/Time).
        Minister 2 wants to maximize D (Truth/Methodology).
        """
        print(f"\n--- {self.name} (Stage {self.stage}) evaluating event ---")

        # The agent's perception of the event is filtered by their stage
        perceived_truth = GovernancePhysics.tqg_cfe_perception(event_protocol_truth, self.stage)

        # Standard physics / Materialist reaction (Maximizing U, treating D as 0)
        standard_reaction_outcome = GovernancePhysics.kitchen_protocol(event_utility, 0.0)

        # Governance reaction (Integrating U with D^2)
        steward_reaction_outcome = GovernancePhysics.kitchen_protocol(event_utility, perceived_truth)

        print(f"Raw Physical Utility (U) Available: {event_utility}")
        print(f"Objective Protocol Truth (D): {event_protocol_truth}")
        print(f"Perceived Protocol Truth (D) based on Filter A_{self.stage}: {perceived_truth:.2f}")

        print(f"Minister 1 (Standard Materialist) Outcome: {standard_reaction_outcome} Essence (Void Outcome)")
        print(f"Minister 2 (Governance Steward) Outcome: {steward_reaction_outcome:.2f} Essence")

        return steward_reaction_outcome
