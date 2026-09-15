"""The semantic seam. It abstains on every call.

No benchmarked latent-energy model exists in this repository. The seam is here
so the absence is executable rather than only documented: every run reports the
abstention, and when a benchmarked model arrives the interface is already the
shape it needs.

ABSTAIN is a value the firewall consumes, not an exception to swallow.
"""

from __future__ import annotations

from .values import Graph, SemanticVerdict


class JEPASemanticFilter:
    """Seam for a future benchmarked latent-energy model.

    Abstains on every call until a benchmark exists. No number leaves here.
    """

    CANNOT = (
        "There is no latent-energy model in this repository. This seam scores "
        "nothing, rejects nothing, and admits nothing. It abstains."
    )

    WHY = "no benchmarked JEPA model in repo"

    def evaluate_edges(self, g: Graph) -> SemanticVerdict:
        # `g` is accepted so the signature is the one a real filter would need.
        # It is deliberately not read: reading it would invite a proxy.
        del g
        return SemanticVerdict.abstain(self.WHY)
