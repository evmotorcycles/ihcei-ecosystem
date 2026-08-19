# Pre-registration — the Lens algorithm

Written and hashed **before** `press.js` or `test_press.py` were run once.

---

## The logic this is built on, without the terminology

A pomegranate is peel, bitter pith and seeds around the part you want. You do
not argue with the peel. You **press it**, and what runs out is what you can
use. Everything that does not run out was never going to nourish anybody, no
matter how good the fruit looked from outside.

The same source draws a distinction it treats as central: **truthfulness is not
truth**. Truthfulness is manner — fluent, confident, sincere-sounding. Truth is
what survives the pressing.

That is the mask and the lens, exactly:

- A **mask** claim has truthfulness. Press it and nothing runs out. There is no
  source to open, no figure to check, no date to compare. You cannot be shown
  wrong about it, which is precisely why it is safe to say and useless to hear.
- A **lens** claim has the *form* of truth. Press it and something runs out —
  things you can go and do. It may still be false. But now it can be *shown*
  false, and quickly.

No terminology from that source appears in any measurement code or on any page.
The logic is the pressing; that is what is being borrowed.

---

## What the algorithm measures, and what it refuses to

It measures **how fast reality could contradict this claim, if reality
disagrees.** Not whether it is true. Not how likely it is. Not how good it is.

The consequence has to be said before the numbers arrive, because it looks like
a bug and it is the whole design:

> A completely fabricated claim carrying a named body, a year, a percentage and
> a stated method scores **maximum**. An honest, careful, vague statement scores
> **nothing**.

That is correct behaviour. The fabricated claim has staked something checkable
and can be destroyed in one phone call. The vague statement cannot be destroyed
at all, which is why fog survives and specifics die. Pressing a well-formed lie
traps the liar inside their own structure; pressing fog produces nothing, and
the algorithm says so rather than producing a number.

---

## The graph

A claim's handles are not independent of one another. A figure attributed to a
report is worth nothing if the report does not exist — so the marks do not
attach to the claim directly, they attach to the **origin** they are attributed
to, and the origin attaches to the claim.

- parts: the claim, one node per origin, one node per mark
- links: each mark → its origin (weight 1); each origin → the claim (weight 1)
- FATHOM sources: the **marks**, because each one is a thing a person can go and
  do that could come back negative
- conclusion: the claim

Disjunctive on purpose, and this time correctly: any single check coming back
negative can kill the claim, so contraction is the right move here — unlike a
bill, where every input is required and packs therefore refuse this readout.

---

## Predictions

Let `m` be the number of marks hanging off a single origin.

| # | Prediction | Value |
|---|---|---|
| L1 | Bearings on the check graph are all 1.000 and total `m + 1` = parts − pieces | tree, exactly |
| L2 | The parts whose removal breaks the graph are **exactly the origins** | origins only |
| L3 | Each mark's dependence is **1/m² exactly** | see below |
| L3a | m = 1 | 1.000000 |
| L3b | m = 2 | 0.250000 |
| L3c | m = 3 | 0.111111 |
| L3d | m = 4 | 0.062500 |
| L3e | m = 5 | 0.040000 |
| L4 | Two independent origins with two marks each: dependence per mark, and count of single points | 0.125000, 2 |
| L5 | A claim with no marks at all: no number is returned; `checkable` is false and the words say it cannot be shown false | refused |
| L6 | **A fabricated claim and a true claim with identical structure return identical numbers, to 1e-12** | identical |
| L7 | The page prints that a perfectly formed false claim scores the same as a true one | printed |
| L8 | The browser engine agrees with `fathom/fathom.py` and `spar/spar.py` | 1e-9 |

L3 is worth stating in words because it is the finding, not a detail: **with
`m` handles all hanging off one origin, each handle reads 1/m² — it falls off as
the square.** Five handles do not give you five ways to check. They give you one
way to check, dressed as five, and each reads 0.040 precisely because the graph
is saying they are not independent. The reassuring number is the warning.

L6 is the THESIS. If a fabricated claim and a true one with the same structure
ever return different numbers, the engine has started guessing about the world,
and it must be stopped rather than improved.

---

## Nulls, registered in advance

**NULL-L1.** Exposure is not truth, not evidence, not probability and not a
score of quality. A high reading means the claim has made a hard wager that can
be settled quickly. It says nothing whatever about which way the settlement goes.

**NULL-L2.** Mark detection is lexical. It matches words, it does not read. It
will miss a source that is named without any of the words it looks for, and it
will fire on the word "study" in a sentence that cites nothing. It is a
suggestion in exactly the sense `suggest()` in `engines.js` is a suggestion, and
nothing measured is allowed to rest on it without a person confirming or
striking it.

**NULL-L3.** Nothing here measures whether anyone actually goes and does the
check. The whole value of the tool is in an action taken outside it, and that
action is unobservable from inside it. The ordering could be perfect and the
effect nil, and this repository could not tell.

**NULL-L4.** The pressing metaphor is a way of explaining what the arithmetic
does. It is not evidence for anything, it does not make the arithmetic more
correct, and no result below depends on it.

---

## What would falsify this

1. **L6 fails.** A fabricated and a true claim of identical shape read
   differently, meaning the engine is guessing about the world. Stop.
2. **L3 fails.** The dependence is not 1/m², so the "reassuring number is the
   warning" reading is wrong and must be withdrawn rather than softened.
3. **A claim with no marks returns a number.** Then the tool has assigned a
   value to fog, which is the mask failure committed by the tool built to name
   it.
