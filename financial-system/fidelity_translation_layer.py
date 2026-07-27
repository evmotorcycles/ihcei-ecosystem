import jax
import jax.numpy as jnp

class FidelityTranslationLayer:
    """
    The Fidelity Translation Layer (FTL) implements a hybrid routing architecture
    designed to escape the Anti-Selection Trap.

    Rather than acting as a rigid Sovereign block that enforces isolation (which
    causes U to collapse), the FTL couples with the global network. It maps
    OQM operational protocols to measurable thermodynamic variables:
      - Al Baya (Trade/Risk-Sharing): High fidelity (D_enc -> 1.0), low friction.
      - Riba (Usury/Synthetic Debt): Introduces measureable friction/latency (tau_v)
        and say-do dissonance (sigma), which degrades D per hop.

    The router seeks to maximize total Thermodynamic Yield (E = U * D^n), balancing
    the massive capacity (U) of conventional hubs against the high fidelity (D) of
    Sovereign nodes.
    """

    def __init__(self, base_d_baya=0.98, base_d_riba=0.85, zombie_floor=0.50):
        self.base_d_baya = float(base_d_baya)
        self.base_d_riba = float(base_d_riba)
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
                       say_do_dissonance: jnp.ndarray,
                       hop_counts: jnp.ndarray,
                       is_riba: jnp.ndarray) -> dict:
        """
        Evaluates a set of parallel routing paths.

        Args:
            capacities (U): The raw throughput/capacity of the path.
            say_do_dissonance (sigma): Measured operational friction (0.0 to 1.0).
            hop_counts (n): Number of intermediaries.
            is_riba: Boolean array indicating if the path relies on conventional
                     synthetic debt (True) or risk-sharing Al Baya (False).

        Returns:
            Dictionary containing computed fidelity, yield E, and optimal path index.
        """
        # Determine base fidelity based on protocol (Riba vs Al Baya)
        base_fidelities = jnp.where(is_riba, self.base_d_riba, self.base_d_baya)

        # Operational dissonance (sigma) further degrades fidelity
        # D_actual = D_base * (1 - sigma)
        actual_fidelities = base_fidelities * (1.0 - say_do_dissonance)

        # Cap fidelity to avoid negative or >1 values
        actual_fidelities = jnp.clip(actual_fidelities, 0.01, 1.0)

        retained_fidelities = actual_fidelities ** hop_counts

        # Calculate Thermodynamic Yield E
        yields = self.calculate_yield(capacities, actual_fidelities, hop_counts)

        # Penalize paths that breach the epistemic zombie floor
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
