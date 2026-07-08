#!/usr/bin/env python3
"""
extract_deg_essential.py
========================
Extracts the S. cerevisiae essential-gene set from the DEG eukaryote annotation
(`deg_annotation_e.csv`), the raw public source the manuscript cites (Giaever
et al. 2002, DEG organism block DEG2001). Produces a per-gene table that
`build_yeast_cohort.py --essential` consumes.

DEG2001 is *Saccharomyces cerevisiae* (confirmed by `deg_eukaryotes.csv`:
"Saccharomyces cerevisiae … Giaever G, et al (2002) … 1110 … DEG2001"). The
annotation lists each essential gene by *standard* name (TFC3, EFB1, …); only a
handful are already systematic ORF names (YAL001C-style). To join against STRING
(which is keyed by systematic ORF name) the standard names are resolved via an
alias map in build_yeast_cohort.py (STRING protein.info / aliases).

Output columns: deg_id, gene_name, systematic_orf (if directly present), gi.
"""
import argparse
import csv
import re

ORF = re.compile(r"^Y[A-P][LR]\d{3}[WC](-[A-Z])?$", re.I)
Q = re.compile(r"^Q\d{4}$")
ORF_ANY = re.compile(r"\bY[A-P][LR]\d{3}[WC]\b")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--annotation", required=True, help="deg_annotation_e.csv (';'-delimited)")
    ap.add_argument("--block", default="DEG2001", help="organism DEG block (default yeast)")
    ap.add_argument("--out", default="scer_essential_genes_DEG.csv")
    a = ap.parse_args()

    rows = []
    with open(a.annotation, newline="") as fh:
        for r in csv.reader(fh, delimiter=";"):
            if not r or r[0].strip('"') != a.block:
                continue
            deg_id = r[1].strip() if len(r) > 1 else ""
            name = r[2].strip() if len(r) > 2 else ""
            gi = r[3].strip() if len(r) > 3 else ""
            syst = name if (ORF.match(name) or Q.match(name)) else ""
            if not syst:
                m = ORF_ANY.search(" ".join(r))
                if m:
                    syst = m.group(0)
            rows.append((deg_id, name, syst, gi))

    with open(a.out, "w", newline="") as w:
        wr = csv.writer(w)
        wr.writerow(["deg_id", "gene_name", "systematic_orf", "gi"])
        wr.writerows(rows)

    resolved = sum(1 for _, _, s, _ in rows if s)
    print(f"[{a.block}] {len(rows)} essential genes -> {a.out} "
          f"({resolved} already systematic; the rest resolve via --aliases)")


if __name__ == "__main__":
    main()
