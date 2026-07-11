"""
ihcei_gateway.py — IHCEI Governance Gateway v3.0 (GT v18.2)
============================================================
Self-hostable API for the between-LLMs governance layer.

Run:    pip install fastapi uvicorn
        uvicorn ihcei_gateway:app --host 0.0.0.0 --port 8080

Endpoints:
  GET  /health                     liveness + law registry status
  GET  /v3/registry                full law registry (retirements visible)
  POST /v3/audit                   {text, direction?, channel?, d_gap?}
                                   -> combined IHCEI + NERE probabilistic audit
  POST /v3/nere                    {text, prior_p?} -> NERE verdict only
  POST /v3/kernel                  {text, channel?, d_gap?} -> kernel verdict only
  GET  /v3/ledger                  session ledger + upstream alarm
  POST /v3/channel/update          {channel, failures, successes}
                                   -> conjugate Bayesian prior update

Design contract (the agency paradigm):
  - The gateway NEVER mutates content. It returns verdicts, posteriors,
    credible intervals, correction pathways, and certificates.
  - HOLD is advice with evidence attached; release authority stays with
    the caller. There is no endpoint that suppresses content server-side.
  - Every probability lives in [0.01, 0.99]. No endpoint can return
    certainty. E=U*D^2 and D_min are RETIRED_FULLY and unreachable.
"""

from __future__ import annotations
import os
from typing import Optional

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError as e:  # pragma: no cover
    raise SystemExit("pip install fastapi uvicorn pydantic") from e

from gt_probabilistic import LAW_REGISTRY, CHANNEL_PRIORS
from ihcei_middleware import GovernanceMiddleware
from ihcei_kernel_v3 import IHCEIKernelV3
from nere_engine_v3 import NEREEngineV3
from nere_deep import AnthropicDeepExtractor

app = FastAPI(title="IHCEI Governance Gateway", version="3.1.0",
              description="Probabilistic governance middleware — sits between "
                          "LLMs and humans. GT v18.2, null-result pivot. "
                          "Fast (regex) and deep (semantic) evidence, one math.")

_mw = GovernanceMiddleware(channel="oss_default")

# Deep mode: built lazily, only if a key is present in the host env. Absent a
# key the gateway still serves fast mode fully — deep is an evidence upgrade,
# not a dependency. The key never leaves the host (self-hosted contract).
def _deep_extractor() -> Optional[AnthropicDeepExtractor]:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    return AnthropicDeepExtractor(api_key=key, ca_bundle=ca)


class AuditIn(BaseModel):
    text: str
    direction: str = "outbound"
    channel: Optional[str] = None
    d_gap: float = 0.0

class NereIn(BaseModel):
    text: str
    prior_p: float = 0.10
    mode: str = "fast"          # fast (regex) | deep (semantic, needs key)

class KernelIn(BaseModel):
    text: str
    channel: str = "oss_default"
    d_gap: float = 0.0

class ChannelUpdateIn(BaseModel):
    channel: str
    failures: int
    successes: int


@app.get("/health")
def health():
    return {"status": "ok", "stack": "ihcei-v3.0-probabilistic",
            "retired": [k for k, v in LAW_REGISTRY.items()
                        if v["status"] == "RETIRED_FULLY"],
            "floor": "[0.01, 0.99]"}

@app.get("/v3/registry")
def registry():
    return LAW_REGISTRY

@app.post("/v3/audit")
def audit(body: AuditIn):
    if body.channel and body.channel != _mw.kernel.channel:
        _mw.kernel.channel = body.channel if body.channel in CHANNEL_PRIORS else "oss_default"
    a = _mw.audit(body.text, direction=body.direction, d_gap=body.d_gap)
    return a.to_dict()

@app.post("/v3/nere")
def nere(body: NereIn):
    extractor = None
    engine_mode = "fast"
    if body.mode == "deep":
        extractor = _deep_extractor()
        if extractor is None:
            return {"error": "deep mode requires ANTHROPIC_API_KEY on the host; "
                             "fast mode is available with no key", "mode": "deep"}
        engine_mode = "deep"
    eng = NEREEngineV3(prior_p=body.prior_p, extractor=extractor)
    out = eng.evaluate(body.text).to_dict()
    out["engine"] = f"nere-v3-{engine_mode}"
    return out

@app.post("/v3/kernel")
def kernel(body: KernelIn):
    k = IHCEIKernelV3(channel=body.channel)
    return k.evaluate(body.text, d_gap=body.d_gap).to_dict()

@app.get("/v3/ledger")
def ledger():
    return _mw.ledger.summary()

@app.post("/v3/channel/update")
def channel_update(body: ChannelUpdateIn):
    return IHCEIKernelV3.update_channel(body.channel, body.failures, body.successes)
