#!/usr/bin/env python3
"""
label_essential_from_deg.py
===========================
Bridges the DEG essential-gene sequences to yeast systematic ORF names, so the
yeast outcome column E in the LISM cohort can be regenerated from raw public
data end-to-end (closing the last gap in referee points M1/M4/M5).

WHY THIS EXISTS
The DEG FASTA files ship essential-gene *sequences* under opaque DEG IDs
(e.g. >DEG20010001) with no organism/gene annotation. For S. cerevisiae the
essential set is the DEG2001 block of DEG20.nt (1,110 CDS). To label a STRING
protein (keyed by systematic ORF name, e.g. YGR222W) as essential, we match
each DEG2001 coding sequence to a yeast ORF-CDS reference and read off the ORF
name. Same genome -> exact nucleotide matches; we add a trimmed/stop-codon and
a fixed-length signature fallback for annotation-version drift.

INPUTS
  --deg        DEG20.nt(.gz) OR the pre-extracted DEG2001 subset FASTA
  --deg-block  DEG-ID prefix selecting the organism (default DEG2001 = yeast)
  --orf-cds    yeast ORF coding-sequence FASTA keyed by systematic name, e.g.
               SGD  orf_coding_all_R64-*.fasta   (header first token = ORF), or
               Ensembl Fungi  Saccharomyces_cerevisiae.R64-1-1.cds.all.fa(.gz)
               (header has  gene:YAL001C  or the ORF as the id).
OUTPUT
  --out        scer_essential_orfs.txt  (one systematic ORF name per line)
               -> feed to  build_yeast_cohort.py --essential

The matched ORF list is exactly the wet-lab essentiality label the manuscript
uses; nothing here defines essentiality from topology (which would be circular).
"""
import argparse
import gzip
import re
import sys


def op(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def read_fasta(path):
    hdr, seq = None, []
    with op(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if hdr is not None:
                    yield hdr, "".join(seq)
                hdr, seq = line[1:], []
            else:
                seq.append(line.strip())
    if hdr is not None:
        yield hdr, "".join(seq)


ORF_RE = re.compile(r"\b(Y[A-P][LR]\d{3}[WC](?:-[A-Z])?)\b")
Q_RE = re.compile(r"\b(Q\d{4})\b")  # mitochondrial ORFs (Q0045 etc.)


def orf_from_header(hdr):
    """Extract a systematic ORF name from an SGD/Ensembl-style header."""
    tok = hdr.split()[0]
    if ORF_RE.fullmatch(tok) or Q_RE.fullmatch(tok):
        return tok
    m = ORF_RE.search(hdr) or Q_RE.search(hdr)
    return m.group(1) if m else None


def norm(seq):
    return re.sub(r"[^ACGT]", "", seq.upper())


def sig(seq, k=300):
    s = norm(seq)
    return s[:k] if len(s) >= k else None


def build_reference(orf_cds_path):
    exact, signature = {}, {}
    n, named = 0, 0
    for hdr, seq in read_fasta(orf_cds_path):
        n += 1
        orf = orf_from_header(hdr)
        if not orf:
            continue
        named += 1
        s = norm(seq)
        exact.setdefault(s, orf)
        exact.setdefault(s.rstrip("N"), orf)
        # also index without a trailing stop codon
        if len(s) >= 3 and s[-3:] in ("TAA", "TAG", "TGA"):
            exact.setdefault(s[:-3], orf)
        g = sig(seq)
        if g:
            signature.setdefault(g, orf)
    if named == 0:
        sys.exit(f"ERROR: no ORF names parsed from {orf_cds_path} headers. "
                 f"Expected systematic names like YAL001C in the FASTA headers.")
    print(f"[ref] {orf_cds_path}: {n} records, {named} with ORF names, "
          f"{len(exact)} sequence keys, {len(signature)} signatures", file=sys.stderr)
    return exact, signature


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deg", required=True, help="DEG20.nt(.gz) or DEG2001 subset FASTA")
    ap.add_argument("--deg-block", default="DEG2001", help="organism DEG-ID prefix")
    ap.add_argument("--orf-cds", required=True, help="yeast ORF CDS FASTA (ORF-keyed)")
    ap.add_argument("--out", default="scer_essential_orfs.txt")
    a = ap.parse_args()

    exact, signature = build_reference(a.orf_cds)

    hits, miss, total = set(), 0, 0
    for hdr, seq in read_fasta(a.deg):
        if not hdr.startswith(a.deg_block):
            continue
        total += 1
        s = norm(seq)
        orf = (exact.get(s) or exact.get(s.rstrip("N"))
               or (exact.get(s[:-3]) if len(s) >= 3 else None))
        if not orf:
            g = sig(seq)
            orf = signature.get(g) if g else None
        if orf:
            hits.add(orf)
        else:
            miss += 1

    with open(a.out, "w") as w:
        for orf in sorted(hits):
            w.write(orf + "\n")

    rate = 100.0 * (total - miss) / total if total else 0.0
    print(f"[match] DEG block {a.deg_block}: {total} essential CDS -> "
          f"{len(hits)} unique ORFs matched ({rate:.1f}% of CDS); {miss} unmatched",
          file=sys.stderr)
    print(f"[write] {a.out} ({len(hits)} essential ORFs)", file=sys.stderr)
    if rate < 80:
        print("[warn] low match rate: check that --orf-cds is the S. cerevisiae "
              "ORF coding-sequence set (R64) and same nucleotide alphabet.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
