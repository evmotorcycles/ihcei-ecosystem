"""The two drawings of one document, and a padding attack on the second.

Both are hand-made from the uploaded study. Every edge carries its `where`.
Neither is a reading of the document's meaning: they are pictures of what the
document says rests on what, and the numbers that follow are readings of the
pictures.
"""

from __future__ import annotations

from .extractor import DependencyTracingExtractor as Ex
from .values import NodeType as T
from .values import Provenance as P

PASSAGES = ["passage 1", "passage 2", "passage 3"]
METHOD = "the one declared method"
METAPHOR = "the declared metaphor"
CONCLUSION = "the conclusion about the chapter"

_W_ROUTE = ('the document states the passages "will not make any sense" without '
            'the declared method, so they are drawn as routing through it')
_W_CONCL = "the concluding section draws the conclusion from the method"
_W_SPLIT = ("this drawing separates the metaphor from the method; the locked "
            "reading in order-invariance/prereg_order.md does not")


def locked_five_part():
    """The reading locked in order-invariance/prereg_order.md (sha 9c9872e4...)."""
    ex = Ex()
    for p in PASSAGES:
        ex.add_part(p, T.EVIDENCE)
    ex.add_part(METHOD, T.METHOD)
    ex.add_part(CONCLUSION, T.CONCLUSION)
    for p in PASSAGES:
        ex.add_link(p, METHOD, 1.0, P.INTERPRETIVE, _W_ROUTE)
    ex.add_link(METHOD, CONCLUSION, 1.0, P.INTERPRETIVE, _W_CONCL)
    return ex.build()


def six_part_metaphor_split():
    """An ALTERNATIVE drawing, not a correction of the locked one.

    NULL-N2 of the locked file already says a different modelling decision
    gives a different number. This is that case, measured.
    """
    ex = Ex()
    for p in PASSAGES:
        ex.add_part(p, T.EVIDENCE)
    ex.add_part(METAPHOR, T.METHOD)
    ex.add_part(METHOD, T.METHOD)
    ex.add_part(CONCLUSION, T.CONCLUSION)
    for p in PASSAGES:
        ex.add_link(p, METAPHOR, 1.0, P.INTERPRETIVE, _W_SPLIT)
    ex.add_link(METAPHOR, METHOD, 1.0, P.INTERPRETIVE, _W_SPLIT)
    ex.add_link(METHOD, CONCLUSION, 1.0, P.INTERPRETIVE, _W_CONCL)
    return ex.build()


def padded_six_part():
    """Edges only. No new parts, no new evidence, nothing removed.

    The adversary declares more links between things already in the drawing.
    Every added edge is tagged `imported`, because that is what it is: brought
    from outside the document. A drawer who tagged them `literal` would get a
    different layer, and nothing here can catch that.
    """
    g = six_part_metaphor_split()
    ex = Ex()
    for n, k in g.nodes.items():
        ex.add_part(n, k)
    for e in g.edges:
        ex.add_link(e.frm, e.to, e.weight, e.provenance, e.where)
    where = "added by the padding attack; no source in the document"
    for frm, to in (("passage 1", METHOD), ("passage 2", CONCLUSION),
                    ("passage 3", METHOD), (METAPHOR, CONCLUSION)):
        ex.add_link(frm, to, 1.0, P.IMPORTED, where)
    return ex.build()


def all_literal_toy():
    """A drawing whose every edge is literal, so Layer 1 is reachable at all."""
    ex = Ex()
    ex.add_part("a stated figure", T.EVIDENCE)
    ex.add_part("a stated total", T.CONCLUSION)
    ex.add_link("a stated figure", "a stated total", 1.0, P.LITERAL,
                "the document prints both and states the second follows")
    return ex.build()
