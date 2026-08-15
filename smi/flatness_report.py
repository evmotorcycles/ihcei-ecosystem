#!/usr/bin/env python3
"""flatness_report.py -- what the flat picture had to throw away, written down.

    python3 smi/flatness_report.py     -> smi/results_flatness.json

Separate from run_smi.py and from results_smi.json ON PURPOSE. That file backs a
hash-locked pre-registration and is not edited after the fact; this is a later
measurement and it gets its own file.

The number here matters beyond SMI. A system that can state what it cannot show
is the closest software gets to disclosing its own blind spot -- and the limit of
that is stated here too: it can only declare the blind spots it can compute.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from smi.lmd import (best_axes, flatness, laplacian_from_edges,  # noqa: E402
                     layout2d, mesh_metric)

IDS = ["qty", "unit", "net", "vat", "total"]
NAMES = {"qty": "Quantity", "unit": "Unit price", "net": "Net",
         "vat": "VAT 20%", "total": "Total"}
EDGES = [("qty", "net", 4.0), ("unit", "net", 4.0),
         ("net", "vat", 8.0), ("net", "total", 8.0)]


def main():
    L = laplacian_from_edges(
        len(IDS), [(IDS.index(a), IDS.index(b), w) for a, b, w in EDGES])
    D, _, _ = mesh_metric(L)
    keep = list(range(len(IDS)))

    xy = layout2d(D, keep)
    ratio, a, b = flatness(D, keep, xy)
    axes, alt = best_axes(D, keep)
    finite = D[np.isfinite(D)]

    out = {
        "mesh": "the invoice mesh shipped in smi/app.html",
        "default_plane": {
            "axes": [0, 1],
            "worst_pair": [NAMES[IDS[a]], NAMES[IDS[b]]],
            "drawn_at_fraction_of_true": float(ratio),
            "their_true_distance": float(D[a][b]),
            "mesh_diameter": float(finite.max()),
            "share_of_diameter_hidden": float(D[a][b] / finite.max()),
        },
        "alternative_plane": {"axes": list(axes), "worst_pair_there": float(alt)},
        "the_limit": (
            "This declares the blind spots it can COMPUTE. A projection loss is "
            "computable because both the true distance and the drawn distance "
            "exist. An omission from a record is not: a ledger cannot contain "
            "its own omissions, which is why keel/run.plumb halts rather than "
            "reporting completeness."),
    }
    path = os.path.join(HERE, "results_flatness.json")
    json.dump(out, open(path, "w", encoding="utf-8"), indent=2)
    d = out["default_plane"]
    print(f"  {d['worst_pair'][0]} / {d['worst_pair'][1]} drawn at "
          f"{d['drawn_at_fraction_of_true']:.2e} of a true {d['their_true_distance']:.4f}")
    print(f"  that gap is {d['share_of_diameter_hidden']:.1%} of the mesh's whole diameter")
    print(f"  another plane keeps every pair at {out['alternative_plane']['worst_pair_there']:.1%}")
    print("  wrote smi/results_flatness.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
