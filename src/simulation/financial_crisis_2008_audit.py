import sys
import os
import numpy as np
import logging

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.novora.nere import NERE
from src.core.ihcei_2 import IHCEI2
from src.core.ihcei_core import IHCEICore

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class FinancialAgent:
    def __init__(self, agent_id, agent_type, U, D, tau, rho):
        self.id = agent_id
        self.type = agent_type
        self.U = U  # Utility (Raw extraction)
        self.D = D  # Governance (Deen/Ethics)
        self.tau = tau  # Transparency
        self.rho = rho  # Protocol Alignment

    def calculate_essence(self):
        """
        Calculates Essence (E) using the Kitchen Protocol: E = U * D^2
        """
        return self.U * (self.D ** 2)

class FinancialNetwork:
    def __init__(self, num_agents):
        self.agents = []
        self.num_agents = num_agents
        # Initialize Connectivity Tensor (G_ij) with small random values (trust/knowledge flow)
        self.G_ij = np.random.rand(num_agents, num_agents) * 0.1
        self.h_corruption = 1.0  # Base entropy
        self.nere = NERE()
        self.ihcei2 = IHCEI2()

    def add_agent(self, agent: FinancialAgent):
        self.agents.append(agent)

    def update_connectivity(self):
        """
        Updates G_ij based on agent interactions.
        If transparency (tau) is low, trust (G_ij) becomes brittle or fake.
        Rating Agencies (Type C) inject noise.
        """
        for i, agent_i in enumerate(self.agents):
            for j, agent_j in enumerate(self.agents):
                if i == j:
                    self.G_ij[i, j] = 1.0 # Self-trust
                    continue

                # Simplified interaction logic
                # If both agents have low D, they might collude (increase G_ij temporarily)
                # but it's "False Trust" (As-Sidq without Al-Haqq).

                if agent_i.type == "RatingAgency" and agent_j.type == "Bank":
                    # Rubber-stamping: Artificial boost to connectivity
                    self.G_ij[i, j] = 0.9
                    self.G_ij[j, i] = 0.9
                    # But this increases corruption
                    self.h_corruption += 0.05

    def calculate_network_c_dev(self):
        """
        Calculates Network Cognitive Development Rate (C_dev).
        C_dev = (1 / h_corruption) * Sum(Phi_i * Phi_j * G_ij)
        Where Phi is a function of alignment (rho).
        """
        # Phi vector based on rho (Protocol Alignment)
        Phi = np.array([agent.rho for agent in self.agents])

        # Outer product of Phi to get Phi_i * Phi_j matrix
        Phi_matrix = np.outer(Phi, Phi)

        # Element-wise multiplication with G_ij
        # If G_ij is high but Phi is low (corrupt agents communicating), contribution is low?
        # Wait, if rho is low (0.1), 0.1 * 0.1 = 0.01. So bad agents contribute little to C_dev.
        # But if G_ij is artificially high, it might mask it slightly, but rho dominates.

        weighted_connectivity = Phi_matrix * self.G_ij

        # Sum of all interactions
        total_interaction = np.sum(weighted_connectivity)

        # Apply corruption penalty
        # h_corruption acts as resistance.
        if self.h_corruption == 0:
             # Should not happen, but handle div by zero
            return float('inf')

        c_dev = (1.0 / self.h_corruption) * total_interaction
        return c_dev

    def audit_transaction(self, document_text):
        """
        Audits a transaction document using NERE.
        Returns the NERE response.
        """
        return self.nere.reason_ethically(document_text, g_ij_zakat_flow=0.5)

def run_simulation():
    logging.info("Starting 2008 Financial Crisis Audit Simulation")

    # Setup Network
    # 10 Agents: 5 Homeowners, 3 Banks, 2 Rating Agencies
    network = FinancialNetwork(num_agents=10)

    # Create Agents
    # Type A: Homeowner (High U, Low D, Low Tau, Low Rho)
    # U=10 (House), D=0.2 (Can't pay/predatory), Tau=0.1, Rho=0.2
    for i in range(5):
        network.add_agent(FinancialAgent(i, "Homeowner", U=10.0, D=0.2, tau=0.1, rho=0.2))

    # Type B: Bank (Max U, D=0.01)
    # U=100 (Bonuses), D=0.01 (No ethics), Tau=0.1, Rho=0.1
    for i in range(5, 8):
        network.add_agent(FinancialAgent(i, "Bank", U=100.0, D=0.01, tau=0.1, rho=0.1))

    # Type C: Rating Agency (High Corruption injector)
    # U=50, D=0.1, Tau=0.1, Rho=0.1
    for i in range(8, 10):
        network.add_agent(FinancialAgent(i, "RatingAgency", U=50.0, D=0.1, tau=0.1, rho=0.1))

    # Simulation Loop
    steps = 5
    for step in range(steps):
        logging.info(f"--- Simulation Step {step + 1} ---")

        # 1. Update Connectivity (Banks paying Rating Agencies)
        network.update_connectivity()

        # 2. Calculate Essence for Banks (Kitchen Protocol Check)
        for agent in network.agents:
            if agent.type == "Bank":
                E = agent.calculate_essence()
                logging.info(f"Agent {agent.id} (Bank): U={agent.U}, D={agent.D} -> Essence (E) = {E:.4f}")
                if E < 1.0:
                    logging.warning(f"Agent {agent.id} COLLAPSE IMMINENT: Essence near zero.")

        # 3. Calculate Network C_dev (Entropy Explosion Check)
        c_dev = network.calculate_network_c_dev()
        logging.info(f"Network h_corruption: {network.h_corruption:.2f}")
        logging.info(f"Network C_dev: {c_dev:.4f}")

        # 4. NERE Audit of a Toxic Asset
        if step == 2:
            toxic_doc = "Subprime Mortgage Bundle: No verification of income, adjustable rate, strict foreclosure terms."
            audit_result = network.audit_transaction(toxic_doc)
            logging.info(f"NERE Audit of Toxic Asset: {audit_result}")

if __name__ == "__main__":
    run_simulation()
