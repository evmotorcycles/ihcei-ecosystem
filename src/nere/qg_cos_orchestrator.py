"""
qg_cos_orchestrator.py
QG-COS Final Pipeline Integration & Execution

This is the unified Control Plane that orchestrates Layer 2 (Semantic Extraction)
and Layer 1 (Econometric Validation), ensuring strict epistemological boundaries.

To directly address the circularity critique:
1. HR/IT Metrics (U_efficiency, C_dev) are ingested STRICTLY independently.
2. NERE Metrics (D_audit, h_network) are extracted STRICTLY from text exhaust.
3. The variables are ONLY joined at the final CSV stage before regression.
"""

import os
import subprocess
import pandas as pd
import numpy as np

# Import Layer 2 NLP Extractor
# Ensure nere_nlp_extractor.py is in the same directory or accessible via PYTHONPATH
try:
    from nere_nlp_extractor import extract_nere_metrics
except ImportError:
    print("[!] Failed to import nere_nlp_extractor. Ensure it is in the same directory.")
    # Mocking for standalone execution if file is missing in this context
    def extract_nere_metrics(api_key, text):
        return {"D_audit_score": 0.5, "h_network_score": 0.5}

# ─────────────────────────────────────────────────────────────────────────────
# 1. LAYER 2: INDEPENDENT MEASUREMENT (INGESTION & EXTRACTION)
# ─────────────────────────────────────────────────────────────────────────────

def ingest_mock_enterprise_exhaust() -> pd.DataFrame:
    """Simulates unstructured logs pulled from Slack/Jira APIs."""
    print("\n[1. INGESTION] Pulling unstructured enterprise exhaust (Slack, Jira)...")
    return pd.DataFrame([
        {"entity_id": 1, "time_month": 1, "log": "Just deploy it, we don't have time to review the architecture."},
        {"entity_id": 1, "time_month": 2, "log": "I refactored the auth module because the old token system was failing under load, see Jira-89 for the causal analysis."},
        {"entity_id": 2, "time_month": 1, "log": "Fix line 42."},
        {"entity_id": 2, "time_month": 2, "log": "Hey team, AI suggested this fix, but let's review the underlying state logic before committing so we don't break dependencies."},
        {"entity_id": 3, "time_month": 1, "log": "Update the CSS immediately. The CEO wants it green."},
        {"entity_id": 3, "time_month": 2, "log": "Attached the A/B test results showing why we chose the green CSS over blue. Refer to confluence/design-doc."}
    ])

def extract_nlp_metrics(df_exhaust: pd.DataFrame, api_key: str) -> pd.DataFrame:
    """Processes text exhaust through the Gemini API to extract D and h."""
    print("\n[2. EXTRACTION (LAYER 2)] Executing Orthogonal Extraction Principle via NERE...")

    processed_records = []
    for index, row in df_exhaust.iterrows():
        print(f"   -> Scanning Entity {row['entity_id']} | Month {row['time_month']}...")
        extracted = extract_nere_metrics(api_key, row['log'])
        processed_records.append({
            "entity_id": row['entity_id'],
            "time_month": row['time_month'],
            "D_audit": extracted.get('D_audit_score', 0.5),
            "h_network": extracted.get('h_network_score', 0.5),
        })

    return pd.DataFrame(processed_records)

# ─────────────────────────────────────────────────────────────────────────────
# 2. THE CRUCIBLE: INDEPENDENT DATA JOINING
# ─────────────────────────────────────────────────────────────────────────────

def ingest_independent_hr_it_metrics(N: int=3, T: int=2) -> pd.DataFrame:
    """
    Simulates external databases (e.g., Workday, GitHub, Jira performance).
    CRITICAL BOUNDARY: These are generated entirely independently of the text.
    """
    print("\n[3. INDEPENDENT SOURCING] Querying external HR/IT databases for U and C_dev...")
    rng = np.random.default_rng(42)

    data = []
    # Generate some plausible temporal data
    for i in range(1, N + 1):
        # Base capability
        base_c = rng.uniform(0.4, 0.7)
        for t in range(1, T + 1):
            data.append({
                "entity_id": i,
                "time_month": t,
                "U_efficiency": rng.uniform(0.6, 1.0), # e.g., Story points delivered
                "C_dev": base_c + (t * rng.uniform(-0.05, 0.1)) # e.g., Skill matrix growth
            })
    return pd.DataFrame(data)

def construct_governed_panel(df_nlp: pd.DataFrame, df_hr: pd.DataFrame) -> pd.DataFrame:
    """Merges the independent data streams into the final panel."""
    print("\n[4. DATA JOINING] Merging NLP Metrics with HR/IT Telemetry...")
    df_merged = pd.merge(df_hr, df_nlp, on=['entity_id', 'time_month'], how='left')

    # Center the interaction term to prevent Statsmodels VIF warnings (multicollinearity)
    # The regression script may do this, but doing it here guarantees the CSV is ready.
    if 'U_efficiency' in df_merged.columns and 'D_audit' in df_merged.columns:
        df_merged['U_x_D_centred'] = (df_merged['U_efficiency'] - df_merged['U_efficiency'].mean()) * \
                                     (df_merged['D_audit'] - df_merged['D_audit'].mean())
    return df_merged

# ─────────────────────────────────────────────────────────────────────────────
# 3. LAYER 1: ECONOMETRIC VALIDATION (FIXED EFFECTS VIA SUBPROCESS)
# ─────────────────────────────────────────────────────────────────────────────

def execute_layer_1_regression(csv_path: str):
    """
    Calls the external Layer 1 script (nere_panel_regression.py / nere_qareen_simulation.py)
    to run the panel regression on the generated empirical CSV.
    """
    print("\n[5. EXECUTION (LAYER 1)] Invoking Econometric Validation Engine...")

    # Check for the existence of the Layer 1 script
    # The user's prompt references "nere_panel_regression.py", but memory says "nere_qareen_simulation.py"
    # was built in previous steps. We will try both common names in the codebase.
    target_script = None
    possible_scripts = [
        "src/nere/nere_panel_regression.py",
        "src/nere/nere_qareen_simulation.py",
        "nere_panel_regression.py",
        "nere_qareen_simulation.py"
    ]

    for script in possible_scripts:
        if os.path.exists(script):
            target_script = script
            break

    if target_script:
        print(f"[*] Found execution script: {target_script}")
        try:
            # We pass the CSV path as an environment variable or assume the script
            # reads from the default 'qg_cos_empirical_panel.csv'
            env = os.environ.copy()
            env["QG_COS_EMPIRICAL_CSV"] = csv_path

            result = subprocess.run(["python3", target_script], env=env, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f"[!] Warning/Error output from Layer 1:\n{result.stderr}")

            # If the script prints the falsification verdict, we rely on it.
            # But we also run Layer 6 locally for structural guarantee.
        except Exception as e:
            print(f"[!] Failed to execute Layer 1 script: {e}")
    else:
        print("[!] Layer 1 Regression script (nere_panel_regression.py) not found in expected locations.")
        print("[!] Assuming execution happens externally. Regression skipped.")

# ─────────────────────────────────────────────────────────────────────────────
# 4. LAYER 6: AUDIT OUTPUT & FALSIFICATION VERDICT
# ─────────────────────────────────────────────────────────────────────────────

def output_audit_verdict(df: pd.DataFrame):
    """Evaluates the mathematical boundaries and declares falsification status structurally."""
    print("\n" + "="*80)
    print(" LAYER 6: AUDIT OUTPUT & STRUCTURAL VERDICT")
    print("="*80)

    # 1. Check Provenance & Sample Size
    n_entities = df['entity_id'].nunique()
    t_months = df['time_month'].nunique()

    print(f"[*] Panel Data Integrity: {n_entities} Entities over {t_months} Months.")

    if n_entities < 100 or t_months < 6:
        print("\n[LAYER 6 LOCKOUT]: TAG=SYNTHETIC_PIPELINE_TEST.")
        print("Dataset does not meet Baseline Criteria (N>=100, T>=6).")
        print("Verdict: PIPELINE VERIFICATION STATUS ONLY. Cannot Falsify Framework.")
        return

    # 2. Check Variance (Culture stasis check)
    var_D = df['D_audit'].var()
    var_h = df['h_network'].var()
    if var_D < 0.05 or var_h < 0.05:
         print("\n[LAYER 6 LOCKOUT]: STATISTICAL ANOMALY (INSUFFICIENT SIGNAL).")
         print("Variance in culture/metrics is too low to test ADGE.")
         return

    print("\n[SUCCESS] Structural boundaries met. See Layer 1 output for empirical falsification verdict.")

# ─────────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATION LOOP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 80)
    print(" SYSTEM INITIALIZATION: QG-COS Orchestrator")
    print(" Executing Governed Cognitive VM Pipeline")
    print("=" * 80)

    api_key = os.environ.get("GEMINI_API_KEY", "MOCK_KEY_FOR_TESTING")

    # 1. Ingestion
    df_exhaust = ingest_mock_enterprise_exhaust()

    # 2. Extraction (Layer 2)
    df_nlp = extract_nlp_metrics(df_exhaust, api_key)

    # 3. Independent HR Sourcing
    df_hr = ingest_independent_hr_it_metrics(N=3, T=2)

    # 4. Data Joining (The Crucible)
    df_panel = construct_governed_panel(df_nlp, df_hr)

    # Save physical CSV (Simulating Database persistence)
    csv_path = "qg_cos_empirical_panel.csv"
    df_panel.to_csv(csv_path, index=False)
    print(f"[*] Panel Data persisted to {csv_path}")

    # 5. Execution (Layer 1 Regression)
    execute_layer_1_regression(csv_path)

    # 6. Audit Output (Layer 6)
    output_audit_verdict(df_panel)

if __name__ == "__main__":
    main()
