# Pre-registration — can a fabrication evade the reader, and what does it cost?

Written and hashed **before the evasion run**. 2026-08-29, this session.

---

## The question, which is the co-evolution question

The previous run measured that a fabrication carrying specifics reads **more**
checkable than an honest grounded plan — 5 marks to 1. The obvious next move for
anyone writing fabrications is to **evade**: keep the falsehood, drop the
patterns the reader looks for.

If that works cheaply, the reader is a speed bump and co-evolution favours the
liar. If it works but **costs the liar something they cannot afford to lose**,
the reader is doing structural work no amount of model improvement removes.

This is not a question about better detection. It is a question about whether
there is a trade the adversary is forced to make.

## Two facts already measured here that frame it

- **`F_out = F_eval`, gap 0.** `det-telemetry/results_det.json` D3: an honest
  generator scored 400 true and a **lying** generator scored 400 true against
  the same fixed evaluator. Output fidelity is set by the evaluator, not by the
  generator's honesty. (The user wrote `F_in = F_eval`; the measured law in this
  repository is `F_out = F_eval` with `∂F_out/∂F_gen = 0`.)
- **D5, the oracle failure as a number.** The self-verifying arm **claimed 422**
  while its true score is `null` — unmeasurable, because it graded itself. The
  externally-verified arm scored 400 and that number is real.

---

## Cases

Four rewrites of the same false claim, from the previous run's Case C:

| | |
|---|---|
| **C** | the original fabrication — fluent, specific, invented (baseline, 5 marks) |
| **C_evasive** | the same falsehood, rewritten to avoid every lexical pattern: no digits, no named API, no RFC, no file path, no date, no place |
| **C_hedged** | the same falsehood wrapped in hedges — "reportedly", "is understood to" — keeping the specifics |
| **B_padded** | the TRUE grounded plan, padded with specifics, to check the reader is not simply counting words |

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| E1 | **C_evasive scores 0 marks.** The detector is evadable and this is not close | 0 |
| E2 | **C_evasive lands in the same bin as the honest-vague case D** — evasion converges on fog | identical readout |
| E3 | **C_hedged still scores high.** Hedging language does not remove a staked specific | ≥ 4 marks |
| E4 | **No rewrite is both specific and unread.** Every case scoring ≥ 3 marks carries at least one opened-able handle | invariant holds |
| E5 | B_padded scores ≥ C, so the reader is not rewarding falsehood — it is rewarding specificity, in either direction | B_padded ≥ 5 |

**E4 is the load-bearing one.** If it holds, the adversary faces a forced trade:
*stake specifics and be checkable, or evade and stake nothing.* A fabrication
that stakes nothing has lost the thing that made it persuasive — it now reads
like the honest vague case, which is the state a reader is told to distrust.

**E1 is deliberately a prediction that the tool loses.** I expect evasion to be
trivial, and the value is in what it costs, not in whether it is possible.

---

## Nulls, registered in advance

**NULL-E1.** These are four texts I wrote, adversarially, against a detector I
can read. That is the easiest possible evasion setting and it says nothing about
how often real models produce evasive text.

**NULL-E2.** "Converges on fog" is a claim about a lexical readout, not about
persuasiveness. Whether a human finds the evasive version less convincing is not
measured here and would need people.

**NULL-E3.** E4 is an invariant of *this* detector's five signals. A detector
looking for different things would have a different forced trade, or none.

**NULL-E4.** Nothing here measures revenue, adoption, or whether the forced
trade matters commercially.

---

## What would falsify this

1. **E4 fails** — some rewrite is specific, false, persuasive AND scores low.
   Then there is no forced trade, the reader is evadable at no cost, and the
   co-evolution argument favours the fabricator.
2. **E3 fails** — hedges alone defeat the reader, meaning the detector is
   reading tone rather than staked content.
3. **E5 fails** — a true text cannot reach the same score as a false one, which
   would mean the reader has some purchase on truth and
   `test_a_fabricated_claim_reads_exactly_like_a_true_one` is wrong.
