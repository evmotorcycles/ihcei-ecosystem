# Pre-registration — the 22-repo cohort is 2 origins, not 22

Written and hashed before the arithmetic was run. This is a SECOND, smaller
question, registered because the first one could not be run at all — see
`HF_NULL.md` for that.

## Why this question

`ei-dashboards/data/qwen_deepseek_frozen.json` holds 22 real Qwen and DeepSeek
projects and is used as a cohort elsewhere in this repository. Twenty-two
projects reads as twenty-two observations. They come from exactly two
organisations.

That is the shape this repository has now met six times, and it is worth
pointing at a cohort we use ourselves rather than only at other people's work.
Press each repository as a mark hanging off the organisation that publishes it,
and ask what any single repository settles.

## Predictions

| # | Prediction | Value |
|---|---|---|
| C1 | Distinct organisations in the cohort | exactly 2 |
| C2 | The split, deepseek-ai / QwenLM | 12 / 10 |
| C3 | Both organisations are cut points — remove one and its repositories cannot reach the rest | both |
| C4 | Each deepseek-ai repository settles | 0.003498 |
| C5 | Each QwenLM repository settles | 0.004962 |
| C6 | Every repository settles less than 1/22 = 0.045455, the figure a naive count implies | all below |
| C7 | Bearings conserve: total = parts − pieces | exact |

C2 is the one I am least sure of and it is a count I could have made wrong.

## Nulls

**NULL-C1.** This says nothing about the quality of any repository, either
organisation, or the cohort's fitness for the use `plumb` already makes of it —
which is marked descriptive-only there for its own separate reasons.

**NULL-C2.** "Two origins" is a fact about who publishes, not about whether the
engineering is correlated. Two labs can make genuinely independent choices. The
arithmetic reads the publishing structure and nothing else.

**NULL-C3.** Nothing here was fetched. This is the frozen file already in the
repository, and its own provenance block governs when it was taken.
