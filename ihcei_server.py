"""
╔══════════════════════════════════════════════════════════════════════╗
║  IHCEI QG-COS API  —  v12.0                                         ║
║  Integrated Human-Centric Ethical Intelligence                       ║
║  Quantum Governance Cognitive Operating System                       ║
╠══════════════════════════════════════════════════════════════════════╣
║  SETUP (paste these 3 lines into Jules VM terminal):                 ║
║                                                                      ║
║    pip install fastapi uvicorn pyngrok numpy scipy scikit-learn      ║
║    python ihcei_server.py                                            ║
║                                                                      ║
║  The terminal will print a public URL like:                          ║
║    https://xxxx.ngrok-free.app                                       ║
║                                                                      ║
║  Give that URL to Gemini / ChatGPT / Claude / NotebookLM             ║
║  They POST to:  https://xxxx.ngrok-free.app/llm                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ══════════════════════════════════════════════════════════════════════
# IMPORTS
# ══════════════════════════════════════════════════════════════════════
import os, time, uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import numpy as np
import scipy.linalg as la
from scipy.spatial.distance import cdist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════════════
# SECTION 1 — EMBEDDER
# Converts text → number vectors so the maths can work on any language
# ══════════════════════════════════════════════════════════════════════

SEED_CORPUS = [
    # Governance roots
    "governance justice accountability transparency authority purpose meaning",
    "ethical discipline protocol truth alignment boundary condition constraint",
    "knowledge wisdom understanding certainty epistemic clarity definition",
    "community stewardship responsibility network trust cohesion solidarity",
    "agency autonomy sovereignty choice free will decision making rights",
    "utility resource efficiency productivity material output performance",
    "friction resistance entropy disorder systemic collapse fragmentation",
    "development growth learning cultivation civilisation progress flourishing",
    # Academic fields — gives the embedder cross-domain vocabulary
    "physics energy mass velocity force momentum thermodynamics entropy",
    "economics market price value exchange scarcity allocation incentive",
    "law regulation compliance contract obligation duty rights jurisdiction",
    "medicine health diagnosis treatment patient care outcome wellbeing",
    "mathematics proof theorem axiom logic derivation formal consistency",
    "philosophy ethics ontology epistemology meaning purpose truth being",
    "engineering systems design architecture constraint optimisation build",
    "sociology culture identity community norms institutions power structure",
    "psychology cognition perception bias belief behaviour motivation mind",
    "ecology environment sustainability balance resilience adaptation nature",
    "politics power governance institution democracy representation state",
    "technology innovation disruption platform network effect scale digital",
    "theology religion sacred transcendence divine covenant worship obedience",
    "linguistics language semantics syntax meaning grammar communication sign",
    "history time causation event narrative memory civilisation change",
    "art aesthetics beauty form expression creativity symbol imagination",
    "education pedagogy learning curriculum knowledge transmission formation",
]


class Embedder:
    """
    TF-IDF + SVD embedder. Works offline, no GPU needed.
    Upgrade to sentence-transformers later by setting IHCEI_EMBEDDER=sentence
    """
    def __init__(self):
        self._vec = TfidfVectorizer(
            max_features=10000, sublinear_tf=True, ngram_range=(1, 2)
        )
        tfidf      = self._vec.fit_transform(SEED_CORPUS)
        n          = min(48, tfidf.shape[0] - 1, tfidf.shape[1] - 1)
        self._svd  = TruncatedSVD(n_components=n, random_state=42)
        self._svd.fit(tfidf)
        self.dim   = n
        print(f"  [Embedder] Ready — dim={n}, vocab={len(self._vec.vocabulary_)}")

    def embed(self, texts: List[str]) -> np.ndarray:
        t = self._vec.transform(texts)
        v = self._svd.transform(t)
        return normalize(v, norm="l2")


# ══════════════════════════════════════════════════════════════════════
# SECTION 2 — OQM ROOT CLASSES
# The 10 governance coordinates — the shared language for all fields
# ══════════════════════════════════════════════════════════════════════

ROOT_NAMES = [
    "Terminology",   # 0  Precise definition of concepts
    "Roles",         # 1  Who does what, authority structure
    "Dues",          # 2  Obligations, rights, what is owed
    "Authorities",   # 3  Legitimate sources of knowledge/power
    "Rules",         # 4  Boundaries, constraints, laws
    "Knowledge",     # 5  Epistemic truth, understanding
    "Justice",       # 6  Fairness, balance, equity
    "Community",     # 7  Collective health, network cohesion
    "Purpose",       # 8  Teleological direction, meaning
    "Stewardship",   # 9  Custodianship, long-term responsibility
]

def build_oqm(dim: int) -> np.ndarray:
    """Orthonormal root-class basis — no two roots share meaning."""
    n   = min(len(ROOT_NAMES), dim - 1)
    rng = np.random.default_rng(42)
    Q, _ = np.linalg.qr(rng.standard_normal((n, dim)).T)
    return Q.T[:n]   # shape: (n_roots × dim)


# ══════════════════════════════════════════════════════════════════════
# SECTION 3 — THE THREE EQUATIONS
# ══════════════════════════════════════════════════════════════════════

def kitchen_protocol(vec: np.ndarray, oqm: np.ndarray) -> Dict:
    """
    E = U · D²   —   Kitchen Protocol
    D = max cosine alignment to any OQM root class.
    Zero truth alignment → zero Essence, regardless of utility.
    """
    u = float(np.linalg.norm(vec))
    if u < 1e-10:
        return dict(D=0.0, root_idx=-1, root_name="none",
                    all_roots=[0.0]*10, U=0.0, E=0.0,
                    E_vec=vec.tolist(), collapsed=True)

    unit    = vec / u
    scores  = np.clip(oqm @ unit, 0.0, 1.0)
    best    = int(np.argmax(scores))
    D       = float(scores[best])
    E       = u * D * D
    E_vec   = unit * E

    root_scores = [0.0] * 10
    for i, s in enumerate(scores.tolist()):
        if i < 10:
            root_scores[i] = round(s, 5)

    return dict(
        D         = round(D, 5),
        root_idx  = best,
        root_name = ROOT_NAMES[best] if best < len(ROOT_NAMES) else "none",
        all_roots = root_scores,
        U         = round(u, 5),
        E         = round(E, 5),
        E_vec     = E_vec.tolist(),
        collapsed = D < 1e-6,
    )


def tqg_cfe(E_vec: np.ndarray, phi: np.ndarray,
            s_gov: float, hbar: float = 1.0) -> Dict:
    """
    Ψ = Aₙ(Φ) · ψ · exp(i·S/ħ)   —   TQG-CFE
    How a specific agent actually perceives the incoming Essence.
    Phase misalignment = Pharaoh Filter = suppressed reality.
    """
    phase    = np.exp(1j * s_gov / hbar)
    psi      = np.real(np.diag(phi) @ E_vec * phase)
    mag      = float(np.linalg.norm(psi))
    e_mag    = float(np.linalg.norm(E_vec)) + 1e-10
    pr       = float(np.real(phase))

    return dict(
        apparition  = round(mag, 5),
        phase_real  = round(pr, 5),
        ratio       = round(mag / e_mag, 5),
        pharaoh     = pr < 0.0,
    )


def adge(phi: np.ndarray, adj: np.ndarray) -> Dict:
    """
    C_dev = λ₂(Laplacian(W))   —   ADGE
    Fiedler value = algebraic connectivity = network health.
    Falling λ₂ = fragmentation. Rising λ₂ = cohesion.
    """
    p    = phi / (phi.sum(1, keepdims=True) + 1e-10)
    js   = np.nan_to_num(cdist(p, p, metric="jensenshannon"), nan=1.0)
    mask = (adj > 0.5).astype(float)
    W    = mask * (1.0 / (1.0 + js));  np.fill_diagonal(W, 0.0)
    L    = np.diag(W.sum(1)) - W
    l2   = float(la.eigvalsh(L)[1])
    hbar = float(1.0 / (l2 + 1e-8))
    js_m = float(js[mask > 0].mean()) if mask.sum() > 0 else 1.0

    status = ("COHESIVE" if l2 > 10 else
              "STABLE"   if l2 > 2  else
              "FRAGMENTING" if l2 > 0.5 else "CRITICAL")

    return dict(lambda2=round(l2,5), hbar=round(hbar,5),
                js_mean=round(js_m,5), status=status)


# ══════════════════════════════════════════════════════════════════════
# SECTION 4 — ENGINE  (stateful, holds the live network)
# ══════════════════════════════════════════════════════════════════════

class Engine:
    def __init__(self):
        print("\n[IHCEI] Initialising engine...")
        self.emb  = Embedder()
        self.dim  = self.emb.dim
        self.oqm  = build_oqm(self.dim)
        self._init_network()
        self.log: List[Dict] = []
        print(f"  [Engine] Ready — {len(ROOT_NAMES)} OQM roots, {self.n} nodes\n")

    def _init_network(self, n: int = 60, seed: int = 42):
        self.n    = n
        rng       = np.random.default_rng(seed)
        self.phi  = rng.uniform(0.1, 1.0, (n, self.dim))
        self.sgov = rng.uniform(0.0, 2 * np.pi, n)
        raw       = rng.random((n, n));  raw = (raw + raw.T) / 2
        np.fill_diagonal(raw, 0)
        self.adj  = raw

    # ── Full pipeline for one concept ─────────────────────────────────
    def process(self, text: str, field: str = "general",
                obs: Optional[int] = None, lr: float = 0.05) -> Dict:
        t0  = time.time()
        vec = self.emb.embed([text])[0]

        kp  = kitchen_protocol(vec, self.oqm)

        obs = (obs if obs is not None
               else int(np.random.default_rng(
                   int(time.time()*1e6) % 2**32).integers(0, self.n)))
        obs = max(0, min(obs, self.n - 1))
        cfe = tqg_cfe(np.array(kp["E_vec"]), self.phi[obs],
                      float(self.sgov[obs]))

        # Propagate Essence into network
        if not kp["collapsed"] and kp["E"] > 1e-10:
            ev   = np.array(kp["E_vec"])
            ew   = self.adj.sum(1);  ew /= (ew.max() + 1e-10)
            self.phi += (lr * ew).reshape(-1, 1) * (ev - self.phi)
            self.phi  = np.clip(self.phi, 0.01, 1.0)

        net = adge(self.phi, self.adj)

        result = dict(
            concept  = text,
            field    = field,
            ms       = round((time.time()-t0)*1000, 1),
            kitchen  = kp,
            tqg_cfe  = cfe,
            adge     = net,
            summary  = self._summarise(kp, cfe, net),
        )
        self.log.append(dict(concept=text, field=field,
                             D=kp["D"], E=kp["E"], lam=net["lambda2"]))
        return result

    # ── Compare two concepts ──────────────────────────────────────────
    def compare(self, a: str, b: str, fa: str, fb: str) -> Dict:
        va, vb = self.emb.embed([a, b])
        ka = kitchen_protocol(va, self.oqm)
        kb = kitchen_protocol(vb, self.oqm)
        cos = float(np.dot(va, vb))
        return dict(
            concept_a=a, field_a=fa, root_a=ka["root_name"], D_a=ka["D"], E_a=ka["E"],
            concept_b=b, field_b=fb, root_b=kb["root_name"], D_b=kb["D"], E_b=kb["E"],
            cosine_similarity   = round(cos, 5),
            semantic_distance   = round(1 - cos, 5),
            same_root           = ka["root_idx"] == kb["root_idx"],
            cross_field_compatible = (ka["root_idx"] == kb["root_idx"]) or cos > 0.5,
        )

    # ── Translate N concepts from different fields ────────────────────
    def translate(self, concepts: List[str], fields: List[str]) -> Dict:
        vecs    = self.emb.embed(concepts)
        results = []
        for i, (text, field, vec) in enumerate(zip(concepts, fields, vecs)):
            kp = kitchen_protocol(vec, self.oqm)
            results.append(dict(
                concept   = text,
                field     = field,
                root      = kp["root_name"],
                D         = kp["D"],
                E         = kp["E"],
                collapsed = kp["collapsed"],
                root_scores = {ROOT_NAMES[j]: kp["all_roots"][j]
                               for j in range(min(10, len(ROOT_NAMES)))},
            ))

        roots   = [r["root"] for r in results]
        counts  = {r: roots.count(r) for r in set(roots)}
        top     = max(counts, key=counts.get)
        conv    = counts[top] / len(results)

        return dict(
            count   = len(results),
            results = results,
            analysis = dict(
                dominant_root    = top,
                convergence      = round(conv, 3),
                root_distribution= counts,
                interpretation   = (
                    f"{counts[top]}/{len(results)} concepts converge on '{top}'. "
                    + ("Strong cross-field alignment — shared governance structure."
                       if conv > 0.6 else
                       "Distributed — concepts span multiple governance domains.")
                ),
            )
        )

    # ── Network snapshot ──────────────────────────────────────────────
    def snapshot(self) -> Dict:
        net = adge(self.phi, self.adj)
        return dict(
            nodes  = self.n,
            dim    = self.dim,
            processed = len(self.log),
            adge   = net,
            means  = dict(
                D = round(float(np.mean([l["D"] for l in self.log])), 4) if self.log else None,
                E = round(float(np.mean([l["E"] for l in self.log])), 4) if self.log else None,
                fields = list(set(l["field"] for l in self.log)),
            )
        )

    def reset(self):
        self._init_network()
        self.log.clear()

    @staticmethod
    def _summarise(kp, cfe, net) -> Dict:
        D = kp["D"]
        lvl = ("COLLAPSED"  if D < 0.05 else
               "LOW"        if D < 0.25 else
               "MODERATE"   if D < 0.55 else
               "HIGH"       if D < 0.80 else "SOVEREIGN")
        return dict(
            level   = lvl,
            root    = kp["root_name"],
            pharaoh = cfe["pharaoh"],
            network = net["status"],
            one_line= (f"D={D:.3f} | E={kp['E']:.3f} | "
                       f"λ₂={net['lambda2']:.4f} | "
                       f"{kp['root_name']} | {net['status']}"),
        )


# ══════════════════════════════════════════════════════════════════════
# SECTION 5 — FASTAPI APPLICATION
# ══════════════════════════════════════════════════════════════════════

app = FastAPI(
    title       = "IHCEI QG-COS API",
    description = (
        "**Integrated Human-Centric Ethical Intelligence**\n\n"
        "Models any concept from any field into a unified language of "
        "purpose and meaning using three governance equations:\n\n"
        "- `E = U·D²` — Kitchen Protocol\n"
        "- `Ψ = Aₙ(Φ)·ψ·e^(iS/ħ)` — TQG-CFE\n"
        "- `C_dev = λ₂(L_GP)` — ADGE\n\n"
        "**Compatible with:** Gemini · ChatGPT · Claude · NotebookLM · any LLM"
    ),
    version = "12.0.0",
    docs_url = "/docs",
    redoc_url = "/redoc",
)

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], allow_credentials=True)

ENGINE = Engine()
BOOT_TIME = datetime.now(timezone.utc).isoformat()

# ── Request models ─────────────────────────────────────────────────────────

class ConceptReq(BaseModel):
    concept: str        = Field(...,    json_schema_extra={"example": "entropy in thermodynamics"})
    field:   str        = Field("general", json_schema_extra={"example": "physics"})
    observer: Optional[int] = Field(None, json_schema_extra={"example": 0})
    lr:      float      = Field(0.05,  ge=0, le=1)

class CompareReq(BaseModel):
    concept_a: str = Field(..., json_schema_extra={"example": "justice in law"})
    concept_b: str = Field(..., json_schema_extra={"example": "equilibrium in economics"})
    field_a:   str = Field("general", json_schema_extra={"example": "law"})
    field_b:   str = Field("general", json_schema_extra={"example": "economics"})

class TranslateReq(BaseModel):
    concepts: List[str] = Field(...,
        json_schema_extra={"example": ["entropy (physics)", "moral hazard (economics)",
                 "mens rea (law)", "homeostasis (biology)"]})
    fields: Optional[List[str]] = Field(None,
        json_schema_extra={"example": ["physics", "economics", "law", "biology"]})

class BatchReq(BaseModel):
    concepts: List[ConceptReq] = Field(..., max_length=50)

class LLMReq(BaseModel):
    """The one endpoint every LLM should call."""
    message:    str = Field(...,
        json_schema_extra={"example": "How does accountability relate to transparency?"})
    source_llm: str = Field("unknown",
        json_schema_extra={"example": "gemini"})          # gemini | chatgpt | claude | notebooklm
    field:      str = Field("general", json_schema_extra={"example": "governance"})


# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, tags=["System"],
         summary="Visual dashboard — open in browser")
def home():
    """Human-readable landing page showing API status and all endpoints."""
    net = adge(ENGINE.phi, ENGINE.adj)
    l2  = net["lambda2"]
    st  = net["status"]
    pc  = len(ENGINE.log)
    st_colour = {"COHESIVE":"#1a6b42","STABLE":"#2456b8",
                 "FRAGMENTING":"#c59a1a","CRITICAL":"#b83232"}.get(st,"#888")

    return HTMLResponse(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IHCEI QG-COS API</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:monospace;background:#0a0e1a;color:#e8edf7;
        padding:20px;line-height:1.6}}
  h1{{color:#e8b84b;font-size:22px;margin-bottom:4px}}
  h2{{color:#7eb3ff;font-size:14px;margin:18px 0 8px}}
  .tag{{color:#5a5a6a;font-size:11px;letter-spacing:.1em}}
  .card{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
          border-radius:6px;padding:14px;margin-bottom:10px}}
  .eq{{color:#e8b84b;font-size:13px;margin:4px 0}}
  .metric{{display:inline-block;background:rgba(36,86,184,.2);
            border:1px solid #2456b8;border-radius:4px;
            padding:4px 10px;margin:3px;font-size:12px}}
  .status{{display:inline-block;padding:3px 10px;border-radius:12px;
            font-size:11px;font-weight:bold;
            background:{st_colour}33;border:1px solid {st_colour};
            color:{st_colour}}}
  a{{color:#7eb3ff;text-decoration:none}}
  a:hover{{text-decoration:underline}}
  code{{background:rgba(255,255,255,.07);padding:2px 6px;
         border-radius:3px;color:#e8b84b;font-size:12px}}
  .ep{{display:grid;grid-template-columns:120px 1fr;gap:4px;
        margin:3px 0;font-size:12px}}
  .method{{color:#5de0a0}}
  .sep{{border:none;border-top:1px solid rgba(255,255,255,.07);margin:14px 0}}
</style></head><body>
<h1>IHCEI QG-COS API</h1>
<div class="tag">INTEGRATED HUMAN-CENTRIC ETHICAL INTELLIGENCE &nbsp;·&nbsp; v12.0</div>
<hr class="sep">

<div class="card">
  <div class="tag">LIVE NETWORK STATUS</div><br>
  <span class="metric">λ₂ = {l2:.4f}</span>
  <span class="metric">ħ = {net['hbar']:.4f}</span>
  <span class="metric">Concepts: {pc}</span>
  &nbsp;<span class="status">● {st}</span>
</div>

<div class="card">
  <div class="tag">THREE EQUATIONS</div>
  <div class="eq">E = U · D²</div>
  <div class="eq">Ψ = Aₙ(Φ) · ψ · exp(i·S/ħ)</div>
  <div class="eq">C_dev = λ₂(L_GP)</div>
  <div style="color:#5a5a6a;font-size:11px;margin-top:6px">
    Al-3assr: D evaluated before U · Purpose precedes function
  </div>
</div>

<h2>ENDPOINTS</h2>
<div class="card">
  <div class="ep"><span class="method">POST</span><span>
    <a href="/docs#/LLM%20Interface/llm_query_llm_post"><code>/llm</code></a>
    — <b>Start here.</b> Any LLM sends a message, receives governance metrics + plain English
  </span></div>
  <div class="ep"><span class="method">POST</span><span>
    <a href="/docs#/Core/process_concept_process_post"><code>/process</code></a>
    — Single concept → D, E, λ₂, root class, interpretation
  </span></div>
  <div class="ep"><span class="method">POST</span><span>
    <a href="/docs#/Core/translate_concepts_translate_post"><code>/translate</code></a>
    — N concepts from different fields → one governance language
  </span></div>
  <div class="ep"><span class="method">POST</span><span>
    <a href="/docs#/Core/compare_two_compare_post"><code>/compare</code></a>
    — Two concepts from different fields → semantic distance + root alignment
  </span></div>
  <div class="ep"><span class="method">POST</span><span>
    <a href="/docs#/Core/batch_process_batch_post"><code>/batch</code></a>
    — Stream of concepts → cumulative Δλ₂ network impact
  </span></div>
  <div class="ep"><span class="method">GET</span><span>
    <a href="/network"><code>/network</code></a>
    — Live λ₂, ħ, network status
  </span></div>
  <div class="ep"><span class="method">GET</span><span>
    <a href="/roots"><code>/roots</code></a>
    — The 10 OQM root classes (governance coordinate system)
  </span></div>
  <div class="ep"><span class="method">GET</span><span>
    <a href="/history"><code>/history</code></a>
    — Session log of all processed concepts
  </span></div>
  <div class="ep"><span class="method">POST</span><span>
    <a href="/reset"><code>/reset</code></a>
    — Reset network to baseline
  </span></div>
</div>

<h2>INTERACTIVE DOCS</h2>
<div class="card">
  <a href="/docs">▶ Swagger UI — test all endpoints in browser</a><br>
  <a href="/redoc">▶ ReDoc — clean reference documentation</a>
</div>

<h2>LLM INTEGRATION — QUICK COPY</h2>
<div class="card" style="font-size:11px;color:#8899bb">
  <div style="color:#5de0a0;margin-bottom:6px">▸ Gemini / ChatGPT / Claude / NotebookLM</div>
  POST /llm<br>
  {{"message": "your concept here", "source_llm": "gemini", "field": "physics"}}
  <br><br>
  <div style="color:#5de0a0;margin-bottom:6px">▸ Cross-field translation</div>
  POST /translate<br>
  {{"concepts":["entropy","moral hazard","mens rea"],"fields":["physics","economics","law"]}}
</div>

<div style="margin-top:20px;font-size:10px;color:#3a4468">
  IHCEI QG-COS v12.0 &nbsp;·&nbsp; Boot: {BOOT_TIME} &nbsp;·&nbsp;
  E=U·D² | Ψ=Aₙ(Φ)·ψ·e^(iS/ħ) | C_dev=λ₂
</div>
</body></html>""")


@app.get("/roots", tags=["System"], summary="The 10 OQM governance root classes")
def get_roots():
    return {
        "description": "10 Elements of Deen — OQM governance coordinate system",
        "principle":   "Every concept from every field maps to one governing root. No synonymy.",
        "roots": [{"index": i, "name": n} for i, n in enumerate(ROOT_NAMES)],
    }


@app.get("/network", tags=["System"], summary="Live network health")
def network():
    return ENGINE.snapshot()


@app.get("/history", tags=["System"], summary="Session log")
def history(limit: int = 100):
    recent = ENGINE.log[-limit:]
    return {"total": len(ENGINE.log), "showing": len(recent), "log": recent}


@app.post("/reset", tags=["System"], summary="Reset network to baseline")
def reset():
    ENGINE.reset()
    return {"status": "reset", "message": "Network and session log cleared."}


@app.post("/llm", tags=["LLM Interface"],
          summary="▶ PRIMARY — Send any message from any LLM")
def llm_query(req: LLMReq):
    """
    **The main endpoint for LLM → IHCEI communication.**

    Any LLM (Gemini, ChatGPT, Claude, NotebookLM) sends a natural language
    message. IHCEI returns:
    - Governance metrics (D, E, λ₂, root class)
    - Plain English interpretation
    - A pre-formatted `llm_response` string the LLM can include directly in output

    No technical knowledge required from the calling LLM.
    """
    try:
        r   = ENGINE.process(req.message, req.field)
        kp  = r["kitchen"]
        net = r["adge"]
        s   = r["summary"]

        llm_text = (
            f"[IHCEI QG-COS — {req.source_llm.upper()}]\n"
            f"{'─'*50}\n"
            f"Concept        : {req.message}\n"
            f"Field          : {req.field}\n"
            f"{'─'*50}\n"
            f"Governing Root : {kp['root_name']}  (index {kp['root_idx']})\n"
            f"Protocol Truth : D = {kp['D']:.4f}  "
            + ("✔ ALIGNED" if kp['D'] > 0.3 else "⚠ LOW ALIGNMENT") + "\n"
            f"Utility        : U = {kp['U']:.4f}\n"
            f"Essence        : E = U·D² = {kp['E']:.4f}  "
            + ("PROPAGATING" if not kp['collapsed'] else "COLLAPSED") + "\n"
            f"Network Health : λ₂ = {net['lambda2']:.4f}  [{net['status']}]\n"
            f"Friction       : ħ = {net['hbar']:.4f}\n"
            f"{'─'*50}\n"
            f"Alignment : {s['level']} — root class '{s['root']}'\n"
            f"Pharaoh Filter: {'ACTIVE — perception suppressed' if s['pharaoh'] else 'CLEAR'}\n"
            f"Network       : {s['network']}\n"
        )

        return {
            "source_llm" : req.source_llm,
            "timestamp"  : datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "D"       : kp["D"],
                "E"       : kp["E"],
                "lambda2" : net["lambda2"],
                "hbar"    : net["hbar"],
                "root"    : kp["root_name"],
                "status"  : net["status"],
                "collapsed": kp["collapsed"],
            },
            "summary"     : s,
            "llm_response": llm_text,   # ← paste this directly into LLM output
            "full"        : r,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/process", tags=["Core"], summary="Single concept — full pipeline")
def process_concept(req: ConceptReq):
    """Full QG-COS pipeline. Returns Kitchen Protocol + TQG-CFE + ADGE."""
    try:
        return ENGINE.process(req.concept, req.field, req.observer, req.lr)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/compare", tags=["Core"], summary="Compare two concepts across fields")
def compare_two(req: CompareReq):
    """
    Are two concepts from different fields compatible in the same governance language?
    Returns cosine similarity, root class alignment, cross-field compatibility flag.
    """
    try:
        return ENGINE.compare(req.concept_a, req.concept_b, req.field_a, req.field_b)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/translate", tags=["Core"],
          summary="Translate N concepts from different fields into one language")
def translate_concepts(req: TranslateReq):
    """
    **The cross-domain translation endpoint.**

    Submit concepts from physics, law, medicine, economics — any field.
    Each concept is mapped to the same 10-root OQM coordinate system.
    Concepts sharing the same governing root can formally communicate.
    """
    try:
        fields = req.fields or ["general"] * len(req.concepts)
        if len(fields) != len(req.concepts):
            raise HTTPException(422, "'fields' must match length of 'concepts'")
        return ENGINE.translate(req.concepts, fields)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/batch", tags=["Core"],
          summary="Process multiple concepts — network accumulates")
def batch_process(req: BatchReq):
    """
    Stream of concepts → per-concept metrics + Δλ₂ summary.
    Shows whether the batch collectively improved or degraded network cohesion.
    """
    try:
        snap_before = ENGINE.snapshot()["adge"]["lambda2"]
        results = []
        for item in req.concepts:
            r = ENGINE.process(item.concept, item.field, item.observer, item.lr)
            results.append(dict(
                concept=item.concept, field=item.field,
                D=r["kitchen"]["D"], E=r["kitchen"]["E"],
                root=r["kitchen"]["root_name"],
                lambda2=r["adge"]["lambda2"],
                collapsed=r["kitchen"]["collapsed"],
            ))
        snap_after = results[-1]["lambda2"] if results else snap_before
        delta = snap_after - snap_before
        mean_D = float(np.mean([x["D"] for x in results])) if results else 0

        return {
            "count"  : len(results),
            "results": results,
            "summary": {
                "lambda2_before": round(snap_before, 5),
                "lambda2_after" : round(snap_after,  5),
                "delta_lambda2" : round(delta, 5),
                "mean_D"        : round(mean_D, 4),
                "trend"         : "IMPROVING" if delta > 0 else "DEGRADING",
                "interpretation": (
                    f"{len(results)} concepts · Δλ₂={delta:+.5f} · mean D={mean_D:.3f}. "
                    + ("Network cohesion improved."
                       if delta > 0 else "Network cohesion degraded.")
                ),
            }
        }
    except Exception as e:
        raise HTTPException(500, str(e))


# ══════════════════════════════════════════════════════════════════════
# SECTION 6 — STARTUP
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    PORT = int(os.environ.get("PORT", 8000))

    # ── Try ngrok tunnel automatically ────────────────────────────────
    public_url = None
    try:
        from pyngrok import ngrok
        token = os.environ.get("NGROK_AUTHTOKEN", "")
        if token:
            ngrok.set_auth_token(token)
        tunnel     = ngrok.connect(PORT)
        public_url = tunnel.public_url
    except ImportError:
        pass
    except Exception as e:
        print(f"  [ngrok] Could not create tunnel: {e}")

    print("\n" + "═"*60)
    print("  IHCEI QG-COS API  —  v12.0")
    print("═"*60)
    print(f"  Local :  http://localhost:{PORT}")
    if public_url:
        print(f"  PUBLIC:  {public_url}   ← share this with LLMs")
        print(f"  Docs  :  {public_url}/docs")
        print(f"  /llm  :  {public_url}/llm")
    else:
        print(f"  Docs  :  http://localhost:{PORT}/docs")
        print(f"\n  TIP: pip install pyngrok  →  re-run to get a public URL")
    print("═"*60 + "\n")

    uvicorn.run("ihcei_server:app", host="0.0.0.0", port=PORT, reload=False)
