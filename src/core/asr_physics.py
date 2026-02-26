
import numpy as np

class AsrPhysicsEngine:
    """
    Models the 'Asr' (Epoch/Time) as a physical force of Temporal Compression.
    Implements the 'Khusr' (Loss) dynamic and the shielding effect of the 4 Conditions.
    """
    def __init__(self, compression_factor: float = 1.0):
        """
        :param compression_factor: The intensity of the Asr squeezing force (default 1.0).
        """
        self.compression = compression_factor

    def calculate_khusr_loss(self, iman: float, amal_salih: float, haqq: float, sabr: float) -> float:
        """
        Calculates the Thermodynamic Loss (Khusr) based on the agent's 4 shielding attributes.
        Formula: Loss = Compression * (1.0 - (Iman * Amal * Haqq * Sabr)^(1/4))

        If attributes are 0.0 (An'am state), Loss is Max (1.0 * Compression).
        If attributes are 1.0 (Sovereign state), Loss is 0.0.
        """
        # Normalize inputs to 0.0 - 1.0
        iman = np.clip(iman, 0.0, 1.0)
        amal = np.clip(amal_salih, 0.0, 1.0)
        haqq = np.clip(haqq, 0.0, 1.0)
        sabr = np.clip(sabr, 0.0, 1.0)

        # Geometric mean of shielding attributes implies all are necessary.
        # If any one is missing (0), the shield fails completely (Loss = Max).
        shield_integrity = (iman * amal * haqq * sabr) ** 0.25

        loss = self.compression * (1.0 - shield_integrity)
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
