"""Synthetic handoff graphs. Every one of them was drawn by this project.

There is no real handoff telemetry in this repository and none is reachable from
this container -- `DOOR1_STATUS.md` and `DOOR2_STATUS.md` record both doors shut
on container egress. These fixtures are the whole substrate the sentry has.
"""

from __future__ import annotations

#: The one retention used across every fixture, so that the only thing varying
#: between them is the SHAPE. A per-hop sweep would confound the two.
D = 0.9


def _retentions(links, d=D):
    return {(a, b) if a <= b else (b, a): d for a, b in links}


def chain(n):
    """`n` agents in a line: `n - 1` hops, one route."""
    parts = [f"a{i}" for i in range(n)]
    links = [(parts[i], parts[i + 1]) for i in range(n - 1)]
    return parts, links, _retentions(links)


def subdivided_chain(n, hop):
    """P11a: a relay inserted into `hop` (0-based). Still one route, one longer."""
    parts, links, _ = chain(n)
    a, b = links[hop]
    relay = f"relay[{a}->{b}]"
    links = links[:hop] + [(a, relay), (relay, b)] + links[hop + 1:]
    return parts[:] + [relay], links, _retentions(links)


def bypass_chain(n, frm, to):
    """P11b: the chain, plus one edge skipping from `a{frm}` to `a{to}`."""
    parts, links, _ = chain(n)
    links = links + [(f"a{frm}", f"a{to}")]
    return parts, links, _retentions(links)


def star(leaves):
    """P12a: one hub, `leaves` leaves. Structure sees a cut vertex."""
    parts = ["hub"] + [f"leaf{i}" for i in range(leaves)]
    links = [("hub", f"leaf{i}") for i in range(leaves)]
    return parts, links, _retentions(links)


def ring(n):
    """P12b: a cycle. Structure sees nothing -- a ring is 2-connected."""
    parts = [f"a{i}" for i in range(n)]
    links = [(parts[i], parts[(i + 1) % n]) for i in range(n)]
    return parts, links, _retentions(links)
