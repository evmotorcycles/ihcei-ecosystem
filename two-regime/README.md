# Two-Regime Telemetry — when the retired equations are each correct

**One command:** `python3 two-regime/two_regime.py` · stdlib · offline · `$0`

Earlier this project **retired** two telemetry equations — the threshold `D > D_min` and the
quadratic `E = U·D²` — in favor of the linear `E = U·D`. The DeepMind generator/evaluator
study shows they were retired from the *wrong* regime. **They aren't wrong — each is the
correct law in its own regime**, and the Novora stack needs both a probabilistic and a
deterministic framework, each with a role.

---

## The three regimes

| regime | verifier | law | governance reading |
|---|---|---|---|
| **R1** soft (probabilistic) | accepts with prob = fidelity `d` | **`E = U·D`** (linear) | free will as *bounded choice within capacity* |
| **R2** hard (deterministic) | accepts iff `q ≥ D_min` | **`D > D_min`** (threshold) | evidence-based knowledge (N157 / Barakah, OQM) — a claim clears the bar or it doesn't |
| **R3** two serial hard hops | encode-gate AND decode-gate | **`E = U·D²`** (quadratic) | DeepMind's compiler + test suite — both must pass |

## The results (gates locked before running, spec `ca2c72e3…`)

```
R1 soft → LINEAR (E=U·D):        slope 0.999   R² 0.9999                        → PASS
R2 hard → THRESHOLD (D>Dmin):    threshold residual 0.0  vs  best-line 6.734    → PASS
R3 serial → QUADRATIC (E=U·D²):  survival-vs-d² slope 0.999  R² 1.0000
                                 two(0.5)=0.250 < soft(0.5)=0.498               → PASS
```

- **R1** — a *soft* verifier (probabilistic accept) makes yield **linear** in fidelity. This is
  `E = U·D`, unchanged: the probabilistic regime.
- **R2** — a *hard* gate is a **step** at `D_min`. A threshold model reproduces it exactly
  (residual **0**); the best straight line **cannot** (residual **6.73**). The retired `D > D_min`
  is the correct law here — the deterministic regime, where evidence either clears the bar or it
  doesn't.
- **R3** — **two** deterministic hops in series **multiply**: survival = `d·d = d²`, exactly
  (R² = 1.0000), and sits strictly *below* the single-gate line. The retired `E = U·D²` is the
  correct **survival** law for a two-hop verified pipeline. *(This does not re-open `U·D²` as a
  single-hop coupling law — that was correctly retired; it is the serial-survival law.)*

## Grounded on real open-source data (`G`)

Pull requests are the probabilistic **generator**; CI + review is the deterministic **evaluator**;
merged = **survived**. Real survival `s = merged / (merged + closed_unmerged)`, fetched via the
GitHub API and frozen:

| repo | merged | closed-unmerged | s |
|---|---|---|---|
| scipy/scipy | 11,436 | 2,216 | **0.838** |
| mitmproxy/mitmproxy | 2,796 | 635 | **0.815** |
| biopython/biopython | 2,570 | 717 | **0.782** |
| nextflow-io/nextflow | 1,829 | 702 | **0.723** |

The deterministic gate is a **real filter** — it passes ~72–84% and rejects the rest. **Excluded
honestly:** `pytorch/pytorch` (merged 6,534 / unmerged 120,675 → s = 0.05), whose unmerged count is
dominated by bot/ghstack mass-closures — a confounded artifact, not a gate rejection rate. The
exclusion is declared, not hidden.

## Why it matters

The Novora stack was building only the probabilistic side (`E = U·D`, `τ_v`). DeepMind's
architecture shows the **deterministic** side is equally required — and it was already retired by
mistake. This module restores both, each in its regime, and proves the split on a clean testbed
and on real GitHub data.

## Files

```
two-regime/
  prereg/two_regime_prereg.json         spec (locked before running) — R1/R2/R3/G
  prereg/MANIFEST.sha256.json
  data/github_pr_survival_frozen.json   real PR-survival counts (frozen)
  two_regime.py                         the experiment (stdlib, seeded, offline)
  test_two_regime.py                    pytest guard (R1/R2/R3/G)
  results_two_regime.json               emitted results
```

Layer-1, offline, `$0`. Both a deterministic and a probabilistic framework — each with a role.
