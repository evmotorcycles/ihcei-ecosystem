
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.simulation.ugo import UnifiedGovernanceObject
import numpy as np

app = FastAPI(title="IHCEI Historical Simulator API", version="1.0")

# API Payload Schema
class HistoricalCaseStudy(BaseModel):
    event_name: str
    historical_utility_u: float           # e.g., GDP, Military Size, Resource Capital
    mulk_tensor_input: List[float]        # 10-Element Vector (Roles, Rules, Dues, etc.)
    millat_corruption_noise: float        # Semantic drift/ideological corruption level (0.0 = Pure, 10.0 = Total Delusion)

def generate_historical_millat(noise_level: float) -> np.ndarray:
    """
    Generates the Millat (Syntax) Matrix based on historical ideological corruption.
    Pure Millat = Identity Matrix (I).
    Corrupted Millat = I + Random Noise.
    """
    base_matrix = np.eye(10)
    if noise_level > 0.0:
        np.random.seed(42) # Seeded for historical reproducibility
        noise = np.random.uniform(0, noise_level, (10, 10))
        base_matrix += noise
    return base_matrix

@app.post("/simulate/historical_case")
def run_historical_simulation(payload: HistoricalCaseStudy) -> Dict[str, Any]:
    """
    Ingests a historical epoch or event and calculates its thermodynamic collapse or scaling
    using the Absolute Divine Governance Equation (E = U * D^2).
    """
    try:
        # Generate the Millat (Syntax) Matrix based on historical ideological corruption
        millat_matrix = generate_historical_millat(payload.millat_corruption_noise)

        # Initialize the Unified Governance Object
        case_ugo = UnifiedGovernanceObject(
            name=payload.event_name,
            mulk_tensor=np.array(payload.mulk_tensor_input),
            millat_matrix=millat_matrix,
            utility_u=payload.historical_utility_u
        )

        # Compile Reality and calculate ADGE metrics
        metrics = case_ugo.compile_reality()

        # Diagnostic Flagging
        friction_val = float(metrics["Systemic Friction (h_net)"].replace(",", ""))
        collapse_warning = "CRITICAL: Systemic Friction exceeds sustainable thresholds." if friction_val > 100.0 else "System Stable."

        return {
            "historical_event": payload.event_name,
            "adge_physics_output": metrics,
            "ihcei_diagnostic": collapse_warning
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
