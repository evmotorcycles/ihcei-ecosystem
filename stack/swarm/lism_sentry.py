"""Serial-fidelity sentry over a handoff graph. Commit 5.

THE LAW
=======
    E = U * prod_k D_k

`U` is the quantity entering a handoff chain; `D_k` in (0, 1] is what hop `k`
retains; `E` is what arrives. **This is a fidelity product and nothing else.**
It is not borrowed from physics, it measures no disorder, and the module is
grepped for that vocabulary by `test_the_module_borrows_no_physics_vocabulary`.
`declarations.md` §3 pins the law and the prohibition together.

THE FLOOR IS A RATIO OF `U`
===========================
`min_ratio` is a **required argument with no default**, expressed as a fraction
of `U`. An absolute floor makes the verdict depend on how much entered the
chain: at `min_E = 0.6` a chain that trips at depth 5 with `U = 1.0` runs to
depth 71 before tripping with `U = 1000.0`, on identical hops. The absolute form
ships in `absolute_floor_trip_depth` **only so that defect can be measured**;
nothing here calls it, in the same arrangement as `leaky_dissonance()` in
`stack/organization/adg_cfe.py`.

TWO ROUTES, REPORTED SIDE BY SIDE, NEVER FUSED
==============================================
A graph with more than one route has more than one product. `ratio_best` is the
highest-fidelity simple route -- the reading an **attacker** gets, because an
attacker picks its route. `ratio_worst` is the lowest. Both are returned and
neither is combined into a single number, because they answer different
questions and `declarations.md` §5 forbids the fusion.

WHAT THIS SENTRY CANNOT DO, in the same size type as what it does
=================================================================
  * It **cannot see a bypass.** Measured on this repository's own fixtures:
    adding one edge that skips three hops of a 5-hop chain lifts `ratio_best`
    from 0.59049 to 0.729, clearing a floor of 0.6 that the unpadded chain
    breached. Serial fidelity is therefore a **third sensor the declared-padding
    attack defeats**, alongside cut vertices and maximum load. Only
    `ratio_worst` and deepest dependence survive that attack.
  * It **cannot read intent, content or correctness.** `D_k` is an input. This
    module does not measure retention from a message; it multiplies the numbers
    it is handed.
  * It **cannot report on any real system.** Every fixture in this package is a
    graph this project drew. No handoff telemetry exists in this repository and
    none is reachable from this container: `DOOR1_STATUS.md` and
    `DOOR2_STATUS.md` record both doors shut on container egress, not on
    inspection.
  * It **refuses rather than guesses** when source and sink have no route
    between them, in the same way `stack/perception/` refuses a pair in two
    different pieces.

SCOPE
=====
Synthetic bounds only. A reading from this module is a statement about a
fixture in this package and about nothing else. Pre-registration:
`stack/swarm/prereg_sentry.md`.
"""

from __future__ import annotations

#: Printed with every reading. Grepped by the suite.
SCOPE = (
    "synthetic bounds only: this reading describes a graph drawn in this "
    "repository; no real handoff telemetry exists here and none is reachable "
    "from this container (see DOOR1_STATUS.md, DOOR2_STATUS.md)"
)

#: The floor form that ships. The other one is a measured defect, not an option.
FLOOR_FORM = "ratio-of-U"

BYPASS_NOTE = (
    "ratio_best is defeated by bypass padding; it is reported next to "
    "ratio_worst for that reason and must never be read alone"
)


class NoRouteError(ValueError):
    """Source and sink have no route. A refusal, not a zero."""


class RetentionError(ValueError):
    """A hop retention outside (0, 1], or a hop with no declared retention."""


def _key(a, b):
    return (a, b) if a <= b else (b, a)


def _validate(retentions):
    for d in retentions:
        if not (0.0 < d <= 1.0):
            raise RetentionError(f"hop retention {d!r} outside (0, 1]")
    return list(retentions)


# ------------------------------------------------------------- the product ----
def serial_fidelity(retentions) -> float:
    """`prod_k D_k`. The ratio `E/U`, with `U` divided out."""
    out = 1.0
    for d in _validate(retentions):
        out *= d
    return out


def running_ratios(retentions) -> list:
    """The ratio after each hop, in order."""
    out, acc = [], 1.0
    for d in _validate(retentions):
        acc *= d
        out.append(acc)
    return out


def trip_depth(retentions, min_ratio):
    """First hop index (1-based) whose running ratio falls below `min_ratio`.

    `None` if the chain never breaches. `min_ratio` is required -- a default
    floor would be an undeclared threshold, and `declarations.md` forbids one.
    """
    if not (0.0 < min_ratio <= 1.0):
        raise ValueError(f"min_ratio {min_ratio!r} outside (0, 1]")
    for i, r in enumerate(running_ratios(retentions), start=1):
        if r < min_ratio:
            return i
    return None


def absolute_floor_trip_depth(U, retentions, min_E):
    """The floor form that does NOT ship. Present only so its defect is visible.

    Nothing in this module calls it. Its verdict depends on `U`, which is the
    whole reason `FLOOR_FORM` is the ratio: identical hops trip at a different
    depth purely because more entered the chain.
    """
    for i, r in enumerate(running_ratios(retentions), start=1):
        if U * r < min_E:
            return i
    return None


# ------------------------------------------------- the structure, measured ----
def routes(parts, links, source, sink) -> list:
    """Every simple route from `source` to `sink`, walked out of the graph.

    Parts and links go in; routes come out. CLAUDE.md: measure the structure,
    never hand-write the number.
    """
    adj = {p: set() for p in parts}
    for a, b in links:
        if a not in adj or b not in adj:
            raise ValueError(f"link {(a, b)!r} names a part not in `parts`")
        adj[a].add(b)
        adj[b].add(a)
    found, path, seen = [], [source], {source}

    def walk(node):
        if node == sink:
            found.append(tuple(path))
            return
        for nxt in sorted(adj[node]):
            if nxt in seen:
                continue
            seen.add(nxt)
            path.append(nxt)
            walk(nxt)
            path.pop()
            seen.discard(nxt)

    walk(source)
    return sorted(found, key=lambda p: (len(p), p))


def route_retentions(route, retention_of) -> list:
    """The `D_k` along a route, looked up edge by edge."""
    out = []
    for a, b in zip(route, route[1:]):
        k = _key(a, b)
        if k not in retention_of:
            raise RetentionError(f"hop {k!r} has no declared retention")
        out.append(retention_of[k])
    return _validate(out)


# -------------------------------------------------------------- the sentry ----
def sentry(U, parts, links, retention_of, source, sink, min_ratio) -> dict:
    """Both extreme routes, both verdicts, side by side. `min_ratio` required.

    Raises `NoRouteError` when the two agents are not connected. Empty is not
    false and a disconnected pair gets no number at all.
    """
    if U <= 0.0:
        raise ValueError(f"U {U!r} must be positive")
    if not (0.0 < min_ratio <= 1.0):
        raise ValueError(f"min_ratio {min_ratio!r} outside (0, 1]")

    rs = routes(parts, links, source, sink)
    if not rs:
        raise NoRouteError(
            f"no route from {source!r} to {sink!r}; this is a refusal, not a "
            "fidelity of zero")

    scored = [(serial_fidelity(route_retentions(r, retention_of)), r) for r in rs]
    best_ratio, best_route = max(scored, key=lambda t: t[0])
    worst_ratio, worst_route = min(scored, key=lambda t: t[0])

    return {
        "U": U,
        "min_ratio": min_ratio,
        "floor_form": FLOOR_FORM,
        "route_count": len(rs),
        "ratio_best": best_ratio,
        "ratio_worst": worst_ratio,
        "E_best": U * best_ratio,
        "E_worst": U * worst_ratio,
        "route_best": best_route,
        "route_worst": worst_route,
        "depth_best": len(best_route) - 1,
        "depth_worst": len(worst_route) - 1,
        "trips_best": best_ratio < min_ratio,
        "trips_worst": worst_ratio < min_ratio,
        "bypass_note": BYPASS_NOTE,
        "scope": SCOPE,
    }
