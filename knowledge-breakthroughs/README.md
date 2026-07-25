# What actually makes knowledge propagate — and the pre-registered thesis that turned out to be wrong

**One command:** `python3 knowledge-breakthroughs/knowledge.py` · stdlib · offline · `$0`

Modern practice accelerates **search** — brute-forcing billions of candidates. The claim tested
here is *prior to speed*: that raw **status** (reputation, stars, likes, field size, team size) is
inert on its own, and that realized knowledge yield is **produced** by a two-hop fidelity channel
`E = U · D_enc · D_dec`. If true, you must **secure the channel before you apply speed** —
otherwise speed only propagates noise faster.

**The central pre-registered prediction was falsified.** That is the headline, and it is reported
here at full force, locked into the test suite so it cannot quietly become a win.

> **Terminology:** functional/engineering meanings only — capacity/status `U`, encoding fidelity
> `D_enc`, decoding fidelity `D_dec`, realized yield `E`, two-source independence (VIF), decoupled
> evaluation. No cultural or religious lexicon.

---

## ⚠ Data-integrity disclosure (read before the results)

The four substrates carrying the empirical gates are **real and frozen**: GitHub (28 repos),
Hugging Face (19 models), bioRxiv (40 preprints), PubMed (8 clinical fields).

**The N=793 "knowledge cohort" fixture committed in this repository is SYNTHETIC.** Its own
provenance block reads `synthetic: true, seed: 20260720, ground_truth: "additive linear latent,
no D²; hops independent"`. It is used here **only** as a labelled **estimator positive control**
— it validates that the measurement code recovers a known ground truth — and it contributes
**zero real-world evidence**. Any narrative citing this committed fixture as a real Stack Exchange
measurement (e.g. "Cohort C, N=793 pooled threads, VIF 1.08, AUC 0.58") is **not supported by
what is in this repo**, and that correction is made here rather than glossed over.

---

## Results — pre-registered K1–K5 (spec `5d468f9e…`)

### K1 — the central thesis: **FALSIFIED** ❌
Does fidelity-adjusted capacity explain realized yield better than raw status alone?

| substrate | ρ(status alone) | ρ(fidelity-adjusted) | verdict |
|---|---:|---:|---|
| **Hugging Face** (likes → downloads, N=19) | **+0.4035** | +0.0123 | status wins |
| **GitHub** (stars → forks, N=28, non-circular leg) | **+0.8763** | +0.5140 | status wins |

The prediction was `ρ(adjusted) > ρ(status)`. **It is false on both real substrates.**

**Diagnosis — stated, not a rescue.** The yield proxies available (**downloads**, **forks**) are
*themselves popularity measures*, so popularity predicts popularity. The fidelity legs — license
clarity, evaluation evidence, backlog health — measure **trustworthiness**, a genuinely
*different* axis. **The thesis conflated reach with verified quality.** What survives is the
weaker, correct claim, and K4 tests it directly.

### K2 — independence gate: **PARTIAL** ⚠
```
VIF(D_enc, D_dec)   Hugging Face 1.0647 ✓ intact      GitHub 1.1741 ✗ exceeds the pre-registered 1.10
self-certifying control (D_dec := D_enc) → VIF = ∞ → REJECTED ✓
```
Hugging Face's channel is intact. **GitHub fails the gate as written** — under this substrate's
non-circular leg definition, backlog health shares some variance with fork-through (r ≈ 0.39).
It remains far below the standard 5.0 collinearity gate, but **1.174 > 1.10, so the gate is not
met and the threshold was not moved.** *Declared up front:* bioRxiv and PubMed are single-leg
substrates, so the independence gate is **untestable** there.

### K3 — capacity does not buy fidelity: **CONFIRMED** ✓
```
PubMed  (field size vs integrity,        N=8):  ρ = +0.1905   [small-N limit declared]
bioRxiv (team size  vs latency fidelity, N=40): ρ = −0.0930   [survivor-only cohort]
```
Neither shows a strong positive coupling. **Being bigger or better-resourced does not, by itself,
buy channel fidelity** — the one part of the "status is inert" reading that the real data supports.

### K4 — prestige ordering ≠ verified ordering: **CONFIRMED** ✓
```
Hugging Face: rankings differ ✓ ; 1 of the top-5 by status is BELOW the fidelity floor (coqui/XTTS-v2)
GitHub:       5 of the top-5 by stars are below the fidelity floor
              (the-book-of-secret-knowledge, tensorflow, stable-diffusion-webui, …)
```
**All five of GitHub's most-starred repositories sit below the fidelity floor.** Ranking by
prestige produces a genuinely different ordering than ranking by verified fidelity — so a network
that allocates by prestige does not allocate by quality.

### K5 — estimator positive control (synthetic, no real-world claim) ✓
On the synthetic N=793 fixture whose declared ground truth is *"hops independent"*, the estimator
recovers **VIF = 1.0032 < 1.10**. This validates the measurement code **only**.

---

## The honest headline

The pre-registered thesis is **false on real data**: status predicts *reach* better than
fidelity-adjusted capacity does, because the available reach proxies **are** popularity measures.
What survives — and is confirmed on real substrates — is sharper and more useful:

1. **Capacity alone does not buy fidelity** (K3).
2. **Reach and trustworthiness are separate axes** (K4) — measurably different orderings, with
   every one of GitHub's top-5 most-starred repos below the fidelity floor.

So the governance conclusion stands, but for a corrected reason: **you cannot read quality off
popularity**, which is exactly why an evaluator must measure fidelity separately (`F_out = F_eval`).
The original framing — that fidelity would out-predict status on yield — is retracted. **Nothing
was retuned; the falsification is asserted in `test_knowledge.py` so it stays in the record.**

*Precedent in this repo: the openalex-lism null (PR #100) and the agency-constitution Law-2
falsification (PR #107). A confirmed null is a valid reproduced outcome — `exit 0` here means
"reproduces exactly as pre-registered, including its nulls," not "the thesis was supported."*

## Files

```
knowledge-breakthroughs/
  prereg/knowledge_prereg.json     spec (locked) — gates K1–K5 + the data-integrity disclosure
  prereg/MANIFEST.sha256.json       spec + 5 fixtures, hash-pinned
  knowledge.py                      the runner (Spearman / VIF, stdlib)
  test_knowledge.py                 pytest guard — locks the FALSIFICATION and the PARTIAL too
  results_knowledge.json            emitted results
```

Layer-1, offline, `$0`, deterministic. Methodology, not speed. Nulls prioritized — this time the
null *was* the result.
