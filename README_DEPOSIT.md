# LISM — Deposit / Release Package

**Linear Institution Stability Model (LISM)** — *Information-Fidelity Coupling in
Networks Is Linear, Not Quadratic: A Pre-Registered Cross-Domain Test, with
Enforcement Latency as a Collapse Predictor.*

Author: Labib Mago — Novora Research Initiative, Open Science Division.
This package is a self-contained, reproducible release.

---

## Headline results (as verified in this deposit)

- **Coupling is linear, not quadratic**, in the two domains where a valid,
  channel-intact two-hop test was possible:
  - **Yeast interactome** (N = 4,825; VIF(D_enc,D_dec) = 1.003): linear AUC ≈ 0.73;
    the quadratic single-term adds nothing (AUC ≈ 0.59–0.72 under any converging
    fit). The previously reported "AUC 0.41 / anti-predictive" is a **non-converged-
    fit artifact** (`converged=False`), corrected here.
  - **GitHub repositories** (N = 992, pre-registered): quadratic disconfirmed
    (ΔAIC = −3.48; VIF = 1.02). Reproduces exactly from the archived CI run.
- **Enforcement latency τ_v is a robust collapse predictor** (GitHub): failed
  50.6 d vs surviving 19.8 d, Mann-Whitney one-tailed p ≈ 10⁻³¹ (≈ 10⁻²⁹ on
  directly measured latency).
- **Legislation & judicial coupling: INCONCLUSIVE** on live Congress.gov data —
  no independent second hop in the corpus (documented, not a null).

## What's in the package

| File | Role |
|---|---|
| `LISM_manuscript_REVISED.md` | The corrected manuscript (M1–M5 addressed) |
| `PEER_REVIEW.md` | Independent referee report + 2 reproduction addenda |
| `REPRODUCIBILITY.md` | Exactly what reproduces, from what, and how |
| `LISM_VALUE_TO_CIVILIZATION.md` / `LISM_EXPLAINED_FOR_EVERYONE.md` | Impact, technical + plain-language |
| `LEGISLATION_JUDICIAL_RESULTS.md` | Live legislation/judicial run (inconclusive) |
| `govphys_quadratic_prereg_test.py` | Pre-registered GitHub fetch + test (spec-hash locked) |
| `PREREGISTRATION.md` | The locked GitHub pre-registration |
| `reproduce_analysis.py` | Framework-neutral recomputation of every headline number |
| `analysis_corrected.py` | Nested-LRT curvature test + reproducible permutation tail (M2/M3) |
| `build_yeast_cohort.py` | Yeast cohort from raw STRING (author's degree/clustering/betweenness construction) |
| `extract_deg_essential.py`, `biogrid_name_map.py`, `label_essential_from_deg.py` | Yeast essentiality labelling from raw DEG + BioGRID |
| `analysis_yeast.py` | Yeast linear-vs-quadratic + the 0.41 artifact reproduction |
| `make_synthetic_cohort.py` | Deterministic fixture so the pipeline runs without private data |
| `legislation_coupling_test.py` | Legislation/judicial test via the live Congress.gov proxy |
| `tau_v_monitor/` + `tests/` | Domain-agnostic enforcement-latency early-warning tool (13 tests) |
| `requirements.txt` | Pinned dependencies |
| `zenodo_metadata.json`, `CITATION.cff`, `SHA256SUMS.txt` | Deposit metadata + integrity |

## Reproduce (quickstart)

```bash
pip install -r requirements.txt

# GitHub arm: recompute headline numbers (needs the per-repo CSV; see REPRODUCIBILITY.md)
python reproduce_analysis.py --github github_repositories.csv

# Yeast arm from raw public inputs:
python extract_deg_essential.py --annotation deg_annotation_e.csv --out scer_essential_genes_DEG.csv
python biogrid_name_map.py --biogrid BIOGRID-ORGANISM-Saccharomyces_cerevisiae-*.tab.txt --out yeast_name_orf_map.csv
python build_yeast_cohort.py --string 4932.protein.physical.links.v12.0.csv \
    --essential scer_essential_genes_DEG.csv --aliases yeast_name_orf_map.csv \
    --betweenness-k 1500 --out yeast_interactome_DEG.csv
python analysis_yeast.py --csv yeast_interactome_DEG.csv

# Pipeline self-test without private data:
python make_synthetic_cohort.py --out github_repositories_SYNTHETIC.csv
python analysis_corrected.py --csv github_repositories_SYNTHETIC.csv --synthetic
python -m pytest tests/ -q
```

## Raw public inputs (not redistributed here; fetch from source)

- STRING v12 physical links, *S. cerevisiae* taxon 4932 (`string-db.org`)
- DEG eukaryote essentiality, block DEG2001 = *S. cerevisiae* (Giaever et al. 2002)
- BioGRID *S. cerevisiae* interactions (name map only)

## License

Manuscript & docs: CC-BY-4.0. Code: MIT. (Adjust before formal submission if
your target venue requires otherwise.)
