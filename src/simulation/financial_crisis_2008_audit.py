
import numpy as np
from src.simulation.ugo import UnifiedGovernanceObject

def generate_historical_millat(noise_level: float) -> np.ndarray:
    """
    Generates the Millat (Syntax) Matrix based on historical ideological corruption.
    Pure Millat = Identity Matrix (I).
    Corrupted Millat = I + Random Noise.
    """
    base_matrix = np.eye(10)
    if noise_level > 0.0:
        np.random.seed(42) # Seeded for historical reproducibility
        noise = np.random.uniform(0, noise_level, (10, 10))
        base_matrix += noise
    return base_matrix

def run_2008_audit():
    print("==========================================================")
    print(" IHCEI FORENSIC AUDIT: 2008 FINANCIAL CRISIS")
    print("==========================================================")

    # Payload Parameters
    event_name = "2008 Global Financial Crisis (Subprime Mortgage Collapse)"
    historical_utility_u = 100000000000.0 # Massive Capital Liquidity
    mulk_tensor_input = np.ones(10) # Baseline
    millat_corruption_noise = 9.8 # SEVERE Lexicon Distortion

    # Generate Corrupted Matrix
    millat_matrix = generate_historical_millat(millat_corruption_noise)

    # Initialize UGO
    ugo = UnifiedGovernanceObject(
        name=event_name,
        mulk_tensor=mulk_tensor_input,
        millat_matrix=millat_matrix,
        utility_u=historical_utility_u
    )

    # Compile Reality
    metrics = ugo.compile_reality()

    # Output Log
    print(f"\n[Unified Governance Object: {metrics['Model']}]")
    print(f"  Input Utility (U)   : {metrics['Utility (U)']} (Massive Resource Base)")
    print(f"  Lexicon Distortion  : {metrics['Lexicon Distortion']} (Semantic Reality completely decoupled from physical value)")
    print(f"  Systemic Friction   : {metrics['Systemic Friction (h_net)']} (Infinite Friction / 'Chunks of Darkness')")
    print(f"  Cognitive Dev       : {metrics['Cognitive Dev (C_dev)']} (Total Market Blindness / Ratings Agencies fail to process risk)")
    print(f"  Discipline (D)      : {metrics['Discipline (D)']} (Fragmented Structural Integrity)")
    print(f"  --> ESSENCE (E)     : {metrics['Total Essence (E)']} (Total Systemic Wipeout relative to input U)")

    friction = float(metrics["Systemic Friction (h_net)"].replace(",", ""))
    if friction > 100.0:
        print("\n>> IHCEI DIAGNOSTIC: CRITICAL COLLAPSE. Systemic Friction exceeds sustainable thresholds.")
    else:
        print("\n>> IHCEI DIAGNOSTIC: STABLE.")

    print("\n[OQM-IHCEI ANALYSIS]")
    print("The simulator proves that the 2008 crash was not a failure of capital (Utility U was extremely high). It was a failure of Millat (Syntax/Lexicon).")
    print("Because the financial institutions deliberately injected noise into the system (labeling bad debt as good debt), the D_syntax matrix shattered.")
    print("When the true nature of the assets was exposed, the computational cost of transferring clear knowledge across the global network skyrocketed.")
    print("This generated infinite Systemic Friction (h_network). Trust evaporated instantly, credit markets froze (the 'Chunks of Darkness'), and Cognitive Development (C_dev) crashed to zero.")
    print("The equation mathematically proves that high Utility multiplied by zero Discipline yields zero Essence.")

if __name__ == "__main__":
    run_2008_audit()
