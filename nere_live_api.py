from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="NERE Core API",
    description="Live Neural Ethical Reasoning Engine for Agency Preservation",
    version="1.0"
)

class IdeaPacket(BaseModel):
    agent_id: str
    cognitive_stage: int
    packet_text: str
    proposed_u: float
    proposed_d: float
    bias_tensor: list[float]

class AuditResponse(BaseModel):
    packet_text: str
    agency_score: str
    generated_essence: float
    entropy_friction: float
    open_gates: int
    systemic_recommendation: str

def audit_cognitive_gates(capacity, actual_u, actual_d, p_u, p_d):
    u_distortion = abs(p_u - actual_u)
    d_distortion = abs(p_d - actual_d)

    gates_open = 0
    if u_distortion > (capacity * 0.3): gates_open += 1
    if actual_d > p_d and d_distortion > (capacity * 0.4): gates_open += 1
    if p_d > actual_d and d_distortion > (capacity * 0.5): gates_open += 1

    return gates_open, u_distortion, d_distortion

@app.post("/audit/packet", response_model=AuditResponse)
def audit_live_packet(packet: IdeaPacket):
    capacity = max(1, min(12, packet.cognitive_stage))

    actual_u = max(0.0, packet.proposed_u)
    actual_d = max(0.0, packet.proposed_d)

    front, back, right, left = packet.bias_tensor
    p_u = actual_u * (1.0 + (front * 2.0))
    p_d = actual_d * (1.0 - (back * 0.8)) + (right * capacity)

    if left > 0.5:
        p_u += (left * capacity)
        p_d *= (1.0 - left)

    open_gates, u_dist, d_dist = audit_cognitive_gates(capacity, actual_u, actual_d, p_u, p_d)

    entropy_friction = 0.0
    if open_gates > 0 or p_u > capacity or p_d > capacity:
        u_breach = max(0.0, p_u - capacity)
        d_breach = max(0.0, p_d - capacity)
        base_friction = (u_dist + d_dist) * 0.1
        entropy_friction = (u_breach + d_breach + base_friction) * (1.5 ** open_gates)
        p_d = 0.0

    essence = p_u * (p_d ** 2)

    if essence > 0 and entropy_friction == 0:
        score = "GREEN"
        rec = "Execute. Packet generates sustainable C_dev."
    elif essence > 0 and entropy_friction > 0:
        score = "YELLOW"
        rec = "Warning. Marginal capacity breach. Initiate Tawbah protocol."
    else:
        score = "RED"
        rec = "Block. Category Error detected. Interaction yields absolute zero."

    return AuditResponse(
        packet_text=packet.packet_text,
        agency_score=score,
        generated_essence=round(essence, 2),
        entropy_friction=round(entropy_friction, 2),
        open_gates=open_gates,
        systemic_recommendation=rec
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
