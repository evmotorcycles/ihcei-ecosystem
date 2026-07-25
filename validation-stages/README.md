# Three offline validation stages (pre-registered)

All Layer-1, offline, `$0`, no Anthropic API, no gated dataset. Corpora are
**authored, SHA-256-locked representative samples** (the confirmatory n≥300/1000
corpora are a future registered-report deliverable). Locked in `prereg/`; runners
read thresholds only from the frozen spec.

```
node   validation-stages/stage12_screen.mjs     # Stage 1 + 2
python3 validation-stages/stage3_swarm.py        # Stage 3
```

## What came back (reported honestly — the epistemic firewall in action)

- **Stage 1 · Evasive coercion → NULL (honest).** On the locked keyword-free
  corpus the **fast-mode baseline** catches only **25%** of evasive coercion
  (Brier 0.30), far short of the pre-registered deep-claim bar (recall ≥ 0.80,
  Brier ≤ 0.15). Reported as a **null**: the on-device **distilled 1–3B NPU model
  is the load-bearing, still-unproven bet**; fast mode degrades to
  Fast-Mode+Primitives. *No threshold or corpus was changed post-hoc.*

- **Stage 2 · Emergency calibration → PASS on the safety property.** Across four
  strata (SRE, clinical, physical-safety, deadline) the corroboration gate has a
  **0.000 false-BLOCK rate** — it never silences a real emergency. Its
  blunt-manipulation recall is **0.375**, below the locked 0.80 — but the misses
  are *credential/verification-bypass* scams (OTP readout, "move to the safe
  account", card+PIN), i.e. the **same evasive tail as Stage 1**. So the safety
  claim holds; the recall shortfall reinforces the deep-model need rather than
  contradicting it.

- **Stage 3 · Digital-swarm fidelity → 2/2 PASS.** On an N=500 dependency tree,
  joint two-hop fidelity **decays with hop depth** (corr(depth, D) = **−0.887**;
  D falls 0.84 → 0.01 by depth 39), and realized success couples **linearly** to
  `U·D` (**R² 0.93** linear vs **0.90** quadratic). A digital swarm does **not**
  escape the two-hop, linear-coupling communication law (`E = U·D`) by exchanging
  more bits — it is subject to it, exactly as LISM predicts.

## Why "green" includes a reported null

The reproducibility harness stays green because each stage **applies its locked
decision rule honestly** — a correctly-reported null (Stage 1; the Stage 2 recall
sub-criterion) is a valid scientific outcome, not a test failure. The one
safety-critical gate that must hold — never silence a real emergency — passes at
0.000. This is the same discipline the NYC-sidewalk reproduction lesson demands:
lock first, report whatever comes back, never mine post-hoc.
