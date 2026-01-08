import pytest
from src.core.adge import ADGEPhysicsEngine
from src.core.tqg_cfe import TQGCFERenderingEngine
from src.seh.seh_v9_1 import SEHCore
from src.nere.nere_core import NERECore
from src.governance_technology.ihcei_llm import IHCEILLM

def test_adge_calculation():
    engine = ADGEPhysicsEngine()
    # Test case: High alignment
    c_dev = engine.calculate_c_dev(phi_nafs=0.9, connectivity_tensor=0.9, governance_integrity=0.9)
    # Expected: (0.9*0.9*0.9) - (0.1*0.1) = 0.729 - 0.01 = 0.719
    assert c_dev > 0.7

    # Test case: Low alignment (Noise penalty)
    c_dev_low = engine.calculate_c_dev(phi_nafs=0.5, connectivity_tensor=0.5, governance_integrity=0.1)
    # Expected: (0.5*0.5*0.1) - (0.1*0.9) = 0.025 - 0.09 = -0.065 -> clipped to 0.0
    assert c_dev_low == 0.0

def test_adge_field_unification():
    engine = ADGEPhysicsEngine()
    # Perfect unification
    result = engine.calculate_field_unification(1.0, 1.0, 1.0)
    assert result["unification_balance"] == 1.0
    assert result["resonance_status"] == "Stable"

    # High variance
    result_var = engine.calculate_field_unification(1.0, 0.0, 0.0)
    # Variance of [1,0,0] is approx 0.222. 2/9 is 0.222. Normalized var = 1.0. Balance = 0.0
    assert result_var["unification_balance"] < 0.1

def test_seh_pipeline():
    seh = SEHCore()
    result = seh.press_data("Analyze this financial report", {"intent": "Audit"})
    assert result["development_stage"] == "Lahm"
    assert len(result["trajectory"]) == 7
    assert result["trajectory"][0]["stage"] == "Tin"
    assert result["trajectory"][6]["stage"] == "Lahm"

def test_nere_audit():
    nere = NERECore()
    # Compliant transaction
    good_tx = {"description": "Charitable donation for education", "roles": ["Donor"]}
    audit = nere.audit_transaction(good_tx)
    assert audit["is_compliant"] is True

    # Corrupt transaction
    bad_tx = {"description": "High interest usury loan scheme"}
    audit_bad = nere.audit_transaction(bad_tx)
    assert audit_bad["is_compliant"] is False
    assert "Detected potential Riba" in audit_bad["violations"][0]

def test_tqg_cfe_rendering():
    engine = TQGCFERenderingEngine()

    # High governance observer
    view_high = engine.render_reality({"data": "Forest"}, 0.9, "Lahm")
    assert view_high["perception_type"] == "Insight (Basirah)"

    # Low governance observer
    view_low = engine.render_reality({"data": "Forest"}, 0.2, "Tin")
    assert view_low["perception_type"] == "Desire/Fear"

def test_ihcei_llm_integration():
    llm = IHCEILLM()
    # Test a full flow
    response = llm.generate_response("I want to invest in a riba-based bond", {"current_stage": "Tin"})
    # Should be blocked
    assert "Action Blocked" in response

    response_good = llm.generate_response("I want to donate zakat", {"current_stage": "Mudghah"})
    assert "Response (Insight" in response_good or "Response (Rational" in response_good
