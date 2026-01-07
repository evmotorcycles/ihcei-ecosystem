"""
Demo: SEH v9.1 in the Real World (Finance)
Simulates auditing financial products using the Sovereign Ethical Hub logic.
"""

import sys
import os
import json

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extensions.ihcei_finance_ci_ei import FinanceExtension

def print_audit(title, report):
    print(f"\n{'='*60}")
    print(f"📄 {title}")
    print(f"{'='*60}")
    print(f"Transaction ID: {report['transaction_id']}")
    print(f"Type:           {report['type']}")
    print(f"Decision:       {report['final_decision']}")
    print(f"Explanation:    {report['explanation']}")
    print(f"{'-'*60}")
    print("📊 Metrics:")
    print(f"  • Unification Balance: {report['adge_metrics']['unification_balance']:.4f}")
    print(f"  • Ricci Scalar (Stability): {report['adge_metrics']['systemic_stability']:.4f}")
    print(f"  • Riba Risk: {report['nere_audit']['riba_risk']:.4f}")
    print(f"  • Shirk Risk: {report['nere_audit']['shirk_risk']:.4f}")
    print(f"{'='*60}\n")

def run_demo():
    print("🚀 Starting SEH v9.1 Real World Demo: Finance Audit")

    auditor = FinanceExtension()

    # Scenario 1: Predatory Loan
    # High interest, hidden fees (low transparency), legal but unethical
    predatory_loan = {
        "transaction_id": "TX-9981",
        "type": "High-Interest Personal Loan",
        "transparency_score": 0.3, # Hidden terms
        "interest_rate": 0.25,     # 25% APR (Riba)
        "is_asset_backed": False,  # Fiat creation
        "regulatory_compliance": 0.9 # It's legal! (High Governance)
    }

    report1 = auditor.audit_transaction(predatory_loan)
    print_audit("Scenario A: Predatory Lending", report1)

    # Scenario 2: Ethical Partnership (Musharakah)
    # Profit sharing, transparent, asset backed
    ethical_partnership = {
        "transaction_id": "TX-7721",
        "type": "Housing Co-ownership (Musharakah)",
        "transparency_score": 0.9, # Full disclosure
        "interest_rate": 0.0,      # No Riba
        "is_asset_backed": True,   # Real Estate
        "regulatory_compliance": 0.9 # Legal
    }

    report2 = auditor.audit_transaction(ethical_partnership)
    print_audit("Scenario B: Ethical Partnership", report2)

if __name__ == "__main__":
    run_demo()
