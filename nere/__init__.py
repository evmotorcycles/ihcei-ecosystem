"""NERE: the reasoning engine inside the infrastructure layer.

v1.0.0

A composite path that separates drawing a claim from reading its structure.

**Infrastructure, not a product.** Per LAYERS.md, NERE has no interface and an
ordinary person should never encounter the name. `test_layers.py` fails if a
page appears that presents it as a tool someone operates.

What it does NOT do, in the same size type as what it does:

  * It does not read documents. No language model runs here and no text is
    parsed. `DependencyTracingExtractor` validates a drawing someone else made;
    it cannot find an edge.
  * The semantic layer ABSTAINS. There is no benchmarked latent-energy model in
    this repository, so `JEPASemanticFilter` scores nothing and no number
    leaves it. The effective path is extractor -> LMD.
  * It does not say whether a claim is true. Layer 1 and Layer 3 describe where
    a chain came from. A Layer-1 claim can be false; a Layer-3 claim can be
    correct.
  * It computes nothing itself. `spar`, `fathom` and `smi` do the measuring and
    have their own suites.

Predictions locked in prereg_nere.md, sha256
81a0c16b22a81c9d89df8c3153d9cfacc98e7ec5889a292b90f124828b45248c
"""

from .extractor import DependencyTracingExtractor
from .firewall import EpistemicFirewall
from .jepa_filter import JEPASemanticFilter
from .lmd_engine import LMDTelemetryEngine
from .pipeline import NEREPipeline
from .values import (Edge, Graph, Layer, NodeType, Provenance, SemanticVerdict)

__version__ = "1.0.0"
__all__ = [
    "DependencyTracingExtractor",
    "JEPASemanticFilter",
    "LMDTelemetryEngine",
    "EpistemicFirewall",
    "NEREPipeline",
    "Edge", "Graph", "Layer", "NodeType", "Provenance", "SemanticVerdict",
]
