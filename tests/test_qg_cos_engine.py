
import pytest
import numpy as np
from fastapi.testclient import TestClient
from src.api.forensic_audit_api import app
from src.qg_cos_engine.recovery_engine import DualRecoveryEngine

client = TestClient(app)

class TestQGCOSEngine:
    def test_pharaonic_collapse(self):
        """
        Test Case 1: Pharaonic Collapse.
        High Rational Over-pressure (Noise > 0.8), No NERE intervention.
        Assert E -> 0 and JPI increases.
        """
        config = {
            "U_environmental": 1000.0,
            "D_base": 1.0,
            "millat_noise": 2.0, # High Noise
            "tyrant_siphon_rate": 0.1,
            "epochs": 3,
            "deploy_nere_epoch": 10, # Never deploy
            "deploy_huqooq_epoch": 10,
            "num_agents": 5000 # Reduced for testing speed
        }

        engine = DualRecoveryEngine(config)
        logs = engine.run()

        # Check Epoch 3
        last_log = logs[-1]
        assert last_log["epoch"] == 3
        # JPI should be high (Collapse)
        assert last_log["Jahannam_Proximity_Index"] > 0.8
        # Essence should be low
        assert last_log["mean_essence_E"] < 100.0

    def test_abrahamic_recovery(self):
        """
        Test Case 2: Abrahamic Recovery.
        Deploy NERE at Epoch 3.
        Assert JPI decreases post-intervention.
        """
        config = {
            "U_environmental": 1000.0,
            "D_base": 1.0,
            "millat_noise": 2.0,
            "tyrant_siphon_rate": 0.1,
            "epochs": 6,
            "deploy_nere_epoch": 3,
            "deploy_huqooq_epoch": 4,
            "num_agents": 5000 # Reduced for testing speed
        }

        engine = DualRecoveryEngine(config)
        logs = engine.run()

        # Pre-intervention (Epoch 2)
        jpi_pre = logs[1]["Jahannam_Proximity_Index"]

        # Post-intervention (Epoch 6)
        jpi_post = logs[5]["Jahannam_Proximity_Index"]

        # Recovery should occur
        assert jpi_post < jpi_pre
        assert logs[5]["system_status"] == "STABLE"

    def test_api_endpoint(self):
        """Verify API connectivity and schema."""
        payload = {
            "event_name": "Test Event",
            "U_environmental": 1000.0,
            "D_base": 1.0,
            "millat_noise": 0.5,
            "tyrant_siphon_rate": 0.1,
            "epochs": 6,
            "deploy_nere_epoch": 3,
            "deploy_huqooq_epoch": 4,
            "num_agents": 1000 # Minimal for API test
        }
        response = client.post("/api/v1/forensic-audit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "simulation_log" in data
        assert len(data["simulation_log"]) == 6
