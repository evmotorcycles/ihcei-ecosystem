"""The structural readouts, taken from the engines that are already tested here.

Nothing in this file computes a Laplacian, a pseudo-inverse, an articulation
point or a dependence. `spar`, `fathom` and `smi` do that, and they have their
own suites. This is a wrapper so the pipeline reads one interface.

The three readouts stay separate. `spar` measures load, `fathom` measures what
a conclusion rests on, and `smi` measures distance; they are different kinds of
quantity and no field here combines them.
"""

from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from fathom.fathom import Claim, sound                       # noqa: E402
from smi.lmd import laplacian_from_edges, mesh_metric        # noqa: E402
from spar.spar import Structure, bearings, single_points     # noqa: E402

from .values import Graph, NodeType                           # noqa: E402


class LMDTelemetryEngine:
    """Reads a drawing with the repository's own engines."""

    CANNOT = (
        "This reads what rests on what, in a drawing. It does not read the "
        "document the drawing came from, and cannot tell whether the drawing "
        "is right."
    )

    def structure(self, g: Graph) -> Structure:
        return Structure(g.names(), g.tuples())

    def load(self, g: Graph) -> dict:
        """Foster: the measured bearings sum to parts - pieces, exactly."""
        b = bearings(self.structure(g))
        return {
            "total_bearing": b["total"],
            "expected_total": b["expected_total"],
            "conserved": b["conserved"],
            "parts": b["steps"],
            "pieces": b["pieces"],
        }

    def cut_parts(self, g: Graph) -> list:
        """The parts whose removal breaks the drawing into more pieces."""
        return sorted(r["part"] for r in single_points(self.structure(g)))

    def resistance(self, g: Graph, a: str, b: str):
        """Effective resistance between two parts, or None if no route.

        mesh_metric walks the adjacency rather than asking pinv whether a path
        exists, so an unreachable pair comes back as no reading at all -- not
        as a small confident number.
        """
        names = g.names()
        idx = {n: i for i, n in enumerate(names)}
        L = laplacian_from_edges(len(names),
                                 [(idx[x], idx[y], w) for x, y, w in g.tuples()])
        D, _, _ = mesh_metric(L)
        d = float(D[idx[a]][idx[b]])
        if not math.isfinite(d):
            return None
        return d * d

    def deepest_dependence(self, g: Graph):
        """FATHOM. Returns None when the drawing has no conclusion to sound."""
        concl = g.of_type(NodeType.CONCLUSION)
        if len(concl) != 1:
            return None
        sources = [n for n in g.names()
                   if g.nodes[n] == NodeType.EVIDENCE and n != concl[0]]
        if not sources:
            return None
        return float(sound(Claim(concl[0], sources, g.tuples()))["deepest_dependence"])

    def read(self, g: Graph) -> dict:
        """All three readouts, side by side and never combined."""
        concl = g.of_type(NodeType.CONCLUSION)
        evid = g.of_type(NodeType.EVIDENCE)
        r = None
        if len(concl) == 1 and evid:
            r = self.resistance(g, sorted(evid)[0], concl[0])
        return {
            "load": self.load(g),
            "cut_parts": self.cut_parts(g),
            "resistance_first_evidence_to_conclusion": r,
            "deepest_dependence": self.deepest_dependence(g),
        }
