import numpy as np

class MillatSyntaxMatrix:
    """
    Models the civilization's 'millat' as a Syntax Matrix (D_syntax) within the QG-COS.
    Calculates semantic drift and its thermodynamic cost on systemic governance.
    """
    def __init__(self, base_matrix: np.ndarray):
        assert base_matrix.ndim == 2 and base_matrix.shape[0] == base_matrix.shape[1]
        self.base = base_matrix.astype(float)
        self.n = self.base.shape[0]

    @staticmethod
    def isotropic_noise(n, noise_level):
        """Constructs a symmetric noise matrix scaled by noise_level."""
        rng = np.random.default_rng()
        W = rng.normal(scale=1.0, size=(n, n))
        W = 0.5 * (W + W.T) # Symmetric to model correlated semantic shifts
        spec = np.linalg.norm(W, ord=2)
        if spec == 0:
            return np.zeros_like(W)
        return (noise_level / spec) * W

    def perturb(self, noise_matrix: np.ndarray):
        """Applies additive perturbation (semantic drift) to the baseline locution."""
        return self.base + noise_matrix

    def lexicon_distortion(self, observed_matrix):
        """
        Calculates Lexicon Distortion L using the Frobenius norm of the
        difference between the Identity matrix and the orthonormal projection.
        """
        U, s, Vt = np.linalg.svd(observed_matrix, full_matrices=False)
        P = U @ Vt
        I = np.eye(self.n)
        L = np.linalg.norm(I - P, ord='fro')
        return float(L)

    def discipline_scalar(self, mulk_integrity, L, noise_penalty_alpha=1.0):
        """Computes D for the ADGE equation: E = U * D^2"""
        coherence = np.exp(-noise_penalty_alpha * L)
        D = float(np.clip(mulk_integrity * coherence, 0.0, 1.0))
        return D

    def systemic_friction(self, L, base_friction=1e-3, beta=5.0):
        """Calculates communication/trust costs which scale exponentially with L."""
        return base_friction * np.exp(beta * L)

    def adge_energy(self, U, D):
        """Computes sustainable civilizational value: E = U * D^2"""
        return float(U * (D ** 2))

def run_monte_carlo_stress_test(
    dimensions=10,
    iterations=1000,
    noise_level=0.5,
    mulk_integrity=0.8,
    U=1_000_000,
    noise_penalty_alpha=1.0,
    beta=5.0
):
    """
    Executes a Monte Carlo simulation to stress-test the D_syntax matrix
    against probabilistic semantic corruption.
    """
    print(f"--- IHCEI Monte Carlo Initialization ---")
    print(f"Iterations: {iterations} | Matrix Dim: {dimensions}x{dimensions} | Noise Level: {noise_level}")
    print(f"Mulk Integrity: {mulk_integrity} | Raw Utility (U): {U}\n")

    base_identity = np.eye(dimensions)
    system = MillatSyntaxMatrix(base_identity)

    # Output arrays
    results_L = np.zeros(iterations)
    results_D = np.zeros(iterations)
    results_friction = np.zeros(iterations)
    results_E = np.zeros(iterations)

    for i in range(iterations):
        # 1. Generate stochastic semantic noise
        noise_matrix = system.isotropic_noise(dimensions, noise_level)

        # 2. Perturb the Millat matrix
        observed_matrix = system.perturb(noise_matrix)

        # 3. Calculate physics variables
        L = system.lexicon_distortion(observed_matrix)
        D = system.discipline_scalar(mulk_integrity, L, noise_penalty_alpha)
        friction = system.systemic_friction(L, base_friction=1e-3, beta=beta)
        E = system.adge_energy(U, D)

        # 4. Store results
        results_L[i] = L
        results_D[i] = D
        results_friction[i] = friction
        results_E[i] = E

    # Compute Statistical Bounds
    print("--- THERMODYNAMIC DIAGNOSTIC OUTPUT ---")

    metrics = {
        "Lexicon Distortion (L)": results_L,
        "Systemic Friction (\\hbar_network)": results_friction,
        "Discipline Scalar (D)": results_D,
        "ADGE Essence (E)": results_E
    }

    for name, data in metrics.items():
        mean_val = np.mean(data)
        p05 = np.percentile(data, 5)
        p95 = np.percentile(data, 95)
        print(f"{name}:")
        print(f"  Mean: {mean_val:.4f}  |  90% CI: [{p05:.4f}, {p95:.4f}]")

if __name__ == "__main__":
    # Execute stress test with moderate historical semantic noise
    run_monte_carlo_stress_test(noise_level=0.35, mulk_integrity=0.75, U=10_000_000)
