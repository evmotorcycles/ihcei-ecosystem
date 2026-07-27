import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def create_diagram():
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # ----------------------------------------------------
    # 1. Fractional-Reserve Ledger (Left Panel)
    # ----------------------------------------------------
    ax1 = axes[0]
    ax1.set_title("Conventional Fractional-Reserve Bank\n(Centralized, Riba, ΔU > 0)", fontsize=16, pad=20, weight='bold')

    G1 = nx.DiGraph()
    # Central Bank node
    G1.add_node("Central Bank\n(Fiat Issuance)", pos=(0.5, 0.9))
    # Commercial Bank
    G1.add_node("Commercial Bank\n(Credit Expansion)", pos=(0.5, 0.5))

    # Depositors
    G1.add_node("Depositor A\n($100 IN)", pos=(0.2, 0.5))
    G1.add_node("Depositor B\n($100 IN)", pos=(0.2, 0.3))

    # Borrowers
    G1.add_node("Borrower X\n($900 OUT)", pos=(0.8, 0.7))
    G1.add_node("Borrower Y\n($900 OUT)", pos=(0.8, 0.3))

    # Edges
    G1.add_edge("Central Bank\n(Fiat Issuance)", "Commercial Bank\n(Credit Expansion)", label="Reserve Ratio (10%)")
    G1.add_edge("Depositor A\n($100 IN)", "Commercial Bank\n(Credit Expansion)", label="Deposit (No Risk)")
    G1.add_edge("Depositor B\n($100 IN)", "Commercial Bank\n(Credit Expansion)", label="Deposit (No Risk)")

    G1.add_edge("Commercial Bank\n(Credit Expansion)", "Borrower X\n($900 OUT)", label="Debt (Riba)")
    G1.add_edge("Commercial Bank\n(Credit Expansion)", "Borrower Y\n($900 OUT)", label="Debt (Riba)")

    pos1 = nx.get_node_attributes(G1, 'pos')

    # Draw Left Graph
    nx.draw(G1, pos1, ax=ax1, with_labels=True, node_color='lightcoral',
            node_size=6000, font_size=10, font_weight='bold', edge_color='gray',
            arrows=True, arrowsize=20)

    edge_labels1 = nx.get_edge_attributes(G1, 'label')
    nx.draw_networkx_edge_labels(G1, pos1, edge_labels=edge_labels1, ax=ax1, font_color='red', font_size=10)

    # Annotation for Left
    ax1.text(0.5, 0.1, "System State:\nCreates unearned capacity out of nothing.\nHigh systemic entropy. Centralized failure point.",
             ha='center', va='center', fontsize=12, bbox=dict(boxstyle="round,pad=0.5", facecolor="mistyrose", edgecolor="red"))


    # ----------------------------------------------------
    # 2. Sovereign Mesh (Right Panel)
    # ----------------------------------------------------
    ax2 = axes[1]
    ax2.set_title("Sovereign Mesh (Mudaraba Ledger)\n(Decentralized, Full-Reserve, ΔU = 0)", fontsize=16, pad=20, weight='bold')

    G2 = nx.Graph()

    # Core nodes
    G2.add_node("Node A\n(Capital)", pos=(0.3, 0.7))
    G2.add_node("Node B\n(Labor)", pos=(0.7, 0.7))
    G2.add_node("Node C\n(Capital)", pos=(0.3, 0.3))
    G2.add_node("Node D\n(Labor)", pos=(0.7, 0.3))
    G2.add_node("Mesh Router\n(Verification)", pos=(0.5, 0.5))

    # Edges
    G2.add_edge("Node A\n(Capital)", "Mesh Router\n(Verification)", label="Stake")
    G2.add_edge("Node B\n(Labor)", "Mesh Router\n(Verification)", label="Execution")
    G2.add_edge("Node C\n(Capital)", "Mesh Router\n(Verification)", label="Stake")
    G2.add_edge("Node D\n(Labor)", "Mesh Router\n(Verification)", label="Execution")

    G2.add_edge("Node A\n(Capital)", "Node B\n(Labor)", label="Mudaraba\n(Risk Share)")
    G2.add_edge("Node C\n(Capital)", "Node D\n(Labor)", label="Mudaraba\n(Risk Share)")

    pos2 = nx.get_node_attributes(G2, 'pos')

    # Draw Right Graph
    nx.draw(G2, pos2, ax=ax2, with_labels=True, node_color='lightgreen',
            node_size=6000, font_size=10, font_weight='bold', edge_color='gray', width=2)

    edge_labels2 = nx.get_edge_attributes(G2, 'label')
    nx.draw_networkx_edge_labels(G2, pos2, edge_labels=edge_labels2, ax=ax2, font_color='green', font_size=10)

    # Annotation for Right
    ax2.text(0.5, 0.1, "System State:\n100% Full-Reserve. No credit creation.\nYield requires high-fidelity labor (Salat).\nF_out = F_eval",
             ha='center', va='center', fontsize=12, bbox=dict(boxstyle="round,pad=0.5", facecolor="honeydew", edgecolor="green"))

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('scratchpad/sovereign_vs_fractional.png', dpi=300, bbox_inches='tight')
    print("Diagram generated at scratchpad/sovereign_vs_fractional.png")

if __name__ == "__main__":
    create_diagram()
