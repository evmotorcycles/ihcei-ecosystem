#!/usr/bin/env python3
"""
build_yeast_cohort.py
=====================
Reconstructs the LISM yeast (S. cerevisiae) cohort from RAW public inputs, in
an auditable way that directly answers referee point M4 ("ship the yeast
D_enc/D_dec construction; the VIF ~= 1.0 claim is load-bearing").

INPUTS (raw, public)
  --string  4932.protein.physical.links.v12.0.csv   STRING v12 physical links
                                                     (protein1 protein2 combined_score)
  --essential  <file>   essentiality labels keyed by systematic ORF name
                        (one ORF per line, or a CSV with an 'orf'/'gene' column).
                        Source: DEG / SGD deletion-project essential set.
                        REQUIRED for the outcome column E; the topology and the
                        two-hop features are built without it.

TWO-HOP CONSTRUCTION (mirrors the manuscript's encode/decode split)
  U      capacity           = log(1 + degree)                 (own connectivity)
  D_enc  encoding fidelity  = scaled mean confidence of the node's OWN incident
                              edges  -> the quality of the node's own signal.
  D_dec  decoding fidelity  = scaled mean DEGREE of the node's neighbours
                              -> a two-hop property measured on OTHERS, using
                              their topology rather than the node's own edge
                              weights, so it is structurally independent of
                              D_enc (that independence is exactly what keeps the
                              two-hop channel intact, i.e. low VIF).
  D      composite          = D_enc * D_dec           (then min-max in analysis)
  E      outcome            = 1 if ORF in essential set else 0   (wet-lab label)

The confidence-cut for "an interaction exists" is STRING medium confidence
(combined_score >= 400), the field-standard threshold; at that cut the yeast
physical graph has ~4.8k proteins, matching the manuscript's N.

Prints VIF(D_enc, D_dec) on the REAL data (no labels needed) so the
channel-intact claim can be checked immediately, and writes
yeast_interactome_DEG.csv with columns reproduce_analysis.py expects.
"""
import argparse
import sys
from collections import defaultdict

import numpy as np
import pandas as pd


def load_edges(path, min_score):
    df = pd.read_csv(path, sep=r"\s+")
    need = {"protein1", "protein2", "combined_score"}
    if not need.issubset(df.columns):
        sys.exit(f"STRING file must have columns {need}; got {list(df.columns)}")
    df = df[df.combined_score >= min_score].copy()
    # strip the '4932.' taxon prefix -> systematic ORF name
    for c in ("protein1", "protein2"):
        df[c] = df[c].str.replace(r"^\d+\.", "", regex=True)
    return df


def build_features(edges):
    """Undirected: aggregate incident-edge stats and neighbour sets per node."""
    deg = defaultdict(int)
    inc_score_sum = defaultdict(float)
    neigh = defaultdict(set)
    for p1, p2, s in edges[["protein1", "protein2", "combined_score"]].itertuples(index=False):
        if p1 == p2:
            continue
        deg[p1] += 1; deg[p2] += 1
        inc_score_sum[p1] += s; inc_score_sum[p2] += s
        neigh[p1].add(p2); neigh[p2].add(p1)

    nodes = list(deg.keys())
    rows = []
    for n in nodes:
        d = deg[n]
        mean_inc = inc_score_sum[n] / d if d else 0.0            # own signal fidelity
        nb = neigh[n]
        mean_nb_deg = np.mean([deg[m] for m in nb]) if nb else 0.0  # two-hop reach
        rows.append((n, d, mean_inc, mean_nb_deg))
    f = pd.DataFrame(rows, columns=["orf", "degree", "mean_inc_score", "mean_neigh_degree"])

    def scale(x):
        x = x.astype(float)
        rng = x.max() - x.min()
        return (x - x.min()) / rng if rng > 0 else x * 0.0

    f["U"] = np.log1p(f["degree"])
    f["D_enc"] = scale(f["mean_inc_score"])
    f["D_dec"] = scale(f["mean_neigh_degree"])
    f["D"] = f["D_enc"] * f["D_dec"]
    return f


def load_essential(path):
    """Accept a plain ORF-per-line list or a CSV with an orf/gene column."""
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
        # prefer a systematic-ORF column if populated; else fall back to gene name
        for c in ("systematic_orf", "orf", "systematic_name", "ORF"):
            if c in df.columns and df[c].astype(str).str.strip().ne("").any():
                names = set(df[c].astype(str).str.strip()) - {""}
                # merge in gene-name column too so aliases can resolve the rest
                for gc in ("gene_name", "gene", "Gene"):
                    if gc in df.columns:
                        names |= set(df[gc].astype(str).str.strip()) - {""}
                return names
        for c in ("gene_name", "gene", "Gene"):
            if c in df.columns:
                return set(df[c].astype(str).str.strip()) - {""}
        sys.exit(f"--essential CSV needs an orf/gene column; got {list(df.columns)}")
    with open(path) as fh:
        return {ln.strip().split()[0] for ln in fh if ln.strip() and not ln.startswith("#")}


import gzip
import re

ORF_RE = re.compile(r"^Y[A-P][LR]\d{3}[WC](-[A-Z])?$", re.I)
Q_RE = re.compile(r"^Q\d{4}$")


def is_systematic(name):
    if not isinstance(name, str):
        return False
    return bool(ORF_RE.match(name) or Q_RE.match(name))


def load_aliases(path):
    """Map any yeast gene alias / preferred name -> systematic ORF name.

    Auto-handles STRING `4932.protein.info.v12.0.txt` (cols: string_protein_id,
    preferred_name, ...), STRING `4932.protein.aliases.v12.0.txt`
    (string_protein_id, alias, source), or a plain 2-column CSV/TSV of
    (name, orf). The systematic ORF is taken from a `4932.<ORF>` id when
    present, else from whichever field looks systematic.
    """
    opn = gzip.open if path.endswith(".gz") else open
    amap = {}
    with opn(path, "rt") as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            parts = re.split(r"[\t,]", line.rstrip("\n"))
            parts = [p.strip().strip('"') for p in parts if p.strip()]
            if not parts:
                continue
            # find the systematic ORF: from a taxon-prefixed id, or any systematic field
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


def resolve_essential(names, amap):
    """Translate a set of essential gene names to systematic ORF names, using
    the alias map for any non-systematic (standard) names."""
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
    ap.add_argument("--essential", default=None,
                    help="essential-gene list/CSV (E column). ORF names or standard "
                         "gene names (with --aliases). If omitted, features + VIF are "
                         "still computed and E is left blank.")
    ap.add_argument("--aliases", default=None,
                    help="name->ORF map to resolve standard gene names: STRING "
                         "4932.protein.info / .aliases file, or a 2-col name,orf CSV.")
    ap.add_argument("--min-score", type=int, default=400,
                    help="STRING combined_score cut (default 400 = medium conf.)")
    ap.add_argument("--out", default="yeast_interactome_DEG.csv")
    a = ap.parse_args()

    edges = load_edges(a.string, a.min_score)
    f = build_features(edges)
    print(f"[topology] score>={a.min_score}: {len(edges)} edges, {len(f)} proteins")

    v, r = vif(f["D_enc"], f["D_dec"])
    gate = "PASS (channel intact)" if v < 5 else "COLLAPSE"
    print(f"[channel]  VIF(D_enc,D_dec) = {v:.3f}  (r={r:+.3f})  -> {gate}")

    if a.essential:
        raw = load_essential(a.essential)
        amap = load_aliases(a.aliases) if a.aliases else {}
        if a.aliases:
            print(f"[aliases]  {len(amap)} name->ORF entries from {a.aliases}")
        ess, unresolved = resolve_essential(raw, amap)
        graph_orfs = {o.upper() for o in f["orf"]}
        f["E_essential"] = f["orf"].str.upper().isin(ess).astype(int)
        n_ess = int(f["E_essential"].sum())
        print(f"[outcome]  essential = {n_ess} / {len(f)} "
              f"({100*n_ess/len(f):.1f}%);  {len(ess & graph_orfs)}/{len(ess)} "
              f"essential ORFs matched into the graph")
        if unresolved:
            print(f"[outcome]  {len(unresolved)} essential names unresolved to an ORF "
                  f"(need --aliases); e.g. {unresolved[:6]}")
    else:
        f["E_essential"] = ""
        print("[outcome]  no --essential provided: E column left blank. "
              "Provide an ORF-keyed essential-gene list to populate it.")

    cols = ["orf", "E_essential", "U", "D_enc", "D_dec", "D",
            "degree", "mean_inc_score", "mean_neigh_degree"]
    f[cols].to_csv(a.out, index=False)
    print(f"[write]    {a.out}  ({len(f)} rows)")


if __name__ == "__main__":
    main()
