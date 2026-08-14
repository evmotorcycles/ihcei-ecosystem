"""Cost at scale -- the claim that this is affordable for everyone.

Three numbers decide whether a proximity layer can be universal: how long an index
takes to build on an ordinary CPU, how many bytes it costs per item, and how long a
query takes. Nothing here uses a GPU, a network or a downloaded model.

Bytes per item is the one to watch. Feature nodes dominate a small index, which is
why a 109-document index looks absurdly expensive per document. Vocabulary grows
sublinearly with corpus size (Heaps' law) while item vectors grow linearly, so the
per-item cost falls steeply and converges on dim x 4 bytes.
"""

from __future__ import annotations

import os
import resource
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prox


def synth(n_docs, vocab=20000, doc_len=80, seed=0):
    rng = np.random.default_rng(seed)
    # Zipf-distributed vocabulary, as real language is.
    z = 1.0 / np.arange(1, vocab + 1) ** 1.07
    z /= z.sum()
    words = np.array([f"w{i}" for i in range(vocab)])
    return [" ".join(rng.choice(words, size=doc_len, p=z)) for _ in range(n_docs)]


def peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def main(sizes=(500, 2000, 8000, 25000), dim=128, min_df=3):
    print(f"dim={dim}, min_df={min_df}, {os.cpu_count()} CPU cores, no GPU\n")
    print(f"{'items':>8}{'features':>10}{'build s':>10}{'us/item':>10}"
          f"{'index MB':>10}{'B/item':>9}{'query ms':>10}")
    for n in sizes:
        texts = synth(n)
        t0 = time.time()
        ix = prox.build(texts, dim=dim, reach=1e-3, seed=0, min_df=min_df)
        build = time.time() - t0

        qs = [" ".join(t.split()[:8]) for t in texts[:50]]
        t0 = time.time()
        for q in qs:
            ix.distances_from(q)
        qms = (time.time() - t0) / len(qs) * 1e3

        print(f"{n:>8}{ix.meta['n_feats']:>10}{build:>10.2f}{build/n*1e6:>10.0f}"
              f"{ix.nbytes()/1e6:>10.1f}{ix.nbytes()/n:>9.0f}{qms:>10.2f}")
    print(f"\npeak RSS {peak_rss_mb():.0f} MB")


if __name__ == "__main__":
    main()
