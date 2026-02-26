
import pytest
import numpy as np
from src.simulation.nafs_agency_simulator import NafsNode, NafsAgencySimulator
from src.simulation.ugo import UnifiedGovernanceObject

class TestNafsAgencySimulator:
    def test_nafs_node_initialization(self):
        """
        Verify that a NafsNode initializes with correct Qareen and Iblees values.
        """
        node = NafsNode(agent_id=1, qareen_filter=0.2, iblees_noise=0.1)
        assert node.id == 1
        assert node.qareen_filter == 0.2
        assert node.iblees_noise == 0.1
        assert node.c_dev == 0.0

    def test_absorb_knowledge_low_friction(self):
        """
        Verify that in a low friction environment (Abrahamic), the agent absorbs high knowledge
        and the Qareen filter barely hardens.
        """
        node = NafsNode(agent_id=1, qareen_filter=0.0, iblees_noise=0.1)
        h_network = 1.0 # Minimal friction
        knowledge_flow = 100.0

        c_dev = node.absorb_knowledge(h_network, knowledge_flow)

        # c_dev should be high
        # Resistance = 1.0 + (0.1 * 1.0 * 0.5) + 1.0 = 2.05
        # C_dev = 100 / 2.05 ~= 48.78
        assert c_dev > 40.0

        # Hardening should be low
        # Factor = 0.25 * log1p(1.0) * 0.1 = 0.25 * 0.693 * 0.1 = 0.017
        assert node.qareen_filter < 0.02

    def test_absorb_knowledge_high_friction(self):
        """
        Verify that in a high friction environment (Pharaonic), the agent absorbs minimal knowledge
        and the Qareen filter hardens rapidly.
        """
        node = NafsNode(agent_id=1, qareen_filter=0.0, iblees_noise=0.5) # Higher noise for stress
        h_network = 1000.0 # Extreme friction
        knowledge_flow = 100.0

        c_dev = node.absorb_knowledge(h_network, knowledge_flow)

        # c_dev should be near zero
        # Resistance ~ 1000
        # C_dev = 100 / 1000 = 0.1
        assert c_dev < 1.0

        # Hardening should be significant
        # Factor = 0.05 * log1p(1000) * 0.5 = 0.05 * 6.9 * 0.5 = 0.17
        assert node.qareen_filter > 0.1

    def test_generational_posterity(self):
        """
        Verify that filters harden over generations in corrupted systems.
        """
        # Mock UGO with high friction
        class MockUGO:
            name = "TestCorrupt"
            h_network = 500.0
            knowledge_flow = 100.0
            def compile_reality(self): return {}

        sim = NafsAgencySimulator(MockUGO(), num_agents=10)
        history = sim.simulate_generations(num_generations=3)

        # Gen 1 End Qareen < Gen 2 End Qareen < Gen 3 End Qareen
        qareen_gen1 = history[0]['avg_end_qareen']
        qareen_gen3 = history[2]['avg_end_qareen']

        assert qareen_gen3 > qareen_gen1

    def test_abraham_vs_pharaoh_generations(self):
        """
        Verify the macro assertions:
        1. Low friction -> Open Heart (Low Qareen)
        2. High friction -> Sealed Heart (High Qareen)
        """
        # 1. Low Friction
        class LowFrictionUGO:
            name = "Abraham"
            h_network = 1.0
            knowledge_flow = 100.0
            def compile_reality(self): return {}

        sim_a = NafsAgencySimulator(LowFrictionUGO(), num_agents=5)
        hist_a = sim_a.simulate_generations(num_generations=3)

        # 2. High Friction
        class HighFrictionUGO:
            name = "Pharaoh"
            h_network = 10000.0
            knowledge_flow = 100.0
            def compile_reality(self): return {}

        sim_p = NafsAgencySimulator(HighFrictionUGO(), num_agents=5)
        hist_p = sim_p.simulate_generations(num_generations=3)

        final_qareen_a = hist_a[-1]['avg_end_qareen']
        final_qareen_p = hist_p[-1]['avg_end_qareen']

        assert final_qareen_a < 0.1 # Stays open
        assert final_qareen_p > 0.5 # Hardens significantly (likely > 0.5 after 3 steps)
