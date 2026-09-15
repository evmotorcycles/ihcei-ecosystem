"""The values the pipeline passes between stages.

ABSTAIN is a value here, not an exception. A stage that cannot answer returns a
verdict saying so, and the stages downstream must consume it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple


class Provenance:
    """Where an edge came from. Written by whoever drew the graph."""

    LITERAL = "literal"          # the document states this link in so many words
    INTERPRETIVE = "interpretive"  # the reader inferred it from the document
    IMPORTED = "imported"        # the reader brought it from outside the document

    ALL = (LITERAL, INTERPRETIVE, IMPORTED)


class NodeType:
    EVIDENCE = "evidence"
    METHOD = "method"
    CONCLUSION = "conclusion"

    ALL = (EVIDENCE, METHOD, CONCLUSION)


class Layer:
    """Where a claim came from. NOT whether it is true.

    A Layer-1 claim can be false. A Layer-3 claim can be correct. These labels
    describe the provenance of the chain, and nothing else.
    """

    ONE = "Layer 1 (stated)"
    THREE = "Layer 3 (motivating)"


@dataclass(frozen=True)
class SemanticVerdict:
    """The output of the semantic seam.

    `energy` exists so the shape is right for a future benchmarked model. While
    the seam abstains it is None, and no code may read a number out of it.
    """

    abstained: bool
    why: str
    energy: Optional[float] = None

    @classmethod
    def abstain(cls, why: str) -> "SemanticVerdict":
        return cls(abstained=True, why=why, energy=None)

    def __post_init__(self):
        if self.abstained and self.energy is not None:
            raise ValueError("an abstaining verdict cannot carry an energy")


@dataclass(frozen=True)
class Edge:
    frm: str
    to: str
    weight: float
    provenance: str
    where: str

    def as_tuple(self) -> Tuple[str, str, float]:
        return (self.frm, self.to, self.weight)


@dataclass
class Graph:
    """A drawing. Parts, links, and who said so."""

    nodes: dict = field(default_factory=dict)   # name -> NodeType
    edges: list = field(default_factory=list)   # list[Edge]

    def names(self):
        return list(self.nodes)

    def tuples(self):
        return [e.as_tuple() for e in self.edges]

    def of_type(self, t):
        return [n for n, k in self.nodes.items() if k == t]
