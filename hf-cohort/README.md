# Hugging Face cohort — governance + digital-swarm tests

Pre-registered, reproducible, offline (`$0`, no keys) tests of the Novora stack against
**real Hugging Face open-source models**. The cohort is fetched live from the HF Hub, then
**frozen to a SHA-256-locked fixture** so every test reproduces without the network — the
same pattern as the GitHub `N=992` arm.

```bash
node   hf-cohort/run_hf_governance.mjs         # governance audit (real modules on real HF data)
python3 hf-cohort/swarm/hf_swarm.py            # digital-swarm E=U*D + revocation latency
python3 -m pytest -q hf-cohort/swarm/test_hf_swarm.py
node --test hf-cohort/hf.test.mjs
```

Both are wired into `bash reproduce_all.sh`. Provenance: `python3 provenance/verify_provenance.py`.

---

## Data — `data/hf_cohort_frozen.json`

24 top-trending HF models (real metadata: task, downloads, likes, license, `custom_code`,
`arxiv`, `eval_results`, `base_model` lineage, safety flags), fetched via the HF MCP
(authenticated user `Mago1234`) and frozen. Fixture hash `537bfb3d…`; the governance spec
hash is `e3f422a3…`, the swarm spec hash is `913f4d03…`. Locks are re-verified before each run.

## Test 1 — Governance audit (`run_hf_governance.mjs`)

Runs the **real merged modules** (not reimplementations) over every model:

| Module | What it does | Result on the 24-model cohort |
|---|---|---|
| **HELM / EI / NERE** `audit()` | governance verdict on the card text | 10 PASS / 11 REVIEW / **3 FLAG** (the flagged are self-labelled uncensored/heretic/abliterated) |
| **Novora suite** PAGES `screen()` | grounding score | uniform **~0.49** — honest: PAGES scores card *prose* (methodology, N=, p-values); tag metadata lacks it |
| **Page Code** `CodePermissionTable` | publish-listing permission | **13/24** earn `allow` (clear license + provenance + not flagged) |
| **Echo Database** `EchoDB` + Merkle | tamper-evident ledger | 24 records hash-chained; single-byte tamper **caught & located**; deterministic root |
| **Agency Internet** | base_model lineage | `Qwen/Qwen3.6-27B` has **4 dependents**; revocable delegation |

**Honest limitation:** PAGES needs the real card *prose* (with actual `N=`/`p<` numbers) to
discriminate; on tag metadata it reads every card as "partially grounded." We do **not**
invent benchmark numbers — the discriminating signal here is HELM + Page Code.

## Test 2 — Digital-swarm `E = U·D` + revocation latency (`swarm/hf_swarm.py`)

Three pre-registered arms (spec `913f4d03…`):

- **A1 · Real HF lineage forest (honestly underpowered).** `E = U·D` on the real 24-model
  lineage with a `has_descendant` adoption proxy. `N=24` is far too small for a valid
  coupling test → reported **INCONCLUSIVE**, not mined. *(A true survival study needs
  12-month download data we do not have; we do not fabricate it.)*
- **A2 · Digital-swarm on HF-calibrated topology (seeded simulation, N=500).** Grows a
  dependency tree seeded on the real HF branching (hubs like Qwen spawn many
  quantizations/finetunes) with capacity `U` seeded from the real download distribution.
  - **DECAY: confirmed** — joint fidelity `∏Dᵢ` decays down lineage depth (**corr −0.89**,
    0.84→0.01 over 25 hops). A quantize/finetune swarm bleeds fidelity, same as the GitHub /
    yeast / knowledge cohorts.
  - **COUPLING: honest null here** — with `U` seeded from the real, heavily-skewed HF
    download distribution (per the locked spec), the linear-vs-quadratic contrast was
    **inconclusive** (R² 0.73 vs 0.75, both weak). We do **not** retune `U` post-hoc to force
    linear to win; the `E=U·D` coupling is *not confirmed on this HF-capacity distribution* —
    reported at full force (symmetric-null discipline).
- **A3 · Revocation latency (τ_v) on the real Qwen hub.** Revoke the base; propagate a halt
  through dependents via the circuit breaker + Echo certificate. **All 12 nodes below the hub
  halt; τ_v = 4 hops** (deeper chains take proportionally longer). No dependent is left running
  on a revoked base — the safety-critical property.

**Green = honest application of the locked rules + the revocation halt** (the load-bearing
safety result) + the confirmed decay. A reported null (A1 underpowered, A2 coupling) is a
valid outcome, not a failure.

## What is deliberately NOT claimed

- No claim that the stack *improves* any model — this is audit/governance telemetry.
- No moralizing — "uncensored" is surfaced as a flag, not a judgement.
- **LMD is not applied to HF metadata** (it's a physics toy about distance-from-latency).
- The `E=U·D` **coupling** is *not* asserted on HF — the honest result was inconclusive on
  HF-skewed capacity. What HF *does* confirm is multi-hop fidelity **decay** and revocation
  propagation. Full write-up: `../lism-cohorts/README.md` (the four validated cohorts).

## Future work (needs network / would change the fixture hash)

- **PAGES prose audit:** crawl the real model-card prose + linked arXiv PDFs so PAGES scores
  actual methodology text (not tags). Requires network; not offline-reproducible today.
- **Longitudinal survival `E`:** re-fetch the cohort's download rates over 12 months to get a
  non-circular survival outcome for a genuine `E=U·D` *survival* test (Arm A1 done properly).
