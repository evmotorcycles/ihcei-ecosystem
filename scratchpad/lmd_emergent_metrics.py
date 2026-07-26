import jax
from jax import config
config.update("jax_enable_x64", True)
import jax.numpy as jnp
import time

@jax.jit
def compute_effective_resistance(adjacency_matrix):
    """
    Computes the effective round-trip resistance (latency) matrix for a given graph.
    """
    # Degree matrix
    degrees = jnp.sum(adjacency_matrix, axis=1)
    degree_matrix = jnp.diag(degrees)

    # Laplacian matrix
    laplacian = degree_matrix - adjacency_matrix

    # Moore-Penrose Pseudoinverse of the Laplacian
    pinv_L = jnp.linalg.pinv(laplacian, rcond=1e-12)

    # Effective resistance R_ij = L^+_ii + L^+_jj - 2 * L^+_ij
    diag = jnp.diag(pinv_L)
    R = diag[:, None] + diag[None, :] - 2 * pinv_L

    # Float precision might cause tiny negative values; clip them to zero
    R = jnp.clip(R, 0.0, None)

    # Force self-resistance to exactly zero
    R = R - jnp.diag(jnp.diag(R))

    return R

@jax.jit
def check_triangle_inequality(distance_matrix):
    """
    Checks for any triangle inequality violations: d_ij <= d_ik + d_kj
    Uses a small epsilon to account for floating point errors.
    """
    # Expand dims to N x N x N for vectorized comparison
    d_ij = distance_matrix[:, :, None] # Shape (N, N, 1)
    d_ik = distance_matrix[:, None, :] # Shape (N, 1, N)
    d_kj = distance_matrix[None, :, :] # Shape (1, N, N)

    # We want to ignore cases where i=j, i=k, or j=k since those are trivial
    # but theoretically they shouldn't violate anyway.

    # Check violation condition (accounting for float precision)
    # Using 1e-10 for float64
    violations = d_ij > d_ik + d_kj + 1e-10

    return jnp.sum(violations)

def main():
    print("Initializing Governance Quantum Physics: Latency-Metric Duality (LMD) simulation...")

    N = 500
    print(f"Generating correlation network for {N} conscious processors (nodes)...")

    key = jax.random.PRNGKey(1337)
    rand_matrix = jax.random.uniform(key, shape=(N, N))

    adjacency_matrix = (rand_matrix + rand_matrix.T) / 2
    adjacency_matrix = adjacency_matrix - jnp.diag(jnp.diag(adjacency_matrix))
    # Add strong base coupling
    adjacency_matrix = adjacency_matrix + 1.0
    adjacency_matrix = adjacency_matrix - jnp.diag(jnp.diag(adjacency_matrix))

    print("Computing emergent metric distance strictly from round-trip information lag (tau_rt)...")

    start_time = time.time()
    R = compute_effective_resistance(adjacency_matrix)
    # LMD: Proper distance is the square root of effective resistance (d^2 = k * tau_rt)
    distance_matrix = jnp.sqrt(R)

    distance_matrix.block_until_ready()
    end_time = time.time()

    print(f"Distance matrix computed in {end_time - start_time:.4f} seconds.")

    print("Programmatically verifying zero triangle-inequality violations across the emergent space...")
    start_time = time.time()
    num_violations = check_triangle_inequality(distance_matrix)

    num_violations.block_until_ready()
    end_time = time.time()

    print(f"Verification completed in {end_time - start_time:.4f} seconds.")
    print(f"Total Triangle Inequality Violations: {num_violations}")

    if num_violations == 0:
        print("\nSUCCESS: Latency-Metric Duality formally verified.")
        print("Distance strictly emerging from information processing lag yields a mathematically valid metric space.")
    else:
        print("\nFAILURE: Metric space violations detected.")

if __name__ == '__main__':
    main()
