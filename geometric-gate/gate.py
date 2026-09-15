#!/usr/bin/env python3
"""Two geometric sensors, and a gate that reports rather than decides.

The gate sits between embedding generation and graph construction. It answers
one question -- has the latent space collapsed -- and it answers it in two
different currencies, because the two failures are different:

  * VOLUMETRIC collapse: the space shrinks toward a point. Spread goes, the
    directions may survive.
  * DIMENSIONAL collapse: the space keeps its size but falls onto a line or a
    plane. Spread survives, independence goes.

NO THRESHOLD IS SET HERE. `reading()` returns numbers and `halts()` takes the
cutoffs as arguments with no defaults, so a caller cannot accidentally inherit
a number nobody chose. What a defensible cutoff would need is measured in
run_gate.py and written up in RESULTS.md.
"""

from __future__ import annotations

import numpy as np


def covariance_trace(E):
    """Total volumetric spread: sum of the per-dimension variances.

    NOT scale-invariant. Multiplying E by c multiplies this by c squared, which
    is the whole problem with giving it an absolute floor.
    """
    E = np.asarray(E, dtype=float)
    return float(E.var(axis=0, ddof=0).sum())


def effective_rank(E, eps=1e-300):
    """Entropy effective rank, exp(H(p)) over normalised singular values.

    Roy & Vetterli's form. Scale-invariant by construction: the singular values
    of cE are c times those of E, and normalising divides the c straight out.

    Returns 1.0 for a rank-one space and approaches the number of dimensions
    for an isotropic one.
    """
    E = np.asarray(E, dtype=float)
    Ec = E - E.mean(axis=0, keepdims=True)
    s = np.linalg.svd(Ec, compute_uv=False)
    total = s.sum()
    if total <= eps:
        # every singular value is zero: the space is a single point. Rank is
        # not merely low, it is undefined, and that is reported as such rather
        # than as a convenient 1.0.
        return float("nan")
    p = s / total
    p = p[p > eps]
    H = -(p * np.log(p)).sum()
    return float(np.exp(H))


def reading(E):
    """Both sensors, side by side. No combined score, no verdict."""
    return {
        "covariance_trace": covariance_trace(E),
        "effective_rank": effective_rank(E),
        "dimensions": int(np.asarray(E).shape[1]),
        "samples": int(np.asarray(E).shape[0]),
    }


def halts(E, trace_floor, rank_floor):
    """Would the gate halt? Both cutoffs are REQUIRED arguments.

    There is no default, because there is no number this file is entitled to
    choose. A caller must pass one and therefore must own it.
    """
    if trace_floor is None or rank_floor is None:
        raise ValueError(
            "the geometric gate has no default cutoffs; a caller that wants a "
            "hard halt has to state the numbers and the reason for them")
    r = reading(E)
    rank = r["effective_rank"]
    return {
        "reading": r,
        "trace_below_floor": bool(r["covariance_trace"] < trace_floor),
        "rank_below_floor": bool(np.isnan(rank) or rank < rank_floor),
        "halt": bool(r["covariance_trace"] < trace_floor
                     or np.isnan(rank) or rank < rank_floor),
    }


def project_to_rank(E, k, seed=0):
    """Dimensional collapse, constructed: keep only the top k directions.

    The spread stays large; the independence is destroyed. A worked example of
    a failure mode, NOT evidence that training produces it.
    """
    E = np.asarray(E, dtype=float)
    mu = E.mean(axis=0, keepdims=True)
    Ec = E - mu
    U, s, Vt = np.linalg.svd(Ec, full_matrices=False)
    s2 = s.copy()
    s2[k:] = 0.0
    # rescale so the retained directions carry the original total energy --
    # otherwise the projection would also shrink the trace and the two failure
    # modes would be confounded.
    if s2.sum() > 0:
        s2 *= s.sum() / s2.sum()
    return (U * s2) @ Vt + mu
