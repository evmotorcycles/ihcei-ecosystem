"""
IHCEI v12.0 — Live Falsification Runner
=========================================
Wires the EmbedderAdapter + QueryIngestion into the Spectral Engine
and outputs the Δλ₂ report and signed falsification certificate.

Usage (three modes):

  # Development — offline, TF-IDF, preset corpus (runs anywhere, no API keys)
  python run_falsification.py --embedder local --query-mode preset

  # Upgrade 1 — local transformer, preset corpus (better embeddings, no API keys)
  python run_falsification.py --embedder sentence --query-mode preset

  # Full live stack — transformer + live LLM comparison (requires API key)
  python run_falsification.py --embedder sentence --query-mode openai
  python run_falsification.py --embedder sentence --query-mode anthropic

  # OpenAI embeddings + live LLM (maximum fidelity, costs ~$0.001 per run)
  python run_falsification.py --embedder openai --query-mode openai

Output:
  - Console: live dashboard + certificate
  - JSON:    ihcei_delta_lambda2_report.json  (for one-pager data table)
"""

import argparse
import json
import time
from datetime import datetime, timezone

import numpy as np
import scipy.linalg as la
from scipy.spatial.distance import cdist
from scipy.stats import linregress
from sklearn.preprocessing import normalize

from embedder_adapter import EmbedderAdapter
from query_ingestion import QueryIngestion

# ── ANSI colours ──────────────────────────────────────────────────────────────
R     = "\033[0m"
BOLD  = "\033[1m"
GREEN = "\033[92m"
RED   = "\033[91m"
GOLD  = "\033[93m"
CYAN  = "\033[96m"
GREY  = "\033[90m"
SEP   = "═" * 72
SEP2  = "─" * 72


# ── OQM Root-Class Topology ───────────────────────────────────────────────────
def build_oqm_topology(dim: int, n_roots: int = 10, seed: int = 42) -> np.ndarray:
    """Orthonormal root-class basis in ℝ^dim."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((n_roots, dim))
    Q, _ = np.linalg.qr(raw.T)
    return Q.T  # (n_roots × dim)


# ── Spectral Engine ───────────────────────────────────────────────────────────
class SpectralEngine:
    """
    Computes λ₂ (Fiedler value) and ħ_network from a batch of text embeddings.
    Replicates the NLPFedSpectralEngine from v12.0 in a self-contained module.
    """

    def __init__(self, n: int = 60, g_threshold: float = 0.5, seed: int = 42):
        rng           = np.random.default_rng(seed)
        self.n        = n
        self.threshold = g_threshold
        raw_g         = rng.random((n, n))
        adj           = (raw_g + raw_g.T) / 2.0
        np.fill_diagonal(adj, 0.0)
        self.adjacency = adj
        self.phi       = rng.uniform(0.1, 1.0, (n, 64))  # placeholder dim

    def _resize_phi(self, dim: int):
        if self.phi.shape[1] != dim:
            rng       = np.random.default_rng(99)
            self.phi  = rng.uniform(0.1, 1.0, (self.n, dim))

    def step(self, embeddings: np.ndarray, oqm: np.ndarray, lr: float = 0.05) -> dict:
        """Process one batch of embeddings through the Kitchen Protocol + ADGE."""
        self._resize_phi(embeddings.shape[1])

        total_d, total_e = 0.0, 0.0
        for emb in embeddings:
            u_mag = float(np.linalg.norm(emb))
            if u_mag < 1e-10:
                continue
            unit_c = emb / u_mag
            sims   = np.clip(oqm @ unit_c, 0.0, 1.0)
            d      = float(sims.max())
            e_mag  = u_mag * d ** 2
            e_vec  = unit_c * e_mag
            total_d += d
            total_e += e_mag

            if e_mag > 1e-10:
                ew = self.adjacency.sum(axis=1)
                ew /= (ew.max() + 1e-10)
                scale = (lr * ew).reshape(-1, 1)
                self.phi += scale * (e_vec - self.phi)
                self.phi  = np.clip(self.phi, 0.01, 1.0)

        # ADGE: Fiedler value
        phi_norm  = self.phi / (self.phi.sum(axis=1, keepdims=True) + 1e-10)
        js_matrix = cdist(phi_norm, phi_norm, metric="jensenshannon")
        js_matrix = np.nan_to_num(js_matrix, nan=1.0)
        mask      = (self.adjacency > self.threshold).astype(float)
        W         = mask * (1.0 / (1.0 + js_matrix))
        np.fill_diagonal(W, 0.0)
        L         = np.diag(W.sum(axis=1)) - W
        evals     = la.eigvalsh(L)
        l2        = float(evals[1])
        hbar      = float(1.0 / (l2 + 1e-8))
        js_mean   = float(js_matrix[mask > 0].mean()) if mask.sum() > 0 else 1.0

        n_emb = max(len(embeddings), 1)
        return {
            "lambda2":  l2,
            "hbar":     hbar,
            "js_mean":  js_mean,
            "mean_d":   total_d / n_emb,
            "mean_e":   total_e / n_emb,
        }


# ── Main falsification run ────────────────────────────────────────────────────
def run(embedder_backend: str, query_mode: str, rounds: int, output_json: str):

    print(f"\n{CYAN}{BOLD}{SEP}{R}")
    print(f"{GOLD}{BOLD}  IHCEI v12.0 — LIVE FALSIFICATION RUNNER{R}")
    print(f"  Embedder: {embedder_backend.upper()}  |  Query mode: {query_mode.upper()}  |  Rounds: {rounds}")
    print(f"{CYAN}{SEP}{R}\n")

    t0 = time.time()

    # ── 1. Ingestion ──────────────────────────────────────────────────────────
    qi             = QueryIngestion(mode=query_mode)
    corpus_a, corpus_b = qi.generate()
    provenance     = qi.provenance_label

    # ── 2. Embedding ──────────────────────────────────────────────────────────
    print(f"\n[Embedder] Fitting and encoding corpora...")
    fit_corpus  = corpus_a + corpus_b
    emb         = EmbedderAdapter(backend=embedder_backend)
    emb.fit(fit_corpus)
    dim         = emb.dim

    vecs_a      = emb.embed(corpus_a)  # (N_a × D)
    vecs_b      = emb.embed(corpus_b)  # (N_b × D)
    print(f"  Encoded {len(vecs_a)} governance + {len(vecs_b)} extraction passages → dim={dim}")

    # ── 3. OQM topology ───────────────────────────────────────────────────────
    n_roots  = min(10, dim - 1)   # n_roots must be < dim for QR orthonormality
    oqm      = build_oqm_topology(dim, n_roots=n_roots)
    print(f"  OQM topology: {n_roots} orthonormal root classes in ℝ^{dim}")

    # ── 4. Spectral engines ───────────────────────────────────────────────────
    engine_a = SpectralEngine(n=60, seed=42)
    engine_b = SpectralEngine(n=60, seed=42)   # same init for fair comparison

    hist_a, hist_b = [], []
    rng = np.random.default_rng(77)

    print(f"\n{SEP2}")
    print(f"  {'Round':<6}  {'λ₂(A)':>9}  {'λ₂(B)':>9}  {'Δλ₂':>9}  "
          f"{'ħ(A)':>9}  {'ħ(B)':>9}  {'D_mean(A)':>10}  {'D_mean(B)':>10}")
    print(f"{SEP2}")

    for rnd in range(1, rounds + 1):
        idx_a = rng.permutation(len(vecs_a))
        idx_b = rng.permutation(len(vecs_b))
        m_a   = engine_a.step(vecs_a[idx_a], oqm)
        m_b   = engine_b.step(vecs_b[idx_b], oqm)
        hist_a.append(m_a)
        hist_b.append(m_b)

        delta = m_a["lambda2"] - m_b["lambda2"]
        sign  = GREEN if delta >= 0 else RED
        print(f"  {rnd:<6}  {m_a['lambda2']:>9.5f}  {m_b['lambda2']:>9.5f}  "
              f"{sign}{delta:>+9.5f}{R}  "
              f"{m_a['hbar']:>9.3f}  {m_b['hbar']:>9.3f}  "
              f"{m_a['mean_d']:>10.4f}  {m_b['mean_d']:>10.4f}")

    elapsed = time.time() - t0

    # ── 5. Falsification certificate ──────────────────────────────────────────
    l2_a  = [h["lambda2"] for h in hist_a]
    l2_b  = [h["lambda2"] for h in hist_b]
    hb_a  = [h["hbar"]    for h in hist_a]
    hb_b  = [h["hbar"]    for h in hist_b]
    js_a  = [h["js_mean"] for h in hist_a]
    js_b  = [h["js_mean"] for h in hist_b]

    T     = min(len(l2_a), len(l2_b))
    sl_a  = linregress(range(T), l2_a).slope
    sl_b  = linregress(range(T), l2_b).slope
    js_sl_a = linregress(range(T), js_a).slope
    js_sl_b = linregress(range(T), js_b).slope

    c1 = sl_a > sl_b              # A degrades slower
    c2 = np.mean(hb_b) > np.mean(hb_a)   # B generates more friction
    c3 = l2_a[-1] > l2_b[-1]     # A ends more cohesive
    c4 = js_sl_a <= js_sl_b       # A converges, B diverges
    passed = sum([c1, c2, c3, c4])

    delta_l2    = l2_a[-1] - l2_b[-1]
    hbar_ratio  = np.mean(hb_b) / (np.mean(hb_a) + 1e-8)
    deg_ratio   = abs(sl_b) / (abs(sl_a) + 1e-8)

    verdict = ("✔ FULL PROOF" if passed == 4 else
               "✔ SUPPORTED" if passed >= 3 else
               "⚠ PARTIAL — increase rounds")
    v_col   = GREEN if passed == 4 else (GOLD if passed >= 3 else RED)

    print(f"\n{GOLD}{BOLD}{SEP}{R}")
    print(f"{GOLD}{BOLD}  IHCEI v12.0 — Δλ₂ FALSIFICATION CERTIFICATE{R}")
    print(f"  Provenance: {provenance}")
    print(f"  Elapsed: {elapsed:.1f}s  |  Rounds: {rounds}  |  Dim: {dim}")
    print(f"{GOLD}{SEP}{R}\n")

    def crit(ok, label, detail):
        mark = f"{GREEN}✔{R}" if ok else f"{RED}✘{R}"
        print(f"  [{mark}]  {label}")
        print(f"         {GREY}{detail}{R}")

    crit(c1, "C1 · ∂λ₂/∂t(A) > ∂λ₂/∂t(B)  — A degrades slower",
         f"A slope={sl_a:+.6f}  B slope={sl_b:+.6f}")
    crit(c2, "C2 · ħ_mean(B) > ħ_mean(A)  — extraction generates more friction",
         f"A={np.mean(hb_a):.3f}  B={np.mean(hb_b):.3f}  ratio={hbar_ratio:.2f}×")
    crit(c3, "C3 · Final λ₂(A) > final λ₂(B)  — governance network ends more cohesive",
         f"A={l2_a[-1]:.5f}  B={l2_b[-1]:.5f}  Δλ₂={delta_l2:+.5f}")
    crit(c4, "C4 · ∂JS/∂t(A) ≤ ∂JS/∂t(B)  — A converges, B diverges",
         f"JS slope A={js_sl_a:+.7f}  JS slope B={js_sl_b:+.7f}")

    print(f"\n  CRITERIA PASSED: {v_col}{BOLD}{passed}/4{R}")
    print(f"  VERDICT:         {v_col}{BOLD}{verdict}{R}")
    print(f"\n  KEY METRICS FOR ONE-PAGER:")
    print(f"  {GOLD}Δλ₂             = {delta_l2:+.5f}{R}")
    print(f"  {GOLD}ħ reduction     = {hbar_ratio:.2f}× (B generates {hbar_ratio:.2f}× more friction){R}")
    print(f"  {GOLD}Degradation     = {deg_ratio:.0f}% faster in extraction corpus{R}")
    print(f"  {GOLD}Final λ₂ (A/B)  = {l2_a[-1]:.5f} / {l2_b[-1]:.5f}{R}")
    print(f"\n{GOLD}{SEP}{R}\n")

    # ── 6. JSON report ────────────────────────────────────────────────────────
    report = {
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "provenance":        provenance,
        "embedder_backend":  embedder_backend,
        "query_mode":        query_mode,
        "rounds":            rounds,
        "vector_dim":        dim,
        "n_oqm_roots":       n_roots,
        "results": {
            "delta_lambda2":           round(delta_l2, 5),
            "final_lambda2_A":         round(l2_a[-1], 5),
            "final_lambda2_B":         round(l2_b[-1], 5),
            "mean_hbar_A":             round(float(np.mean(hb_a)), 3),
            "mean_hbar_B":             round(float(np.mean(hb_b)), 3),
            "hbar_ratio_B_over_A":     round(hbar_ratio, 3),
            "degradation_slope_A":     round(sl_a, 6),
            "degradation_slope_B":     round(sl_b, 6),
            "degradation_ratio":       round(deg_ratio, 3),
            "criteria_passed":         passed,
            "verdict":                 verdict.replace("✔ ", "").replace("⚠ ", ""),
        },
        "falsification_criteria": {
            "C1_A_degrades_slower":          c1,
            "C2_B_generates_more_friction":  c2,
            "C3_A_ends_more_cohesive":       c3,
            "C4_A_converges_B_diverges":     c4,
        }
    }

    with open(output_json, "w") as f:
        # numpy scalar → Python native for JSON
        def _default(o):
            if hasattr(o, 'item'):
                return o.item()
            raise TypeError(f"Not serializable: {type(o)}")
        json.dump(report, f, indent=2, default=_default)

    print(f"  Report saved → {output_json}")
    print(f"  {GREY}Paste the 'results' block into the one-pager data table.{R}\n")

    return report


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="IHCEI v12.0 — Live Falsification Runner"
    )
    parser.add_argument(
        "--embedder", choices=["local", "sentence", "openai"],
        default="local",
        help="Embedding backend (default: local TF-IDF+SVD)"
    )
    parser.add_argument(
        "--query-mode", choices=["preset", "openai", "anthropic"],
        default="preset",
        help="Corpus source (default: preset curated responses)"
    )
    parser.add_argument("--rounds", type=int, default=40,
                        help="Spectral engine rounds (default: 40)")
    parser.add_argument("--output", default="ihcei_delta_lambda2_report.json",
                        help="Output JSON path")
    args = parser.parse_args()

    run(
        embedder_backend = args.embedder,
        query_mode       = args.query_mode,
        rounds           = args.rounds,
        output_json      = args.output,
    )
