"""
novora_regime_router.py — Novora Governance Gateway · Two-Regime endpoints
==========================================================================
GT v18.1 add-on router for ihcei_api.py (the Novora Gateway). Mount with:

    try:
        from novora_regime_router import regime_router
        app.include_router(regime_router)
    except ImportError:
        pass

Endpoints (all Layer 1/2; none claims L3):
  POST /v1/regime/classify   — Gate 0: classify a channel's role
  POST /v1/regime/predict_e  — E under the regime's OWN law (refuses mismatches)
  POST /v1/regime/diagnose   — read a fitted exponent as a regime signature
  POST /v1/regime/ledger     — correction-capacity accounting (UPSTREAM-D alarm)
  GET  /v1/regime/status     — laws, epistemic statuses, ledger, locked predictions

Design contract: the gateway REFUSES category errors (HTTP 422 with the
reason) instead of committing them — the API-level embodiment of the
judicial-campaign lesson.
"""
from __future__ import annotations
from typing import List, Optional

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field
    _FASTAPI = True
except ImportError:  # graceful degradation, mirroring ihcei_api.py
    _FASTAPI = False

    class BaseModel:            # minimal stubs so the module still imports
        pass

    def Field(default=None, **kw):
        return default

import gt_regimes as gr
from nere_engine import CorrectionCapacityLedger


# ── request/response models ──────────────────────────────────────────────────
class ClassifyReq(BaseModel):
    role_description: str = ""
    declared: Optional[str] = Field(
        None, description="explicit regime declaration; overrides the heuristic")


class PredictEReq(BaseModel):
    U: float
    regime: str
    D: Optional[float] = None
    D_in: Optional[float] = None
    q: Optional[float] = None
    kappa: float = 1.0


class DiagnoseReq(BaseModel):
    k_hat: float
    ci_low: float
    ci_high: float
    inversion_observed: Optional[bool] = None
    dead_D: bool = False


class LedgerWindow(BaseModel):
    window_id: str
    influx: int
    repaired: int
    inspected_clean: int = 0
    non_engaged: int = 0


class LedgerReq(BaseModel):
    windows: List[LedgerWindow]
    alarm_windows: int = 3


# ── router ───────────────────────────────────────────────────────────────────
if _FASTAPI:
    regime_router = APIRouter(prefix="/v1/regime", tags=["two-regime (GT v18.1)"])

    @regime_router.post("/classify")
    async def classify(req: ClassifyReq):
        dec = gr.Regime(req.declared.upper()) if req.declared else None
        try:
            return gr.classify_channel(req.role_description, declared=dec).to_dict()
        except ValueError as e:
            raise HTTPException(422, str(e))

    @regime_router.post("/predict_e")
    async def predict_e(req: PredictEReq):
        try:
            out = gr.predict_E(U=req.U, regime=gr.Regime(req.regime.upper()),
                               D=req.D, D_in=req.D_in, q=req.q, kappa=req.kappa)
            return out.to_dict()
        except (gr.RegimeError, ValueError) as e:
            # refusal is the feature: category errors return 422 + reason
            raise HTTPException(422, str(e))

    @regime_router.post("/diagnose")
    async def diagnose(req: DiagnoseReq):
        return gr.diagnose_exponent(req.k_hat, (req.ci_low, req.ci_high),
                                    inversion_observed=req.inversion_observed,
                                    dead_D=req.dead_D)

    @regime_router.post("/ledger")
    async def ledger(req: LedgerReq):
        led = CorrectionCapacityLedger(alarm_windows=req.alarm_windows)
        status = {}
        for w in req.windows:
            status = led.record(w.window_id, w.influx, w.repaired,
                                w.inspected_clean, w.non_engaged)
        return status

    @regime_router.get("/status")
    async def status():
        return {
            "gt_version": "v18.1 (Two-Regime Addendum)",
            "laws": {r.value: {"form": v["form"],
                               "status": v["status"].value,
                               "reading": v["reading"]}
                     for r, v in gr.LAWS.items()},
            "quadratic": gr.QUADRATIC_NOTE,
            "empirical_ledger": gr.EMPIRICAL_LEDGER,
            "locked_predictions": gr.preregistered_predictions(),
            "module_sha256": gr.spec_sha(),
        }
else:
    regime_router = None
