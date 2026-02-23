import pytest
import numpy as np
import time
from src.nere_api import NERE_API
from src.nere_api_optimized import NERE_API_Optimized

class TestNEREAPIOptimized:
    def test_parity_with_legacy(self):
        """
        Verify that NERE_API_Optimized produces identical results to NERE_API
        given the same initial state and inputs.
        """
        network_size = 100

        # Initialize both
        legacy_api = NERE_API(network_size)
        optimized_api = NERE_API_Optimized(network_size)

        # Force identical state
        # Legacy: self.agents = {i: CGMM_Agent(i, cap)}
        # Optimized: self.capacity_bounds[i] = cap

        test_capacities = np.random.randint(1, 13, size=network_size)

        for i in range(network_size):
            legacy_api.agents[i].capacity_bound = test_capacities[i]
            legacy_api.agents[i].earned_essence = 0.0
            legacy_api.agents[i].entropy_friction = 0.0

        optimized_api.capacity_bounds = test_capacities.copy()
        optimized_api.earned_essence = np.zeros(network_size)
        optimized_api.entropy_friction = np.zeros(network_size)

        # Generate random inputs
        # Mix of scenarios A, B, C
        us = np.random.uniform(0.5, 15.0, size=network_size)
        ds = np.random.uniform(0.5, 15.0, size=network_size)

        # Run legacy audits
        legacy_results = []
        for i in range(network_size):
            res = legacy_api.audit_input(i, "test", us[i], ds[i])
            legacy_results.append(res)

        # Run optimized batch audit
        agent_ids = np.arange(network_size)
        opt_res = optimized_api.audit_input_batch(agent_ids, us, ds)

        # Compare results
        # 1. Essence Generated
        # Note: legacy audit_input returns a dict with "Generated_Essence"
        legacy_essences = np.array([r["Generated_Essence"] for r in legacy_results])
        np.testing.assert_allclose(opt_res["essence_generated"], legacy_essences, err_msg="Essence mismatch")

        # 2. Earned Essence (internal state)
        legacy_earned = np.array([legacy_api.agents[i].earned_essence for i in range(network_size)])
        np.testing.assert_allclose(optimized_api.earned_essence, legacy_earned, err_msg="Earned essence state mismatch")

        # 3. Entropy Friction (internal state)
        legacy_friction = np.array([legacy_api.agents[i].entropy_friction for i in range(network_size)])
        np.testing.assert_allclose(optimized_api.entropy_friction, legacy_friction, err_msg="Friction state mismatch")

    def test_scalability_initialization(self):
        """
        Verify that initialization and batch processing for 100,000 agents
        is performant (finishes quickly).
        """
        start_time = time.time()
        network_size = 100000
        api = NERE_API_Optimized(network_size)
        init_time = time.time() - start_time

        print(f"Initialization time for {network_size} agents: {init_time:.4f}s")
        assert init_time < 1.0, "Initialization took too long"

        # Batch audit for all agents
        us = np.random.uniform(1, 15, size=network_size)
        ds = np.random.uniform(1, 15, size=network_size)
        agent_ids = np.arange(network_size)

        batch_start = time.time()
        api.audit_input_batch(agent_ids, us, ds)
        batch_time = time.time() - batch_start

        print(f"Batch audit time for {network_size} agents: {batch_time:.4f}s")
        assert batch_time < 1.0, "Batch audit took too long"

    def test_friction_decrease_logic_vectorized(self):
        """
        Explicitly verify that the vectorized version preserves the questionable
        logic where friction decreases if U < Capacity but D > Capacity.
        """
        api = NERE_API_Optimized(1)
        api.capacity_bounds[0] = 5

        # Case: U=4, D=6. Breach (D>Cap). Friction += 4-5 = -1.
        u = 4.0
        d = 6.0

        api.audit_input_batch([0], [u], [d])

        assert api.entropy_friction[0] == -1.0
