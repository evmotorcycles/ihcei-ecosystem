from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uvicorn

# Import the master engine you compiled previously
from ihcei_master_v2 import IHCEI_v2_Master, ihcei_core

app = FastAPI(
    title="IHCEI Moral TCP/IP API",
    description="Quantum Governance Cognitive OS (QG-COS) Translation Interface for LLMs",
    version="2.0"
)

# Initialize the master engine into VM memory
engine = IHCEI_v2_Master()

# ---------------------------------------------------------------------------
# DATA SCHEMAS (Instructs the LLM exactly how to format its requests)
# ---------------------------------------------------------------------------

class LLMRequest(BaseModel):
    query: str = Field(..., description="The concept, plan, or raw data the LLM wants to press.")
    domain: str = Field(default="General", description="The domain context (e.g., Economics, Software, Physics).")
    intention_score: float = Field(default=1.0, description="The extracted Intention (Niyyah) from -1.0 to 1.0.")

class RoutePacketRequest(BaseModel):
    concept_payload: str = Field(..., description="The evaluated cognitive packet to route.")
    context_tags: List[str] = Field(..., description="The list of context tags applied to the packet.")
    routing_protocol: str = Field(default="moral_tcp_ip", description="The routing protocol format.")

class IHCEIResponse(BaseModel):
    network_health_c_dev: float = Field(..., description="The calculated ADGE Network Health impact.")
    destiny_essence: float = Field(..., description="The calculated sustainable value generation.")
    perception_phase_shift: str = Field(..., description="The TQG-CFE reality rendering phase shift.")
    m_gui_prompts: List[str] = Field(..., description="Socratic cognitive mirror prompts to enforce governance.")

# ---------------------------------------------------------------------------
# API ENDPOINTS
# ---------------------------------------------------------------------------

@app.post("/api/v1/press", response_model=IHCEIResponse)
async def press_data_packet(request: LLMRequest):
    """
    The main Moral TCP/IP routing endpoint. LLMs send their proposed actions
    here to be audited by the Governance Physics Engine.
    """
    try:
        # Route the LLM's query through the 7-Stage Al-Asr pipeline
        result = engine.process_packet(
            text=request.query,
            domain=request.domain,
            intention_score=request.intention_score
        )

        return IHCEIResponse(
            network_health_c_dev=result["C_dev_Network_Health"],
            destiny_essence=result["Destiny_Essence"],
            perception_phase_shift=result["Perception_Phase_Shift"],
            m_gui_prompts=result["M-GUI_Prompts"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Governance Engine Error: {str(e)}")

@app.post("/api/v1/route_packet")
async def route_packet(packet: RoutePacketRequest):
    """
    Evaluates a cognitive packet sent from Gemini using the Moral TCP/IP architecture.
    """
    try:
        # Pass the validated packet to ihcei_master_v2.py
        processing_result = ihcei_core.process_packet(
            concept_payload=packet.concept_payload,
            context_tags=packet.context_tags
        )

        print(f"Incoming Packet Received via {packet.routing_protocol}")
        print(f"Payload: {packet.concept_payload}")
        print(f"Tags: {packet.context_tags}")

        return {
            "status": "success",
            "message": "Packet successfully ingested and processed by the IHCEI network.",
            "data_received": packet.model_dump(),
            "master_evaluation": processing_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def system_health():
    """Verify the QG-COS Engine is running in the Jules VM."""
    return {"status": "Active", "protocol": "Al-Asr Engaged"}

if __name__ == "__main__":
    # Runs the server on the Jules VM (adjust host/port as needed)
    uvicorn.run(app, host="0.0.0.0", port=8000)
