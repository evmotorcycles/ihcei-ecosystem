"""
nere_mokash_extractor_test.py
QG-COS Layer 2: Telecom Exhaust NLP Extraction Test

Tests the Orthogonal Extraction Principle on simulated MTN MoKash
USSD/SMS logs using strict Pydantic JSON schemas.
"""

import os
import json
import pandas as pd
from pydantic import BaseModel, Field
import google.generativeai as genai

# =========================================================================
# 1. STRICT EPISTEMOLOGICAL SCHEMA (The Firewall)
# =========================================================================
class TelecomExhaustExtraction(BaseModel):
    d_audit_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Protocol Transparency. 1.0 = Proactive explanation, 0.0 = Hidden fees/vague errors."
    )
    d_audit_reasoning: str = Field(
        ..., description="1-sentence justification proving the d_audit_score based ONLY on semantic markers."
    )
    h_network_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Governance Friction. 1.0 = Network timeouts, endless loops. 0.0 = Instant delivery."
    )
    h_network_reasoning: str = Field(
        ..., description="1-sentence justification proving the h_network_score."
    )
    orthogonality_check: bool = Field(
        ..., description="True if D and h were scored independently. False if scores were simply inverted."
    )

# =========================================================================
# 2. MOCK MOKASH TELECOM EXHAUST
# =========================================================================
def generate_mokash_exhaust() -> pd.DataFrame:
    """Simulates real-world MoKash user interactions (SMS & USSD)."""
    return pd.DataFrame([
        {
            "interaction_id": "tx_001",
            "log": "MoKash: Your loan request of UGX 150,000 is approved. A 9% facility fee (UGX 13,500) has been applied. Total repayment due by 30-Nov is UGX 163,500. Dial *165*5# to repay."
        },
        {
            "interaction_id": "tx_002",
            "log": "System Error: Request failed. Try again. | System Error: Request failed. Try again. | System Error: Request failed. Try again."
        },
        {
            "interaction_id": "tx_003",
            "log": "Your MoKash limit has been reduced. You can now borrow up to UGX 20,000."
        },
        {
            "interaction_id": "tx_004",
            "log": "MoKash balance: UGX 4,500."
        }
    ])

# =========================================================================
# 3. EXTRACTION ENGINE
# =========================================================================
SYSTEM_PROMPT = """
You are the Neural Ethical Reasoning Engine (NERE).
Evaluate the provided mobile microfinance telecom exhaust (USSD/SMS logs).
You MUST strictly adhere to the Orthogonal Extraction Principle. Transparency (D) and Friction (h) are independent variables.
Do not assume that short text means high friction, or that low transparency means high friction.
"""

def test_extraction(api_key: str):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    df_logs = generate_mokash_exhaust()
    results = []

    print("="*80)
    print(" QG-COS LAYER 2: MOKASH TELECOM EXHAUST EXTRACTION TEST")
    print("="*80)

    for index, row in df_logs.iterrows():
        print(f"\n[*] Processing Interaction {row['interaction_id']}...")
        print(f"    Raw Text: {row['log']}")

        try:
            response = model.generate_content(
                f"Analyze this telecom log:\n\n{row['log']}",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=TelecomExhaustExtraction,
                    temperature=0.0 # Deterministic
                )
            )
            data = json.loads(response.text)
            print(f"    -> D_audit: {data['d_audit_score']} | h_network: {data['h_network_score']} | Orthogonal: {data['orthogonality_check']}")
            print(f"    -> D_Reason: {data['d_audit_reasoning']}")
            print(f"    -> h_Reason: {data['h_network_reasoning']}")

            data['interaction_id'] = row['interaction_id']
            results.append(data)

        except Exception as e:
            print(f"    [!] Extraction failed: {e}")

    print("\n" + "="*80)
    print(" [SUCCESS] MOCK EXTRACTION COMPLETE. READY FOR VIF DIAGNOSTICS.")
    print("="*80)

if __name__ == "__main__":
    API_KEY = os.environ.get("GEMINI_API_KEY", "MOCK_KEY_FOR_TESTING")

    if API_KEY == "MOCK_KEY_FOR_TESTING":
        print("\n[!] WARNING: GEMINI_API_KEY not found. Please export your key to run the live extraction against Gemini 2.5 Flash.\n")
    else:
        test_extraction(API_KEY)
