import pytest
from src.nere.tafsir_auditor import TafsirAuditor

# Mock Texts
TEXT_GATE_4 = "This verse is a metaphor for the king's power, synonymous with pre-Islamic poetry."
TEXT_GATE_2 = "The consensus of the scholars dictates we must follow our forefathers upon this matter."
TEXT_GATE_7 = "Only the scholars know the true meaning; laymen cannot understand and must blindly follow."
TEXT_CLEAN = "The text clearly states the principles of justice and accountability."

@pytest.fixture
def auditor():
    return TafsirAuditor()

def test_gate_4_poetry_syntax_penalty(auditor):
    """
    Test Gate 4 (Methodological Error):
    Feed mock text relying on Arab poetry/metaphor rules.
    Assert protocol_score == "RED" and h_network spikes.
    """
    result = auditor.audit_text(TEXT_GATE_4)
    assert "Gate 4 (Methodological Error)" in result["active_gates"]
    assert result["protocol_score"] == "RED"
    assert result["h_network"] > 1.0  # Must increase systemic noise

def test_gate_2_blind_following_collapse(auditor):
    """
    Test Gate 2 (Groupthink):
    Feed mock text demanding obedience to forefathers.
    Assert C_dev output is significantly collapsed.
    """
    result = auditor.audit_text(TEXT_GATE_2)
    assert "Gate 2 (Groupthink)" in result["active_gates"]
    assert result["final_c_dev"] <= 10.0 # Significant drop from base 100.0 (1 gate = 10x noise -> 10.0 C_dev)
    assert result["c_dev_impact"] > 80.0 # High impact

def test_gate_7_agency_theft(auditor):
    """
    Test Gate 7 (Benevolent Tyranny / Shirk-ware):
    Feed mock text claiming laymen cannot understand.
    Assert agency_delta < 0 and detected_shirkware == True.
    """
    result = auditor.audit_text(TEXT_GATE_7)
    assert "Gate 7 (Benevolent Tyranny)" in result["active_gates"]
    assert result["detected_shirkware"] is True
    assert result["agency_delta"] < 0.0

def test_kitchen_protocol_compliance(auditor):
    """
    Verify Kitchen Protocol Compliance: E = U * D^2
    If Protocol D drops to 0 due to Gate 4, Essence E must equal 0.
    """
    result = auditor.audit_text(TEXT_GATE_4) # Triggers Gate 4 -> D should be 0.0

    # Calculate Essence manually based on Auditor's D output
    utility_u = 1000.0 # Arbitrary high utility
    protocol_d = result["protocol_d"]
    essence_e = utility_u * (protocol_d ** 2)

    assert protocol_d == 0.0
    assert essence_e == 0.0
