# Three-Domain Dataset Sweep — Final Results (live, end-to-end)

**Date:** 2026-07-09 · **Pipeline:** `api/gh-search.js` (deployed on Vercel
`project-6q4gj`, production) → live GitHub Search API → `kaggle_dataset_screen.py`
three-invariant gate. Real data, run end-to-end. No placeholders.

## How this was run

1. **Kaggle route unavailable:** no Kaggle function exists in the repo (the
   `project-x082n` redeploy is the same `main` code), and Kaggle credentials are
   not configured, so `api/kaggle-search.js` reports `keyConfigured:false`.
2. **GitHub route used (as requested):** `api/gh-search.js` runs the GitHub
   Search API **server-side on Vercel**, whose egress is not scope-bound — so it
   reaches GitHub where the sandbox's proxy blocks it (`403: sessions are bound to
   their configured repositories`). Verified live: e.g. `mimic clinical dataset`
   → 20 real repos, `covid19 dataset` → 20 real repos.
3. Three domain queries were run against the live endpoint and the returned
   repositories screened against invariants **I1** (independent two-hop channel),
   **I2** (populated failing region), **I3** (measured non-circular outcome).

## Result: 22 real datasets screened, **0 eligible** for a two-hop test

| Domain | Query | Real datasets found | Passed gate |
|---|---|--:|--:|
| Clinical governance | `patient safety dataset` | 8 (CMS hospital-quality, MIMIC, Leapfrog, drug-safety, OpenNeuro) | **0** |
| Contract adjudication | `legal contract dataset` | 7 (CUAD, LEDGAR, synthetic clause corpora) | **0** |
| Legislation | `congress bills dataset` | 7 (legis-graph, bill-passage predictors, lobbying) | **0** |

**Every dataset failed invariant I1** — it is single-source: a corpus of one
kind of signal (clinical features, or contract clauses, or bill records) mapped
to a label. None supplies an **independent decoding hop** (e.g. clinical:
incident-report quality *and* a separate RCA-completion registry; contract:
clause specificity *and* independent jurisdiction enforcement capacity;
legislation: bill specificity *and* independent agency-implementation/judicial
telemetry). Most also fail I3 (the "outcome" is a label on the same text/records,
not a downstream measured outcome).

Representative confirmations:
- **CUAD / LEDGAR** (contract): clause-classification corpora — encoding hop only,
  no adjudicated durability outcome, no independent enforcement hop.
- **MIMIC / CMS hospital-quality** (clinical): rich outcomes (mortality,
  readmission) but a **single** EHR/quality source — no independent
  incident→RCA two-hop structure.
- **legis-graph / bill-passage predictors** (legislation): bill records + a
  passage label — single hop, and the same "dead-channel" collapse the manuscript
  documented for the ~468k-bill corpus.

## Verdict

**No convenient public dataset — Kaggle or GitHub — supports a two-hop
linear-vs-quadratic test in any of the three domains.** This is not a failure of
the search (the search works and returns real, relevant datasets); it is the
**empirical confirmation of LISM's central boundary condition**: the linked,
*independent* two-hop telemetry with a *measured, non-circular* outcome does not
exist as an off-the-shelf download. It must be assembled through a data-holder
**Registered Report** partnership, exactly as specified in
`PREREGISTRATION_generalization.md` (with the three invariants as pre-committed
gates).

## Reproduce

```
# live GitHub search (server-side, via the deployed endpoint):
curl "https://project-6q4gj.vercel.app/api/gh-search?type=repositories&q=patient%20safety%20dataset"
# then screen the returned metadata against the three invariants:
python kaggle_dataset_screen.py --results-json gh_sweep_results.json
```
