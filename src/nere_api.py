import numpy as np


class CGMM_Agent:
    def __init__(self, agent_id, cognitive_stage):
        self.agent_id = agent_id
        self.capacity_bound = max(1, min(12, cognitive_stage))
        self.earned_essence = 0.0
        self.entropy_friction = 0.0

    def evaluate_choice(self, utility_u, governance_d):
        if utility_u > self.capacity_bound or governance_d > self.capacity_bound:
            self.entropy_friction += (utility_u - self.capacity_bound)
            governance_d = 0.0

        essence_generated = utility_u * (governance_d ** 2)

        if essence_generated > 0:
            self.earned_essence += essence_generated

        return essence_generated


class NERE_API:
    def __init__(self, network_size=1000):
        self.agents = {i: CGMM_Agent(i, np.random.randint(1, 13)) for i in range(network_size)}

    def audit_input(self, agent_id, text_packet, proposed_u, proposed_d):
        agent = self.agents[agent_id]
        essence = agent.evaluate_choice(proposed_u, proposed_d)

        if essence > 0 and agent.entropy_friction == 0:
            agency_delta = "Positive (Kasabat)"
            score = "GREEN: Agency Preserved. C_dev of the network enhanced."
        elif essence > 0 and agent.entropy_friction > 0:
            agency_delta = "Frictional"
            score = "YELLOW: Marginal capacity breach. \\hbar_{corruption} increasing."
        else:
            agency_delta = "Void (Ektasabat)"
            score = "RED: Category Error Detected (D=0). Essence mathematically voided."

        return {
            "Packet": text_packet,
            "Agent_Capacity": agent.capacity_bound,
            "Agency_Delta": agency_delta,
            "Generated_Essence": essence,
            "NERE_Score": score
        }
