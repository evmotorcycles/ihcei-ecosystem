# Pre-registration — the 24-model HF fixture, at the metadata level

Locked before any distribution was computed. What had been seen when this was
written: the field names, and one record (`thinkingmachines/Inkling`:
`arxiv: false`, `eval_results: true`, `base_model: null`), and the list of 24
ids. Nothing else.

## Why this is a SECOND question, not the first one

`hf_preregistration.md` (sha256 `ebe1366f…65adf87`) asks seven questions about
the **text** of model cards. `hf-cohort/data/hf_cohort_frozen.json` holds
metadata — task, downloads, licence, `custom_code`, `arxiv`, `eval_results`,
`base_model`, flags — and **no card text at all**. So H1 to H7 remain unrun and
that pre-registration stays locked and unedited. This asks what the metadata
alone can answer.

## Predictions

| # | Prediction | Value |
|---|---|---|
| G1 | Share of models reporting evaluation results **and** having no arXiv reference — numbers with no paper a third party can open | ≥ 0.50 |
| G2 | Share with an arXiv reference at all | ≤ 0.35 |
| G3 | Share with `base_model` absent — the field that would show what a model descends from is empty | ≥ 0.50 |
| G4 | Distinct declared origins (base models plus models declaring none) is **fewer than 24** | < 24 |
| G5 | Pressing each model as a mark on its declared origin, every model settles less than 1/24 | < 0.041667 |
| G6 | At least one model carries a safety flag | ≥ 1 |

G1 is the one that matters: it is the press finding at the metadata level —
figures reported, and nothing named that a reader could open instead of asking
the authors. G3 is the null I expect and would rather be wrong about.

## Nulls

**NULL-G1.** `eval_results` and `arxiv` are booleans on a hub listing. They say
whether a field is populated, not whether the evaluation was sound or the paper
says what the card claims. This is a much weaker instrument than pressing the
text would be, and it is not a substitute for it.

**NULL-G2.** A model without an arXiv reference is not thereby unreliable, and a
model with one is not thereby reliable. Publishing without a paper is normal.

**NULL-G3.** 24 trending models on one day is not a sample of anything wider.

**NULL-G4.** This cohort is not Qwen-and-DeepSeek-specific; it is top-trending
models, several of which are Qwen derivatives by third parties. The
Qwen/DeepSeek-specific frozen cohort is the separate 22-repo GitHub file already
reported on.
