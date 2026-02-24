import numpy as np

class NetworkOfAnfus:
    def __init__(self, num_agents=10000, random_seed=42):
        np.random.seed(random_seed)
        self.num_agents = num_agents

        # Initialize agents with random cognitive stages (1-12)
        # For simplicity and test control, we might allow external configuration,
        # but here we'll default to a distribution.
        # However, the test will override these, so simple initialization is fine.
        self.capacity_bound = np.random.randint(1, 13, size=num_agents).astype(np.float64)

        # Bias Tensor: [Front, Back, Right, Left]
        # Initialized randomly, will be overridden by test for specific populations
        self.bias_tensor = np.random.uniform(0.0, 1.0, size=(num_agents, 4))

        # State tracking
        self.entropy_friction = np.zeros(num_agents, dtype=np.float64)
        self.earned_essence = np.zeros(num_agents, dtype=np.float64)

        # Network Stats
        self.network_c_dev_history = []
        self.network_friction_history = []
        self.network_essence_history = []

    def simulate_network_epoch(self, absolute_u, absolute_d):
        """
        Simulates one epoch of the network.
        absolute_u, absolute_d: The 'Absolute Truth' parameters for this epoch.
        """

        # --- 1. TQG-CFE Rendering (Vectorized) ---
        # "An agent can only perceive an apparition up to capacity_bound * 1.5"
        perceived_u = np.minimum(absolute_u, self.capacity_bound * 1.5)
        perceived_d = np.minimum(absolute_d, self.capacity_bound * 1.5)

        # --- 2. Agent Processing (Vectorized CGMM Logic) ---
        # Extract biases for clarity
        front = self.bias_tensor[:, 0]
        back = self.bias_tensor[:, 1]
        right = self.bias_tensor[:, 2]
        left = self.bias_tensor[:, 3]

        # Apply Front/Back/Right biases
        internal_u = perceived_u * (1.0 + (front * 2.0))
        internal_d = perceived_d * (1.0 - (back * 0.8)) + (right * self.capacity_bound)

        # Apply Left Bias (> 0.5 condition)
        left_mask = left > 0.5
        # We need to apply this only where mask is True
        # internal_u += (left * capacity_bound)
        internal_u[left_mask] += (left[left_mask] * self.capacity_bound[left_mask])
        # internal_d *= (1.0 - left)
        internal_d[left_mask] *= (1.0 - left[left_mask])

        # --- 3. Capacity Bounds & Entropy Friction ---
        u_breach = np.maximum(0.0, internal_u - self.capacity_bound)
        d_breach = np.maximum(0.0, internal_d - self.capacity_bound)

        current_friction = u_breach + d_breach
        self.entropy_friction += current_friction

        # Category Error: If breach occurs, D collapses to 0 for the calculation
        breach_mask = current_friction > 0
        internal_d[breach_mask] = 0.0

        # --- 4. The Destiny Equation (E = UD^2) ---
        current_essence = internal_u * (internal_d ** 2)
        self.earned_essence += current_essence

        # --- 5. Network Interaction (The G_ij Connectivity Tensor) ---
        # Randomly pair agents
        indices = np.arange(self.num_agents)
        np.random.shuffle(indices)

        # Ensure even number for pairing; if odd, drop one (negligible for 10k)
        if self.num_agents % 2 != 0:
            indices = indices[:-1]

        half_k = len(indices) // 2
        group_a = indices[:half_k]
        group_b = indices[half_k:]

        # Calculate combined friction for pairs
        # "inverse of their combined entropy_friction"
        friction_a = self.entropy_friction[group_a]
        friction_b = self.entropy_friction[group_b]
        combined_friction = friction_a + friction_b

        # G_ij: Alignment Coefficient (0.0 to 1.0)
        # Using a simple inverse function: 1 / (1 + friction)
        g_ij = 1.0 / (1.0 + combined_friction)

        # Network C_dev Calculation
        # "Sum of shared Essence minus sum of Network Friction"
        essence_a = current_essence[group_a]
        essence_b = current_essence[group_b]

        shared_essence = (essence_a + essence_b) * g_ij
        network_friction_loss = combined_friction # Sum of friction in the network interaction

        epoch_c_dev = np.sum(shared_essence) - np.sum(network_friction_loss)

        # Store History
        self.network_c_dev_history.append(epoch_c_dev)
        self.network_friction_history.append(np.sum(current_friction))
        self.network_essence_history.append(np.sum(current_essence))

        return {
            "epoch_c_dev": epoch_c_dev,
            "total_friction_added": np.sum(current_friction),
            "total_essence_generated": np.sum(current_essence)
        }

    def get_population_stats(self, indices):
        """
        Returns stats for a specific sub-population defined by indices.
        """
        return {
            "mean_friction": np.mean(self.entropy_friction[indices]),
            "mean_essence": np.mean(self.earned_essence[indices]),
            "total_friction": np.sum(self.entropy_friction[indices]),
            "total_essence": np.sum(self.earned_essence[indices])
        }
