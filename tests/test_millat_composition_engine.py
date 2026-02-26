
import pytest
import numpy as np
from src.simulation.millat_composition_engine import MillatCompositionEngine

class TestMillatCompositionEngine:
    def setup_method(self):
        self.engine = MillatCompositionEngine(size=10)

    def test_initialization(self):
        """
        Verify that the Millat Codebase initializes with perfect semantic alignment (Identity Matrix).
        """
        assert np.array_equal(self.engine.D_syntax, np.eye(10))
        assert self.engine.get_integrity() == 1.0
        assert self.engine.calculate_systemic_friction() == 1.0 # 1.0 / 1.0^2
        assert self.engine.calculate_cognitive_development(1.0) == 1.0

    def test_qurayshite_bug_impact(self):
        """
        Verify that injecting the Qurayshite Bug (Lexicon Corruption) degrades D_syntax integrity.
        """
        initial_integrity = self.engine.get_integrity()
        self.engine.inject_qurayshite_bug(corruption_level=0.5)
        corrupted_integrity = self.engine.get_integrity()

        assert corrupted_integrity < initial_integrity
        assert corrupted_integrity < 1.0

    def test_friction_and_cdev_inverse(self):
        """
        Verify the inverse relationship between Systemic Friction (hbar_network) and Cognitive Development (C_dev).
        """
        # Inject significant corruption
        self.engine.inject_qurayshite_bug(corruption_level=0.8)
        self.engine.inject_qurayshite_bug(corruption_level=0.8)

        integrity = self.engine.get_integrity()
        friction = self.engine.calculate_systemic_friction()
        c_dev = self.engine.calculate_cognitive_development(friction)

        # As integrity drops (< 1), friction should rise (> 1)
        assert friction > 1.0

        # C_dev should drop (< 1)
        assert c_dev < 1.0

        # Mathematical verification
        expected_friction = 1.0 / (integrity ** 2)
        assert np.isclose(friction, expected_friction)
        assert np.isclose(c_dev, 1.0 / friction)

    def test_essence_collapse_with_high_utility(self):
        """
        Verify that Essence (E) collapses due to low D, regardless of high Utility (U).
        ADGE: E = U * D^2
        """
        high_utility = 1000.0

        # Case 1: Perfect Alignment
        e_perfect = self.engine.calculate_essence(high_utility)
        assert e_perfect == 1000.0 # 1000 * 1.0^2

        # Case 2: Corrupted D
        # Degrade D to approx 0.1
        while self.engine.get_integrity() > 0.1:
            self.engine.inject_qurayshite_bug(corruption_level=1.0)

        d_corrupted = self.engine.get_integrity()
        e_collapsed = self.engine.calculate_essence(high_utility)

        # E should be much lower than U
        assert e_collapsed < high_utility
        assert np.isclose(e_collapsed, high_utility * (d_corrupted ** 2))

    def test_simulation_loop(self):
        """
        Run a short simulation and verify history tracking.
        """
        result = self.engine.run_simulation(steps=5, corruption_rate=0.5, utility=100.0)

        assert len(result['corruption_history']) > 0
        assert len(result['c_dev_history']) > 0
        assert len(result['essence_history']) > 0

        # Verify trend: Essence should generally decrease
        assert result['essence_history'][-1] < result['essence_history'][0]
