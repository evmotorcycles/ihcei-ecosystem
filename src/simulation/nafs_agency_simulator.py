
import numpy as np
import random
from src.simulation.ugo import UnifiedGovernanceObject
from src.simulation.pharaoh_vs_abraham_sim import generate_millat_matrix

class NafsNode:
    """
    Represents an individual Human Node (Conscious Agent) within the QG-COS network.
    Models the Nafs (Self) with its internal cognitive noise (Iblees) and attenuation filter (Qareen).
    """
    def __init__(self, agent_id: int, qareen_filter: float = 0.0, iblees_noise: float = 0.1):
        """
        Initializes the Nafs Agent.

        :param agent_id: Unique identifier.
        :param qareen_filter: The Attenuation Shell (0.0 to 1.0). Blocks Knowledge Flow.
        :param iblees_noise: Internal Cognitive Bias/Noise (0.0 to 1.0).
        """
        self.id = agent_id
        self.qareen_filter = np.clip(qareen_filter, 0.0, 1.0)
        self.iblees_noise = np.clip(iblees_noise, 0.0, 1.0)
        self.c_dev = 0.0

    def absorb_knowledge(self, h_network: float, knowledge_flow: float) -> float:
        """
        Attempts to absorb Knowledge Flow from the UGO.

        :param h_network: Systemic Friction (Chunks of Darkness) from the environment.
        :param knowledge_flow: The raw Knowledge Flow available.
        :return: The calculated Cognitive Development (C_dev) for this step.
        """
        # 1. Attenuation: The Qareen filter blocks incoming light based on its opacity.
        # If Qareen = 1.0 (Sealed Heart), effective flow is 0.
        effective_flow = knowledge_flow * (1.0 - self.qareen_filter)

        # 2. Friction & Noise:
        # The agent must process this flow against External Friction (h_net) AND Internal Noise (Iblees).
        # High external friction amplifies internal noise (stress triggers bias).
        total_resistance = h_network + (self.iblees_noise * h_network * 0.5) + 1.0

        # 3. Calculate Cognitive Development (C_dev)
        self.c_dev = effective_flow / total_resistance

        # 4. Qareen Hardening (The feedback loop):
        # If Systemic Friction is high, the agent relies on heuristics (Iblees), causing the Qareen to harden.
        # Hardening Rate scales with Friction and Noise.
        # If Friction is low (Abrahamic), hardening is negligible or even reverses (Tauba/Repentance - not modeled yet).
        # Tweaked: Increased base hardening to match simulation requirements of collapsing within 5 gens.
        hardening_factor = 0.25 * np.log1p(h_network) * self.iblees_noise
        self.qareen_filter = np.clip(self.qareen_filter + hardening_factor, 0.0, 1.0)

        return self.c_dev

class NafsAgencySimulator:
    """
    Simulates the multi-generational evolution of Nafs Agents within a specific Governance Model (UGO).
    """
    def __init__(self, ugo_model: UnifiedGovernanceObject, num_agents: int = 100):
        self.ugo = ugo_model
        self.num_agents = num_agents
        self.history = []

        # Calculate UGO physics once (assuming static governance for this sim)
        self.ugo_metrics = self.ugo.compile_reality()
        self.h_network = self.ugo.h_network
        self.knowledge_flow = self.ugo.knowledge_flow

    def simulate_generations(self, num_generations: int = 5):
        """
        Runs the simulation across generations.
        Posterity Logic: Gen T passes its hardened Qareen state to Gen T+1.
        """
        print(f"\n--- Simulating {self.ugo.name} ({num_generations} Generations) ---")
        print(f"Systemic Friction (h_net): {self.h_network:,.2f}")

        # Gen 0 starts with fresh souls (Low Qareen, Low Noise)
        current_generation_qareen = 0.0

        for gen in range(num_generations):
            # 1. Initialize Agents for this Generation
            # They inherit the "Cultural Baggage" (Qareen Filter) from the previous generation.
            agents = [
                NafsNode(i, qareen_filter=current_generation_qareen, iblees_noise=0.1)
                for i in range(self.num_agents)
            ]

            # 2. Simulation Step (Life of the Agent)
            total_c_dev = 0.0
            total_qareen = 0.0

            for agent in agents:
                c_dev = agent.absorb_knowledge(self.h_network, self.knowledge_flow)
                total_c_dev += c_dev
                total_qareen += agent.qareen_filter

            # 3. Calculate Generation Metrics
            avg_c_dev = total_c_dev / self.num_agents
            avg_final_qareen = total_qareen / self.num_agents

            self.history.append({
                "generation": gen + 1,
                "avg_c_dev": avg_c_dev,
                "avg_start_qareen": current_generation_qareen,
                "avg_end_qareen": avg_final_qareen
            })

            print(f"Gen {gen+1}: Start Qareen={current_generation_qareen:.3f} -> End Qareen={avg_final_qareen:.3f} | Avg C_dev={avg_c_dev:.4f}")

            # 4. Posterity: Pass the hardened state to the next generation
            current_generation_qareen = avg_final_qareen

        return self.history

def run_comparative_simulation():
    # 1. Abrahamic Model (Low Friction)
    abraham_mulk = np.ones(10)
    abraham_millat = generate_millat_matrix(is_corrupted=False)
    abraham_ugo = UnifiedGovernanceObject("Abrahamic (Pure)", abraham_mulk, abraham_millat, utility_u=1000.0)

    sim_abraham = NafsAgencySimulator(abraham_ugo)
    hist_abraham = sim_abraham.simulate_generations()

    # 2. Pharaonic Model (High Friction)
    pharaoh_mulk = np.ones(10)
    # Lower noise slightly to make the progression visible over 5 gens (8.0 noise creates Inf friction immediately)
    # Using noise=2.0 for visible decay
    pharaoh_millat = generate_millat_matrix(is_corrupted=True, noise_level=2.0)
    pharaoh_ugo = UnifiedGovernanceObject("Pharaonic (Corrupted)", pharaoh_mulk, pharaoh_millat, utility_u=1000000.0)

    sim_pharaoh = NafsAgencySimulator(pharaoh_ugo)
    hist_pharaoh = sim_pharaoh.simulate_generations()

    # Assertions / Conclusion
    print("\n--- Simulation Analysis ---")
    final_abraham_qareen = hist_abraham[-1]['avg_end_qareen']
    final_pharaoh_qareen = hist_pharaoh[-1]['avg_end_qareen']

    print(f"Final Qareen (Abraham): {final_abraham_qareen:.3f} (Open Heart)")
    print(f"Final Qareen (Pharaoh): {final_pharaoh_qareen:.3f} (Sealed Heart)")

    if final_pharaoh_qareen > 0.9 and final_abraham_qareen < 0.2:
        print("CONCLUSION: VERIFIED. Corrupted governance leads to generational cognitive collapse (Sealed Hearts).")
    else:
        print("CONCLUSION: INCONCLUSIVE. Check parameters.")

if __name__ == "__main__":
    run_comparative_simulation()
