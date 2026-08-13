#!/usr/bin/env python3
"""mesh.py -- nodes, synapses, and the layout they imply.

An SMI screen is not a set of boxes at coordinates. It is a graph of what
depends on what, and the coordinates fall out of the graph:

    SMINode      one live element: a label, a number, a result
    SMISynapse   a wire: source -> target, a rule, and a coupling J
    SMIMesh      the whole screen, plus the layout it currently implies

Positions come from the metric (lmd.py), not from a designer. Move a
dependency and the picture rearranges because the arithmetic changed, not
because an animation was written.

Deterministic throughout: same mesh in, same pixels out. No model, no weights,
no network. The whole layout for 100 nodes is one pinv.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from .lmd import laplacian_from_edges, mesh_metric, normalised


@dataclass
class SMINode:
    """One live element on the screen."""
    node_id: str
    text: str = ""
    value: float | None = None          # current surface value, None = unresolved
    x: float = 0.0
    y: float = 0.0

    @property
    def resolved(self):
        return self.value is not None


@dataclass
class SMISynapse:
    """A wire from one element to another: how the value gets there, and how hard.

    `rule` is a plain deterministic function of the upstream value. It is called
    with one float and must return a float or None. None means "the upstream did
    not determine this" -- the downstream stays unresolved rather than guessing,
    which is the same rule the rest of this project follows everywhere.
    """
    source: str
    target: str
    rule: Callable[[float], float | None] = lambda v: v
    J: float = 1.0
    label: str = ""

    @property
    def broken(self):
        return self.J <= 0.0


@dataclass
class SMIMesh:
    """A screen. Nodes, wires, and whatever layout those two imply right now."""
    nodes: dict = field(default_factory=dict)
    synapses: list = field(default_factory=list)

    # ------------------------------------------------------------ building --
    def add_node(self, node_id, text="", value=None):
        if node_id in self.nodes:
            raise ValueError(f"there is already a node called {node_id!r}")
        self.nodes[node_id] = SMINode(node_id, text, value)
        return self.nodes[node_id]

    def connect(self, source, target, rule=lambda v: v, J=1.0, label=""):
        for nid in (source, target):
            if nid not in self.nodes:
                raise KeyError(f"no node called {nid!r}")
        self.synapses.append(SMISynapse(source, target, rule, J, label))
        return self.synapses[-1]

    @property
    def order(self):
        return list(self.nodes)

    def index(self, node_id):
        return self.order.index(node_id)

    # ------------------------------------------------------------- the maths -
    def laplacian(self):
        """Only live wires carry current. A broken one is not a weak one."""
        idx = {nid: k for k, nid in enumerate(self.order)}
        edges = [(idx[s.source], idx[s.target], s.J)
                 for s in self.synapses if not s.broken]
        return laplacian_from_edges(len(self.nodes), edges)

    def distances(self):
        """(D, component labels, dead?) -- the trustworthy metric, inf and all."""
        return mesh_metric(self.laplacian())

    # ---------------------------------------------------------- propagation --
    def recompute(self):
        """Push values along the wires, in dependency order, without guessing.

        A node whose upstream is unresolved stays unresolved. A rule that returns
        None leaves its target unresolved. Nothing downstream of a broken wire
        gets a number, and no number is ever invented to fill a gap.
        """
        incoming = {}
        for s in self.synapses:
            incoming.setdefault(s.target, []).append(s)

        roots = [nid for nid in self.order if nid not in incoming]
        for nid in self.order:
            if nid not in roots:
                self.nodes[nid].value = None

        settled, changed = set(roots), True
        while changed:
            changed = False
            for target, wires in incoming.items():
                if target in settled:
                    continue
                live = [w for w in wires if not w.broken and w.source in settled]
                if not live:
                    continue
                src = self.nodes[live[0].source]
                if not src.resolved:
                    continue
                self.nodes[target].value = live[0].rule(src.value)
                settled.add(target)
                changed = True

        return {nid: n.value for nid, n in self.nodes.items()}

    # -------------------------------------------------------------- layout ---
    def layout(self, width=1000.0, height=640.0, anchor=None, seed=0):
        """Turn the distance matrix into x, y on a screen.

        Classical multidimensional scaling: double-centre the squared distance
        matrix and take its top two eigenvectors. The result is the flat picture
        that best preserves the metric -- so what is near on screen is near in
        the dependency graph, and that is the only reason anything is anywhere.

        Nodes cut off from `anchor` cannot be placed by the metric (their
        distance is infinite). They are parked, deterministically, and marked --
        an unreachable element must not be quietly drawn next to a live one.
        """
        D, labels, dead = self.distances()
        order = self.order
        n = len(order)
        anchor_i = self.index(anchor) if anchor else 0
        reachable = np.isfinite(D[anchor_i])
        stranded = [order[k] for k in range(n) if not reachable[k]]

        if dead or reachable.sum() < 2:
            # nothing to lay out. Parking everything on a line is honest;
            # inventing a picture is not.
            for k, nid in enumerate(order):
                self.nodes[nid].x = width * 0.5
                self.nodes[nid].y = height * (k + 1) / (n + 1)
            return {"stranded": list(order), "dead": True, "placed": 0}

        keep = np.nonzero(reachable)[0]
        sub = D[np.ix_(keep, keep)] ** 2
        m = len(keep)
        Jc = np.eye(m) - np.ones((m, m)) / m
        B = -0.5 * Jc @ sub @ Jc
        vals, vecs = np.linalg.eigh(B)
        top = np.argsort(vals)[::-1][:2]
        coords = vecs[:, top] * np.sqrt(np.clip(vals[top], 0.0, None))

        span = coords.max(0) - coords.min(0)
        span[span == 0] = 1.0
        pad = 0.08
        norm = (coords - coords.min(0)) / span
        for slot, k in enumerate(keep):
            self.nodes[order[k]].x = float((pad + norm[slot, 0] * (1 - 2 * pad)) * width)
            self.nodes[order[k]].y = float((pad + norm[slot, 1] * (1 - 2 * pad)) * height)

        # Stranded nodes go down the right-hand edge, evenly, every time. The
        # inset is generous because a NODE IS A BOX, not a point: parking the
        # centre at 0.965 hung half of every label off the edge of the picture.
        for j, nid in enumerate(stranded):
            self.nodes[nid].x = width * 0.88
            self.nodes[nid].y = height * (j + 1) / (len(stranded) + 1)

        return {"stranded": stranded, "dead": False, "placed": int(len(keep))}

    def shape(self):
        """Layout with scale divided out. H1 says uniform J cannot change this."""
        D, _, _ = self.distances()
        return normalised(np.where(np.isfinite(D), D, 0.0))
