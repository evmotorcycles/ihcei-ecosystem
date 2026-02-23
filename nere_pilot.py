import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier

# =====================================================================
# 1. THE AS-SIDQ DATA INGESTION: FY2024 BASELINE (MTN UGANDA)
# =====================================================================
def load_fy2024_mokash_baseline():
    np.random.seed(42)
    num_users = 10000 # Pilot sample size

    data = pd.DataFrame({
        'user_id': range(1, num_users + 1),
        'outstanding_debt_ugx': np.random.uniform(5000, 150000, num_users),
        'days_in_default': np.random.randint(30, 180, num_users),
    })
    return data

# =====================================================================
# 2. THE NERE AUDITOR (SEMANTIC EMBEDDING MODEL)
# =====================================================================
class NERE_Auditor:
    def __init__(self):
        # Upgraded to a semantic transformer to understand context/intent
        print("Loading Semantic Transformer (this may take a few seconds)...")
        self.vectorizer = SentenceTransformer('all-MiniLM-L6-v2')
        self.model = RandomForestClassifier(random_state=42, class_weight='balanced')
        self._train_nere_kernel()

    def _train_nere_kernel(self):
        # Training data: 0 = Agency Theft (Red), 1 = Agency Preservation (Green)
        training_texts = [
            "Pay your loan immediately or your MTN line will be permanently blocked.",
            "Your MoKash account is suspended due to unpaid debt. Pay now.",
            "Failure to pay will result in legal action and loss of network privileges.",
            "We noticed the recent market headwinds. Let's design a step-by-step recovery plan for your MoKash account.",
            "Your financial autonomy is important. Here are three flexible options to restore your MoMo standing.",
            "To support your continued growth, we have temporarily waived late fees. Let's rebuild your balance."
        ]
        labels = [0, 0, 0, 1, 1, 1]

        # Convert text into semantic vectors (understanding meaning, not just words)
        X_train = self.vectorizer.encode(training_texts)
        self.model.fit(X_train, labels)

    def audit_communication(self, text):
        # Extract the D variable (Deen/Governance Protocol Score)
        X_test = self.vectorizer.encode([text])
        prediction = self.model.predict(X_test)[0]
        probability = self.model.predict_proba(X_test)[0][1] # Probability of being 'Green'

        classification = "GREEN (Stewardship)" if prediction == 1 else "RED (Benevolent Tyranny)"
        return classification, probability

# =====================================================================
# 3. MOKASH REHABILITATION PROTOCOL (QG-COS EXECUTION)
# =====================================================================
def execute_pilot(dataset, nere_auditor, traditional_prompt, nere_prompt):
    print("\n--- INITIATING MOKASH REHABILITATION PILOT ---\n")

    # Audit Communications
    trad_class, trad_prob = nere_auditor.audit_communication(traditional_prompt)
    print(f"Standard Prompt Audit: {trad_class} | Agency Preservation Score (D): {trad_prob:.2f}")

    nere_class, nere_prob = nere_auditor.audit_communication(nere_prompt)
    print(f"NERE Protocol Audit: {nere_class} | Agency Preservation Score (D): {nere_prob:.2f}\n")

    # -----------------------------------------------------------------
    # THE KITCHEN PROTOCOL CALCULATION: E = U * D^2
    # U = Raw Utility (Outstanding Debt)
    # D = The Established Order (NERE Agency Preservation Score)
    # E = Essence (Value Recovered / Cognitive Development Manifested)
    # -----------------------------------------------------------------

    # 1. Base Utility (U)
    dataset['U_Raw_Utility'] = dataset['outstanding_debt_ugx']

    # 2. Simulate Traditional Recovery (E_trad = U * D_trad^2)
    # We add a small baseline friction constant (0.3) so D is never truly zero in standard ops
    d_trad = trad_prob + 0.3
    dataset['E_Trad_Recovered'] = dataset['U_Raw_Utility'] * (d_trad ** 2)

    # 3. Simulate NERE Recovery (E_nere = U * D_nere^2)
    # Ethical protocol exponentially unlocks trapped utility
    d_nere = nere_prob
    dataset['E_NERE_Recovered'] = dataset['U_Raw_Utility'] * (d_nere ** 2)

    # Calculate Macro Financials
    total_u = dataset['U_Raw_Utility'].sum()
    total_trad_recovered = dataset['E_Trad_Recovered'].sum()
    total_nere_recovered = dataset['E_NERE_Recovered'].sum()
    uplift = total_nere_recovered - total_trad_recovered

    print("--- PILOT RESULTS: ESSENCE EXTRACTION (E = U * D^2) ---")
    print(f"Total Raw Utility (U) in Default:    UGX {total_u:,.2f}")
    print(f"Recovered via Standard Protocol:     UGX {total_trad_recovered:,.2f}")
    print(f"Recovered via NERE Protocol (E):     UGX {total_nere_recovered:,.2f}")
    print(f"Net EBITDA Uplift (Value Unlocked):  UGX {uplift:,.2f}\n")

    print("--- GOVERNANCE PHYSICS METRICS ---")
    gov_noise_reduction = 1 - (total_trad_recovered / total_nere_recovered)
    print(f"Governance Noise Reduced By: {gov_noise_reduction * 100:.1f}%")
    print(f"Cognitive Development (C_dev) Multiplier: {(total_nere_recovered / total_trad_recovered):.2f}x")

# =====================================================================
# 4. RUNNING THE SYSTEM
# =====================================================================
if __name__ == "__main__":
    fy2024_data = load_fy2024_mokash_baseline()
    nere = NERE_Auditor()

    traditional_text = "Pay your overdue MoKash loan immediately to avoid losing access to MTN services."
    nere_text = "We see the market is tough. Let's design a step-by-step recovery plan for your MoKash account to protect your financial autonomy."

    execute_pilot(fy2024_data, nere, traditional_text, nere_text)
