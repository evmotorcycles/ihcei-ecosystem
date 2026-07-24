#!/usr/bin/env python3
"""
build_yeast_features.py -- freeze the per-node channel features of the REAL yeast
interactome so the biomedical runner can stay stdlib-only and fast.
============================================================================
Reads the committed raw STRING v12 physical-links file for S. cerevisiae
(taxon 4932) and computes, for every protein node, the exact three-hop channel
features used throughout LISM -- identical construction to repro/reproduce_yeast.py:

  U      = node degree                                (capacity)
  D_enc  = local clustering coefficient               (encode-fidelity hop)
  D_dec  = min-max-scaled betweenness centrality       (decode-fidelity hop, k-sample seed=7)

Writes data/yeast_channel_frozen.json (the frozen feature table + provenance +
the SHA-256 of the raw STRING source). This is a DERIVED fixture: a faithful
reproduction recomputes it from the committed raw data.

    python3 biomedical-agency/build_yeast_features.py     # needs networkx, pandas, numpy
"""
import gzip
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STRING_GZ = os.path.join(ROOT, "repro", "data", "4932.protein.physical.links.v12.0.csv.gz")
OUT = os.path.join(HERE, "data", "yeast_channel_frozen.json")
THRESHOLD = 400


def main():
    import numpy as np
    import pandas as pd
    import networkx as nx

    with gzip.open(STRING_GZ, "rt") as fh:
        e = pd.read_csv(fh, sep=r"\s+", engine="python")
    e = e[e["combined_score"] >= THRESHOLD]
    e["p1"] = e["protein1"].str.replace(r"^\d+\.", "", regex=True)
    e["p2"] = e["protein2"].str.replace(r"^\d+\.", "", regex=True)

    G = nx.Graph()
    G.add_edges_from(zip(e["p1"], e["p2"]))
    G.remove_edges_from(nx.selfloop_edges(G))
    nodes = list(G.nodes())

    clustering = nx.clustering(G)                                        # D_enc
    bc = nx.betweenness_centrality(G, k=1500, normalized=True, seed=7)   # D_dec (k-sample)
    deg = dict(G.degree())
    braw = np.array([bc[v] for v in nodes], float)
    bmin, bspan = braw.min(), (braw.max() - braw.min())

    feats = []
    for v in nodes:
        d_dec = float((bc[v] - bmin) / bspan)
        feats.append({"U": int(deg[v]), "D_enc": round(float(clustering[v]), 6), "D_dec": round(d_dec, 6)})

    src_hash = hashlib.sha256(open(STRING_GZ, "rb").read()).hexdigest()
    out = {"_provenance": {
        "source": "STRING v12 physical links, S. cerevisiae taxon 4932, combined_score >= %d" % THRESHOLD,
        "raw_file": "repro/data/4932.protein.physical.links.v12.0.csv.gz",
        "raw_sha256": src_hash,
        "n_nodes": len(nodes), "n_edges": G.number_of_edges(),
        "features": "U=degree, D_enc=clustering coefficient, D_dec=min-max betweenness (k=1500, seed=7)",
        "note": "DERIVED from real committed STRING data via build_yeast_features.py; identical construction to repro/reproduce_yeast.py. Frozen so the biomedical runner is stdlib-only."},
        "nodes": feats}
    json.dump(out, open(OUT, "w"))
    print("wrote %s : %d nodes, %d edges, raw sha256 %s" % (OUT, len(nodes), G.number_of_edges(), src_hash[:16]))


if __name__ == "__main__":
    main()
