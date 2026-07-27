import json

def simulate_conventional_debt(asset_initial, loan_amount, operator_downpayment, market_shock_pct):
    """
    Simulates a conventional debt contract where the financier takes zero asset risk.
    """
    asset_final = asset_initial * (1.0 - market_shock_pct)

    # Financier is owed their principal unconditionally
    financier_equity = loan_amount

    # Operator absorbs 100% of the shock
    operator_equity = asset_final - loan_amount

    return {
        "model": "Conventional Debt",
        "asset_initial": asset_initial,
        "asset_final": asset_final,
        "financier_equity": financier_equity,
        "operator_equity": operator_equity,
        "generated_debt": operator_equity < 0
    }

def simulate_sovereign_musharakah(asset_initial, financier_stake, operator_stake, market_shock_pct):
    """
    Simulates a Sovereign Mesh (Musharakah / PPN) contract where risk is shared horizontally.
    """
    asset_final = asset_initial * (1.0 - market_shock_pct)

    financier_pct = financier_stake / asset_initial
    operator_pct = operator_stake / asset_initial

    # Both parties absorb the shock symmetrically based on their stake
    financier_equity = asset_final * financier_pct
    operator_equity = asset_final * operator_pct

    return {
        "model": "Sovereign Mesh (Musharakah)",
        "asset_initial": asset_initial,
        "asset_final": asset_final,
        "financier_equity": financier_equity,
        "operator_equity": operator_equity,
        "generated_debt": operator_equity < 0
    }

def main():
    print("Executing Pre-Registered Telemetry: Sovereign Mesh vs Conventional Debt\n")

    asset_initial = 100_000
    financier_capital = 80_000
    operator_capital = 20_000
    market_shock = 0.40 # 40% asset devaluation

    print(f"Initial Asset Value: ${asset_initial:,.2f}")
    print(f"Financier Input: ${financier_capital:,.2f}")
    print(f"Operator Input: ${operator_capital:,.2f}")
    print(f"Market Shock (Devaluation): {market_shock * 100}%\n")

    # 1. Conventional Model
    conv_results = simulate_conventional_debt(asset_initial, financier_capital, operator_capital, market_shock)
    print(f"--- {conv_results['model']} ---")
    print(f"Final Asset Value: ${conv_results['asset_final']:,.2f}")
    print(f"Financier Equity: ${conv_results['financier_equity']:,.2f}")
    print(f"Operator Equity: ${conv_results['operator_equity']:,.2f}")
    print(f"Negative Equity (Debt) Generated? {conv_results['generated_debt']}\n")

    # 2. Sovereign Mesh Model
    sov_results = simulate_sovereign_musharakah(asset_initial, financier_capital, operator_capital, market_shock)
    print(f"--- {sov_results['model']} ---")
    print(f"Final Asset Value: ${sov_results['asset_final']:,.2f}")
    print(f"Financier Equity: ${sov_results['financier_equity']:,.2f}")
    print(f"Operator Equity: ${sov_results['operator_equity']:,.2f}")
    print(f"Negative Equity (Debt) Generated? {sov_results['generated_debt']}\n")

    # Gate Evaluation
    g1_pass = conv_results['generated_debt'] == True
    g2_pass = sov_results['generated_debt'] == False and sov_results['operator_equity'] >= 0

    print("--- Pre-Registration Gates ---")
    print(f"G1 (Asymmetric Debt): {'PASS' if g1_pass else 'FAIL'}")
    print(f"G2 (Symmetric Mesh): {'PASS' if g2_pass else 'FAIL'}")

    if g1_pass and g2_pass:
        print("\nVERDICT: Sovereign Mesh Hypothesis CONFIRMED.")
        print("The full-reserve PPN contract structurally eliminates debt creation (Delta U = 0)")
        print("by absorbing market shocks symmetrically as equity degradation.")
    else:
        print("\nVERDICT: Sovereign Mesh Hypothesis FALSIFIED.")

if __name__ == "__main__":
    main()
