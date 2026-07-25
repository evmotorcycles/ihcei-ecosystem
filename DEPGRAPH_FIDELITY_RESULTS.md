# E = U·D on a real dependency graph — an external test that could fail

*The honest one. Unlike the NCU simulations (which confirm their own construction),
this scores the linear coupling law on a **real PyPI dependency graph** against an
**external outcome the theory never saw** — so it could have come out wrong, and it
came out **mixed**. Reproduce: `python3 depgraph_fidelity_scorer.py --cap 1500 --seed 1`.*

---

## Why this one is different (and the only NCU-adjacent thing that can fail)

A critique worth taking seriously: four of the five NCU tests are
*construction-confirming*. Barakah is **defined** as `U·D_enc·D_dec` and Shaytan is
**defined** as a thing that lowers D, so "more Shaytan → less Barakah" is arithmetic,
not evidence — reality never got a vote. A green light that cannot turn red is a
**spec test**, not an experiment. The tell is the clean 5/5 sweep; real testing
produces a *mixed* record (the quadratic died, `D_gap` returned a null p=0.735,
irreducibility went 0-for-3).

This test is built to be able to fail:

- **Nodes** = Python packages crawled live from the PyPI JSON API (real topology).
- **Edges** = `A requires B` (real runtime dependencies).
- **U** = degree (utilization). **D_enc** = local clustering coefficient,
  **D_dec** = min-max betweenness — the *same* construction validated on yeast.
- **E** = survival: released within 24 months = alive, else abandoned. Release
  recency is **independent of graph topology** → non-circular.

Four ways it could have failed: the VIF gate could collapse; the failing region
could be too small (→ honest non-test); D could be at chance; the quadratic could
win.

## Results (N = 434 packages, 840 edges, 66 abandoned)

| Check | Result | Could it fail? |
|---|---|---|
| **[a] Channel-intact gate** | VIF(D_enc, D_dec) = **1.018** → PASS (intact) | yes — clustering & betweenness could have been collinear |
| **[b] Failing region** | 66 abandoned → populated (first crawl was underpowered and was **triaged as a non-test**, not forced) | yes |
| **[c] Does D predict survival?** | D alone CV AUC = **0.553** — *weak, barely above chance* | yes — could be 0.5 |
| **[d] Does U·D beat U alone?** | **NO**: U·D 0.570 vs U 0.590 — utilization dominates | yes |
| **[e] Linear vs quadratic (out-of-sample CV, robust to separation)** | M1 U+D = 0.590, M2 +D² = 0.590 (Δ +0.000) → **linear adequate, quadratic adds nothing** | yes — quadratic could have improved |

*(The MLE likelihood-ratio curvature test hit separation — the same degeneracy as
the yeast M5 artifact — so curvature was adjudicated by regularized 5-fold CV AUC,
which is separation-robust.)*

## The honest read

This is a **mixed / weak** result, and that is its value:

- **Reconfirmed on external data:** the channel-intact construction works on a real
  graph (VIF 1.02), and **the quadratic adds nothing** out-of-sample — consistent
  with the yeast/GitHub finding, now on a third, independent, external network.
- **Not confirmed:** on this graph the two-hop fidelity **D is only marginally
  predictive of survival (0.553)**, and the multiplicative **U·D does not beat raw
  utilization U** (0.570 vs 0.590). The linear law's *predictive superiority* is
  **not** demonstrated here — utilization alone is the stronger single signal.

So the dependency graph **neither overturns nor cleanly re-confirms** LISM. It
sharpens the scope: the strong external validation remains **yeast essentiality and
GitHub survival**; software-package abandonment is only weakly coupled to two-hop
topology, and utilization carries most of what little signal exists. That is a
result that could have come out otherwise — which is exactly why it counts.

## What would make it stronger (pre-registered next step)

Bind D to survival on a graph where two-hop fidelity should matter more and the
abandoned class is larger: crawl to several thousand packages (deeper, with more
niche/old libraries), or use a domain where the "decoding" hop is a genuinely
independent actor (e.g., downstream dependents' adoption vs the maintainer's release
cadence). Lock the criterion first; report the null if it stays null.

## Reproduce
```
python3 depgraph_fidelity_scorer.py --cap 1500 --months 24 --seed 1
# real PyPI crawl (cached in /tmp/pypi_cache); prints checks [a]-[e]; writes depgraph_results.json
```
