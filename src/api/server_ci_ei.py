from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.core.orchestrator import SovereignOrchestrator

app = FastAPI(title="IHCEI Ecosystem API", version="1.0.0")

orchestrator = SovereignOrchestrator()

class QueryRequest(BaseModel):
    text: str
    user_id: str
    context: Optional[Dict[str, Any]] = {}

class QueryResponse(BaseModel):
    response: str
    details: Dict[str, Any]

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sovereign Operating System API"}

@app.post("/process", response_model=QueryResponse)
def process_query(request: QueryRequest):
    try:
        # Enrich context with defaults if missing
        context = request.context or {}
        if "phi_nafs" not in context:
            context["phi_nafs"] = 0.5
        if "current_stage" not in context:
            context["current_stage"] = "Nutfah" # Default learning stage

        result = orchestrator.process(request.text, context)

        return QueryResponse(
            response=result["response"],
            details=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
