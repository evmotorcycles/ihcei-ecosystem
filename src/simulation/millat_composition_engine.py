
import numpy as np
import random

class MillatCompositionEngine:
    """
    Implements the physics engine for Millat (Compositional Style/Syntax).
    Operationalizes the Absolute Divine Governance Equation (ADGE): E = U * D^2.
    """

    def __init__(self, size: int = 10):
        """
        Initializes the Millat Codebase (D_syntax Matrix) with perfect semantic alignment.
        """
        self.size = size
        # D_syntax starts as an identity matrix (Perfect Alignment/Tawhid)
        self.D_syntax = np.eye(size)
        self.base_friction = 1.0
        self.corruption_history = []
        self.c_dev_history = []
        self.essence_history = []

    def get_integrity(self) -> float:
        """
        Calculates the integrity of the D_syntax matrix.
        Integrity measures deviation from the perfect Identity Matrix (Tawhid).
        Formula: 1.0 - (Mean Absolute Error vs Identity Matrix)
        """
        # Calculate deviation from the perfect syntax (Identity Matrix)
        identity = np.eye(self.size)
        mae = np.mean(np.abs(self.D_syntax - identity))

        # Integrity decreases as error increases. Clamped at 0.0.
        # We multiply MAE by a factor to make it sensitive.
        integrity = max(0.0, 1.0 - (mae * 5.0))
        return integrity

    def inject_qurayshite_bug(self, corruption_level: float):
        """
        Simulates the "Qurayshite Bug" (Lexicon Corruption).
        Injects fault/noise into the D_syntax matrix, representing localized locution hijacking.

        :param corruption_level: Magnitude of corruption (0.0 to 1.0) applied in this step.
        """
        # Determine number of elements to corrupt based on level
        num_elements = self.size * self.size
        num_corruptions = int(num_elements * corruption_level * 0.1) # Scale factor

        for _ in range(num_corruptions):
            r, c = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            # Corruption replaces precise values (0 or 1) with random noise (Jahileen logic)
            # This destroys the identity structure.
            noise = random.uniform(-0.5, 0.5)
            self.D_syntax[r, c] += noise

        # Ensure values stay somewhat bounded but degraded
        self.D_syntax = np.clip(self.D_syntax, -1.0, 2.0)

    def calculate_systemic_friction(self) -> float:
        """
        Calculates Systemic Friction (hbar_network) based on Millat integrity.
        As alignment drops, friction increases exponentially.
        """
        integrity = self.get_integrity()
        # Friction = Base / Integrity^2 (inverse square law of alignment)
        # If integrity is 1.0, friction is base.
        # If integrity -> 0, friction -> Infinity.
        if integrity < 0.01:
            return float('inf')

        hbar_network = self.base_friction / (integrity ** 2)
        return hbar_network

    def calculate_cognitive_development(self, hbar_network: float) -> float:
        """
        Calculates Cognitive Development (C_dev) using the relationship:
        C_dev = 1 / hbar_network
        """
        if hbar_network == 0:
            return float('inf') # Theoretically impossible infinite development
        if hbar_network == float('inf'):
            return 0.0

        return 1.0 / hbar_network

    def calculate_essence(self, utility: float) -> float:
        """
        Calculates Essence (E) using the ADGE: E = U * D^2
        Here, D is represented by the integrity of the Millat (D_syntax).
        """
        D = self.get_integrity()
        E = utility * (D ** 2)
        return E

    def run_simulation(self, steps: int = 50, corruption_rate: float = 0.05, utility: float = 100.0):
        """
        Runs the simulation loop demonstrating the collapse.
        """
        print(f"Starting Simulation: Steps={steps}, Corruption Rate={corruption_rate}, Utility={utility}")

        for i in range(steps):
            # 1. Inject Corruption (Qurayshite Bug)
            self.inject_qurayshite_bug(corruption_rate)

            # 2. Calculate Physics
            integrity = self.get_integrity()
            hbar_network = self.calculate_systemic_friction()
            c_dev = self.calculate_cognitive_development(hbar_network)
            essence = self.calculate_essence(utility)

            # 3. Record Data
            self.corruption_history.append(1.0 - integrity)
            self.c_dev_history.append(c_dev)
            self.essence_history.append(essence)

            print(f"Step {i+1}: D_integrity={integrity:.4f}, hbar={hbar_network:.4f}, C_dev={c_dev:.4f}, Essence={essence:.4f}")

            if integrity < 0.1:
                print("SYSTEM COLLAPSE: Millat Integrity Critical.")
                break

        return {
            "corruption_history": self.corruption_history,
            "c_dev_history": self.c_dev_history,
            "essence_history": self.essence_history
        }

if __name__ == "__main__":
    engine = MillatCompositionEngine()
    engine.run_simulation()
