
import numpy as np

class AsrPhysicsEngine:
    """
    Models the 'Asr' (The Pressing) as a physical force of Extraction.
    Implements the OQM metaphor: Extracting Truth (Juice) from Truthfulness (Pomegranate).
    'Khusr' is the Waste/Pulp remaining if the extraction fails.
    """
    def __init__(self, extraction_pressure: float = 1.0):
        """
        :param extraction_pressure: The intensity of the Asr pressing/extraction force (default 1.0).
        """
        self.pressure = extraction_pressure

    def calculate_khusr_loss(self, iman: float, amal_salih: float, haqq: float, sabr: float) -> float:
        """
        Calculates Khusr (Waste/Loss) based on the agent's 4 filtering attributes (The Success Filter).

        Logic:
        - Asr is the Pressure.
        - The 4 Attributes are the Filter Mesh.
        - If Filter is weak (attributes -> 0.0), the output is mostly Pulp/Waste (Loss).
        - If Filter is strong (attributes -> 1.0), the output is pure Juice (Success), Loss is 0.

        Formula: Waste = Pressure * (1.0 - (Iman * Amal * Haqq * Sabr)^(1/4))
        """
        # Normalize inputs to 0.0 - 1.0
        iman = np.clip(iman, 0.0, 1.0)
        amal = np.clip(amal_salih, 0.0, 1.0)
        haqq = np.clip(haqq, 0.0, 1.0)
        sabr = np.clip(sabr, 0.0, 1.0)

        # Geometric mean of shielding attributes implies all are necessary.
        # If any one is missing (0), the shield fails completely (Loss = Max).
        shield_integrity = (iman * amal * haqq * sabr) ** 0.25

        loss = self.pressure * (1.0 - shield_integrity)
        return max(0.0, loss)

    def apply_vector_displacement(self, mulk_tensor: np.ndarray, loss: float) -> np.ndarray:
        """
        Models 'Zulm' as Vector Displacement.
        The Loss function displaces the governance tensor from its orthogonal truth.
        """
        # Displacement is proportional to loss
        displacement_noise = np.random.normal(0, loss * 0.5, mulk_tensor.shape)
        displaced_tensor = mulk_tensor + displacement_noise
        return displaced_tensor
