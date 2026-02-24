import pytest
import numpy as np
from src.nafs_model_optimized import NafsNetwork_Optimized

class TestNafsNetworkOptimized:

    @pytest.fixture
    def network(self):
        num_agents = 10
        stages = np.full(num_agents, 6)
        return NafsNetwork_Optimized(num_agents, stages)

    def test_initialization(self, network):
        assert network.num_agents == 10
        assert np.all(network.capacity_bounds == 6)
        assert np.all(network.earned_essence == 0.0)
        assert np.all(network.entropy_friction == 0.0)
        assert np.all(network.gates_status == False)

    def test_vectorized_bias(self, network):
        # Setup identical inputs for all agents
        actual_u = np.full(10, 10.0)
        actual_d = np.full(10, 10.0)

        # Agent 0: Front Bias 0.1
        # Agent 1: Left Bias 0.6
        # Agent 2: Left Bias 0.5 (Threshold check)

        attack = np.zeros((10, 4))
        attack[0, 0] = 0.1 # Front
        attack[1, 3] = 0.6 # Left
        attack[2, 3] = 0.5 # Left

        p_u, p_d = network.apply_iblees_4d_bias(actual_u, actual_d, attack)

        # Agent 0
        expected_u_0 = 10.0 * 1.2
        assert p_u[0] == pytest.approx(expected_u_0)

        # Agent 1
        expected_u_1 = 10.0 + (0.6 * 6)
        expected_d_1 = 10.0 * 0.4
        assert p_u[1] == pytest.approx(expected_u_1)
        assert p_d[1] == pytest.approx(expected_d_1)

        # Agent 2 (Threshold not met)
        assert p_u[2] == pytest.approx(10.0)
        assert p_d[2] == pytest.approx(10.0)

    def test_vectorized_gates(self, network):
        # Agent 0: Trigger Gate 1 (Zeenah)
        # u_distortion > 1.8. Let's make p_u = 13.0 (actual 10.0)

        actual_u = np.full(10, 10.0)
        actual_d = np.full(10, 10.0)
        perceived_u = np.full(10, 10.0)
        perceived_d = np.full(10, 10.0)

        perceived_u[0] = 13.0

        network.audit_cognitive_gates(actual_u, actual_d, perceived_u, perceived_d)

        assert network.gates_status[0, 0] == True
        assert np.sum(network.gates_status[0]) == 1
        assert np.sum(network.gates_status[1:]) == 0

    def test_batch_processing_and_friction(self, network):
        # Agent 0: Zero Friction Loophole (Open Gate, No Breach)
        # Agent 1: Friction Spike (Open Gate, Breach)

        actual_u = np.full(10, 1.0)
        actual_d = np.full(10, 1.0)
        attack = np.zeros((10, 4))

        # Agent 0: Front Bias large enough to distort but not breach
        # Actual 1.0. Cap 6.0.
        # Target p_u = 3.0. Dist 2.0 > 1.8 (Gate 1).
        # 3 = 1 * (1 + 2*f) -> 2 = 2f -> f = 1.0
        attack[0, 0] = 1.0

        # Agent 1: Front Bias large enough to breach
        # Target p_u = 8.0. Breach 2.0.
        # 8 = 1 * (1 + 2*f) -> 7 = 2f -> f = 3.5
        attack[1, 0] = 3.5

        results = network.process_packet(actual_u, actual_d, attack)

        # Agent 0
        # Gate 1 open
        assert network.gates_status[0, 0] == True
        # Friction = 0 (Loophole)
        assert network.entropy_friction[0] == 0.0

        # Agent 1
        # Gate 1 open (Distortion 7.0 > 1.8)
        assert network.gates_status[1, 0] == True
        # Friction = (2.0 + 0) * 1.5^1 = 3.0
        assert network.entropy_friction[1] == pytest.approx(3.0)
        # Perceived D collapsed to 0
        # Essence = 8.0 * 0^2 = 0
        assert results["Essence_Generated"][1] == 0.0

        # Agent 2 (Clean)
        assert network.entropy_friction[2] == 0.0
        assert results["Essence_Generated"][2] == 1.0 # 1 * 1^2
