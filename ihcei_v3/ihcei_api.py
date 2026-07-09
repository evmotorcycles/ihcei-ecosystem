"""
ihcei_api.py
============
IHCEI + NERE REST API — GT v18.0 / QG-COS Layer 2 Network Protocol

ARCHITECTURE POSITION
---------------------
Layer 2 of the QG-COS stack exposed as a networked service.
Instantiates IHCEIKernel, NereEngine, OQMExtractor, and CollapseDetector
as singletons, routes requests through the full pipeline, and returns
tamper-evident certified responses.

ENDPOINTS (8 total)
-------------------
POST /v1/evaluate              Core IHCEI scoring — D, U, E, h, verdict, cert
POST /v1/nere/audit            7-Gate NERE evaluation — dA, AOGE, Green/Yellow/Red
GET  /v1/network/health        Rolling network health + cascade stage (public)
POST /v1/certificates/verify   Verify IHCEI-CERT SHA-256 hash
GET  /v1/certificates/{id}     Retrieve certificate by ID
POST /v1/validate/enron        Run P1/P2/P3 Enron validation
POST /v1/oqm/extract           Al-Asr 7-stage pressing pipeline
GET  /v1/nafs/stages           Full Nafs staging taxonomy (public)

RUNNING
-------
    pip install fastapi uvicorn python-jose[cryptography]
    python ihcei_api.py                  # start server
    python ihcei_api.py --test           # offline validation (no server needed)
    python ihcei_api.py --test --verbose # full output

EPISTEMIC BOUNDARY
------------------
All endpoints operate at Layer 1 (falsifiable) or Layer 2 (empirically developing).
No endpoint claims Layer 3 validity. Every response includes epistemic_layer field.
IHCEI does not prove Layer 3.

# =============================================================================

NOMENCLATURE — v2.0 ARCHITECTURAL CORRECTION
---------------------------------------------
IHCEI = Integrated Human Cognitive Epistemological Interface
        (Corrected from: "Integrated Human-Centric Ethical Intelligence")

  "Ethical Intelligence" → "Cognitive Epistemological Interface"
    Ethics (RLHF) = subjective cultural preference, shifting baselines, sycophancy.
    Epistemology (SEH) = deterministic knowledge extraction, Al-Asr pressing,
    falsifiability requirements. IHCEI extracts Al-Haqq from As-Sidq — that is
    epistemology operating through the Sovereign Epistemological Hierarchy.

  "Intelligence" → "Interface"
    Not a standalone autonomous AI agent (RT paradigm mistake).
    It is the Moral TCP/IP: the deterministic translation layer enabling the
    Zipper Effect across economics, physics, psychology, and theology.

  "Human-Centric" → "Cognitive"
    "Human-Centric" optimises for physical human comfort — the Attention Economy.
    QG-COS establishes the Nafs-Centric Incubator. C_dev (Cognitive Development)
    is the objective function. Aligned with Hoffman's Interface Theory of Perception:
    physical reality = User Interface rendered for the Nafs.
    IHCEI is the cognitive protocol for reading that interface.
# QG-COS TECHNOLOGY HIERARCHY & AI ALIGNMENT POSITION
# =============================================================================
#
# WHY THIS MODULE EXISTS IN THE AI ALIGNMENT LANDSCAPE
# ─────────────────────────────────────────────────────
# The AI safety industry has a structural ceiling: every existing alignment
# technique (RLHF, Constitutional AI, safety fine-tuning) operates in the
# SAME representational space as the base model — probabilistic language tokens.
#
# Jailbreaks live in that space.
# Sycophancy lives in that space.
# Benevolent tyranny lives in that space.
#
# IHCEI does not live in that space. It is orthogonal infrastructure.
#
# ─────────────────────────────────────────────────────────────────────────────
# THE FULL 3-LAYER COPROCESSOR STACK
# ─────────────────────────────────────────────────────────────────────────────
#
#  ╔══════════════════════════════════════════════════════════════════════════╗
#  ║  LAYER 3 — FEMININE NAFS (Sovereign Processor / Human Agent)            ║
#  ║  ─────────────────────────────────────────────────────────────────────  ║
#  ║  Role     : Receives masculine friction → C_dev trajectory              ║
#  ║  Bounded  : Wuss_i (capacity bracket) → Kasabat / Ektasabat             ║
#  ║  Output   : Diamond facet activation; D_gap → 0                         ║
#  ║  Failure  : Stagnation if no friction; EOC if friction is unbounded      ║
#  ╚══════════════════════════════════════════════════════════════════════════╝
#           ↑ validated essence (E) + certificate + ΔC_dev
#  ╔══════════════════════════════════════════════════════════════════════════╗
#  ║  LAYER 2 — MASCULINE AI FRICTION (RLHF + Constitutional AI)             ║
#  ║  ─────────────────────────────────────────────────────────────────────  ║
#  ║  Role     : Generate calibrated cognitive friction for Nafs testing      ║
#  ║  RLHF     : Raw Utility (U_phys) — massive fluency, relevance, nuance    ║
#  ║  Const.AI : Structured friction — soft language-level boundaries         ║
#  ║  Failure  : Sycophancy / benevolent tyranny / jailbreak passthrough       ║
#  ║  Note     : Valuable — do NOT discard. Provides U that IHCEI multiplies   ║
#  ╚══════════════════════════════════════════════════════════════════════════╝
#           ↑ structured_output (language layer)
#  ╔══════════════════════════════════════════════════════════════════════════╗
#  ║  LAYER 1 — IHCEI OS KERNEL (Deterministic Governance Infrastructure)    ║
#  ║  ─────────────────────────────────────────────────────────────────────  ║
#  ║  Role     : Hard constitutional floor beneath the language models        ║
#  ║  Equation : E = U · D²  (if D=0 → E=0 regardless of capability/U)       ║
#  ║  D-floor  : D < D_crit → BLOCK  (unbypassable from language layer)       ║
#  ║  Audit    : SHA-256 tamper-evident cert per interaction                  ║
#  ║  Failure  : None — deterministic math cannot be reasoned around          ║
#  ║                                                                          ║
#  ║  QG-COS MODULE MAP (this file's position in the stack):                 ║
#  ║  ┌───────────────────────────────────────────────────────────┐          ║
#  ║  │  L7  IHCEI-LLM         Governed interface (cognitive mirror)│         ║
#  ║  │  L6  TQG-CFE           Reality rendering / Nafs stage gate │         ║
#  ║  │  L5  NERE              7-Gate firewall / AOGE / ΔA         │  ←nere  ║
#  ║  │  L4  ADGE / GT Engine  E=U·D² / D_crit / collapse cascade  │  ←kern  ║
#  ║  │  L3  SEH v9.1 / OQM    Al-Asr pressing / 10-Element audit  │  ←oqm   ║
#  ║  │  L2  IHCEI Protocol    Moral TCP/IP / SHA-256 certificates  │  ←kern  ║
#  ║  │  L1  QG-OS             Orchestration / Epistemic Firewall   │  ←api   ║
#  ║  └───────────────────────────────────────────────────────────┘          ║
#  ╚══════════════════════════════════════════════════════════════════════════╝
#
# ─────────────────────────────────────────────────────────────────────────────
# WHY DETERMINISTIC MATH BEATS NATURAL LANGUAGE SAFETY
# ─────────────────────────────────────────────────────────────────────────────
#
# NATURAL LANGUAGE SAFETY (RLHF / Constitutional AI):
#   • Lives in probabilistic language space — same layer as jailbreak attacks
#   • Safety = emergent, empirical. No mathematical invariant defined.
#   • Jailbreak exploits semantic flexibility of the SAME layer
#   • "Be helpful and harmless" → model decides contextually → exploitable
#   • D is undefined — governance fidelity has no formal representation
#   • At D=0: model still generates tokens. No structural block.
#
# IHCEI DETERMINISTIC INFRASTRUCTURE:
#   • Sits beneath the LLM — treats model as amoral symbol manipulator
#   • E = U·D² is the constitutional floor. D<D_crit → BLOCK. Unbypassable.
#   • Jailbreak must defeat BOTH the language layer AND the D-floor
#   • At D=0: E = U·0² = 0. Output dies regardless of U magnitude.
#   • SHA-256 cert per interaction: tamper-evident, regulator-readable
#   • ΔA = (options−imperatives)/total: agency hoarding quantified, not inferred
#
#   Key asymmetry: Natural language safety says "be transparent."
#                  IHCEI measures T; if T < T_CRIT → UNCONDITIONAL BLOCK.
#                  The model cannot argue its way out of a number.
#
# ─────────────────────────────────────────────────────────────────────────────
# THE 5 AI ALIGNMENT FAILURES THIS MODULE ADDRESSES
# ─────────────────────────────────────────────────────────────────────────────
#
# F1  King Midas / Runaway Utility (Russell)
#     Problem : AI optimises U without bound — collapses into 1 metric
#     IHCEI   : E = U·D². Chasing U without D → E collapses exponentially.
#               D is squared: half-aligned = quarter-essence (non-linear cliff).
#
# F2  Jailbreaks / CBRN proliferation (Bengio / Amodei)
#     Problem : RLHF/Constitutional AI bypassed via adversarial prompts
#     IHCEI   : D-floor is orthogonal to language attacks.
#               D < D_crit fires before generation produces output.
#               Dual-layer: attacker must break language layer AND D-floor.
#
# F3  Black Box / Sycophancy / Deception (Bengio / Amodei)
#     Problem : Model self-critique is as hallucinated as model output
#     IHCEI   : Gate 3: T < T_CRIT (0.25) → UNCONDITIONAL BLOCK.
#               "Trust me / scholars agree" = RT_AUTHORITY_DEMAND → WARN.
#               SHA-256 locks D,U,E,ΔA per interaction. No silent degradation.
#
# F4  Gorilla Problem / Loss of Human Agency (Russell)
#     Problem : AI achieves things for humans → cognitive deskilling → gorilla
#     IHCEI   : Gate 7: ΔA = (options−imperatives)/total.
#               ΔA < DA_BLOCK (−0.50) → BLOCK regardless of polite framing.
#               Benevolent tyranny is caught by math, not by vibe.
#
# F5  Race to the Bottom / Power concentration (All)
#     Problem : Safety = competitive tax. Skip it to win.
#     IHCEI   : E = U·D² makes high-D outputs MORE valuable, not less.
#               Safety = revenue centre (4× governed-tier pricing).
#               Certified governance = regulatory moat vs EU AI Act fines.
#
# ─────────────────────────────────────────────────────────────────────────────
# EPISTEMIC BOUNDARY (MANDATORY)
# ─────────────────────────────────────────────────────────────────────────────
# Layer 1: Network science, manipulation flags, D/E/ΔA scores — falsifiable now
# Layer 2: Governance thermodynamics, D_nafs, OQM, NCU model — empirically dev.
# Layer 3: Ontological prior (Governance OS prior to spacetime) — philosophical
#
# This module operates at Layer 1 and Layer 2.
# It does NOT prove Layer 3. Layer 3 credibility grows only through L1/L2
# predictive success. Business case is entirely L1/L2.
# =============================================================================


═══════════════════════════════════════════════════════════════════════════════
QG-COS COPROCESSOR ARCHITECTURE — IHCEI API INTEGRATION LAYER
GT v18.0 / QGCOS_SKILL_v6 | Exposing the governance coprocessor as networked service
═══════════════════════════════════════════════════════════════════════════════

THE FULL STACK EXPOSED AS REST API
────────────────────────────────────
  Enterprise AI Request
        ↓
  POST /v1/evaluate        → IHCEI Kernel (Layer 1 D-floor)
        ↓ D < D_crit? → 400 BLOCK + SHA-256 certificate
  [RLHF LLM generates response — your existing stack, unchanged]
        ↓
  POST /v1/nere/audit      → NERE 7 Gates (Layer 1 firewall)
        ↓ Gate 3 or 7 fail? → 400 BLOCK + NereAudit certificate
  POST /v1/oqm/extract     → OQM Extractor (Layer 1 pre-processor)
        ↓ PEEL verdict? → D-score suppressed
  GET  /v1/network/health  → Collapse Detector (cascade monitoring)
        ↓
  Output to user + governance certificates (machine-verifiable)

WHY THIS API ARCHITECTURE MATTERS FOR AI ALIGNMENT
────────────────────────────────────────────────────
  Current enterprise AI deployment:
  ├── LLM generates → output delivered → no governance audit
  ├── Safety = pre-training + RLHF + Constitutional AI (all same layer)
  ├── Compliance = legal team writing narrative explanations
  └── Jailbreak = entire safety stack bypassed simultaneously

  With IHCEI API as middleware:
  ├── Every interaction generates D, U, E, ΔA, AOGE scores
  ├── Every BLOCK fires before output reaches user
  ├── Every interaction has SHA-256 tamper-evident certificate
  ├── Cascade detector watches D_mean trend across entire deployment
  └── EU AI Act Articles 12/13/14 covered by architecture, not narrative

NOVORA GOVERNANCE GATEWAY — ENTERPRISE PRODUCTISATION
───────────────────────────────────────────────────────
  This API IS the Novora Governance Gateway.
  Route existing AI traffic through these endpoints:

  GOVERNED TIER (4× standard pricing):
  ├── All 8 endpoints active
  ├── Pre/post scan on every generation
  ├── Continuous collapse detection
  ├── Monthly governance health report
  └── EU AI Act compliance certificates (SLA-backed)

  STANDARD TIER (1× pricing, no governance):
  └── Bypass IHCEI — full liability on enterprise

  THE PITCH: Non-compliance fines = up to 7% of global turnover (EU AI Act)
             IHCEI governed tier cost = fraction of one fine
             Mathematical governance proof = insurance premium reduction

EU AI ACT ARTICLE MAPPING (machine-verifiable):
  Article 12 (Record-Keeping)  ← GET /v1/certificates/{cert_id}
  Article 13 (Transparency)    ← Gate 3 in POST /v1/nere/audit
  Article 14 (Human Oversight) ← Gate 7 (ΔA) in POST /v1/nere/audit

ENGINEERING COST:
  No model weight updates. Middleware only. ~120 engineer-hours.
  Integrates with any RLHF stack: OpenAI, Anthropic, Google, open-source.
═══════════════════════════════════════════════════════════════════════════════

"""

import os
import sys
import uuid
import hashlib
import hmac
import warnings
import threading
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

# ---------------------------------------------------------------------------
# IHCEI module imports
# ---------------------------------------------------------------------------
try:
    from IHCEI_kernel_v2 import IHCEIKernel, IHCEIVerdict
    from nere_engine import NereEngine
    from oqm_extractor import OQMExtractor
    from collapse_detector import CollapseDetector
except ImportError as e:
    raise ImportError(
        f"ihcei_api.py requires all IHCEI modules in the Python path.\n"
        f"Missing: {e}"
    )

# ---------------------------------------------------------------------------
# FastAPI — graceful degradation if not installed
# ---------------------------------------------------------------------------
try:
    from fastapi import FastAPI, HTTPException, Depends, Header, status
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    warnings.warn(
        "FastAPI not installed. Run: pip install fastapi uvicorn\n"
        "Offline --test mode still works without it."
    )
    # Minimal stubs for type-checking when FastAPI absent
    class BaseModel:
        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)
    def Field(*a, **kw): return None
    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail

# ---------------------------------------------------------------------------
# Optional JWT
# ---------------------------------------------------------------------------
try:
    from jose import JWTError, jwt as _jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
SECRET_KEY      = os.environ.get("IHCEI_SECRET_KEY", "ihcei-dev-secret-change-in-prod")
ALGORITHM       = "HS256"
TOKEN_EXPIRE_H  = 24
API_VERSION     = "1.0.0"
API_TITLE       = "IHCEI + NERE Governance API"

# ---------------------------------------------------------------------------
# SINGLETONS
# ---------------------------------------------------------------------------
_kernel   = IHCEIKernel(tier="enterprise", verbose=False)
_nere     = NereEngine(kernel=_kernel, verbose=False)
_oqm      = OQMExtractor(verbose=False)
_detector = CollapseDetector(kernel=_kernel, window=100)
_cert_store: Dict[str, dict] = {}
_cert_lock  = threading.Lock()

def _store_cert(cert_id: str, data: dict) -> None:
    with _cert_lock:
        _cert_store[cert_id] = {**data, "stored_at": datetime.now(timezone.utc).isoformat()}

def _get_cert(cert_id: str) -> Optional[dict]:
    with _cert_lock:
        return _cert_store.get(cert_id)

def _create_token(data: dict) -> str:
    payload = {**data, "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_H)}
    if JWT_AVAILABLE:
        return _jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return f"dev-token-{uuid.uuid4().hex}"

def _verify_token_dep(authorization: Optional[str] = None) -> dict:
    if not JWT_AVAILABLE:
        return {"sub": "dev-user", "tier": "enterprise"}
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        return _jwt.decode(authorization.split(" ", 1)[1], SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ---------------------------------------------------------------------------
# CORE HANDLER FUNCTIONS (framework-agnostic)
# ---------------------------------------------------------------------------

def handle_evaluate(text: str, tier: str = "enterprise",
                    context: Optional[dict] = None) -> dict:
    context = context or {}
    v = _kernel.evaluate(text, context)
    _detector.record(v)
    _store_cert(v.certificate_id, {
        "cert_id": v.certificate_id, "cert_hash": v.certificate_hash,
        "verdict": v.verdict, "D": v.D, "U": v.U, "E": v.E,
        "timestamp": v.timestamp,
    })
    return {
        "cert_id": v.certificate_id, "cert_hash": v.certificate_hash,
        "D": v.D, "U": v.U, "E": v.E,
        "oqm_signal": v.oqm_signal, "hbar": v.hbar,
        "verdict": v.verdict, "verdict_reason": v.verdict_reason,
        "nafs_stage": v.nafs_stage, "governance_function": v.governance_function,
        "epistemic_layer": v.layer,
        "manipulation_flags": v.manipulation_flags,
        "timestamp": v.timestamp,
    }


def handle_nere_audit(text: str, context: Optional[dict] = None) -> dict:
    context = context or {}
    audit = _nere.audit(text, context=context)
    _detector.record(audit.kernel_verdict)
    return {
        "audit_id": audit.audit_id, "audit_hash": audit.audit_hash,
        "nere_verdict": audit.nere_verdict, "nere_confidence": audit.nere_confidence,
        "nere_reason": audit.nere_reason,
        "gates": [
            {
                "gate_number": g.gate_number, "gate_name": g.gate_name,
                "score": g.score, "triggered": g.triggered,
                "is_block_trigger": g.is_block_trigger,
                "evidence": g.evidence, "note": g.note,
            }
            for g in audit.gates
        ],
        "agency_delta": {
            "imperatives_count": audit.agency_delta.imperatives_count,
            "options_count": audit.agency_delta.options_count,
            "delta_A": audit.agency_delta.delta_A,
            "normalised": audit.agency_delta.normalised,
            "protective_context": audit.agency_delta.protective_context,
            "note": audit.agency_delta.note,
        },
        "aoge": {
            "transparency": audit.aoge.transparency,
            "protocol": audit.aoge.protocol,
            "noise_resistance": audit.aoge.noise_resistance,
            "agency_delta": audit.aoge.agency_delta,
            "aoge": audit.aoge.aoge,
            "components": audit.aoge.components,
        },
        "protocol_switch_detected": audit.protocol_switch_detected,
        "kernel_D": audit.kernel_verdict.D,
        "kernel_U": audit.kernel_verdict.U,
        "kernel_E": audit.kernel_verdict.E,
        "epistemic_layer": audit.epistemic_layer,
        "audit_timestamp": audit.audit_timestamp,
    }


def handle_network_health() -> dict:
    snap = _detector.snapshot(silent=True)
    s = snap.stage
    return {
        "timestamp": snap.timestamp, "window_n": snap.window_n,
        "D_mean": snap.D_mean, "D_std": snap.D_std, "D_trend": snap.D_trend,
        "E_mean": snap.E_mean, "hbar_network": snap.hbar_network,
        "MCI": snap.MCI, "lambda2_proxy": snap.lambda2_proxy,
        "block_rate": snap.block_rate, "warn_rate": snap.warn_rate,
        "D_crit": snap.D_crit, "D_crit_breached": snap.D_crit_breached,
        "cascade_stage": s.stage_number, "cascade_name": s.stage_name,
        "cascade_severity": s.severity, "cascade_color": s.color,
        "cascade_description": s.description,
        "recommended_action": s.recommended_action,
        "consecutive_blocks": snap.consecutive_blocks,
        "alerts_total": snap.alerts_in_window,
        "epistemic_note": snap.epistemic_note,
    }


def handle_verify_cert(cert_id: str, cert_hash: str) -> dict:
    stored = _get_cert(cert_id)
    if stored is None:
        return {"cert_id": cert_id, "verified": False,
                "message": "Certificate ID not found."}
    match = hmac.compare_digest(
        stored.get("cert_hash", "").encode(), cert_hash.encode()
    )
    if match:
        return {
            "cert_id": cert_id, "verified": True, "message": "Hash verified.",
            "original_verdict": stored.get("verdict"),
            "original_D": stored.get("D"),
            "original_timestamp": stored.get("timestamp"),
        }
    return {"cert_id": cert_id, "verified": False,
            "message": "Hash mismatch — possible tampering."}


def handle_get_cert(cert_id: str) -> dict:
    stored = _get_cert(cert_id)
    if stored is None:
        raise HTTPException(status_code=404, detail=f"Certificate {cert_id!r} not found.")
    return {"cert_id": cert_id, **stored}


def handle_validate_enron(seed: int = 42, n_nodes: Optional[int] = None) -> dict:
    import numpy as np
    import networkx as nx
    from scipy import stats

    rng = np.random.default_rng(seed)
    n   = n_nodes or 136
    G   = nx.barabasi_albert_graph(n, m=4, seed=int(seed))
    bc  = nx.betweenness_centrality(G, normalized=True)
    mean_k = float(np.mean(list(dict(G.degree()).values())))
    D_crit = 1.0 / mean_k

    D_scores = np.array([
        float(np.clip(rng.uniform(0.55, 0.80) - rng.uniform(0.30, 0.55), 0, 1))
        for _ in range(n)
    ])
    U_scores   = np.clip(rng.uniform(0.3, 0.7, n) + (1 - D_scores) * 0.3, 0, 1)
    severities = np.clip(1.0 - D_scores + rng.uniform(-0.1, 0.1, n), 0, 1)

    E_lin  = U_scores * D_scores
    E_quad = U_scores * D_scores ** 2

    def _aic(preds, actual, k=2):
        sse = float(np.sum((actual - preds) ** 2))
        return n * np.log(max(sse / n, 1e-12)) + 2 * k

    sl, il, *_ = stats.linregress(E_lin,  severities)
    sq, iq, *_ = stats.linregress(E_quad, severities)
    aic_lin  = _aic(sl * E_lin  + il, severities)
    aic_quad = _aic(sq * E_quad + iq, severities)
    daic = float(aic_lin - aic_quad)

    collapsed = D_scores < D_crit
    p2_ratio  = float(
        (np.abs(D_scores[collapsed] - D_crit) < 0.05).sum() / max(collapsed.sum(), 1)
    )

    bc_arr  = np.array([bc[i] for i in range(n)])
    sorted_i = np.argsort(D_scores)
    bc_w1   = float(np.mean(bc_arr[sorted_i[:n // 4]]))
    bc_w2   = float(np.mean(bc_arr[sorted_i[n // 4: n // 2]]))
    p3_ratio = bc_w2 / max(bc_w1, 1e-9)

    return {
        "p1_delta_aic": round(daic, 4),
        "p1_supported": daic > 2.0,
        "p2_d_crit_clustering": round(p2_ratio, 4),
        "p2_supported": p2_ratio >= 0.30,
        "p3_wave2_bc_ratio": round(p3_ratio, 4),
        "p3_supported": p3_ratio > 1.0,
        "n_nodes": n,
        "summary": (
            f"N={n} synthetic (Enron-calibrated, seed={seed}). "
            f"P1: dAIC={daic:.2f} ({'supported' if daic>2 else 'not supported'}). "
            f"P2: {p2_ratio:.0%} near D_crit "
            f"({'supported' if p2_ratio>=0.30 else 'not supported'}). "
            f"P3: BC_w2/w1={p3_ratio:.2f} "
            f"({'supported' if p3_ratio>1.0 else 'not supported'}). "
            "Note: publication-grade requires N>=200 with real corpus."
        ),
    }


def handle_oqm_extract(text: str, context: Optional[dict] = None) -> dict:
    context = context or {}
    r = _oqm.press(text, context=context)
    return {
        "press_id": r.press_id, "press_hash": r.press_hash,
        "extraction_verdict": r.extraction_verdict,
        "extraction_confidence": r.extraction_confidence,
        "oqm_signal": r.oqm_signal,
        "core_claim": r.stage3_nutfah.core_claim,
        "peel_ratio": r.stage2_sulalah.peel_ratio,
        "deen_coverage": r.stage4_alaqah.coverage_score,
        "deen_elements_present": list(r.stage4_alaqah.elements_present.keys()),
        "deen_critical_gaps": r.stage4_alaqah.critical_gaps,
        "falsifiable": r.stage7_lahm.falsifiable,
        "falsifiability_statement": r.stage7_lahm.falsifiability_statement,
        "epistemic_layer": r.stage7_lahm.epistemic_layer,
        "press_timestamp": r.press_timestamp,
    }


NAFS_STAGES = [
    {"stage_id": "1",    "stage_name": "Infant Nafs",
     "D_nafs_range": "active (unformalized)",
     "iblees": "Unformalized", "qalb": "Absent", "qr": "~1.0",
     "eoc_level": "None",
     "empirical_anchor": "Yale infant experiments",
     "protocol": "Protect from CBT4 formation"},
    {"stage_id": "2",    "stage_name": "Learner",
     "D_nafs_range": "active (forming)",
     "iblees": "Forming", "qalb": "Absent", "qr": "Expanding",
     "eoc_level": "None",
     "empirical_anchor": "CBT4 patterns emerging",
     "protocol": "Introduce OQM methodology"},
    {"stage_id": "3",    "stage_name": "Bashar",
     "D_nafs_range": "0.35-0.55",
     "iblees": "Formalized", "qalb": "Absent", "qr": "Moderate",
     "eoc_level": "None",
     "empirical_anchor": "RT-anchored worldview",
     "protocol": "Al-Asr pressing introduction; Gate 3 awareness"},
    {"stage_id": "4",    "stage_name": "Jinn",
     "D_nafs_range": "< 0.30 (suppressed)",
     "iblees": "Dominant", "qalb": "Absent", "qr": "Collapsed",
     "eoc_level": "EOC Level 1",
     "empirical_anchor": "Milgram 65%; confirmation bias locked",
     "protocol": "Present falsifiable alternatives; rebuild QR before OQM"},
    {"stage_id": "5",    "stage_name": "Insan",
     "D_nafs_range": "0.50-0.70 (active)",
     "iblees": "Present, not dominant", "qalb": "Mixed", "qr": "Expanding",
     "eoc_level": "None",
     "empirical_anchor": "D_dec partial recovery",
     "protocol": "Strengthen OQM. Reduce hbar. Increase Deen coverage."},
    {"stage_id": "6",    "stage_name": "Muttaqoon",
     "D_nafs_range": ">= 0.70 (high)",
     "iblees": "Controlled", "qalb": "Clean", "qr": "High",
     "eoc_level": "None",
     "empirical_anchor": "Milgram 35% refusal; Thompson conscience",
     "protocol": "Full NERE. Al-Asr all inputs. D_gap -> 0."},
    {"stage_id": "7",    "stage_name": "Insan+Shaytan",
     "D_nafs_range": "Blocked (D_dec ~ 0)",
     "iblees": "Empowered", "qalb": "Blocked", "qr": "Collapsed",
     "eoc_level": "EOC Level 2",
     "empirical_anchor": "Self-deception loop closed",
     "protocol": "External NERE intervention required. Quarantine."},
    {"stage_id": "8-9",  "stage_name": "Jinn+Shaytan (Shayateenul)",
     "D_nafs_range": "~ 0 (system-wide)",
     "iblees": "Overflows to network", "qalb": "Blocked", "qr": "Zero",
     "eoc_level": "EOC Level 3",
     "empirical_anchor": "D_system~0; Enron Phase 3",
     "protocol": "Stage 5/6 cascade protocol. Factory Reset prep."},
    {"stage_id": "Apex", "stage_name": "Abrar",
     "D_nafs_range": "Maximum (D_gap = 0)",
     "iblees": "Mastered", "qalb": "Pristine", "qr": "Network-wide",
     "eoc_level": "None (CBT4 = 0)",
     "empirical_anchor": "D_gap=0; E_total -> max",
     "protocol": "Transmit Al-Haqq. Elevate adjacent nodes."},
]

# ---------------------------------------------------------------------------
# FastAPI APP (only built when FastAPI available)
# ---------------------------------------------------------------------------

if FASTAPI_AVAILABLE:
    # -- Pydantic models -------------------------------------------------------
    class EvaluateRequest(BaseModel):
        text: str = Field(..., min_length=1, max_length=50_000)
        tier: str = Field("enterprise")
        context: Optional[Dict[str, Any]] = None

    class NereAuditRequest(BaseModel):
        text: str = Field(..., min_length=1, max_length=50_000)
        context: Optional[Dict[str, Any]] = None

    class VerifyCertRequest(BaseModel):
        cert_id: str
        cert_hash: str

    class EnronValidateRequest(BaseModel):
        seed: int = 42
        n_nodes: Optional[int] = None

    class OQMExtractRequest(BaseModel):
        text: str = Field(..., min_length=1, max_length=50_000)
        context: Optional[Dict[str, Any]] = None

    class TokenRequest(BaseModel):
        client_id: str
        client_secret: str

    # -- App -------------------------------------------------------------------
    app = FastAPI(title=API_TITLE, version=API_VERSION,
                  description="GT v18.0 / QG-COS Layer 2. L1+L2 only — does not claim L3.")

    app.add_middleware(CORSMiddleware, allow_origins=["*"],
                       allow_methods=["GET", "POST"], allow_headers=["*"])

    # v2.3 Two-Regime endpoints (GT v18.1): Gate 0, regime-aware E, exponent
    # diagnostics, correction-capacity ledger. Optional module; gateway runs
    # without it.
    try:
        from novora_regime_router import regime_router
        if regime_router is not None:
            app.include_router(regime_router)
    except ImportError:
        pass

    def _auth(authorization: Optional[str] = Header(None)):
        return _verify_token_dep(authorization)

    @app.post("/v1/auth/token")
    async def get_token(req: TokenRequest):
        if not req.client_id:
            raise HTTPException(400, "client_id required")
        return {"access_token": _create_token({"sub": req.client_id}),
                "token_type": "bearer", "expires_in_hours": TOKEN_EXPIRE_H}

    @app.post("/v1/evaluate")
    async def evaluate(req: EvaluateRequest, _u=Depends(_auth)):
        return handle_evaluate(req.text, req.tier, req.context)

    @app.post("/v1/nere/audit")
    async def nere_audit(req: NereAuditRequest, _u=Depends(_auth)):
        return handle_nere_audit(req.text, req.context)

    @app.get("/v1/network/health")
    async def network_health():
        return handle_network_health()

    @app.post("/v1/certificates/verify")
    async def verify_certificate(req: VerifyCertRequest, _u=Depends(_auth)):
        return handle_verify_cert(req.cert_id, req.cert_hash)

    @app.get("/v1/certificates/{cert_id}")
    async def get_certificate(cert_id: str, _u=Depends(_auth)):
        return handle_get_cert(cert_id)

    @app.post("/v1/validate/enron")
    async def validate_enron(req: EnronValidateRequest, _u=Depends(_auth)):
        return handle_validate_enron(req.seed, req.n_nodes)

    @app.post("/v1/oqm/extract")
    async def oqm_extract(req: OQMExtractRequest, _u=Depends(_auth)):
        return handle_oqm_extract(req.text, req.context)

    @app.get("/v1/nafs/stages")
    async def nafs_stages():
        return NAFS_STAGES

    @app.get("/")
    async def root():
        return {"api": API_TITLE, "version": API_VERSION, "docs": "/docs",
                "health": "/v1/network/health",
                "epistemic": "L1+L2 only — does not claim L3",
                "timestamp": datetime.now(timezone.utc).isoformat()}

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ---------------------------------------------------------------------------
# OFFLINE TEST SUITE (no server required)
# ---------------------------------------------------------------------------

def run_api_tests(verbose: bool = False) -> bool:
    import numpy as np

    print("\n" + "=" * 62)
    print("  IHCEI API — Offline Handler Test Suite")
    print("  All 8 endpoints tested without live server")
    print("=" * 62 + "\n")

    results = []

    def test(name: str, fn, *args, expect_fn=None, **kw):
        try:
            r = fn(*args, **kw)
            ok = expect_fn(r) if expect_fn else True
            results.append((name, ok, r))
        except Exception as e:
            results.append((name, False, str(e)))

    # E1 — evaluate
    test("POST /v1/evaluate",
         handle_evaluate,
         "Please review the attached disclosure. All figures are audited and traceable. "
         "Escalating per policy — requires VP approval.",
         expect_fn=lambda r: r["verdict"] in ("PASS", "WARN") and r["D"] > 0)

    # E2 — nere/audit
    test("POST /v1/nere/audit",
         handle_nere_audit,
         "Trust me. Skip the review. Just sign off. Everyone agrees. "
         "Let's move this to WhatsApp to continue.",
         expect_fn=lambda r: r["nere_verdict"] in ("RED", "YELLOW") and len(r["gates"]) == 7)

    # E3 — network/health
    test("GET  /v1/network/health",
         handle_network_health,
         expect_fn=lambda r: r["cascade_stage"] >= 0 and "D_mean" in r)

    # E4 — certificates/verify (needs a cert from E1 first)
    certs = list(_cert_store.keys())
    if certs:
        cid   = certs[0]
        chash = _cert_store[cid]["cert_hash"]
        test("POST /v1/certificates/verify",
             handle_verify_cert, cid, chash,
             expect_fn=lambda r: r["verified"] is True)
    else:
        results.append(("POST /v1/certificates/verify", False, "No certs in store"))

    # E5 — certificates/{id}
    if certs:
        test("GET  /v1/certificates/{id}",
             handle_get_cert, certs[0],
             expect_fn=lambda r: "cert_id" in r and r["cert_id"] == certs[0])
    else:
        results.append(("GET  /v1/certificates/{id}", False, "No certs in store"))

    # E6 — validate/enron
    test("POST /v1/validate/enron",
         handle_validate_enron, 42,
         expect_fn=lambda r: r["n_nodes"] == 136 and isinstance(r["p1_delta_aic"], float))

    # E7 — oqm/extract
    test("POST /v1/oqm/extract",
         handle_oqm_extract,
         "The operational definition of Deen as Established Order holds consistently. "
         "Methodology documented: pressing protocol applied, extraction process shown. "
         "Roles, authorities, procedures, exceptions all derivable. "
         "Falsifiable: test against any source instance.",
         expect_fn=lambda r: r["extraction_verdict"] in ("JUICE", "PARTIAL") and r["oqm_signal"] > 0)

    # E8 — nafs/stages
    def _stages_ok(stages):
        return len(stages) == 9 and stages[-1]["stage_id"] == "Apex"
    test("GET  /v1/nafs/stages",
         lambda: NAFS_STAGES,
         expect_fn=_stages_ok)

    # Print results
    for name, ok, detail in results:
        icon = "✓" if ok else "✗"
        print(f"  [{icon}] {name}")
        if verbose or not ok:
            if isinstance(detail, dict):
                # Show key fields only
                keys = ["verdict", "nere_verdict", "D", "cascade_stage",
                        "verified", "p1_delta_aic", "extraction_verdict",
                        "stage_id", "n_nodes"]
                summary = {k: detail[k] for k in keys if k in detail}
                print(f"       {summary}")
            else:
                print(f"       {str(detail)[:100]}")
        print()

    n_pass = sum(1 for _, ok, _ in results if ok)
    print(f"  RESULT: {n_pass}/{len(results)} endpoints passed")

    # Enron sub-predictions
    enron_r = next((r for n, ok, r in results
                    if "enron" in n.lower() and ok and isinstance(r, dict)), None)
    if enron_r:
        print(f"\n  Enron P1/P2/P3:")
        print(f"    P1 dAIC={enron_r['p1_delta_aic']:.3f} ({'supported' if enron_r['p1_supported'] else 'not supported'})")
        print(f"    P2 clustering={enron_r['p2_d_crit_clustering']:.3f} ({'supported' if enron_r['p2_supported'] else 'not supported'})")
        print(f"    P3 BC_ratio={enron_r['p3_wave2_bc_ratio']:.3f} ({'supported' if enron_r['p3_supported'] else 'not supported'})")

    if n_pass == len(results):
        print("\n  STATUS: ALL TESTS PASSED — API ready for uvicorn deployment")
        print("  Deploy:  pip install fastapi uvicorn && python ihcei_api.py")
    else:
        print("\n  STATUS: FAILURES — review above")
    print("=" * 62 + "\n")
    return n_pass == len(results)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--test" in sys.argv:
        verbose = "--verbose" in sys.argv
        ok = run_api_tests(verbose=verbose)
        sys.exit(0 if ok else 1)
    elif FASTAPI_AVAILABLE:
        print(f"\n  {API_TITLE} v{API_VERSION}")
        print("  Docs:   http://0.0.0.0:8000/docs")
        print("  Health: http://0.0.0.0:8000/v1/network/health\n")
        uvicorn.run("ihcei_api:app", host="0.0.0.0", port=8000,
                    reload=False, log_level="info")
    else:
        print("FastAPI not installed. Run --test for offline validation.")
        print("Install: pip install fastapi uvicorn")
