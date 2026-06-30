# Pre-Registration — Human–AI Hybrid Network Coupling Test

**Status: speculative, new hypothesis — NOT implied by the existing results.** The
yeast and GitHub cohorts contain no human–AI interfaces, so nothing in the current
data speaks to this. This test exists to find out whether the linear coupling found
in two network types *holds* at a human–AI boundary, or fails there. It is designed
to **confirm, disconfirm, or come back inconclusive**, and all three are reportable.
Keep it separate from the empirical manuscript, which stands on what the two cohorts
actually show.

Commit this file and the SHA-256 printed by `hybrid_network_test.py` **before** any
data is collected. Do not change a definition or threshold after data is seen.

## Hypotheses
- **H1 (coupling form).** In human–AI hybrid task networks, viability E couples to
  the interface fidelity D_align *linearly* (E = U·D_align), as in the prior two
  domains — versus *quadratically* (E = U·D_align²).
- **H2 (binding constraint).** The interface fidelity D_align is the binding
  constraint: scaling AI capacity U yields diminishing returns once D_align
  saturates. This is the "human bottleneck" claim, here made falsifiable.

## Unit & domain
- **Primary domain:** AI-assisted software development. **Unit:** one human–AI task
  instance — a human issues an initiating instruction to an AI assistant/agent,
  which produces an artifact that is then accepted or not.
- Generalizable to other human–AI workflows (support, writing, analysis) with the
  same variable roles, but pre-register one domain at a time.

## Outcome (measured, non-circular)
- **E:** task success. `E = 1` if the AI-produced artifact was accepted/merged AND
  survived a window W (passed tests / not reverted within W days); `E = 0` if
  rejected, failed, or reverted. Derived from task lifecycle only — independent of
  the fidelity measures and of U.

## Variables
- **D_enc,human ∈ [0,1] — human encoding fidelity (INPUT side).** Specificity /
  completeness of the initiating instruction, scored by a fixed rubric (explicit
  goal, constraints, acceptance criteria, examples, context), computed from the
  PROMPT ALONE.
- **D_dec,AI ∈ [0,1] — AI decoding fidelity (OUTPUT side).** How faithfully the AI's
  first output realized the human's intent, operationalized as retention of that
  output in the final accepted artifact:
  `D_dec,AI = 1 − normalized_edit_distance(AI_first_output, final_accepted)`.
  Measured OUTPUT-side, independent of the prompt's specificity.
- **D_align = D_enc,human × D_dec,AI** — the interface fidelity.
- **U — capacity.** The AI model's capability tier, mapped to a fixed capability
  score (e.g. a published benchmark resolved-rate for that model/version). Must span
  ≥ 3 tiers for H2.

## The channel-independence risk — the main threat to this design
Unlike yeast (VIF 1.003) and GitHub (VIF 1.02), `D_enc,human` and `D_dec,AI` are at
genuine risk of collinearity: a clearer prompt plausibly produces a better AI output,
so the two hops may carry the same information. This is the single biggest threat
here. The VIF gate handles it honestly: **if VIF(D_enc,human, D_dec,AI) ≥ 5 the
channel has collapsed and BOTH H1 and H2 are INCONCLUSIVE** — you cannot attribute
variance to a two-hop interface when the hops are redundant. A collapsed channel is
itself an informative negative result about the operationalization.

## Analysis
- **H1 PRIMARY (coupling form).** Min-max scale D_align to [0,1]. Logistic AIC:
  `M_lin: logit(E)=b0+b1(U·D_align_s)` vs `M_quad: logit(E)=b0+b1(U·D_align_s²)`.
  `ΔAIC = AIC_lin − AIC_quad` (>0 favours quadratic). Permutation null on D_align_s
  (1000×, seed 42), z-scored. Secondary nested: `M0:U`, `M1:U+D_align`,
  `M2:U+D_align+D_align²` on natural D_align.
- **H2 SECONDARY (binding constraint / ceiling).** Interaction model:
  `logit(E)=b0+b1·U+b2·D_align+b3·(U×D_align)`. Stratify by D_align tercile and
  estimate the U→E slope within each stratum (`logit(E)~U` per tercile).

## Decision rule (pre-committed, both directions — thresholds LOCKED)
A verdict requires `N ≥ 500`, minority-class `≥ 100`, and
`VIF(D_enc,human, D_dec,AI) < 5`.

| H1 verdict | condition |
|---|---|
| QUADRATIC SUPPORTED | `ΔAIC > 10` and permutation `z > 3` |
| LINEAR (quadratic disconfirmed) | `ΔAIC ≤ 0` |
| INCONCLUSIVE | `VIF ≥ 5`, or `0 < ΔAIC ≤ 10`, or gate not met |

| H2 verdict | condition |
|---|---|
| BINDING-CONSTRAINT SUPPORTED | the U×D_align interaction is positive and significant (`b3` > 0, p < 0.01) AND the highest-D_align-tercile U→E slope is positive (CI excludes 0) and steeper than the lowest-tercile slope |
| BINDING-CONSTRAINT REJECTED | the interaction is not positive-significant AND the U→E slope is positive (CI excludes 0) in both the low and high D_align terciles (capacity helps regardless of interface) |
| INCONCLUSIVE | otherwise, or gate not met |

*Pre-lock validation.* This decision rule was checked on synthetic cohorts with known
ground truth before being committed: it correctly returns LINEAR when coupling is
linear, BINDING-CONSTRAINT SUPPORTED when AI capacity helps only at high interface
fidelity, BINDING-CONSTRAINT REJECTED when capacity helps regardless, and INCONCLUSIVE
when the signal is weak — and it does not false-positive on noise. An earlier version
of the H2 rule was discarded during this check because it could not detect a genuine
binding constraint (it required the low-fidelity stratum slope to be exactly zero,
which the bottom tercile is not).

## What each outcome means
- **H1 linear** → the coupling generalizes to the human–AI boundary; the manuscript's
  regularity extends one domain further (still not a "law").
- **H1 quadratic** → the boundary behaves differently from the two network domains;
  interesting, and would warrant its own write-up.
- **H1/H2 inconclusive via VIF** → the two-hop interface operationalization failed;
  redesign the fidelity measures before making any claim.
- **H2 supported** → the "human bottleneck" is real and measurable: AI capacity has
  diminishing returns once interface fidelity saturates.
- **H2 rejected** → capacity matters independently of interface fidelity; the
  bottleneck claim is false in this domain.

## Data requirements (what it would take)
- `N ≥ 500` human–AI task instances with measured outcomes and balance (≥ 100
  failures).
- Variance: ≥ 3 model tiers (U); a range of prompt qualities (D_enc,human) including
  poor ones; a range of output-retention (D_dec,AI) including low.
- Per instance: the initiating prompt, the AI's first output, the final accepted
  artifact, the lifecycle outcome (merged / reverted / test-pass), and the
  model/version.
- **Honest sourcing constraint.** Unlike STRING (a file) or GitHub (an API), this
  data is not off-the-shelf. Realistic sources:
  (a) instrumented assistant/agent telemetry that retains prompt → first-output →
  final → outcome → model (Copilot / Cursor / Claude-Code-style logs);
  (b) a curated dataset of public AI-disclosed pull requests with the prompt, the
  suggestion, the merged version, and the merge/revert outcome;
  (c) a controlled study varying model tier and prompt quality with scored outcomes.
  The binding practical constraint on this test is obtaining (a)–(c) — not the
  analysis, which is already locked in `hybrid_network_test.py`.
