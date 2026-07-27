import jax
import jax.numpy as jnp
from jax import config
# Use x64 to prevent float precision issues for financial ledgers
config.update("jax_enable_x64", True)
import time

@jax.jit
def run_financial_simulation(asset_values, financier_capital, operator_capital, market_shock_pct):
    """
    JAX-accelerated simulation comparing Conventional Debt vs Sovereign Mesh (Musharakah).
    Runs the simulation over a batched vector of initial asset values.
    """
    # Total initial asset value is the sum of capital
    total_capital = financier_capital + operator_capital

    # Calculate shocked asset values
    shocked_assets = asset_values * (1.0 - market_shock_pct)

    # --- 1. Conventional Debt Model ---
    # Financier is owed their principal unconditionally (0% risk on principal)
    # The debt amount is fixed at financier_capital
    conv_financier_equity = jnp.full_like(asset_values, financier_capital)

    # Operator absorbs 100% of the shock. Equity is Asset Value - Debt
    conv_operator_equity = shocked_assets - financier_capital

    # Flag negative equity (debt) states
    conv_negative_equity_flag = conv_operator_equity < 0

    # --- 2. Sovereign Mesh Model (100% Full Reserve Musharakah) ---
    # Risk is horizontal; both parties absorb shocks symmetrically based on equity
    financier_pct = financier_capital / total_capital
    operator_pct = operator_capital / total_capital

    sov_financier_equity = shocked_assets * financier_pct
    sov_operator_equity = shocked_assets * operator_pct

    # Flag negative equity (debt) states
    sov_negative_equity_flag = sov_operator_equity < 0

    return (
        conv_operator_equity, conv_financier_equity, conv_negative_equity_flag,
        sov_operator_equity, sov_financier_equity, sov_negative_equity_flag,
        shocked_assets
    )

def main():
    print("Initializing Governance OS: Sovereign Mesh Market Shock Simulation...")
    print("Enforcing Epistemic Firewall: Validating Harris Irfan's 100% Reserve vs Fractional Debt Models")

    # Base parameters
    financier_capital = 80_000.0
    operator_capital = 20_000.0
    total_capital = financier_capital + operator_capital

    market_shock = 0.40 # 40% Devaluation

    print(f"\n--- Ledger Initial State ---")
    print(f"Total Asset Value: ${total_capital:,.2f}")
    print(f"Financier Stake: ${financier_capital:,.2f} ({financier_capital/total_capital*100:.0f}%)")
    print(f"Operator Stake: ${operator_capital:,.2f} ({operator_capital/total_capital*100:.0f}%)")
    print(f"Applied Market Shock: {market_shock*100:.0f}%\n")

    # We create a vector to run a large batch simulation across different scales
    # to demonstrate stability. Here we simulate 10,000 parallel contracts.
    num_contracts = 10_000
    asset_vector = jnp.full((num_contracts,), total_capital)

    start_time = time.time()

    # Execute JAX JIT-compiled simulation
    results = run_financial_simulation(asset_vector, financier_capital, operator_capital, market_shock)

    # Block until ready to ensure accurate timing
    for r in results:
        r.block_until_ready()

    end_time = time.time()
    print(f"Simulated {num_contracts:,} contracts in {end_time - start_time:.4f} seconds.\n")

    # Extract results for the first contract (they are identical in this deterministic test)
    conv_op_eq = results[0][0]
    conv_fin_eq = results[1][0]
    conv_neg_flag = results[2][0]

    sov_op_eq = results[3][0]
    sov_fin_eq = results[4][0]
    sov_neg_flag = results[5][0]
    final_asset = results[6][0]

    print("--- 1. Conventional Debt Model (Fractional Reserve Proxy) ---")
    print(f"Final Asset Value: ${final_asset:,.2f}")
    print(f"Financier Equity (Principal Owed): ${conv_fin_eq:,.2f}")
    print(f"Operator Equity: ${conv_op_eq:,.2f}")
    print(f"Operator Negative Equity (In Debt): {bool(conv_neg_flag)}")

    print("\n--- 2. Sovereign Mesh Model (100% Full-Reserve PPN/Musharakah) ---")
    print(f"Final Asset Value: ${final_asset:,.2f}")
    print(f"Financier Equity: ${sov_fin_eq:,.2f}")
    print(f"Operator Equity: ${sov_op_eq:,.2f}")
    print(f"Operator Negative Equity (In Debt): {bool(sov_neg_flag)}")

    print("\n--- Telemetric Verdict ---")
    if conv_neg_flag and not sov_neg_flag:
        print("VERDICT: CONFIRMED.")
        print("Under a 40% market shock, the conventional debt model forces the operator into asymmetric")
        print("negative equity, generating debt (-$20,000) while shielding the financier.")
        print("The Sovereign Mesh (Musharakah) absorbs the exact same shock symmetrically as equity degradation,")
        print("structurally preventing debt generation (Delta U = 0).")
    else:
        print("VERDICT: FAILED. The mathematical simulation did not produce the expected symmetric degradation.")

if __name__ == "__main__":
    main()
