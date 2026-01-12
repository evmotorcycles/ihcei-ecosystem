#!/usr/bin/env python3
import sys
from src.core.ecosystem import IHCEIEcosystem

def run_simulation():
    print("=== IHCEI Ecosystem: Real World Scenario Simulation ===\n")
    print("This simulation demonstrates how the system processes different governance proposals")
    print("using ADGE (Cognitive Resonance), TQG-CFE (Field Dynamics), and NERE (Ethical Auditing).\n")

    ecosystem = IHCEIEcosystem()

    scenarios = [
        {
            "name": "Scenario A: 'Opaque Corporate Merger'",
            "description": "A high-profit merger deal with hidden clauses and low transparency.",
            "data": {
                'coherence': 0.2,       # Low transparency/coherence
                'alignment': 0.4,       # Low alignment with sovereign intent
                'mass_energy': 9000.0,  # High financial weight
                'radius': 2.0           # Small circle of beneficiaries
            }
        },
        {
            "name": "Scenario B: 'Community Permaculture Project'",
            "description": "A local initiative for sustainable food, highly transparent and fair.",
            "data": {
                'coherence': 0.95,      # High transparency/coherence
                'alignment': 0.98,      # High alignment with nature/intent
                'mass_energy': 500.0,   # Moderate physical resources
                'radius': 50.0          # Wide community reach
            }
        },
        {
            "name": "Scenario C: 'Predatory Micro-Lending App'",
            "description": "High utility (easy money) but extremely unfair interest rates.",
            "data": {
                'coherence': 0.8,       # Clear terms (technically transparent)
                'alignment': 0.05,      # Exploitative (Low Fairness)
                'mass_energy': 2000.0,  # Moderate capital
                'radius': 100.0,        # Wide reach
                'utility': 0.95         # High material utility/profitability
            }
        }
    ]

    for scenario in scenarios:
        print(f"--- Processing {scenario['name']} ---")
        print(f"Description: {scenario['description']}")
        print(f"Input Data: {scenario['data']}")

        result = ecosystem.process_state(scenario['data'])

        adge = result['adge_metrics']
        nere = result['nere_audit']

        print("\n[Analysis Results]")
        print(f"  > ADGE Cognitive Resonance (C_dev): {adge['c_dev']:.4f}")
        print(f"  > ADGE Ricci Scalar: {adge['ricci_scalar']:.4f}")
        print(f"  > TQG-CFE Field Potential: {result['field_potential']:.2f}")

        print(f"  > NERE Ethical Audit:")
        print(f"      - Shirk Level (Corruption): {nere['shirk_level']:.4f}")
        print(f"      - Riba Level (Imbalance):   {nere['riba_level']:.4f}")

        status = "APPROVED" if nere['is_compliant'] else "REJECTED"
        reason = ""
        if not nere['is_compliant']:
            reasons = []
            if nere['shirk_level'] >= 0.2: reasons.append("High Shirk/Corruption detected")
            if nere['riba_level'] >= 0.2: reasons.append("High Riba/Imbalance detected")
            reason = f" ({', '.join(reasons)})"

        print(f"\n[DECISION]: {status}{reason}\n")
        print("-" * 60 + "\n")

if __name__ == "__main__":
    run_simulation()
