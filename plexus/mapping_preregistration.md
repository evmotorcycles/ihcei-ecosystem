# Pre-registration — does the five map onto the ten?

Locked before the graph was built or measured.

## The claim under test

From the exchange: *"Use the five questions to extract the ten elements doesn't
work in either direction. Scope touches domains-of-application, figures touches
actions-and-results, and the other eight elements have no corresponding signal
at all. That's 2 of 10, weakly."*

That is a falsifiable numeric claim about a mapping between two things this
repository already holds in code — the five signals in `cairn/ei_engine.js` and
the ten elements in `plexus/intercept.js`. It can be measured rather than
eyeballed.

## What is hand-written and what is not

**The links are a judgement.** I assign them, each with a stated reason, before
computing anything. The coverage arithmetic over them is not a judgement.

## My assignment, written down before measuring

| Signal | Element | Strength | Why |
|---|---|---|---|
| method | procedures | strong | how a thing was done *is* the procedure |
| scope | domains of application | strong | who and where it applies is the domain |
| figures | rules | medium | a number in a claim is usually a constraint |
| figures | actions and their results | medium | a reported figure is usually an outcome |
| source | authorities and domains of action | weak | a named source is who is entitled to assert |
| time | — | none | "when" has no counterpart among the ten |

## Predictions

| # | Prediction | Value |
|---|---|---|
| M1 | Elements with at least one signal pointing at them, on my assignment | **5** |
| M2 | Elements with none | **5** |
| M3 | The set with none includes, robustly, terminology · roles · dues · policies · exceptions | all five |
| M4 | The graph is in **more than one piece** — some elements cannot be reached from any signal | pieces > 1 |
| M5 | The covered count is **not stable** across reasonable alternative assignments; the uncovered set largely is | unstable / stable |
| M6 | My count disagrees with the 2 in the exchange, and the conclusion drawn from it survives anyway | 5 ≠ 2 |

**M5 is the real finding if it holds.** A derivation has one answer. If two
careful people assign these links differently and get different counts, the
mapping is a resemblance, not a derivation — which is a stronger statement than
any particular number, and it is the thing the exchange was right about even
though its count looks low to me.

## Nulls

**NULL-M1.** My assignment is no more authoritative than theirs. Both are
readings. The arithmetic is only as good as the links, and the links are
opinions with reasons attached.

**NULL-M2.** Nothing here says the ten elements are wrong, or that the five
signals are wrong. It says only that one cannot be pressed out of the other.

**NULL-M3.** This measures a mapping between two lists in this repository. It
says nothing about whether either list is the right list.
