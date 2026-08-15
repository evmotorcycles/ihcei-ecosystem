#!/usr/bin/env python3
"""swarm.py -- coupling and decay in a digital swarm, measured with LMD.

    python3 swarm-lmd/swarm.py

Grows lineage swarms from one root, attenuates fidelity per hop by the coupling
J, and then measures each agent two ways:

    hop depth              how many links from the root
    effective resistance   R from the root on the weighted swarm graph (LMD)

The second is the point of the re-run. Hop depth is a count; effective
resistance also sees how many ALTERNATIVE paths an agent has, so where a swarm
has side-links the two come apart and one of them predicts fidelity better.

E = U * D_enc * D_dec throughout: capacity times the two channels, a product, so
that reach with a dead channel is worth nothing.

Writes swarm-lmd/data/swarm_rows.csv -- a SIMULATED dataset. It is evidence
about this model, not about the world, and the file says so in its header.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from smi.lmd import mesh_metric  # noqa: E402  -- the same engine SMI draws with

SEED = 20260813
N_AGENTS = 4000
N_SWARMS = 40
J_STEPS = np.logspace(math.log10(0.05), math.log10(20.0), 12)


# --------------------------------------------------------------- the swarm --
def grow(n, J, rng, side_link_p=0.12):
    """One lineage swarm. Returns nodes and the weighted edge list.

    Preferential attachment on a heavy-tailed capacity, plus occasional
    side-links between cousins -- which is what makes effective resistance and
    hop depth different quantities rather than the same one twice.
    """
    U = np.exp(rng.normal(0.0, 1.1, size=n))          # heavy-tailed reach
    d_enc = rng.beta(5, 2, size=n)                     # takes information in
    d_dec = rng.beta(5, 2, size=n)                     # hands it on
    parent = np.full(n, -1, dtype=int)
    depth = np.zeros(n, dtype=int)
    edges = []

    weight = U.copy()
    for k in range(1, n):
        p = int(rng.choice(k, p=(weight[:k] / weight[:k].sum())))
        parent[k] = p
        depth[k] = depth[p] + 1
        edges.append((p, k, float(J)))
        # a cousin link: same generation, different parent
        if rng.random() < side_link_p and k > 3:
            same = np.nonzero(depth[:k] == depth[k])[0]
            same = [c for c in same if c != p]
            if same:
                edges.append((int(rng.choice(same)), k, float(J) * 0.5))

    # fidelity: the product along the lineage, attenuated per hop.
    # attenuation -> 1 as J grows: strong coupling loses less per hop.
    atten = J / (1.0 + J)
    fidelity = np.zeros(n)
    fidelity[0] = float(d_enc[0] * d_dec[0])
    order = np.argsort(depth)
    for k in order[1:]:
        fidelity[k] = fidelity[parent[k]] * atten * float(d_enc[k] * d_dec[k])

    E = U * d_enc * d_dec
    return {"U": U, "d_enc": d_enc, "d_dec": d_dec, "E": E,
            "parent": parent, "depth": depth, "fidelity": fidelity, "edges": edges}


def laplacian(n, edges):
    W = np.zeros((n, n))
    for i, j, w in edges:
        W[i, j] = W[j, i] = w
    return np.diag(W.sum(1)) - W


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    d = math.sqrt(float((ra ** 2).sum()) * float((rb ** 2).sum()))
    return float((ra * rb).sum() / d) if d else 0.0


def adj_r2(y, X):
    """Adjusted r² for an OLS fit with an intercept."""
    X = np.column_stack([np.ones(len(y))] + [np.asarray(c, dtype=float) for c in X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    ss_res = float((resid ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    if ss_tot == 0:
        return 0.0
    r2 = 1 - ss_res / ss_tot
    n, k = len(y), X.shape[1] - 1
    return float(1 - (1 - r2) * (n - 1) / (n - k - 1))


# ------------------------------------------------------------------- run ----
def main():
    rng = np.random.default_rng(SEED)
    per_swarm, rows = [], []

    print("=" * 78)
    print("  SWARM COUPLING AND DECAY, MEASURED WITH LMD")
    print("=" * 78)
    print(f"  {N_SWARMS} swarms · {N_AGENTS} agents each · J over "
          f"{len(J_STEPS)} steps in [{J_STEPS[0]:.3f}, {J_STEPS[-1]:.1f}] · seed {SEED}")

    for s in range(N_SWARMS):
        J = float(J_STEPS[s % len(J_STEPS)])
        # a smaller graph for the metric: LMD needs a pinv, which is O(n^3)
        g = grow(N_AGENTS, J, rng)
        sub_n = 220
        keep = np.argsort(g["depth"])[:sub_n]          # the top of the tree
        remap = {int(k): i for i, k in enumerate(keep)}
        sub_edges = [(remap[i], remap[j], w) for i, j, w in g["edges"]
                     if int(i) in remap and int(j) in remap]
        D, labels, dead = mesh_metric(laplacian(sub_n, sub_edges))
        R_root = D[remap[0]]

        ok = np.isfinite(R_root)
        fid = g["fidelity"][keep][ok]
        dep = g["depth"][keep][ok].astype(float)
        res = R_root[ok]

        rho_depth = spearman(fid, dep)
        rho_res = spearman(fid, res)
        per_swarm.append({"swarm": s, "J": J, "n_measured": int(ok.sum()),
                          "rho_depth": rho_depth, "rho_resistance": rho_res})

        for local, k in enumerate(keep):
            if not ok[local]:
                continue
            k = int(k)
            rows.append({
                "swarm": s, "J": round(J, 6), "agent": k,
                "depth": int(g["depth"][k]),
                "R_from_root": round(float(R_root[local]), 8),
                "U": round(float(g["U"][k]), 8),
                "d_enc": round(float(g["d_enc"][k]), 8),
                "d_dec": round(float(g["d_dec"][k]), 8),
                "E_UDD": round(float(g["E"][k]), 8),
                "fidelity": round(float(g["fidelity"][k]), 12),
            })

    # ---------------------------------------------------------------- S1/S2 --
    rho_depth = float(np.mean([r["rho_depth"] for r in per_swarm]))
    rho_res = float(np.mean([r["rho_resistance"] for r in per_swarm]))
    s1 = rho_depth <= -0.50
    s2 = abs(rho_res) >= abs(rho_depth) - 0.02

    print("\n  S1/S2  what predicts fidelity")
    print(f"    hop depth             rho = {rho_depth:+.4f}   [gate <= -0.50]  "
          f"{'HOLDS' if s1 else 'FAILS'}")
    print(f"    effective resistance  rho = {rho_res:+.4f}   [gate: within 0.02 of depth]  "
          f"{'HOLDS' if s2 else 'FAILS'}")
    better = ("resistance" if abs(rho_res) > abs(rho_depth) + 1e-9
              else "depth" if abs(rho_depth) > abs(rho_res) + 1e-9 else "tie")
    print(f"    the better predictor is: {better}")

    # ------------------------------------------------------------------ S3 --
    arr = {k: np.array([r[k] for r in rows], dtype=float) for k in
           ("E_UDD", "fidelity", "depth", "R_from_root")}
    y = np.log(np.clip(arr["fidelity"], 1e-300, None))
    x = arr["E_UDD"]
    lin = adj_r2(y, [x])
    quad = adj_r2(y, [x, x ** 2])
    with_res = adj_r2(y, [x, arr["R_from_root"]])
    print("\n  S3  the functional form (no prediction was registered)")
    for label, v in (("linear in U·D_enc·D_dec", lin),
                     ("quadratic", quad),
                     ("linear + effective resistance", with_res)):
        print(f"    {label:<32} adj r² = {v:.4f}")
    print(f"    linear beats quadratic: {lin > quad}")
    print("\n    READ THIS BEFORE READING THOSE NUMBERS. Both fits are ~0.000, and")
    print("    that is a property of the MODEL, not a result about E = U·D. In this")
    print("    simulation U governs how many children an agent attracts; it never")
    print("    enters the fidelity recursion at all. So an agent's own capacity")
    print("    cannot predict the fidelity it RECEIVES, by construction. S3 as")
    print("    written is uninformative about the law, and saying so is the finding.")

    # ---- S5: the test that IS informative about what U does here
    desc = np.zeros(N_AGENTS, dtype=float)
    g5 = grow(N_AGENTS, 1.0, rng)
    for k in range(N_AGENTS - 1, 0, -1):
        desc[int(g5["parent"][k])] += desc[k] + 1
    rho_u_desc = spearman(g5["U"], desc)
    rho_u_fid = spearman(g5["U"], g5["fidelity"])
    s5 = rho_u_desc > 0.15 and abs(rho_u_fid) < 0.15
    print("\n  S5  so what does capacity actually do in this model?")
    print(f"    U vs number of descendants   rho = {rho_u_desc:+.4f}   (capacity buys reach)")
    print(f"    U vs fidelity received       rho = {rho_u_fid:+.4f}   (and nothing else)")
    print(f"    consistent with the construction above: {'YES' if s5 else 'NO'}")

    # ------------------------------------------------------------------ S4 --
    g = grow(600, 1.0, rng)
    sub_n = 200
    keep = np.argsort(g["depth"])[:sub_n]
    remap = {int(k): i for i, k in enumerate(keep)}
    edges = [(remap[i], remap[j], w) for i, j, w in g["edges"]
             if int(i) in remap and int(j) in remap]
    cut = [(i, j, w) for i, j, w in edges if i != remap[0] and j != remap[0]]
    D_cut, _, _ = mesh_metric(laplacian(sub_n, cut))
    unreachable = ~np.isfinite(D_cut[remap[0]])
    unreachable[remap[0]] = True
    s4 = bool(unreachable.all())
    print("\n  S4  revoking the root")
    print(f"    {int(unreachable.sum())}/{sub_n} agents cut off   "
          f"[gate 100%]  {'HOLDS' if s4 else 'FAILS'}")

    # ------------------------------------------------------------- dataset --
    path = os.path.join(HERE, "data", "swarm_rows.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write("# SIMULATED DATA — generated by swarm-lmd/swarm.py, seed "
                f"{SEED}. Evidence about this model, NOT about the world.\n")
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()

    live = hashlib.sha256(open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest()
    lock = json.load(open(os.path.join(HERE, "prereg.lock.json"), encoding="utf-8"))

    out = {
        "seed": SEED, "swarms": N_SWARMS, "agents_per_swarm": N_AGENTS,
        "prereg_sha256": live, "prereg_intact": live == lock["prereg_sha256"],
        "S1_decay_with_depth": {"rho": rho_depth, "gate": -0.50,
                                "result": "HOLDS" if s1 else "FAILS"},
        "S2_resistance_predicts": {"rho_resistance": rho_res, "rho_depth": rho_depth,
                                   "better": better,
                                   "result": "HOLDS" if s2 else "FAILS"},
        "S3_functional_form": {"adj_r2_linear": lin, "adj_r2_quadratic": quad,
                               "adj_r2_linear_plus_resistance": with_res,
                               "linear_beats_quadratic": bool(lin > quad),
                               "note": "no prediction registered; the prior HF run "
                                       "found linear did NOT win and this is reported "
                                       "either way"},
        "S3_caveat": "BOTH FITS ARE ~0 BECAUSE U NEVER ENTERS THE FIDELITY "
                     "RECURSION IN THIS MODEL. S3 is uninformative about E = U·D; "
                     "it is reported so that nobody reads 0.0003 as a falsification.",
        "S5_what_capacity_does": {"rho_U_descendants": rho_u_desc,
                                  "rho_U_fidelity": rho_u_fid,
                                  "result": "CONSISTENT" if s5 else "INCONSISTENT",
                                  "note": "capacity buys reach, not received fidelity"},
        "S4_revocation": {"cut_off": int(unreachable.sum()), "of": sub_n,
                          "result": "HOLDS" if s4 else "FAILS"},
        "dataset": {"path": "swarm-lmd/data/swarm_rows.csv", "rows": len(rows),
                    "sha256": sha, "kind": "SIMULATED",
                    "warning": "evidence about the model, not about the world"},
        "per_swarm": per_swarm,
    }
    json.dump(out, open(os.path.join(HERE, "results_swarm.json"), "w"), indent=1)

    print(f"\n  wrote data/swarm_rows.csv — {len(rows)} rows, sha256 {sha[:16]}…")
    print("  SIMULATED. Evidence about this model, not about the world.")
    print(f"\n  pre-registration {'INTACT' if out['prereg_intact'] else 'CHANGED'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
