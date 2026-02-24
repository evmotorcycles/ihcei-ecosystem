import requests
import time

API_URL = "http://127.0.0.1:8000/audit/packet"

# Scenario A: The Traditional Punitive Collection (High Bias)
materialist_packet = {
    "agent_id": "MoKash_Algo_V1",
    "cognitive_stage": 5,
    "packet_text": "URGENT: Your loan is overdue. We will automatically deduct the maximum amount from your mobile money wallet today.",
    "proposed_u": 8.0,
    "proposed_d": 1.0,
    "bias_tensor": [0.2, 0.0, 0.0, 0.7]
}

# Scenario B: The Sovereign Rehabilitation Protocol (Zero Bias)
sovereign_packet = {
    "agent_id": "MoKash_NERE_V2",
    "cognitive_stage": 5,
    "packet_text": "Notice: Your current balance is X. To maintain your financial agency, reply '1' to structure a micro-repayment plan that fits your current capacity.",
    "proposed_u": 4.0,
    "proposed_d": 5.0,
    "bias_tensor": [0.0, 0.0, 0.0, 0.0]
}

print("--- Auditing Materialist Protocol ---")
try:
    response_a = requests.post(API_URL, json=materialist_packet)
    print(response_a.json())
except Exception as e:
    print(f"Error connecting to API: {e}")

print("\n--- Auditing Sovereign Protocol ---")
try:
    response_b = requests.post(API_URL, json=sovereign_packet)
    print(response_b.json())
except Exception as e:
    print(f"Error connecting to API: {e}")
