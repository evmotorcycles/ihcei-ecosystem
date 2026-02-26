
import pytest
import numpy as np
from src.simulation.nafs_agency_simulator import NafsNode
from src.simulation.zikra_taqwa_engine import ZikraTaqwaEngine

class MockNetwork:
    """Simple mock for testing Zakat."""
    def __init__(self, main_agent):
        self.nodes = [main_agent, NafsNode(2), NafsNode(3)]

class TestZikraTaqwaEngine:
    def setup_method(self):
        self.agent = NafsNode(agent_id=1, qareen_filter=0.8, iblees_noise=0.5)
        self.network = MockNetwork(self.agent)
        self.engine = ZikraTaqwaEngine(self.agent, self.network)

    def test_taqwa_dampening(self):
        """
        Verify that Taqwa dampens Iblees Noise.
        """
        initial_noise = self.agent.iblees_noise
        self.engine.execute_taqwa(discipline_factor=0.5)

        # Should be reduced by 50%
        assert np.isclose(self.agent.iblees_noise, initial_noise * 0.5)

    def test_salat_friction_drop(self):
        """
        Verify that Salat drops local friction and shields.
        """
        self.agent.local_friction = 1000.0
        self.agent.active_qareen_shield = 0.8

        self.engine.execute_salat()

        assert self.agent.local_friction <= 0.01
        assert self.agent.active_qareen_shield == 0.0

    def test_zikra_qareen_shatter(self):
        """
        Verify that Zikra permanently reduces the Qareen filter.
        """
        # Ensure Salat has run (shield down)
        self.agent.active_qareen_shield = 0.0
        initial_qareen = self.agent.qareen_filter

        self.engine.execute_zikra(truth_packet_size=0.2)

        # Should be reduced by 0.2
        assert np.isclose(self.agent.qareen_filter, initial_qareen - 0.2)

        # If shield is UP, it shouldn't work
        self.agent.active_qareen_shield = 1.0
        self.engine.execute_zikra(truth_packet_size=0.2)
        # Should remain unchanged
        assert np.isclose(self.agent.qareen_filter, initial_qareen - 0.2)

    def test_zakat_propagation(self):
        """
        Verify that Zakat distributes juice to the network.
        """
        # Give agent some C_dev
        self.agent.c_dev = 100.0

        propagated = self.engine.execute_zakat(distribution_rate=0.5)

        # Should distribute 50.0
        assert propagated == 50.0

        # Network nodes should have received it
        # 2 neighbors, so 25 each
        assert self.network.nodes[1].c_dev == 25.0
        assert self.network.nodes[2].c_dev == 25.0

    def test_full_repair_lifecycle(self):
        """
        Verify the full sequence repairs a corrupted agent.
        """
        # Corrupted Agent
        self.agent.iblees_noise = 0.9
        self.agent.qareen_filter = 0.9
        self.agent.local_friction = 1000.0

        result = self.engine.run_repair_lifecycle()

        # Assertions
        assert result['final_c_dev'] > 10.0 # Should be healthy
        assert result['final_qareen'] < 0.9 # Should be reduced (0.9 - 0.6 = 0.3)
        assert result['final_noise'] < 0.9 # Should be dampened (0.9 * 0.15 = 0.135)
