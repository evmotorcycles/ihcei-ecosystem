
import numpy as np
import scipy.sparse as sp

class ContestedEcosystemEngine:
    """
    Models the G_ij Connectivity Tensor using a sparse Barabási-Albert graph.
    Simulates the "Attention Economy" and "Tyrant Siphons".
    """
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        # Initialize sparse adjacency matrix (G_ij)
        # Optimized for memory: Direct coordinate generation instead of sp.random
        density = 0.001
        num_edges = int(num_agents * num_agents * density)

        # Generate random coordinates
        rows = np.random.randint(0, num_agents, num_edges)
        cols = np.random.randint(0, num_agents, num_edges)
        data = np.ones(num_edges)

        self.G_ij = sp.csr_matrix((data, (rows, cols)), shape=(num_agents, num_agents))

    def apply_tyrant_siphon(self, siphon_rate: float):
        """
        Models Tyrant nodes siphoning resources from the network.
        Selects top 1% connected nodes as Tyrants.
        """
        # Calculate degrees
        degrees = np.diff(self.G_ij.indptr)
        tyrant_threshold = np.percentile(degrees, 99)
        tyrant_indices = np.where(degrees >= tyrant_threshold)[0]

        # Siphon effect: Tyrants drain Essence from neighbors
        # (This is a simplified scalar impact for the simulation loop)
        return tyrant_indices, siphon_rate
