# Results — the JEPA mechanism, and why the Claude arm was not run

Run 2026-09-15. Offline, CPU, deterministic, no network, no keys, no downloads.
Predictions locked in `prereg_jepa.md`, sha256
`65522d024b5f06db18e871cf527fbec151ae9375b38bc362bdedea0ea6b98dc9`.

**Five predictions, five hits — including the one I said I expected to miss.**
The most useful result is a **limitation of this repository's own readouts**.

---

## What was built

`nere/JEPASemanticFilter` abstains because there is no latent-energy model here.
Rather than describe one, this builds the single mechanism the paper names as
load-bearing (Assran et al., arXiv:2301.08243v3, §2):

> *"as with Joint-Embedding Architectures, representation collapse is also a
> concern with JEPAs; we leverage an asymmetric architecture between the x- and
> y-encoders to avoid representation collapse."*

Two arms, **differing in exactly one thing**: whether the target encoder is the
context encoder with gradients flowing through it, or an exponential moving
average of it behind a stop-gradient. Same data, same initialisation, same steps,
same learning rate — `test_the_two_arms_differ_in_exactly_one_thing` pins that.

---

## Arm 1 — the mechanism works, and it works in a linear toy

| arm | final loss | spread at init | spread after | ratio |
|---|---|---|---|---|
| symmetric | 1.205e-12 | 0.187209 | 1.317e-13 | **7.0e-13** |
| asymmetric | 3.298e+00 | 0.187209 | 1.316e-01 | **0.703** |

| seed | symmetric ratio | asymmetric ratio |
|---|---|---|
| 0 | 7.0e-13 | 0.703 |
| 1 | 3.5e-13 | 0.723 |
| 2 | 3.1e-14 | 0.687 |
| 3 | 1.6e-12 | 0.658 |
| 4 | 2.0e-10 | 0.707 |

**J1 hit** — the symmetric arm collapses, on all five seeds, by twelve orders of
magnitude. **J3 hit** — its loss reaches 1e-12 while carrying no information,
which is precisely the flat energy landscape the paper describes.

**J2 hit, and I registered in advance that I expected it to miss.** The reasoning
was sound and the prediction was still right: collapse remains a global optimum
of the asymmetric arm — drive the context encoder to zero and the moving average
follows it, taking the loss to zero — and the arrangement **still does not reach
it**, on any seed. The paper's mechanism survives a reduction far below the
setting it was demonstrated in. `test_the_prediction_i_expected_to_miss_and_did_not`.

---

## Arm 2 — the finding that matters, and it is a limitation

Build a k-nearest-neighbour graph (k=3) over 40 held-out embeddings from each arm
and read it with `spar`.

| arm | edges | pieces | total bearing | expected | conserved | cut parts |
|---|---|---|---|---|---|---|
| symmetric (collapsed) | 79 | 4 | 36.000000 | 36.0 | True | 0 |
| asymmetric (healthy) | 81 | 4 | 36.000000 | 36.0 | True | 0 |
| **noise, post-hoc control** | 86 | 1 | 39.000000 | 39.0 | True | 0 |

The embedding scales differ by a factor of **a million** — mean pairwise distance
1.903e-06 against 1.916e+00, ratio 9.9e-07 (**J5 hit**). Both structural readouts
available here report the same thing (**J4 hit**).

**This is blindness, not sameness.** The two graphs are genuinely different — 53
shared edges out of 79 and 81, Jaccard 0.495 — and the readouts still cannot
separate them. Untrained noise is conserved too, because parts − pieces is a
property of the node and component count and not of the representation at all.

### Why, and what it connects to

I first guessed that direction survived collapse while magnitude vanished.
**That was wrong** — the cosine structures correlate at only 0.68 and the mean
matched-row cosine is 0.21. The real reason is the one `lmd-scaling/` measured
last commit: **the structural readouts are scale-invariant.** `spar.scaled()`
carries the docstring *"Bearings must not move."*

That invariance is what makes bearings immune to the padding attack in
`agi-stack/`, and it is the *same property* that makes them blind here.
`test_this_is_the_same_scale_invariance_measured_in_lmd_scaling` multiplies the
healthy embeddings by 1e-6 and every readout holds still.

**One property, two consequences: ungameable by scale, and blind to a collapse
that is purely a change of scale.** A conserved quantity conserves through a
failure. That is the argument for the seam, made against my own tools rather
than for them.

---

## Arm 3 — Claude in the semantic seam: NOT RUN

**C1 hit: this arm is unrun and no number is reported for it.**

The seam needs something LMD provably lacks. `smi`/`spar` are blind to party
inversion — `test_the_parties_can_be_inverted_and_the_readout_does_not_move`
pins a bit-identical readout when the parties in a sentence are swapped. A
semantic layer earns its place only if it is **not** blind to that. The protocol
is registered in `prereg_jepa.md` in enough detail for someone else to run it.

**Why I did not run it.** Claude wrote that pre-registration. A model that has
just written down the expected answer and then answers its own probe is
contaminated by construction — the defect already recorded in `agi-stack/` as
A3/A6 CONTAMINATED, where predictions written after a sample was printed came
out **worse**, not better. Self-report is not measurement. There is also no
offline, deterministic, resamplable model access in this container, so the run
could not be reproduced even if the contamination were removed.

Running it anyway and reporting a number would have produced exactly the
furnished box the abstaining seam exists to refuse.

**What would make it runnable:** a second party issues the probes, the probes are
sealed before the model sees this file, and each is sampled more than once.

---

## What this run cannot do

- **It is not I-JEPA.** No Vision Transformer, no images, no ImageNet, no masking
  over patches of a real picture, no pretraining. Nothing here reproduces,
  contradicts or bears on any number in the paper's tables.
- **It says nothing about whether Claude can be a semantic filter.** Arm 3 is a
  design, and **a design is not a result**.
- **Embedding variance is a proxy for collapse, not a definition.** A
  representation can be varied and useless.
- **The k-nearest-neighbour graph is a modelling decision.** A different k gives a
  different graph and different structural readouts.
- **The blindness result is about the two readouts measured here** — total bearing
  and cut parts. It is not a claim about every possible structural readout; a
  scale-*sensitive* one would separate these arms trivially.
- **n = 1 synthetic dataset, 5 seeds.** Nothing generalises.

## Reproduce

```
python3 jepa-probe/run_jepa.py          # ~14s
python3 -m pytest jepa-probe/test_jepa.py -q
```
