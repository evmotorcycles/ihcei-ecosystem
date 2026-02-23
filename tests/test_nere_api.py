import pytest
import numpy as np
from src.nere_api import CGMM_Agent, NERE_API

class TestCGMMAgent:
    def test_init(self):
        """Test initialization of CGMM_Agent."""
        agent = CGMM_Agent(1, 5)
        assert agent.agent_id == 1
        assert agent.capacity_bound == 5
        assert agent.earned_essence == 0.0
        assert agent.entropy_friction == 0.0

    def test_init_bounds(self):
        """Test capacity bounds clamping."""
        agent_low = CGMM_Agent(2, -1)
        assert agent_low.capacity_bound == 1

        agent_high = CGMM_Agent(3, 100)
        assert agent_high.capacity_bound == 12

    def test_scenario_a_within_bounds(self):
        """
        Scenario A: Within Bounds.
        U <= Capacity and D <= Capacity.
        Should generate positive essence and no friction.
        """
        capacity = 5
        agent = CGMM_Agent(1, capacity)
        u = 4.0
        d = 3.0

        essence = agent.evaluate_choice(u, d)

        expected_essence = u * (d ** 2)
        assert essence == expected_essence
        assert agent.earned_essence == expected_essence
        assert agent.entropy_friction == 0.0

    def test_scenario_b_materialist_category_error(self):
        """
        Scenario B: Materialist Category Error.
        D > Capacity (Governance/Order forced beyond capacity).
        Should result in D collapsing to 0.0, Essence = 0.0.
        """
        capacity = 5
        agent = CGMM_Agent(1, capacity)
        u = 4.0
        d = 6.0 # Exceeds capacity

        essence = agent.evaluate_choice(u, d)

        # Logic: if d > capacity: d = 0.0
        # essence = u * (0.0 ** 2) = 0.0
        assert essence == 0.0
        # Friction should NOT increase if only D is high?
        # Code: if utility_u > self.capacity_bound or governance_d > self.capacity_bound:
        #           self.entropy_friction += (utility_u - self.capacity_bound)
        #           governance_d = 0.0
        # Wait, friction adds (u - capacity). If u <= capacity, (u-capacity) is <= 0.
        # So friction decreases? Or does it add a negative value?
        # Let's check the code provided:
        # self.entropy_friction += (utility_u - self.capacity_bound)
        # If u=4, cap=5, friction += (4-5) = -1.
        # This seems like a bug/exploit in the provided code, but for this test I must assert what the code DOES.
        # If I am to "verify the math", I should test what the current code does.
        # I will document this in logic audit.

        expected_friction_change = u - capacity # 4 - 5 = -1.0
        assert agent.entropy_friction == expected_friction_change
        assert agent.earned_essence == 0.0

    def test_scenario_c_delusion_infinite_options(self):
        """
        Scenario C: The Delusion of Infinite Options.
        U > Capacity.
        Should generate friction, collapse D to 0, Essence = 0.
        """
        capacity = 5
        agent = CGMM_Agent(1, capacity)
        u = 10.0 # Exceeds capacity
        d = 3.0

        essence = agent.evaluate_choice(u, d)

        # Logic: if u > capacity: friction += (u - capacity); d = 0.0
        # friction += 10 - 5 = 5.0
        # essence = 10 * 0^2 = 0

        assert essence == 0.0
        assert agent.entropy_friction == 5.0
        assert agent.earned_essence == 0.0

class TestNEREAPI:
    def test_audit_input_green(self):
        """Test GREEN score scenario."""
        api = NERE_API(network_size=10)
        agent_id = 0
        agent = api.agents[agent_id]
        capacity = agent.capacity_bound

        # Ensure U and D are within bounds
        u = float(max(1, capacity - 1))
        d = float(max(1, capacity - 1))

        result = api.audit_input(agent_id, "test packet", u, d)

        assert result["Agency_Delta"] == "Positive (Kasabat)"
        assert "GREEN" in result["NERE_Score"]
        assert result["Generated_Essence"] > 0

    def test_audit_input_red(self):
        """Test RED score scenario (Category Error)."""
        api = NERE_API(network_size=10)
        agent_id = 0
        agent = api.agents[agent_id]
        capacity = agent.capacity_bound

        # Force U > Capacity
        u = float(capacity + 5)
        d = 1.0

        result = api.audit_input(agent_id, "test packet", u, d)

        assert result["Agency_Delta"] == "Void (Ektasabat)"
        assert "RED" in result["NERE_Score"]
        assert result["Generated_Essence"] == 0.0

    def test_audit_input_yellow(self):
        """
        Test YELLOW score scenario.
        Essence > 0 BUT friction > 0.
        This requires the agent to already have friction from a previous step,
        but the current step is valid (producing essence).
        """
        api = NERE_API(network_size=10)
        agent_id = 0
        agent = api.agents[agent_id]
        capacity = agent.capacity_bound

        # Step 1: Create friction (Scenario C)
        u_bad = float(capacity + 5)
        d_bad = 1.0
        api.audit_input(agent_id, "bad step", u_bad, d_bad)
        assert agent.entropy_friction > 0

        # Step 2: Good step (Scenario A)
        u_good = float(max(1, capacity - 1))
        d_good = float(max(1, capacity - 1))

        result = api.audit_input(agent_id, "good step", u_good, d_good)

        assert result["Generated_Essence"] > 0
        assert agent.entropy_friction > 0
        assert result["Agency_Delta"] == "Frictional"
        assert "YELLOW" in result["NERE_Score"]
