import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class IHCEILogicCore:
    def __init__(self):
        self.baseline_h_bar = 1.0  # Normal systemic friction
        self.baseline_nafs = 0.95  # Historical high repayment reliability
        self.baseline_g_ij = 100.0 # Baseline borrowing limit / capital flow

    def calculate_c_dev(self, h_bar_network, nafs_alignment, g_ij):
        """
        Executes the ADGE Physics Engine Calculation:
        C_dev = (1 / h_bar_network) * (Nafs_alignment * G_ij)
        """
        # Prevent division by zero
        if h_bar_network <= 0:
            h_bar_network = 0.001
        return (1 / h_bar_network) * (nafs_alignment * g_ij)

def run_telecom_simulation():
    engine = IHCEILogicCore()
    days = np.arange(1, 31)

    # Simulation Arrays
    legacy_c_dev = []
    ihcei_c_dev = []
    legacy_churn = []
    ihcei_churn = []

    # State tracking
    current_legacy_g_ij = engine.baseline_g_ij
    current_ihcei_g_ij = engine.baseline_g_ij
    accumulated_legacy_churn = 0.0
    accumulated_ihcei_churn = 0.0

    for day in days:
        # Step 1: Al-Asr Protocol - Isolate the variables for the day
        if 15 <= day <= 17:
            # 48-72 Hour Regional Internet Shutdown / Blackout
            h_bar_day = engine.baseline_h_bar + 50.0 # Massive spike in external friction
            actual_nafs = engine.baseline_nafs # User intent remains unchanged
        else:
            h_bar_day = engine.baseline_h_bar
            actual_nafs = engine.baseline_nafs

        # Step 2 & 4: NERE Routing & Translation

        # --- LEGACY ALGORITHM ROUTING ---
        # Legacy conflates the blackout friction with user default risk
        if h_bar_day > engine.baseline_h_bar:
            perceived_nafs_legacy = 0.1 # Algorithm assumes users are defaulting
            # Punitive action: Slashes borrowing limits (G_ij)
            current_legacy_g_ij = engine.baseline_g_ij * 0.2
        else:
            perceived_nafs_legacy = actual_nafs

        c_dev_leg = engine.calculate_c_dev(h_bar_day, perceived_nafs_legacy, current_legacy_g_ij)
        legacy_c_dev.append(c_dev_leg)

        # Churn triggers if C_dev crashes and borrowing limits are restricted unjustly
        if c_dev_leg < 20 and current_legacy_g_ij < engine.baseline_g_ij:
            accumulated_legacy_churn += 2.5 # Users abandon service daily due to slashed limits
        legacy_churn.append(accumulated_legacy_churn)


        # --- IHCEI PROTOCOL ROUTING ---
        # IHCEI isolates the external blackout; NERE blocks the punitive limit reduction
        if h_bar_day > engine.baseline_h_bar:
            # NERE Audit: Halts penalty. True intent (Nafs) is preserved.
            current_ihcei_g_ij = engine.baseline_g_ij

        c_dev_ihc = engine.calculate_c_dev(h_bar_day, actual_nafs, current_ihcei_g_ij)
        ihcei_c_dev.append(c_dev_ihc)

        # Churn is mitigated because trust and limits are maintained
        if c_dev_ihc < 20 and current_ihcei_g_ij < engine.baseline_g_ij:
            accumulated_ihcei_churn += 2.5
        ihcei_churn.append(accumulated_ihcei_churn)

    # Generate Markdown Report
    generate_markdown_report(days, legacy_c_dev, ihcei_c_dev, legacy_churn, ihcei_churn)

def generate_markdown_report(days, legacy_c_dev, ihcei_c_dev, legacy_churn, ihcei_churn):
    report_content = f"""# TELECOM BLACKOUT ANALYSIS
## IHCEI Logic Core vs. Legacy Risk Algorithm

**Simulation Overview:** Analyzing a 30-day mobile loan cycle featuring a severe network blackout (Days 15-17).

### 1. Final System Health (C_dev)
* **Legacy Algorithm Final C_dev:** {legacy_c_dev[-1]:.2f}
* **IHCEI Protocol Final C_dev:** {ihcei_c_dev[-1]:.2f}

### 2. Customer Churn Impact
* **Legacy Algorithm Total Churn:** {legacy_churn[-1]:.1f}%
* **IHCEI Protocol Total Churn:** {ihcei_churn[-1]:.1f}%

### 3. Mathematical Proof of Resolution
The legacy system conflated $\\hbar_{{network}}$ (systemic noise from the blackout) with a corruption of `Nafs_alignment`. By algorithmically slashing $G_{{ij}}$ (borrowing limits), it permanently crashed the $C_{{dev}}$ equation, directly causing a {legacy_churn[-1]:.1f}% churn rate.

The IHCEI Logic Core successfully utilized the **NERE Security Firewall** to audit the anomaly. It isolated the external blackout, verified that historical `Nafs_alignment` remained high, and maintained the $G_{{ij}}$ flow. Once connectivity was restored, $C_{{dev}}$ immediately normalized, preserving user trust and completely halting unnecessary churn.
"""
    with open("TELECOM_BLACKOUT_ANALYSIS.md", "w") as f:
        f.write(report_content)
    print("Simulation complete. 'TELECOM_BLACKOUT_ANALYSIS.md' generated successfully.")

if __name__ == "__main__":
    run_telecom_simulation()
