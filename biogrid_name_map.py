#!/usr/bin/env python3
"""
biogrid_name_map.py
==================
Builds a yeast standard-gene-name -> systematic-ORF-name map from a BioGRID
organism tab file (e.g. BIOGRID-ORGANISM-Saccharomyces_cerevisiae-*.tab.txt).

BioGRID rows pair, on each side, a systematic ORF id (INTERACTOR_A, e.g.
YFL039C) with its OFFICIAL_SYMBOL (ACT1) and pipe-separated ALIASES
(ABY1|END7). Emitting (symbol -> ORF) and (alias -> ORF) for both sides yields
the standard->systematic map `build_yeast_cohort.py --aliases` needs to resolve
DEG's standard essential-gene names onto STRING's systematic ORF ids.

Output: a 2-column CSV `name,orf` (systematic names also mapped to themselves).
"""
import argparse
import csv
import re

ORF = re.compile(r"^Y[A-P][LR]\d{3}[WC](-[A-Z])?$", re.I)
Q = re.compile(r"^Q\d{4}$")


def is_syst(x):
    return bool(ORF.match(x) or Q.match(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--biogrid", required=True, help="BioGRID yeast .tab.txt")
    ap.add_argument("--out", default="yeast_name_orf_map.csv")
    a = ap.parse_args()

    amap = {}

    def add(name, orf):
        name = (name or "").strip()
        if name and name.upper() != "N/A" and is_syst(orf):
            amap.setdefault(name.upper(), orf)

    with open(a.biogrid, encoding="latin-1") as fh:
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 6 or cols[0] == "INTERACTOR_A":
                continue
            orf_a, orf_b, sym_a, sym_b, ali_a, ali_b = cols[:6]
            for orf, sym, ali in ((orf_a, sym_a, ali_a), (orf_b, sym_b, ali_b)):
                if not is_syst(orf):
                    continue
                add(orf, orf)          # systematic -> itself
                add(sym, orf)          # official symbol -> ORF
                for al in ali.split("|"):
                    add(al, orf)        # each alias -> ORF

    with open(a.out, "w", newline="") as w:
        wr = csv.writer(w)
        wr.writerow(["name", "orf"])
        for name, orf in sorted(amap.items()):
            wr.writerow([name, orf])
    print(f"[biogrid] {a.out}: {len(amap)} name->ORF entries")


if __name__ == "__main__":
    main()
