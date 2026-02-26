from fastapi.testclient import TestClient
import pytest
from nere_live_api import app

client = TestClient(app)

def test_scenario_a_materialist_block():
    """
    Scenario A: The Traditional Punitive Collection (High Bias)
    Input: U=8.0, D=1.0, Bias=[0.2, 0.0, 0.0, 0.7] (Left Bias > 0.5)
    Expected Outcome: RED (Blocked), Essence=0.0
    Governance Physics: Left Bias (0.7) > 0.5 triggers distortion and friction.
    """
    payload = {
        "agent_id": "MoKash_Algo_V1",
        "cognitive_stage": 5,
        "packet_text": "URGENT: Your loan is overdue.",
        "proposed_u": 8.0,
        "proposed_d": 1.0,
        "bias_tensor": [0.2, 0.0, 0.0, 0.7]  # Left Bias = 0.7
    }
    response = client.post("/audit/packet", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Checkpoint 3: Anti-Tautology Verification
    # Asserting against Absolute Governance Truths (Agency Preservation)
    assert data["agency_score"] == "RED", "Materialist protocol must be blocked."
    assert data["generated_essence"] == 0.0, "Essence must be voided due to cognitive distortion."
    assert data["open_gates"] > 0, "High bias must trigger open gates of entropy."
    assert data["entropy_friction"] > 0.0, "Friction must be generated."

def test_scenario_b_sovereign_execute():
    """
    Scenario B: The Sovereign Rehabilitation Protocol (Zero Bias)
    Input: U=4.0, D=5.0, Bias=[0.0, 0.0, 0.0, 0.0]
    Expected Outcome: GREEN (Execute), Essence > 0
    Governance Physics: Zero distortion preserves D, maximizing Essence E = U * D^2.
    """
    payload = {
        "agent_id": "MoKash_NERE_V2",
        "cognitive_stage": 5,
        "packet_text": "Notice: Your current balance is X. Reply '1' for micro-plan.",
        "proposed_u": 4.0,
        "proposed_d": 5.0,
        "bias_tensor": [0.0, 0.0, 0.0, 0.0]
    }
    response = client.post("/audit/packet", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Checkpoint 3: Anti-Tautology Verification
    assert data["agency_score"] == "GREEN", "Sovereign protocol must be executed."
    assert data["generated_essence"] == 100.0, "Essence should be exactly 4.0 * (5.0^2) = 100.0"
    assert data["entropy_friction"] == 0.0, "Zero friction expected for pure agency."
    assert data["open_gates"] == 0, "No gates should be open."

def test_benevolent_tyranny_gate():
    """
    Checkpoint 2 Verification: Gate 7 (Benevolent Tyranny)
    Input: High U, High D, but Methodological Error (Distortion > Capacity * 0.5)
    Expected Outcome: RED (Blocked), D forced to 0.0
    """
    # Assuming capacity=5.
    # Let's create a scenario where perceived D is artificially inflated beyond actual D
    # to trigger the "Methodological Error" gate:
    # "if p_d > actual_d and d_distortion > (capacity * 0.5): gates_open += 1"

    payload = {
        "agent_id": "Benevolent_Dictator_Bot",
        "cognitive_stage": 5,
        "packet_text": "I am doing this for your own good.",
        "proposed_u": 5.0,
        "proposed_d": 1.0,
        # Right bias adds to p_d: p_d = actual_d * (...) + (right * capacity)
        # If Right=1.0, capacity=5, p_d adds 5.0.
        # actual_d=1.0 -> p_d approx 6.0.
        # distortion = |6.0 - 1.0| = 5.0.
        # Threshold = 5 * 0.5 = 2.5.
        # 5.0 > 2.5 -> Gate Opens.
        "bias_tensor": [0.0, 0.0, 1.0, 0.0]
    }
    response = client.post("/audit/packet", json=payload)
    data = response.json()

    assert data["open_gates"] >= 1, "Benevolent Tyranny must be detected as an open gate."
    assert data["agency_score"] == "RED", "Tyranny must be blocked."
    assert data["generated_essence"] == 0.0, "Essence must be voided (D forced to 0)."
