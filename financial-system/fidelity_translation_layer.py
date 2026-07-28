import jax
import jax.numpy as jnp

class HybridSovereignMesh:
    """
    The Hybrid Sovereign Mesh implements a routing architecture designed to escape
    the Anti-Selection Trap while neutralizing the 'Debt Trap' of fractional-reserve finance.

    Rather than acting as a rigid block that enforces absolute isolation (which
    causes capacity U to collapse), the Mesh couples with the global network. It maps
    operational protocols to measurable thermodynamic variables:
      - True Risk-Sharing (100% Full Reserve, delta U = 0): High fidelity (D_enc -> 1.0),
        low systemic friction. It preserves structural integrity over time.
      - Synthetic Debt (Fractional Reserve, delta U > 0): Temporarily inflates capacity (U),
        but introduces measurable systemic friction/latency (tau_v) and structural
        dissonance (sigma). This imposes an exponential, inescapable compounding penalty
        that degrades D per hop/time-step.

    The router seeks to maximize total Thermodynamic Yield (E = U * D^n), balancing
    the massively inflated capacity (U) of synthetic-debt hubs against the
    high-fidelity structural permanence (D) of risk-sharing Sovereign nodes.
    """

    def __init__(self, base_d_risk_sharing=0.98, base_d_synthetic_debt=0.85, zombie_floor=0.50):
        self.base_d_risk_sharing = float(base_d_risk_sharing)
        self.base_d_synthetic_debt = float(base_d_synthetic_debt)
        self.zombie_floor = float(zombie_floor)

    @staticmethod
    @jax.jit
    def calculate_yield(u_capacity: jnp.ndarray,
                        hop_fidelities: jnp.ndarray,
                        hop_counts: jnp.ndarray) -> jnp.ndarray:
        """
        Calculates the thermodynamic yield E = U * (D^n)
        hop_fidelities is the mean fidelity D for the path.
        """
        retained_fidelity = hop_fidelities ** hop_counts
        return u_capacity * retained_fidelity

    def evaluate_paths(self,
                       capacities: jnp.ndarray,
                       structural_dissonance: jnp.ndarray,
                       hop_counts: jnp.ndarray,
                       is_synthetic_debt: jnp.ndarray) -> dict:
        """
        Evaluates a set of parallel routing paths, modeling the Debt Trap reversal.

        Args:
            capacities (U): The raw throughput/capacity of the path (inflated if synthetic).
            structural_dissonance (sigma): Measured operational friction (0.0 to 1.0).
            hop_counts (n): Number of intermediaries or time steps.
            is_synthetic_debt: Boolean array indicating if the path relies on
                               synthetic debt (True) or true risk-sharing (False).

        Returns:
            Dictionary containing computed fidelity, yield E, and optimal path index.
        """
        # Determine base fidelity based on protocol
        base_fidelities = jnp.where(is_synthetic_debt, self.base_d_synthetic_debt, self.base_d_risk_sharing)

        # Operational dissonance (sigma) further degrades fidelity.
        # This models the "Debt Trap": as debt compounds, structural dissonance rises,
        # degrading the baseline fidelity.
        actual_fidelities = base_fidelities * (1.0 - structural_dissonance)

        # Cap fidelity to avoid negative or >1 values
        actual_fidelities = jnp.clip(actual_fidelities, 0.01, 1.0)

        # The compounding penalty over n hops/time-steps
        retained_fidelities = actual_fidelities ** hop_counts

        # Calculate Thermodynamic Yield E
        # Synthetic debt paths may have massive U, but their low D imposes a heavy penalty over time.
        yields = self.calculate_yield(capacities, actual_fidelities, hop_counts)

        # Penalize paths that breach the epistemic zombie floor (default/collapse)
        zombie_mask = retained_fidelities < self.zombie_floor
        # If it breaches, yield is zeroed out as the information/value is effectively lost
        effective_yields = jnp.where(zombie_mask, 0.0, yields)

        optimal_path_idx = jnp.argmax(effective_yields)

        return {
            "retained_fidelities": retained_fidelities,
            "raw_yields": yields,
            "effective_yields": effective_yields,
            "zombie_mask": zombie_mask,
            "optimal_path_index": int(optimal_path_idx),
            "optimal_yield": float(effective_yields[optimal_path_idx])
        }
