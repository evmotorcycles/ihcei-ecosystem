#!/usr/bin/env python3
"""
build_yeast_cohort.py
=====================
Reconstructs the LISM yeast cohort from raw public data using the AUTHOR'S
ORIGINAL, verified feature construction (recovered from the archived
gt18_p1_biological_final_results.csv and supplied by the author):

  network : STRING v12 physical links, taxon 4932, combined_score >= 400
  U       = node degree
  D_enc   = local clustering coefficient
  D_dec   = betweenness centrality (normalized), then min-max scaled
  D       = D_enc * D_dec
  E       = 1 if protein essential (S. cerevisiae DEG set), else 0

This supersedes an earlier proxy construction (mean incident-edge score /
mean neighbour degree); the features above are the ones behind the published
numbers. See PEER_REVIEW.md addendum 3 for the M5 audit these enable.

Essentiality labelling: STRING ids are systematic ORF names; the DEG essential
set is largely in standard gene names. Pass a name map with --aliases (STRING
protein.info/.aliases, a BioGRID-derived map from biogrid_name_map.py, or a
2-col name,orf CSV) to resolve them; or --use-archived-E to take verified labels
from an archived per-protein CSV.

USAGE
    python build_yeast_cohort.py \
        --string 4932.protein.physical.links.v12.0.csv \
        --essential scer_essential_genes_DEG.csv \
        --aliases yeast_name_orf_map.csv \
        --out yeast_interactome_DEG.csv
    # faster betweenness on large graphs: --betweenness-k 1500
"""
import argparse
import gzip
import re
import sys

import numpy as np
import pandas as pd

ORF_RE = re.compile(r"^Y[A-P][LR]\d{3}[WC](-[A-Z])?$", re.I)
Q_RE = re.compile(r"^Q\d{4}$")
STRING_THRESHOLD = 400


def is_systematic(name):
    return isinstance(name, str) and bool(ORF_RE.match(name) or Q_RE.match(name))


def load_graph(path, threshold):
    import networkx as nx
    e = pd.read_csv(path, sep=r"\s+", engine="python")
    e["p1"] = e["protein1"].str.replace(r"^\d+\.", "", regex=True)
    e["p2"] = e["protein2"].str.replace(r"^\d+\.", "", regex=True)
    score = next((c for c in e.columns if "score" in c.lower()), None)
    if score:
        e = e[e[score] >= threshold]
    G = nx.Graph()
    G.add_edges_from(zip(e["p1"], e["p2"]))
    G.remove_edges_from(nx.selfloop_edges(G))
    return G


def build_features(G, betweenness_k=None):
    import networkx as nx
    nodes = list(G.nodes())
    print(f"[topology] {len(nodes)} proteins, {G.number_of_edges()} interactions")
    clustering = nx.clustering(G)
    bc = (nx.betweenness_centrality(G, k=betweenness_k, normalized=True, seed=7)
          if betweenness_k else nx.betweenness_centrality(G, normalized=True))
    f = pd.DataFrame({
        "orf": nodes,
        "U": [G.degree(v) for v in nodes],
        "D_enc": [float(clustering[v]) for v in nodes],       # clustering coeff (in [0,1])
        "D_dec_raw": [float(bc[v]) for v in nodes],           # betweenness
    })

    def mm(x):
        x = x.astype(float)
        r = x.max() - x.min()
        return (x - x.min()) / r if r > 0 else x * 0.0
    f["D_dec"] = mm(f["D_dec_raw"])
    f["D"] = f["D_enc"] * f["D_dec"]
    return f


def load_aliases(path):
    opn = gzip.open if path.endswith(".gz") else open
    amap = {}
    with opn(path, "rt") as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            parts = [p.strip().strip('"') for p in re.split(r"[\t,]", line.rstrip("\n")) if p.strip()]
            syst = None
            for p in parts:
                cand = p.split(".", 1)[1] if re.match(r"^\d+\.", p) else p
                if is_systematic(cand):
                    syst = cand
                    break
            if not syst:
                continue
            for p in parts:
                cand = p.split(".", 1)[1] if re.match(r"^\d+\.", p) else p
                amap[cand.upper()] = syst
                amap[p.upper()] = syst
    return amap


def load_essential(path):
    df = pd.read_csv(path)
    names = set()
    for c in ("systematic_orf", "orf", "gene_name", "gene", "Gene"):
        if c in df.columns:
            names |= set(df[c].astype(str).str.strip()) - {"", "nan"}
    if not names:
        sys.exit(f"--essential needs an orf/gene column; got {list(df.columns)}")
    return names


def resolve_essential(names, amap):
    out, unresolved = set(), []
    for n in names:
        if not isinstance(n, str) or not n.strip() or n.lower() == "nan":
            continue
        if is_systematic(n):
            out.add(n.upper())
        elif amap and n.upper() in amap:
            out.add(amap[n.upper()].upper())
        else:
            unresolved.append(n)
    return out, unresolved


def vif(a, b):
    r = np.corrcoef(a, b)[0, 1]
    return 1.0 / (1.0 - r ** 2), r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--string", required=True)
    ap.add_argument("--essential", default=None)
    ap.add_argument("--aliases", default=None)
    ap.add_argument("--use-archived-E", default=None,
                    help="archived per-protein CSV (protein_id,E_essential) with verified labels")
    ap.add_argument("--betweenness-k", type=int, default=None)
    ap.add_argument("--threshold", type=int, default=STRING_THRESHOLD)
    ap.add_argument("--out", default="yeast_interactome_DEG.csv")
    a = ap.parse_args()

    G = load_graph(a.string, a.threshold)
    f = build_features(G, a.betweenness_k)

    v, r = vif(f["D_enc"], f["D_dec"])
    print(f"[channel]  VIF(D_enc,D_dec) = {v:.3f} (r={r:+.3f})  -> "
          f"{'PASS (channel intact)' if v < 5 else 'COLLAPSE'}")

    if a.use_archived_E:
        ae = pd.read_csv(a.use_archived_E)
        lab = dict(zip(ae["protein_id"].astype(str).str.upper(), ae["E_essential"].astype(int)))
        f["E_essential"] = f["orf"].str.upper().map(lab).fillna(0).astype(int)
        print(f"[outcome]  essential = {int(f.E_essential.sum())} / {len(f)} (archived labels)")
    elif a.essential:
        raw = load_essential(a.essential)
        amap = load_aliases(a.aliases) if a.aliases else {}
        ess, unresolved = resolve_essential(raw, amap)
        f["E_essential"] = f["orf"].str.upper().isin(ess).astype(int)
        print(f"[outcome]  essential = {int(f.E_essential.sum())} / {len(f)} "
              f"({len(ess & {o.upper() for o in f.orf})}/{len(ess)} essential ORFs in graph)")
        if unresolved:
            print(f"[outcome]  {len(unresolved)} names unresolved (need --aliases); "
                  f"e.g. {unresolved[:6]}")
    else:
        f["E_essential"] = ""
        print("[outcome]  no --essential/--use-archived-E: E left blank.")

    cols = ["orf", "E_essential", "U", "D_enc", "D_dec", "D", "D_dec_raw"]
    f[cols].to_csv(a.out, index=False)
    print(f"[write]    {a.out} ({len(f)} rows)")


if __name__ == "__main__":
    main()
