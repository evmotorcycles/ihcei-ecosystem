import pytest
from src.nere.network_admin import NetworkOfAnfusAdmin, Node, InteractionResult

# Mock Data
SENDER_ADVANCED = Node("Node_A", 5.0, "Advanced")
SENDER_STUDENT = Node("Node_B", 2.0, "Student")
RECEIVER_STUDENT = Node("Node_C", 1.0, "Student")

TEXT_ZAKAT_FLOW = "Here is the evidence and principles for your consideration."
TEXT_GATE_7_CONCEIT = "You cannot understand this without me. Listen to me and obey."

@pytest.fixture
def admin():
    return NetworkOfAnfusAdmin()

def test_zakat_flow_success(admin):
    """
    Simulate Node A successfully transferring Zakat (Liquid Network).
    Assert: G_ij > 0.8, Status = APPROVED, Growth > 1.0.
    """
    # G_ij = 0.9 * 1.0 * 1.0 = 0.9.
    # Growth = e^(0.9 * 5.0) = e^4.5 ~ 90.0
    result = admin.process_interaction(
        sender=SENDER_ADVANCED,
        receiver=RECEIVER_STUDENT,
        text="Here is the evidence and principles for your consideration.",
        connection_strength=0.9,
        domain_compatibility=1.0,
        press_alignment=1.0
    )

    assert result.status == "APPROVED"
    assert result.g_ij >= 0.9
    assert result.network_growth > 10.0 # e^4.5 is large
    assert result.agency_delta > 0.0 # Empowerment

def test_gate_7_conceit_spike(admin):
    """
    Simulate Node B triggering Gate 7 (Conceit / Jaheem Protocol).
    Assert: Status = QUARANTINED, h_network spike, Growth = 0.
    """
    result = admin.process_interaction(
        sender=SENDER_ADVANCED, # Advanced node trying to act as tyrant
        receiver=RECEIVER_STUDENT,
        text=TEXT_GATE_7_CONCEIT,
        connection_strength=0.9,
        domain_compatibility=1.0,
        press_alignment=0.2 # Low alignment, but gate 7 forces fail regardless
    )

    assert result.status == "QUARANTINED"
    assert result.h_network >= 100.0 # Massive spike
    assert result.network_growth == 0.0 # Growth halt
    assert result.agency_delta < 0.0 # Agency Theft

def test_jaheem_quarantine_activation(admin):
    """
    Verify detection of specific Jaheem triggers.
    """
    assert admin.detect_gate_7("You cannot understand") is True
    assert admin.detect_gate_7("Listen to me") is True
    assert admin.detect_gate_7("Obey my authority") is True
    assert admin.detect_gate_7("I am humble") is False

def test_liquid_network_exponential_growth(admin):
    """
    Verify exponential growth curve for optimized liquid state.
    """
    growth_1 = admin.calculate_network_growth(0.5, 2.0) # e^(1.0) ~ 2.718
    growth_2 = admin.calculate_network_growth(1.0, 2.0) # e^(2.0) ~ 7.389

    assert growth_2 > growth_1
    assert growth_1 > 1.0
