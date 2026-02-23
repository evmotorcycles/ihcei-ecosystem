import numpy as np

class NERE_API_Optimized:
    def __init__(self, network_size=1000):
        self.network_size = network_size
        # Vectorized state management
        # Agent IDs are implicit indices 0 to network_size-1
        self.capacity_bounds = np.random.randint(1, 13, size=network_size)
        self.earned_essence = np.zeros(network_size, dtype=np.float64)
        self.entropy_friction = np.zeros(network_size, dtype=np.float64)

    def audit_input_batch(self, agent_ids, proposed_us, proposed_ds):
        """
        Vectorized audit of inputs for multiple agents.
        agent_ids: array-like of int
        proposed_us: array-like of float
        proposed_ds: array-like of float
        """
        agent_ids = np.asarray(agent_ids)
        us = np.asarray(proposed_us)
        ds = np.asarray(proposed_ds)

        # Get capacities for the target agents
        caps = self.capacity_bounds[agent_ids]

        # Check breaches
        # Condition: U > Capacity OR D > Capacity
        breach_mask = (us > caps) | (ds > caps)

        # Calculate friction updates
        # Friction += (U - Capacity) if breach
        # Wait, the original logic is:
        # if u > cap or d > cap:
        #    friction += (u - cap)
        #    d = 0.0

        friction_updates = np.zeros_like(us)
        friction_updates[breach_mask] = us[breach_mask] - caps[breach_mask]

        # Update friction state
        # Note: In original code, friction can be negative if u < cap but d > cap.
        # This behavior is preserved here.
        np.add.at(self.entropy_friction, agent_ids, friction_updates)

        # Apply governance collapse
        effective_ds = ds.copy()
        effective_ds[breach_mask] = 0.0

        # Calculate essence
        essence_generated = us * (effective_ds ** 2)

        # Update earned essence if > 0
        positive_essence_mask = essence_generated > 0

        # We need to add essence only where essence > 0
        # Create an array of updates
        essence_updates = np.zeros_like(essence_generated)
        essence_updates[positive_essence_mask] = essence_generated[positive_essence_mask]

        np.add.at(self.earned_essence, agent_ids, essence_updates)

        return {
            "agent_ids": agent_ids,
            "essence_generated": essence_generated,
            "entropy_friction_snapshot": self.entropy_friction[agent_ids],
            "breach_mask": breach_mask
        }

    def audit_input(self, agent_id, text_packet, proposed_u, proposed_d):
        """
        Wrapper to maintain single-agent interface compatibility,
        but using the vectorized backend.
        """
        res = self.audit_input_batch([agent_id], [proposed_u], [proposed_d])

        essence = res["essence_generated"][0]
        friction = res["entropy_friction_snapshot"][0]
        capacity = self.capacity_bounds[agent_id]

        if essence > 0 and friction == 0:
            agency_delta = "Positive (Kasabat)"
            score = "GREEN: Agency Preserved. C_dev of the network enhanced."
        elif essence > 0 and friction > 0:
            agency_delta = "Frictional"
            score = "YELLOW: Marginal capacity breach. \\hbar_{corruption} increasing."
        else:
            agency_delta = "Void (Ektasabat)"
            score = "RED: Category Error Detected (D=0). Essence mathematically voided."

        return {
            "Packet": text_packet,
            "Agent_Capacity": int(capacity),
            "Agency_Delta": agency_delta,
            "Generated_Essence": float(essence),
            "NERE_Score": score
        }
