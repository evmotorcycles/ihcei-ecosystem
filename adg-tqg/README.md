# ADG (`C_dev`) & TQG-CFE (`Ψ`) — an empirical telemetry experiment

*The ADG and TQG-CFE equations are **not** physical laws with SI units. Like
`E = U·D` in LISM, they are **organization-graph telemetry**: a way to combine
measurable signals of a network into a scalar that should track its health. This
experiment tests **only** that Layer-1 telemetry reading, on real open-source
GitHub projects. It makes **no** claim about the Layer-3 metaphysical
interpretation (Nafs, Deen, perception), which the framework's own note labels
"a formal analogy, not empirical measurement." The two layers are kept strictly
apart — the same discipline `FLOOR_RETIREMENT.md` applies to LISM.*

```
python3 adg-tqg/experiment.py     # stdlib only, no network   (pytest: adg-tqg/ 4/4)
```

## Operationalization — each symbol → a measurable proxy

A repo is a governance network of contributors resolving flagged risk. Per repo:

| equation symbol | telemetry proxy |
|---|---|
| adoption (reach) | `a = ln(1+stars)` |
| throughput `G_ij` (knowledge transferred) | `t = ln(1+closed issues)` |
| responsiveness (enforcement speed) | `r = 1/(1+τ_v)`  (τ_v = LISM enforcement latency) |
| `Φ_Nafs` (practice vector) | `Φ = (a, t, r)`, each min-max normalized to [0,1] |
| `Θ_Deen` (perfect governance) | `(1, 1, 1)` |
| **TQG-CFE `A_n(Φ)`** (alignment) | `⟨Φ\|Θ⟩ / (\|Φ\|\|Θ\|)` — the paper's exact cosine formula, ∈[0,1] |
| **Ψ rendering** | `Ψ_Yusr` (ease) if `A_n > κ`; `Ψ_Usr` (hardship) if `A_n ≤ κ`  (`κ` = median) |
| `ħ_network` (noise) | normalized `τ_v` (enforcement latency = governance-failure noise) |
| `Σ Φ_iΦ_j G_ij` (aligned connectivity) | `a·t` (breadth × depth of transfer) |
| **ADG `C_dev`** | `A_n · (a·t) / (ε + ħ_network)` |

**The outcome `E` is measured independently**: `E=0` (failed) if archived or no
push in >365 days, else `E=1` (survived). Push-date/archived are **not** inputs to
`A_n` or `C_dev`, so predicting `E` from them is a genuine test, not a tautology.

## Falsifiable predictions and results (22 real repos, 16 survived / 6 failed)

| prediction | result | verdict |
|---|---|---|
| **H1 (ADG):** survived repos have higher `C_dev` | 3.19 vs 1.18, 1-tailed MWU **p=0.033** | supported |
| **H2 (TQG):** survived repos have higher alignment `A_n` | 0.860 vs 0.727, **p=0.018** | supported |
| **H3 (TQG):** `Ψ`-rendering at `κ` predicts survival | `Yusr` 90% survive vs `Usr` 58% | supported |

**3/3 on this cohort.** The Mann-Whitney U is computed in pure stdlib (the same
routine validated against `scipy` in `repro/`); the p-values are conservative.

## Honest scope

- **Correlational, not an oracle**, and a small cohort. The operationalization
  makes real errors: `angular/angular.js` is *archived* (`E=0`) yet scored high
  `A_n`/`C_dev` (`Yusr`) because it froze its issue queue while responsive — a
  genuine false positive that shows the proxy is a signal, not a certainty.
  `less.js` is the opposite (alive but slow → `Usr`). Those edge cases are why
  the separation is significant-but-imperfect, which is the honest state.
- **It recovers and extends LISM.** Because responsiveness `r` embeds `1/(1+τ_v)`,
  the experiment re-derives the LISM enforcement-latency signal through the
  ADG/TQG lens and adds adoption + throughput structure. That's the expected,
  coherent result — the ADG C_dev is a superset of the τ_v hazard read.
- **Layer 1 only.** This tests the telemetry. It neither supports nor refutes any
  metaphysical claim in the framework; those are explicitly out of empirical scope.

## Files

- `experiment.py` — operationalization + the three tests + display (stdlib).
- `fixtures/experiment_cohort.json` — 22 real repos (stars, closed-issues, τ_v,
  push date, archived, E), fetched via the deployed `api/gh-issues`.
- `test_experiment.py` — pytest wrapper (4/4).
