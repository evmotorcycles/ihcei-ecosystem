import sys
import os
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

# Add parent directory to path to import nere_pilot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import nere_pilot

@pytest.fixture
def sample_dataset():
    """Fixture to provide a sample dataset."""
    return pd.DataFrame({
        'user_id': [1, 2, 3],
        'outstanding_debt_ugx': [10000.0, 20000.0, 30000.0],
        'days_in_default': [30, 60, 90]
    })

@patch('nere_pilot.SentenceTransformer')
@patch('nere_pilot.RandomForestClassifier')
def test_nere_auditor_init(mock_rfc, mock_st):
    """Test NERE_Auditor initialization with mocked SentenceTransformer."""
    # Setup mocks
    mock_model = MagicMock()
    mock_st.return_value = mock_model
    # Mock encode to return a dummy 2D array for the training step
    # There are 6 training texts in _train_nere_kernel
    # We return a numpy array of shape (6, 10)
    mock_model.encode.return_value = np.zeros((6, 10))

    auditor = nere_pilot.NERE_Auditor()

    # Verify SentenceTransformer was loaded with correct model
    mock_st.assert_called_with('all-MiniLM-L6-v2')
    # Verify encode was called (at least once for training)
    assert mock_model.encode.called
    # Verify model.fit was called
    assert mock_rfc.return_value.fit.called

def test_execute_pilot_math(sample_dataset):
    """Test the E = U * D^2 logic in execute_pilot."""
    # Verify the E = U * D^2 logic

    # Mock the NERE_Auditor
    mock_auditor = MagicMock()

    # Define behavior for audit_communication
    # First call (Standard Prompt): Returns trad_class, trad_prob
    # Second call (NERE Prompt): Returns nere_class, nere_prob
    # Let's say:
    # trad_prob = 0.1
    # nere_prob = 0.8
    mock_auditor.audit_communication.side_effect = [
        ("RED", 0.1),   # Traditional
        ("GREEN", 0.8)  # NERE
    ]

    traditional_prompt = "pay now"
    nere_prompt = "let's help"

    nere_pilot.execute_pilot(sample_dataset, mock_auditor, traditional_prompt, nere_prompt)

    # Check calculations
    # U = outstanding_debt_ugx
    # E_Trad = U * (trad_prob + 0.3)^2 = U * (0.1 + 0.3)^2 = U * 0.16
    # E_NERE = U * (nere_prob)^2 = U * (0.8)^2 = U * 0.64

    expected_trad_factor = (0.1 + 0.3) ** 2
    expected_nere_factor = (0.8) ** 2

    # We check the first row for example
    u_val = 10000.0
    expected_trad = u_val * expected_trad_factor
    expected_nere = u_val * expected_nere_factor

    actual_trad = sample_dataset.iloc[0]['E_Trad_Recovered']
    actual_nere = sample_dataset.iloc[0]['E_NERE_Recovered']

    # Using pytest.approx for float comparison
    assert actual_trad == pytest.approx(expected_trad, rel=1e-5)
    assert actual_nere == pytest.approx(expected_nere, rel=1e-5)

    # Verify entire columns
    pd.testing.assert_series_equal(
        sample_dataset['E_Trad_Recovered'],
        sample_dataset['U_Raw_Utility'] * expected_trad_factor,
        check_names=False
    )
    pd.testing.assert_series_equal(
        sample_dataset['E_NERE_Recovered'],
        sample_dataset['U_Raw_Utility'] * expected_nere_factor,
        check_names=False
    )
