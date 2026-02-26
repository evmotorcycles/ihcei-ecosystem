from src.simulation.mulk_entropy_engine import MulkTensor, Agent, NetworkADGE, SystemWideEntropyError, verify_kitchen_protocol
import numpy as np

def run_simulation(scenario_name, tensor, agents, steps=15):
    print(f"\n--- Simulation: {scenario_name} ---")
    print(f"{'Step':<5} | {'Alignment':<10} | {'h_network':<10} | {'C_dev':<10} | {'Status'}")
    print("-" * 60)

    network = NetworkADGE(agents, tensor)

    for step in range(1, steps + 1):
        alignment = network.governance_tensor.calculate_alignment()
        try:
            c_dev = network.simulate_step()
            status = "STABLE"
            print(f"{step:<5} | {alignment:.4f}     | {network.h_network:.4f}     | {c_dev:.4f}     | {status}")
        except SystemWideEntropyError as e:
            print(f"{step:<5} | {alignment:.4f}     | {network.h_network:.4f}     | COLLAPSED  | KERNEL PANIC")
            print(f"\n[!!!] {e}")
            break

def prove_kitchen_protocol():
    print("\n--- Kitchen Protocol Verification (E = U * D^2) ---")
    u_massive = 1_000_000
    d_corrupt = 0.0
    essence = verify_kitchen_protocol(u_massive, d_corrupt)
    print(f"Input U: {u_massive:,}")
    print(f"Input D: {d_corrupt}")
    print(f"Calculated Essence (E): {essence}")
    if essence == 0.0:
        print("PROOF VERIFIED: Zero Governance yields Zero Essence.")
    else:
        print("PROOF FAILED.")

# Scenario 1: Healthy Network
healthy_tensor = MulkTensor(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
healthy_agents = [Agent(f"H{i}", 100, 1.0, 5.0) for i in range(5)]

# Scenario 2: Pharaoh Model (Corrupted Mulk)
# Alignment = 0.05
pharaoh_tensor = MulkTensor(0.1, 0.0, 0.1, 0.0, 0.0, 0.1, 0.1, 0.1, 0.0, 0.0)
pharaoh_agents = [Agent(f"P{i}", 1_000_000, 0.1, 5.0) for i in range(5)]

if __name__ == "__main__":
    prove_kitchen_protocol()
    run_simulation("Healthy Network (Sovereign)", healthy_tensor, healthy_agents)
    run_simulation("Pharaoh Model (Tyranny)", pharaoh_tensor, pharaoh_agents)
