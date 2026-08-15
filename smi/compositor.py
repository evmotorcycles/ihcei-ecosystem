#!/usr/bin/env python3
"""compositor.py -- from distances to things you can actually draw.

The metric produces numbers. A compositor turns them into stroke widths,
opacities and dash patterns, and it has to do that without ever drawing a
confident picture of something it does not know.

    tension(d)          how tight a wire is: short = taut and crisp
    wire_style(...)     stroke width, opacity, dash, colour
    node_style(...)     is this element live, or has it rotted?
    simulate_human_pull_gesture(...)   drag an element and watch it settle

THE VISUAL RULE THAT MATTERS
Three states, never two -- the same discipline the rest of this project uses for
verdicts:

    LIVE        connected, resolved      full contrast, solid wire
    SLACK       connected, far away      thin, faded, still real
    ROTTED      unreachable or dead      #475569 grey, broken wireframe

ROTTED is not "very slack". An element cut off from its source has no distance
at all, and rendering it as merely distant would put something unrelated in the
same picture as something live, looking only slightly less important.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

#: how big a node draws, in layout units. Used to keep boxes apart and inside
#: the frame -- a layout engine that positions points and then draws boxes will
#: happily stack two elements and clip a third off the edge.
NODE_W, NODE_H = 150.0, 44.0

#: the grey a dead element fades to
ROT_COLOUR = "#475569"
LIVE_COLOUR = "#0EA5E9"
SLACK_COLOUR = "#64748B"
HELD_COLOUR = "#D97706"


@dataclass(frozen=True)
class WireStyle:
    stroke: str
    width: float
    opacity: float
    dash: str
    state: str

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class NodeStyle:
    colour: str
    opacity: float
    state: str

    def as_dict(self):
        return asdict(self)


def tension(d, d_ref=1.0):
    """How taut a wire is. Short distance = high tension = crisp thin line.

    Bounded to [0, 1] so a compositor can use it directly, and defined at both
    ends: an infinite distance is zero tension, a zero distance is full tension.
    """
    if d is None or not np.isfinite(d):
        return 0.0
    if d <= 0:
        return 1.0
    return float(1.0 / (1.0 + d / max(d_ref, 1e-12)))


def wire_style(d, d_ref=1.0, broken=False, slack_at=0.25, reachable=True):
    """Stroke properties for one synapse.

    High coupling contracts the distance, which raises tension, which draws a
    thin crisp line -- the wire looks tight because it IS tight.

    `reachable` is about the ANCHOR, not about the two endpoints. Two cut-off
    elements are still perfectly coupled to each other, so their own distance is
    small and the wire between them would otherwise draw as taut and live inside
    a region of the screen that is entirely dead. A wire is only live if what it
    joins is still attached to the rest of the picture.
    """
    if broken or not reachable or d is None or not np.isfinite(d):
        return WireStyle(ROT_COLOUR, 1.0, 0.35, "4 6", "ROTTED")
    t = tension(d, d_ref)
    if t < slack_at:
        return WireStyle(SLACK_COLOUR, 1.4, 0.45 + 0.3 * t, "none", "SLACK")
    # taut wires get THINNER, not thicker: a high-frequency hairline reads as
    # tight, a fat rope reads as heavy
    width = float(np.interp(t, [slack_at, 1.0], [2.2, 0.9]))
    opacity = float(np.interp(t, [slack_at, 1.0], [0.7, 1.0]))
    return WireStyle(LIVE_COLOUR, round(width, 3), round(opacity, 3), "none", "LIVE")


def node_style(reachable, resolved):
    """An element is only drawn as live if it is BOTH connected and resolved."""
    if not reachable:
        return NodeStyle(ROT_COLOUR, 0.45, "ROTTED")
    if not resolved:
        # reachable but carrying no value: held, not dead, and not pretending
        return NodeStyle(HELD_COLOUR, 0.85, "HELD")
    return NodeStyle(LIVE_COLOUR, 1.0, "LIVE")


def compose(mesh, anchor=None, width=1000.0, height=640.0):
    """Everything a renderer needs for one frame, as plain data.

    Returns a dict of nodes and wires with positions and styles. No drawing
    happens here -- the same frame description feeds an SVG, a canvas, or a
    terminal table, and can be diffed between frames in a test.
    """
    mesh.recompute()
    info = mesh.layout(width, height, anchor=anchor)
    D, labels, dead = mesh.distances()
    order = mesh.order
    anchor_i = mesh.index(anchor) if anchor else 0
    finite = D[np.isfinite(D)]
    d_ref = float(np.median(finite[finite > 0])) if (finite > 0).any() else 1.0

    nodes = []
    for k, nid in enumerate(order):
        n = mesh.nodes[nid]
        reachable = np.isfinite(D[anchor_i, k]) and not dead
        st = node_style(reachable, n.resolved)
        nodes.append({"id": nid, "text": n.text, "value": n.value,
                      "x": round(n.x, 2), "y": round(n.y, 2),
                      "distance_from_anchor": (None if not reachable
                                               else round(float(D[anchor_i, k]), 6)),
                      **st.as_dict()})

    live_ids = {n["id"] for n in nodes if n["state"] != "ROTTED"}
    wires = []
    for s in mesh.synapses:
        i, j = mesh.index(s.source), mesh.index(s.target)
        d = float(D[i, j])
        joined_to_the_picture = s.source in live_ids and s.target in live_ids
        st = wire_style(d, d_ref, broken=s.broken, reachable=joined_to_the_picture)
        wires.append({"source": s.source, "target": s.target, "label": s.label,
                      "J": s.J, "distance": (None if not np.isfinite(d) else round(d, 6)),
                      "tension": round(tension(d, d_ref), 4), **st.as_dict()})

    # Two elements at the same coordinates are one element as far as a person is
    # concerned. Distinct nodes CAN be metrically identical -- vat and total sit
    # at the same distance from everything by symmetry -- and a flat projection
    # then stacks them exactly. Report it, and nudge deterministically so the
    # picture does not silently hide an element.
    collisions = []
    placed = []
    for n in nodes:
        # A node is a BOX. Two centres 13px apart still draw one on top of the
        # other, so the separation has to clear the box, not the point.
        bump = 0
        while any(abs(n["x"] - px) < NODE_W * 0.75 and abs(n["y"] - py) < NODE_H * 1.15
                  for px, py in placed):
            if bump == 0:
                near = next(i for i, (px, py) in enumerate(placed)
                            if abs(n["x"] - px) < NODE_W * 0.75
                            and abs(n["y"] - py) < NODE_H * 1.15)
                collisions.append([nodes[near]["id"], n["id"]])
            bump += 1
            n["y"] = round(n["y"] + NODE_H * 1.25, 2)
            if bump > len(nodes):
                break
        n["x"] = round(min(max(n["x"], NODE_W / 2), width - NODE_W / 2), 2)
        n["y"] = round(min(max(n["y"], NODE_H), height - NODE_H), 2)
        mesh.nodes[n["id"]].x, mesh.nodes[n["id"]].y = n["x"], n["y"]
        placed.append((n["x"], n["y"]))

    return {"nodes": nodes, "wires": wires, "stranded": info["stranded"],
            "dead": bool(dead), "d_ref": round(d_ref, 6),
            "collisions": collisions,
            "components": int(labels.max() + 1) if len(labels) else 0}


def simulate_human_pull_gesture(mesh, source, target, delta_tension, anchor=None):
    """Drag one element away from (or toward) what it hangs off.

    Pulling away lowers the coupling on that one wire; pushing toward raises it.
    This is deliberately NOT a global rescale -- one edge changes, so the layout
    genuinely rearranges rather than merely zooming, and the frames before and
    after can be compared to see exactly which elements moved and by how much.

    delta_tension > 0 pulls tighter, < 0 pulls apart. J is clamped at 0, which
    is a cut wire, and the compositor renders that as rot rather than as slack.
    """
    wire = next((s for s in mesh.synapses if s.source == source and s.target == target), None)
    if wire is None:
        raise KeyError(f"no wire from {source!r} to {target!r}")

    before = compose(mesh, anchor=anchor)
    J_before = wire.J
    wire.J = max(0.0, J_before * (1.0 + float(delta_tension)))
    after = compose(mesh, anchor=anchor)

    pos_b = {n["id"]: (n["x"], n["y"]) for n in before["nodes"]}
    moved = sorted(
        ({"id": n["id"],
          "moved_px": round(float(np.hypot(n["x"] - pos_b[n["id"]][0],
                                           n["y"] - pos_b[n["id"]][1])), 2),
          "state_before": next(b["state"] for b in before["nodes"] if b["id"] == n["id"]),
          "state_after": n["state"]}
         for n in after["nodes"]),
        key=lambda r: -r["moved_px"])

    return {"wire": f"{source} -> {target}", "J_before": J_before, "J_after": wire.J,
            "cut": wire.broken, "moved": moved,
            "newly_rotted": [m["id"] for m in moved
                             if m["state_after"] == "ROTTED" and m["state_before"] != "ROTTED"],
            "before": before, "after": after}
