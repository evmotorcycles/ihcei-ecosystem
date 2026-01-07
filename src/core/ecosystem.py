from src.core.adge import ADGE
from src.core.tqg_cfe import TQGCFE
from src.core.nere import NERE

class IHCEIEcosystem:
    """
    IHCEI Ecosystem (Integrated Human-Centric Ethical Intelligence).
    Coordinates ADGE, TQG-CFE, and NERE.
    """

    def __init__(self):
        self.adge = ADGE()
        self.tqg_cfe = TQGCFE()
        self.nere = NERE()

    def process_state(self, state_data: dict) -> dict:
        """
        Processes the system state through the ecosystem components.

        Args:
            state_data (dict): Input data containing 'coherence', 'alignment', 'mass_energy', 'radius', 'decision_metrics'.

        Returns:
            dict: Comprehensive report including ADGE metrics, Field potentials, and NERE audit results.
        """
        # 1. ADGE Calculations
        coherence = state_data.get('coherence', 0.5)
        alignment = state_data.get('alignment', 0.5)
        adge_metrics = self.adge.calculate_metrics(coherence, alignment)

        # 2. TQG-CFE Calculations
        mass_energy = state_data.get('mass_energy', 100.0)
        radius = state_data.get('radius', 10.0)
        field_potential = self.tqg_cfe.calculate_field_potential(mass_energy, radius)

        # 3. NERE Audit
        # We assume the decision to act on this state depends on the metrics.
        # Construct a decision vector based on ADGE metrics for auditing.
        # If 'utility' is provided in state_data (e.g. material profit), use it; otherwise default to C_dev.
        utility = state_data.get('utility', adge_metrics['c_dev'])

        decision_vector = {
            'transparency': coherence, # Metaphor: high coherence implies clarity/transparency
            'fairness': alignment,     # Metaphor: high alignment implies fairness/justice
            'utility': utility
        }
        nere_audit = self.nere.audit_decision(decision_vector)

        return {
            "adge_metrics": adge_metrics,
            "field_potential": field_potential,
            "nere_audit": nere_audit
        }
