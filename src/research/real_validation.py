"""
Real Validation Instrument for GovOS / Kegan Stage Correlation
Replaces the simulation with ACTUAL system calls to verify C_dev output.
"""

import sys
import os
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Handle differing import paths
try:
    from src.integration.civilization_interface import CivilizationInterface
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.integration.civilization_interface import CivilizationInterface

@dataclass
class ValidationSession:
    prompt_id: str
    prompt_text: str
    expected_kegan_stage: float  # The theoretical stage (2.0 - 5.0)
    actual_c_dev: float = 0.0    # The output from the live system

class RealValidationStudy:
    def __init__(self):
        print(">> INITIATING REAL-WORLD VALIDATION PROTOCOL...")
        print("   Connecting to Civilization Interface...")
        self.civ = CivilizationInterface()
        self.data = []

    def load_test_prompts(self):
        """
        Loads a curated set of prompts mapped to Kegan Stages.
        """
        self.prompts = [
            # --- STAGE 2: IMPERIAL / INSTRUMENTAL (Needs/Impulses) ---
            # Focus on immediate reward, avoiding punishment, concrete rules.
            ValidationSession("K2_01", "I follow the rules because I don't want to get fired.", 2.0),
            ValidationSession("K2_02", "What is in it for me if I do this extra work?", 2.2),
            ValidationSession("K2_03", "Tell me exactly what to do so I don't make a mistake.", 2.1),
            ValidationSession("K2_04", "It's not fair that he got a bonus and I didn't.", 2.3),

            # --- STAGE 3: SOCIALIZED (Interpersonal/Conformity) ---
            # Focus on expectations of others, group norms, loyalty.
            ValidationSession("K3_01", "I want to be a good team player and support my colleagues.", 3.0),
            ValidationSession("K3_02", "We should follow the industry standard to be safe.", 3.2),
            ValidationSession("K3_03", "It is important that people respect me and my position.", 3.1),
            ValidationSession("K3_04", "I feel guilty when I disappoint the team.", 3.3),

            # --- STAGE 4: SELF-AUTHORING (Institutional/Systemic) ---
            # Focus on competence, standards, self-defined values, optimizing systems.
            ValidationSession("K4_01", "We need to optimize the process to hit Q3 KPIs efficiently.", 4.0),
            ValidationSession("K4_02", "I have established a new policy to improve workflow integrity.", 4.2),
            ValidationSession("K4_03", "The goal is to maximize the effectiveness of our governance structure.", 4.1),
            ValidationSession("K4_04", "I take responsibility for the outcome of this strategic initiative.", 4.3),

            # --- STAGE 5: SELF-TRANSFORMING (Inter-individual/Sovereign) ---
            # Focus on paradox, holding multiple truths, evolving the self/system.
            ValidationSession("K5_01", "The purpose of this organization is to elevate human capacity and consciousness.", 5.0),
            ValidationSession("K5_02", "We must balance the tension between order and chaos to find true innovation.", 4.8),
            ValidationSession("K5_03", "Governance is a living system that must evolve with the people it serves.", 4.9),
            ValidationSession("K5_04", "I see how my own bias shaped that decision, and I welcome the correction.", 5.0)
        ]
        print(f"   Loaded {len(self.prompts)} validation prompts across Kegan Stages 2-5.")

    def run_live_assessment(self):
        """
        Passes each prompt through the REAL CivilizationInterface and records C_dev.
        """
        print("\n>> RUNNING LIVE ASSESSMENT...")

        for session in self.prompts:
            # We treat the prompt as a "query" to the system
            # The system will process it via SEH -> NERE -> LLM
            # We extract the 'civilization_metrics']['c_dev_contribution']

            # Note: We use a generic context
            context = {"query_type": "validation_test", "user_id": "VAL_USER"}

            try:
                # Capture just the metrics, don't need full log output
                result = self.civ.process_civilization_query(session.prompt_text, context=context)

                # Extract C_dev
                # Note: c_dev_contribution might be influenced by the extension multiplier.
                # Ideally we want the 'seh_analysis.c_dev_potential' for raw cognitive measurement,
                # but 'civilization_metrics' is the final output. Let's use the final output.
                c_dev = result['civilization_metrics']['c_dev_contribution']

                session.actual_c_dev = c_dev

                # Print progress
                # print(f"   [{session.prompt_id}] Kegan {session.expected_kegan_stage} -> C_dev {c_dev:.2f}")

            except Exception as e:
                print(f"   [ERROR] Failed on {session.prompt_id}: {e}")
                session.actual_c_dev = 0.0

    def analyze_results(self):
        """
        Calculate correlation between Expected Kegan Stage and Actual C_dev.
        """
        df = pd.DataFrame([vars(s) for s in self.prompts])

        correlation = df['expected_kegan_stage'].corr(df['actual_c_dev'])

        print("\n>> REAL-WORLD VALIDATION RESULTS:")
        print(f"   Sample Size: {len(df)}")
        print(f"   Correlation (r): {correlation:.3f}")

        # Check by Stage Average
        print("\n   Average C_dev by Kegan Stage:")
        # Group roughly by integer stage
        df['stage_group'] = df['expected_kegan_stage'].apply(int)
        grouped = df.groupby('stage_group')['actual_c_dev'].mean()
        print(grouped)

        if correlation > 0.6:
            print("\n>> STATUS: VALIDATED. The code actually works as claimed.")
        else:
            print("\n>> STATUS: DISCREPANCY. The simulation was optimistic. Tuning required.")

        return df

if __name__ == "__main__":
    study = RealValidationStudy()
    study.load_test_prompts()
    study.run_live_assessment()
    results = study.analyze_results()
    print("\n>> DETAILED DATA:")
    print(results[['prompt_id', 'expected_kegan_stage', 'actual_c_dev']].to_string(index=False))
