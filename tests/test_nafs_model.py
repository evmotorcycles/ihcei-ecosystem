import pytest
import numpy as np
from src.nafs_model import NafsPsychologicalModel

class TestNafsPsychologicalModel:

    @pytest.fixture
    def model(self):
        return NafsPsychologicalModel(agent_id=1, cognitive_stage=6)

    def test_initialization(self, model):
        assert model.capacity_bound == 6
        assert model.earned_essence == 0.0
        assert model.entropy_friction == 0.0
        assert not any(model.gates_status.values())

    def test_apply_iblees_4d_bias_pure(self, model):
        # Front: 0.1 -> u * (1 + 0.2)
        # Back: 0.1 -> d * (1 - 0.08)
        # Right: 0.1 -> d + (0.1 * 6) = d + 0.6
        # Left: 0.0 (no effect)
        actual_u = 10.0
        actual_d = 10.0
        attack = [0.1, 0.1, 0.1, 0.0]

        p_u, p_d = model.apply_iblees_4d_bias(actual_u, actual_d, attack)

        expected_u = 10.0 * 1.2
        expected_d = 10.0 * (1.0 - 0.08) + 0.6

        assert p_u == pytest.approx(expected_u)
        assert p_d == pytest.approx(expected_d)

    def test_left_attack_activation(self, model):
        # Left > 0.5
        actual_u = 10.0
        actual_d = 10.0
        attack = [0.0, 0.0, 0.0, 0.6] # Left = 0.6

        p_u, p_d = model.apply_iblees_4d_bias(actual_u, actual_d, attack)

        # u += 0.6 * 6 = 3.6 -> 13.6
        expected_u = 10.0 + (0.6 * 6)
        # d *= (1.0 - 0.6) = 0.4 * 10 = 4.0
        expected_d = 10.0 * 0.4

        assert p_u == pytest.approx(expected_u)
        assert p_d == pytest.approx(expected_d)

    def test_left_attack_threshold_exploit(self, model):
        # Left = 0.5 (Threshold is > 0.5)
        actual_u = 10.0
        actual_d = 10.0
        attack = [0.0, 0.0, 0.0, 0.5]

        p_u, p_d = model.apply_iblees_4d_bias(actual_u, actual_d, attack)

        # Should be no change
        assert p_u == pytest.approx(10.0)
        assert p_d == pytest.approx(10.0)

    def test_right_attack_conceit(self, model):
        # Right attack inflates D
        actual_u = 2.0
        actual_d = 2.0
        attack = [0.0, 0.0, 0.8, 0.0] # Right = 0.8 -> + 4.8 to D

        result = model.process_packet(actual_u, actual_d, attack)

        # Perceived D = 2.0 + 4.8 = 6.8
        # Actual D = 2.0
        # Distortion = 4.8
        # Threshold for Conceit (Gate 7): capacity * 0.5 = 3.0
        # 4.8 > 3.0 -> Gate 7 opens

        assert model.gates_status["G7_Conceit"] is True
        assert "G7_Conceit" in result["Open_Gates"]

    def test_zero_friction_loophole(self, model):
        # Setup conditions where gates open but perceived values are <= capacity
        # Capacity = 6
        # Actual U = 1.0
        # Actual D = 1.0
        # Attack causes distortion > threshold but total remains <= 6

        # Target: Open Gate 1 (Zeenah) -> u_distortion > capacity * 0.3 (1.8)
        # We need u_distortion > 1.8. Let's make perceived_u = 3.0 (Actual 1.0).
        # Front bias needs to double U or similar.
        # perceived_u = actual_u * (1 + 2*front)
        # 3.0 = 1.0 * (1 + 2*front) -> 2 = 2*front -> front = 1.0

        actual_u = 1.0
        actual_d = 1.0
        attack = [1.0, 0.0, 0.0, 0.0] # Front = 1.0

        # Run process
        result = model.process_packet(actual_u, actual_d, attack)

        # Check Gate 1
        # u_distortion = |3.0 - 1.0| = 2.0 > 1.8. Gate 1 opens.
        assert model.gates_status["G1_Zeenah"] is True

        # Check Friction
        # perceived_u = 3.0 <= 6 (No breach)
        # perceived_d = 1.0 <= 6 (No breach)
        # Friction = (0 + 0) * ... = 0

        assert result["Entropy_Friction"] == 0.0
        assert model.entropy_friction == 0.0

    def test_friction_calculation(self, model):
        # Force a breach with open gates
        # Capacity = 6
        # Perceived U = 8.0 (Breach 2.0)
        # Open Gates = 1

        actual_u = 8.0 # Already breached
        actual_d = 1.0
        attack = [0.0, 0.0, 0.0, 0.0] # No bias, just testing friction logic?
        # Wait, if no bias, distortion is 0. No gates open.
        # We need to force a gate open OR have high perceived values.
        # If open_gates > 0 OR perceived > capacity.
        # Here we rely on perceived > capacity to trigger friction.

        # Let's use Front bias to boost U to 8.0 from 4.0
        # 8 = 4 * (1 + 2*front) -> 2 = 1 + 2*front -> 1 = 2*front -> front = 0.5

        actual_u = 4.0
        actual_d = 1.0
        attack = [0.5, 0.0, 0.0, 0.0]

        # Run
        # Perceived U = 8.0. Breach = 2.0.
        # Distortion = |8-4| = 4.0.
        # Gate 1 Threshold = 1.8. Distortion > 1.8. Gate 1 Opens.
        # Open Gates = 1.

        result = model.process_packet(actual_u, actual_d, attack)

        # Friction = (2.0 + 0) * (1.5 ** 1) = 2.0 * 1.5 = 3.0

        assert model.gates_status["G1_Zeenah"] is True
        assert result["Entropy_Friction"] == pytest.approx(3.0)

        # And Perceived D becomes 0.0 due to friction trigger
        # Essence = 8.0 * (0.0^2) = 0.0
        assert result["Essence_Generated"] == 0.0
