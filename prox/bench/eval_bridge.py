"""Vocabulary-mismatch benchmark — does resistance geometry really associate?

Construction. Each topic owns two disjoint vocabularies, A and B, sharing no words
and no character n-grams. Three kinds of document exist per topic:

    A-docs      drawn from A only
    B-docs      drawn from B only        <- these are the relevance targets
    bridge-docs drawn from both

Queries are drawn from A only. A relevant B-doc therefore shares *zero* terms with
the query, and any term-matching method scores it exactly 0.0 -- not by tuning, but
by construction. The only route from query to target is the two-hop path
A-word -> bridge-doc -> B-word, which is precisely the transitive association that
effective resistance integrates over.

This isolates the mechanism. It is a mechanism demonstration, not a claim about
general benchmark superiority: on tasks where query terms do appear in the target,
BM25 is a strong baseline and we report that case separately.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prox
from bench.baselines import BM25, mrr, ndcg_at_k, recall_at_k

ALPHA = "abcdefghijklmnopqrstuvwxyz"


def _word(rng):
    return "".join(rng.choice(list(ALPHA), size=8))


def make_corpus(n_topics=12, vocab=14, n_a=8, n_b=8, n_bridge=4, doc_len=12, seed=0):
    """Returns (texts, queries, relevant_sets)."""
    rng = np.random.default_rng(seed)
    used = set()

    def fresh():
        while True:
            w = _word(rng)
            if w not in used:
                used.add(w)
                return w

    topics = []
    for _ in range(n_topics):
        topics.append(([fresh() for _ in range(vocab)], [fresh() for _ in range(vocab)]))

    texts, meta = [], []
    for t, (A, B) in enumerate(topics):
        for _ in range(n_a):
            texts.append(" ".join(rng.choice(A, size=doc_len)))
            meta.append((t, "A"))
        for _ in range(n_b):
            texts.append(" ".join(rng.choice(B, size=doc_len)))
            meta.append((t, "B"))
        for _ in range(n_bridge):
            half = doc_len // 2
            words = list(rng.choice(A, size=half)) + list(rng.choice(B, size=half))
            rng.shuffle(words)
            texts.append(" ".join(words))
            meta.append((t, "bridge"))

    queries, relevant = [], []
    for t, (A, _B) in enumerate(topics):
        queries.append(" ".join(rng.choice(A, size=4)))
        relevant.append([i for i, (tt, kind) in enumerate(meta) if tt == t and kind == "B"])
    return texts, queries, relevant, meta


def evaluate(dim=256, reach=1e-3, seed=0, k=10, n_seeds=5, verbose=True):
    """Rank B-docs only, which is what isolates the transitive signal.

    Ranking the whole corpus would be meaningless here: a topic's own A-docs and
    bridge-docs share vocabulary with the query and legitimately outrank the
    targets, so no method could place a B-doc in the top 10. Restricting the
    candidate pool to B-docs asks the one question that matters -- given only
    documents that share nothing with the query, can the method still pick the
    right topic? Chance is 10/96 = 0.1042 for Recall@10.
    """
    agg = {"prox": [], "bm25": [], "chance": []}
    leak = 0.0
    for s in range(seed, seed + n_seeds):
        texts, queries, relevant, meta = make_corpus(seed=s)
        pool = np.array([i for i, (_t, kind) in enumerate(meta) if kind == "B"])
        ix = prox.build(texts, dim=dim, reach=reach, seed=s)
        bm = BM25(texts)
        rng = np.random.default_rng(s)

        for q, rel in zip(queries, relevant):
            d, _ = ix.distances_from(q)
            p = list(pool[np.argsort(d[pool])])
            agg["prox"].append((recall_at_k(p, rel, k), mrr(p, rel), ndcg_at_k(p, rel, k)))

            sc = bm.scores(q)
            leak = max(leak, float(sc[pool].max()))
            b = list(pool[np.argsort(-sc[pool], kind="stable")])
            agg["bm25"].append((recall_at_k(b, rel, k), mrr(b, rel), ndcg_at_k(b, rel, k)))

            c = list(rng.permutation(pool))
            agg["chance"].append((recall_at_k(c, rel, k), mrr(c, rel), ndcg_at_k(c, rel, k)))

    out = {m: np.array(v).mean(axis=0) for m, v in agg.items()}
    if verbose:
        texts, queries, relevant, meta = make_corpus(seed=seed)
        print(f"corpus {len(texts)} docs | pool {len([1 for _t,kd in meta if kd=='B'])} B-docs "
              f"| {len(queries)} queries x {n_seeds} seeds | dim={dim} reach={reach:g}")
        print(f"max BM25 score over the entire candidate pool: {leak:.6f} "
              f"-> the vocabulary gap is total, so BM25 ranking is arbitrary\n")
        print(f"{'method':<10}{'Recall@'+str(k):>12}{'MRR':>10}{'nDCG@'+str(k):>12}")
        for m in ("chance", "bm25", "prox"):
            r, mr, nd = out[m]
            print(f"{m:<10}{r:>12.4f}{mr:>10.4f}{nd:>12.4f}")
    return out, leak


if __name__ == "__main__":
    evaluate(dim=int(sys.argv[1]) if len(sys.argv) > 1 else 256)
