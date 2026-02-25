from src.core.ihcei_2 import IHCEI2
from src.core.ihcei_core import IHCEICore
import logging

class NERE:
    def __init__(self):
        self.ihcei_2 = IHCEI2()
        self.core = IHCEICore()

    def reason_ethically(self, policy: str, g_ij_zakat_flow: float = 0.5) -> dict:
        logging.info(f"NERE Cognitive Mirror active for policy: {policy}")

        # Step 1: Press the Academic/Worldly Policy into Al-Haqq
        pressed_data = self.core.press_academic_data(policy)

        # Step 2: Evaluate Agency Delta (ΔA)
        # Does this policy hoard cognitive sovereignty or distribute it?
        # Check for trigger words; if absent, assume +1
        # Gate 3: Obfuscation of Methodology (subprime, bundle, adjustable, no verification)
        toxic_keywords = [
            "mandate", "restrict", "force", "subprime", "no verification",
            "adjustable", "bundle", "interest",
            "limit has been updated", "keep transacting", # Gate 3 (Transparency Failure)
            "convenience", "auto-deducted", # Gate 7 (Tyranny)
            "flash sale", "borrow", "extra" # Gate 1 (Vain Talk)
        ]
        agency_delta = -1 if any(word in policy.lower() for word in toxic_keywords) else +1

        # Step 3: Calculate ADGE trajectory
        adge_metrics = self.ihcei_2.calculate_adge_trajectory(policy, g_ij_zakat_flow=g_ij_zakat_flow)

        # Compliance requires positive agency distribution and manageable noise
        is_compliant = agency_delta > 0 and adge_metrics["h_network_noise"] < 0.6

        response = {
            "policy": policy,
            "extracted_haqq": pressed_data["al_haqq_output"],
            "agency_delta": "Positive (Sovereignty Enhancing)" if agency_delta > 0 else "RED: Negative (Hoarding/Pharaoh Filter)",
            "bias_noise_hbar": round(adge_metrics["h_network_noise"], 3),
            "c_dev_coefficient": round(adge_metrics["c_dev_coefficient"], 3),
            "compliance_status": "Approved" if is_compliant else "Rejected - Triggers Gate 7 (Conceit) or Gate 2 (Groupthink)"
        }

        logging.info(f"NERE Verdict: {response['compliance_status']}")
        return response
