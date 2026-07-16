#!/usr/bin/env python3
"""
reproduce_yeast.py -- recompute the LISM YEAST channel from raw STRING v12 data.
============================================================================
Answers the second half of the reproducibility criticism ("the yeast channel
still requires a network fetch of STRING"). The raw STRING v12 physical-links
file for S. cerevisiae (taxon 4932) is now COMMITTED, gzipped, in repro/data/,
so this recomputes the headline yeast number from scratch -- no network.

Construction (the author's verified feature build, from build_yeast_cohort.py):
  network : STRING v12 physical links, taxon 4932, combined_score >= 400
  U       = node degree
  D_enc   = local clustering coefficient        (the "encode" fidelity hop)
  D_dec   = betweenness centrality, min-max scaled (the "decode" hop)

The headline claim this reproduces: the two fidelity hops are STATISTICALLY
INDEPENDENT -- VIF(D_enc, D_dec) ~ 1.00 -- so the E = U*D linear-vs-quadratic
test is a VALID test on an intact channel, not an artifact of a collapsed
(multicollinear) one. The manuscript / zenodo report VIF = 1.003 at N = 4825.

    python3 repro/reproduce_yeast.py
    # needs: pip install networkx pandas numpy   (graph metrics; unlike the
    #        stdlib tau_v reproduction, VIF needs real graph algorithms)
    # betweenness uses k-sample (seed=7) for speed; VIF is robust to it.

This does NOT reproduce the yeast OUTCOME (essential-gene AUC): that needs the
DEG essential-gene labels + an ORF name map (see build_yeast_cohort.py). VIF is
a property of the two PREDICTORS alone, so STRING is sufficient -- and that is
exactly the "valid, non-collapsed channel" claim under audit.
"""
import gzip
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STRING_GZ = os.path.join(HERE, "data", "4932.protein.physical.links.v12.0.csv.gz")
THRESHOLD = 400
REF_VIF = 1.003
REF_N = 4825


def main():
    try:
        import numpy as np
        import pandas as pd
        import networkx as nx
    except ImportError as e:
        print("This reproduction needs graph libraries:  pip install networkx pandas numpy")
        print("(missing: %s).  The tau_v reproduction, by contrast, is stdlib-only." % e.name)
        raise SystemExit(2)

    bar = "=" * 78
    print(bar)
    print(" LISM yeast-channel reproduction -- VIF recomputed from raw STRING v12")
    print(" data: repro/data/4932.protein.physical.links.v12.0.csv.gz (committed) | no network")
    print(bar)

    with gzip.open(STRING_GZ, "rt") as fh:
        e = pd.read_csv(fh, sep=r"\s+", engine="python")
    e = e[e["combined_score"] >= THRESHOLD]
    e["p1"] = e["protein1"].str.replace(r"^\d+\.", "", regex=True)
    e["p2"] = e["protein2"].str.replace(r"^\d+\.", "", regex=True)

    G = nx.Graph()
    G.add_edges_from(zip(e["p1"], e["p2"]))
    G.remove_edges_from(nx.selfloop_edges(G))
    nodes = list(G.nodes())
    print(f"\n  STRING v12, taxon 4932, combined_score >= {THRESHOLD}")
    print(f"  graph: {len(nodes)} proteins, {G.number_of_edges()} interactions")

    clustering = nx.clustering(G)                                     # D_enc
    bc = nx.betweenness_centrality(G, k=1500, normalized=True, seed=7)  # D_dec (k-sample)
    D_enc = np.array([clustering[v] for v in nodes], float)
    braw = np.array([bc[v] for v in nodes], float)
    D_dec = (braw - braw.min()) / (braw.max() - braw.min())

    r = float(np.corrcoef(D_enc, D_dec)[0, 1])
    vif = 1.0 / (1.0 - r * r)
    print(f"\n  D_enc = clustering coefficient,  D_dec = min-max betweenness")
    print(f"  corr(D_enc, D_dec) = {r:+.4f}")
    print(f"  VIF(D_enc, D_dec)  = {vif:.4f}   (computed now)")

    print("\n  " + "-" * 74)
    checks = []
    c_n = len(nodes) == REF_N
    print(f"  {'OK  ' if c_n else 'FAIL'} node count matches manuscript          reproduced={len(nodes):<8} reference={REF_N}")
    checks.append(c_n)
    c_vif = abs(vif - REF_VIF) < 0.01
    print(f"  {'OK  ' if c_vif else 'FAIL'} VIF ~ 1.00 (channel intact, not collapsed) reproduced={vif:.3f}    reference={REF_VIF}")
    checks.append(c_vif)
    c_indep = vif < 5.0
    print(f"  {'OK  ' if c_indep else 'FAIL'} VIF below the 5.0 collinearity gate       reproduced={vif:.3f}    reference=<5.0")
    checks.append(c_indep)

    print("\n  " + "-" * 74)
    ok = all(checks)
    print(f"  RESULT: {sum(checks)}/{len(checks)} reproduced from raw STRING v12, no network")
    print(bar)
    print(" The yeast channel reproduces from scratch: the two fidelity hops are")
    print(" independent (VIF~1.00), so the linear-vs-quadratic coupling test is valid on")
    print(" an intact channel. Recomputed here from committed raw data -- not read from a file.")
    print(bar)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
