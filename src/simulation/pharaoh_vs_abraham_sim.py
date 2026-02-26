
import numpy as np
from src.simulation.ugo import UnifiedGovernanceObject

def generate_millat_matrix(is_corrupted=False, noise_level=5.0):
    """
    Generates the 10x10 Millat syntax matrix.
    Pure Millat = Identity Matrix (I).
    Corrupted Millat = I + Random Noise representing lexical hijacking.
    """
    matrix = np.eye(10)
    if is_corrupted:
        np.random.seed(42) # Seeded for reproducible entropy
        noise = np.random.uniform(0, noise_level, (10, 10))
        matrix = matrix + noise
    return matrix

def run_simulation():
    print("==========================================================")
    print(" IHCEI SIMULATION: PHYISCS OF COLLAPSE (PHARAOH VS ABRAHAM)")
    print("==========================================================\n")

    # Baseline Mulk Tensor (10 Elements: Roles, Zakat, Authorities, etc. all perfectly aligned at 1.0)
    baseline_mulk = np.ones(10)

    # ---------------------------------------------------------
    # 1. The Abraham Model (High Discipline, Balanced Utility)
    # ---------------------------------------------------------
    abraham_millat = generate_millat_matrix(is_corrupted=False)
    abraham_ugo = UnifiedGovernanceObject(
        name="Abrahamic Governance (Pure Millat)",
        mulk_tensor=baseline_mulk,
        millat_matrix=abraham_millat,
        utility_u=1_000.0  # Sustainable, balanced resources
    )
    abraham_metrics = abraham_ugo.compile_reality()

    # ---------------------------------------------------------
    # 2. The Pharaoh Model (Zero Discipline, Infinite Utility)
    # ---------------------------------------------------------
    pharaoh_millat = generate_millat_matrix(is_corrupted=True, noise_level=8.0)
    pharaoh_ugo = UnifiedGovernanceObject(
        name="Pharaonic Dominion (Corrupted Lexicon/Qurayshite Bug)",
        mulk_tensor=baseline_mulk,
        millat_matrix=pharaoh_millat,
        utility_u=1_000_000_000.0  # Massive monumental resources / raw power
    )
    pharaoh_metrics = pharaoh_ugo.compile_reality()

    # --- Output formatting ---
    for metrics in [abraham_metrics, pharaoh_metrics]:
        print(f"[{metrics['Model']}]")
        print(f"  Input Utility (U)   : {metrics['Utility (U)']}")
        print(f"  Lexicon Distortion  : {metrics['Lexicon Distortion']}")
        print(f"  Systemic Friction   : {metrics['Systemic Friction (h_net)']} (Chunks of Darkness)")
        print(f"  Cognitive Dev       : {metrics['Cognitive Dev (C_dev)']}")
        print(f"  Discipline (D)      : {metrics['Discipline (D)']}")
        print(f"  --> ESSENCE (E)     : {metrics['Total Essence (E)']}\n")

if __name__ == "__main__":
    run_simulation()
