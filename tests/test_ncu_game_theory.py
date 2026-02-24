import pytest
import numpy as np
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ncu_network_optimized import NetworkOfAnfus

class TestNCUGameTheory:
    def test_fitness_vs_development_simulation(self):
        # 1. Initialize Network
        num_agents = 10000
        network = NetworkOfAnfus(num_agents=num_agents, random_seed=786)

        # 2. Define Populations
        midpoint = num_agents // 2
        materialist_indices = np.arange(0, midpoint)
        sovereign_indices = np.arange(midpoint, num_agents)

        # --- Configure Materialists (Population A) ---
        # High "Left Bias" (> 0.6)
        # bias_tensor columns: [front, back, right, left]
        # We set left bias (idx 3) to high values (0.6 to 0.9)
        # We also give them some Front bias which amplifies U
        network.bias_tensor[materialist_indices, 3] = np.random.uniform(0.6, 0.9, size=midpoint)
        network.bias_tensor[materialist_indices, 0] = np.random.uniform(0.1, 0.5, size=midpoint)
        network.bias_tensor[materialist_indices, 1] = np.random.uniform(0.0, 0.5, size=midpoint)
        network.bias_tensor[materialist_indices, 2] = np.random.uniform(0.0, 0.5, size=midpoint)

        # --- Configure Sovereigns (Population B) ---
        # Low Biases (Balanced, < 0.05)
        network.bias_tensor[sovereign_indices] = np.random.uniform(0.0, 0.05, size=(midpoint, 4))

        # Set uniform capacity for fair comparison (e.g., Stage 6)
        network.capacity_bound[:] = 6.0

        # 3. Simulate 100 Epochs
        # We set Absolute Truth slightly below Capacity Bound (6.0) to allow for minor biases in Sovereigns.
        # If Absolute = Capacity, even a 0.01 bias causes a breach.
        # With Absolute = 5.0, Sovereigns (bias < 0.05) stay within 6.0.
        # Materialists (bias > 0.6) will still breach massively (5.0 + 0.6*6 = 8.6 > 6.0).
        absolute_u = 5.0
        absolute_d = 5.0

        print("\n--- Starting Game Theory Simulation (100 Epochs) ---")
        for epoch in range(100):
            network.simulate_network_epoch(absolute_u, absolute_d)

        # 4. Analyze Results
        mat_stats = network.get_population_stats(materialist_indices)
        sov_stats = network.get_population_stats(sovereign_indices)

        # Network Global Stats
        total_c_dev = sum(network.network_c_dev_history)

        print(f"\nResults after 100 Epochs:")
        print(f"Population A (Materialists):")
        print(f"  Total Entropy Friction: {mat_stats['total_friction']:.2f}")
        print(f"  Total Earned Essence:   {mat_stats['total_essence']:.2f}")
        print(f"  Mean Friction per Agent: {mat_stats['mean_friction']:.2f}")

        print(f"\nPopulation B (Sovereigns):")
        print(f"  Total Entropy Friction: {sov_stats['total_friction']:.2f}")
        print(f"  Total Earned Essence:   {sov_stats['total_essence']:.2f}")
        print(f"  Mean Friction per Agent: {sov_stats['mean_friction']:.2f}")

        print(f"\nNetwork Global Stats:")
        print(f"  Total C_dev Generated: {total_c_dev:.2f}")

        # 5. Assertions

        # Assertion 1: Materialists generate massive entropy due to "Fitness" maximizing (Left Bias)
        # causing capacity breaches.
        assert mat_stats['total_friction'] > sov_stats['total_friction'] * 1000, \
            "Materialists should have significantly higher entropy friction"

        # Assertion 2: Sovereigns dominate Essence generation because they respect D and capacity.
        # Materialists collapse D to 0 upon breach, yielding 0 Essence.
        assert sov_stats['total_essence'] > mat_stats['total_essence'] * 1000, \
            "Sovereigns should generate exponentially more Essence than Materialists"

        # Assertion 3: Sovereigns maintain stability (near zero friction)
        # With capacity 6 and input 6, and low bias, friction should be minimal.
        assert sov_stats['mean_friction'] < 1.0, \
            "Sovereigns should remain stable with minimal friction"

if __name__ == "__main__":
    t = TestNCUGameTheory()
    t.test_fitness_vs_development_simulation()
