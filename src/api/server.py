from fastapi import FastAPI
from src.core.centric_intelligence import CentricIntelligenceCore
from src.core.ethical_intelligence import EthicalIntelligenceCore

app = FastAPI()
ci = CentricIntelligenceCore()
ei = EthicalIntelligenceCore()

@app.get("/")
def read_root():
    return {"message": "IHCEI Ecosystem Online"}

@app.get("/pilot")
def run_pilot():
    result = ci.run_pilot_test("System Check", {'density': 1.0})
    return {
        "context": result.context,
        "c_dev": result.c_dev,
        "unification_balance": result.unification_balance
    }

@app.get("/audit")
def run_audit():
    # Simulate a CI result
    ci_output = {'c_dev': 100.0, 'unification_balance': 0.9}
    audit = ei.audit_decision("System Audit", ci_output)
    return audit
