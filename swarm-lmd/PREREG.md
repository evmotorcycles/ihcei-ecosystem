# Swarm coupling and decay — pre-registration

Locked before the harness ran. This re-runs the digital-swarm coupling/decay
simulation and, this time, adds the LMD link: fidelity is tested against
**effective resistance from the root**, not only hop depth.

## Standing on a prior result that did NOT fully pass

`hf-cohort/swarm` A2 recorded, on a 500-node HF-calibrated tree:

| | |
|---|---|
| decay with depth | **confirmed**, corr = −0.89 |
| success couples LINEARLY to U·D | **not confirmed** — r² linear 0.7336 < r² quadratic 0.7511 |
| arm verdict | `coupling_confirmed: false` |

So the simulation aligned with E = U·D on the **decay** half and did not on the
**functional-form** half. This re-run does not assume otherwise. Whatever comes
out is what gets written down, and the dataset carries both.

## The model (fixed now)

A lineage swarm grown from one root. Each agent inherits from a parent through a
coupling `J`; each agent has capacity `U` (reach) drawn from a heavy-tailed
distribution, and two channels:

```
E = U · D_enc · D_dec
```

`D_enc` is how well an agent takes information in, `D_dec` how well it hands it
on. Fidelity at an agent is the product along its lineage, attenuated per hop by
a factor set by `J`. The whole swarm is also a weighted graph, so the LMD metric
gives an **effective resistance from the root** for every agent.

Seed 20260813. N = 4000 agents, 40 independent swarms, sweep J over 12
logarithmic steps in [0.05, 20].

## Predictions

**S1 — fidelity decays with hop depth.** Spearman ρ(fidelity, depth) ≤ −0.5.
*(This is the half that previously held; it is a replication, not a discovery.)*

**S2 — effective resistance predicts fidelity at least as well as hop depth.**
|ρ(fidelity, R_root)| ≥ |ρ(fidelity, depth)| − 0.02.
**This is the LMD link and it can fail.** Hop depth is a count; effective
resistance also sees how many *alternative paths* an agent has. If side-links
matter, resistance wins; if lineage is all that matters, they tie.

**S3 — the functional form of E.** Fit outcome against U·D_enc·D_dec, linear
against quadratic, by adjusted r². **No prediction is registered for which
wins**, because the prior run says linear did not. Both are reported.

**S4 — revoking the root zeroes the swarm.** With the root's outbound coupling
set to 0, every descendant's effective resistance from the root becomes
infinite and its delivered fidelity becomes exactly 0. Gate: 100%.

## Gates

| quantity | gate |
|---|---|
| S1 ρ(fidelity, depth) | ≤ −0.50 |
| S2 resistance vs depth | ≥ ρ_depth − 0.02 |
| S3 | reported, not gated |
| S4 descendants zeroed | 100% |

## The dataset

`data/swarm_rows.csv`, one row per agent, with the columns used above. It is a
**simulated** dataset. It is evidence about the model, not about the world, and
the header says so.
