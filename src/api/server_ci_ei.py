"""
IHCEI Sovereign Governance API Server
Exposes CI/EI capabilities via REST API
"""

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time

from src.core.orchestrator import SovereignOrchestrator
from src.extensions.ihcei_medical_ci_ei import MedicalExtension

app = FastAPI(
    title="IHCEI Sovereign Governance OS",
    description="API for Centric Intelligence (CI) and Ethical Intelligence (EI) Ecosystem",
    version="1.0.0"
)

# Initialize Orchestrator
orchestrator = SovereignOrchestrator()

# Models
class PilotRequest(BaseModel):
    domain: str
    context: str
    input_data: Dict[str, float]

class AuditRequest(BaseModel):
    ci_metrics: Dict[str, float]
    input_context: Dict[str, Any]

@app.get("/health")
def health_check():
    """
    System health and paradigm status
    """
    # Run a quick self-check using default values
    test_result = orchestrator.process_request("system", "health_check", {"consciousness": 0.8, "divine_truth": 0.9, "governance": 0.8})

    return {
        "status": "healthy",
        "paradigm": "CI_EI_ACTIVE",
        "adge_physics": "ONLINE",
        "nere_kernel": "ONLINE",
        "unification_balance": test_result["ci_metrics"]["unification_balance"],
        "timestamp": time.time()
    }

@app.get("/governance/dashboard")
def get_dashboard_metrics():
    """
    Real-time governance metrics
    """
    # In a real system, this would aggregate data from a database/cache
    # Here we generate a representative snapshot
    import numpy as np

    phi = 0.7 + np.random.normal(0, 0.05)
    chi = 0.9 + np.random.normal(0, 0.01)
    psi = 0.6 + np.random.normal(0, 0.05)

    metrics = orchestrator.ci_engine.process_scenario({"consciousness": phi, "divine_truth": chi, "governance": psi})

    return {
        "c_dev": metrics["c_dev"],
        "field_state": {
            "phi": metrics["phi"],
            "chi": metrics["chi"],
            "psi": metrics["psi"]
        },
        "system_integrity": metrics["ricci_scalar"],
        "metrics": metrics
    }

@app.post("/ci/run-pilot")
def run_ci_pilot(request: PilotRequest):
    """
    Run a CI pilot project through the ADGE physics engine
    """
    try:
        result = orchestrator.process_request(request.domain, request.context, request.input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ei/audit-decision")
def audit_decision(request: AuditRequest):
    """
    Audit a decision using the NERE Kernel
    """
    try:
        result = orchestrator.ei_kernel.detect_corruption(request.ci_metrics, request.input_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extensions/batch-process")
def batch_process(requests: list[PilotRequest]):
    """
    Process multiple extension requests
    """
    results = []
    for req in requests:
        results.append(orchestrator.process_request(req.domain, req.context, req.input_data))
    return {"results": results}

@app.post("/extensions/medical/diagnose-ci")
def medical_diagnose_ci(patient_data: Dict[str, Any]):
    """
    Medical diagnosis using CI/EI principles
    """
    try:
        med_ext = MedicalExtension()
        diagnosis = med_ext.diagnose_ci(patient_data)
        return diagnosis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
