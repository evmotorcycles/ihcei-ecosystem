"""PROX — a proximity layer for everything.

The graphical user interface gave every person coordinates on a screen. PROX gives
every person coordinates on their own information: a true metric space, built from
counting alone, on the CPU they already own, with no model, no training data, no
network and no vendor.

    import prox
    ix = prox.build(texts, ids=names)
    ix.search("mtoto ana homa")

Distances obey the triangle inequality exactly, not approximately, so proximity can
be explained and audited rather than merely trusted.
"""

from .core import (
    build_system,
    distance_matrix,
    exact_resistance_matrix,
    resistance_embedding,
    triangle_violations,
)
from .index import FORMAT, ProxIndex, build
from .text import FeatureSpace, normalize

__version__ = "1.0.0"

__all__ = [
    "build", "ProxIndex", "FORMAT", "FeatureSpace", "normalize",
    "resistance_embedding", "exact_resistance_matrix", "build_system",
    "distance_matrix", "triangle_violations", "__version__",
]
