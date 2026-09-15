"""The layering rules, and the one declared fusion.

Layer 1 / Layer 3 are labels about where a claim came from. They are NOT
about whether it is true: a Layer-1 claim can be false, and a Layer-3 claim can
be correct.
"""

from __future__ import annotations

from .extractor import DependencyTracingExtractor
from .values import Graph, Layer, Provenance, SemanticVerdict


class EpistemicFirewall:
    """Decides layering from provenance. Structure is reported, never fused in."""

    CANNOT = (
        "This says where a chain came from, not whether it is true. It cannot "
        "tell whether an edge marked `literal` really is stated in the "
        "document -- that is written by whoever drew the graph."
    )

    #: Why the rule is categorical rather than a tuned fraction: a Layer-1 claim
    #: is one the document states. One inferred edge means the reader supplied
    #: part of the chain, so the claim is not lexical. The sensor is the
    #: provenance tag; there is no threshold to choose.
    RULE = ("Layer 1 requires every edge to be literal. "
            "One interpretive or imported edge makes it Layer 3.")

    def layer(self, g: Graph) -> str:
        if all(e.provenance == Provenance.LITERAL for e in g.edges):
            return Layer.ONE
        return Layer.THREE

    def why(self, g: Graph) -> list:
        """The specific edges that kept it out of Layer 1."""
        return [f"{e.frm} -> {e.to} ({e.provenance}; {e.where})"
                for e in g.edges if e.provenance != Provenance.LITERAL]

    # --------------------------------------------------- the declared fusion --
    #: THIS IS A FUSION AND IS LABELLED ONE. It combines two readouts by
    #: explicit decision, registered in prereg_nere.md.
    #:
    #: Reason: neither half is evidence alone. Cuts fall whenever anyone adds a
    #: link, honestly included. Dependence rises for many reasons. Clearing a
    #: bottleneck while the argument comes to rest HARDER on one thing is the
    #: signature of declaring links rather than finding them.
    #:
    #: It emits a named boolean with both source readouts beside it, produces no
    #: number, and changes no layer.
    FUSION_NOTE = ("declared fusion: cut count fell AND deepest dependence rose "
                   "in the same comparison")

    def padding_tripwire(self, before: dict, after: dict) -> dict:
        b_cuts, a_cuts = len(before["cut_parts"]), len(after["cut_parts"])
        b_dep = before["deepest_dependence"]
        a_dep = after["deepest_dependence"]
        if b_dep is None or a_dep is None:
            return {"is_a_fusion": True, "note": self.FUSION_NOTE,
                    "fired": False, "reading": "no dependence to compare"}
        return {
            "is_a_fusion": True,
            "note": self.FUSION_NOTE,
            "cut_parts_before": b_cuts,
            "cut_parts_after": a_cuts,
            "deepest_dependence_before": b_dep,
            "deepest_dependence_after": a_dep,
            "fired": bool(a_cuts < b_cuts and a_dep > b_dep),
        }

    # -------------------------------------------------------------- report --
    def report(self, g: Graph, telemetry: dict,
               semantic: SemanticVerdict) -> dict:
        ex = DependencyTracingExtractor
        out = {
            "layer": self.layer(g),
            "layer_rule": self.RULE,
            "kept_out_of_layer_1_by": self.why(g),
            "provenance_counts": ex.provenance_counts(g),
            # reported, gates nothing
            "inferred_edge_ratio": ex.inferred_ratio(g),
            "structure": telemetry,
            "semantic_layer": ("ABSTAIN (" + semantic.why + ")"
                               if semantic.abstained else "scored"),
            "handoff": (
                "This measured the structure of the drawing provided. It makes "
                "no claim about whether the drawing corresponds to anything "
                "outside itself. The judgement is the reader's."),
        }
        if semantic.abstained:
            out["semantic_energy"] = None
        return out
