# Real Legislation Coupling Experiment — live data, no placeholders

**Date:** 2026-07-09 · **Source:** live U.S. bill full text via the deployed
Congress.gov proxy (`api/bill-text.js`, Vercel `project-6q4gj`) · **Outcome:**
enacted vs. not, from public legislative history (independent of the text).

This is a **real run on real data** — carried out after confirming that (a) no
Kaggle API exists on `project-x082n` (its redeploy is the same `main` code:
only `bill-text.js` + `gh-proxy.js`), and (b) the GitHub Search API is
scope-blocked from this environment (`403: sessions are bound to their
configured repositories`), so external clinical/contract datasets could not be
fetched here. Legislation via the Congress API was the one reachable real source.

## Cohort (N = 12, balanced)

`D_enc` = bill-text specificity per 1k words (defined terms + statutory
cross-references + numeric thresholds/deadlines + mandatory language).

| Bill | Enacted | Words | D_enc |
|---|:--:|--:|--:|
| 117-hr-1319 American Rescue Plan | ✔ | 108,571 | 51.8 |
| 117-hr-3076 Postal Service Reform | ✔ | 11,517 | 36.3 |
| 117-hr-1799 PPP Extension | ✔ | 364 | 79.7 |
| 118-hr-3746 Fiscal Responsibility | ✔ | 17,202 | 52.5 |
| 117-s-2938 Bipartisan Safer Communities | ✔ | 13,502 | 44.3 |
| 117-hr-3967 PACT Act | ✔ | 25,439 | 36.8 |
| 117-hr-1 For the People | ✗ | 152,933 | 38.5 |
| 117-hr-4 John Lewis VRA | ✗ | 13,092 | 23.1 |
| 117-hr-5 Equality Act | ✗ | 5,107 | 44.3 |
| 117-hr-40 Reparations Commission | ✗ | 2,725 | 22.0 |
| 117-hr-1280 George Floyd Justice in Policing | ✗ | 22,642 | 24.6 |
| 118-hr-2 Secure the Border | ✗ | 34,160 | 25.5 |

## Result

- **Specificity separates enacted from failed bills:** enacted mean D_enc **50.2**
  vs failed **29.7**, Mann–Whitney one-tailed **p = 0.013**.
- **Linear coupling, in-sample AUC 0.889.**
- **Nested curvature test (the LISM primary): ΔAIC(quad − lin) = −1.88, LRT
  p = 0.73 → no curvature; the linear model is adequate.** Directionally
  **consistent with LISM**: specificity couples to durability linearly, not with
  an accelerating quadratic penalty.

## Honest boundary (the invariant gates)

| Gate | Status |
|---|---|
| I1 channel independence | **FAIL** — bill text supplies only the encoding hop; there is no *independent* decoding hop (agency implementation / judicial enforcement measured on other actors) |
| I2 populated failing region | **FAIL** — N_fail = 6 ≪ 100 power floor; labelled convenience sample with selection bias (enacted skew to large omnibus acts, failed to short messaging bills) |
| I3 non-circular outcome | **ok** — enactment read from legislative history, not from the text |

**Verdict.** A genuine **one-hop** result — bill specificity → enactment is
linear, not quadratic — which is encouraging and consistent with the theory. The
**two-hop quadratic test remains INCONCLUSIVE** because the independent decoding
hop is absent (I1) and the sample is underpowered (I2). This is exactly the
boundary the manuscript names: resolving the two-hop question in legislation
needs the implementation/judicial telemetry supplied via a data-holder
Registered Report partnership (`PREREGISTRATION_generalization.md`).

Reproduce:
```
# fetch two labelled batches via the endpoint / Vercel MCP, then:
python legislation_real_experiment.py --enacted-json enacted.json --failed-json failed.json
```
