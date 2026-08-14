"""Real-prose retrieval, where BM25 is genuinely strong.

The bridge benchmark isolates association by removing all lexical overlap. This is
the complementary case and the fairer headline test: real documents, real queries
that do share vocabulary with their target. Here BM25 is a serious baseline and
PROX has no structural advantage, so the honest question is whether it stays
competitive rather than whether it wins.

Task: known-item retrieval by continuation. Each document is split in half; first
halves are indexed, second halves become queries, and the target is the document
the query came from. Vocabulary overlap is real but partial, which is what makes
it a retrieval task rather than a string lookup.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prox
from bench.baselines import BM25, mrr, recall_at_k

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_markdown(root=REPO, min_words=120, limit=400):
    """Real prose from the repository itself -- not a curated benchmark set."""
    docs, names = [], []
    for p in sorted(glob.glob(os.path.join(root, "**", "*.md"), recursive=True)):
        if os.sep + ".git" + os.sep in p:
            continue
        try:
            t = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        t = re.sub(r"```.*?```", " ", t, flags=re.S)      # drop code fences
        t = re.sub(r"[^\w\s]", " ", t)
        words = t.split()
        if len(words) < min_words:
            continue
        docs.append(words)
        names.append(os.path.relpath(p, root))
        if len(docs) >= limit:
            break
    return docs, names


def evaluate(dim=256, reach=1e-3, k=10, seed=0, verbose=True):
    docs, names = load_markdown()
    if len(docs) < 20:
        raise RuntimeError("not enough markdown found to evaluate")

    # First half indexed, second half is the query. Cap query length so the task
    # is retrieval, not whole-document matching.
    corpus = [" ".join(w[: len(w) // 2]) for w in docs]
    queries = [" ".join(w[len(w) // 2 :][:40]) for w in docs]

    t0 = time.time()
    ix = prox.build(corpus, ids=names, dim=dim, reach=reach, seed=seed)
    t_prox = time.time() - t0
    t0 = time.time()
    bm = BM25(corpus)
    t_bm = time.time() - t0

    res = {"prox": [], "bm25": []}
    lat = {"prox": [], "bm25": []}
    for i, q in enumerate(queries):
        t0 = time.time()
        d, _ = ix.distances_from(q)
        lat["prox"].append(time.time() - t0)
        r = list(np.argsort(d))
        res["prox"].append((recall_at_k(r, [i], k), mrr(r, [i])))

        t0 = time.time()
        s = bm.scores(q)
        lat["bm25"].append(time.time() - t0)
        r = list(np.argsort(-s))
        res["bm25"].append((recall_at_k(r, [i], k), mrr(r, [i])))

    out = {m: np.array(v).mean(axis=0) for m, v in res.items()}
    if verbose:
        words = sum(len(c.split()) for c in corpus)
        print(f"corpus: {len(corpus)} real markdown documents, {words:,} words, dim={dim}")
        print(f"task:   known-item retrieval, second half of each document as query\n")
        print(f"{'method':<8}{'Recall@'+str(k):>12}{'MRR':>10}{'build s':>10}{'query ms':>11}")
        for m in ("bm25", "prox"):
            r, mr = out[m]
            bt = t_bm if m == "bm25" else t_prox
            print(f"{m:<8}{r:>12.4f}{mr:>10.4f}{bt:>10.2f}{np.mean(lat[m])*1e3:>11.2f}")
        print(f"\nindex size: {ix.nbytes()/1e6:.1f} MB "
              f"({ix.nbytes()/max(len(corpus),1)/1024:.1f} KB/document)")
    return out


if __name__ == "__main__":
    evaluate(dim=int(sys.argv[1]) if len(sys.argv) > 1 else 256)
