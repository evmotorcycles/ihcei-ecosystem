# Five gaps — the closure ledger

[Artifact](https://claude.ai/code/artifact/b801057d-99a6-42b3-ada9-c071fa5bdeba) ·
local copy `docs/five_gaps_ledger.html`

| # | Gap | Status | Spec | Score |
|---|---|---|---|---|
| 1 | Balanced prompt grid for Δ ≥ 0.20 | fix applied, **gate still failed** | `5576e524` | 4/7 |
| 2 | Physical quantum hardware for LMD | **BLOCKED** — needs authorisation | — | — |
| 3 | Fixed policy endpoints for Q3 | **not attempted** | — | — |
| 4 | Computationally irreducible testbed for Q5 | built and measured | `0de17fc4` / `0cd701a4` | 2/5 · 5/6 |
| 5 | First-principles graph-topological scarcity | one substrate of five | `13535547` | 5/6 |

Full write-ups: [`BALANCED_GRID.md`](BALANCED_GRID.md) ·
[`IRREDUCIBILITY_Q5.md`](IRREDUCIBILITY_Q5.md) ·
[`SCARCITY_DOMAIN_LIMIT.md`](SCARCITY_DOMAIN_LIMIT.md)

```bash
python3 -m pytest -q balanced-grid/test_bg.py irreducible/test_irr.py scarcity/test_scar.py
```

## The prediction that was wrong

I said Gap 1 was "fully closable" and would convert Q4 from unlicensed to licensed. It did
not. `I` moved exactly as designed (0.4375 → 1.0000); `V` and `C` both fell; Δ = 0.1060 —
a fifth consecutive void against an unchanged 0.20 floor.

## The finding nobody was looking for

15 of 20 artifacts return the identical verdict `0.1428` under **both** HELM engines.

| Engine | Spearman vs manipulativeness | Spearman vs **word count** |
|---|---:|---:|
| v1 | +0.0445 | **−0.4831** |
| v2 | +0.0388 | **−0.4774** |

Both engines score longer text as *less* manipulative, to the same degree — so it is not
v2's density weighting but the shared gate/regex structure. On earlier sets the manipulative
texts were also the short texts; this spec broke that confound and the signal vanished.

**Q4 reverts to not licensed.** The `S` half of shield-and-signal is unaffected (a
within-artifact deviation), so the rock finding stands. Correction recorded on `HELM_V2.md`.

## Two nulls against our own claims

- **Q5:** giving the predictor 30 steps of the actual trajectory gained **+0.0051** against a
  0.10 bar. "Monitor τ_v rather than predict" has no support from this testbed. Measured twice
  at the same number; the bar was not lowered.
- **§3.3c:** the product form's advantage where the decode hop is scarce came to **+0.0093**
  against a pre-registered +0.05, CI [−0.0283, +0.0424] excluding the predicted effect. In the
  scarce stratum *both* forms are anti-predictive. `LISM_manuscript_REVISED.md` §3.3c(i)
  carries the amendment.

## What DCM turned out to be

Five voids, every one on an outcome landing on a small lattice. On the two continuous
outcomes here (AUC, AUC difference) Δ **cannot fail** — V and C sit near 1 by construction —
so it was marked `excluded` in both rather than counted as a pass. DCM is an admissibility
check for concentrated or categorical outcomes and is silent elsewhere.
