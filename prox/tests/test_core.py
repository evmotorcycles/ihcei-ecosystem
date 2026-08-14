"""Core guarantees: metricity, sketch accuracy, and the LMD contraction law."""

from __future__ import annotations

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prox
from prox.core import (
    distance_matrix,
    exact_resistance_matrix,
    resistance_embedding,
    triangle_violations,
)


def random_graph(n=250, deg=4, seed=1):
    rng = np.random.default_rng(seed)
    E = set()
    for i in range(n):
        for _ in range(deg):
            j = int(rng.integers(0, n))
            if i != j:
                E.add((min(i, j), max(i, j)))
    edges = np.array(sorted(E), dtype=np.int64)
    return edges, rng.uniform(0.2, 3.0, len(edges)), n


def ring(n, J):
    edges = np.array([[i, (i + 1) % n] for i in range(n)], dtype=np.int64)
    return edges, np.full(n, float(J)), n


# --------------------------------------------------------------- metric axioms

def test_exact_resistance_is_a_metric():
    """sqrt(R) satisfies the metric axioms exactly, not statistically."""
    edges, w, n = random_graph()
    D = np.sqrt(np.maximum(exact_resistance_matrix(edges, w, n, reach=1e-2), 0.0))
    assert np.allclose(np.diag(D), 0.0, atol=1e-9)          # identity
    assert np.allclose(D, D.T, atol=1e-12)                   # symmetry
    off = D[~np.eye(n, dtype=bool)]
    assert off.min() > 0                                     # separation
    count, worst = triangle_violations(D, atol=1e-9)
    assert count == 0, f"{count} triangle violations, worst {worst:.2e}"


def test_embedding_is_a_metric_by_construction():
    """The compressed index is still exactly a metric -- it IS a Euclidean space."""
    edges, w, n = random_graph()
    X = resistance_embedding(edges, w, n, dim=64, reach=1e-2, seed=0)
    count, worst = triangle_violations(distance_matrix(X), atol=1e-9)
    assert count == 0, f"{count} violations, worst {worst:.2e}"


# ------------------------------------------------------------- sketch accuracy

def test_sketch_converges_at_the_johnson_lindenstrauss_rate():
    """Error must fall as 1/sqrt(dim): quadrupling dim halves it."""
    edges, w, n = random_graph()
    D_exact = np.sqrt(np.maximum(exact_resistance_matrix(edges, w, n, reach=1e-2), 0.0))
    iu = np.triu_indices(n, 1)
    errs = []
    for dim in (16, 64, 256, 1024):
        X = resistance_embedding(edges, w, n, dim=dim, reach=1e-2, seed=0)
        D = distance_matrix(X)
        errs.append(float(np.median(np.abs(D[iu] - D_exact[iu]) / D_exact[iu])))

    assert errs == sorted(errs, reverse=True), f"error not monotone: {errs}"
    for a, b in zip(errs, errs[1:]):
        assert 1.6 < a / b < 2.6, f"ratio {a/b:.2f} off the 1/sqrt(k) rate ({errs})"
    assert errs[-1] < 0.03


def test_sketch_is_deterministic():
    """Same input, same index -- unlike a model whose weights drift between versions."""
    edges, w, n = random_graph()
    a = resistance_embedding(edges, w, n, dim=32, seed=7)
    b = resistance_embedding(edges, w, n, dim=32, seed=7)
    assert np.array_equal(a, b)


# ------------------------------------------------------- the LMD contraction law

def test_reproduces_the_ring_telemetry_closed_form():
    """The published sweep is d = sqrt(k(N-k)/N) * J^-1/2, an algebraic identity.

    Reproduced through the telemetry's own path (a dense pseudo-inverse of the
    ungrounded Laplacian) against the closed form. The measured slope of -0.500000
    at R^2 = 1.000000 is not a fit succeeding; it is this identity being evaluated,
    which is why the published run reports no residual scatter whatsoever.
    """
    N, k = 100, 50
    for J in (0.1, 1.1787686347935878, 100.0):
        L = np.zeros((N, N))
        for i in range(N):
            j = (i + 1) % N
            L[i, i] += J
            L[j, j] += J
            L[i, j] -= J
            L[j, i] -= J
        P = np.linalg.pinv(L)
        d = np.sqrt(P[0, 0] + P[k, k] - 2 * P[0, k])
        assert d == pytest.approx(np.sqrt(k * (N - k) / N) / np.sqrt(J), rel=1e-9)


def test_grounded_engine_converges_to_the_ungrounded_telemetry():
    """PROX's horizon term is a controlled perturbation: reach -> 0 recovers LMD.

    The residual is bounded by conditioning, not by modelling error -- cond(A)
    grows as 1/reach, so a tolerance near 1e-4 is the floor double precision allows
    at reach = 1e-12, and the bias shrinks monotonically with reach.
    """
    N, k, J = 100, 50, 1.0
    target = np.sqrt(k * (N - k) / N) / np.sqrt(J)
    prev = np.inf
    for reach in (1e-6, 1e-9, 1e-12):
        edges, w, n = ring(N, J)
        d = np.sqrt(max(exact_resistance_matrix(edges, w, n, reach=reach)[0, k], 0.0))
        err = abs(d - target) / target
        assert err < prev, "grounding bias must shrink as reach falls"
        prev = err
    assert err < 1e-4


def test_contraction_law_survives_compression_exactly():
    """Scaling every coupling by J scales the sketch by exactly J^-1/2.

    C -> sqrt(J) C, so A -> J A and X = A^-1 (QC)^T -> J^-1/2 X, with the same Q.
    The -0.5 slope of the telemetry is therefore preserved to machine precision
    through the compressed index -- which is what makes coupling a usable dial
    rather than an internal hyper-parameter.
    """
    edges, w, n = random_graph(n=150, seed=3)
    Js = np.logspace(-1, 2, 15)
    d = []
    for J in Js:
        X = resistance_embedding(edges, w * J, n, dim=32, reach=1e-2 * J, seed=0)
        d.append(float(np.linalg.norm(X[0] - X[7])))
    slope, _ = np.polyfit(np.log10(Js), np.log10(d), 1)
    r2 = np.corrcoef(np.log10(Js), np.log10(d))[0, 1] ** 2
    assert slope == pytest.approx(-0.5, abs=1e-9), f"slope {slope}"
    assert r2 == pytest.approx(1.0, abs=1e-12)


def test_per_class_coupling_changes_geometry():
    """Independent dials must actually move the space, or the control is a placebo."""
    texts = ["alpha beta gamma", "beta gamma delta", "epsilon zeta eta", "zeta eta theta"]
    rel = [(0, 2, "link")]
    weak = prox.build(texts, relations=rel, couplings={"link": 1e-3}, dim=64, seed=0)
    strong = prox.build(texts, relations=rel, couplings={"link": 1e3}, dim=64, seed=0)

    def gap(ix):
        return float(np.linalg.norm(ix.X_items[0] - ix.X_items[2]))

    assert gap(strong) < 0.5 * gap(weak)
