#!/usr/bin/env python3
import sys
from src.core.adge import ADGE
from src.core.nere import NERE

def verify_deployment():
    print("Initiating Deployment Verification...")
    print("Auditing ADGE Physics Engine and NERE Kernel logic for paradigm alignment.")

    # 1. Verify ADGE (Apparition Dynamics Governance Engine)
    adge = ADGE()
    print("\n[ADGE Audit]")
    # Test case: High coherence and alignment should yield high C_dev (Cognitive Resonance)
    metrics_high = adge.calculate_metrics(coherence_level=0.95, intention_alignment=0.95)
    c_dev_high = metrics_high['c_dev']
    print(f"High Alignment Input -> C_dev: {c_dev_high:.4f}, Ricci Scalar: {metrics_high['ricci_scalar']:.4f}")

    if c_dev_high < 0.8:
        print("FAIL: ADGE failing to reward high coherence/alignment.")
        return False

    # Test case: Low coherence should yield low C_dev
    metrics_low = adge.calculate_metrics(coherence_level=0.2, intention_alignment=0.9)
    c_dev_low = metrics_low['c_dev']
    print(f"Low Coherence Input  -> C_dev: {c_dev_low:.4f}, Ricci Scalar: {metrics_low['ricci_scalar']:.4f}")

    if c_dev_low > 0.3:
        print("FAIL: ADGE failing to reflect low coherence.")
        return False

    print("PASS: ADGE Logic aligns with Cognitive Resonance principles.")

    # 2. Verify NERE (Neural Ethical Reasoning Engine)
    nere = NERE()
    print("\n[NERE Audit]")

    # Check Shirk Detection (Corruption/Lack of Transparency)
    # Low transparency should trigger Shirk alert
    shirk_vector = {'transparency': 0.1, 'fairness': 0.9, 'utility': 0.8}
    shirk_audit = nere.audit_decision(shirk_vector)
    print(f"Shirk Vector Audit -> Shirk Level: {shirk_audit['shirk_level']:.4f}, Compliant: {shirk_audit['is_compliant']}")

    if shirk_audit['is_compliant'] or shirk_audit['shirk_level'] < 0.8:
        print("FAIL: NERE failed to detect high Shirk (Corruption).")
        return False

    # Check Riba Detection (Imbalance/Exploitation)
    # High utility but low fairness should trigger Riba alert
    riba_vector = {'transparency': 0.9, 'fairness': 0.05, 'utility': 0.95}
    riba_audit = nere.audit_decision(riba_vector)
    print(f"Riba Vector Audit  -> Riba Level: {riba_audit['riba_level']:.4f}, Compliant: {riba_audit['is_compliant']}")

    if riba_audit['is_compliant'] or riba_audit['riba_level'] < 0.5:
        print("FAIL: NERE failed to detect high Riba (Imbalance).")
        return False

    print("PASS: NERE Logic aligns with Ethical Intelligence principles.")

    print("\nDeployment Verification SUCCESS: System is Paradigm Aligned.")
    return True

if __name__ == "__main__":
    success = verify_deployment()
    sys.exit(0 if success else 1)
