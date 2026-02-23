
import random
from src.core.qg_cos_cgmm import ADGENetwork, CGMM_Agent, GovernancePhysics

def run_simulation():
    """
    Multi-Agent Stress Test Simulation.
    """
    NUM_AGENTS = 10

    # 1. Generate 10 CGMM Agents with random cognitive stages
    print(f"--- 1. Generating {NUM_AGENTS} CGMM Agents ---")
    agents = []
    network = ADGENetwork(num_agents=NUM_AGENTS)

    # Use a fixed seed for reproducibility
    random.seed(42)

    for i in range(NUM_AGENTS):
        stage = random.randint(1, 12)
        agents.append(CGMM_Agent(f"Agent-{i}", stage))
        network.set_agent_stage(i, stage)
        print(f"Agent-{i}: Stage {stage}")

    # Set random alignments (mutual)
    print("\n--- Setting Random Alignments ---")
    for i in range(NUM_AGENTS):
        for j in range(NUM_AGENTS):
            if i != j:
                # Random alignment between 0.0 and 1.0
                alignment = random.uniform(0.0, 1.0)
                network.set_alignment(i, j, alignment)

    # 2. Feed them a standardized "Market Fluctuation" event
    EVENT_UTILITY = 100.0
    EVENT_PROTOCOL_TRUTH = 50.0

    print(f"\n--- 2. Standardized Market Fluctuation Event ---")
    print(f"Event Utility: {EVENT_UTILITY}, Protocol Truth: {EVENT_PROTOCOL_TRUTH}")

    total_essence = 0.0
    for agent in agents:
        # Evaluate event for each agent
        # Note: evaluate_event prints output, we might want to suppress it or just let it print
        # For simulation clarity, we'll just sum the result without printing details for each
        perceived_truth = GovernancePhysics.tqg_cfe_perception(EVENT_PROTOCOL_TRUTH, agent.stage)
        steward_outcome = GovernancePhysics.kitchen_protocol(EVENT_UTILITY, perceived_truth)
        total_essence += steward_outcome

    print(f"Total Network Essence Generated (Sum of Individual Agents): {total_essence:.2f}")

    # 3. Calculate C_dev drop as Gates of Entropy open
    print(f"\n--- 3. Network C_dev vs. 7 Gates of Entropy ---")
    print(f"{'Open Gates':<12} | {'C_dev':<15} | {'Drop %':<10}")
    print("-" * 45)

    # Calculate baseline (0 gates)
    baseline_c_dev = network.calculate_c_dev(open_gates_of_entropy=0)

    for gates in range(8): # 0 to 7
        c_dev = network.calculate_c_dev(open_gates_of_entropy=gates)
        drop_percent = ((baseline_c_dev - c_dev) / baseline_c_dev) * 100
        print(f"{gates:<12} | {c_dev:<15.2f} | {drop_percent:<10.1f}%")

if __name__ == "__main__":
    run_simulation()
