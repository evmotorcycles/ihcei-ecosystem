#!/usr/bin/env python3
"""Guards for the Synaptic Mesh Interface.

    python3 -m pytest -q smi/test_smi.py

The most important tests here are the ones that keep the -0.5 slope labelled
honestly. It is an algebraic identity that holds on every graph, so a suite
that only checked "slope == -0.5" would be checking that arithmetic works and
reporting it as a discovery.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import jax                                                              # noqa: E402
import jax.numpy as jnp                                                 # noqa: E402

from smi.lmd import (components, laplacian_from_edges, mesh_metric,     # noqa: E402
                     metric_from_laplacian, normalised, ring_laplacian,
                     sweep_coupling)
from smi.mesh import SMIMesh                                            # noqa: E402
from smi.compositor import (ROT_COLOUR, compose, node_style,            # noqa: E402
                            simulate_human_pull_gesture, tension, wire_style)


# ------------------------------------------------------- the pre-registration
def test_the_prereg_is_unchanged_since_it_was_locked():
    live = hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest()
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json"), encoding="utf-8"))
    assert live == lock["prereg_sha256"], \
        "PREREG.md changed after locking; the predictions are no longer the committed ones"


def test_the_prereg_says_up_front_that_the_slope_is_an_identity():
    src = open(os.path.join(HERE, "PREREG.md"), encoding="utf-8").read()
    assert "IDENTITY, NOT A RESULT" in src
    assert "cannot fail" in src


def test_float64_is_on():
    """At float32 the N=100 ring reads -0.500003, and that is noise as signal."""
    assert jax.config.read("jax_enable_x64") is True
    assert jnp.zeros(1).dtype == jnp.float64


# ---------------------------------------------------- H0: the identity itself
def test_the_slope_is_minus_half_on_the_specified_ring():
    sw = sweep_coupling(ring_laplacian(100, 1.0), (0, 50))
    assert abs(sw.slope + 0.5) < 1e-4
    assert sw.r_squared >= 0.999999
    assert sw.matches_identity


@pytest.mark.parametrize("name,L,pair", [
    ("ring odd", ring_laplacian(7, 1.0), (0, 3)),
    ("path", laplacian_from_edges(30, [(k, k + 1, 1.0) for k in range(29)]), (0, 29)),
    ("star", laplacian_from_edges(20, [(0, k, 1.0) for k in range(1, 20)]), (1, 2)),
    ("complete", laplacian_from_edges(
        12, [(i, j, 1.0) for i in range(12) for j in range(i + 1, 12)]), (0, 11)),
])
def test_the_same_slope_appears_on_every_topology(name, L, pair):
    """This is the test that stops the sweep being read as a discovery."""
    sw = sweep_coupling(L, pair)
    assert abs(sw.slope + 0.5) < 1e-4, f"{name} should give the identity too"
    assert sw.r_squared >= 0.999999


def test_the_identity_holds_for_every_pair_not_just_antipodal_ones():
    L = ring_laplacian(16, 1.0)
    for j in range(1, 16):
        sw = sweep_coupling(L, (0, j), steps=8)
        assert abs(sw.slope + 0.5) < 1e-4, f"pair (0,{j})"


def test_the_algebra_behind_it_holds_directly():
    """pinv(J·L) == J⁻¹·pinv(L). Everything else about the slope follows."""
    L = np.asarray(ring_laplacian(24, 1.0))
    base = np.asarray(jnp.linalg.pinv(jnp.asarray(L)))
    for J in (0.3, 1.0, 7.5, 91.0):
        scaled = np.asarray(jnp.linalg.pinv(jnp.asarray(J * L)))
        assert np.allclose(scaled, base / J, atol=1e-12)


def test_the_results_file_never_calls_the_invariant_a_pass():
    r = json.load(open(os.path.join(HERE, "results_smi.json"), encoding="utf-8"))
    h0 = r["phase2_test"]["H0_identity"]
    assert h0["result"] == "INVARIANT (BY CONSTRUCTION)"
    assert "verifies\nnothing" in h0["note"] or "verifies nothing" in h0["note"]


def test_nothing_printed_claims_a_result_about_the_physical_world():
    """The scope is software. Denying a physics claim four times implied one had
    been made, so the denials went; what must not appear is the claim itself."""
    src = open(os.path.join(HERE, "run_smi.py"), encoding="utf-8").read()
    printed = "\n".join(ln for ln in src.splitlines() if "print(" in ln)
    for phrase in ("Space is Emergent", "spacetime", "the nature of space",
                   "physical distance", "dead matter"):
        assert phrase.lower() not in printed.lower(), f"printed: {phrase!r}"


def test_the_scope_is_stated_and_the_prereg_was_not_rewritten_to_match_it():
    """An amendment records a framing change. It must not quietly move a gate."""
    scope = open(os.path.join(HERE, "SCOPE.md"), encoding="utf-8").read()
    assert "information layer" in scope
    assert "Changes no prediction, no gate, and no\nnumber" in scope or \
        "changes no prediction" in scope.lower()
    # the locked file is still the locked file
    live = hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest()
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json"), encoding="utf-8"))
    assert live == lock["prereg_sha256"], \
        "the pre-registration was edited to match the amendment — that is not an amendment"
    # and every gate it fixed is still the gate the code uses
    prereg = open(os.path.join(HERE, "PREREG.md"), encoding="utf-8").read()
    for gate in ("−0.5 ± 1e-4", "≥ 0.999999", "< 1e-4", "≥ 0.90"):
        assert gate in prereg


# --------------------------------------------------------- H1: shape vs scale
def test_uniform_coupling_changes_scale_but_not_shape():
    base = normalised(np.asarray(metric_from_laplacian(jnp.asarray(ring_laplacian(30, 1.0)))))
    for J in np.logspace(-1, 2, 9):
        D = normalised(np.asarray(metric_from_laplacian(jnp.asarray(ring_laplacian(30, J)))))
        assert np.max(np.abs(D - base)) < 1e-4


def test_but_the_scale_really_does_change():
    """Otherwise the invariance above would be vacuous."""
    a = float(np.asarray(metric_from_laplacian(jnp.asarray(ring_laplacian(30, 0.1))))[0, 15])
    b = float(np.asarray(metric_from_laplacian(jnp.asarray(ring_laplacian(30, 100.0))))[0, 15])
    assert a / b > 30


# ------------------------------------ H2 + H3: where the specification is wrong
def _split_ring(n=8, cuts=((0, 1), (4, 5))):
    L = ring_laplacian(n, 1.0)
    for a, b in cuts:
        L[a, b] = L[b, a] = 0.0
        L[a, a] -= 1.0
        L[b, b] -= 1.0
    return L


def test_raw_pinv_reports_a_finite_distance_across_a_broken_mesh():
    """The specified behaviour — 'broken links yield infinite distance' — is false."""
    L = _split_ring()
    lab = components(L)
    a, b = 0, 2
    assert lab[a] != lab[b], "the test pair must genuinely have no path"
    raw = float(np.asarray(metric_from_laplacian(jnp.asarray(L)))[a, b])
    assert np.isfinite(raw) and raw < 1e3, \
        "if this ever becomes inf, the guard below is no longer needed"


def test_the_guarded_metric_returns_infinity_where_there_is_no_path():
    L = _split_ring()
    D, lab, dead = mesh_metric(L)
    assert not dead
    assert lab.max() == 1, "the ring should be in exactly two pieces"
    assert not np.isfinite(D[0, 2]), "no path means no distance"
    assert np.isfinite(D[0, 5]), "same piece: a real, finite distance"


def test_zero_coupling_collapses_distance_to_zero_not_infinity():
    """The specified visual rule is inverted at the limit, and this proves it."""
    d = float(np.asarray(metric_from_laplacian(jnp.asarray(ring_laplacian(8, 0.0))))[0, 4])
    assert d == 0.0, "a totally broken mesh measures as maximally CONTRACTED"


def test_the_guarded_metric_calls_a_dead_mesh_dead():
    D, _, dead = mesh_metric(ring_laplacian(8, 0.0))
    assert dead is True
    assert not np.isfinite(D[0, 4])
    assert D[3, 3] == 0.0, "a node is still zero distance from itself"


def test_weak_but_present_coupling_is_not_treated_as_dead():
    D, _, dead = mesh_metric(ring_laplacian(8, 1e-6))
    assert dead is False
    assert np.isfinite(D[0, 4]) and D[0, 4] > 1e3


# ------------------------------------------------------------- H4: a local pull
def test_a_local_pull_falls_off_with_distance():
    n = 24
    L1 = ring_laplacian(n, 1.0)
    D1, _, _ = mesh_metric(L1)
    L2 = L1.copy()
    L2[0, 1] = L2[1, 0] = -6.0
    L2[0, 0] += 5.0
    L2[1, 1] += 5.0
    D2, _, _ = mesh_metric(L2)
    delta = np.abs(D2[0] - D1[0])
    hops = np.array([min(k, n - k) for k in range(n)])
    by_hop = [delta[hops == h].mean() for h in range(1, n // 2 + 1)]
    steps = list(zip(by_hop, by_hop[1:]))
    mono = sum(1 for a, b in steps if b <= a + 1e-12) / len(steps)
    assert mono >= 0.90, f"only {mono:.0%} of steps fall off"
    assert by_hop[0] > by_hop[-1] * 2, "the nearest node must move most"


def test_a_local_pull_is_not_the_same_as_a_global_rescale():
    """H1 must NOT apply here, or dragging would be indistinguishable from zoom."""
    L1 = ring_laplacian(20, 1.0)
    L2 = L1.copy()
    L2[0, 1] = L2[1, 0] = -9.0
    L2[0, 0] += 8.0
    L2[1, 1] += 8.0
    s1 = normalised(np.asarray(metric_from_laplacian(jnp.asarray(L1))))
    s2 = normalised(np.asarray(metric_from_laplacian(jnp.asarray(L2))))
    assert np.max(np.abs(s1 - s2)) > 1e-3, "a local change must change the shape"


# --------------------------------------------------------------- the compositor
def _invoice():
    m = SMIMesh()
    m.add_node("qty", "Quantity", 12)
    m.add_node("net", "Net")
    m.add_node("vat", "VAT")
    m.add_node("aside", "Unrelated note", 1.0)
    m.connect("qty", "net", lambda q: q * 4.5, J=4.0)
    m.connect("net", "vat", lambda x: round(x * 0.2, 2), J=8.0)
    return m


def test_values_propagate_and_are_never_invented():
    m = _invoice()
    vals = m.recompute()
    assert vals["net"] == 54.0 and vals["vat"] == 10.8
    assert vals["aside"] == 1.0


def test_a_broken_wire_leaves_everything_downstream_unresolved():
    m = _invoice()
    m.synapses[0].J = 0.0
    vals = m.recompute()
    assert vals["net"] is None and vals["vat"] is None, \
        "nothing downstream of a cut may carry a number"


def test_an_unreachable_element_renders_grey_and_broken():
    frame = compose(_invoice(), anchor="qty")
    aside = next(n for n in frame["nodes"] if n["id"] == "aside")
    assert aside["state"] == "ROTTED"
    assert aside["colour"] == ROT_COLOUR
    assert aside["distance_from_anchor"] is None


def test_a_wire_between_two_dead_elements_does_not_render_live():
    """Two cut-off elements are still coupled to EACH OTHER, and their own
    distance is small. Styling on that alone drew a taut live wire inside a
    region of the screen that was entirely dead."""
    m = _invoice()
    m.add_node("aside2", "Another note", 2.0)
    m.connect("aside", "aside2", J=9.0)
    frame = compose(m, anchor="qty")
    w = next(w for w in frame["wires"] if w["source"] == "aside")
    assert np.isfinite(w["distance"]), "they really are close to each other"
    assert w["state"] == "ROTTED", "but neither is attached to the picture"


def test_two_elements_are_never_drawn_on_the_same_pixel():
    m = SMIMesh()
    m.add_node("root", "Root", 1.0)
    m.add_node("a", "A")
    m.add_node("b", "B")
    m.connect("root", "a", J=3.0)
    m.connect("root", "b", J=3.0)          # a and b are metrically identical
    frame = compose(m, anchor="root")
    pts = [(n["x"], n["y"]) for n in frame["nodes"]]
    assert len(set(pts)) == len(pts), f"elements stacked exactly: {frame['collisions']}"


def test_tension_is_defined_at_both_ends():
    assert tension(float("inf")) == 0.0
    assert tension(0.0) == 1.0
    assert 0.0 < tension(1.0) < 1.0


def test_a_taut_wire_is_drawn_thinner_than_a_slack_one():
    taut = wire_style(0.05, d_ref=1.0)
    slack = wire_style(6.0, d_ref=1.0)
    assert taut.state == "LIVE" and slack.state == "SLACK"
    assert taut.width < slack.width, "tight should read as a hairline, not a rope"


def test_a_resolved_and_an_unresolved_element_look_different():
    assert node_style(True, True).state == "LIVE"
    assert node_style(True, False).state == "HELD"
    assert node_style(False, True).state == "ROTTED"
    assert node_style(False, False).state == "ROTTED"


def test_pulling_a_wire_moves_the_near_nodes_and_reports_which():
    m = _invoice()
    out = simulate_human_pull_gesture(m, "qty", "net", -0.9, anchor="qty")
    assert out["J_after"] < out["J_before"]
    assert not out["cut"]
    assert any(r["moved_px"] > 0 for r in out["moved"]), "a pull must move something"
    assert out["moved"] == sorted(out["moved"], key=lambda r: -r["moved_px"])


def test_cutting_a_wire_rots_what_it_was_holding_up():
    m = _invoice()
    out = simulate_human_pull_gesture(m, "net", "vat", -1.0, anchor="qty")
    assert out["cut"] is True
    assert "vat" in out["newly_rotted"]
    assert out["after"]["components"] > out["before"]["components"]


def test_the_whole_frame_is_deterministic():
    a = compose(_invoice(), anchor="qty")
    b = compose(_invoice(), anchor="qty")
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_it_runs_offline_with_no_model_and_no_network():
    for name in ("lmd.py", "mesh.py", "compositor.py"):
        src = open(os.path.join(HERE, name), encoding="utf-8").read()
        for bad in ("requests", "urllib", "http", "torch", "sklearn", "openai", "socket"):
            assert bad not in src, f"{name} reaches for {bad}"
