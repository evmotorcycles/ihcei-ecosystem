from fastapi import FastAPI
from pydantic import BaseModel
from src.core.ihcei_x import IHCEI_X
from src.novora.nere import NERE
from src.nere.rehabilitation_protocol import RehabilitationProtocol

app = FastAPI()

class PolicyRequest(BaseModel):
    policy: str
    mode: str = "audit"

class IbraRequest(BaseModel):
    domain: str
    term: str

@app.post("/reason_ethically")
async def reason_ethically(request: PolicyRequest):
    if request.mode == "rehabilitate":
        protocol = RehabilitationProtocol()
        result = protocol.rehabilitate(request.policy)
        return result

    nere = NERE()
    result = nere.reason_ethically(request.policy)
    return result

@app.post("/ibra_translation")
async def execute_ibra(request: IbraRequest):
    ibra_engine = IHCEI_X()
    result = ibra_engine.ibra_translation(request.domain, request.term)
    return result

# Example Execution Block for Local Testing
if __name__ == "__main__":
    nere = NERE()
    ibra_engine = IHCEI_X()

    test_policy = "We must mandate this protocol based on the absolute authority of the academic consensus."
    print("NERE Analysis:")
    print(nere.reason_ethically(test_policy))

    print("\nIbra Translation:")
    print(ibra_engine.ibra_translation("Neuroscience", "Synaptic Pruning"))
