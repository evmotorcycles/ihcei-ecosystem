
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.qg_cos_engine.core.abm_network import ABMNetworkEngine
from src.qg_cos_engine.core.bayesian_kernel import ConflatedQalb, OrthogonalQalb, BiDimensionalBarad

app = FastAPI(title="QG-COS Forensic Audit API (v1.0 RC)", version="1.0")

class SimulationConfig(BaseModel):
    event_name: str = "Forensic Audit"
    U_environmental: float = 1000.0
    D_base: float = 1.0
    millat_noise: float = 0.5
    tyrant_siphon_rate: float = 0.1
    epochs: int = 6
    deploy_nere_epoch: int = 3
    deploy_huqooq_epoch: int = 4
    num_agents: int = 50000

@app.post("/api/v1/network/simulate-recovery")
def simulate_recovery(config: SimulationConfig) -> Dict[str, Any]:
    """
    Endpoint 1: Macro-Civilizational Audit.
    Runs the 50k node simulation using DualRecoveryEngine logic (wrapped in ABMNetworkEngine).
    """
    try:
        engine = ABMNetworkEngine(config.model_dump())
        time_series = engine.run_simulation()
        final_log = time_series[-1]

        return {
            "event": config.event_name,
            "timeline": time_series,
            "final_diagnostic": {
                "Jahannam_Proximity_Index": final_log["Jahannam_Proximity_Index"],
                "Kanz_Readiness": final_log["Kanz_Readiness"],
                "Status": final_log["system_status"],
                "Narrative": final_log["narrative"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/kernel/conflation-audit")
def conflation_audit(packets: List[BiDimensionalBarad]) -> Dict[str, Any]:
    """
    Endpoint 2: Micro-Epistemic Conflation Audit.
    Compares Rank-1 (Conflated) vs Rank-2 (Orthogonal) processing of Barad packets.
    """
    try:
        rank1_kernel = ConflatedQalb()
        rank2_kernel = OrthogonalQalb()

        results = []
        for packet in packets:
            r1 = rank1_kernel.process_packet(packet)
            r2 = rank2_kernel.process_packet(packet)

            # Calculate comparative metrics
            # Friction Spike: R1 friction / R2 friction
            friction_spike = r1["friction_hbar"] / r2["friction_hbar"] if r2["friction_hbar"] > 0 else 0.0

            # ADGE Efficiency: R1 D / R2 D (Ratio of discipline)
            adge_efficiency = r1["d_effective"] / r2["d_effective"] if r2["d_effective"] > 0 else 0.0

            results.append({
                "input": packet.model_dump(),
                "rank1_conflated": r1,
                "rank2_orthogonal": r2,
                "comparative_metrics": {
                    "hbar_friction_spike": friction_spike,
                    "adge_efficiency_ratio": adge_efficiency
                }
            })

        return {
            "audit_summary": "Conflation Audit Complete",
            "packet_analysis": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
