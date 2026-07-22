# Hoffman conscious-agent simulation — LISM in a perceptual-interface substrate

A pre-registered, reproducible (`$0`, offline, stdlib) agent-based simulation of Donald
Hoffman's **Interface Theory of Perception (ITP)**, used to test whether LISM's laws hold
in a substrate where *accurate perception does not maximise fitness*.

```bash
python3 hoffman-agents/hoffman_sim.py
python3 -m pytest -q hoffman-agents/test_hoffman.py
```

Spec SHA-256-locked at `79f75028…`; the runner re-hashes and refuses to run on mismatch.
Wired into `bash reproduce_all.sh`.

## The world

A true state `x ∈ [0,1]`; fitness `f(x) = exp(−((x−0.5)/0.18)²)` is **non-monotonic** (a
resource is good in moderation). Because the fitness peak is *not* at "see x accurately,"
this is a world where Hoffman's **Fitness-Beats-Truth (FBT)** can happen.

## Three pre-registered hypotheses

| | Hypothesis | Result (seeded) |
|---|---|---|
| **P1** | FBT control: fitness-tuned strategy outcompetes truth-tuned under selection | **confirmed** — fitness-tuned share → **1.00** (a genuine Hoffman world) |
| **P2** | LISM: survival couples **linearly** to `U·D` (not quadratically) | **partial/weak** — linear directionally beats quadratic (R² **0.28 vs 0.14**, ~2×) but the absolute fit is weak; **no clean win claimed** |
| **P3** | τ_v: reconciliation latency predicts loss of coherence | **confirmed** — corr(τ_v, coherence) = **−0.94** |

**Green = P1 (genuine Hoffman world) + P3 (τ_v tracks coherence) + P2 reported honestly.**
A weak/partial P2 is a valid reported outcome, not a failure — the same symmetric-null
discipline that governs the HF coupling null.

## What this does and does not show

- **Does:** in a Hoffman-ITP world, a fitness-tuned interface is selected (FBT), and the
  latency to reconcile conflicting percepts strongly predicts network incoherence (τ_v law).
  Survival's coupling to fidelity leans linear (consistent with LISM's "graceful slide, not a
  quadratic cliff" — LISM's explanation of *why* a non-veridical interface is stable), but the
  effect here is weak, so we don't claim a clean linear win.
- **Does not:** prove ITP is true of reality, or claim the agents are conscious. It is a
  Layer-1 computational model.

## Honesty note on the "statutory / legislative" cohort

A companion note described a "Statutory / US Congressional Acts (N=365)" cohort as *already
tested*, "linear won decisively, ΔAIC=−10.03." **That is not in this repo, and it contradicts
the repo's own record**, which reports legislation/judicial coupling as **INCONCLUSIVE** (run
on live Congress.gov data, no independent second hop — see `zenodo_metadata.json`,
`LEGISLATION_JUDICIAL_RESULTS.md`, `LISM_CONTRIBUTION.md`). We do **not** count a statutory
cohort as validated. The validated LISM cohorts remain: yeast (N=4,825), GitHub (N=992),
knowledge/Stack Exchange (N=793), and the generic swarm — plus this Hoffman substrate as a
*partial* addition. Enron and SEC EDGAR are correctly filed as excluded non-tests.
