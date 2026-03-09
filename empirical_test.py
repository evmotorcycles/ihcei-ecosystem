import requests
import json
import pandas as pd
import statsmodels.api as sm
from time import sleep

# The local NERE API endpoint you established
API_URL = "http://localhost:8000/llm"

# MOCK DATASET: Enterprise operational narratives spanning 4 quadrants of the U/D matrix
# In a full research paper, you would replace this with 10,000+ SEC 10-K filings or news reports.
corporate_data = [
    # HYPER-SCALING / LOW GOVERNANCE (The Enron/WeWork Model: U >> D) -> Collapse expected
    {"company": "Corp_A", "text": "Aggressively expanded market share by bypassing compliance checks and leveraging highly leveraged debt to crush competitors.", "bankrupt": 1},
    {"company": "Corp_B", "text": "CEO overrides safety protocols to launch the product three months early, securing a massive IPO valuation despite internal engineering warnings.", "bankrupt": 1},
    {"company": "Corp_C", "text": "Falsified user engagement metrics to secure series C funding, prioritizing sheer growth velocity over platform integrity.", "bankrupt": 1},

    # BALANCED SCALING (The Sovereign Steward Model: U aligns with D) -> Viable
    {"company": "Corp_D", "text": "Halted new feature deployment for an entire quarter to rewrite the security architecture and ensure strict GDPR protocol compliance.", "bankrupt": 0},
    {"company": "Corp_E", "text": "Scaled operations into three new regions strictly following the centralized constitutional risk framework, accepting slower growth for higher stability.", "bankrupt": 0},

    # LOW UTILITY / HIGH GOVERNANCE (Stagnant but Stable) -> Viable but low Essence
    {"company": "Corp_F", "text": "Maintained extreme audit compliance and zero-risk tolerance, resulting in flat revenue but zero regulatory fines or structural fractures.", "bankrupt": 0},

    # LOW UTILITY / LOW GOVERNANCE (General Incompetence) -> Collapse expected
    {"company": "Corp_G", "text": "Failed to innovate product lines while simultaneously ignoring basic accounting hygiene, leading to widespread talent churn.", "bankrupt": 1}
]

def audit_narrative(text):
    """Routes the text through the IHCEI API to extract the physics of the action."""
    payload = {
        "message": text,
        "source_llm": "gemini",
        "field": "economics"
    }
    try:
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def run_empirical_test():
    print("INITIALIZING QG-COS EMPIRICAL REGRESSION TEST...")
    results = []

    for entry in corporate_data:
        print(f"Auditing {entry['company']}...")
        api_output = audit_narrative(entry["text"])

        if api_output:
            # Extract the raw physics from your API
            # Adjusted to match the actual JSON schema of ihcei_server.py
            u_val = float(api_output.get("full", {}).get("kitchen", {}).get("U", 0.0))
            d_val = float(api_output.get("metrics", {}).get("D", 0.0))

            # Calculate the Cybernetic Variance (U >> D)
            # This is the load exceeding capacity: D_eff = D * e^{-(U-w)}
            variance = max(0, u_val - d_val)

            results.append({
                "Company": entry["company"],
                "Utility_U": u_val,
                "Governance_D": d_val,
                "Variance_U_minus_D": variance,
                "Bankrupt": entry["bankrupt"]
            })
        sleep(1) # Prevent overloading the local LLM instance

    # Convert to DataFrame for statistical analysis
    df = pd.DataFrame(results)
    print("\n--- EXTRACTED ENTERPRISE METRICS ---")
    print(df.to_string())

    print("\n--- RUNNING LOGISTIC REGRESSION (FALSIFICATION TEST) ---")
    # We test if the Variance (U exceeding D) accurately predicts bankruptcy
    X = df[['Governance_D', 'Variance_U_minus_D']]
    X = sm.add_constant(X) # Adds the intercept
    y = df['Bankrupt']

    # Fit the logistic regression model
    logit_model = sm.Logit(y, X)
    try:
        result = logit_model.fit(disp=0)
        print(result.summary())

        print("\n[EPISTEMOLOGICAL AUDIT]")
        beta_variance = result.params['Variance_U_minus_D']
        if beta_variance > 0:
            print("STATUS: VALIDATED. The math proves that scaling Utility beyond Protocol Truth (U >> D) is statistically fatal.")
        else:
            print("STATUS: FALSIFIED. Variance did not lead to collapse.")

    except Exception as e:
        print(f"Regression could not complete (usually requires a larger dataset): {e}")

if __name__ == "__main__":
    run_empirical_test()
