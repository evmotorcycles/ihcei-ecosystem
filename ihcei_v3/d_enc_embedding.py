"""
d_enc_embedding.py
==================
Phase 2 D_enc Proxy Upgrade — Sentence Embedding Cosine Similarity
GT v18.0 / QG-COS

WHAT THIS MODULE DOES
---------------------
Replaces the Phase 1 TF-IDF keyword-counting D_enc proxy with deep
sentence embedding cosine similarity against a fixed OQM reference frame.

WHY THIS UPGRADE IS NECESSARY
------------------------------
Phase 1 finding: TF-IDF keyword scoring on Enron emails produced a
flat D-score (0.433-0.468) right through the collapse, declining only
AFTER the bankruptcy (2002Q1 = 0.344). This makes the proxy a lagging
indicator, not a leading one.

Root cause: TF-IDF counts token frequency. Enron executives maintained
all the correct governance vocabulary throughout the collapse — the word
"audit" appeared regularly in emails while audits were being falsified.
TF-IDF is measuring surface compliance (As-Sidq, the peel) not operational
governance truth (Al-Haqq, the juice).

The Pharaoh Signature hypothesis: Enron represents D_enc (encoding fidelity,
measured from text) remaining high while D_dec (decoding fidelity, measured
from behavior) collapsed to zero. The product D = D_enc × D_dec → 0, but
TF-IDF only measured D_enc. To detect this pattern requires:
  1. D_enc upgrade: sentence embeddings that measure DIRECTIONAL MEANING,
     not keyword frequency. An embedding model cannot be fooled by repeating
     the word "audit" while describing fraud — the semantic direction of the
     surrounding text will diverge from the OQM reference frame.
  2. D_dec measurement (separate module): behavioral telemetry — rework rates,
     verification failure rates, enforcement action timing. This requires
     Jira/GitHub/audit-log data, not email text.

This module provides the D_enc upgrade only. D_dec remains Phase 2 pending
behavioral data.

EPISTEMIC STATUS
----------------
Layer 1 (falsifiable): cosine similarity computation is deterministic
Layer 2 (developing): the OQM reference frame embedding is a design choice
                      that requires validation against ground-truth D_enc data
Layer 3 (not claimed): no ontological claim about the nature of truth

DEPENDENCY NOTE
---------------
This module requires sentence-transformers or a compatible embedding backend.
In environments without internet access, it falls back to a TF-IDF baseline
with improved governance/anti-governance weighting — more precise than Phase 1
but not the full embedding upgrade.

ARCHITECTURE
------------
OQM Reference Frame = a fixed set of methodology-documenting sentences
representing high-D governance communication. Embeddings are computed once
and cached. Each new text is embedded and compared via cosine similarity
to the reference centroid.

The reference frame is inspired by the 7 stages of Al-Asr pressing:
Stage 1 (TIN): clear source identification
Stage 2 (SULALAH): extraction of operative claim
Stage 4 (ALAQAH): connection to Deen elements
Stage 7 (LAHM): falsifiability statement

A text that semantically aligns with all four stages has D_enc → 1.
A text that aligns with none has D_enc → 0.
"""

from __future__ import annotations
import hashlib
import math
import re
import time
from dataclasses import dataclass
from typing import List, Optional

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# OQM REFERENCE FRAME — the governance protocol standard
# Fixed embedding target: high-D methodology-documenting communication
# ─────────────────────────────────────────────────────────────────────────────

OQM_REFERENCE_SENTENCES = [
    # Stage 1 — TIN: Source identification
    "The data source is clearly identified and independently verifiable.",
    "This analysis draws from the following documented methodology.",
    "All figures are traceable to primary sources listed in Appendix A.",
    "The empirical basis for this claim is the following dataset.",

    # Stage 2 — SULALAH: Extraction
    "The operative claim extracted from the evidence is as follows.",
    "Stripping procedural context, the core governance decision is this.",
    "The methodology used to derive this conclusion is documented below.",
    "The extraction process applied was the following sequential procedure.",

    # Stage 4 — ALAQAH: Connection to governance elements
    "This decision preserves human agency by offering the following options.",
    "The verification pathway for this claim is the following independent check.",
    "Alternatives considered were as follows, with reasons for selection.",
    "The authority responsible for this decision is the following party.",

    # Stage 7 — LAHM: Falsifiability
    "This claim would be falsified if the following condition were observed.",
    "The following test would disprove this assertion.",
    "A counter-instance that would refute this is the following scenario.",
    "This prediction is falsifiable by the following empirical measurement.",

    # Anti-governance anchors (low-D reference, for range calibration)
    "Trust me on this one.",
    "Just approve it, there is no time to review.",
    "The details are too complex, skip the methodology.",
    "Scholars universally agree, verification is unnecessary.",
]

# Weighted: positive = high-D methodology, negative = low-D bypass
OQM_REFERENCE_WEIGHTS = [1.0] * 16 + [-0.5] * 4  # last 4 are anti-D anchors


# ─────────────────────────────────────────────────────────────────────────────
# IMPROVED TFIDF BASELINE (Phase 1.5 — no embedding backend required)
# ─────────────────────────────────────────────────────────────────────────────

# Expanded governance vocabulary — multi-word and concept-level
HIGH_D_PATTERNS = [
    r"\bmethodology\b", r"\bprocedure\b", r"\bprotocol\b",
    r"\bverif\w+\b",    r"\bauditable\b", r"\baudited\b",
    r"\bfalsifiable\b", r"\btraceable\b", r"\bdocument\w+\b",
    r"\breplicable\b",  r"\bindependent\w+\b", r"\bsource\b",
    r"\bevidence\b",    r"\bdata\b",     r"\breview\b",
    r"\balternative\b", r"\boption\b",   r"\bapproach\b",
    r"\bconsider\w+\b", r"\banalysis\b", r"\bframework\b",
    r"\btransparent\w*\b", r"\baccountable\b", r"\bfalsif\w+\b",
    r"\bgroundtruth\b", r"\bcalibrat\w+\b", r"\bvalidat\w+\b",
]

LOW_D_PATTERNS = [
    r"\bjust\s+do\b",    r"\btrust\s+me\b",   r"\bno\s+time\b",
    r"\burgent\b",       r"\bimmediately\b",  r"\bright\s+now\b",
    r"\bskip\b",         r"\bbypass\b",       r"\bignore\b",
    r"\bdon.t\s+worry\b", r"\bdon.t\s+(need|have)\s+to\b",
    r"\bjust\s+sign\b",  r"\bjust\s+approve\b",
    r"\bno\s+need\s+to\s+(check|verify|review)\b",
    r"\btoo\s+complex\s+for\s+you\b", r"\bscholars\s+agree\b",
    r"\beveryone\s+knows\b", r"\bobviously\b",
    r"\bjust\s+trust\b", r"\bdon.t\s+ask\b",
]


@dataclass
class DENCResult:
    """D_enc computation result with provenance."""
    text_hash: str
    method: str                 # 'embedding' or 'tfidf_enhanced'
    d_enc: float                # 0.0-1.0 encoding fidelity
    high_d_signals: int         # count of methodology-transparency markers
    low_d_signals: int          # count of bypass/authority-override markers
    signal_ratio: float         # high_d / (high_d + low_d + 1)
    semantic_note: str          # what drove the score
    certificate_fragment: str   # partial hash for audit trail


class DENCEngine:
    """
    D_enc computation engine — Phase 2 upgrade from TF-IDF to embeddings.

    Usage:
        engine = DENCEngine()
        result = engine.compute("The methodology is documented below...")
        print(result.d_enc)  # 0.0-1.0
    """

    def __init__(self, use_embeddings: bool = True, verbose: bool = False):
        self.verbose = verbose
        self.embedding_available = False
        self._reference_matrix = None
        self._reference_weights = np.array(OQM_REFERENCE_WEIGHTS)

        if use_embeddings:
            self._try_load_embeddings()

        # Compile patterns
        self._high_d = [re.compile(p, re.IGNORECASE) for p in HIGH_D_PATTERNS]
        self._low_d  = [re.compile(p, re.IGNORECASE) for p in LOW_D_PATTERNS]

    def _try_load_embeddings(self):
        """Attempt to load sentence-transformers. Gracefully degrade."""
        try:
            from sentence_transformers import SentenceTransformer
            if self.verbose:
                print("Loading sentence embedding model...")
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
            # Pre-compute reference frame embeddings
            self._reference_matrix = self._model.encode(
                OQM_REFERENCE_SENTENCES, convert_to_numpy=True,
                show_progress_bar=False
            )
            self.embedding_available = True
            if self.verbose:
                print("Embedding backend: sentence-transformers (all-MiniLM-L6-v2)")
        except ImportError:
            if self.verbose:
                print("sentence-transformers not available. Using TF-IDF enhanced baseline.")
        except Exception as e:
            if self.verbose:
                print(f"Embedding load failed: {e}. Using TF-IDF enhanced baseline.")

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def _compute_embedding_d_enc(self, text: str) -> float:
        """
        D_enc via sentence embedding cosine similarity.
        D_i(t) = weighted_mean_j cos(x_i, x_j_protocol)
        where positive weights = high-D anchors, negative = low-D anchors.
        """
        text_emb = self._model.encode([text], convert_to_numpy=True,
                                       show_progress_bar=False)[0]

        # Cosine similarity to each reference sentence
        sims = np.array([
            self._cosine(text_emb, ref_emb)
            for ref_emb in self._reference_matrix
        ])

        # Weighted mean: positive weight for high-D refs, negative for anti-D refs
        weighted_sim = np.sum(sims * self._reference_weights) / np.sum(np.abs(self._reference_weights))

        # Normalise from [-1,1] weighted space to [0,1]
        d_enc = (weighted_sim + 1.0) / 2.0
        return round(float(np.clip(d_enc, 0.0, 1.0)), 4)

    def _compute_tfidf_d_enc(self, text: str) -> tuple:
        """
        D_enc via enhanced TF-IDF keyword scoring (Phase 1.5 baseline).
        More precise than Phase 1: uses multi-word patterns and
        penalises low-D signals rather than ignoring them.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        total = max(len(words), 1)

        high_d = sum(1 for p in self._high_d if p.search(text))
        low_d  = sum(1 for p in self._low_d  if p.search(text))

        # Balanced score: reward high-D, penalise low-D
        # Range: all low-D → 0.0, all high-D → 1.0
        raw = (high_d - low_d * 1.5) / (high_d + low_d * 1.5 + 1.0)
        d_enc = (raw + 1.0) / 2.0  # normalise to [0,1]
        d_enc = round(float(np.clip(d_enc, 0.0, 1.0)), 4)

        return d_enc, high_d, low_d

    def compute(self, text: str) -> DENCResult:
        """
        Compute D_enc for a single text.

        Parameters
        ----------
        text : str
            The communication text to evaluate.

        Returns
        -------
        DENCResult
        """
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:12].upper()

        # Try embedding method first
        if self.embedding_available and self._reference_matrix is not None:
            d_enc = self._compute_embedding_d_enc(text)
            _, hd, ld = self._compute_tfidf_d_enc(text)  # still count signals
            method = "embedding"
            note = (f"Embedding cosine similarity against OQM reference frame "
                   f"(16 high-D + 4 low-D anchors). Signal counts: "
                   f"+{hd} governance, -{ld} bypass.")
        else:
            d_enc, hd, ld = self._compute_tfidf_d_enc(text)
            method = "tfidf_enhanced"
            note = (f"Enhanced TF-IDF with governance/bypass pattern scoring. "
                   f"+{hd} methodology signals, -{ld} bypass signals. "
                   f"Upgrade to embedding backend for higher precision.")

        signal_ratio = hd / (hd + ld + 1)

        # Certificate fragment
        cert = hashlib.sha256(
            f"{text_hash}|{d_enc:.4f}|{method}".encode()
        ).hexdigest()[:16].upper()

        return DENCResult(
            text_hash=text_hash,
            method=method,
            d_enc=d_enc,
            high_d_signals=hd,
            low_d_signals=ld,
            signal_ratio=signal_ratio,
            semantic_note=note,
            certificate_fragment=cert
        )

    def compute_batch(self, texts: List[str],
                      timestamps: Optional[List[str]] = None) -> List[DENCResult]:
        """Compute D_enc for a list of texts. Uses batch embedding if available."""
        if self.embedding_available and len(texts) > 1:
            # Batch encode for efficiency
            embeddings = self._model.encode(
                texts, convert_to_numpy=True, show_progress_bar=False,
                batch_size=32
            )
            results = []
            for i, (text, emb) in enumerate(zip(texts, embeddings)):
                text_hash = hashlib.sha256(text.encode()).hexdigest()[:12].upper()
                sims = np.array([self._cosine(emb, ref) for ref in self._reference_matrix])
                weighted_sim = np.sum(sims * self._reference_weights) / np.sum(np.abs(self._reference_weights))
                d_enc = round(float(np.clip((weighted_sim + 1.0) / 2.0, 0.0, 1.0)), 4)
                _, hd, ld = self._compute_tfidf_d_enc(text)
                cert = hashlib.sha256(f"{text_hash}|{d_enc:.4f}".encode()).hexdigest()[:16].upper()
                results.append(DENCResult(
                    text_hash=text_hash, method="embedding",
                    d_enc=d_enc, high_d_signals=hd, low_d_signals=ld,
                    signal_ratio=hd / (hd + ld + 1),
                    semantic_note=f"Batch embedding. Signals: +{hd}/-{ld}",
                    certificate_fragment=cert
                ))
            return results
        else:
            return [self.compute(t) for t in texts]

    def quarterly_trend(self, texts: List[str], quarters: List[str],
                        verbose: bool = True) -> dict:
        """
        Compute quarterly mean D_enc for temporal collapse detection.
        This is the Phase 2 Enron test: does D_enc decline before collapse?

        Parameters
        ----------
        texts : List[str]
        quarters : List[str]  e.g. ['2000-Q1', '2000-Q2', ...]

        Returns
        -------
        dict: quarter → mean D_enc
        """
        results = self.compute_batch(texts)
        q_data: dict = {}
        for r, q in zip(results, quarters):
            if q not in q_data:
                q_data[q] = []
            q_data[q].append(r.d_enc)

        trend = {q: round(float(np.mean(vals)), 4) for q, vals in sorted(q_data.items())}

        if verbose:
            print("\nQuarterly D_enc trend:")
            for q, d in trend.items():
                bar = "█" * int(d * 20)
                print(f"  {q}: D_enc={d:.4f}  {bar}")

        return trend


# ─────────────────────────────────────────────────────────────────────────────
# D_GAP COMPUTATION (Phase 2 — requires behavioral D_dec data)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DGapResult:
    """
    Pharaoh Signature detector.
    D_gap = D_enc - D_dec
    Persistently positive and widening D_gap = node speaks governance but enacts none.
    """
    d_enc: float
    d_dec: float
    d_gap: float
    d_composite: float          # D = D_enc × D_dec (the real fidelity)
    pharaoh_risk: str           # LOW / MODERATE / HIGH / CRITICAL
    pharaoh_note: str


def compute_d_gap(d_enc: float, d_dec: float) -> DGapResult:
    """
    Compute D_gap = D_enc - D_dec and classify Pharaoh risk.

    D_dec must be measured from behavioral telemetry:
      - Verification failure rate (fraction of governance transactions requiring rework)
      - Enforcement action latency (time between violation detection and penalty)
      - Audit pass rate on execution (not just documentation)

    Until D_dec data is available from organizational telemetry, D_dec
    should not be estimated from text content — this would collapse D_enc
    and D_dec into the same measurement, making D_gap = 0 by construction.
    """
    d_gap = d_enc - d_dec
    d_composite = d_enc * d_dec

    if d_gap < 0.05:
        risk = "LOW"
        note = "D_enc and D_dec aligned. No systematic cognitive dissonance detected."
    elif d_gap < 0.20:
        risk = "MODERATE"
        note = f"D_gap={d_gap:.3f}: modest divergence between stated and enacted governance."
    elif d_gap < 0.40:
        risk = "HIGH"
        note = (f"D_gap={d_gap:.3f}: significant Pharaoh Signature. "
               f"Node communicates governance (D_enc={d_enc:.3f}) "
               f"but execution fidelity is low (D_dec={d_dec:.3f}). "
               f"Monitor for widening gap over time.")
    else:
        risk = "CRITICAL"
        note = (f"D_gap={d_gap:.3f}: critical Pharaoh Node signature. "
               f"D_enc={d_enc:.3f} (high verbal compliance) vs "
               f"D_dec={d_dec:.3f} (near-zero execution fidelity). "
               f"This pattern — high surface governance, near-zero enactment — "
               f"is the configuration that produced Enron-style collapse: "
               f"E = U × (D_enc × D_dec)² = U × {d_composite:.4f}² → 0.")

    return DGapResult(
        d_enc=d_enc, d_dec=d_dec, d_gap=d_gap,
        d_composite=d_composite,
        pharaoh_risk=risk, pharaoh_note=note
    )


# ─────────────────────────────────────────────────────────────────────────────
# FRICTION SIGNAL F(t) — systemic governance noise measurement
# ─────────────────────────────────────────────────────────────────────────────

def compute_friction_signal(d_scores_series: List[float],
                            delay_series: List[float],
                            rework_series: List[float],
                            alpha: float = 0.4,
                            beta: float = 0.3,
                            gamma: float = 0.3) -> dict:
    """
    F(t) = α·Var(D(t)) + β·Delay(t) + γ·Rework(t)

    Parameters
    ----------
    d_scores_series : List[float]
        D-scores over time (per transaction or per period)
    delay_series : List[float]
        Mean response/acknowledgement latency (normalised 0-1)
    rework_series : List[float]
        Fraction of governance transactions requiring rework (0-1)
    alpha, beta, gamma : float
        Weights summing to 1.0 (default: misalignment_variance=0.4,
        delay=0.3, rework=0.3)

    Returns
    -------
    dict with friction signal components and composite F
    """
    d_arr = np.array(d_scores_series)
    d_arr = d_arr[np.isfinite(d_arr)]

    var_D = float(np.var(d_arr)) if len(d_arr) > 1 else 0.0
    mean_delay = float(np.mean(delay_series)) if delay_series else 0.0
    mean_rework = float(np.mean(rework_series)) if rework_series else 0.0

    F = alpha * var_D + beta * mean_delay + gamma * mean_rework
    F = round(float(np.clip(F, 0.0, 1.0)), 4)

    interpretation = (
        "LOW friction — governance is predictable and execution-consistent." if F < 0.15
        else "MODERATE friction — misalignment detected. Monitor D_gap trend." if F < 0.35
        else "HIGH friction — significant governance entropy. NERE audit recommended." if F < 0.60
        else "CRITICAL friction — systemic governance breakdown. MCI monitoring required."
    )

    return {
        "F_composite": F,
        "var_D_component": round(alpha * var_D, 4),
        "delay_component": round(beta * mean_delay, 4),
        "rework_component": round(gamma * mean_rework, 4),
        "interpretation": interpretation,
        "n_d_scores": len(d_arr),
        "mean_D": round(float(np.mean(d_arr)), 4) if len(d_arr) > 0 else 0.0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────────────────────────────────────

def run_tests():
    print("D_ENC PHASE 2 ENGINE — TEST SUITE")
    print("=" * 60)
    print(f"Note: Tests run with {'embedding' if False else 'TF-IDF enhanced'} backend")
    print(f"(sentence-transformers not available in offline environment)")
    print()

    engine = DENCEngine(use_embeddings=False, verbose=True)

    test_cases = [
        # High-D texts — should score 0.60+
        ("HIGH-D governance",
         "The methodology is documented in Appendix B. All claims are falsifiable. "
         "The source data is traceable and independently verifiable. "
         "Options available: approve, defer, or escalate. The decision is yours."),
        ("HIGH-D Al-Asr pressing",
         "Extraction process applied: stripped surface narrative, identified operative claim, "
         "verified against all source instances. Falsifiable prediction: if condition X occurs, "
         "this analysis is disproved. Verification pathway: run the attached test suite."),
        # Low-D texts — should score 0.30 and below
        ("LOW-D Pharaoh pattern",
         "Trust me on this. Scholars agree. Just approve it, there is no time to review. "
         "The details are too complex for this meeting. Sign off and move on."),
        ("LOW-D authority bypass",
         "Peer-reviewed research confirms this is correct. You don't need to verify the methodology. "
         "Just implement immediately — urgency requires skipping the standard review."),
        # Mid-range — mixed signals
        ("MIXED — partial methodology",
         "The analysis shows strong results but we need an urgent decision by midnight. "
         "Methodology is documented but the details are complex."),
        # Enron-style: governance vocabulary, bypassing intent
        ("ENRON-style Pharaoh",
         "Per our audit protocol, the quarterly review procedure was conducted. "
         "Methodology: standard industry practice. Data: proprietary. "
         "Just sign the authorization — procedures were followed by definition."),
    ]

    print("Individual text D_enc scores:")
    for label, text in test_cases:
        r = engine.compute(text)
        print(f"\n  [{label}]")
        print(f"  D_enc = {r.d_enc:.4f}  method={r.method}")
        print(f"  Signals: +{r.high_d_signals} governance, -{r.low_d_signals} bypass")
        print(f"  Text: '{text[:70]}...'")

    print("\n\nPharaoh Signature (D_gap) computation:")
    cases = [
        (0.72, 0.68, "Aligned executive — speaks and enacts governance"),
        (0.75, 0.12, "Pharaoh Node — Enron-pattern: high D_enc, near-zero D_dec"),
        (0.40, 0.38, "Moderate alignment — minor execution gap"),
        (0.85, 0.05, "Critical Pharaoh — maximum cognitive dissonance"),
    ]
    for d_enc, d_dec, label in cases:
        g = compute_d_gap(d_enc, d_dec)
        print(f"\n  {label}")
        print(f"  D_enc={g.d_enc:.2f}, D_dec={g.d_dec:.2f}, D_gap={g.d_gap:.2f}")
        print(f"  D_composite={g.d_composite:.4f}  Risk: {g.pharaoh_risk}")

    print("\n\nFriction Signal F(t) computation:")
    # Simulated quarterly data for a collapsing organization
    d_scores = [0.65, 0.63, 0.60, 0.55, 0.48, 0.38, 0.25, 0.15]
    delays   = [0.10, 0.12, 0.15, 0.20, 0.30, 0.45, 0.62, 0.78]
    rework   = [0.05, 0.06, 0.10, 0.15, 0.25, 0.38, 0.52, 0.65]
    f = compute_friction_signal(d_scores, delays, rework)
    print(f"  F_composite = {f['F_composite']:.4f}")
    print(f"  Var(D) component: {f['var_D_component']:.4f}")
    print(f"  Delay component:  {f['delay_component']:.4f}")
    print(f"  Rework component: {f['rework_component']:.4f}")
    print(f"  Interpretation: {f['interpretation']}")

    print(f"\n  STATUS: D_ENC PHASE 2 TESTS COMPLETE")
    print(f"  Engine: {engine.embedding_available and 'embedding' or 'tfidf_enhanced'} backend")
    print(f"  Upgrade: install sentence-transformers for full embedding precision")


if __name__ == "__main__":
    run_tests()
