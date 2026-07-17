# EI LLM — a receiver-side attestation & verification layer

An **EI LLM** does not generate tokens and does not compete with a generator. It
sits independently between models, humans, and nodes and answers *verifiable*
questions — is this claim grounded? is this delegation in-bounds? is the human
still growing? is the record intact? is this queue saturating? — **without ever
censoring or mutating a token stream.** Final release always stays with the human.

It adds **no new unproven engine.** It is a *policy layer* over the five EI
primitives already tested in `ei/` (`AUDIT, DELEGATE, DEVELOP, PROVE, HAZARD`),
wired into the two model families the architecture calls for.

```
node ei-llm/field_test.mjs          # 17/17 checks, real 22-repo GitHub cohort
node --test ei-llm/ei-llm.test.mjs  # 9/9 unit tests
```

## The two families (8 models)

| Model | Family | Primitives | Targeted failure mode | How it is tested here |
|---|---|---|---|---|
| **Veridian PAGES** | Deep | AUDIT & PROVE | multimodal fidelity loss, deepfakes | hop-hash chain localises a spliced frame at the exact `t` |
| **Veridian SENTRY** | Deep | HAZARD | swarm-queue saturation, cascades | τ_v/σ compass on **22 real repos**: throttles, flags 4 zombies, holds third law |
| **Veridian VITALIS** | Deep | DELEGATE | clinician cognitive hollowing | no record write until the physician audits the evidence path |
| **Veridian CHARTER** | Deep | AUDIT | circular consensus, legal hallucination | detects a closed citation loop; requires a reachable primary source |
| **Apex PAGE CODE** | Edge | DELEGATE & PROVE | opaque vibe-coding, un-reviewed agent actions | in-scope edit allowed; **force-push & secret edits denied**; all attested |
| **Apex ASCENT** | Edge | DEVELOP | human deskilling, tool dependency | injects friction only when ΔA turns to substitution |
| **Apex SHIELD** | Edge | AUDIT | cloned-voice scams, alarm fatigue | **conjunctive** gate: alarms on manipulation, silent on benign urgency |
| **Apex SCALE** | Edge | AUDIT & DEVELOP | the expert trap, decision pressure | multi-path table, calibrated posteriors that sum to 1 |

**Veridian** is the deep-audit family (offline/batch, ~4 GB via sequential layer
loading). **Apex** is the edge family (on-device, ≤4 GB, `$0` marginal, zero
network — privacy by topology). Both are receiver-side and non-suppressive.

## Field-test results (real GitHub telemetry)

```
 VERIDIAN/SENTRY — SRE τ_v/σ compass on 22 real repos
   throttle=true  worst τ_v=251.3d  load=1.00  zombies=[less.js, underscore, backbone, gatsby]
   third-law τ_v: survived 26.5d (n=16) vs failed 101.7d (n=6) → survived-close-faster=true
 APEX/PAGE_CODE   edit src/util.js → allow   force-push → deny   edit .env → deny
 VERIDIAN/PAGES   tamper verify → intact=false at t=1   (deepfaked frame localised)
 VERIDIAN/CHARTER grounded doc → GROUNDED   circular doc → FLAG (1 loop)
 APEX/SHIELD      scam → alarm=true (p=0.98)   benign urgency → alarm=false
 APEX/ASCENT      outsourcing trajectory → trend=substituting, friction=true
 VERIDIAN/VITALIS not-audited → hold   audited → commit-to-record
 APEX/SCALE       3 paths, posteriors [0.50, 0.30, 0.20] (sum 1.00)
 SHARED LEDGER    5 receipts, hash chain intact=true
 RESULT: 17/17 EI-LLM field checks passed across all 8 models
```

The whole point: every model **calibrates and records**, none of them **censor**.
The one shared, hash-chained receipt ledger makes every decision tamper-evident.

## Files
- `ei-llm.mjs` — the 8 models + `EILLM` router over a shared EI core.
- `field_test.mjs` — the real-cohort field harness (SENTRY runs on the 22 repos).
- `ei-llm.test.mjs` — `node --test` unit suite (9/9).
