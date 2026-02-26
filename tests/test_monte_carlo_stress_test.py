import pytest
import numpy as np
from src.simulation.monte_carlo_stress_test import MillatSyntaxMatrix

class TestMillatSyntaxMatrix:
    def setup_method(self):
        self.dims = 5
        self.base = np.eye(self.dims)
        self.system = MillatSyntaxMatrix(self.base)

    def test_millat_syntax_matrix_initialization(self):
        """Verify initialization sets up the base matrix correctly."""
        assert np.array_equal(self.system.base, self.base)
        assert self.system.n == self.dims

    def test_isotropic_noise(self):
        """Verify noise generation produces symmetric matrices of correct shape."""
        noise_level = 0.5
        noise = self.system.isotropic_noise(self.dims, noise_level)

        # Check shape
        assert noise.shape == (self.dims, self.dims)

        # Check symmetry
        assert np.allclose(noise, noise.T)

        # Check spectral norm constraint (if not zero)
        spec = np.linalg.norm(noise, ord=2)
        if spec > 1e-10:
            assert np.isclose(spec, noise_level)

    def test_lexicon_distortion(self):
        """
        Verify L calculation.
        Identity matrix should have L=0.
        Perturbed matrix should have L>0.
        """
        # Case 1: Identity (No distortion)
        L_identity = self.system.lexicon_distortion(self.base)
        assert np.isclose(L_identity, 0.0)

        # Case 2: Perturbed
        noise = np.random.normal(0, 0.1, (self.dims, self.dims))
        perturbed = self.base + noise
        L_perturbed = self.system.lexicon_distortion(perturbed)

        # L should be non-negative
        assert L_perturbed >= 0.0
        # Given random noise, L is likely > 0
        assert L_perturbed > 0.0

    def test_discipline_scalar(self):
        """Verify D calculation logic and clamping."""
        mulk_integrity = 0.8

        # Case 1: L=0 -> D = mulk_integrity
        D_pure = self.system.discipline_scalar(mulk_integrity, L=0.0)
        assert np.isclose(D_pure, mulk_integrity)

        # Case 2: High L -> D should decay
        D_decay = self.system.discipline_scalar(mulk_integrity, L=10.0)
        assert D_decay < D_pure

        # Case 3: Clamping
        # Even if mulk_integrity > 1 (theoretical edge case), result clipped to 1.0?
        # The function clips at 1.0.
        D_clipped = self.system.discipline_scalar(1.5, L=0.0)
        assert np.isclose(D_clipped, 1.0)

    def test_adge_energy(self):
        """Verify ADGE calculation E = U * D^2."""
        U = 100.0
        D = 0.5
        expected_E = 100.0 * (0.5 ** 2) # 25.0

        E = self.system.adge_energy(U, D)
        assert np.isclose(E, expected_E)
