"""Builds and validates a drawing. It does NOT read documents.

The name comes from the specification this implements and it overstates what is
here. No language model runs in this module. Nothing is parsed, nothing is
extracted, and no edge is ever found: every part and every link is supplied by
whoever draws the graph, and this class's whole job is to refuse the ones that
do not say where they came from.
"""

from __future__ import annotations

from .values import Edge, Graph, NodeType, Provenance


class DependencyTracingExtractor:
    """A validator. It refuses; it does not discover."""

    CANNOT = (
        "This class does not read text, does not run a language model, and "
        "cannot find an edge. It validates a drawing someone else made."
    )

    def __init__(self):
        self._g = Graph()

    def add_part(self, name: str, kind: str) -> "DependencyTracingExtractor":
        if kind not in NodeType.ALL:
            raise ValueError(
                f"part {name!r} has type {kind!r}; it must be one of "
                f"{NodeType.ALL}. A part with no stated type is refused rather "
                "than defaulted.")
        if name in self._g.nodes:
            raise ValueError(f"two parts are both called {name!r}")
        self._g.nodes[name] = kind
        return self

    def add_link(self, frm: str, to: str, weight: float = 1.0,
                 provenance: str = None, where: str = None):
        """Every link names its provenance and its `where`. No defaults."""
        if provenance is None:
            raise ValueError(
                f"link {frm!r}->{to!r} has no provenance. An untagged link is "
                "refused rather than assumed literal -- assuming it would let "
                "an inferred step read as a stated one.")
        if provenance not in Provenance.ALL:
            raise ValueError(
                f"link {frm!r}->{to!r} has provenance {provenance!r}; it must "
                f"be one of {Provenance.ALL}")
        if not where:
            raise ValueError(
                f"link {frm!r}->{to!r} has no `where`. A hand-assigned link "
                "carries the reason it was drawn, or it is refused.")
        for n in (frm, to):
            if n not in self._g.nodes:
                raise ValueError(f"link {frm!r}->{to!r} names an unknown part {n!r}")
        if frm == to:
            raise ValueError(f"a part cannot depend on itself: {frm!r}")
        if float(weight) <= 0:
            raise ValueError(
                f"link {frm!r}->{to!r} has weight {weight}; a link that is not "
                "there should be left out, not weighted zero")
        self._g.edges.append(Edge(frm, to, float(weight), provenance, where))
        return self

    def build(self) -> Graph:
        if not self._g.nodes:
            raise ValueError("an empty drawing has nothing to read")
        if not self._g.edges:
            raise ValueError(
                "a drawing with parts but no links has nothing to measure; "
                "that is an empty result, not a zero")
        return self._g

    # ------------------------------------------------------------- readouts --
    @staticmethod
    def provenance_counts(g: Graph) -> dict:
        counts = {p: 0 for p in Provenance.ALL}
        for e in g.edges:
            counts[e.provenance] += 1
        return counts

    @staticmethod
    def inferred_ratio(g: Graph) -> float:
        """Reported. It gates nothing.

        A 30%-of-edges downgrade was proposed for this number and is NOT
        registered: it has no stated reason and no sensor beyond itself.
        FLOOR_RETIREMENT.md records a gate retired at p = 0.735 for that.
        """
        if not g.edges:
            return 0.0
        n = sum(1 for e in g.edges if e.provenance != Provenance.LITERAL)
        return n / len(g.edges)
