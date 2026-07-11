# IHCEI Stack v3.0 — Probabilistic Kernel
**GT v18.2 · QG-COS · The Null-Result Pivot · July 2026**

## The evidence that forced the pivot

The pre-registered kubernetes/kubernetes confirmatory campaign (n = 4,979 human
PRs, 1,584 failures) returned **[NO SIGNAL]** on the D_gap → failure hazard:
coefficient +0.1939, 95% CI [−0.9286, +1.3164], p = 0.735, replicated null in the
unpressed robustness arm (p = 0.971). Any deterministic law of the form
"D_gap beyond a threshold ⇒ failure" predicts a detectable coefficient at this n.
None appeared.

Epistemic firewall note: the vscode exploratory pull (n = 3,685) shows a nominally
significant univariate association (β = −1.97 on merge, p = 0.0012), but 77% of its
rows sit at D_gap = 0 (degenerate mass; the multivariate fit separates). Per the
firewall, exploratory results are logged in `gt_probabilistic.CALIBRATION`, not
promoted. The confirmatory null governs.

Interpretation discipline (Layer honesty): the null **licenses** retiring
deterministic threshold physics and adopting a base-rate stochastic model in which
D-variables are covariates with null-centered priors. It does **not** positively
prove "reality is probabilistic" — absence of a deterministic signal is consistent
with probabilistic dynamics *and* with unmeasured deterministic causes. The
probabilistic model is adopted because it is the one the telemetry does not
contradict. Registry status: `SUPPORTED_BY_NULL`.

## Retirements (full, not partial)

| Construct | v2.3 status | v3.0 status |
|---|---|---|
| E = U·D² | "Prescriptive Lyapunov floor" | **RETIRED_FULLY.** No kernel quantity is computed as U·D². |
| D > D_min / D_crit hard trips | Constitutional floor, unbypassable | **RETIRED_FULLY.** Replaced by the probabilistic floor. |
| NERE unconditional Gates 3 & 7 | Certainty switches | **Retired.** Highest-weight evidence, with uncertainty (llr_sd). |
| Point-valued D | Everywhere | Beta posterior: mean + 95% credible interval. |
| Verdict-by-threshold | BLOCK/WARN/PASS trips | Posterior bands on P(fail \| evidence). |

## The Probabilistic Floor (replaces D_min)

1. **Epistemic floor** — every probability lives in [0.01, 0.99]. Certainty is
   unrepresentable by construction (`clip_floor`). The system cannot claim
   P(fail) = 0 for any D, nor P(fail) = 1 for any evidence.
2. **Base-rate floor** — each channel carries a Beta-distributed irreducible
   hazard calibrated from telemetry: kubernetes Beta(1585, 3396), mean 0.318;
   vscode Beta(602, 3085), mean 0.163; oss_default pooled weak prior.
3. **Verdict floor** — BLOCK requires posterior mean ≥ 0.85 **and** lower 95%
   credible bound ≥ 0.50. Wide intervals (genuine uncertainty) cannot trip BLOCK;
   they resolve to WARN. Confidence is a property of the whole posterior.

## What survives, transformed

- **E[E] = U·E[D | evidence]** — the SUPPORTED linear transmission form is kept
  as an *expectation* over the D posterior, with a CI. Never a point law.
- **Null-centered D_gap prior** — `b_Dgap ~ Normal(+0.1939, 0.5727)` straddles
  zero. Regression test: pushing D_gap from 0.00 to 0.86 **widens the credible
  interval and leaves the verdict band unchanged** — exactly what a null result
  should do to a model. This test is in `ihcei_kernel_v3.run_tests()`.
- **CBT4 taxonomy, correction pathways, certificates** — unchanged in structure;
  now attached to posteriors. Certificates carry P, CI, and prior provenance.
- **Correction-pump hypothesis** E_c = U·κ(1−D_in)·q — unchanged status
  (HYPOTHESIS, predictions locked).
- **Bayesian learning hooks** — `NEREEngineV3.update_gate_llr()` recalibrates
  gate weights from labelled telemetry; `IHCEIKernelV3.update_channel()`
  conjugate-updates channel base rates.

## Modules

| File | Role |
|---|---|
| `gt_probabilistic.py` | Core: law registry v3, calibration provenance (SHA-pinned), Beta hazards, Monte Carlo posterior, banded verdicts, floor enforcement. |
| `nere_engine_v3.py` | Seven gates as log-likelihood-ratio evidence → posterior P(manipulative) with CI. 5/5 on the v2.2 adversarial band suite. |
| `ihcei_kernel_v3.py` | Subclasses the v2.3 kernel's feature scorers verbatim; replaces verdict physics with posterior bands + expected essence. Runs standalone if v2.3 absent. |

## Quick start

```python
from ihcei_kernel_v3 import IHCEIKernelV3
from nere_engine_v3 import NEREEngineV3

kernel = IHCEIKernelV3(channel="kubernetes", verbose=True)
nere   = NEREEngineV3(prior_p=0.10)

v  = kernel.evaluate("Your AI output here", d_gap=0.02)
nv = nere.evaluate("Your AI output here", verbose=True)

print(v.verdict, v.p_failure, v.p_failure_ci95)   # band, posterior, CI
print(nv.verdict, nv.p_manipulative, nv.ci95)
```

## Verdict semantics (breaking change)

A v3.0 BLOCK means "the posterior probability of governance failure is high and
its lower credible bound is high." It never means "a law was violated." Downstream
consumers that logged `E = U·D²` or `D_min` breaches must migrate to
`p_failure` / `p_failure_ci95`. The Novora regime router's Gate 0 remains valid;
its `predict_e` endpoint should route to `expected_essence()` for TRANSMISSION.
