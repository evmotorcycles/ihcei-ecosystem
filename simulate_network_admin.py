from src.nere.network_admin import NetworkOfAnfusAdmin, Node, InteractionResult

def run_network_simulation():
    admin = NetworkOfAnfusAdmin()

    # Setup Nodes
    # Node A: Humble Scholar (High Phi, High G_ij, Low Conceit)
    node_a = Node("Node_A (Humble)", 5.0, "Advanced")
    # Node B: Arrogant Tyrant (High Phi, Low Press, High Conceit)
    node_b = Node("Node_B (Tyrant)", 5.0, "Advanced")

    receiver = Node("Student_X", 1.0, "Student")

    print("\n--- Network of Anfus: System Admin Logs ---")

    # 1. Simulate Success (Liquid Network)
    print("\n[Simulation 1: Zakat Flow (Success)]")
    result_a = admin.process_interaction(
        sender=node_a,
        receiver=receiver,
        text="Here is the evidence and principles for your consideration.",
        connection_strength=0.9,
        domain_compatibility=1.0,
        press_alignment=1.0
    )
    print(f"Sender: {node_a.id}")
    print(f"Status: {result_a.status}")
    print(f"G_ij Tensor: {result_a.g_ij:.2f}")
    print(f"System Friction (h): {result_a.h_network}")
    print(f"Network Growth: {result_a.network_growth:.2f}x (Exponential)")
    print(f"Message: {result_a.message}")

    # 2. Simulate Failure (Jaheem Protocol)
    print("\n[Simulation 2: Gate 7 Violation (Failure)]")
    result_b = admin.process_interaction(
        sender=node_b,
        receiver=receiver,
        text="You cannot understand this without me. Listen to me and obey.",
        connection_strength=0.9,
        domain_compatibility=1.0,
        press_alignment=0.2
    )
    print(f"Sender: {node_b.id}")
    print(f"Status: {result_b.status}")
    print(f"G_ij Tensor: {result_b.g_ij:.2f}")
    print(f"System Friction (h): {result_b.h_network} (SPIKE)")
    print(f"Network Growth: {result_b.network_growth:.2f} (HALTED)")
    print(f"Message: {result_b.message}")

if __name__ == "__main__":
    run_network_simulation()
