
import numpy as np

class AsrEngine:
    """
    Refactored Asr Extraction Engine.
    Handles the thermodynamic extraction of Truth (E) from Utility (U) based on Discipline (D).
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

    def process_epoch(self, phi_nafs_array: np.ndarray, millat_noise: float):
        """
        Executes one thermodynamic extraction cycle.

        Logic:
        - Optimal Extraction: 0.6 <= phi <= 0.8
        - Over-pressure (Zulm): phi > 0.8 -> Spikes Noise & Khusr
        - Under-pressure: phi < 0.6 -> Low Yield
        """
        self.phi_nafs = phi_nafs_array

        # 1. Calculate Over-pressure Noise Injection (Exponential)
        # If phi > 0.8, noise = exp((phi - 0.8) * 10) * millat_noise
        over_pressure_mask = self.phi_nafs > 0.8
        self.hbar_noise[:] = 0.0 # Reset
        self.hbar_noise[over_pressure_mask] = np.exp((self.phi_nafs[over_pressure_mask] - 0.8) * 10.0) * millat_noise

        # 2. Calculate Khusr (Waste Ratio)
        # Simplified for integration: Khusr scales with Noise
        # If noise > 1.0, Khusr -> 1.0
        self.khusr_ratio = np.clip(self.hbar_noise / 4.0, 0.0, 1.0)

        # 3. Calculate Essence (E = U * D_effective^2)
        # D_effective = D_base * (1 - Khusr)
        d_effective = self.D_base * (1.0 - self.khusr_ratio)
        self.essence_E = self.U * (d_effective ** 2)

        return self.essence_E
