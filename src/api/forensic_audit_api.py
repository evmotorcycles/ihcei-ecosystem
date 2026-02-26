
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.qg_cos_engine.recovery_engine import DualRecoveryEngine

app = FastAPI(title="QG-COS Forensic Audit API", version="1.0")

class ForensicAuditRequest(BaseModel):
    event_name: str
    U_environmental: float
    D_base: float
    millat_noise: float
    tyrant_siphon_rate: float
    epochs: int
    deploy_nere_epoch: int
    deploy_huqooq_epoch: int
    num_agents: int = 50000

@app.post("/api/v1/forensic-audit")
def run_forensic_audit(payload: ForensicAuditRequest) -> Dict[str, Any]:
    """
    Executes a Historical Forensic Audit using the QG-COS Dual Recovery Engine.
    Returns a 6-Epoch Time-Series Log of thermodynamic collapse/recovery.
    """
    try:
        config = payload.model_dump()
        engine = DualRecoveryEngine(config)

        # Run Simulation
        time_series = engine.run()

        # Extract Final Metrics
        final_log = time_series[-1]

        return {
            "event": payload.event_name,
            "simulation_log": time_series,
            "final_diagnostic": {
                "Jahannam_Proximity_Index": final_log["Jahannam_Proximity_Index"],
                "Kanz_Readiness": final_log["Kanz_Readiness"],
                "Status": final_log["system_status"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
