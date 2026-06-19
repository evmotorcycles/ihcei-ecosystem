# Pre-Registration — Quadratic Governance Coupling Test (GovPhys)

**Hypothesis under test:** that systemic viability in a *semantic* network couples
to communication fidelity *quadratically*, `E = U · D²`, rather than linearly,
`E = U · D`.

**Status:** locked specification. Commit this file and the SHA‑256 printed by
`govphys_quadratic_prereg_test.py` **before** the first data fetch. Do not change
any definition or threshold after data is seen. The point of the design is that it
can **confirm, disconfirm, or come back inconclusive**, and all three are reportable.

This test exists because every prior cohort with real outcome data favoured the
**linear** relation, and because the one cohort with genuinely independent two‑hop
telemetry (yeast, VIF ≈ 1.0) *rejected* the quadratic (ΔAIC ≈ −1805, AUC 0.47).
GitHub is the cheapest domain where an *independent* two‑hop D can be measured at
scale, so it is where the quadratic gets its fair, falsifiable shot.

## Unit & outcome
- **Unit:** one public GitHub repository.
- **E (outcome, measured, non‑circular):** `E=0` if `archived=True` **or** no push
  in > 24 months; else `E=1`. Source: repo lifecycle metadata only — independent of
  D and of τ_v. (This is the firewall against the ZEGL-style circularity, where the
  outcome was *defined* rather than observed.)

## Variables
- **D_enc ∈ [0,1] — encoding fidelity (the node's own output):** mean TF‑IDF (1–2 gram)
  cosine of up to 100 recent commit messages against a locked methodology reference
  (`OQM_REFERENCE`), ×4 stretch, clipped.
- **D_dec ∈ [0,1] — enablement / decoding fidelity (measured on *others*):**
  `mean(outsider_merge_rate, contribution_spread)` where
  `outsider_merge_rate` = merged PRs by non‑core authors ÷ all PRs by non‑core authors
  (non‑core = `author_association ∈ {CONTRIBUTOR, FIRST_TIME_CONTRIBUTOR, FIRST_TIMER,
  MANNEQUIN, NONE}`), and `contribution_spread = 1 − Gini(contributions)`.
  *Why this is the crux:* D_dec is computed on **other** contributors' success, so it
  is structurally independent of D_enc (a node's own message quality). That
  independence is precisely what gives the two‑hop channel a chance to stay intact
  (low VIF) — the condition under which the quadratic term could carry unique variance.
- **U — capacity:** `log(1+contributors) · log(1+commits_sampled)`.
- **τ_v — enforcement latency (Third Law; reported separately, never inside D):**
  mean issue‑close latency over closed non‑PR issues, capped 365 days; imputed to 30.0
  and flagged when unmeasurable. **Imputed fraction is reported per group** — the exact
  robustness check the earlier τ_v result lacked.

## Sampling (locked queries, dedupe by `full_name`, seed 42)
| Stratum | Query | Purpose |
|---|---|---|
| S1 thriving | `language:python stars:>1000 pushed:>2024-06-01` | high‑D / survivors |
| S2 aging | `language:python stars:100..1000 pushed:2022-01-01..2023-12-31` | mid |
| S3 at‑risk | `language:python stars:10..100 pushed:<2022-01-01` | low‑D / stale |
| S4 failed | `language:python archived:true stars:>10` | guarantees failures |

Target ≈ 250/stratum. **Require N_total ≥ 1000 and N_fail ≥ 100** (so the low‑D /
failing region — where linear and quadratic actually diverge — is populated, and the
outcome is not degenerate the way the 3/492 SEC cohort was).

## VIF gate (channel‑intact requirement)
Compute `VIF(D_enc, D_dec) = 1/(1−r²)`. **If VIF ≥ 5 the two hops are redundant
(channel collapse) and the quadratic test is INCONCLUSIVE** — you cannot discriminate
two‑hop structure when the hops carry the same information. This is the framework's own
boundary condition, applied honestly as a gate rather than an excuse.

## Analysis
- **PRIMARY (framework's literal claim).** Scale D to [0,1] by empirical min‑max
  (so D² is not artificially crushed toward zero, the artefact that handicapped the
  yeast fit). Logistic AIC: `M_lin: logit(E)=b₀+b₁(U·D_s)` vs
  `M_quad: logit(E)=b₀+b₁(U·D_s²)`. `ΔAIC = AIC_lin − AIC_quad` (>0 favours quadratic).
  Permutation null: permute D_s 1000× (seed 42), z‑score the observed ΔAIC.
- **SECONDARY (scale‑robust curvature).** Nested logistic on natural D∈[0,1]:
  `M0: U`, `M1: U+D`, `M2: U+D+D²`. Reported for concordance.

## Decision rule (pre‑committed, both directions — **thresholds locked**)
A verdict on the quadratic requires `N_fail ≥ 100` **and** `VIF < 5`.

| Verdict | Condition |
|---|---|
| **QUADRATIC SUPPORTED** | `ΔAIC > 10` **and** permutation `z > 3` |
| **QUADRATIC DISCONFIRMED** | `ΔAIC ≤ 0` (linear at least as good) |
| **INCONCLUSIVE** | `VIF ≥ 5`, or `0 < ΔAIC ≤ 10`, or `N_fail < 100` |

## What each outcome means for the paper
- **Supported** → the first genuine, pre‑registered evidence for the quadratic in a
  semantic domain. It would justify upgrading the claim from hypothesis to finding.
- **Disconfirmed** → a clean negative that, with the yeast result, strengthens the
  honest boundary paper: coupling is linear even where the channel is intact.
- **Inconclusive (channel collapse)** → the two‑hop construction itself failed on
  GitHub, and the operationalisation needs rethinking before any claim is made.

The Third Law (τ_v → failure) is reported regardless and is **logically separate**
from the quadratic claim; a significant τ_v result neither requires nor rescues it.