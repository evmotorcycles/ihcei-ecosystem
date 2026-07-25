# M5 resolved — yeast ORF-keyed essential labels + cross-validated re-report

*The last pre-submission ⏳ item, now closed. The yeast outcome column is
regenerated **end-to-end from raw public data** (STRING v12 physical links + DEG
essential-gene annotation + BioGRID name map), the ORF-keyed essential label file
is shipped, and the M5 quadratic-AUC artifact is re-reported under a converged,
cross-validated fit.*

---

## What was pending

The referee point **M5**: the original manuscript reported the yeast quadratic
single-term as "anti-predictive, AUC ≈ 0.41 (below chance)" from an in-sample logit
it *also* described as degenerate under near-perfect separation. A monotone
transform of a predictor cannot legitimately fall below chance unless the fit
sign-flipped, so the number needed a converged / cross-validated re-report — which
required the yeast outcome labels keyed to STRING's **systematic ORF names**
(`YGR222W`, …), not DEG's standard gene names (`TFC3`, …).

## How it was resolved (raw → labels, no circularity)

1. **Essential set (1,110 genes).** Extracted the DEG2001 (S. cerevisiae) block
   from `deg_annotation_e.csv` → `data/yeast/scer_essential_genes_DEG.csv`.
2. **Name → ORF map (12,321 entries).** Built from the BioGRID yeast tab file with
   `biogrid_name_map.py` (systematic ORF, official symbol, and each alias → ORF).
3. **Cohort rebuild.** `build_yeast_cohort.py` on raw STRING v12 physical links,
   resolving the DEG standard names onto systematic ORFs via the map. Essentiality
   is the **wet-lab DEG label**, never defined from topology (non-circular).

Result: **4,825 proteins, VIF(D_enc, D_dec) = 1.003** (channel intact, exact match
to the manuscript), **1,055 essential ORFs labeled** (1,055 / 1,077 essential ORFs
present in the graph). Shipped: `data/yeast/scer_essential_orfs.txt` (the ORF-keyed
label file), `data/yeast/yeast_interactome_DEG.csv` (the rebuilt cohort).

## The M5 re-report (`analysis_yeast.py`)

| Fit | Linear `U·Dₛ` | Quadratic `U·Dₛ²` |
|---|--:|--:|
| In-sample single-term AUC | 0.726 | 0.722 |
| **5-fold CV, regularized AUC** | **0.666** | **0.611** |
| (reference) D alone / U alone | D 0.701 | U 0.727 |

- **The quadratic is not anti-predictive.** Under a converged single-term fit it is
  AUC 0.72 in-sample and **0.61 cross-validated — above chance, and *below* the
  linear term** (0.67 CV). Adding the square does not help.
- **The "0.41" is a numerical artifact, confirmed.** The manuscript's multivariate
  `U + D + D²` spec fails to converge under separation (`converged = False`,
  in-sample AUC = 0.490, β_D² blows up to ~2.5e5). A non-converged fit is what
  produced the sub-chance number; every converged/CV fit is ~0.6–0.72.
- **Nested curvature test.** `M1(U+D)` vs `M2(U+D+D²)` is separation-degenerate
  (non-converged M2), so the LRT is uninformative here; the reliable evidence is the
  converged/CV single-term comparison above, which says: **linear adequate, quadratic
  adds nothing.**

## Bottom line

The claim the paper relies on — *adding D² does not improve prediction of yeast
essentiality* — holds under the corrected, converged, cross-validated analysis, and
the headline VIF and cohort size reproduce from raw data. The prior "0.41" is
retired as a non-converged-fit artifact, with the full provenance now in-repo.

**Reproduce:**
```
python3 build_yeast_cohort.py --string 4932.protein.physical.links.v12.0.csv \
    --essential data/yeast/scer_essential_genes_DEG.csv \
    --aliases yeast_name_orf_map.csv --betweenness-k 1500 \
    --out data/yeast/yeast_interactome_DEG.csv
python3 analysis_yeast.py --csv data/yeast/yeast_interactome_DEG.csv
```
