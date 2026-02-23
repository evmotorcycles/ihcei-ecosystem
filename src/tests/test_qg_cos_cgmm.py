
import pytest
from src.core.qg_cos_cgmm import GovernancePhysics, ADGENetwork, CGMM_Agent

class TestGovernancePhysics:
    """
    Tests for the GovernancePhysics class.
    """

    def test_kitchen_protocol_edge_cases(self):
        """
        Test the Kitchen Protocol (E = U * D^2) with various edge cases.
        """
        # Test negative utility (Debt)
        utility = -100.0
        deen = 5.0
        expected_essence = -100.0 * (5.0 ** 2)
        assert GovernancePhysics.kitchen_protocol(utility, deen) == pytest.approx(expected_essence)

        # Test zero utility
        utility = 0.0
        deen = 5.0
        assert GovernancePhysics.kitchen_protocol(utility, deen) == pytest.approx(0.0)

        # Test zero Deen (Materialist view)
        utility = 100.0
        deen = 0.0
        assert GovernancePhysics.kitchen_protocol(utility, deen) == pytest.approx(0.0)

        # Test fractional Deen
        utility = 100.0
        deen = 0.5
        expected_essence = 100.0 * (0.5 ** 2)
        assert GovernancePhysics.kitchen_protocol(utility, deen) == pytest.approx(expected_essence)

        # Test massive integer values
        utility = 1000000
        deen = 1000
        expected_essence = 1000000 * (1000 ** 2)
        assert GovernancePhysics.kitchen_protocol(utility, deen) == pytest.approx(expected_essence)

    def test_tqg_cfe_perception_bounds(self):
        """
        Test the TQG-CFE Perception (Psi_experienced = A_n(Psi_quantum)) with out-of-bounds inputs.
        """
        psi_quantum = 100.0

        # Test lower bound (stage < 1) -> should be clamped to 1
        assert GovernancePhysics.tqg_cfe_perception(psi_quantum, 0) == pytest.approx(psi_quantum * (1/12.0))
        assert GovernancePhysics.tqg_cfe_perception(psi_quantum, -5) == pytest.approx(psi_quantum * (1/12.0))

        # Test upper bound (stage > 12) -> should be clamped to 12
        assert GovernancePhysics.tqg_cfe_perception(psi_quantum, 13) == pytest.approx(psi_quantum * (12/12.0))
        assert GovernancePhysics.tqg_cfe_perception(psi_quantum, 100) == pytest.approx(psi_quantum * (12/12.0))

        # Test normal case
        assert GovernancePhysics.tqg_cfe_perception(psi_quantum, 6) == pytest.approx(psi_quantum * (6/12.0))

class TestADGENetwork:
    """
    Tests for the ADGENetwork class.
    """

    def test_adge_network_zero_alignment(self):
        """
        Test network with zero alignment between agents.
        """
        network = ADGENetwork(num_agents=2)
        network.set_agent_stage(0, 5)
        network.set_agent_stage(1, 5)
        # Alignment is 0 by default

        c_dev = network.calculate_c_dev(open_gates_of_entropy=0)
        assert c_dev == pytest.approx(0.0)

    def test_adge_network_negative_alignment(self):
        """
        Test network with negative alignment (conflict/discord).
        """
        network = ADGENetwork(num_agents=2)
        network.set_agent_stage(0, 5)
        network.set_agent_stage(1, 5)

        network.set_alignment(0, 1, -1.0)
        # Interaction: 5 * 5 * -1.0 = -25.0
        # C_dev = -25.0 / 1.0 = -25.0

        c_dev = network.calculate_c_dev(open_gates_of_entropy=0)
        assert c_dev == pytest.approx(-25.0)

    def test_adge_network_max_entropy(self):
        """
        Test network with maximum entropy (7 open gates).
        Verifies inverse scaling of C_dev with hbar_corruption.
        """
        network = ADGENetwork(num_agents=2)
        network.set_agent_stage(0, 10)
        network.set_agent_stage(1, 10)
        network.set_alignment(0, 1, 1.0)

        # Interaction sum: 10 * 10 * 1.0 = 100.0
        interaction_sum = 100.0

        # 0 gates -> hbar = 1.0 -> C_dev = 100.0
        c_dev_0 = network.calculate_c_dev(open_gates_of_entropy=0)
        assert c_dev_0 == pytest.approx(interaction_sum)

        # 7 gates -> hbar = 1.0 + (7 * 0.5) = 4.5
        # C_dev = 100.0 / 4.5
        c_dev_7 = network.calculate_c_dev(open_gates_of_entropy=7)
        expected_c_dev_7 = interaction_sum / 4.5

        assert c_dev_7 == pytest.approx(expected_c_dev_7)
        assert c_dev_7 < c_dev_0

class TestCGMMAgent:
    """
    Tests for the CGMM_Agent class.
    """

    def test_agent_stage_comparison(self):
        """
        Compare a Stage 1 Agent against a Stage 12 Agent given the same event.
        """
        agent_stage_1 = CGMM_Agent("Stage 1 Agent", cognitive_stage=1)
        agent_stage_12 = CGMM_Agent("Stage 12 Agent", cognitive_stage=12)

        event_utility = 100.0
        event_protocol_truth = 12.0 # Easy number for calculation

        # Stage 1 Agent:
        # Perceived truth = 12.0 * (1/12) = 1.0
        # Essence = 100 * (1.0 ** 2) = 100.0
        outcome_1 = agent_stage_1.evaluate_event(event_utility, event_protocol_truth)
        assert outcome_1 == pytest.approx(100.0)

        # Stage 12 Agent:
        # Perceived truth = 12.0 * (12/12) = 12.0
        # Essence = 100 * (12.0 ** 2) = 14400.0
        outcome_12 = agent_stage_12.evaluate_event(event_utility, event_protocol_truth)
        assert outcome_12 == pytest.approx(14400.0)

        assert outcome_12 > outcome_1
