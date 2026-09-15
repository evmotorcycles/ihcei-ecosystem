# Pre-registration — can a geometric gate be given a threshold at all?

Written and hashed **before the run**. 2026-09-15.

---

## The question, as asked

> "what threshold of variance (or effective rank) in the Geometric Gate should
> trigger a hard halt before the graph is allowed to form?"

This file does not answer that by choosing a number. It measures what the two
proposed sensors actually do, because CLAUDE.md requires a stated reason and an
operable sensor before any number gates a decision, and `FLOOR_RETIREMENT.md`
records one retired at p = 0.735 for failing exactly that.

Two sensors are proposed: **trace of the covariance matrix** (volumetric spread)
and **effective rank** of the embedding matrix (dimensional spread). Effective
rank here is the entropy form, `exp(H(p))` with `p_i = σ_i / Σσ_j` over the
singular values.

`where`: both sensors, and the halt rule, are specified in the message that
asked the question, this session.

## One correction carried in

The same message states that under collapse *"the kNN algorithm faithfully draws
the exact same topological connections."* `jepa-probe/` measured otherwise: 53
shared edges out of 79 and 81, **Jaccard 0.495**. The graphs differ. The
blindness has a different cause — `parts − pieces` is a counting identity that
never reads the embeddings — and that is why a scale sensor cannot be assumed
sufficient on its own. Re-asserted as a test here, not taken on faith.

---

## Arm 1 — is an absolute variance threshold a valid instrument?

| # | Prediction | Value |
|---|---|---|
| G1 | Trace of covariance is **not scale-invariant**: multiplying every embedding by `c` multiplies the trace by `c²` | ratio = c², rel. err < 1e-9 |
| G2 | So **any fixed epsilon is defeated by a rescale**: the collapsed arm, multiplied by a constant, passes a gate it previously failed, while being exactly as collapsed | passes after rescale |
| G3 | Effective rank **is** scale-invariant, across six orders of magnitude | max change < 1e-9 |

**G1–G3 decide whether the question has an answer in the form it was asked.** An
absolute variance floor is a number an adversary moves by choosing units. A
gate that can be cleared by multiplication is not a gate.

## Arm 2 — does either sensor catch both failures?

Two different collapses, which the proposing message correctly distinguishes:

- **volumetric** — the trained symmetric arm from `jepa-probe/`, spread ratio 7e-13
- **dimensional** — healthy embeddings projected onto their top 2 singular
  directions, so the spread is intact but the independence is gone

| # | Prediction | Value |
|---|---|---|
| G4 | Effective rank **does not detect the volumetric collapse**: the collapsed arm keeps at least half the healthy effective rank | ≥ 0.5 × healthy |
| G5 | Trace **does not detect the dimensional collapse**: the rank-2 projection keeps most of the healthy trace | ≥ 0.5 × healthy |
| G6 | Effective rank **does** detect the dimensional collapse | < 0.5 × healthy |
| G7 | So neither sensor dominates: the 2×2 of (sensor × failure) has misses on **both** off-diagonals | both miss |

**G4 is the one I am least sure of.** If the symmetric arm drives its encoder
toward zero without rotating it, the embeddings are a tiny multiple of a
full-rank map and effective rank survives. If training also crushes the spectrum,
rank falls and G4 misses. I do not know which.

## Arm 3 — is there a knee to put a threshold on?

A real dial rather than a synthetic one: retrain the asymmetric arm with the
exponential-moving-average momentum swept over
`{0.0, 0.5, 0.9, 0.99, 0.996, 0.999}`, five seeds each.

| # | Prediction | Value |
|---|---|---|
| G8 | The spread ratio is **monotone non-decreasing** in momentum | monotone |
| G9 | The transition is **abrupt, not gradual** — at least one adjacent pair of momenta differs by more than six orders of magnitude, and no intermediate value lands between 0.01 and 0.5 | a gap, no middle |

**G9 is the direct answer to the question and it is the one that could most
easily be wrong.** If the sweep lands values in the middle of the range, there
is no knee, the sensor is continuous, and **no threshold is empirically
defensible** — the number would have to be a declared preference, which is a
different object and allowed only if it says so. If instead the readings
separate into two clumps with an empty band between, a threshold placed inside
that band has a stated reason and is not arbitrary.

---

## Nulls, registered in advance

**NULL-G1 — this measures sensors, not networks.** Nothing here says a geometric
gate would improve any real pipeline, or that collapse is a common failure in
practice. It says what two proposed instruments can and cannot see.

**NULL-G2.** The dimensional collapse in Arm 2 is **constructed** by projection,
not trained. It is a worked example of a failure mode, not evidence that
training produces it.

**NULL-G3.** Effective rank has several definitions. The entropy form is chosen
here and stated; a different definition gives different numbers.

**NULL-G4.** An empty band in Arm 3 is a property of this toy, this optimiser and
this sweep. It is not a law, and a threshold read off it does not transfer to
embeddings from a real model.

**NULL-G5.** Neither sensor measures whether a representation is *useful*. A
full-rank, high-variance embedding can be worthless. Passing this gate is not
evidence of health; failing it is evidence of one specific sickness.

**NULL-G6.** n = 1 synthetic dataset, 5 seeds, one architecture. Nothing
generalises.

---

## What would falsify this

1. **G1 fails** — trace is somehow scale-invariant and an absolute epsilon is
   defensible after all.
2. **G4 or G6 fails** — one sensor catches both failures, and the two-sensor
   gate is unnecessary.
3. **G9 fails** — the transition is gradual, there is no empty band, and the
   honest report is that the threshold cannot be chosen from data.
