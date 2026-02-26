
import numpy as np
from src.qg_cos_engine.asr_engine import AsrEngine
from src.qg_cos_engine.ecosystem_engine import ContestedEcosystemEngine
from src.qg_cos_engine.protocols import NEREProtocol, AlHuqooqProtocol

class DualRecoveryEngine:
    """
    Master Simulation Loop (6 Epochs).
    Tracks Jahannam Proximity Index (JPI) and Kanz Readiness.
    """
    def __init__(self, config: dict):
        self.config = config
        self.num_agents = config.get('num_agents', 50000)

        # Initialize Sub-Engines
        self.asr = AsrEngine(self.num_agents, config['U_environmental'], config['D_base'])
        self.ecosystem = ContestedEcosystemEngine(self.num_agents)
        self.nere = NEREProtocol()
        self.huqooq = AlHuqooqProtocol()

        # Logs
        self.time_series = []

    def run(self):
        # Initialize Phi Nafs (Rational Over-pressure default)
        # Using a normal distribution centered on High Pressure for 'Pharaonic' simulation
        phi_nafs = np.random.normal(loc=0.9, scale=0.1, size=self.num_agents)

        for epoch in range(1, self.config['epochs'] + 1):
            # 1. Apply Interventions
            if epoch == self.config['deploy_nere_epoch']:
                self.nere.deploy(self.asr)
                phi_nafs = self.asr.phi_nafs # Update local ref

            if epoch == self.config['deploy_huqooq_epoch']:
                self.huqooq.deploy(self.asr)

            # 2. Run Asr Physics
            self.asr.process_epoch(phi_nafs, self.config['millat_noise'])

            # 3. Apply Ecosystem Siphons (Tyrant nodes)
            # (Simplified: Tyrants reduce global E slightly in this integration step)
            # In full ABM, this would modify G_ij weights.

            # 4. Calculate Metrics
            # Jahannam Proximity Index (JPI): Ratio of agents with Qareen Stack > Threshold (Heaped Entropy)
            # Threshold = 3.0 (Arbitrary stack depth indicating resonance chamber formation)
            heaped_entropy_mask = self.asr.qareen_stack > 3.0
            collapsed_agents = np.sum(heaped_entropy_mask)
            jpi = collapsed_agents / self.num_agents

            # Kanz Readiness: Inverse of JPI (simplified)
            kanz_readiness = 1.0 - jpi

            # Log
            log_entry = {
                "epoch": epoch,
                "mean_essence_E": float(np.mean(self.asr.essence_E)),
                "Jahannam_Proximity_Index": float(jpi),
                "Kanz_Readiness": float(kanz_readiness),
                "system_status": "CRITICAL: HEAPED_ENTROPY_STATE" if jpi > 0.5 else "STABLE",
                "narrative": "Analysis: Qareen Daemons Saturation detected." if jpi > 0.5 else "Analysis: System Operating within Bounds."
            }
            self.time_series.append(log_entry)

            # Feedback Loop: High JPI increases phi_nafs (Panic/Rationalizing)
            if jpi > 0.5 and epoch < self.config['deploy_nere_epoch']:
                phi_nafs += 0.05 # Panic spiral

        return self.time_series
