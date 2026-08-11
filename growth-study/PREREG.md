# Pre-registration — how AI projects changed, and what that does not tell us

**SHA-256 locked in `prereg.lock.json` BEFORE the statistics were computed.**
Re-verified by `test_growth.py`.

---

## 0. The question that was asked, and the two halves of it

The request was: *study how AI grew at first and how it is growing now, verify it
on open-source projects from GitHub and Hugging Face, and use that to see how
Cairn, Trig, HELM, Page Code and the Novora suite will grow.*

That is two questions with very different answerability.

**The first half is measurable, narrowly.** I have 50 real GitHub repositories with
creation dates and 43 real Hugging Face models, all committed. I can measure how
their properties differ by era, and whether the material a governance tool would
need actually exists in them.

**The second half is not answerable at all, and no dataset changes that.**
Forecasting the adoption of tools that currently have no users is not a
measurement, it is a projection. Nothing in this repository — or in any repository
— can produce it. **This study makes no growth forecast for any tool, and any
number that looked like one would be invented.** What it can do is measure the
*precondition*: whether the evidence these tools consume is present in the wild.

---

## 1. The confound that dominates everything below

**Survivorship.** Every cohort here contains projects that still exist. Projects
that were created and died are absent — invisibly, and not at random.

This is not a caveat, it is a structural limit:

> A cohort of survivors can describe what survived. It cannot estimate a growth
> rate, a failure rate, or a trend in the population, because the denominator was
> deleted before the data was collected.

So the predictions below are deliberately about **composition** ("what do
surviving projects of era X look like") and never about **rate** ("how fast did
the field grow"). Any reader who takes a composition result as a growth rate has
been misled, and this file says so in advance so that they cannot be.

---

## 2. Cohorts

| Cohort | N | Source | Fields used |
|---|---|---|---|
| **GitHub A** | 22 | `ei-dashboards/data/qwen_deepseek_frozen.json` | created, stars, forks, open_issues |
| **GitHub B** | 28 | `github-lism/data/github_cohort_frozen.json` | created, stars, forks, open_issues |
| **HF A** | 24 | `hf-cohort/data/hf_cohort_frozen.json` | arxiv, eval_results, license, downloads, likes |
| **HF B** | 19 | `hf-media/data/hf_media_cohort_frozen.json` | arxiv, eval_results, license, downloads, likes |

All four are already committed and already used elsewhere in this repository. No
new collection, no network.

**Era split, declared now:** *early* = created before 2023-01-01, *recent* =
created on or after. The date is chosen because it is the boundary the request
itself proposed (assistant era → agent era), not because it optimises anything.

---

## 3. Pre-registered predictions

### G1 — Composition changed between eras (GitHub, N=50)
Recent projects differ from earlier ones in the two fidelity legs used throughout
this project: `D_enc = 1/(1+open_issues)` and `D_dec = forks/stars`.

- **Gate:** a two-sided permutation test on the difference in mean `D_dec`
  between eras, 10,000 shuffles, seed 42. **SUPPORTED** if `p < 0.05`.
- **Falsified** if `p ≥ 0.05` — meaning surviving projects look much the same
  whenever they were started, which would be a real and interesting negative.

### G2 — Capacity rises with age (GitHub, N=50) · **a control, expected to hold**
Older surviving projects have more accumulated capacity (stars).

- **Gate:** mean `log10(stars)` is higher in the early group, `p < 0.05`.
- **Why it is here:** if this *fails*, the cohorts are too small or too odd to
  detect anything, and G1's result should be discounted accordingly. It is a
  sanity check on the instrument, not a finding.

### G3 — The material a governance tool needs is mostly absent (HF, N=43)
Trig needs published evaluation results to compare a claim against. Cairn needs a
checkable source. This measures whether either exists.

- **Gate:** the fraction of models carrying **published evaluation results** is
  **below 0.50**. **SUPPORTED** if below; **FALSIFIED** if at or above.
- Reported alongside: fraction with a linked paper, fraction with a license, and
  the fraction carrying **none of the three**.

### G4 — Popularity is not evidence (HF, N=43)
If downloads predicted whether a model publishes its evaluations, then attention
would be a proxy for checkability and a governance tool would be less necessary
for popular models.

- **Gate:** correlation between `log10(1+downloads)` and having eval results.
  **SUPPORTED** (i.e. popularity is *not* evidence) if `|r| < 0.30`.
- **Falsified** if `|r| ≥ 0.30` in either direction — which would be worth knowing
  and would change where a tool like Trig is most useful.

### G5 — No forecast is produced · **pre-registered refusal**
The study emits **no** projected user counts, adoption curves, market sizes or
valuations for any tool. This is recorded as a prediction so that its violation
is a test failure rather than a matter of taste.

**No gate above will be altered after the results are seen.**

---

## 4. What a result here would and would not license

- **Would:** a description of the committed cohorts, and a measurement of whether
  the inputs these tools depend on are present in real published models.
- **Would not:** any claim about the AI industry, about growth rates, about what
  will happen next, or about how any tool in this repository will be adopted.
  N is 50 and 43, drawn from cohorts assembled for other purposes, containing only
  survivors.

The honest summary of this study's *scope*, written before its results: **it can
tell you whether the raw material for governance tooling exists in the open. It
cannot tell you whether anyone will use the tooling.**
