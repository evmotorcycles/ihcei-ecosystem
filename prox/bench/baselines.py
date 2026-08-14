"""Okapi BM25 baseline — the standard every retrieval claim must clear.

BM25 is the right comparison for PROX because it is the other method that needs no
training, no GPU and no vendor. If PROX only matched BM25 it would be a curiosity;
the question worth testing is whether resistance geometry buys association that
term matching provably cannot reach.
"""

from __future__ import annotations

import math
import re

import numpy as np

_TOK = re.compile(r"\w+", re.UNICODE)


def tokenize(text):
    return _TOK.findall(str(text).lower())


class BM25:
    def __init__(self, texts, k1=1.5, b=0.75):
        self.docs = [tokenize(t) for t in texts]
        self.N = len(self.docs)
        self.k1, self.b = k1, b
        self.len = np.array([len(d) for d in self.docs], dtype=np.float64)
        self.avgdl = max(self.len.mean(), 1e-9)
        self.tf = []
        df = {}
        for d in self.docs:
            c = {}
            for w in d:
                c[w] = c.get(w, 0) + 1
            self.tf.append(c)
            for w in c:
                df[w] = df.get(w, 0) + 1
        self.idf = {
            w: math.log(1.0 + (self.N - n + 0.5) / (n + 0.5)) for w, n in df.items()
        }

    def scores(self, query):
        s = np.zeros(self.N, dtype=np.float64)
        for w in tokenize(query):
            idf = self.idf.get(w)
            if idf is None:
                continue
            for i, c in enumerate(self.tf):
                f = c.get(w)
                if f:
                    denom = f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avgdl)
                    s[i] += idf * (f * (self.k1 + 1)) / denom
        return s

    def rank(self, query, top_k=10):
        s = self.scores(query)
        idx = np.argsort(-s)[:top_k]
        return [(int(i), float(s[i])) for i in idx if s[i] > 0]


# ------------------------------------------------------------------ IR metrics

def recall_at_k(ranked_idx, relevant, k):
    if not relevant:
        return float("nan")
    hit = len(set(ranked_idx[:k]) & set(relevant))
    return hit / len(relevant)


def mrr(ranked_idx, relevant):
    for r, i in enumerate(ranked_idx, start=1):
        if i in relevant:
            return 1.0 / r
    return 0.0


def ndcg_at_k(ranked_idx, relevant, k):
    if not relevant:
        return float("nan")
    dcg = sum(
        1.0 / math.log2(r + 1)
        for r, i in enumerate(ranked_idx[:k], start=1)
        if i in relevant
    )
    ideal = sum(1.0 / math.log2(r + 1) for r in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal > 0 else float("nan")
