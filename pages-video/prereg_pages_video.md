# Pre-registration — PAGES on the AI-video workflow

Written and hashed **before the run**. 2026-09-13.

---

## What changed today

`huggingface.co` answered **000** for this entire project, which is why
`plexus/hf_preregistration.md` (H1–H7) has stayed UNRUN: it presses the
quantitative sentences of model cards, and no card text was reachable.

Today the Hugging Face connector is live and card text comes back in full.
**Plain `curl` to huggingface.co is still 000** — only the connector reaches it
— so the fetch is an attested manual step and everything downstream runs on a
frozen fixture, the same arrangement `hf-cohort/data/hf_cohort_frozen.json`
already documents.

**H1–H7 is now runnable and is still not run.** It specifies Qwen and DeepSeek
*text-generation* models, not video models. Running it on a different cohort
would not be running it. It is recorded here as unblocked, and left for its own
turn.

## What is being tested

Six real open-source video generators, fetched today:
`Wan-AI/Wan2.2-T2V-A14B`, `tencent/HunyuanVideo`, `Lightricks/LTX-Video`,
`zai-org/CogVideoX-5b`, `genmo/mochi-1-preview`,
`stabilityai/stable-video-diffusion-img2vid-xt`.

PAGES does **not** audit video. It binds a **transcript** to its **sources**:
a temporal hash-chain so a spliced or edited segment breaks the chain at an
exact timestamp, and a Merkle tree so one tap shows the committed source. The
realistic case is the one the market is actually in — a person writes a script
*about* these models, narrates it, and publishes. The sources are the model
cards. The question is whether PAGES catches what goes wrong there.

Four script segments, grounded against verbatim card excerpts:

| | |
|---|---|
| **S1** | a claim that restates its source closely |
| **S2** | a claim carrying a **number that is not in its source** |
| **S3** | a claim about a real model grounded against the **wrong card** |
| **S4** | a claim that is true of the source and loosely worded |

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| P1 | S2 is caught by `addedNumbers`, and its `p_alignment` is capped at **0.25** | ≤ 0.25 |
| P2 | S3 scores low on overlap without any number being fabricated — wrong-source is a *different* failure from invented-figure | not grounded, `addedNumbers` empty |
| P3 | Editing one segment's text after building breaks `verifyStream` at **exactly that index**, and no earlier one | index == the edited one |
| P4 | Deleting a segment (a splice) also breaks the chain | verify fails |
| P5 | `tapToSource` returns the **un-mutated** source and its inclusion proof verifies against the published root | proof verifies |
| P6 | At least one of the four segments is grounded — the instrument is not simply refusing everything | ≥ 1 grounded |

**P2 is the one I am least sure of.** Lexical overlap between two model cards in
the same field may be high enough that a wrong-source attribution still reads
grounded, because both cards talk about diffusion, video, frames and resolution
in the same vocabulary. If P2 fails, PAGES catches invented numbers and splices
but **not** misattribution, and that limit belongs on the box.

---

## Nulls, registered in advance

**NULL-P1.** `groundFast` is lexical overlap plus a number check. It does not
understand either text. A claim that contradicts its source while reusing its
words will read grounded, and that is not a bug to be fixed later — it is the
reach of a word-overlap measure.

**NULL-P2.** The hash chain proves a stream was not edited **after it was
built**. It says nothing about whether the transcript was true when built. A
liar who commits their lie at t=0 gets a chain that verifies perfectly.

**NULL-P3.** Card text was fetched with a byte cap (4,000–9,000 bytes per card)
and the excerpts used as sources are short verbatim passages from within that.
Nothing here characterises the full cards.

**NULL-P4.** Six models chosen by name recognition, not sampled. Nothing
generalises to open-source video generation.

**NULL-P5 — the market null.** Nothing in this run measures whether anybody
making YouTube videos wants provenance, would pay for it, or would ship a video
that shows its sources. That is an adoption question and no arithmetic here
touches it.

---

## What would falsify this

1. **P3 or P4 fails** — the chain does not localise an edit, and the central
   claim of the temporal structure is wrong.
2. **P1 fails** — a fabricated statistic passes, which is the single most common
   failure in generated media narration.
3. **P6 fails** — nothing is ever grounded, so the instrument is useless rather
   than strict.
