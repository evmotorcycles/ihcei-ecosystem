"""Language-agnostic feature extraction.

Every learned embedding model carries a vocabulary, and every vocabulary was fixed
by whoever paid for the training run. That is the mechanism by which relevance
became something most of the world rents in a language it did not choose.

PROX takes the opposite route: features are hashed character n-grams. There is no
vocabulary file, no tokenizer, no training corpus and no language list. Swahili,
Amharic, Urdu, Khmer, Quechua, source code and chemical formulae all decompose into
n-grams identically, and morphologically rich languages benefit most, because
n-grams see shared stems that whitespace tokenisers split apart.

Weighting is BM25-style: saturating term frequency times inverse document
frequency. IDF is not cosmetic here -- it is structural. In a resistance graph a
high-degree feature node is a short circuit, so an unweighted "the" would wire the
entire corpus into one point. Down-weighting common features is what keeps the
geometry informative.
"""

from __future__ import annotations

import re
import unicodedata
import zlib

import numpy as np

__all__ = ["FeatureSpace", "normalize"]

_WS = re.compile(r"\s+")


def normalize(text: str) -> str:
    """NFKC-fold, lowercase and collapse whitespace. No language assumptions."""
    text = unicodedata.normalize("NFKC", str(text)).lower()
    return _WS.sub(" ", text).strip()


class FeatureSpace:
    """Maps documents to sparse hashed n-gram features with BM25 weights.

    n_buckets bounds memory regardless of corpus size or script. Collisions are
    tolerable: a collision merges two features, which perturbs the graph slightly
    rather than corrupting it, and the metric guarantee is unaffected.
    """

    def __init__(self, ngrams=(3, 4, 5), n_buckets=1 << 18, use_words=True, k1=1.2, seed=0):
        self.ngrams = tuple(ngrams)
        self.n_buckets = int(n_buckets)
        self.use_words = bool(use_words)
        self.k1 = float(k1)
        self.seed = int(seed)
        self.idf = None          # (n_buckets,) filled by fit()
        self.n_docs = 0

    def _hash(self, s: str) -> int:
        # CRC32 is deterministic across processes and platforms (unlike Python's
        # salted hash()), runs in C, and is ~20 lines to reimplement in JavaScript
        # or C -- which matters because the index format must be readable by the
        # browser build without shipping a hashing dependency.
        return zlib.crc32(s.encode("utf-8"), self.seed) % self.n_buckets

    def raw_counts(self, text: str) -> dict:
        """Bucket -> raw count for one document."""
        t = normalize(text)
        if not t:
            return {}
        counts = {}
        padded = f" {t} "
        crc32, mask, seed = zlib.crc32, self.n_buckets - 1, self.seed
        pow2 = (self.n_buckets & mask) == 0  # bitmask beats modulo on powers of two
        for n in self.ngrams:
            if len(padded) < n:
                continue
            for i in range(len(padded) - n + 1):
                h = crc32(padded[i : i + n].encode("utf-8"), seed)
                b = h & mask if pow2 else h % self.n_buckets
                counts[b] = counts.get(b, 0) + 1
        if self.use_words:
            for w in t.split(" "):
                if w:
                    h = crc32(b"\x00w" + w.encode("utf-8"), seed)
                    bb = h & mask if pow2 else h % self.n_buckets
                    counts[bb] = counts.get(bb, 0) + 1
        return counts

    def fit(self, texts):
        """Compute IDF over a corpus. Returns the per-document raw counts."""
        docs = [self.raw_counts(t) for t in texts]
        self.n_docs = len(docs)
        df = np.zeros(self.n_buckets, dtype=np.float64)
        for c in docs:
            if c:
                df[np.fromiter(c.keys(), dtype=np.int64, count=len(c))] += 1.0
        N = max(self.n_docs, 1)
        # Lucene-style non-negative IDF; unseen buckets get the max value.
        self.idf = np.log(1.0 + (N - df + 0.5) / (df + 0.5))
        return docs

    def weights(self, counts: dict):
        """Saturating tf * idf for one document's counts -> (buckets, weights)."""
        if not counts:
            return np.empty(0, dtype=np.int64), np.empty(0, dtype=np.float64)
        b = np.fromiter(counts.keys(), dtype=np.int64, count=len(counts))
        tf = np.fromiter(counts.values(), dtype=np.float64, count=len(counts))
        sat = tf / (tf + self.k1)
        w = sat * (self.idf[b] if self.idf is not None else 1.0)
        keep = w > 0
        return b[keep], w[keep]

    def transform(self, text: str):
        """Feature buckets and weights for an unseen document or query."""
        return self.weights(self.raw_counts(text))

    def to_dict(self):
        return {
            "ngrams": list(self.ngrams),
            "n_buckets": self.n_buckets,
            "use_words": self.use_words,
            "k1": self.k1,
            "seed": self.seed,
            "n_docs": self.n_docs,
        }

    @classmethod
    def from_dict(cls, d, idf=None):
        fs = cls(
            ngrams=tuple(d["ngrams"]),
            n_buckets=int(d["n_buckets"]),
            use_words=bool(d["use_words"]),
            k1=float(d["k1"]),
            seed=int(d["seed"]),
        )
        fs.n_docs = int(d.get("n_docs", 0))
        fs.idf = idf
        return fs
