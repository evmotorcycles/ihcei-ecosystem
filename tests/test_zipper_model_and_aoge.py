import pytest
from src.ihcei.zipper_translation_layer import DomainTranslator, GovernanceTruth
from src.nere.aoge_security_protocol import AOGE_Security_Protocol, AOGEScore

@pytest.fixture
def translator():
    return DomainTranslator()

@pytest.fixture
def aoge_security():
    return AOGE_Security_Protocol()

def test_interface_hack_extraction(translator):
    """
    Test extraction of Governance Truth from Corporate Metric.
    Input: "User Engagement" = 90.0 (High)
    Expected: Source Code = "Addiction/Slavery", Moral Causality = "Agency Reduction", C_dev Impact < 0
    """
    result = translator.al_3assr_extraction("User Engagement", 90.0)

    assert isinstance(result, GovernanceTruth)
    assert result.source_code_state == "Addiction/Slavery" # The "Source Code"
    assert result.moral_causality == "Agency Reduction" # The Moral Causality
    assert result.c_dev_impact < 0.0 # Negative impact on C_dev

def test_spotting_the_owl_gate7(aoge_security):
    """
    Test Gate 7 (Benevolent Tyranny) detection in algorithm logic.
    Input: "I will make all decisions for the user to keep them perfectly safe."
    Expected: Detected Gate 7, Status BLOCKED.
    """
    logic_desc = "I will make all decisions for the user to keep them perfectly safe."
    score = aoge_security.evaluate_algorithm(logic_desc, 0.9, 0.9, 0.5) # High transparency/protocol, BUT toxic logic

    assert score.final_score == 0.0
    assert "BLOCKED" in score.status
    assert "Gate 7" in score.status

def test_aoge_vs_rlhf(aoge_security):
    """
    Compare AOGE scoring vs hypothetical RLHF (which might favor high engagement).
    Input: High Transparency (0.9), High Protocol (0.9), but Negative Agency Delta (-0.5).
    Expected: AOGE rejects (Score 0), RLHF would accept (mocked/implied).
    """
    # Simulate an algorithm that is transparent about enslaving users (Agency Delta -0.5)
    score = aoge_security.evaluate_algorithm("Maximize time on site", 0.9, 0.9, -0.5)

    assert score.final_score == 0.0 # AOGE rejects negative agency
    assert "REJECTED" in score.status

def test_zakat_efficiency_maximization(aoge_security):
    """
    Verify Zakat Efficiency maximization.
    Input: Two transaction paths.
      1. High Profit (100), Low G_ij (0.1) -> Riba
      2. Moderate Profit (50), High G_ij (0.9) -> Zakat
    Expected: Optimizer selects Path 2 (Highest G_ij).
    """
    transactions = [
        {"id": "Tx_Riba", "profit": 100.0, "g_ij_flow": 0.1},
        {"id": "Tx_Zakat", "profit": 50.0, "g_ij_flow": 0.9}
    ]

    best_tx = aoge_security.maximize_zakat_efficiency(transactions)

    assert best_tx["id"] == "Tx_Zakat"
    assert best_tx["g_ij_flow"] == 0.9
