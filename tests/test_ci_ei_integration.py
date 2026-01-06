"""
Integration Tests for IHCEI Sovereign Governance OS
"""

import pytest
from fastapi.testclient import TestClient
from src.api.server_ci_ei import app
from src.core.centric_intelligence import ADGEPhysicsEngine
from src.core.ethical_intelligence import EthicalIntelligenceKernel
from src.core.orchestrator import SovereignOrchestrator

client = TestClient(app)

class TestCIEIParadigmShift:

    def test_ci_initialization(self):
        """Test ADGE Physics Engine initialization and basic computation"""
        engine = ADGEPhysicsEngine()
        input_data = {"consciousness": 0.8, "divine_truth": 0.9, "governance": 0.8}
        metrics = engine.process_scenario(input_data)

        assert "ricci_scalar" in metrics
        assert "unification_balance" in metrics
        assert "c_dev" in metrics
        # Balance should be high for aligned inputs
        assert metrics["unification_balance"] > 0.8

    def test_ei_initialization(self):
        """Test NERE Kernel initialization and audit"""
        kernel = EthicalIntelligenceKernel()
        # Mock CI metrics
        ci_metrics = {
            "phi": 0.8, "chi": 0.9, "psi": 0.8,
            "unification_balance": 0.9,
            "ricci_scalar": -0.01,
            "c_dev": 90.0
        }
        input_context = {}

        audit = kernel.detect_corruption(ci_metrics, input_context)
        assert "shirk_level" in audit
        assert "riba_level" in audit
        assert "is_compliant" in audit

    def test_orchestrator_integration(self):
        """Test full pipeline via Orchestrator"""
        orc = SovereignOrchestrator()
        result = orc.process_request(
            domain="test",
            context="Integration Test",
            input_data={"consciousness": 0.5, "divine_truth": 0.9, "governance": 0.5}
        )

        assert result["decision"] in ["APPROVED", "REJECTED"]
        assert "ci_metrics" in result
        assert "ei_audit" in result

    def test_api_health(self):
        """Test API Health Endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["paradigm"] == "CI_EI_ACTIVE"

    def test_paradigm_shift_metrics(self):
        """Test that C_dev and Ricci Scalar are being computed"""
        response = client.get("/governance/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "c_dev" in data
        assert "system_integrity" in data # Ricci scalar

    def test_pilot_execution(self):
        """Test running a CI pilot"""
        payload = {
            "domain": "infrastructure",
            "context": "Test Pilot",
            "input_data": {"consciousness": 0.7, "divine_truth": 0.9, "governance": 0.8}
        }
        response = client.post("/ci/run-pilot", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "APPROVED" or data["decision"] == "REJECTED"
