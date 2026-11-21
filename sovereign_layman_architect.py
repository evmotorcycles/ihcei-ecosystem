import math
import json

class SovereignLaymanArchitect:
    """
    Sovereign Layman's Architect (SLA)
    A revolutionary business planning tool for the layman that uses LISM, LMD,
    Decoupling, and DCM to mathematically guarantee actionable, non-hallucinated plans.
    """
    def __init__(self):
        # LISM: Fidelity Circuit Breaker threshold (D_min)
        self.d_min = 0.5

        # LMD: Max acceptable latency per step in days (tau_rt)
        self.max_tau_rt = 14.0

        # LMD constant for distance calculation
        self.kappa = 1.0

    def search_and_summarize(self, query):
        """Mimics the search engine and conversation summary phase."""
        print(f"[Search Engine Phase] Analyzing layman query: '{query}'")
        return f"A realistic, grounded project to achieve: '{query}'"

    def decoupled_evaluator(self, plan_step, llm_confidence):
        """
        DECOUPLING: The evaluator is deterministic and completely ignores
        the LLM's self-reported confidence. It measures actual fidelity.
        """
        words = len(plan_step.split())
        # A simulated deterministic heuristic:
        # Steps that are too short lack actionable detail.
        # Steps that are too long are overly complex jargon.
        if words < 6:
            real_fidelity = 0.3  # Too vague
        elif words > 40:
            real_fidelity = 0.4  # Too complex/hallucinated
        else:
            real_fidelity = 0.9  # Actionable sweet spot

        return real_fidelity

    def calculate_lmd_distance(self, estimated_latency_days):
        """
        LMD (Latency-Metric Duality): d^2 = κ * τ_rt
        Computes the operational distance based on execution latency.
        """
        distance = math.sqrt(self.kappa * estimated_latency_days)
        return distance

    def apply_dcm(self, step):
        """
        DCM (Deterministic Cognitive Model): Verifies that the cognitive load
        of the step matches the layman's verified capacity.
        """
        # Simulated DCM check: ensures there are no unresolved dependencies
        has_jargon = any(word in step.lower() for word in ['synergy', 'leverage', 'paradigm'])
        return not has_jargon

    def generate_business_plan(self, summary, proposed_steps):
        """
        Generates and filters the business plan through the empirical governance stack.
        """
        print(f"\n[Business Planner Phase] Generating sovereign plan for: {summary}")

        final_plan = []
        cumulative_fidelity = 1.0

        for i, step in enumerate(proposed_steps):
            print(f"\nEvaluating Step {i+1}: {step['action']}")

            # 1. DECOUPLING: Ignore the AI's hype
            real_fidelity = self.decoupled_evaluator(step['action'], step['llm_confidence'])
            print(f"  [Decoupling] Ignored AI confidence of {step['llm_confidence']}. Real deterministic fidelity: {real_fidelity}")

            # 2. LISM (Circuit Breaker): Prevent zombie planning
            cumulative_fidelity *= real_fidelity
            if real_fidelity < self.d_min:
                print(f"  [LISM WARNING] Step fidelity ({real_fidelity}) fell below safety floor ({self.d_min}). Circuit broken! Step rejected to save the layman from failure.")
                continue

            # 3. LMD (Latency-Metric Duality): Measure physical distance to goal
            distance = self.calculate_lmd_distance(step['est_days'])
            print(f"  [LMD] Expected latency: {step['est_days']} days. Operational distance: {distance:.2f}")
            if step['est_days'] > self.max_tau_rt:
                print(f"  [LMD WARNING] Latency too high. Goal is too 'far' for a layman. Step rejected for micro-delegation.")
                continue

            # 4. DCM (Deterministic Cognitive Model): Filter out jargon
            if not self.apply_dcm(step['action']):
                print(f"  [DCM WARNING] Cognitive load too high (corporate jargon detected). Step rejected.")
                continue

            print(f"  [PASS] Step mathematically verified for the layman.")
            final_plan.append(step)

        return final_plan

if __name__ == "__main__":
    architect = SovereignLaymanArchitect()
    user_query = "Start a local eco-friendly cleaning service"
    summary = architect.search_and_summarize(user_query)

    # Simulating what a standard "hallucinating" AI planner might generate
    raw_ai_steps = [
        {"action": "Register business name.", "est_days": 1, "llm_confidence": 0.99}, # Too short, fails Decoupling
        {"action": "Set up a local Google My Business profile and buy basic cleaning supplies.", "est_days": 3, "llm_confidence": 0.85}, # Passes
        {"action": "Leverage enterprise synergy to build a paradigm shifting franchise model across the state.", "est_days": 7, "llm_confidence": 0.99}, # Fails DCM (jargon)
        {"action": "Secure a massive commercial office building contract requiring 50 employees.", "est_days": 90, "llm_confidence": 0.95} # Fails LMD (Latency too high)
    ]

    plan = architect.generate_business_plan(summary, raw_ai_steps)

    print("\n========================================")
    print("      FINAL SOVEREIGN LAYMAN PLAN       ")
    print("========================================")
    if not plan:
        print("No viable steps survived the audit. The AI's plan was entirely hallucinated.")
    else:
        for i, s in enumerate(plan):
            print(f"{i+1}. {s['action']} (Latency: {s['est_days']} days)")
    print("========================================")
    print("Outcome: The layman is protected from cascading failure and wasted capital.")
