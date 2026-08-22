# Pre-registration — label-blind masking, and four gates rewritten so they can fail

Locked before `test_mask.py` was written.

## What this covers, and what it does not

It covers **Stage 1 only**: stripping every name off a contract until only the
dependencies remain. Stages 2 to 4 of the proposed protocol are not covered,
because the data they need does not exist in this repository — see `NO_DATA.md`.

## The four gates, rewritten

Every gate in the protocol as received is phrased so that it can only pass:
*"definitively proving"*, *"the surviving suites"*, *"verify F4 to ensure the
knife is sharp"*, *"hardcode the certified equations"*. A gate that cannot fail
is not a gate. Restated so each has a losing side:

| | As received | Restated so it can kill the hypothesis |
|---|---|---|
| **F1** | prove structural class out-predicts label class | Both are fitted on the same held-out split. **The hypothesis dies if the structural class does not beat the label class by a margin fixed before the split is drawn.** A tie kills it too. |
| **F2** | track the moment `L_ΔU` breaches 0.15 | **The threshold is struck.** There is no sensor for `L_ΔU` anywhere in this repository, and a hard gate on an unmeasurable quantity is the floor this project retired at p = 0.735. What remains testable without it is monotonicity: **the hypothesis dies if fragility does not rise monotonically with decoupled share.** |
| **F3** | determine if the hardship branch shrinks cascades | **Dies if recoveries with the branch are equal to or worse than without**, on matched pairs. |
| **F4** | verify that label-based books stagger like conventional debt | This is a **negative control** and it is the sharpest thing in the protocol. **If label-based books do NOT behave like conventional debt, the label carries real information and F1's whole premise is weaker.** F4 failing is informative; F4 was written as a formality and is not one. |

## Predictions about the masker itself

| # | Prediction | Value |
|---|---|---|
| K1 | Masking leaves no stripped term anywhere in the masked artefact | 0 leaks |
| K2 | Masking changes no measurement **to tolerance** | worst difference < 1e-12 |
| K3 | Masking is **not** bit-identical, because node names are sort keys and renaming changes floating-point operation order | not identical |
| K4 | Pieces, expected total and single-point count are unchanged exactly | unchanged |
| K5 | A spec arriving with its own classification attached is refused | refused |
| K6 | A spec not declaring whether it is real or synthetic is refused | refused |

K3 is the one worth stating out loud. A study validating its masker with exact
equality would fail spuriously and might then weaken the mask to make the test
pass. The labels do enter the computation — not as information, but as sort
keys, at the fifteenth decimal place.

## Nulls

**NULL-K1.** Masking makes the topology label-free. It does **not** make a coder
blind: a person who knows the field may still recognise a shape. Whether coders
are actually blind needs coders, and there are none here.

**NULL-K2.** Nothing in this file classifies anything. Whether a return is
coupled or fixed, whether a hardship branch is present, is a judgement made by
people looking at masked topology. The masker exists so that what they look at
carries no clue about which answer is wanted.

**NULL-K3.** No result about any financial instrument is produced, implied or
prepared here. There are no contracts.
