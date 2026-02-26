
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestFinalSystem:
    def test_conflation_audit_dimensionality_collapse(self):
        """
        Verify that P1_SYNTAX_HIGH_PROTOCOL_ZERO causes D_effective -> 0.00 in Rank-1 kernel.
        """
        payload = [
            {"syntax_delta": 0.9, "protocol_delta": 0.0}
        ]

        response = client.post("/api/v1/kernel/conflation-audit", json=payload)
        assert response.status_code == 200
        data = response.json()

        result = data["packet_analysis"][0]
        rank1 = result["rank1_conflated"]
        rank2 = result["rank2_orthogonal"]

        # Assert Rank-1 Collapse (Dimensionality Bug active)
        assert rank1["d_effective"] == 0.0
        assert rank1["recursive_loop_depth"] == 100
        assert rank1["friction_hbar"] == 1000.0

        # Assert Rank-2 Stability (Orthogonality preserved, even if value is low)
        # Sqrt(0.9 * 0) = 0. But friction should be low.
        assert rank2["d_effective"] == 0.0
        assert rank2["friction_hbar"] == 0.1 # Low friction

        # Assert Spike
        metrics = result["comparative_metrics"]
        assert metrics["hbar_friction_spike"] > 100.0

    def test_macro_audit_simulation(self):
        """
        Verify the 50k node macro-audit endpoint.
        """
        config = {
            "event_name": "Final System Test",
            "U_environmental": 1000.0,
            "D_base": 1.0,
            "millat_noise": 0.5,
            "tyrant_siphon_rate": 0.1,
            "epochs": 6,
            "deploy_nere_epoch": 3,
            "deploy_huqooq_epoch": 4,
            "num_agents": 1000 # Reduced for test speed
        }

        response = client.post("/api/v1/network/simulate-recovery", json=config)
        assert response.status_code == 200
        data = response.json()

        assert data["event"] == "Final System Test"
        assert len(data["timeline"]) == 6
        assert "Narrative" in data["final_diagnostic"]
