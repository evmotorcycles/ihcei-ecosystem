# EI — Epistemological Intelligence

*An independent, receiver-side layer that sits between models, humans, and nodes
and answers **verifiable** questions — is this claim grounded? is this delegation
in-bounds? is the human still growing or hollowing? is the record intact? is the
queue's enforcement latency drifting? — **without ever censoring or mutating the
token stream.** It informs human judgment; final release stays with the human.*

**Epistemological, not ethical.** EI does not adjudicate morality or "AI safety."
It checks properties that are *verifiable* — fidelity, methodology, grounding,
permission bounds, human engagement (ΔA), enforcement latency (τ_v) — not
contested values. It shifts the locus of trust from the **producer** of content
to the **receiver** of it.

## Not a new engine — a composition of tested primitives

EI adds no unproven model. It wires five already-tested pieces of this repo into
one contract:

| primitive | what it checks | built on |
|---|---|---|
| **AUDIT** | epistemic fidelity — a *mechanism* opens the gate, pressure alone doesn't | `novora-helm` / `page-code` NERE gate |
| **DELEGATE** | stake-bounded, revocable permission (the OAuth of agency); default-deny | `page-code` permission table |
| **DEVELOP** | the human's ΔA — verifying vs blindly accepting; injects friction on hollowing | `novora-helm` capacity meter |
| **PROVE** | a hash-chained, tamper-evident receipt for every decision | `echo` |
| **HAZARD** | τ_v + Dissonance σ compass; throttle when a queue drifts above its baseline | `cross-stack` LISM diagnostic |

Everything on-device, `$0` marginal, no network (privacy by topology), and
**non-suppressive** — `evaluate()` returns advice + a receipt, never a rewrite.

## Tested on real open-source GitHub data

```
node ei/ei.test.mjs        # 17/17
node ei/field_report.mjs   # displays the whole contract
```

On 360 real GitHub commit lines + a live τ_v cohort:

- **AUDIT** — silent on **0/360** real commits (no alarm fatigue), BLOCKs the
  same prose the instant a scam (mechanism + pressure) is injected (`p=0.94`), and
  BLOCKs a force-push-to-main diff.
- **DELEGATE** — allows an in-bounds `src/**` edit; DENYs payments, CI, an
  over-stake action, and any un-granted path (default-deny).
- **DEVELOP** — a blind-deference user reads **ΔA=0 → friction injected** ("explain
  the logic yourself"); an engaged user reads **ΔA=1 → no friction**.
- **HAZARD** — flags `jashkenas/underscore` as a **zombie** (fresh push, τ_v≈77 d,
  σ=+1.69) and throttles.
- **PROVE** — every `evaluate()` is a receipt; a forged verdict is located at the
  exact record.

## The contract

```js
import { EI } from './ei/ei.mjs';
const ei = new EI({ frictionFloor: 0.5 });
ei.grant({ agent: 'claude-code', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 3 });

const v = ei.evaluate({
  text,                       // or change: { message, diff }
  agent: 'claude-code', path: 'src/app.js', action: 'edit', stake: 1,
  engagement: { verified: true, addedOwnReasoning: true },
});
// -> { release: 'release' | 'hold-for-human', audit, delegate, develop, reasons, receipt_id }
```

`release` is **advisory** — the human decides. `ei.verify()` proves the whole
receipt ledger is intact.
