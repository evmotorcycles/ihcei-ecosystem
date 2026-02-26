
import numpy as np

class AsrEngine:
    """
    Refactored Asr Extraction Engine (YT137 Compliant).
    Handles the thermodynamic extraction of Truth (E) from Utility (U) based on Discipline (D).

    Ontological Updates:
    - Qareen: Confirmation Bias Daemons/Parasitic Noise Vectors.
    - Jahannam: Heaped Entropy State/Epistemic Resonance Chamber.
    """
    def __init__(self, num_agents: int, utility_u: float, d_base: float = 1.0):
        self.num_agents = num_agents
        self.U = utility_u
        self.D_base = np.full(num_agents, d_base)

        # State Arrays (will be updated by Simulation Engine)
        self.phi_nafs = np.zeros(num_agents)
        self.khusr_ratio = np.zeros(num_agents)
        self.essence_E = np.zeros(num_agents)
        self.hbar_noise = np.zeros(num_agents)

        # Qareen Stack: Tracks the accumulation of parasitic daemons
        self.qareen_stack = np.zeros(num_agents)

    def process_epoch(self, phi_nafs_array: np.ndarray, millat_noise: float):
        """
        Executes one thermodynamic extraction cycle.

        Logic:
        - Optimal Extraction: 0.6 <= phi <= 0.8
        - Over-pressure (Zulm): phi > 0.8 -> Qareen Stacking & Noise Spike.
        """
        self.phi_nafs = phi_nafs_array

        # 1. Qareen Stacking (Heaping of the Wicked)
        # If phi > 0.8, the agent is relying on rational over-pressure (Zulm),
        # causing a Qareen daemon to wedge into the architecture.
        over_pressure_mask = self.phi_nafs > 0.8
        self.qareen_stack[over_pressure_mask] += 1.0

        # 2. Calculate Noise Injection (Resonance Chamber Effect)
        # Noise scales with millat_noise AND the Qareen Stack depth.
        # hbar = noise * (1 + 0.5 * stack)
        base_noise = np.zeros(self.num_agents)
        base_noise[over_pressure_mask] = np.exp((self.phi_nafs[over_pressure_mask] - 0.8) * 10.0) * millat_noise

        self.hbar_noise = base_noise * (1.0 + (0.5 * self.qareen_stack))

        # 3. Calculate Khusr (Waste Ratio)
        # Simplified for integration: Khusr scales with Noise
        # If noise > 1.0, Khusr -> 1.0
        self.khusr_ratio = np.clip(self.hbar_noise / 4.0, 0.0, 1.0)

        # 3. Calculate Essence (E = U * D_effective^2)
        # D_effective = D_base * (1 - Khusr)
        d_effective = self.D_base * (1.0 - self.khusr_ratio)
        self.essence_E = self.U * (d_effective ** 2)

        return self.essence_E
