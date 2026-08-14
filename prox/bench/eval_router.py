"""Routing, not fusion.

Measured on the two tasks separately, term matching and resistance geometry are
near-perfect complements: BM25 wins known-item retrieval by 8x, PROX wins
vocabulary-gap association by 9x. The tempting move is to blend their rankings, and
it is wrong -- reciprocal rank fusion measured *worse than either* on its own
strong task, because averaging a sharp signal with a smooth one discards both.

The correct rule is a router, and the routing signal is already free: BM25's own
top score. When a query shares discriminative terms with the corpus, term matching
is both better and cheaper. When it shares none -- a synonym, another language, a
"find things like this", an empty query box -- term matching cannot rank at all and
returns zeros, and geometry is the only method that can answer.

PROX therefore does not replace lexical search. It answers the queries lexical
search must decline.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prox
from bench.baselines import BM25, mrr, recall_at_k
from bench.eval_bridge import make_corpus
from bench.eval_real import load_markdown

THRESHOLD = 1e-9  # "did term matching produce any evidence at all?"


def route(bm_scores, prox_dist, pool=None):
    """Return a ranking and which engine produced it."""
    cand = np.arange(len(bm_scores)) if pool is None else pool
    if float(bm_scores[cand].max()) > THRESHOLD:
        return list(cand[np.argsort(-bm_scores[cand], kind="stable")]), "bm25"
    return list(cand[np.argsort(prox_dist[cand])]), "prox"


def _run(corpus, queries, relevants, pool=None, dim=256, seed=0, label=""):
    ix = prox.build(corpus, dim=dim, reach=1e-3, seed=seed)
    bm = BM25(corpus)
    rows = {"bm25": [], "prox": [], "router": []}
    used = {"bm25": 0, "prox": 0}
    for q, rel in zip(queries, relevants):
        d, _ = ix.distances_from(q)
        s = bm.scores(q)
        cand = np.arange(len(corpus)) if pool is None else pool
        b = list(cand[np.argsort(-s[cand], kind="stable")])
        p = list(cand[np.argsort(d[cand])])
        r, who = route(s, d, pool)
        used[who] += 1
        rows["bm25"].append((recall_at_k(b, rel, 10), mrr(b, rel)))
        rows["prox"].append((recall_at_k(p, rel, 10), mrr(p, rel)))
        rows["router"].append((recall_at_k(r, rel, 10), mrr(r, rel)))

    print(f"\n{label}")
    print(f"{'method':<10}{'Recall@10':>12}{'MRR':>10}")
    for m in ("bm25", "prox", "router"):
        a = np.array(rows[m]).mean(axis=0)
        print(f"{m:<10}{a[0]:>12.4f}{a[1]:>10.4f}")
    print(f"router chose: bm25 {used['bm25']}x, prox {used['prox']}x")
    return {m: np.array(v).mean(axis=0) for m, v in rows.items()}


def main():
    docs, names = load_markdown()
    corpus = [" ".join(w[: len(w) // 2]) for w in docs]
    queries = [" ".join(w[len(w) // 2 :][:40]) for w in docs]
    _run(corpus, queries, [[i] for i in range(len(corpus))],
         label="TASK A - known-item retrieval on real prose (query shares vocabulary)")

    texts, qs, rel, meta = make_corpus(seed=0)
    pool = np.array([i for i, (_t, k) in enumerate(meta) if k == "B"])
    _run(texts, qs, rel, pool=pool,
         label="TASK B - association across a total vocabulary gap (zero shared terms)")


if __name__ == "__main__":
    main()
