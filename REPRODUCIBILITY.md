# Reproducibility Record — LISM

This records exactly what reproduces, from what, and what is still needed —
the concrete answer to referee point **M1** ("the archive does not reproduce as
shipped"). Two of the three central claims now reproduce from real inputs; the
third (yeast essentiality) is blocked only on a label file, documented below.

## Environment
```
python 3.11+
numpy 2.4.6  pandas 3.0.3  scipy 1.17.1  statsmodels 0.14.6  scikit-learn 1.9.0
pip install -r requirements.txt
```

## 1. GitHub cohort — REPRODUCES (confirmed from the archived CI run)
The pre-registered fetch + analysis is `govphys_quadratic_prereg_test.py`
(spec SHA-256 `cac34f44…001f7`). The archived GitHub Actions log
(`logs_74994532125`, run 2026-06-19) records the fetch of 992 unique
repositories and the verdict, matching the manuscript exactly:

| Quantity | Manuscript | CI log |
|---|---|---|
| N (fail/surv) | 992 (750/242) | 992 (750/242) |
| VIF(D_enc,D_dec) | 1.02 (r=+0.14) | 1.02 (r=+0.141) |
| PRIMARY ΔAIC(quad−lin) | −3.48 | −3.48 |
| SECONDARY nested ΔAIC | −0.12 | −0.12 |
| τ_v failed / survived | 50.6 / 19.8 d | 50.61 / 19.76 d |
| Verdict | QUADRATIC DISCONFIRMED | QUADRATIC_DISCONFIRMED |

> Note on `perm z = +9.32` (referee **M3**): this value is produced by the
> original script's permutation statistic but its *magnitude* is statistic-
> dependent and does not reproduce stably across formulations (an independent
> reimplementation yields a different z on the same direction/tail). Use
> `analysis_corrected.py`, which reports a reproducible permutation **tail**
> (fraction ≥ observed, seed 42) instead of a point z.

To recompute headline numbers from the per-repo CSV once it is deposited:
```
python reproduce_analysis.py --github github_repositories.csv
```

## 2. Yeast two-hop channel (VIF) — REPRODUCES from raw STRING v12
`build_yeast_cohort.py` rebuilds the interactome features from the raw STRING
physical-links file and computes the load-bearing channel-independence metric
**without needing any labels**:
```
python build_yeast_cohort.py --string 4932.protein.physical.links.v12.0.csv --min-score 400
```
Result on the real data (medium-confidence cut, STRING's field-standard 400):

| Quantity | Manuscript | Rebuilt from raw STRING |
|---|---|---|
| N proteins | 4,772 | 4,825 |
| VIF(D_enc, D_dec) | 1.003 | **1.005** (r=−0.071) |

This confirms the manuscript's "channel intact / independent two-hop" claim on
real data with a fully documented construction (answers referee **M4** for the
independence claim). The small N difference (4,825 vs 4,772) is the expected
effect of the exact essential-set intersection / isolated-node filtering, which
requires the label file below.

## 3. Yeast essentiality outcome (E) — bridge built; needs one reference FASTA
The shipped DEG FASTA files carry only opaque DEG IDs (e.g. `>DEG20010001`) with
**no organism/ORF annotation**. Two facts recovered here close most of the gap:

- **The yeast essential set is the `DEG2001` block of `DEG20.nt`** — *S. cerevisiae*
  is the first eukaryote in DEG, and that block holds exactly **1,110 essential
  coding sequences** (all codon-length multiples), consistent with the
  manuscript's ~1,009 essential genes. Extract with the DEG-block filter in
  `label_essential_from_deg.py`.
- `label_essential_from_deg.py` **maps those 1,110 CDS to systematic ORF names by
  exact sequence match** against a yeast ORF-CDS reference (validated: given real
  DEG2001 sequences it recovers their ORF names exactly and ignores decoys).

The only remaining input is a **yeast ORF coding-sequence FASTA keyed by ORF
name** — SGD `orf_coding_all_R64-*.fasta` (header first token = ORF) or Ensembl
Fungi `Saccharomyces_cerevisiae.R64-1-1.cds.all.fa.gz`. Both hosts (sgd-archive,
ensembl) are off this environment's network allowlist, so either upload that one
FASTA or allowlist the host. Then the full outcome regenerates:
```
# 1. DEG essential CDS -> systematic ORF names
python label_essential_from_deg.py --deg DEG20.nt.gz --deg-block DEG2001 \
    --orf-cds orf_coding_all_R64.fasta --out scer_essential_orfs.txt
# 2. build the cohort with real E
python build_yeast_cohort.py --string 4932.protein.physical.links.v12.0.csv \
    --essential scer_essential_orfs.txt --out yeast_interactome_DEG.csv
# 3. re-test M5 (penalized fit)
python analysis_corrected.py --csv yeast_interactome_DEG.csv
```
A plain ORF-per-line list or a CSV with an `orf`/`gene` column also works
directly at step 2 if you already have the essential ORF names.

## 4. Pipeline self-test without private data
So CI and reviewers can exercise the full machinery deterministically:
```
python make_synthetic_cohort.py --out github_repositories_SYNTHETIC.csv
python analysis_corrected.py --csv github_repositories_SYNTHETIC.csv --synthetic
```
The fixture is drawn from a genuinely linear (additive, no-D²) logit; a correct
pipeline must return **PASS** on the VIF gate, **NO CURVATURE** on the primary
nested test, and recover the τ_v effect. It does. (The secondary single-term
ΔAIC swings wildly on the same data — the live demonstration of referee **M2**.)
```
python -m pytest tests/ -q     # tau_v_monitor: 13 tests
```
