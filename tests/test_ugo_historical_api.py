
import pytest
from fastapi.testclient import TestClient
from src.api.ugo_historical_simulation import app, generate_historical_millat
import numpy as np

client = TestClient(app)

class TestUGOHistoricalAPI:
    def test_historical_simulation_endpoint_pharaoh(self):
        """
        Verify that the historical simulation endpoint correctly processes a 'Pharaoh' scenario
        and returns a collapse warning due to high friction.
        """
        payload = {
            "event_name": "Pharaonic Collapse",
            "historical_utility_u": 1000000000.0, # Massive resources
            "mulk_tensor_input": [1.0] * 10,
            "millat_corruption_noise": 8.0 # High corruption
        }

        response = client.post("/simulate/historical_case", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["historical_event"] == "Pharaonic Collapse"

        # Verify collapse warning
        assert "CRITICAL" in data["ihcei_diagnostic"]

        # Verify physics output
        physics = data["adge_physics_output"]
        friction = float(physics["Systemic Friction (h_net)"].replace(",", ""))
        assert friction > 100.0

    def test_historical_simulation_endpoint_abraham(self):
        """
        Verify that the endpoint correctly processes an 'Abraham' scenario (stable).
        """
        payload = {
            "event_name": "Abrahamic Stability",
            "historical_utility_u": 1000.0,
            "mulk_tensor_input": [1.0] * 10,
            "millat_corruption_noise": 0.0 # Pure
        }

        response = client.post("/simulate/historical_case", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["ihcei_diagnostic"] == "System Stable."
        physics = data["adge_physics_output"]
        assert float(physics["Discipline (D)"]) == 1.0

    def test_generate_historical_millat(self):
        """
        Verify helper function logic.
        """
        # Case 1: Pure
        matrix_pure = generate_historical_millat(0.0)
        assert np.array_equal(matrix_pure, np.eye(10))

        # Case 2: Corrupted
        matrix_corrupt = generate_historical_millat(5.0)
        assert not np.array_equal(matrix_corrupt, np.eye(10))
        # Ensure it's still 10x10
        assert matrix_corrupt.shape == (10, 10)
