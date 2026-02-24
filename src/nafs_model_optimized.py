import numpy as np

class NafsNetwork_Optimized:
    def __init__(self, num_agents, cognitive_stages):
        """
        Initialize the optimized Nafs Network for mass simulation.
        num_agents: Integer number of agents.
        cognitive_stages: NumPy array of shape (num_agents,) containing cognitive stages.
        """
        self.num_agents = num_agents
        # Vectorized capacity bound
        # bound = max(1, min(12, stage))
        self.capacity_bounds = np.clip(cognitive_stages, 1, 12).astype(np.float64)

        self.earned_essence = np.zeros(num_agents, dtype=np.float64)
        self.entropy_friction = np.zeros(num_agents, dtype=np.float64)

        # Gates as boolean matrix: (num_agents, 7)
        # Mapping index to gate name for reference (not stored per row for memory efficiency)
        # 0: G1_Zeenah, 1: G2_Groupthink, 2: G3_Indirect_Guidance,
        # 3: G4_Methodological_Error, 4: G5_Misusing_Scripture,
        # 5: G6_Distraction, 6: G7_Conceit
        self.gates_status = np.zeros((num_agents, 7), dtype=bool)

    def apply_iblees_4d_bias(self, actual_u, actual_d, attack_vectors):
        """
        Vectorized 4D Bias application.
        actual_u, actual_d: NumPy arrays of shape (num_agents,)
        attack_vectors: NumPy array of shape (num_agents, 4)
        """
        front_bias = attack_vectors[:, 0]
        back_bias = attack_vectors[:, 1]
        right_bias = attack_vectors[:, 2]
        left_bias = attack_vectors[:, 3]

        # 1. FRONT
        perceived_u = actual_u * (1.0 + (front_bias * 2.0))

        # 2. BACK
        perceived_d = actual_d * (1.0 - (back_bias * 0.8))

        # 3. RIGHT
        perceived_d += (right_bias * self.capacity_bounds)

        # 4. LEFT (Conditional Mask)
        left_mask = left_bias > 0.5

        # Apply where mask is true
        perceived_u[left_mask] += (left_bias[left_mask] * self.capacity_bounds[left_mask])
        perceived_d[left_mask] *= (1.0 - left_bias[left_mask])

        return perceived_u, perceived_d

    def audit_cognitive_gates(self, actual_u, actual_d, perceived_u, perceived_d):
        """
        Vectorized Gate Auditing.
        """
        u_distortion = np.abs(perceived_u - actual_u)
        d_distortion = np.abs(perceived_d - actual_d)

        # Gate 1: Zeenah
        g1_mask = u_distortion > (self.capacity_bounds * 0.3)
        self.gates_status[:, 0] |= g1_mask

        # Gate 3: Indirect Guidance
        g3_mask = (actual_d > perceived_d) & (d_distortion > (self.capacity_bounds * 0.4))
        self.gates_status[:, 2] |= g3_mask

        # Gate 7: Conceit
        g7_mask = (perceived_d > actual_d) & (d_distortion > (self.capacity_bounds * 0.5))
        self.gates_status[:, 6] |= g7_mask

        # Count open gates per agent
        open_gates_counts = np.sum(self.gates_status, axis=1)
        return open_gates_counts

    def process_packet(self, actual_u, actual_d, attack_vectors):
        """
        Vectorized processing of packets for all agents.
        """
        # Enforce floors
        actual_u = np.maximum(0.0, actual_u)
        actual_d = np.maximum(0.0, actual_d)

        perceived_u, perceived_d = self.apply_iblees_4d_bias(actual_u, actual_d, attack_vectors)

        open_gates_counts = self.audit_cognitive_gates(actual_u, actual_d, perceived_u, perceived_d)

        # Friction Logic Trigger
        # if open_gates > 0 OR perceived_u > bound OR perceived_d > bound
        friction_condition = (open_gates_counts > 0) | (perceived_u > self.capacity_bounds) | (perceived_d > self.capacity_bounds)

        # Calculate breach
        u_breach = np.maximum(0.0, perceived_u - self.capacity_bounds)
        d_breach = np.maximum(0.0, perceived_d - self.capacity_bounds)

        # Friction spike calculation
        # Note: This reproduces the "Zero Friction Loophole" where if breach is 0, friction is 0 regardless of open gates.
        friction_spike = (u_breach + d_breach) * (1.5 ** open_gates_counts)

        # Apply friction only where condition is met (redundant if 0, but logically sound)
        # Using np.where to be explicit about the condition logic, though mathematical result is same if friction_spike is 0.
        # But we must ensure we only add friction if the condition triggered?
        # The scalar code says: if condition: friction += spike.
        # If condition is False, friction doesn't change.
        # If condition is True but spike is 0, friction doesn't change.
        # So we can just add friction_spike where condition is True.

        self.entropy_friction[friction_condition] += friction_spike[friction_condition]

        # Collapse perceived_d where friction occurs
        perceived_d[friction_condition] = 0.0

        # Essence Calculation
        essence_generated = perceived_u * (perceived_d ** 2)

        # Add to cumulative
        self.earned_essence += np.maximum(0.0, essence_generated)

        return {
            "Essence_Generated": essence_generated,
            "Entropy_Friction": self.entropy_friction.copy(),
            "Open_Gates_Counts": open_gates_counts
        }
