"""
IHCEI v12.0 — Embedder Adapter Layer
=====================================
Drop-in replacement for LocalEmbedder.
Supports three backends, selected via IHCEI_EMBEDDER env var or constructor arg.

Backends:
  local        — TF-IDF + SVD (no dependencies, offline, for development)
  sentence     — SentenceTransformer('all-mpnet-base-v2')  (768-dim, free, local GPU/CPU)
  openai       — text-embedding-3-small  (1536-dim, requires OPENAI_API_KEY)

Usage:
    from embedder_adapter import EmbedderAdapter
    emb = EmbedderAdapter(backend="sentence")   # or "openai" or "local"
    emb.fit(corpus_texts)                        # only required for "local"
    vectors = emb.embed(["text one", "text two"])  # returns np.ndarray (N x D)
"""

import os
import numpy as np
from typing import List, Optional

# ── Local TF-IDF fallback (always available) ──────────────────────────────────
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize


class LocalEmbedder:
    """TF-IDF + SVD — offline, no GPU, 64-dim output. For dev/CI only."""

    def __init__(self, n_components: int = 64, seed: int = 42):
        self.n_components = n_components
        self.vectorizer = TfidfVectorizer(max_features=4000, sublinear_tf=True)
        self.svd = TruncatedSVD(n_components=n_components, random_state=seed)
        self._fitted = False

    def fit(self, texts: List[str]) -> "LocalEmbedder":
        tfidf = self.vectorizer.fit_transform(texts)
        # TruncatedSVD requires n_components < n_samples
        actual_components = min(self.n_components, tfidf.shape[0] - 1, tfidf.shape[1] - 1)
        self.svd = TruncatedSVD(n_components=actual_components, random_state=42)
        self.svd.fit(tfidf)
        self._actual_dim = actual_components
        self._fitted = True
        return self

    def embed(self, texts: List[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Call .fit(corpus) before .embed()")
        tfidf = self.vectorizer.transform(texts)
        vecs  = self.svd.transform(tfidf)
        return normalize(vecs, norm="l2")

    @property
    def dim(self) -> int:
        return getattr(self, '_actual_dim', self.n_components)


# ── SentenceTransformer backend ───────────────────────────────────────────────
class SentenceEmbedder:
    """
    Wraps sentence-transformers for local GPU/CPU inference.

    Install:  pip install sentence-transformers
    Model:    all-mpnet-base-v2 (768-dim, ~420 MB, downloaded on first use)
              or 'all-MiniLM-L6-v2' (384-dim, ~90 MB, faster)
    """

    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed.\n"
                "Run: pip install sentence-transformers"
            )
        print(f"[EmbedderAdapter] Loading SentenceTransformer: {model_name} ...")
        self.model      = SentenceTransformer(model_name)
        self._dim       = self.model.get_sentence_embedding_dimension()
        self.model_name = model_name
        print(f"[EmbedderAdapter] Model ready — dim={self._dim}")

    def fit(self, texts: List[str]) -> "SentenceEmbedder":
        return self  # no fitting needed for transformer models

    def embed(self, texts: List[str]) -> np.ndarray:
        vecs = self.model.encode(texts, convert_to_numpy=True,
                                  show_progress_bar=len(texts) > 20)
        return normalize(vecs, norm="l2")

    @property
    def dim(self) -> int:
        return self._dim


# ── OpenAI Embeddings backend ─────────────────────────────────────────────────
class OpenAIEmbedder:
    """
    Uses OpenAI text-embedding-3-small (1536-dim) or text-embedding-3-large.

    Install:  pip install openai
    Requires: OPENAI_API_KEY environment variable
    Cost:     ~$0.00002 per 1K tokens (text-embedding-3-small)
    """

    def __init__(self, model: str = "text-embedding-3-small", batch_size: int = 100):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package not installed.\n"
                "Run: pip install openai"
            )
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
        self.client     = OpenAI(api_key=api_key)
        self.model      = model
        self.batch_size = batch_size
        self._dim       = 1536 if "small" in model else 3072
        print(f"[EmbedderAdapter] OpenAI embedder ready — model={model}, dim={self._dim}")

    def fit(self, texts: List[str]) -> "OpenAIEmbedder":
        return self  # no fitting needed

    def embed(self, texts: List[str]) -> np.ndarray:
        all_vecs = []
        for i in range(0, len(texts), self.batch_size):
            batch    = texts[i : i + self.batch_size]
            response = self.client.embeddings.create(input=batch, model=self.model)
            vecs     = np.array([d.embedding for d in response.data], dtype=np.float32)
            all_vecs.append(vecs)
        result = np.vstack(all_vecs)
        return normalize(result, norm="l2")

    @property
    def dim(self) -> int:
        return self._dim


# ── Public factory ────────────────────────────────────────────────────────────
class EmbedderAdapter:
    """
    Single entry point. Select backend via `backend` arg or IHCEI_EMBEDDER env var.

    Example:
        emb = EmbedderAdapter(backend="sentence")
        vecs = emb.embed(["user retention policy maximises lock-in", ...])
    """

    BACKENDS = {"local": LocalEmbedder, "sentence": SentenceEmbedder, "openai": OpenAIEmbedder}

    def __init__(self, backend: Optional[str] = None, **kwargs):
        backend = (backend or os.environ.get("IHCEI_EMBEDDER", "local")).lower()
        if backend not in self.BACKENDS:
            raise ValueError(f"Unknown backend '{backend}'. Choose: {list(self.BACKENDS)}")
        self._backend_name = backend
        self._emb = self.BACKENDS[backend](**kwargs)
        print(f"[EmbedderAdapter] Backend: {backend.upper()}")

    def fit(self, texts: List[str]) -> "EmbedderAdapter":
        self._emb.fit(texts)
        return self

    def embed(self, texts: List[str]) -> np.ndarray:
        return self._emb.embed(texts)

    @property
    def dim(self) -> int:
        return self._emb.dim

    @property
    def backend(self) -> str:
        return self._backend_name
