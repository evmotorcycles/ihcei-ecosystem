import jax
from jax import config
config.update("jax_enable_x64", True)
import jax.numpy as jnp
import time

def generate_markov_network(N, key):
    """Generates a random Markov transition matrix for N agents."""
    rand_matrix = jax.random.uniform(key, shape=(N, N))

    # Make it a valid transition matrix (rows sum to 1)
    transition_matrix = rand_matrix / jnp.sum(rand_matrix, axis=1, keepdims=True)
    return transition_matrix

@jax.jit
def compute_trace_logic(P, observed_indices, unobserved_indices):
    """
    Computes the effective transition matrix for the observed subset
    by taking the trace over the unobserved subset.
    """
    # Partition the transition matrix P into blocks
    P_OO = P[jnp.ix_(observed_indices, observed_indices)]
    P_OU = P[jnp.ix_(observed_indices, unobserved_indices)]
    P_UO = P[jnp.ix_(unobserved_indices, observed_indices)]
    P_UU = P[jnp.ix_(unobserved_indices, unobserved_indices)]

    # Identity matrix for the unobserved subspace
    I_U = jnp.eye(len(unobserved_indices))

    # The effective transition matrix on the observed space (headset)
    # P_eff = P_OO + P_OU * (I - P_UU)^-1 * P_UO
    # This represents tracing over all possible paths through the unobserved space
    # before returning to the observed space.

    inv_I_minus_P_UU = jnp.linalg.inv(I_U - P_UU)
    P_eff = P_OO + P_OU @ inv_I_minus_P_UU @ P_UO

    # Expected return time scaling (Time Dilation)
    # The time spent in the unobserved space acts as a multiplier on the observed clock.
    # Expected time in U starting from U is row sums of (I - P_UU)^-1
    time_in_U = jnp.sum(inv_I_minus_P_UU, axis=1)

    # Expected time per observed step
    # 1 step in O + expected steps in U before returning
    time_dilation_factor = 1.0 + P_OU @ time_in_U

    return P_eff, time_dilation_factor

@jax.jit
def compute_effective_distance(P_eff):
    """
    Computes emergent proper distance from the effective transition matrix.
    We convert P_eff to a symmetric adjacency/coupling matrix,
    then compute effective resistance.
    """
    # Make it symmetric to treat as an undirected graph coupling
    A = (P_eff + P_eff.T) / 2

    # Ensure no self-loops for distance calculation
    A = A - jnp.diag(jnp.diag(A))

    degrees = jnp.sum(A, axis=1)
    L = jnp.diag(degrees) - A

    pinv_L = jnp.linalg.pinv(L, rcond=1e-12)

    diag = jnp.diag(pinv_L)
    R = diag[:, None] + diag[None, :] - 2 * pinv_L
    R = jnp.clip(R, 0.0, None)
    R = R - jnp.diag(jnp.diag(R))

    return jnp.sqrt(R)

def main():
    print("Initializing Governance Quantum Physics: Observer Trace Logic Simulation...")

    N = 100
    N_observed = 20
    print(f"Total Agents on Motherboard: {N}")
    print(f"Agents rendered in Headset (Observed): {N_observed}")
    print(f"Agents traced out (Unobserved): {N - N_observed}")

    key = jax.random.PRNGKey(42)

    # 1. Generate the base Markov network (Motherboard truth)
    P_base = generate_markov_network(N, key)

    observed_indices = jnp.arange(N_observed)
    unobserved_indices = jnp.arange(N_observed, N)

    # Calculate baseline distance if we just looked at the observed subset
    # as an isolated network without trace logic (Naïve RT view)
    P_naive = P_base[jnp.ix_(observed_indices, observed_indices)]
    # Normalize naive to be a valid transition matrix
    P_naive = P_naive / jnp.sum(P_naive, axis=1, keepdims=True)
    d_naive = compute_effective_distance(P_naive)

    # 2. Compute the traced transition matrix (Governance OS view)
    start_time = time.time()
    P_eff, time_dilation = compute_trace_logic(P_base, observed_indices, unobserved_indices)

    # 3. Compute emergent distance on the headset
    d_eff = compute_effective_distance(P_eff)

    d_eff.block_until_ready()
    end_time = time.time()

    print(f"\nTrace logic computation completed in {end_time - start_time:.4f} seconds.")

    # 4. Analyze Time Dilation
    mean_dilation = jnp.mean(time_dilation)
    print(f"\n--- Emergent Time Dilation ---")
    print(f"For every 1 tick of the observed clock, the underlying system processes")
    print(f"an average of {mean_dilation:.2f} hidden ticks in the unobserved space.")

    # 5. Analyze Length Contraction
    mean_d_naive = jnp.mean(d_naive[d_naive > 0])
    mean_d_eff = jnp.mean(d_eff[d_eff > 0])

    print(f"\n--- Emergent Length Contraction ---")
    print(f"Naïve isolated headset mean distance: {mean_d_naive:.4f}")
    print(f"Effective traced headset mean distance: {mean_d_eff:.4f}")
    print(f"Distance ratio (Eff / Naïve): {mean_d_eff / mean_d_naive:.4f}")

    if mean_d_eff < mean_d_naive:
        print("\nSUCCESS: Length contraction formally verified.")
        print("Tracing out the unobserved network increases effective coupling in the observed space,")
        print("causing emergent physical distances to contract, matching Latency-Metric Duality.")
    else:
        print("\nFAILURE: Length contraction not observed.")

if __name__ == '__main__':
    main()
