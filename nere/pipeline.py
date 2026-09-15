"""The four stages, composed.

Because the semantic seam abstains, the effective path is
extractor -> LMD -> firewall. The seam still runs, and its abstention is
carried into every report rather than dropped.
"""

from __future__ import annotations

from .firewall import EpistemicFirewall
from .jepa_filter import JEPASemanticFilter
from .lmd_engine import LMDTelemetryEngine
from .values import Graph


class NEREPipeline:
    """One way in. Each stage can only refuse."""

    CANNOT = (
        "Nothing here reads a document, understands a sentence, or decides "
        "whether a claim is true. It reads a drawing and says what rests on "
        "what."
    )

    def __init__(self):
        self.semantic = JEPASemanticFilter()
        self.telemetry = LMDTelemetryEngine()
        self.firewall = EpistemicFirewall()

    def run(self, g: Graph) -> dict:
        verdict = self.semantic.evaluate_edges(g)
        if not verdict.abstained:
            raise RuntimeError(
                "the semantic seam returned a score; no benchmarked model "
                "exists, so this cannot happen without one being wired in")
        readings = self.telemetry.read(g)
        return self.firewall.report(g, readings, verdict)

    def compare(self, before: Graph, after: Graph) -> dict:
        """Two drawings, side by side, plus the one declared fusion."""
        b = self.telemetry.read(before)
        a = self.telemetry.read(after)
        return {
            "before": b,
            "after": a,
            "padding_tripwire": self.firewall.padding_tripwire(b, a),
        }
