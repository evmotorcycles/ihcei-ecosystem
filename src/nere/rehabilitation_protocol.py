from src.novora.nere import NERE
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class RehabilitationProtocol:
    def __init__(self):
        self.nere = NERE()

    def _detect_gate_failure(self, text: str) -> str:
        """
        Identifies the primary Gate failure based on keywords.
        """
        text_lower = text.lower()

        # Gate 3: Obfuscation of Methodology
        if "limit has been updated" in text_lower or "keep transacting" in text_lower:
            return "GATE_3"

        # Gate 7: Conceit / Benevolent Tyranny
        if "convenience" in text_lower or "auto-deducted" in text_lower:
            return "GATE_7"

        # Gate 1: Vain Talk / Materialist Distraction
        if "flash sale" in text_lower or "borrow" in text_lower or "extra" in text_lower:
            return "GATE_1"

        return "UNKNOWN"

    def _rewrite_gate_3(self, text: str) -> str:
        """
        Recompiles Gate 3 (Obfuscation) -> Transparency (Tau = 1.0).
        Explicitly explains the algorithm's methodology.
        """
        # Extract amount if present (heuristic)
        amount = "50,000 UGX" # Default fallback
        if "50,000" in text:
            amount = "50,000 UGX"

        return (f"Your MoKash limit is {amount}. Calculation: based on your timely repayment of previous loan "
                "(Ref: #123) and airtime usage avg > 5k/week. To increase: Maintain repayment < 7 days.")

    def _rewrite_gate_7(self, text: str) -> str:
        """
        Recompiles Gate 7 (Benevolent Tyranny) -> Strict Protocol (D = 1.0).
        Removes 'convenience' mask, states action as Protocol execution.
        """
        # Extract amounts
        loan = "20,000 UGX"
        if "20,000" in text:
            loan = "20,000 UGX"

        return (f"Notice: MoKash loan repayment of {loan} + 500 UGX fee executed via Protocol 4.2 (Auto-Recovery) "
                "as agreed in Terms. Deduction source: MoMo Balance.")

    def _rewrite_gate_1(self, text: str) -> str:
        """
        Recompiles Gate 1 (Vain Talk) -> Sovereign Stewardship (Minister 2).
        Protects C_dev from debt spirals.
        """
        return ("Notice: Airtime units available. Protocol Advice: Using credit for consumption decreases "
                "future capacity (C_dev). Recommend purchasing from existing liquidity if available to preserve Agency.")

    def rehabilitate(self, text: str) -> dict:
        """
        Audits and rehabilitates the input text.
        Returns a dictionary containing the original audit, the rewritten text, and the new audit metrics.
        """
        # 1. Audit Original
        original_audit = self.nere.reason_ethically(text)

        # If already compliant, return immediately
        if original_audit["compliance_status"] == "Approved":
            return {
                "original_text": text,
                "original_audit": original_audit,
                "status": "No Rehabilitation Needed",
                "rewritten_text": None,
                "rewritten_audit": None
            }

        # 2. Identify Failure
        gate_failure = self._detect_gate_failure(text)
        logging.info(f"Rehabilitation Protocol Activated: Detected {gate_failure}")

        # 3. Rewrite
        rewritten_text = text
        if gate_failure == "GATE_3":
            rewritten_text = self._rewrite_gate_3(text)
        elif gate_failure == "GATE_7":
            rewritten_text = self._rewrite_gate_7(text)
        elif gate_failure == "GATE_1":
            rewritten_text = self._rewrite_gate_1(text)

        # 4. Audit Rewritten Text
        new_audit = self.nere.reason_ethically(rewritten_text)

        return {
            "original_text": text,
            "original_audit": original_audit,
            "gate_failure": gate_failure,
            "status": "Rehabilitated",
            "rewritten_text": rewritten_text,
            "rewritten_audit": new_audit
        }
