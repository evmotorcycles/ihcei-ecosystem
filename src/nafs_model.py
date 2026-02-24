import numpy as np

class NafsPsychologicalModel:
    def __init__(self, agent_id, cognitive_stage):
        self.agent_id = agent_id
        # The operational reality bound (1 to 12)
        self.capacity_bound = max(1, min(12, cognitive_stage))

        # State Tracking
        self.earned_essence = 0.0
        self.entropy_friction = 0.0  # Represents Jahannam: computational friction/crushing (YT137)

        # The 7 Gates of Jahannam (Cognitive Failure Modes)
        # Stored as boolean states. True = Gate is open (breached).
        self.gates_status = {
            "G1_Zeenah": False,          # Vain adornments/superficial data
            "G2_Groupthink": False,      # Surrendering processing to the collective
            "G3_Indirect_Guidance": False, # Blindly following flawed tradition
            "G4_Methodological_Error": False, # Failing to apply the pressing protocol
            "G5_Misusing_Scripture": False,   # Forcing text to match bias
            "G6_Distraction": False,     # Loss of focal alignment
            "G7_Conceit": False          # Hoarding agency/Benevolent Tyranny
        }

    def apply_iblees_4d_bias(self, actual_u, actual_d, attack_vector):
        """
        The 4D Bias Model (YT74/YT75).
        Iblees acts as an innate adversarial algorithm applying a 4-dimensional
        perturbation tensor to distort the Nafs's perception of U and D.
        attack_vector = [front, back, right, left] (Values 0.0 to 1.0)
        """
        front_bias, back_bias, right_bias, left_bias = attack_vector

        # 1. FRONT (Future/Delusion): Artificially inflates perceived Utility (Hope without mechanics)
        perceived_u = actual_u * (1.0 + (front_bias * 2.0))

        # 2. BACK (Past/Sunk Cost): Drags Governance backward, refusing to update established schema
        perceived_d = actual_d * (1.0 - (back_bias * 0.8))

        # 3. RIGHT (Conceit/False Piety): Inflates perceived D, masking a lack of actual U
        perceived_d += (right_bias * self.capacity_bound)

        # 4. LEFT (Materialism): Maximizes raw U while zeroing out D (The Category Error)
        if left_bias > 0.5:
            perceived_u += (left_bias * self.capacity_bound)
            perceived_d *= (1.0 - left_bias)

        return perceived_u, perceived_d

    def audit_cognitive_gates(self, actual_u, actual_d, perceived_u, perceived_d):
        """
        Evaluates the delta between absolute Truth (Al-Haqq) and the biased
        Apparition (As-Sidq). If the delta exceeds capacity, specific Gates open.
        """
        u_distortion = abs(perceived_u - actual_u)
        d_distortion = abs(perceived_d - actual_d)

        # Gate 1: Zeenah (Focusing on superficial utility over structural truth)
        if u_distortion > (self.capacity_bound * 0.3):
            self.gates_status["G1_Zeenah"] = True

        # Gate 3: Indirect Guidance (Relying on flawed past schemas - Back attack)
        if actual_d > perceived_d and d_distortion > (self.capacity_bound * 0.4):
            self.gates_status["G3_Indirect_Guidance"] = True

        # Gate 7: Conceit (Artificially inflated D - Right attack)
        if perceived_d > actual_d and d_distortion > (self.capacity_bound * 0.5):
            self.gates_status["G7_Conceit"] = True

        # Summing the open gates to calculate the exact spike in systemic friction
        open_gates = sum(self.gates_status.values())
        return open_gates

    def process_packet(self, actual_u, actual_d, attack_vector):
        """
        The main cognitive loop. The Nafs processes an event, faces the 4D bias,
        evaluates against the 7 Gates, and calculates final Essence.
        """
        # Step 1: Enforce Absolute Reality (Floor of 0.0)
        actual_u = max(0.0, actual_u)
        actual_d = max(0.0, actual_d)

        # Step 2: The Counterpart Attack (Iblees applies the 4D perturbation)
        perceived_u, perceived_d = self.apply_iblees_4d_bias(actual_u, actual_d, attack_vector)

        # Step 3: Gate Auditing (Checking for cognitive vulnerabilities)
        open_gates = self.audit_cognitive_gates(actual_u, actual_d, perceived_u, perceived_d)

        # Step 4: Friction & Capacity Enforcement
        if open_gates > 0 or perceived_u > self.capacity_bound or perceived_d > self.capacity_bound:
            # Friction scales exponentially with the number of open gates (Jahannam state)
            u_breach = max(0.0, perceived_u - self.capacity_bound)
            d_breach = max(0.0, perceived_d - self.capacity_bound)

            # The crushing state of the Qareen: friction compounds heavily
            friction_spike = (u_breach + d_breach) * (1.5 ** open_gates)
            self.entropy_friction += friction_spike

            # Category Error: If gates are open, operational truth collapses
            perceived_d = 0.0

        # Step 5: The Destiny Equation (E = UD^2)
        # Using the perceived values because the agent operates on its filtered reality
        essence_generated = perceived_u * (perceived_d ** 2)

        if essence_generated > 0:
            self.earned_essence += essence_generated

        return {
            "Essence_Generated": essence_generated,
            "Entropy_Friction": self.entropy_friction,
            "Open_Gates": [gate for gate, is_open in self.gates_status.items() if is_open]
        }
