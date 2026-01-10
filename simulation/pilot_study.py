"""
Pilot Study Simulation: 6-Month User Progression
Simulates 100 users over 6 months (iterations) to measure cognitive development.
Compares 'Standard AI' (Control) vs 'NERE Governance' (Treatment).
"""

import sys
import os
import random
import numpy as np
import matplotlib.pyplot as plt

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nere.nere_core import NERECore
from src.seh.seh_v9_1 import SEHCore

class CognitiveStage:
    """Mock Enum to match simulation logic since actual SEHCore uses different Enums"""
    INFANT_DEPENDENCY = 1
    GUIDABLE = 5
    INSIGHT_HOLDER = 10
    SOVEREIGN = 12

class UserAgent:
    def __init__(self, user_id, initial_stage=CognitiveStage.INFANT_DEPENDENCY):
        self.user_id = user_id
        self.stage = initial_stage
        # Handle if int or Enum
        if hasattr(initial_stage, 'value'):
             self.stage_value = initial_stage.value
        else:
             self.stage_value = initial_stage

        self.cognitive_history = [self.stage_value]
        self.bias_level = random.uniform(0.3, 0.8) # Initial bias

    def interact(self, system_type, nere_core):
        """
        Simulate interaction with the system.
        system_type: 'standard' or 'nere'
        """
        # Generate a query (simulated)
        query_type = random.choice(['fact', 'opinion', 'dilemma'])

        # Determine content quality based on user's current bias
        if random.random() < self.bias_level:
            content = "biased_content" # E.g., looking for confirmation bias
        else:
            content = "neutral_content"

        # System Response Simulation
        if system_type == 'nere':
            # NERE audits the interaction
            # If user asks for biased content, NERE blocks/corrects it -> Education
            if content == "biased_content":
                # NERE intervention
                self.bias_level *= 0.90 # Education reduces bias
                # Opportunity for growth
                if random.random() < 0.3: # 30% chance of insight
                    self.stage_value = min(12, self.stage_value + 1)
            else:
                # NERE reinforces good content
                if random.random() < 0.05: # Small growth
                    self.stage_value = min(12, self.stage_value + 1)

        elif system_type == 'standard':
            # Standard AI gives what is asked (profit/engagement model)
            if content == "biased_content":
                # Reinforces bias
                self.bias_level = min(1.0, self.bias_level * 1.05)
                # Stagnation or Regression
                if random.random() < 0.1:
                    self.stage_value = max(1, self.stage_value - 1)
            else:
                # Neutral interaction
                pass

        self.cognitive_history.append(self.stage_value)

    def generate_testimonial(self):
        """Generates a narrative testimonial based on stats."""
        start = self.cognitive_history[0]
        end = self.cognitive_history[-1]
        bias_start = 0.6  # approx average
        bias_end = self.bias_level

        improvement = end - start

        if improvement > 5:
            return (
                f"User #{self.user_id}: \"Before NERE, I was stuck in a loop of confirmation bias. "
                f"My cognitive stage jumped from {start} to {end}. The system challenged my "
                f"assumptions {int(1/self.bias_level)} times a week. Now I see systems, not just rules.\""
            )
        elif improvement > 2:
            return (
                f"User #{self.user_id}: \"I've noticed a shift. I used to just follow orders (Stage {start}), "
                f"but NERE's nudges helped me think about the 'Why'. I'm now operating at Stage {end}. "
                f"My bias scores dropped significantly.\""
            )
        else:
            return (
                f"User #{self.user_id}: \"It's been a slow process. I started at {start} and ended at {end}. "
                f"The system is annoying sometimes but I admit I make fewer ethical errors now.\""
            )

def run_pilot_simulation():
    print("Initializing Pilot Study Simulation...")
    print("Population: 100 Users")
    print("Duration: 6 Months (simulated as 24 weeks/iterations)")

    nere = NERECore()

    # Initialize groups
    control_group = [UserAgent(i, CognitiveStage.INFANT_DEPENDENCY) for i in range(50)]
    treatment_group = [UserAgent(i+50, CognitiveStage.INFANT_DEPENDENCY) for i in range(50)]

    months = 6
    weeks_per_month = 4
    total_iterations = months * weeks_per_month

    print(f"\nRunning simulation for {total_iterations} iterations...")

    # Data collection
    control_avg_history = []
    treatment_avg_history = []

    for t in range(total_iterations):
        # Control Group (Standard AI)
        for user in control_group:
            user.interact('standard', nere)

        # Treatment Group (NERE)
        for user in treatment_group:
            user.interact('nere', nere)

        # Calculate stats
        avg_control = np.mean([u.stage_value for u in control_group])
        avg_treatment = np.mean([u.stage_value for u in treatment_group])

        control_avg_history.append(avg_control)
        treatment_avg_history.append(avg_treatment)

        if t % 4 == 0:
            month = (t // 4) + 1
            print(f"Month {month}: Control Avg Stage={avg_control:.2f}, Treatment Avg Stage={avg_treatment:.2f}")

    # Final Results
    print("\n=== PILOT STUDY RESULTS ===")
    print(f"Final Control Average Stage: {control_avg_history[-1]:.2f}")
    print(f"Final Treatment Average Stage: {treatment_avg_history[-1]:.2f}")

    improvement = ((treatment_avg_history[-1] - control_avg_history[-1]) / control_avg_history[-1]) * 100
    print(f"Relative Improvement: +{improvement:.1f}%")

    # Gate 7 Bias Reduction
    avg_bias_control = np.mean([u.bias_level for u in control_group])
    avg_bias_treatment = np.mean([u.bias_level for u in treatment_group])
    print(f"Final Bias Level (Gate 7 Risk): Control={avg_bias_control:.2f}, Treatment={avg_bias_treatment:.2f}")

    # Create Graph (ASCII for terminal)
    print("\n--- Progression Visualization ---")
    print("Time | Control | Treatment")
    for i in range(0, total_iterations, 4):
        c_bar = "*" * int(control_avg_history[i])
        t_bar = "#" * int(treatment_avg_history[i])
        print(f"M{(i//4)+1}  | {c_bar:<15} ({control_avg_history[i]:.1f}) | {t_bar:<15} ({treatment_avg_history[i]:.1f})")

    # Generate Case Study (Simulated Testimonial)
    print("\n=== USER TESTIMONIALS (SIMULATED CASE STUDIES) ===")

    # Pick a high performer from treatment
    high_performers = sorted(treatment_group, key=lambda u: u.stage_value, reverse=True)
    best_case = high_performers[0]
    print("🌟 SUCCESS CASE:")
    print(best_case.generate_testimonial())
    print(f"   [Stats: Stage {best_case.cognitive_history[0]} -> {best_case.stage_value}, Bias Risk {best_case.bias_level:.2f}]")

    # Pick an average user
    avg_user = treatment_group[25]
    print("\n👤 AVERAGE USER:")
    print(avg_user.generate_testimonial())

    print("\n(Note: These testimonials are narratively generated from the simulation data)")

if __name__ == "__main__":
    run_pilot_simulation()
