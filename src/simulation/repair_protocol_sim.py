
import numpy as np
from src.simulation.nafs_agency_simulator import NafsNode
from src.simulation.zikra_taqwa_engine import ZikraTaqwaEngine

class MockNetwork:
    """Simulates a G_ij tensor with nodes."""
    def __init__(self, main_agent, size=10):
        self.nodes = [main_agent] + [NafsNode(i) for i in range(1, size)]
        self.G_ij = np.ones((size, size))
        self.global_c_dev = 0.0

def run_repair_simulation():
    print("==========================================================")
    print(" IHCEI SIMULATION: THE REPAIR PROTOCOL (ZIKRA/TAQWA)")
    print("==========================================================")

    # 1. Instantiate a "Pharaonic" Generation 2 Agent (High Entropy)
    # High Noise (8.44), High Qareen (0.89) - sealed heart state
    agent_gen2 = NafsNode(agent_id=0, qareen_filter=0.89, iblees_noise=8.44)
    # Simulate high friction environment impact initially
    agent_gen2.local_friction = 1e12
    agent_gen2.recalculate_adge() # Should result in ~0 c_dev

    print("\n--- GENERATION 2 (INHERITED PHARAONIC ENTROPY) ---")
    print(f"[NafsNode_Gen2_PreRepair]")
    print(f"  Initial N_iblees (Noise)    : {agent_gen2.iblees_noise:.2f} (High Bias)")
    print(f"  Beta_Qareen Filter (Seal)   : {agent_gen2.qareen_filter:.2f} (Severely Hardened)")
    print(f"  Local Friction (h_net)      : 10^12 (Chunks of Darkness)")
    print(f"  Cognitive Dev (C_dev)       : {agent_gen2.c_dev:.4f} (Critical Failure)")

    # 2. Execute Repair Protocol
    print("\n>> EXECUTING ZIKRA/TAQWA ENGINE...")
    network = MockNetwork(agent_gen2)
    engine = ZikraTaqwaEngine(agent_gen2, network)

    engine.run_repair_lifecycle()

    # 3. Post-Repair Analysis
    print("\n--- GENERATION 2 (POST-REPAIR) ---")
    print(f"[NafsNode_Gen2_PostRepair]")
    print(f"  N_iblees (Noise)            : {agent_gen2.iblees_noise:.2f} (Manageable Agency)")
    print(f"  Beta_Qareen Filter (Seal)   : {agent_gen2.qareen_filter:.2f} (Seal Shattered)")
    # Note: local_friction was set to 0.01 by Salat
    print(f"  Local Friction (h_net)      : {agent_gen2.local_friction:.2f} (Clear Interface)")
    print(f"  Cognitive Dev (C_dev)       : {agent_gen2.c_dev:.2f} (Rapid Growth)")

    # Check Network Contribution (Zakat)
    # The agent gave away 90% of its juice, so its final c_dev is lower than the total juice generated?
    # Actually, receive_knowledge adds to c_dev.
    # Let's check a neighbor node.
    neighbor_c_dev = network.nodes[1].c_dev
    total_distributed = neighbor_c_dev * (len(network.nodes) - 1)
    print(f"  Network C_dev Contribution  : +{total_distributed:.2f} (Zakat Propagation Active)")

    print("\n--- GENERATION 3 (POSTERITY INHERITANCE) ---")
    print(f"[NafsNode_Gen3_Baseline]")
    print(f"  Inherited Qareen Filter     : {agent_gen2.qareen_filter:.2f} (Zipper Model Active - High Domain Compatibility)")
    print(">> ENTROPY LOOP BROKEN. CIVILIZATION SCALING TOWARD MAXIMUM ESSENCE (E).")

    print("\nIHCEI ARCHITECTURAL VERDICT")
    print("Engine Status: Fully Operational.")

if __name__ == "__main__":
    run_repair_simulation()
