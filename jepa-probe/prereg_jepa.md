# Pre-registration — the JEPA mechanism, and whether Claude can stand in for it

Written and hashed **before the run**. 2026-09-15.

---

## Why this exists

`nere/JEPASemanticFilter` abstains on every call because there is no benchmarked
latent-energy model in this repository. The request is to test Claude using
JEPA's architecture instead. That splits into two questions with very different
answers, and the split is the point.

**Source:** Assran et al., *Self-Supervised Learning from Images with a
Joint-Embedding Predictive Architecture*, arXiv:2301.08243v3.

`where`: the paper text supplied in this session. Section 2 states the mechanism
under test verbatim: *"as with Joint-Embedding Architectures, representation
collapse is also a concern with JEPAs; we leverage an asymmetric architecture
between the x- and y-encoders to avoid representation collapse."* Section 3
states the loss is the average L2 distance between predicted and target
patch-level representations, and that the target-encoder parameters are updated
by an exponential moving average of the context-encoder parameters.

---

## Arm 1 — the collapse mechanism, built and run

A **miniature** of the mechanism, not of the paper. Linear encoders on synthetic
block-structured vectors: a context block is encoded and passed through a
predictor conditioned on a positional embedding; target blocks are encoded by a
second encoder; the loss is L2 in representation space. Two arms differing in
**one** thing:

| arm | target encoder | gradient to target branch |
|---|---|---|
| **symmetric** | the same weights as the context encoder | yes |
| **asymmetric** | exponential moving average, momentum 0.996 | no (stop-grad) |

| # | Prediction | Value |
|---|---|---|
| J1 | The symmetric arm **collapses**: target-embedding variance falls below 1% of its value at initialisation | < 0.01 |
| J2 | The asymmetric arm does **not** collapse: variance stays above half of initialisation | > 0.5 |
| J3 | The symmetric arm's loss reaches **near zero while carrying no information** — a flat energy landscape, which is the failure the paper names | loss < 0.01 |

**J2 is the one I expect to be wrong about, and the reason is worth stating in
advance.** Collapse is still a global optimum of the asymmetric arm: if the
context encoder goes to zero, the exponential moving average follows it and the
loss goes to zero too. The paper's claim is that the asymmetry avoids collapse
**in practice, with Vision Transformers, at scale**. A linear toy may not show
the mechanism at all. If J2 misses, the finding is that the asymmetry alone is
not sufficient — not that the paper is wrong.

## Arm 2 — what the repository's own readouts see

Build a k-nearest-neighbour graph (k = 3, ties by index) over the learned
embeddings of 40 held-out samples, in each arm, and read it with `spar`.

| # | Prediction | Value |
|---|---|---|
| J4 | The measured total bearing equals parts − pieces in **both** arms, so **Foster's total cannot detect collapse** | conserved in both |
| J5 | The embedding-space distance scale in the collapsed arm is orders of magnitude smaller than in the healthy arm | ratio < 0.01 |

**J4 is the finding that matters and it is a limitation, not a win.** The
readout that survived the padding attack in `agi-stack/` — immune because
Foster fixes the total at parts − pieces — is immune here too, and here that
immunity is blindness. A conserved quantity conserves through a failure.

---

## Arm 3 — Claude in the semantic seam: DESIGNED, NOT RUN

The seam needs something LMD provably lacks. `smi`/`spar` are blind to party
inversion: `test_the_parties_can_be_inverted_and_the_readout_does_not_move`
pins a bit-identical readout when the parties in a sentence are swapped. A
semantic layer earns its place only if it is **not** blind to that.

The protocol, registered so someone other than Claude can run it:

1. Take *n* sentence pairs that are party-inversions of one another.
2. Ask the model which of a pair carries a given obligation, with no other context.
3. Score agreement against the inversion, and repeat each probe under two
   surface rewordings to measure stability.
4. Pass requires both: distinguishes the inversion, **and** is stable across
   rewordings.

| # | Prediction | Value |
|---|---|---|
| C1 | This arm is **NOT RUN** in this session, and no number is reported for it | UNRUN |

**Why it is not run, stated rather than worked around.** Claude is the author of
this pre-registration. A model that has just written down the expected answer and
then answers its own probe is contaminated by construction — the same defect
recorded in `agi-stack/` as A3/A6 CONTAMINATED, where predictions written after
a sample was printed came out *worse*, not better. Self-report is not
measurement. There is also no offline, deterministic, resamplable access to a
model here, so the run could not be reproduced even if it were clean.

**What would make it runnable:** a second party issues the probes, the probes are
sealed before the model sees any of this file, and each is sampled more than once.

---

## Nulls, registered in advance

**NULL-J1 — this is not I-JEPA.** No Vision Transformer, no images, no ImageNet,
no masking over patches of a real picture. It is the collapse mechanism reduced
to linear encoders. Nothing here reproduces, contradicts or bears on any number
in the paper's tables.

**NULL-J2.** A miniature that fails to show a mechanism is evidence about the
miniature first. Scale is part of the paper's claim and is absent here.

**NULL-J3.** Embedding variance is a **proxy** for collapse, not a definition of
it. A representation can be varied and useless.

**NULL-J4.** The k-nearest-neighbour graph is a modelling decision. A different k
gives a different graph and therefore different structural readouts.

**NULL-J5 — the one that governs Arm 3.** Nothing in this run measures whether
Claude, or any language model, can serve as a semantic filter. Arm 3 is a design,
and a design is not a result.

**NULL-J6.** n = 1 synthetic dataset, one seed reported with a seed sweep beside
it. Nothing generalises.

---

## What would falsify this

1. **J1 fails** — the symmetric arm does not collapse, and the failure mode the
   paper builds its asymmetry against does not appear even in the setting most
   likely to show it.
2. **J4 fails** — Foster's total does move between the two arms, which would mean
   a conserved quantity is detecting collapse and my reading of it is wrong.
3. **J2 fails** — recorded as a miss, with the toy named as the likely cause
   rather than the paper.
