from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.core.ecosystem import IHCEIEcosystem

app = FastAPI(title="IHCEI Ecosystem API")

# Initialize the ecosystem
ecosystem = IHCEIEcosystem()

class EcosystemInput(BaseModel):
    coherence: float
    alignment: float
    mass_energy: float
    radius: float

class EcosystemResponse(BaseModel):
    adge_metrics: dict
    field_potential: float
    nere_audit: dict
    status: str

@app.post("/process_state", response_model=EcosystemResponse)
async def process_state(input_data: EcosystemInput):
    """
    Process a system state through the IHCEI Ecosystem.
    """
    try:
        # Convert Pydantic model to dict
        data = input_data.dict()

        # Process through the core logic
        result = ecosystem.process_state(data)

        # Determine overall status based on NERE audit
        is_compliant = result['nere_audit']['is_compliant']
        status = "APPROVED" if is_compliant else "REJECTED"

        return {
            "adge_metrics": result['adge_metrics'],
            "field_potential": result['field_potential'],
            "nere_audit": result['nere_audit'],
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the IHCEI Ecosystem API"}
