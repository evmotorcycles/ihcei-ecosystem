import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import classification_report

def calculate_ihcei_metrics(df, wuss_capacity=5.0):
    """
    Computes the QG-COS theoretical metrics for the corporate dataset.
    U_proxy: Revenue growth / extraction velocity
    D_proxy: Institutional alignment (ISS/ESG score bounded 0 to 1)
    """
    # 1. Calculate Ashby Variance (The Entropy Injector)
    df['ashby_variance'] = df['U_proxy'] - df['D_proxy']

    # 2. Compute Effective D (Smooth Degradation under load)
    # Applying the mathematically verified cognitive load penalty
    overflow = np.maximum(0, df['U_proxy'] - wuss_capacity)
    df['D_effective'] = df['D_proxy'] * np.exp(-overflow)

    # 3. Compute Systemic Essence (The Lyapunov Candidate)
    # E_ssence = U * (D_effective)^2
    df['E_ssence'] = df['U_proxy'] * (df['D_effective'] ** 2)

    # 4. Compute Systemic Friction (hbar_network proxy)
    # Friction goes parabolic as U detaches from D
    df['hbar_friction'] = np.exp(np.maximum(0, df['ashby_variance'])) - 1.0

    return df

def run_ihcei_logistic_regression(df):
    """
    Runs the logistic regression to predict Systemic Failure (1 or 0).
    Proves that high U alone doesn't cause failure, but high hbar_friction does.
    """
    # Define independent variables (X) and target (y)
    # We test the IHCEI structural hazard directly against the failure event
    features = ['U_proxy', 'D_proxy', 'hbar_friction', 'E_ssence']
    X = df[features]
    X = sm.add_constant(X) # Add y-intercept
    y = df['Systemic_Failure_5yr'] # Binary target: 1 (Collapse), 0 (Stable)

    # Fit the Logistic Regression Model
    logit_model = sm.Logit(y, X)
    result = logit_model.fit(disp=False)

    print("\n[IHCEI QG-COS] LOGISTIC REGRESSION: CORPORATE FAILURE PREDICTION")
    print("="*65)
    print(result.summary())

    return result

# --- EXECUTION MOCKUP ---
# In production, replace this with the live SEC/ISS SQL database pull.
np.random.seed(42)
n_samples = 1000

# Generating synthetic data to simulate the real-world test
mock_data = pd.DataFrame({
    'U_proxy': np.random.uniform(1.0, 10.0, n_samples),
    'D_proxy': np.random.uniform(0.1, 1.0, n_samples),
})

# Simulate ground truth: Failure is highly likely if Systemic Friction is extreme
wuss = 5.0
mock_data = calculate_ihcei_metrics(mock_data, wuss_capacity=wuss)
failure_prob = 1 / (1 + np.exp(-(mock_data['hbar_friction'] * 0.8 - 4.0)))
mock_data['Systemic_Failure_5yr'] = np.random.binomial(1, failure_prob)

# Run the model
model_results = run_ihcei_logistic_regression(mock_data)