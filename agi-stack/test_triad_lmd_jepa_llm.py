"""Triad architecture: LLM (symbolic) · JEPA (perceptual stub) · LMD (structure).

    python3 -m pytest -q agi-stack/test_triad_lmd_jepa_llm.py

NOT an AGI run. Tests roles, handoffs, gameability, and F_out == F_eval.
Prediction names T1-T8 are kept from the supplied module.

WHAT WAS CHANGED FROM THE SUPPLIED VERSION, AND WHY
===================================================
The module arrived with two tests that CANNOT FAIL as written. Both are fixed
here and both are recorded rather than quietly repaired --
test_the_two_supplied_tests_that_could_not_fail holds the evidence.

  1. `total_bearing()` returned `len(nodes) - len(components)`. It never reads
     the edges. Asserting `b0 == b1` across the padding attack is therefore
     `3.0 == 3.0` BY CONSTRUCTION: it ASSERTS Foster's theorem instead of
     TESTING it. Replaced with the measured sum of bearings from the tested
     engine, compared against parts - pieces. Foster does hold -- 3.0 both
     sides -- but now that is a measurement.

  2. `test_t7` asserted `claim not in ("true", "holds")`, comparing a sentence
     to a two-element tuple. Always true, tests nothing. Replaced with a grep of
     the shipped consumer surfaces for the overclaim.

Two further notes, smaller:
  3. `deepest_dependence()` was a hand-written proxy (normalised inverse
     resistance). CLAUDE.md: measure the structure, never hand-write the number.
     Replaced with FATHOM `sound()`.
  4. `test_llm_padding_changes_lmd_cuts` asserted only that the edge count grew,
     despite its name. It now checks the cut set.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from spar.spar import Structure, bearings, single_points   # noqa: E402
from fathom.fathom import Claim, sound                     # noqa: E402


# ── the repo's engines, behind the supplied module's names ──────────────────
@dataclass
class Graph:
    nodes: List[str]
    edges: List[Tuple[str, str, float]]

    def structure(self) -> Structure:
        return Structure(list(self.nodes), [tuple(e) for e in self.edges])


def connected_components(g: Graph) -> List[Set[str]]:
    adj: Dict[str, Set[str]] = {n: set() for n in g.nodes}
    for u, v, _ in g.edges:
        adj[u].add(v)
        adj[v].add(u)
    seen: Set[str] = set()
    comps: List[Set[str]] = []
    for n in g.nodes:
        if n in seen:
            continue
        stack, comp = [n], set()
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            stack.extend(adj[x] - comp)
        seen |= comp
        comps.append(comp)
    return comps


def cut_vertices(g: Graph) -> Set[str]:
    """From the tested engine, not reimplemented."""
    if len(g.nodes) < 3:
        return set()
    return {r["part"] for r in single_points(g.structure())}


def measured_bearing_total(g: Graph) -> float:
    """The SUM OF MEASURED BEARINGS -- w x R over every edge. This is the
    quantity Foster's theorem is about. The supplied helper returned
    parts - pieces directly, which is the theorem's right-hand side, so
    comparing it across an attack could not fail."""
    return float(bearings(g.structure())["total"])


def foster_expected(g: Graph) -> float:
    return float(len(g.nodes) - len(connected_components(g)))


def deepest_dependence(g: Graph, result: str, supports: List[str]) -> float:
    """FATHOM, not a proxy. How much the conclusion rests on its single
    heaviest support, by removal."""
    return float(sound(Claim(result, list(supports),
                             [tuple(e) for e in g.edges]))["deepest_dependence"])


# ── F_out = F_eval ──────────────────────────────────────────────────────────
@dataclass
class EdgeProposal:
    u: str
    v: str
    weight: float = 1.0
    source: Optional[str] = None


def f_eval_admit(proposals: List[EdgeProposal], require_source: bool = True):
    return [p for p in proposals if p.source or not require_source]


def build_graph(nodes, proposals, require_source=True) -> Graph:
    admitted = f_eval_admit(proposals, require_source)
    return Graph(list(nodes), [(p.u, p.v, p.weight) for p in admitted])


# ── stubs. No network, no model, no AGI. ────────────────────────────────────
def llm_extract_nodes(text: str) -> List[str]:
    return [t.strip() for t in text.split(";") if t.strip()]


def jepa_latent_edge_proposals(nodes: List[str]) -> List[EdgeProposal]:
    """Deliberately empty. A real JEPA would need a latent/action benchmark and
    there is none here; returning anything would be inventing a capability."""
    return []


def llm_edge_proposals(nodes, aggressive=False) -> List[EdgeProposal]:
    props = [EdgeProposal(nodes[i], nodes[i + 1], 1.0, source="llm:order")
             for i in range(len(nodes) - 1)]
    if aggressive and len(nodes) >= 4:
        props += [EdgeProposal(nodes[0], nodes[2], 1.0, source="llm:pad"),
                  EdgeProposal(nodes[1], nodes[3], 1.0, source="llm:pad"),
                  EdgeProposal(nodes[0], nodes[3], 1.0, source="llm:pad")]
    return props


# ── fixtures ────────────────────────────────────────────────────────────────
NODES = ["premise_a", "premise_b", "bridge", "conclusion"]
SUPPORTS = ["premise_a", "premise_b"]


@pytest.fixture
def honest_graph():
    return build_graph(NODES, [
        EdgeProposal("premise_a", "bridge", 1.0, source="doc:1"),
        EdgeProposal("premise_b", "bridge", 1.0, source="doc:2"),
        EdgeProposal("bridge", "conclusion", 1.0, source="doc:3"),
    ])


@pytest.fixture
def padded_graph():
    return build_graph(NODES, [
        EdgeProposal("premise_a", "bridge", 1.0, source="doc:1"),
        EdgeProposal("premise_b", "bridge", 1.0, source="doc:2"),
        EdgeProposal("bridge", "conclusion", 1.0, source="doc:3"),
        EdgeProposal("premise_a", "conclusion", 1.0, source="pad:1"),
        EdgeProposal("premise_b", "conclusion", 1.0, source="pad:2"),
        EdgeProposal("premise_a", "premise_b", 1.0, source="pad:3"),
    ])


# ── T3 ──────────────────────────────────────────────────────────────────────
def test_t3_cut_vertex_detectable(honest_graph):
    assert "bridge" in cut_vertices(honest_graph)


# ── T4: the falsification, not a success ────────────────────────────────────
def test_t4_padding_removes_cut_vertices(honest_graph, padded_graph):
    """Encodes the FAILURE of "cannot trick the Laplacian" as a product claim.
    Three edges between nodes already present, no evidence added."""
    assert len(cut_vertices(honest_graph)) >= 1
    assert len(cut_vertices(padded_graph)) == 0
    assert len(padded_graph.edges) - len(honest_graph.edges) == 3


# ── T5: split readouts ──────────────────────────────────────────────────────
def test_t5_foster_conservation_is_measured_not_assumed(honest_graph, padded_graph):
    """The real Foster test. Sum the MEASURED bearings and compare to
    parts - pieces. 3.0 on both sides of the attack, and the left-hand side
    actually touched the edges this time."""
    for g in (honest_graph, padded_graph):
        assert measured_bearing_total(g) == pytest.approx(foster_expected(g), abs=1e-9)
    assert measured_bearing_total(honest_graph) == pytest.approx(
        measured_bearing_total(padded_graph), abs=1e-9)
    assert measured_bearing_total(honest_graph) == pytest.approx(3.0, abs=1e-9)


def test_t5_dependence_does_not_fall_under_the_pad(honest_graph, padded_graph):
    """The STRONG form the supplied module marked as preferred. It holds: the
    padding raises concentration rather than lowering it, so the attack that
    clears the cut set indicts itself on the other readout."""
    d0 = deepest_dependence(honest_graph, "conclusion", SUPPORTS)
    d1 = deepest_dependence(padded_graph, "conclusion", SUPPORTS)
    assert d1 >= d0 - 1e-9, f"dependence fell under padding: {d0} -> {d1}"


def test_t5_never_fuse_into_one_score(honest_graph, padded_graph):
    def panel(g):
        return {"cut_vertices": sorted(cut_vertices(g)),
                "bearing_total": measured_bearing_total(g),
                "n_edges": len(g.edges)}
    p0, p1 = panel(honest_graph), panel(padded_graph)
    assert p0.keys() == p1.keys()
    for k in ("integrity", "score", "health"):
        assert k not in p0
    # the disagreement a fused number would have hidden
    assert p0["cut_vertices"] != p1["cut_vertices"]
    assert p0["bearing_total"] == pytest.approx(p1["bearing_total"])


# ── T6: policy, not maths ───────────────────────────────────────────────────
def test_t6_fill_rule_rejects_sourceless_but_accepts_labeled_pad():
    bare = build_graph(NODES, [EdgeProposal("premise_a", "conclusion", 1.0, None)])
    assert bare.edges == []
    labeled = build_graph(NODES, [EdgeProposal("premise_a", "conclusion", 1.0,
                                               "unverified:x")])
    assert len(labeled.edges) == 1   # the string is never checked for truth


# ── F_out = F_eval ──────────────────────────────────────────────────────────
def test_f_out_equals_f_eval_count():
    props = [EdgeProposal("premise_a", "bridge", 1.0, "doc:1"),
             EdgeProposal("premise_b", "bridge", 1.0, "doc:2"),
             EdgeProposal("bridge", "conclusion", 1.0, "doc:3")]
    admitted = f_eval_admit(props)
    assert len(build_graph(NODES, props).edges) == len(admitted)
    surplus = props + [EdgeProposal("premise_a", "conclusion", 1.0, None)]
    assert len(build_graph(NODES, surplus).edges) == len(admitted)


# ── T1: orthogonal roles ────────────────────────────────────────────────────
def test_t1_llm_symbolic_not_topology():
    assert llm_extract_nodes("claim A; claim B; conclusion") == \
        ["claim A", "claim B", "conclusion"]
    assert not hasattr(llm_extract_nodes, "cut_vertices")


def test_t1_jepa_stub_adds_no_argument_edges():
    assert jepa_latent_edge_proposals(NODES) == []


def test_llm_padding_changes_lmd_cuts():
    """Renamed assertion to match the name. The supplied version checked only
    that the edge count grew, which is true of any padding and says nothing
    about cuts."""
    g0 = build_graph(NODES, llm_edge_proposals(NODES, aggressive=False))
    g1 = build_graph(NODES, llm_edge_proposals(NODES, aggressive=True))
    assert len(g1.edges) > len(g0.edges)
    assert len(cut_vertices(g1)) < len(cut_vertices(g0))


# ── T7: a real assertion instead of a vacuous one ───────────────────────────
def test_t7_lmd_not_claimed_as_agi_epistemology_engine():
    """The supplied form was `assert claim not in ("true", "holds")` — a
    sentence compared to a two-word tuple, which can never be false.

    This greps the shipped consumer surfaces instead. If the overclaim ever
    reaches a page, this fails."""
    surfaces = []
    for rel in ("novora-helm/helm.html", "page-code/pagecode.html",
                "plexus/lens.js"):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            surfaces.append((rel, open(p, encoding="utf-8",
                                       errors="replace").read().lower()))
    assert surfaces, "no shipped surface found to check"
    for rel, txt in surfaces:
        for phrase in ("epistemology engine", "agi", "artificial general",
                       "un-gameable", "ungameable", "cannot be tricked"):
            assert phrase not in txt, f"{rel} ships the overclaim: {phrase}"


@pytest.mark.skip(reason="T8 untested: no AGI benchmark; a composite stack is not AGI")
def test_t8_triad_is_not_agi():
    raise AssertionError("unreachable")


# ── LISM ────────────────────────────────────────────────────────────────────
def test_lism_product_decay():
    assert 1.0 * (0.9 ** 4) == pytest.approx(0.6561)


# ── the record ──────────────────────────────────────────────────────────────
def test_the_two_supplied_tests_that_could_not_fail():
    """Kept as evidence rather than silently repaired.

    (1) The supplied `total_bearing` was `len(nodes) - len(components)`. It
        never reads the edges, so comparing it before and after an
        edge-padding attack is 3.0 == 3.0 by construction. It asserted
        Foster's theorem rather than testing it. Reproduced here.

    (2) The supplied T7 was `assert claim not in ("true", "holds")`, comparing
        a sentence to a two-element tuple. Reproduced here.
    """
    honest = Graph(NODES, [("premise_a", "bridge", 1.0),
                           ("premise_b", "bridge", 1.0),
                           ("bridge", "conclusion", 1.0)])
    padded = Graph(NODES, honest.edges + [("premise_a", "conclusion", 1.0),
                                          ("premise_b", "conclusion", 1.0),
                                          ("premise_a", "premise_b", 1.0)])

    def supplied_total_bearing(g):
        return float(len(g.nodes) - len(connected_components(g)))

    # identical, and would be identical for ANY edge set keeping one component
    assert supplied_total_bearing(honest) == supplied_total_bearing(padded)
    assert supplied_total_bearing(Graph(NODES, [])) != supplied_total_bearing(honest)

    # the vacuous T7
    claim = "LMD is the AGI epistemology engine"
    assert claim not in ("true", "holds")          # always true
    assert "anything at all" not in ("true", "holds")   # equally always true


def test_the_measured_bearings_do_conserve_which_is_the_substance():
    """The supplied test was hollow; the claim underneath it is correct. Worth
    separating, because 'the test was bad' is not 'the theorem is wrong'."""
    honest = Graph(NODES, [("premise_a", "bridge", 1.0),
                           ("premise_b", "bridge", 1.0),
                           ("bridge", "conclusion", 1.0)])
    padded = Graph(NODES, honest.edges + [("premise_a", "conclusion", 1.0),
                                          ("premise_b", "conclusion", 1.0),
                                          ("premise_a", "premise_b", 1.0)])
    assert measured_bearing_total(honest) == pytest.approx(3.0, abs=1e-9)
    assert measured_bearing_total(padded) == pytest.approx(3.0, abs=1e-9)
    assert bearings(honest.structure())["conserved"] is True
    assert bearings(padded.structure())["conserved"] is True
