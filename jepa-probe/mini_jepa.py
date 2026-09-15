#!/usr/bin/env python3
"""The JEPA collapse mechanism, in miniature. NOT I-JEPA.

No Vision Transformer, no images, no ImageNet. Linear encoders on synthetic
block-structured vectors. What is reproduced is the ONE mechanism the paper
names as load-bearing:

    "as with Joint-Embedding Architectures, representation collapse is also a
     concern with JEPAs; we leverage an asymmetric architecture between the
     x- and y-encoders to avoid representation collapse."
        -- Assran et al., arXiv:2301.08243v3, section 2

Everything else about the paper is out of scope and nothing here bears on any
number in its tables.

Shape, following section 3:
  * a context block x is encoded to s_x
  * a predictor g, conditioned on a positional embedding per target block,
    predicts each target representation
  * targets s_y come from a SECOND encoder
  * the loss is mean squared L2 in representation space, never in input space

The two arms differ in exactly one thing: whether the target encoder is the
context encoder with gradients flowing through it (symmetric), or an
exponential moving average of it with a stop-gradient (asymmetric).
"""

from __future__ import annotations

import numpy as np

N_BLOCKS = 4          # the vector is split into this many "patches"
BLOCK = 8             # dimensions per block
H = 16                # embedding width
CONTEXT = [0, 1]      # blocks used as context
TARGETS = [2, 3]      # blocks whose representations are predicted
EMA_MOMENTUM = 0.996  # the paper's starting value
STEPS = 4000
LR = 0.05


def make_data(n=400, n_clusters=4, noise=0.25, seed=0):
    """Block-structured vectors: a shared latent per cluster plus noise.

    Structure exists, so a non-collapsed encoder has something to represent.
    """
    rng = np.random.default_rng(seed)
    centres = rng.normal(size=(n_clusters, N_BLOCKS * BLOCK))
    which = rng.integers(0, n_clusters, size=n)
    X = centres[which] + noise * rng.normal(size=(n, N_BLOCKS * BLOCK))
    return X.reshape(n, N_BLOCKS, BLOCK), which


def _init(seed):
    rng = np.random.default_rng(seed + 1000)
    scale = 1.0 / np.sqrt(BLOCK)
    We = rng.normal(scale=scale, size=(H, BLOCK))     # context encoder
    P = rng.normal(scale=1.0 / np.sqrt(H), size=(H, H))  # predictor
    pos = rng.normal(scale=0.1, size=(len(TARGETS), H))  # positional embeddings
    return We, P, pos


def embed(W, blocks):
    """W applied per block. blocks: (n, b, BLOCK) -> (n, b, H)."""
    return np.einsum("hd,nbd->nbh", W, blocks)


def train(X, symmetric: bool, steps=STEPS, lr=LR, seed=0, batch=64):
    """Returns the trained encoders and a per-step history.

    symmetric=True  -> target encoder IS the context encoder, gradients flow
                       through the target branch. No asymmetry at all.
    symmetric=False -> target encoder is an EMA of the context encoder and the
                       target branch is stop-gradient. The paper's arrangement.
    """
    rng = np.random.default_rng(seed + 7)
    We, P, pos = _init(seed)
    Wt = We.copy()
    n = X.shape[0]
    hist = []

    for step in range(steps):
        idx = rng.choice(n, size=batch, replace=False)
        xb = X[idx]

        s_x = embed(We, xb[:, CONTEXT, :]).mean(axis=1)          # (B, H)
        tgt_blocks = xb[:, TARGETS, :]                           # (B, T, BLOCK)
        enc_for_target = We if symmetric else Wt
        s_y = embed(enc_for_target, tgt_blocks)                  # (B, T, H)

        pred = (s_x @ P.T)[:, None, :] + pos[None, :, :]         # (B, T, H)
        err = pred - s_y                                         # (B, T, H)
        M = batch * len(TARGETS)
        loss = float((err ** 2).sum() / M)

        g = 2.0 * err / M                                        # dL/dpred
        gP = np.einsum("bth,bk->hk", g, s_x)
        gpos = g.sum(axis=0)
        g_sx = np.einsum("bth,hk->bk", g, P)

        ctx_mean = xb[:, CONTEXT, :].mean(axis=1)                # (B, BLOCK)
        gWe = np.einsum("bh,bd->hd", g_sx, ctx_mean)

        if symmetric:
            # the target branch is NOT detached: its gradient reaches the same
            # weights. This is the whole difference between the two arms.
            gWe += np.einsum("bth,btd->hd", -g, tgt_blocks)

        We -= lr * gWe
        P -= lr * gP
        pos -= lr * gpos

        if symmetric:
            Wt = We
        else:
            Wt = EMA_MOMENTUM * Wt + (1.0 - EMA_MOMENTUM) * We

        if step % 50 == 0 or step == steps - 1:
            hist.append({"step": step, "loss": loss})

    return {"We": We, "Wt": Wt, "P": P, "pos": pos, "history": hist,
            "final_loss": hist[-1]["loss"]}


def target_embeddings(W, X):
    """Mean over target blocks -- one vector per sample."""
    return embed(W, X[:, TARGETS, :]).mean(axis=1)


def spread(E):
    """Mean variance per embedding dimension across samples.

    A proxy for collapse, NOT a definition of it: a representation can be
    varied and useless.
    """
    return float(E.var(axis=0).mean())


def mean_pairwise_distance(E):
    d = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=-1)
    iu = np.triu_indices(len(E), k=1)
    return float(d[iu].mean())


def knn_edges(E, k=3):
    """Deterministic k-nearest-neighbour edges. Ties broken by index.

    A MODELLING DECISION: a different k gives a different graph and therefore
    different structural readouts.
    """
    n = len(E)
    d = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=-1)
    np.fill_diagonal(d, np.inf)
    seen = set()
    edges = []
    for i in range(n):
        order = np.lexsort((np.arange(n), d[i]))    # distance, then index
        for j in order[:k]:
            a, b = (i, int(j)) if i < int(j) else (int(j), i)
            if (a, b) in seen:
                continue
            seen.add((a, b))
            edges.append((a, b, 1.0))
    return edges
