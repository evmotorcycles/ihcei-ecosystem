# ASSAY — the browser EI LLM, plus Page Code and HELM dashboards

**One command:** `node ei-dashboards/assay_run.mjs` · offline · `$0` · deterministic
**Then open:** `ei-dashboards/dashboards.html` — straight from disk. No server, no network.

---

## The name

The browser-run EI LLM is **ASSAY**.

An *assay* determines what a sample **actually contains**, independently of what its label
claims. That is exactly this stack's founding rule — `F_out = F_eval`, judge the measured
behaviour and ignore the self-report. It works as a verb too ("assay this claim"), it fits a
browser tab, and it isn't a generic AI product name.

---

## What the Novora stack is actually for

**One problem:** *you cannot tell whether software, a model, or a claim is trustworthy by
looking at how popular it is.* Every component exists to measure **verified behaviour**
instead of **reported reputation**.

| component | the question it answers |
|---|---|
| **NERE / IHCEI** | Is the reasoning exposed and gated, or is this a black box? |
| **Novora PAGES** | Does this text carry gradable evidence — and if not, will it **abstain** instead of bluffing? |
| **Page Code** | Is this agent permitted to change *this exact path*, at *this stake*? |
| **Echo** | Can this verdict be re-checked later by someone who trusts nobody involved? |
| **EI** | Does the whole transaction **expand** the human's options rather than replace their judgement? |
| **Agency** | Where should limited repair budget go — the weakest link, or the loudest one? |

---

## The cohort: 22 real Qwen + DeepSeek repositories

Fetched live from the GitHub REST API on 2026-08-06 and frozen:
**10 from `QwenLM` (Alibaba) + 12 from `deepseek-ai`**, all with >500 stars — real `stars`,
`forks`, `open_issues`, `license`, `created`, `pushed`, `archived`.

> **Honest data note.** The Hugging Face connector dropped mid-session, so this cohort is
> **GitHub-only**. Qwen models *do* appear in previously frozen HF fixtures (3 in `hf-cohort`,
> 1 in `hf-media`) and are cited as-is — **no new Hugging Face data is claimed, and nothing was
> fabricated to fill the gap.**

Every gate calls the **real committed module**, not a reimplementation.

---

## Results — pre-registered D1–D8 (spec `7bb44ce7…`)

### D1 — PAGES abstains instead of bluffing ✓ (and a genuine finding)
```
empty input                   → "Insufficient Evidence"   abstain = true
evidence-bearing control text → gradable verdict          abstain = false
REAL: PAGES abstained on 22/22 actual repository descriptions
```
It abstained on **every real repo description** — because repo descriptions are *marketing
blurbs*, not evidence. That is **correct behaviour**, and the labelled control proves PAGES is
*cautious, not broken*: give it method + numbers + a checkable source and it grades normally.

### D2 — Page Code is deterministic and default-deny ✓
All 22 descriptions audited twice → **byte-identical**. `docs/**` granted → **allow**;
ungranted `src/core.mjs` → **deny**; stake 99 against a cap of 5 → **deny**.

### D3 — Echo is tamper-evident ✓
Merkle root over all 22 repos; **every leaf proves inclusion**. Change **one star count by 1**
→ the root changes and the old proof is **rejected**.

### D4 — EI is accountable ✓
22 evaluations → **22 receipts**, ledger verifies. Every verdict can be re-examined later.

### D5 — the Agency allocator beats naive ✓
22/22 below the collapse floor, budget 66: **constitution 16.92** vs capacity 14.28 vs equal 6.55.

### D6 — "reach is not quality" **REPLICATES** ✓
On this fresh, independent cohort the star ranking differs from the verified-fidelity ranking,
and **all 5 of the top-5 most-starred repositories fall below the fidelity floor** — including
`DeepSeek-V3` (104k stars) and `DeepSeek-R1` (92k stars). The surviving finding from PR #111
reproduces on data it was never derived from.

### D7 — a real governance gap (descriptive)
**2 of 22 repositories publish no license at all:** `QwenLM/Qwen3` and `QwenLM/Qwen3-Coder`.
`Qwen3` has **27,483 stars and no license** — a genuine downstream-reuse hazard that popularity
completely hides. This is exactly the kind of thing prestige-ranking misses.

### D8 — the dashboards are genuinely offline ✓
One self-contained 12.9 KB HTML file, **zero external resources**, with this run's measured
numbers embedded at build time. Three tabs: **ASSAY**, **Page Code**, **HELM**.

---

## What this is *not*

This measures **repository governance telemetry only**. It does **not** evaluate Qwen or
DeepSeek model quality, does **not** benchmark their capabilities, and makes **no claim about
which lab is better**. "Below floor" is a statement about backlog health and fork-through
relative to popularity — not about whether a model is any good.

## Files

```
ei-dashboards/
  prereg/assay_prereg.json        spec (locked before running) — gates D1–D8 + the naming rationale
  prereg/MANIFEST.sha256.json      spec + frozen cohort, hash-pinned
  data/qwen_deepseek_frozen.json   22 real repos, live GitHub REST API, frozen
  assay_run.mjs                    runs the REAL stack modules + builds the dashboards
  assay.test.mjs                   node:test guard (locks the replication and the licence gap)
  dashboards.html                  ← open this in a browser (built artifact)
  results_assay.json               emitted results
```

Offline, `$0`, deterministic. Methodology, not speed.
