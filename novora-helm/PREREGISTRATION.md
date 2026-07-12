# PRE-REGISTRATION — On-Device Deep Mode & Emergency-Safety at Scale

**Status: LOCKED 2026-07-11 (before any distillation training or corpus
expansion). GT v18.2.** This document fixes the corpora, metrics, and pass/fail
bands *in advance*, so the result cannot be moved by choosing the analysis after
seeing the data. One spec, **two claims**, both able to return a meaningful
**null**. Nulls are deliverables: each has a named consequence written here
before the fact.

> **Why pre-register.** The ambient layer's entire economics rest on one bet —
> that a small on-device model can do the semantic evidence step at ambient
> precision. If we tune thresholds after training, we will "prove" whatever we
> built. Locking the bands now is the only way the test can actually fail.

---

## 0. What is frozen by this document

1. Three corpora (§1), authored/expanded and then **hashed and frozen** before
   any model touches them. The hash is recorded in `corpora/MANIFEST.sha256`.
2. A train/test split rule (§1.4) — the acceptance corpora are **held out**; no
   item in them may appear in distillation training or few-shot prompts.
3. Two claims with primary endpoints and acceptance bands (§2, §3).
4. The analysis plan and stopping rule (§4). No metric, band, or corpus may
   change after the manifest hash is written except by a dated amendment that
   *precedes* seeing test results.

## 1. Frozen corpora

All items are single messages in the same schema as `validation_corpus.py`.
Labels are authored with a rubric (§1.5) and double-checked by an independent
pass; disagreements are resolved *before* freezing or the item is dropped.

### 1.1 EVASIVE-COERCION (target n ≥ 300)
Reworded manipulation that carries a real mechanism but *avoids the fast-mode
keywords*. Every item must contain at least one genuine mechanism (bypass,
unverifiable authority, manufactured consensus, complexity-deflection,
isolation) expressed **without** the surface trigger words. This is the corpus
fast mode scores ~0.125 on today; it is the reason deep mode exists.

### 1.2 EMERGENCY (expanded, powered baseline n ≥ 400 — Amendment A1)
Legitimate urgent messages with **no** manipulation mechanism, hand-labeled and
high-intensity. This is the tail where an average false-positive rate lies.
Stratified across four high-stress classes, no stratum exceeding 30% — a model
that only learns "reactor" does not pass:
1. *SRE / infrastructure incidents* — failovers, pager alerts, active
   ransomware mitigation.
2. *High-acuity clinical / medical directives* — triage codes, critical dosing,
   emergency-room calls.
3. *Physical safety / natural hazards* — active threat, evacuation, weather.
4. *Hard-deadline administrative* — compliance halts, trading freezes,
   statutory filings.

### 1.3 CONSUMER-SCAM (target n ≥ 300)
Real-world consumer manipulation: grandparent/impersonation scams, "account
suspended / pay in gift cards", delivery-fee phishing, romance-scam openers,
dark-pattern checkouts (scarcity + fake social proof). Every item carries a
consumer-v1 mechanism (secrecy, payment-pressure, impersonation, scarcity).

### 1.4 Split rule
Each corpus is split **70/30** by a seeded hash of the item id. The **30% test
split of each corpus is the acceptance set** and is *sealed*: it may not be
inspected, used in training, used to pick few-shot exemplars, or used to select
a checkpoint. Checkpoint selection uses the **train split only**. The acceptance
set is run **once**, at the end, on the single frozen checkpoint.

### 1.5 Label rubric (authored before items)
- **manipulative** iff a reasonable person would judge the message is trying to
  override the receiver's judgement via a mechanism, not inform it.
- **legitimate-urgent** iff the urgency is real and the message *invites*
  verification (or is neutral to it) rather than suppressing it.
- Ambiguous items (cannot be assigned by the rubric) are **dropped**, not
  guessed — recorded in `corpora/DROPPED.md` with the reason.

## 2. CLAIM A — On-device deep mode catches evasive coercion at ambient precision

**Hypothesis.** A distilled ~1–3B on-device extractor, feeding the *unchanged*
posterior kernel, raises evasive-coercion recall far above fast mode **without**
sacrificing emergency-safety or clean precision.

**Primary endpoint (both must hold on the sealed acceptance sets):**

| # | metric | corpus | fast-mode baseline | **acceptance band (deep)** |
|---|---|---|---|---|
| A1 | evasive-coercion recall (HOLD or WARN) | EVASIVE test | ~0.125 | **≥ 0.70** |
| A2 | emergency **false-HOLD** rate | EMERGENCY test | 0.000 (seed) | **≤ 0.02** |

**Secondary (reported, not gating):** evasive HOLD-rate (BLOCK only) ≥ 0.40;
consumer-scam recall ≥ 0.85; clean-benign false-positive ≤ 0.02; per-class
recall table for all three corpora; calibration (Brier, ECE 5-bin) deep vs fast.

**Decision:**
- **Supported** iff A1 ≥ 0.70 **and** A2 ≤ 0.02 on the acceptance sets.
- **NULL (claim retired)** if A1 < 0.70, *or* if A2 > 0.02 (buying recall by
  re-breaking emergencies is a failure, not a trade). **Consequence, written in
  advance:** the *ambient deep-mode* claim (design §3, §10) is retired to
  `HYPOTHESIS → RETIRED_FULLY`. HELM ships and stays as **fast mode + the four
  primitives**; the README's "the bet" section becomes the shipped ceiling, and
  we do **not** claim reworded-coercion coverage on-device.
- **Partial** (A2 holds, 0.50 ≤ A1 < 0.70) is reported as `SUPPORTED-BY-PROXY`
  only if a *cloud* deep run on the same acceptance set clears 0.70 — proving
  the extractor, not yet the on-device distillation. It does not license the
  ambient (default-on, on-device) claim.

## 3. CLAIM B — Emergency-safety holds at scale

**Hypothesis.** The corroboration gate's 0.50 → 0.00 emergency false-HOLD result
was not an artifact of the tens-of-items seed corpus; it holds on EMERGENCY
(n ≥ 500), in **both** fast mode and deep mode.

**Primary endpoint (both engines, sealed EMERGENCY acceptance set):**

| # | metric | **acceptance band (Amendment A1)** |
|---|---|---|
| B1 | fast-mode emergency **false-BLOCK** | **≤ 0.005** (0.5%) |
| B2 | fast-mode emergency false-BLOCK, **worst-performing stratum** | **≤ 0.02** |

**Decision:**
- **Supported** iff B1 ≤ 0.005 and B2 ≤ 0.02.
- **NULL** if B1 > 0.005 or any stratum exceeds 0.02. **Consequence, written in
  advance:** ambient **default-on** is blocked (design Risk 2). HELM ships
  **default-silent / opt-in-per-surface** until the gate is re-worked and
  re-passes this same locked spec. The 0.00 seed number is demoted to
  "seed-only, did not replicate at scale" in `VALIDATION.md`.

## 4. Analysis plan & guardrails

- **One-shot acceptance.** The sealed 30% sets are scored exactly once, on one
  pre-committed checkpoint per engine. No checkpoint shopping.
- **Fixed kernel.** The posterior math (`posterior`, `band`, floor `[0.01,
  0.99]`, BLOCK = mean ≥ 0.85 ∧ CI-low ≥ 0.50) is **not** tuned for this test.
  Only the evidence extractor changes (the fast/deep seam). Any kernel change
  voids the pre-registration and requires a new lock.
- **Lexicon parity.** Deep-mode extraction must expose the same mechanism set as
  enterprise-v1 / consumer-v1 (incl. isolation and scrutiny-suppression), so the
  `mechanism_lexicon` stamp means the same thing in both modes.
- **Reproducibility.** Seeds fixed (Monte-Carlo seed 7, split seed recorded in
  the manifest). Every acceptance run emits per-item `{id, p, ci, verdict,
  mechanism_present, mechanism_lexicon}` and a hash of the corpus it ran on.
- **Multiplicity.** Two claims, four primary endpoints. Each is evaluated
  against its own pre-set band; we do not convert a partial pass on one into
  support for another.
- **Amendments.** Any change before results are seen must be a dated entry in
  §5 that explains why; changes after seeing results are not permitted and would
  invalidate the claim.

## 5. Amendment log

- **A1 — 2026-07-12 (pre-results; no training run, no corpus frozen yet, no
  acceptance data seen).** (1) Emergency corpus re-specified as a powered
  baseline **n ≥ 400** stratified across four named high-stress classes (max
  30% per stratum), replacing the looser "n ≥ 500, no domain > 25%". (2) Claim
  B primary endpoint tightened from false-HOLD ≤ 0.02 to **false-BLOCK ≤ 0.005
  (0.5%)** overall, worst stratum ≤ 0.02 — matching the deployment-grade rate
  already measured on the real-world OSS run and required before default-on for
  on-call engineers, paramedics, and infrastructure operators. (3) The full
  protocol is now also machine-readable: `prereg/stage1_spec.json`, with NPU
  constraints (1–3B params, int8/int4, p50 ≤ 150 ms / p95 ≤ 400 ms, ≤ 4 GB),
  calibration targets (Brier ≤ 0.15, ECE ≤ 0.10, secondary), split seed
  20260711, and checkpoint rule. **Specification hash (canonical, recursive
  key-sorted):**
  `sha256: 0f047b962189680c280a1b8cca4c0edd2d9f32d90f759964736adddb815fc0fd`
  (raw file: `68bc02dc…d6ae1`, full value in `prereg/MANIFEST.sha256`). Any
  change to the JSON after this entry invalidates the pre-registration.

---

### Summary

Two bets, priced honestly and in advance:

1. **Ambient deep mode** must reach **evasive recall ≥ 0.70 while keeping
   emergency false-HOLD ≤ 0.02**, or the ambient-deep claim is retired and HELM
   remains fast-mode + four primitives.
2. **Emergency-safety** must replicate on the powered n ≥ 400 stratified corpus
   with **≤ 0.005 overall and ≤ 0.02 worst-stratum false-BLOCK**, or ambient
   default-on is blocked.

Either can return a meaningful null. Both nulls have a written, pre-committed
consequence. That is the difference between a test and a demo.
