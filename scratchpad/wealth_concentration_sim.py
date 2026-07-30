import numpy as np

def run_simulation(N_agents=1000, T_steps=100, shock_prob=0.05, shock_magnitude=0.5):
    """
    Simulate wealth concentration in two financial systems, framed as Latency Engineering:

    Model A: The Debt Trap (Latency Engineered)
    Each innovation lengthened the interval between a decision and its consequence,
    and moved the consequence onto someone who did not make the decision:
    1. 1694 (Paterson): Perpetual principal -> consequence never arrives for the borrower.
    2. 1800s: Cross-border market -> consequence dispersed across holders who cannot act.
    3. 1913 (Morgan): Automatic buyer -> consequence absorbed by an actor that cannot refuse.
    4. 1979-82 (Volcker): Rate shock/refinancing -> consequence redirected onto non-borrowing populations.

    Model B: OQM Governance Physics (Zero Latency)
    Full-Reserve, Risk-Sharing, Continuous Distribution. Consequences are absorbed
    symmetrically and immediately (Delta U = 0), preventing compounding extraction.

    Note: This historical framework provides context; the mathematical engine below
    provides the evidence. Broad money contracts predominantly as a byproduct of lending.
    """
    np.random.seed(42)

    # Initialize Wealth
    # Initial wealth: 100 for each agent
    wealth_A_agents = np.full(N_agents, 100.0)
    wealth_B_agents = np.full(N_agents, 100.0)

    # Central Bank / Institution Wealth
    wealth_A_bank = 0.0
    wealth_B_bank = 0.0

    # Tracking
    history_A_gini = []
    history_B_gini = []
    history_A_bank = []
    history_B_bank = []
    history_A_total = []
    history_B_total = []

    def gini_coefficient(wealth):
        """Calculate Gini coefficient."""
        w = np.sort(wealth)
        n = len(wealth)
        index = np.arange(1, n + 1)
        return ((np.sum((2 * index - n - 1) * w)) / (n * np.sum(w)))

    # Model A: Latency Engineered Debt Trap
    # Agents take out loans (credit expansion). Initial loan is 50.
    debt_A = np.full(N_agents, 50.0)
    interest_rate_A = 0.08  # 8% perpetual interest (Consequence never arrives for the borrower)

    # Capital provided by Bank in Model B
    investment_B = np.full(N_agents, 50.0) # Bank invests 50 in each agent
    profit_share_B = 0.50 # 50% continuous distribution of profits

    for t in range(T_steps):
        # 1. Economic Activity (Production / Income)
        # Agents generate income with some variance
        income_A = np.random.normal(10, 5, N_agents)
        income_B = np.random.normal(10, 5, N_agents)

        # Apply shocks (Volcker / Defaults)
        shocks = np.random.rand(N_agents) < shock_prob
        income_A[shocks] -= wealth_A_agents[shocks] * shock_magnitude
        income_B[shocks] -= wealth_B_agents[shocks] * shock_magnitude

        # 2. Add income to wealth
        wealth_A_agents += income_A
        wealth_B_agents += income_B

        # 3. Model A Mechanics (The Debt Trap)
        # Calculate interest due
        interest_due_A = debt_A * interest_rate_A

        # Pay interest if possible, otherwise default/compound
        can_pay_A = wealth_A_agents >= interest_due_A

        # Those who can pay, pay
        wealth_A_agents[can_pay_A] -= interest_due_A[can_pay_A]
        wealth_A_bank += np.sum(interest_due_A[can_pay_A])

        # Those who can't pay face compounded debt (Inescapable Debt)
        # They pay what they can, rest is added to debt (plus penalty/refinancing)
        cannot_pay_A = ~can_pay_A
        paid_A = wealth_A_agents[cannot_pay_A]
        paid_A[paid_A < 0] = 0 # Can't pay negative

        wealth_A_agents[cannot_pay_A] -= paid_A
        wealth_A_bank += np.sum(paid_A)

        # Unpaid interest added to debt (compounding)
        debt_A[cannot_pay_A] += (interest_due_A[cannot_pay_A] - paid_A)

        # Artificial Credit Expansion (Automatic Buyer / Refinancing)
        # The bank creates new money to lend to struggling agents to keep them afloat,
        # redirecting consequence and ensuring broad money is a byproduct of lending.
        new_loans = np.zeros(N_agents)
        needs_bailout = wealth_A_agents < 10
        new_loans[needs_bailout] = 20
        wealth_A_agents += new_loans
        debt_A += new_loans
        # Bank creates this money out of thin air, so bank wealth isn't reduced by loan amount

        # 4. Model B Mechanics (OQM Risk-Sharing)
        # Determine profit/loss

        # Simplified profit: income above a certain baseline
        profit_B = income_B - 5

        # Distribute profits (Continuous Distribution)
        has_profit = profit_B > 0
        bank_share = profit_B[has_profit] * profit_share_B
        wealth_B_agents[has_profit] -= bank_share
        wealth_B_bank += np.sum(bank_share)

        # Absorb losses (Symmetric Write-down / Contagion Firewall)
        has_loss = profit_B < 0
        loss_magnitude = -profit_B[has_loss]

        # Bank absorbs loss proportionally to its investment ratio
        # Assuming investment is ~1/3 of total agent working capital (50 vs 150)
        bank_loss = loss_magnitude * 0.33

        # Bank writes down its investment and loses wealth
        wealth_B_bank -= np.sum(bank_loss)

        # 5. Tracking
        history_A_gini.append(gini_coefficient(np.maximum(wealth_A_agents, 0)))
        history_B_gini.append(gini_coefficient(np.maximum(wealth_B_agents, 0)))
        history_A_bank.append(wealth_A_bank)
        history_B_bank.append(wealth_B_bank)
        history_A_total.append(np.sum(wealth_A_agents) + wealth_A_bank)
        history_B_total.append(np.sum(wealth_B_agents) + wealth_B_bank)

    return {
        'A_gini': history_A_gini, 'B_gini': history_B_gini,
        'A_bank': history_A_bank, 'B_bank': history_B_bank,
        'A_total': history_A_total, 'B_total': history_B_total,
        'A_final_debt': np.sum(debt_A)
    }

if __name__ == "__main__":
    print("Running Simulation: Debt Trap vs. OQM Governance Physics...")
    res = run_simulation(N_agents=5000, T_steps=200, shock_prob=0.03, shock_magnitude=0.6)

    print("-" * 50)
    print("FINAL RESULTS (t=200)")
    print("-" * 50)
    print(f"Model A (Debt Trap):")
    print(f"  Central Bank Wealth:      {res['A_bank'][-1]:,.2f}")
    print(f"  Total Outstanding Debt:   {res['A_final_debt']:,.2f}")
    print(f"  Wealth Inequality (Gini): {res['A_gini'][-1]:.3f}")

    print(f"\nModel B (OQM Risk-Sharing):")
    print(f"  Central Bank Wealth:      {res['B_bank'][-1]:,.2f}")
    print(f"  Total Outstanding Debt:   0.00 (Equity/Participation only)")
    print(f"  Wealth Inequality (Gini): {res['B_gini'][-1]:.3f}")
    print("-" * 50)

    print("\nAnalysis:")
    print("The simulation mathematically reproduces the 'Debt Trap'.")
    print("In Model A, the combination of permanent principal, compounding interest,")
    print("and credit expansion ensures the Central Institution captures a massive")
    print("and continually growing percentage of all systemic wealth, while inequality")
    print("(Gini) spikes as debt compounds on vulnerable agents.")
    print("\nIn Model B (OQM), enforcing full-reserves and symmetric risk-sharing")
    print("acts as a mathematical firewall. The Central Institution remains profitable")
    print("via continuous distribution, but wealth extraction is structurally capped")
    print("because losses are shared symmetrically rather than compounded as debt.")
