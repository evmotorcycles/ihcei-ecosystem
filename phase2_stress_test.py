import json
import logging
from src.core.ihcei_x import IHCEI_X
from src.novora.nere import NERE

# Configure logging to show info
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_stress_test():
    print("System Actuation: Initialize the NERE Cognitive Mirror and the full IHCEI Sovereign Governance Engine.")

    input_domain = "Neuroscience"
    input_policy = "Facilitating Synaptic Pruning across the network to clear the Default Mode Network, distributing decision-making to local nodes to prevent any absolute authority from forming."

    print(f"Input Domain: {input_domain}")
    print(f"Input Policy: \"{input_policy}\"")

    # 1. Ibra Engine Translation
    ibra = IHCEI_X()
    terms_to_translate = ["Synaptic Pruning", "Default Mode Network"]
    ibra_results = []
    for term in terms_to_translate:
        result = ibra.ibra_translation(input_domain, term)
        ibra_results.append(result)

    # 2. ADGE Calculation & 3. NERE Verdict
    nere = NERE()
    # Note: Phase 2 Stress Test requires G_ij=0.8
    nere_result = nere.reason_ethically(input_policy, g_ij_zakat_flow=0.8)

    # Construct Final JSON Log
    execution_log = {
        "Ibra_Mapping_Results": ibra_results,
        "ADGE_State": {
            "h_network_noise": nere_result["bias_noise_hbar"],
            "c_dev_coefficient": nere_result["c_dev_coefficient"],
            "agency_delta": nere_result["agency_delta"]
        },
        "Final_NERE_Verdict": nere_result["compliance_status"]
    }

    print("\n--- JSON Execution Log ---")
    print(json.dumps(execution_log, indent=4))

if __name__ == "__main__":
    run_stress_test()
