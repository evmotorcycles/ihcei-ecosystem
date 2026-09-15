"""The NERE pipeline, checked against predictions locked before it was wired.

A caution this suite cannot remove: E4-E10 are predictions about code written
in the same commit to satisfy them. They are specification, not discovery, and
`test_most_of_these_predictions_are_specification_not_discovery` says so.
The only prediction here that could have gone either way was E14.
"""

import hashlib
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from nere import (DependencyTracingExtractor, EpistemicFirewall,     # noqa: E402
                  JEPASemanticFilter, LMDTelemetryEngine, NEREPipeline,
                  NodeType, Provenance, SemanticVerdict)
from nere.drawings import (all_literal_toy, locked_five_part,        # noqa: E402
                           padded_six_part, six_part_metaphor_split)

PREREG_SHA = "81a0c16b22a81c9d89df8c3153d9cfacc98e7ec5889a292b90f124828b45248c"

SHIPPED = ["__init__.py", "extractor.py", "firewall.py", "jepa_filter.py",
           "lmd_engine.py", "pipeline.py", "values.py", "drawings.py"]


@pytest.fixture(scope="module")
def run():
    p = NEREPipeline()
    six = six_part_metaphor_split()
    padded = padded_six_part()
    return {
        "five": p.run(locked_five_part()),
        "six": p.run(six),
        "toy": p.run(all_literal_toy()),
        "cmp": p.compare(six, padded),
        "added": len(padded.edges) - len(six.edges),
    }


# ------------------------------------------------------------- the lock ----
def test_the_preregistration_is_the_one_that_was_hashed():
    with open(os.path.join(HERE, "prereg_nere.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == PREREG_SHA


def test_the_module_declares_the_same_hash():
    import nere
    assert PREREG_SHA in nere.__doc__


# ------------------------------------------- arm 1: the two drawings ----
def test_e1_the_locked_five_part_drawing(run):
    s = run["five"]["structure"]
    assert s["load"]["total_bearing"] == pytest.approx(4.0, abs=1e-9)
    assert s["load"]["conserved"]
    assert s["cut_parts"] == ["the one declared method"]


def test_e2_the_six_part_drawing(run):
    s = run["six"]["structure"]
    assert s["load"]["total_bearing"] == pytest.approx(5.0, abs=1e-9)
    assert s["cut_parts"] == ["the declared metaphor", "the one declared method"]


def test_e3_resistance_is_three_on_the_six_part_drawing(run):
    s = run["six"]["structure"]
    assert s["resistance_first_evidence_to_conclusion"] == pytest.approx(3.0, abs=1e-9)


def test_the_two_drawings_of_one_document_disagree(run):
    """The drawing dictates the telemetry. Neither reading corrects the other."""
    a = run["five"]["structure"]
    b = run["six"]["structure"]
    assert a["load"]["total_bearing"] != b["load"]["total_bearing"]
    assert len(a["cut_parts"]) == 1 and len(b["cut_parts"]) == 2
    assert a["resistance_first_evidence_to_conclusion"] != \
        b["resistance_first_evidence_to_conclusion"]


def test_the_locked_reading_is_named_as_the_locked_one():
    src = open(os.path.join(HERE, "drawings.py"), encoding="utf-8").read()
    assert "order-invariance/prereg_order.md" in src
    assert "ALTERNATIVE" in src


# --------------------------------------------- arm 2: the abstaining seam ----
def test_e4_the_seam_abstains_on_every_call():
    f = JEPASemanticFilter()
    for g in (locked_five_part(), six_part_metaphor_split(), all_literal_toy()):
        assert f.evaluate_edges(g).abstained


def test_e5_no_number_leaves_the_seam():
    v = JEPASemanticFilter().evaluate_edges(all_literal_toy())
    assert v.abstained
    assert v.energy is None


def test_an_abstaining_verdict_cannot_be_given_an_energy():
    """The type refuses it, so a future edit cannot quietly fill the box."""
    with pytest.raises(ValueError):
        SemanticVerdict(abstained=True, why="x", energy=0.5)


def test_e6_the_abstention_reaches_the_report(run):
    for key in ("five", "six", "toy"):
        assert "ABSTAIN" in run[key]["semantic_layer"]
        assert run[key]["semantic_energy"] is None


def test_the_pipeline_refuses_a_seam_that_starts_scoring():
    """If a model is wired in without updating the contract, the run stops."""
    class Scoring(JEPASemanticFilter):
        def evaluate_edges(self, g):
            return SemanticVerdict(abstained=False, why="wired", energy=0.1)

    p = NEREPipeline()
    p.semantic = Scoring()
    with pytest.raises(RuntimeError):
        p.run(all_literal_toy())


# ------------------------------------------------------- arm 3: firewall ----
def test_e7_an_edge_without_provenance_is_refused():
    ex = DependencyTracingExtractor()
    ex.add_part("a", NodeType.EVIDENCE).add_part("b", NodeType.CONCLUSION)
    with pytest.raises(ValueError, match="no provenance"):
        ex.add_link("a", "b", 1.0, where="somewhere")


def test_an_edge_without_a_where_is_refused():
    ex = DependencyTracingExtractor()
    ex.add_part("a", NodeType.EVIDENCE).add_part("b", NodeType.CONCLUSION)
    with pytest.raises(ValueError, match="no `where`"):
        ex.add_link("a", "b", 1.0, Provenance.LITERAL, where="")


def test_a_part_without_a_type_is_refused():
    with pytest.raises(ValueError):
        DependencyTracingExtractor().add_part("a", "guess")


def test_parts_with_no_links_are_an_empty_result_not_a_zero():
    ex = DependencyTracingExtractor()
    ex.add_part("a", NodeType.EVIDENCE)
    with pytest.raises(ValueError, match="empty result, not a zero"):
        ex.build()


def test_e8_both_n182_drawings_are_layer_three(run):
    assert run["five"]["layer"] == "Layer 3 (motivating)"
    assert run["six"]["layer"] == "Layer 3 (motivating)"
    assert run["six"]["kept_out_of_layer_1_by"]


def test_e9_an_all_literal_drawing_reaches_layer_one(run):
    """Otherwise the Layer-3 result above would be vacuous."""
    assert run["toy"]["layer"] == "Layer 1 (stated)"
    assert run["toy"]["kept_out_of_layer_1_by"] == []


def test_the_layer_rule_is_categorical_and_states_its_reason():
    assert "every edge to be literal" in EpistemicFirewall.RULE
    prereg = open(os.path.join(HERE, "prereg_nere.md"), encoding="utf-8").read()
    assert "categorical, not a tuned number" in prereg


def _ratio_graph(n_literal, n_interpretive):
    """A chain where the first n_literal edges are literal and the rest are not."""
    ex = DependencyTracingExtractor()
    total = n_literal + n_interpretive
    for i in range(total + 1):
        ex.add_part(f"s{i}", NodeType.EVIDENCE if i < total else NodeType.CONCLUSION)
    for i in range(total):
        ex.add_link(f"s{i}", f"s{i + 1}", 1.0,
                    Provenance.LITERAL if i < n_literal else Provenance.INTERPRETIVE,
                    "constructed for this test")
    return ex.build()


def test_the_thirty_percent_gate_was_not_added(run):
    """Behavioural, not a grep: one inferred edge in ten is BELOW any such gate.

    If a 30%-of-edges downgrade existed, a ratio of 0.1 would still read
    Layer 1. It does not, because the rule is categorical.
    """
    p = NEREPipeline()
    low = p.run(_ratio_graph(9, 1))
    assert low["inferred_edge_ratio"] == pytest.approx(0.1)
    assert low["layer"] == "Layer 3 (motivating)"

    clean = p.run(_ratio_graph(10, 0))
    assert clean["inferred_edge_ratio"] == pytest.approx(0.0)
    assert clean["layer"] == "Layer 1 (stated)"


def test_the_ratio_is_reported_and_decides_nothing(run):
    """Two drawings, same layer, different ratios."""
    p = NEREPipeline()
    a, b = p.run(_ratio_graph(9, 1)), p.run(_ratio_graph(1, 9))
    assert a["inferred_edge_ratio"] != b["inferred_edge_ratio"]
    assert a["layer"] == b["layer"]
    assert run["six"]["inferred_edge_ratio"] == pytest.approx(1.0)


def test_e10_no_fused_field_reaches_the_report(run):
    """Structure and provenance stay in separate blocks with separate keys."""
    banned = re.compile(r"score|confidence|composite|combined|overall|fused|index",
                        re.I)
    for key in ("five", "six", "toy"):
        rep = run[key]
        for k in rep:
            assert not banned.search(k), f"{key}: {k}"
        assert set(rep["structure"]) & set(rep["provenance_counts"]) == set()


def test_the_report_states_what_it_did_not_do(run):
    assert "makes" in run["six"]["handoff"]
    assert "no claim" in run["six"]["handoff"]


# ----------------------------------- arm 4: the attack and the one fusion ----
def test_e11_padding_clears_every_cut_part(run):
    assert run["cmp"]["before"]["cut_parts"]
    assert run["cmp"]["after"]["cut_parts"] == []


def test_e12_it_took_at_most_four_added_edges(run):
    assert run["added"] <= 4


def test_e13_the_measured_foster_total_is_immune_to_padding(run):
    b = run["cmp"]["before"]["load"]
    a = run["cmp"]["after"]["load"]
    assert b["total_bearing"] == pytest.approx(5.0, abs=1e-9)
    assert a["total_bearing"] == pytest.approx(5.0, abs=1e-9)
    assert a["conserved"]


def test_e14_dependence_rises_under_padding(run):
    """The one prediction here that could have gone either way."""
    b = run["cmp"]["before"]["deepest_dependence"]
    a = run["cmp"]["after"]["deepest_dependence"]
    assert a > b


def test_the_attack_defeats_one_readout_of_three(run):
    """Cuts gamed, Foster immune, dependence moved against the attacker."""
    c = run["cmp"]
    assert len(c["after"]["cut_parts"]) < len(c["before"]["cut_parts"])   # gamed
    assert c["after"]["load"]["total_bearing"] == \
        pytest.approx(c["before"]["load"]["total_bearing"])               # immune
    assert c["after"]["deepest_dependence"] > c["before"]["deepest_dependence"]


def test_the_fusion_is_labelled_a_fusion_and_produces_no_number(run):
    tw = run["cmp"]["padding_tripwire"]
    assert tw["is_a_fusion"] is True
    assert "declared fusion" in tw["note"]
    assert isinstance(tw["fired"], bool)
    assert tw["fired"] is True
    # both source readouts stay separately readable beside it
    assert tw["cut_parts_before"] > tw["cut_parts_after"]
    assert tw["deepest_dependence_after"] > tw["deepest_dependence_before"]


def test_the_fusion_is_registered_in_the_prereg():
    prereg = open(os.path.join(HERE, "prereg_nere.md"), encoding="utf-8").read()
    assert "The declared fusion" in prereg
    assert "recorded as a fusion, not hidden as a score" in prereg


# ----------------------------------------------------- what it cannot do ----
def test_every_stage_states_what_it_cannot_do():
    for cls in (DependencyTracingExtractor, JEPASemanticFilter,
                LMDTelemetryEngine, EpistemicFirewall, NEREPipeline):
        assert cls.CANNOT and len(cls.CANNOT) > 60, cls.__name__


def test_the_extractor_says_it_is_not_a_language_model():
    d = DependencyTracingExtractor.__doc__ + DependencyTracingExtractor.CANNOT
    assert "does not read" in d.lower() or "not read documents" in d.lower()
    assert "language model" in d.lower()


def test_nere_ships_no_interface():
    """LAYERS.md: infrastructure that grows a GUI has stopped being infrastructure."""
    for f in os.listdir(HERE):
        assert not f.endswith((".html", ".htm", ".js", ".mjs")), f


def test_the_shipped_module_never_claims_the_errand_was_done():
    """`check` is an errand; the past participles claim it was completed."""
    done = ["check" + "ed", "veri" + "fied", "sup" + "ported"]
    for f in SHIPPED:
        text = open(os.path.join(HERE, f), encoding="utf-8").read().lower()
        for w in done:
            assert w not in text, f"{f} contains {w}"


def test_most_of_these_predictions_are_specification_not_discovery():
    """The honest caveat, kept in the suite rather than in a footnote.

    E4-E10 describe code written in the same commit to satisfy them. E1-E3 and
    E13 are fixed by Foster's theorem. Only E14 could have gone either way.
    """
    prereg = open(os.path.join(HERE, "prereg_nere.md"), encoding="utf-8").read()
    assert "verification, not discovery" in prereg
    assert "E14 is the one I could be wrong about" in prereg
