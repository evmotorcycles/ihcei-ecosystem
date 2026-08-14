"""ProxIndex — build a coordinate system over a collection, then search it.

The collection becomes a bipartite coupling graph: item nodes on one side, hashed
feature nodes on the other, plus any typed item-to-item relations the application
already knows (a link, a shared folder, a reply, a co-purchase, an appointment).
Resistance geometry over that graph is what produces association: two items that
share no feature at all are still pulled together when many short paths run
between them through other items. Transitive relatedness falls out of counting.

Each relation class carries its own coupling J. Raising one class contracts the
space along that kind of relation by exactly J^-1/2, which is what makes the
coupling dial a user-facing control rather than an internal hyper-parameter.
"""

from __future__ import annotations

import json
import time

import numpy as np

from .core import resistance_embedding
from .text import FeatureSpace

__all__ = ["ProxIndex", "build"]

FORMAT = "PROX/1"


class ProxIndex:
    """A metric coordinate system over a collection of items."""

    def __init__(self, X_items, X_feats, buckets, idf, ids, meta):
        self.X_items = X_items        # (n_items, dim) float32
        self.X_feats = X_feats        # (n_feats, dim) float32
        self.buckets = buckets        # (n_feats,) sorted hash buckets
        self.idf = idf                # (n_feats,)
        self.ids = list(ids)
        self.meta = dict(meta)
        self.fs = FeatureSpace.from_dict(meta["feature_space"])

    # ---------------------------------------------------------------- geometry

    @property
    def dim(self):
        return self.X_items.shape[1]

    def _fold_in(self, text):
        """Place unseen text in the existing space (harmonic extension).

        A query node q coupled to features f with weights w satisfies
            (sum_f w_f + eps) z_q = sum_f w_f z_f + b_q
        where b_q is q's own sketch row. Dropping b_q leaves an isotropic residual
        whose expected contribution to || z_q - z_j ||^2 is the same for every item
        j, so rankings are preserved while the re-solve is avoided entirely.
        """
        counts = self.fs.raw_counts(text)
        if not counts:
            return None, 0
        b = np.fromiter(counts.keys(), dtype=np.int64, count=len(counts))
        tf = np.fromiter(counts.values(), dtype=np.float64, count=len(counts))

        pos = np.searchsorted(self.buckets, b)
        pos = np.clip(pos, 0, len(self.buckets) - 1)
        hit = self.buckets[pos] == b
        if not hit.any():
            return None, 0
        pos, tf = pos[hit], tf[hit]

        w = (tf / (tf + self.fs.k1)) * self.idf[pos]
        w = w * self.meta["couplings"].get("text", 1.0)
        denom = w.sum() + self.meta["reach"]
        z = (w[:, None] * self.X_feats[pos]).sum(axis=0) / denom
        return z.astype(np.float32), int(hit.sum())

    def distances_from(self, text):
        """LMD distance from a query to every item. Lower is nearer."""
        z, n_hit = self._fold_in(text)
        if z is None:
            return None, 0
        diff = self.X_items - z[None, :]
        return np.sqrt(np.einsum("ij,ij->i", diff, diff)), n_hit

    def search(self, text, top_k=10):
        """Rank items by proximity to the query. Returns [(id, distance, idx)]."""
        d, n_hit = self.distances_from(text)
        if d is None:
            return []
        top_k = min(top_k, len(d))
        idx = np.argpartition(d, top_k - 1)[:top_k]
        idx = idx[np.argsort(d[idx])]
        return [(self.ids[i], float(d[i]), int(i)) for i in idx]

    def neighbors(self, item_idx, top_k=10):
        """Items nearest to an existing item -- 'more like this', no query text."""
        diff = self.X_items - self.X_items[item_idx][None, :]
        d = np.sqrt(np.einsum("ij,ij->i", diff, diff))
        d[item_idx] = np.inf
        top_k = min(top_k, len(d) - 1)
        idx = np.argpartition(d, top_k - 1)[:top_k]
        idx = idx[np.argsort(d[idx])]
        return [(self.ids[i], float(d[i]), int(i)) for i in idx]

    # ------------------------------------------------------------- persistence

    def save(self, path):
        np.savez_compressed(
            path,
            X_items=self.X_items,
            X_feats=self.X_feats,
            buckets=self.buckets,
            idf=self.idf.astype(np.float32),
            ids=np.array(self.ids, dtype=object),
            meta=json.dumps(self.meta),
        )

    @classmethod
    def load(cls, path):
        z = np.load(path, allow_pickle=True)
        return cls(
            z["X_items"], z["X_feats"], z["buckets"], z["idf"].astype(np.float64),
            list(z["ids"]), json.loads(str(z["meta"])),
        )

    def nbytes(self):
        return int(
            self.X_items.nbytes + self.X_feats.nbytes
            + self.buckets.nbytes + self.idf.nbytes
        )


def build(
    texts,
    ids=None,
    relations=None,
    dim=64,
    reach=1e-2,
    couplings=None,
    ngrams=(3, 4, 5),
    n_buckets=1 << 18,
    min_df=1,
    seed=0,
    verbose=False,
):
    """Build a ProxIndex from texts and optional typed item-to-item relations.

    relations -- iterable of (i, j, class_name); coupling taken from `couplings`
    couplings -- {class_name: J}; "text" governs the item-feature edges
    min_df    -- drop features seen in fewer than this many items (pendant nodes
                 carry no association and only cost memory)
    """
    t0 = time.time()
    texts = list(texts)
    n_items = len(texts)
    if n_items == 0:
        raise ValueError("cannot index an empty collection")
    ids = list(ids) if ids is not None else [str(i) for i in range(n_items)]
    if len(ids) != n_items:
        raise ValueError("ids and texts must agree in length")
    couplings = dict(couplings or {})
    couplings.setdefault("text", 1.0)

    fs = FeatureSpace(ngrams=ngrams, n_buckets=n_buckets, seed=seed)
    doc_counts = fs.fit(texts)

    # Keep only buckets meeting min_df, and compact them into node indices.
    df = np.zeros(n_buckets, dtype=np.int32)
    for c in doc_counts:
        if c:
            df[np.fromiter(c.keys(), dtype=np.int64, count=len(c))] += 1
    active = np.flatnonzero(df >= min_df).astype(np.int64)
    if active.size == 0:
        raise ValueError("no features survived min_df")
    lookup = np.full(n_buckets, -1, dtype=np.int64)
    lookup[active] = np.arange(active.size)
    n_feats = active.size

    # Item-feature edges.
    e_i, e_j, e_w = [], [], []
    J_text = couplings["text"]
    for d, counts in enumerate(doc_counts):
        b, w = fs.weights(counts)
        if b.size == 0:
            continue
        f = lookup[b]
        keep = f >= 0
        if not keep.any():
            continue
        f, w = f[keep], w[keep]
        e_i.append(np.full(f.size, d, dtype=np.int64))
        e_j.append(f + n_items)
        e_w.append(w * J_text)

    # Typed item-item relations, each scaled by its own coupling.
    for (a, b_, cls) in (relations or []):
        e_i.append(np.array([a], dtype=np.int64))
        e_j.append(np.array([b_], dtype=np.int64))
        e_w.append(np.array([couplings.get(cls, 1.0)], dtype=np.float64))

    edges = np.column_stack([np.concatenate(e_i), np.concatenate(e_j)])
    weights = np.concatenate(e_w)
    n_nodes = n_items + n_feats
    if verbose:
        print(f"[prox] {n_items} items, {n_feats} features, {len(weights)} couplings")

    X = resistance_embedding(edges, weights, n_nodes, dim=dim, reach=reach, seed=seed)

    meta = {
        "format": FORMAT,
        "dim": int(dim),
        "reach": float(reach),
        "couplings": couplings,
        "n_items": n_items,
        "n_feats": int(n_feats),
        "n_edges": int(len(weights)),
        "min_df": int(min_df),
        "seed": int(seed),
        "build_seconds": round(time.time() - t0, 3),
        "feature_space": fs.to_dict(),
    }
    idx = ProxIndex(
        X[:n_items].astype(np.float32), X[n_items:].astype(np.float32),
        active, fs.idf[active], ids, meta,
    )
    if verbose:
        print(f"[prox] built in {meta['build_seconds']}s, {idx.nbytes()/1e6:.1f} MB")
    return idx
