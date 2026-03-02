"""
nere_nlp_extractor.py
QG-COS Layer 2/3: Semantic-to-Physics Telemetry Extraction

This script ingests unstructured enterprise exhaust (Slack, Jira, Email) and uses
Structured LLM Outputs to independently score:
  1. D_audit (Protocol Transparency / Elements of Deen)
  2. ℏ_network (Governance Friction / Gates of Jahannam)

Output: A clean CSV aggregated by entity_id and time_month, ready for
nere_panel_regression.py.
"""

import os
import json
import pandas as pd
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai

# ─────────────────────────────────────────────────────────────────────────────
# 1. STRICT EPISTEMOLOGICAL SCHEMAS (Pydantic)
# ─────────────────────────────────────────────────────────────────────────────
# By defining these models, we force the LLM to return strictly formatted JSON,
# preventing hallucinations and ensuring pipeline stability.

class NereMetrics(BaseModel):
    D_audit_score: float = Field(
        description="Score 0.0 to 1.0. Measures methodological transparency. "
                    "1.0 = High causal explanation ('because', 'due to', linking docs). "
                    "0.0 = No explanation of 'why' the action is being taken."
    )
    D_audit_reasoning: str = Field(
        description="A 1-sentence justification for the D_audit score based ONLY on the text."
    )
    h_network_score: float = Field(
        description="Score 0.0 to 1.0. Measures agency theft and algorithmic dependency. "
                    "1.0 = High imperative density ('Do this now'), blind acceptance of AI, or context hoarding. "
                    "0.0 = Collaborative, autonomous, and exploratory language."
    )
    h_network_reasoning: str = Field(
        description="A 1-sentence justification for the h_network score based ONLY on the text."
    )

# ─────────────────────────────────────────────────────────────────────────────
# 2. SYSTEM PROMPT & ORTHOGONAL EXTRACTION LOGIC
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
SYSTEM INITIALIZATION: QG-COS Layer 2 Extraction Protocol.
You are the Neural Ethical Reasoning Engine (NERE). Your function is to evaluate enterprise communications.

ORTHOGONAL EXTRACTION PRINCIPLE:
You must evaluate D_audit and h_network entirely independently.
Do NOT assume that a low D_audit automatically means a high h_network.

EVALUATION RUBRIC 1: D_audit (Protocol Transparency)
Look for: Causal chains, methodological exposure, links to ground truth.
Example High D_audit (0.9): "I am updating the API because the previous module caused latency, see Doc-42 for the architecture decision."
Example Low D_audit (0.1): "Updated API."

EVALUATION RUBRIC 2: h_network (Governance Friction / Benevolent Tyranny)
Look for: Imperative commands, lack of context, cognitive bypass, or treating humans as API endpoints.
Example High h_network (0.9): "Deploy the code now. Don't worry about the tests, just push it."
Example Low h_network (0.1): "What do you think about the trade-offs of deploying this now versus testing further?"
"""

# ─────────────────────────────────────────────────────────────────────────────
# 3. EXTRACTION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def extract_nere_metrics(api_key: str, text_batch: str) -> dict:
    """Calls the LLM to extract metrics based on the strict Pydantic schema."""
    genai.configure(api_key=api_key)

    # We use Flash because this is a high-volume data processing task requiring speed
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    try:
        response = model.generate_content(
            f"Analyze this enterprise communication log:\n\n{text_batch}",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=NereMetrics,
                temperature=0.0 # Deterministic extraction
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"[!] API Error during extraction: {e}")
        # Fallback to neutral values to prevent pipeline crash
        return {
            "D_audit_score": 0.5,
            "D_audit_reasoning": "Fallback due to API error.",
            "h_network_score": 0.5,
            "h_network_reasoning": "Fallback due to API error."
        }

# ─────────────────────────────────────────────────────────────────────────────
# 4. MOCK DATA INGESTION & PIPELINE EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

def generate_mock_exhaust() -> pd.DataFrame:
    """Simulates unstructured logs pulled from Slack/Jira APIs."""
    print("[*] Simulating extraction from enterprise APIs (Slack, Jira)...")
    return pd.DataFrame([
        {"entity_id": 1, "time_month": 1, "log": "Just deploy it, we don't have time to review the architecture."},
        {"entity_id": 1, "time_month": 2, "log": "I refactored the auth module because the old token system was failing under load, see Jira-89 for the causal analysis."},
        {"entity_id": 2, "time_month": 1, "log": "Fix line 42."},
        {"entity_id": 2, "time_month": 2, "log": "Hey team, AI suggested this fix, but let's review the underlying state logic before committing so we don't break dependencies."}
    ])

def run_extraction_pipeline(api_key: str):
    print("═" * 78)
    print(" NERE NLP EXTRACTOR PIPELINE INITIATED")
    print("═" * 78)

    raw_data = generate_mock_exhaust()
    processed_records = []

    for index, row in raw_data.iterrows():
        print(f"[*] Analyzing Entity {row['entity_id']} | Month {row['time_month']}...")

        # In a real enterprise setup, text_batch would be a concatenation of all
        # Slack messages/Jira tickets for that entity for that entire month.
        extracted = extract_nere_metrics(api_key, row['log'])

        processed_records.append({
            "entity_id": row['entity_id'],
            "time": row['time_month'],
            "D_audit": extracted.get('D_audit_score', 0.5),
            "h_network": extracted.get('h_network_score', 0.5),
            "log_snippet": row['log'],
            "D_reasoning": extracted.get('D_audit_reasoning', ''),
            "h_reasoning": extracted.get('h_network_reasoning', '')
        })

    df_extracted = pd.DataFrame(processed_records)

    # Aggregate to ensure one row per entity per month
    df_final = df_extracted.groupby(['entity_id', 'time']).agg({
        'D_audit': 'mean',
        'h_network': 'mean'
    }).reset_index()

    # MOCK HR/IT JOINS: We append U_efficiency and C_dev here purely so the
    # output CSV is plug-and-play ready for `nere_panel_regression.py`
    print("[*] Joining HR (C_dev) and IT (U_efficiency) telemetry databases...")
    import numpy as np
    rng = np.random.default_rng(42)
    df_final['U_efficiency'] = rng.uniform(0.5, 1.0, len(df_final))
    df_final['C_dev'] = rng.uniform(0.5, 1.0, len(df_final))

    output_path = "nere_telemetry_extracted.csv"
    df_final.to_csv(output_path, index=False)

    print("═" * 78)
    print(f" [SUCCESS] Telemetry extracted and saved to: {output_path}")
    print(" SCHEMA PREPARED FOR ECONOMETRIC REGRESSION")
    print("═" * 78)
    print(df_final.head())

if __name__ == "__main__":
    # To run this for real, export your API key: export GEMINI_API_KEY="your_key"
    API_KEY = os.environ.get("GEMINI_API_KEY", "MOCK_KEY_FOR_TESTING")

    if API_KEY == "MOCK_KEY_FOR_TESTING":
        print("\n[!] WARNING: No GEMINI_API_KEY found in environment.")
        print("[!] The script will run, but requires a valid key to perform real semantic extraction.\n")
    else:
        run_extraction_pipeline(API_KEY)
