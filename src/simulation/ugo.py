
import numpy as np

class UnifiedGovernanceObject:
    """
    Implements the Unified Governance Object (UGO) class.
    Fuses Structural Laws (Mulk) with Syntactical Code (Millat) to compute
    physical realities (D, E, h_network, C_dev).
    """
    def __init__(self, name, mulk_tensor, millat_matrix, utility_u, base_friction=1.0, knowledge_flow=100.0):
        """
        Initializes the UGO with the structural laws (Mulk) and the operating syntax (Millat).

        :param name: Identifier string (e.g., "Abrahamic Governance").
        :param mulk_tensor: 10-element array representing structural laws (Roles, Rules, etc.).
        :param millat_matrix: 10x10 matrix representing the Divine Lexicon/Compositional Style.
        :param utility_u: Base Utility/Resources (U).
        :param base_friction: Starting friction value (default 1.0).
        :param knowledge_flow: Available cognitive flow (default 100.0).
        """
        self.name = name
        # Mulk: The 10-dimensional vector of Governance
        self.mulk_tensor = np.array(mulk_tensor, dtype=float)
        # Millat: The 10x10 transformation matrix
        self.millat_matrix = np.array(millat_matrix, dtype=float)

        # ADGE Input Variables
        self.U = utility_u
        self.base_friction = base_friction
        self.knowledge_flow = knowledge_flow

        # Computed ADGE State
        self.active_governance = None
        self.distortion = 0.0
        self.D = 0.0          # Discipline/Ethics
        self.E = 0.0          # Essence
        self.h_network = 0.0  # Systemic Friction
        self.c_dev = 0.0      # Cognitive Development

    def compile_reality(self):
        """
        Executes the mathematical transformation and calculates ADGE metrics.
        """
        # 1. Apply the Syntactical Code (Millat) to the Structural Laws (Mulk)
        # Millat acts as the interpreter/compiler for Mulk.
        self.active_governance = np.dot(self.millat_matrix, self.mulk_tensor)

        # 2. Calculate Lexicon Distortion (The "Qurayshite Bug")
        # If Millat is pure (Identity Matrix), active_governance matches mulk_tensor perfectly.
        # Distortion is the Euclidean distance between intended Mulk and applied Mulk.
        # This represents semantic drift or hijacking.
        self.distortion = np.linalg.norm(self.active_governance - self.mulk_tensor)

        # 3. Calculate Discipline (D)
        # D shatters as distortion increases. Perfect alignment yields D = 1.0.
        # Formula: D = 1 / (1 + Distortion)
        self.D = 1.0 / (1.0 + self.distortion)

        # 4. Calculate Master Equation: Essence (E = U * D^2)
        # Demonstrates that Essence is highly sensitive to Discipline (squared term).
        self.E = self.U * (self.D ** 2)

        # 5. Calculate Systemic Friction (h_network) and Cognitive Development (C_dev)
        # Friction scales exponentially with lexical corruption (The "Chunks of Darkness" / Kisafan)
        # C_dev is inversely proportional to friction.
        self.h_network = self.base_friction * np.exp(self.distortion)

        if self.h_network == 0:
             self.c_dev = float('inf')
        else:
             self.c_dev = self.knowledge_flow / self.h_network

        return self.get_metrics()

    def get_metrics(self):
        """
        Returns a formatted dictionary of the calculated metrics.
        """
        return {
            "Model": self.name,
            "Utility (U)": f"{self.U:,.2f}",
            "Lexicon Distortion": f"{self.distortion:.4f}",
            "Discipline (D)": f"{self.D:.4f}",
            "Systemic Friction (h_net)": f"{self.h_network:,.2f}",
            "Cognitive Dev (C_dev)": f"{self.c_dev:.4f}",
            "Total Essence (E)": f"{self.E:,.2f}"
        }
