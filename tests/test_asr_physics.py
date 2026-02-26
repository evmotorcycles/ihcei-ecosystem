
import pytest
import numpy as np
from src.core.asr_physics import AsrPhysicsEngine

class TestAsrPhysics:
    def setup_method(self):
        self.engine = AsrPhysicsEngine(extraction_pressure=5.0)

    def test_khusr_default_state(self):
        """
        Verify that an agent with zero attributes suffers max loss.
        """
        loss = self.engine.calculate_khusr_loss(0.0, 0.0, 0.0, 0.0)
        assert loss == 5.0 # Max compression

    def test_success_filter(self):
        """
        Verify that full attributes reduce loss to zero.
        """
        loss = self.engine.calculate_khusr_loss(1.0, 1.0, 1.0, 1.0)
        assert loss == 0.0

    def test_partial_shielding(self):
        """
        Verify that partial attributes result in partial loss.
        """
        # Attributes at 0.5 -> Integrity = 0.5^0.25 = 0.84
        # Loss = 5.0 * (1 - 0.84) = 0.8
        loss = self.engine.calculate_khusr_loss(0.5, 0.5, 0.5, 0.5)
        assert 0.0 < loss < 5.0

    def test_vector_displacement(self):
        """
        Verify that Zulm (displacement) is applied proportional to loss.
        """
        tensor = np.zeros(10)
        loss = 2.0
        displaced = self.engine.apply_vector_displacement(tensor, loss)

        # Norm should be roughly proportional to loss * sqrt(10) * 0.5 (std dev)
        norm = np.linalg.norm(displaced)
        assert norm > 0.0
