#!/usr/bin/env python3
"""run_smi.py -- the three phases, end to end.

    python3 smi/run_smi.py

  PHASE 1  PRE-REGISTER   hardware, precision, and the architecture
  PHASE 2  TEST           the sweep, and the four predictions that can fail
  PHASE 3  FINALISE       a real mesh, laid out, pulled, and re-composed

Writes smi/results_smi.json. Deterministic: same input, same numbers, offline.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jax                                                        # noqa: E402
import jax.numpy as jnp                                           # noqa: E402

from smi.lmd import (DEAD_MESH_EPS, laplacian_from_edges,         # noqa: E402
                     mesh_metric, metric_from_laplacian, normalised,
                     ring_laplacian, sweep_coupling)
from smi.mesh import SMIMesh                                      # noqa: E402
from smi.compositor import compose, simulate_human_pull_gesture   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BAR = "-" * 74


def rule(title):
    print(f"\n{BAR}\n  {title}\n{BAR}")


def table(rows, headers):
    widths = [max(len(str(h)), *(len(str(r[k])) for r in rows)) for k, h in enumerate(headers)]
    print("  " + "  ".join(str(h).ljust(w) for h, w in zip(headers, widths)))
    print("  " + "  ".join("-" * w for w in widths))
    for r in rows:
        print("  " + "  ".join(str(c).ljust(w) for c, w in zip(r, widths)))


# ======================================================== PHASE 1 ===========
def phase1():
    rule("PHASE 1  PRE-REGISTER — device, precision, architecture")
    x64 = jax.config.read("jax_enable_x64")
    dev = jax.devices()
    table([["backend", jax.default_backend()],
           ["devices", ", ".join(f"{d.platform}:{d.id}" for d in dev)],
           ["jax", jax.__version__],
           ["numpy", np.__version__],
           ["python", platform.python_version()],
           ["float64 enabled", x64],
           ["dtype in use", str(jnp.zeros(1).dtype)]],
          ["parameter", "value"])
    if jax.default_backend() != "gpu":
        print("\n  No GPU here, so this ran on CPU. Nothing degrades: the whole")
        print("  hot path is one pinv, and a 100-node mesh is microseconds either way.")
    if not x64:
        print("\n  WARNING: float64 is off. A 100-node ring reads slope -0.500003,")
        print("  which is noise being read as signal.")

    lock = json.load(open(os.path.join(HERE, "prereg.lock.json"), encoding="utf-8"))
    live = hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest()
    ok = live == lock["prereg_sha256"]
    print(f"\n  pre-registration  {live[:16]}…  {'INTACT' if ok else 'CHANGED SINCE LOCKING'}")
    if not ok:
        print("  the predictions below were not the ones committed to. Treat as void.")
    return {"backend": jax.default_backend(),
            "devices": [f"{d.platform}:{d.id}" for d in dev],
            "jax": jax.__version__, "float64": bool(x64),
            "dtype": str(jnp.zeros(1).dtype),
            "prereg_sha256": live, "prereg_intact": ok}


# ======================================================== PHASE 2 ===========
def phase2():
    rule("PHASE 2  TEST — the sweep, and the four things that can actually fail")

    # ---- H0: the identity. Ring N=100, exactly as specified.
    N = 100
    sw = sweep_coupling(ring_laplacian(N, 1.0), (0, N // 2))
    print("\n  H0  the J-sweep on a 100-node ring")
    table([[f"{J:10.4f}", f"{d:12.6f}"] for J, d in zip(sw.couplings, sw.distances)],
          ["coupling J", f"d(0,{N // 2})"])
    print(f"\n      slope {sw.slope:.6f}   R² {sw.r_squared:.6f}")

    # ---- H0b: the same slope regardless of topology, which is the point.
    rng = np.random.default_rng(42)

    def random_L(n, p):
        A = (rng.random((n, n)) < p).astype(float)
        A = np.triu(A, 1)
        A = A + A.T
        return np.diag(A.sum(1)) - A

    def path_L(n):
        return laplacian_from_edges(n, [(k, k + 1, 1.0) for k in range(n - 1)])

    def star_L(n):
        return laplacian_from_edges(n, [(0, k, 1.0) for k in range(1, n)])

    others = [("ring N=7 (odd)", ring_laplacian(7, 1.0), (0, 3)),
              ("path N=40", path_L(40), (0, 39)),
              ("star N=50", star_L(50), (1, 2)),
              ("random p=0.05 N=80", random_L(80, 0.05), (0, 40)),
              ("random p=0.50 N=30", random_L(30, 0.5), (0, 15))]
    rows, slopes = [], []
    for name, L0, pair in others:
        s = sweep_coupling(L0, pair)
        slopes.append(s.slope)
        rows.append([name, f"{s.slope:.6f}", f"{s.r_squared:.6f}"])
    print("\n  H0b  the same sweep on five other graphs")
    table(rows, ["graph", "slope", "R²"])

    identity = (sw.matches_identity
                and all(abs(s + 0.5) <= 1e-4 for s in slopes))
    print(f"\n  H0  IDENTITY (CONTROL) — {'confirmed' if identity else 'BROKEN'}")
    print("      pinv(J·L) = J⁻¹·pinv(L), so d ∝ J^(−1/2) on every graph, always.")
    print("      This is linear algebra, not a discovery. It is reported as a")
    print("      correctness check on the engine — it fails if pinv breaks — and")
    print("      it is NOT evidence that space is emergent.")

    # ---- H1: uniform J changes scale, never shape.
    base = normalised(np.asarray(metric_from_laplacian(jnp.asarray(ring_laplacian(40, 1.0)))))
    drift = max(float(np.max(np.abs(
        normalised(np.asarray(metric_from_laplacian(jnp.asarray(ring_laplacian(40, J))))) - base)))
        for J in np.logspace(-1, 2, 15))
    h1 = drift < 1e-4
    print(f"\n  H1  uniform J: max change in layout shape = {drift:.3e}   "
          f"[gate < 1e-4]  {'HOLDS' if h1 else 'FAILS'}")
    print("      A screen can zoom without a single element changing neighbours.")

    # ---- H2: a disconnected mesh does NOT report infinite distance.
    L = ring_laplacian(8, 1.0)
    for a, b in [(0, 1), (4, 5)]:
        L[a, b] = L[b, a] = 0.0
        L[a, a] -= 1.0
        L[b, b] -= 1.0
    guarded, labels, _ = mesh_metric(L)
    # cutting (0,1) and (4,5) leaves {5,6,7,0} and {1,2,3,4}. Nodes 0 and 5 are
    # in the SAME piece, so pick a pair that genuinely has no path: 0 and 2.
    a, b = 0, 2
    assert labels[a] != labels[b], "the demonstration pair must be in different pieces"
    raw = float(np.asarray(metric_from_laplacian(jnp.asarray(L)))[a, b])
    same = float(np.asarray(metric_from_laplacian(jnp.asarray(L)))[0, 5])
    h2 = np.isfinite(raw) and raw < 1e3 and not np.isfinite(guarded[a, b])
    print(f"\n  H2  two elements with NO path between them (nodes {a} and {b})")
    table([["raw pinv metric", f"{raw:.6f}", "finite — and meaningless"],
           ["guarded", "inf", "components detected explicitly"],
           ["same-piece pair d(0,5)", f"{same:.6f}", "finite, and correctly so"],
           ["components found", int(labels.max() + 1), ""]],
          ["", "distance", "note"])
    print(f"      {'CONFIRMED' if h2 else 'NOT CONFIRMED'} — the specified "
          "'broken links yield infinite distance' is false as written.")
    print("      Unguarded, the layout would place unrelated elements side by side.")

    # ---- H3: J -> 0 collapses to zero, not infinity.
    rows, zero_at_zero = [], None
    for J in [1e-2, 1e-4, 1e-8, 0.0]:
        d = float(np.asarray(metric_from_laplacian(jnp.asarray(ring_laplacian(8, J))))[0, 4])
        rows.append([f"{J:g}", f"{d:.6e}"])
        if J == 0.0:
            zero_at_zero = d
    Dg, _, dead = mesh_metric(ring_laplacian(8, 0.0))
    h3 = zero_at_zero == 0.0 and dead and not np.isfinite(Dg[0, 4])
    print("\n  H3  what happens as coupling goes to zero")
    table(rows, ["uniform J", "d(0,4)"])
    print(f"      {'CONFIRMED' if h3 else 'NOT CONFIRMED'} — distance goes to ZERO, "
          "not to infinity.")
    print("      A completely broken mesh would render as a perfectly contracted")
    print("      one. The engine special-cases it and returns inf instead.")

    # ---- H4: a local pull is not a global rescale.
    N4 = 24
    L1 = ring_laplacian(N4, 1.0)
    D1, _, _ = mesh_metric(L1)
    L2 = L1.copy()
    L2[0, 1] = L2[1, 0] = -6.0
    L2[0, 0] += 5.0
    L2[1, 1] += 5.0
    D2, _, _ = mesh_metric(L2)
    delta = np.abs(D2[0] - D1[0])
    hops = np.array([min(k, N4 - k) for k in range(N4)])
    by_hop = [delta[hops == h].mean() for h in range(1, N4 // 2 + 1)]
    pairs = list(zip(by_hop, by_hop[1:]))
    mono = sum(1 for a, b in pairs if b <= a + 1e-12) / len(pairs)
    h4 = mono >= 0.90
    print(f"\n  H4  raising J on ONE wire (a pull gesture), N={N4}")
    table([[h, f"{v:.6f}"] for h, v in zip(range(1, 7), by_hop[:6])],
          ["hops from the pulled edge", "mean shift"])
    print(f"      falls off monotonically over {mono * 100:.0f}% of hop steps "
          f"[gate ≥ 90%]  {'HOLDS' if h4 else 'FAILS'}")
    print("      A local pull rearranges; a global J only zooms. That difference")
    print("      is the whole reason the interface can be dragged.")

    return {"H0_identity": {"slope": sw.slope, "r_squared": sw.r_squared,
                            "other_graph_slopes": slopes,
                            "result": "IDENTITY (CONTROL)" if identity else "BROKEN",
                            "note": "pinv(J·L)=J⁻¹·pinv(L); true on every graph; "
                                    "not evidence about space"},
            "H1_shape_invariance": {"max_drift": drift, "gate": 1e-4,
                                    "result": "HOLDS" if h1 else "FAILS"},
            "H2_disconnected_is_finite": {"pair": [a, b], "raw": raw, "guarded": "inf",
                                          "components": int(labels.max() + 1),
                                          "result": "CONFIRMED" if h2 else "NOT CONFIRMED"},
            "H3_zero_coupling_collapses": {"d_at_J0": zero_at_zero,
                                           "result": "CONFIRMED" if h3 else "NOT CONFIRMED"},
            "H4_local_pull_is_local": {"monotone_fraction": mono, "gate": 0.90,
                                       "by_hop": [float(v) for v in by_hop[:6]],
                                       "result": "HOLDS" if h4 else "FAILS"},
            "sweep": {"couplings": sw.couplings.tolist(),
                      "distances": sw.distances.tolist()}}


# ======================================================== PHASE 3 ===========
def build_invoice_mesh():
    """A small real screen: a price, a quantity, and what falls out of them."""
    m = SMIMesh()
    m.add_node("qty", "Quantity", 12)
    m.add_node("unit", "Unit price", 4.50)
    m.add_node("net", "Net")
    m.add_node("vat", "VAT at 20%")
    m.add_node("total", "Total due")
    m.add_node("terms", "Payment terms")
    m.add_node("late", "Late fee")

    m.connect("qty", "net", lambda q: q * 4.50, J=4.0, label="× unit price")
    m.connect("unit", "net", lambda u: u * 12, J=4.0, label="× quantity")
    m.connect("net", "vat", lambda n: round(n * 0.20, 2), J=8.0, label="20%")
    m.connect("net", "total", lambda n: round(n * 1.20, 2), J=8.0, label="+ VAT")
    m.connect("vat", "total", lambda v: None, J=2.0, label="checked against VAT")
    m.connect("terms", "late", lambda t: t, J=0.5, label="if overdue")
    return m


def phase3():
    rule("PHASE 3  FINALISE — a real screen, laid out and then dragged")
    m = build_invoice_mesh()
    frame = compose(m, anchor="qty")

    print("\n  the screen as composed (positions derived, never authored)")
    table([[n["id"], n["text"][:18], "—" if n["value"] is None else n["value"],
            f'{n["x"]:7.1f}', f'{n["y"]:7.1f}',
            "—" if n["distance_from_anchor"] is None else f'{n["distance_from_anchor"]:.4f}',
            n["state"]] for n in frame["nodes"]],
          ["node", "label", "value", "x", "y", "d from qty", "state"])

    print("\n  the wires")
    table([[f'{w["source"]}→{w["target"]}', f'{w["J"]:6.2f}',
            "—" if w["distance"] is None else f'{w["distance"]:.4f}',
            f'{w["tension"]:.3f}', f'{w["width"]:.2f}', w["state"]]
           for w in frame["wires"]],
          ["wire", "J", "distance", "tension", "stroke", "state"])
    print(f"\n  components {frame['components']}   "
          f"stranded {frame['stranded'] or 'none'}   dead {frame['dead']}")

    # ---- the gesture
    print("\n  simulate_human_pull_gesture('net' → 'total', −0.97): drag it away")
    pull = simulate_human_pull_gesture(m, "net", "total", -0.97, anchor="qty")
    table([[r["id"], f'{r["moved_px"]:8.2f}', r["state_before"], r["state_after"]]
           for r in pull["moved"]],
          ["node", "moved px", "before", "after"])
    print(f"      J {pull['J_before']:.2f} → {pull['J_after']:.3f}   "
          f"cut {pull['cut']}   newly rotted {pull['newly_rotted'] or 'none'}")

    # ---- cut it completely
    print("\n  now cut the wire entirely (J → 0)")
    cut = simulate_human_pull_gesture(m, "terms", "late", -1.0, anchor="qty")
    after = cut["after"]
    table([[n["id"], n["state"], n["colour"],
            "—" if n["distance_from_anchor"] is None else f'{n["distance_from_anchor"]:.4f}']
           for n in after["nodes"]],
          ["node", "state", "colour", "d from qty"])
    print(f"      stranded: {after['stranded']}   components: {after['components']}")
    print("      An element with no path back to the anchor renders grey and")
    print("      broken — not as a slightly more distant live element.")

    return {"frame": frame, "pull": {k: pull[k] for k in
                                     ("wire", "J_before", "J_after", "cut", "moved",
                                      "newly_rotted")},
            "cut": {"stranded": after["stranded"], "components": after["components"],
                    "states": {n["id"]: n["state"] for n in after["nodes"]}}}


# ============================================================================
def main():
    print("=" * 74)
    print("  SYNAPTIC MESH INTERFACE — layout derived from effective resistance")
    print("=" * 74)
    out = {"phase1_prereg": phase1(), "phase2_test": phase2(), "phase3_finalise": phase3()}

    rule("VERDICT")
    p2 = out["phase2_test"]
    table([["H0  d ∝ J^(−1/2)", p2["H0_identity"]["result"],
            "an algebraic identity, used here as an engine check"],
           ["H1  shape invariant under uniform J", p2["H1_shape_invariance"]["result"],
            "a screen can zoom without reordering"],
           ["H2  disconnected ⇒ finite distance", p2["H2_disconnected_is_finite"]["result"],
            "the spec is wrong; guarded explicitly"],
           ["H3  J→0 ⇒ distance 0, not ∞", p2["H3_zero_coupling_collapses"]["result"],
            "the spec is inverted; guarded explicitly"],
           ["H4  a local pull stays local", p2["H4_local_pull_is_local"]["result"],
            "what makes dragging meaningful"]],
          ["prediction", "result", "note"])

    print("\n  The sweep reproduces slope −0.500000 with R² 1.000000, and would")
    print("  do so on any graph anyone ever passes it. That is why it is labelled")
    print("  IDENTITY (CONTROL) here and not PASS: a check that cannot fail is not")
    print("  evidence, it is a smoke test — a useful one, kept for that reason.")

    path = os.path.join(HERE, "results_smi.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\n  wrote {os.path.relpath(path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
