
import numpy as np
from src.core.asr_physics import AsrPhysicsEngine
from src.simulation.ugo import UnifiedGovernanceObject

def run_asr_stress_test():
    print("==========================================================")
    print(" IHCEI SIMULATION: AL-ASR (THE PRESSING/EXTRACTION)")
    print("==========================================================")

    # Baseline UGO
    mulk = np.ones(10)
    millat = np.eye(10)
    ugo = UnifiedGovernanceObject("Baseline", mulk, millat, 1000.0)

    # Initialize Asr Engine with High Extraction Pressure
    asr = AsrPhysicsEngine(extraction_pressure=10.0)

    # Scenario 1: The 'An'am' Agent (Herds)
    # Lacks the 4 attributes (Iman, Amal, Haqq, Sabr). Filter fails.
    print("\n[Scenario 1: An'am Agent (Weak Filter)]")
    loss_anam = asr.calculate_khusr_loss(0.1, 0.1, 0.1, 0.1) # Weak attributes
    print(f"  Calculated Khusr (Waste/Pulp): {loss_anam:.4f}")

    # Apply Zulm (Displacement)
    displaced_mulk = asr.apply_vector_displacement(ugo.mulk_tensor, loss_anam)
    displacement_norm = np.linalg.norm(displaced_mulk - mulk)
    print(f"  Resulting Zulm (Vector Displacement): {displacement_norm:.4f}")

    if displacement_norm > 1.0:
        print(">> DIAGNOSTIC: CRITICAL FAILURE. Extraction yielded mostly Pulp (Waste).")

    # Scenario 2: The Sovereign Agent
    # Possesses full attributes. Filter succeeds.
    print("\n[Scenario 2: Sovereign Agent (Strong Filter)]")
    loss_sov = asr.calculate_khusr_loss(1.0, 1.0, 1.0, 1.0)
    print(f"  Calculated Khusr (Waste/Pulp): {loss_sov:.4f}")

    displaced_mulk_sov = asr.apply_vector_displacement(ugo.mulk_tensor, loss_sov)
    displacement_norm_sov = np.linalg.norm(displaced_mulk_sov - mulk)
    print(f"  Resulting Zulm (Vector Displacement): {displacement_norm_sov:.4f}")

    if displacement_norm_sov < 0.1:
        print(">> DIAGNOSTIC: SUCCESS. Pure Juice (Truth) extracted.")

    print("\n[OQM-IHCEI PHYSICS VERDICT]")
    print("The simulation confirms that without the Success Filter (4 Conditions),")
    print("the 'Asr' pressing force results in Khusr (Waste), displacing the Mulk Tensor.")

if __name__ == "__main__":
    run_asr_stress_test()
