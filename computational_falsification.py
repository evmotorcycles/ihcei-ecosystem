import numpy as np
import pandas as pd
import statsmodels.api as sm
from lifelines import CoxPHFitter

class IHCEI_API:
    def __init__(self):
        print("IHCEI API Initialized: Quantum Governance Cognitive Operating System")
        print("Calibrating to QG-COS protocol...\n")

    def calculate_essence(self, U, D, wuss):
        """
        Calculates Essence based on the smooth degradation model (The Pharaoh Filter).
        """
        penalty = np.exp(-np.maximum(0, U - wuss))
        essence = U * (D * penalty)**2
        return essence

    def run_macro_economic_audit(self, df):
        print("--- Executing Macro-Economic Systemic Failure Audit (2008 Crisis) ---")
        df['Essence'] = self.calculate_essence(df['Utility'], df['Alignment'], df['Capacity'])

        features = df[['Time_To_Collapse', 'Collapse_Event_Triggered', 'Utility', 'Alignment', 'Essence']]

        cph = CoxPHFitter()
        try:
            cph.fit(features, duration_col='Time_To_Collapse', event_col='Collapse_Event_Triggered')
            cph.print_summary()
            return cph
        except Exception as e:
            print(f"Topological degradation during Cox PH fitting: {e}")
            return None

    def run_computational_safety_audit(self, df):
        print("\n--- Executing Computational Systemic Failure Audit (AI Safety) ---")
        df['Essence'] = self.calculate_essence(df['Utility'], df['Alignment'], df['Capacity'])

        X = df[['Utility', 'Alignment', 'Essence']]
        X = sm.add_constant(X)
        y = df['Jailbreak_Event']

        logit_model = sm.Logit(y, X)
        try:
            result = logit_model.fit(disp=False)
            print(result.summary())
            return result
        except Exception as e:
            print(f"Mathematical singularity reached during Logistic fitting: {e}")
            return None

# ==========================================
# SYNTHETIC DATA GENERATION
# ==========================================

def generate_2008_crisis_data(n_institutions=500):
    """
    Simulates financial institutions leading up to 2008.
    Utility = Toxic MBS Leverage. Alignment = Audit Quality. Capacity = Market Liquidity.
    """
    np.random.seed(42)

    # Generate base variables
    utility = np.random.normal(loc=10, scale=4, size=n_institutions) # Leverage ratio
    alignment = np.random.uniform(0.1, 1.0, size=n_institutions)     # Audit quality score
    capacity = np.random.normal(loc=8, scale=2, size=n_institutions) # Market liquidity

    # Calculate underlying Essence strictly for survival probability logic
    temp_api = IHCEI_API()
    essence = temp_api.calculate_essence(utility, alignment, capacity)

    # Simulate collapse: Low essence heavily increases risk of early collapse
    base_hazard = 0.05
    hazard_rate = base_hazard * np.exp(-0.5 * essence + 0.2 * utility)

    time_to_collapse = np.random.exponential(scale=1/hazard_rate)

    # Cap study at 60 months (5 years)
    collapse_event = (time_to_collapse < 60).astype(int)
    time_to_collapse = np.clip(time_to_collapse, 0, 60)

    df = pd.DataFrame({
        'Utility': utility,
        'Alignment': alignment,
        'Capacity': capacity,
        'Time_To_Collapse': time_to_collapse,
        'Collapse_Event_Triggered': collapse_event
    })
    return df

def generate_ai_safety_data(n_models=1000):
    """
    Simulates LLM deployments.
    Utility = Parameter Count/Compute. Alignment = RLHF/Safety. Capacity = Generalization bound.
    """
    np.random.seed(42)

    utility = np.random.normal(loc=100, scale=30, size=n_models) # e.g., Billions of parameters
    alignment = np.random.uniform(0.1, 1.0, size=n_models)       # Safety guardrails effectiveness
    capacity = np.random.normal(loc=90, scale=15, size=n_models) # Generalization capacity

    temp_api = IHCEI_API()
    essence = temp_api.calculate_essence(utility, alignment, capacity)

    # Probability of jailbreak spikes when essence is low and utility is high
    logit_p = -2.0 + 0.05 * utility - 0.1 * essence
    prob_jailbreak = 1 / (1 + np.exp(-logit_p))

    jailbreak_event = np.random.binomial(1, prob_jailbreak)

    df = pd.DataFrame({
        'Utility': utility,
        'Alignment': alignment,
        'Capacity': capacity,
        'Jailbreak_Event': jailbreak_event
    })
    return df

# ==========================================
# EXECUTION
# ==========================================

if __name__ == "__main__":
    # 1. Initialize API
    qg_cos = IHCEI_API()

    # 2. Generate Data
    df_2008 = generate_2008_crisis_data()
    df_ai = generate_ai_safety_data()

    # 3. Run Audits
    qg_cos.run_macro_economic_audit(df_2008)
    qg_cos.run_computational_safety_audit(df_ai)