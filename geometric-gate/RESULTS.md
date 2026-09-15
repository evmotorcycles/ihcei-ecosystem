# Results — can the geometric gate be given a threshold at all?

Run 2026-09-15. Offline, CPU, deterministic, no network, no keys.
Predictions locked in `prereg_gate.md`, sha256
`ddaa4b4a3ca7f02c0e468bf14b765fa23b926db19f17a45534ffde21e602cca4`.

**Eight predictions hit. G9 missed, on both of its clauses — and the miss is
the answer to the question.**

---

## The short answer

**No threshold is picked out by this data.** The sensor walks continuously
through the whole band where a cutoff would sit. Any hard-halt number is a
**declared preference**, not an empirical finding, and has to say so — the
distinction this repository has now had to make five times.

That is not a refusal to answer. It is the answer, and the rest of this file is
how it was reached, including the point where a coarser run would have produced
a confident wrong one.

---

## One correction to the proposal

The message proposing the gate states that under collapse *"the kNN algorithm
faithfully draws the exact same topological connections."* **Measured: it does
not.** 53 shared edges of 79 and 81, Jaccard 0.495, pinned by
`test_the_knn_graphs_really_do_differ_under_collapse`.

LMD is blind for a different reason: `parts − pieces` is a counting identity
that never reads the embeddings. Untrained noise scored conserved too. The
conclusion — that LMD must be bounded rather than withdrawn — survives the
correction intact. The mechanism does not, and it matters, because if scale
carried all the information then a scale sensor alone would be sufficient.

---

## Arm 1 — an absolute variance floor is not an instrument

| scale c | trace | trace / c² | effective rank |
|---|---|---|---|
| 1e-03 | 2.105349e-06 | 2.105348790 | 5.732086 |
| 1e+00 | 2.105349e+00 | 2.105348790 | 5.732086 |
| 1e+03 | 2.105349e+06 | 2.105348790 | 5.732086 |

**G1 hit** (rel. err 4.2e-16): trace scales as `c²`. **G3 hit** (1.2e-14):
effective rank does not move at all.

**G2 hit, and it is the load-bearing one.** Put the floor at 1% of healthy
trace, `eps = 2.105e-02`:

| | trace | halts? |
|---|---|---|
| collapsed | 2.107686e-12 | **yes** |
| collapsed × 1e7 | 2.107686e+02 | **no** |

Same space, exactly as collapsed — its effective rank is identical to 1e-9 — and
it now clears the gate. **A gate that can be cleared by choosing units is not a
gate.** Any absolute epsilon on the trace is defeated by multiplication, which
is precisely the operation it was built to catch.

## Arm 2 — neither sensor catches both failures

| embedding | trace | trace / healthy | eff. rank | rank / healthy |
|---|---|---|---|---|
| healthy | 2.105349e+00 | 1.000 | 5.7321 | 1.000 |
| volumetric collapse (trained) | 2.107686e-12 | **1.0e-12** | 4.0785 | **0.712** |
| dimensional collapse (rank-2) | 5.172450e+00 | **2.457** | 1.9505 | **0.340** |

**G4, G5, G6, G7 all hit.** Rank keeps 71% of healthy through a collapse of
twelve orders of magnitude; trace keeps 246% through a collapse of independence.
**Both off-diagonals miss.** A one-sensor gate is blind to one of the two
failures whichever sensor you pick — which is the strongest argument for the
two-sensor design as proposed.

One detail worth keeping: a space collapsed to a single point returns
**`nan`**, not a tidy 1.0. Empty is not a number.

---

## Arm 3 — G9 MISSED, twice

### Clause (a): momentum is the wrong dial

| momentum | 0.0 | 0.5 | 0.9 | 0.99 | 0.996 | 0.999 |
|---|---|---|---|---|---|---|
| median spread ratio | 0.698 | 0.698 | 0.699 | 0.700 | 0.703 | 0.717 |

**G8 hit** — monotone, on the five registered seeds. It is a thin result:
the whole sweep spans 0.698 to 0.717, and on a three-seed subsample the
monotonicity does not survive, which
`test_g8s_monotonicity_does_not_survive_a_three_seed_subsample` records. The
largest adjacent step is **0.008 orders of
magnitude**, not the 6 predicted, because the sweep **never collapses at all**.
A dial that does not move the failure cannot have a knee in it.

### Clause (b): the empty band was an artefact of resolution

The coarse leak sweep put nothing inside `[0.01, 0.5]` — which would have made a
cutoff there defensible, on exactly the "empty band" reasoning the
pre-registration set up. Sampled finely:

| leak | 0.0 | 0.001 | 0.0025 | 0.005 | 0.0075 | 0.01 | 0.02 | 0.05 | 0.1 |
|---|---|---|---|---|---|---|---|---|---|
| median spread ratio | 0.703 | 0.542 | **0.444** | **0.349** | **0.285** | **0.236** | **0.111** | **0.013** | 0.0006 |

**The band is fully occupied.** Six of nine sampled leaks land inside it. The
sensor walks smoothly from healthy to collapsed with no knee anywhere.

**A coarser run would have reported a defensible threshold and been wrong.**
That is recorded rather than tidied away, in `test_the_prediction_that_missed`.

---

## Arm 4 — which half of the asymmetry is load-bearing

**POST HOC. No prediction was registered, and this revises the previous commit.**

| arrangement | spread ratio |
|---|---|
| shared weights + full gradient | 7.037e-13 |
| shared weights + **stop-gradient**, no moving average | **7.032e-01** |
| moving-average target + full gradient | 2.609e-08 |
| moving-average target + stop-gradient | **7.029e-01** |

**The stop-gradient is the entire mechanism here. The exponential moving average
contributes nothing.** `jepa-probe/` attributed collapse-prevention to the
asymmetry as a whole; split into its two halves, one half does all the work and
the other is inert in this toy. The earlier result is not wrong — both arms were
labelled correctly — but its explanation was too generous, and this is the
correction.

---

## So what should the gate do

Reported rather than decided, because the data does not choose:

- **Never an absolute trace floor.** G2 shows it is defeated by a rescale. If a
  volumetric cutoff is wanted it must be a **ratio against a declared
  reference** — spread at initialisation is the reference used throughout this
  study — so that the units cancel.
- **Effective rank may take an absolute floor**, because G3 shows it is already
  scale-free. A floor expressed as a fraction of the embedding width is
  dimensionless in the same way.
- **Both sensors must be reported**, because G7 shows each is blind to the
  other's failure.
- **Any halt number is a declared preference.** `FLOOR_RETIREMENT.md` retired a
  gate at p = 0.735 for having no sensor; this one has two working sensors and
  still no empirical cutoff, which is a different failure with the same
  remedy — say that the number is chosen, not found.

`gate.py` therefore takes both cutoffs as **required arguments with no
defaults**. A caller who wants a hard halt has to state the numbers and own
them. `test_the_gate_has_no_default_cutoffs` pins that.

## What this run cannot do

- **It cannot give you a threshold.** That is the finding, not an omission.
- **It measures sensors, not networks.** Nothing here says a geometric gate
  improves any real pipeline, or that collapse is common in practice.
- **The dimensional collapse is constructed by projection, not trained.** It is
  a worked example of a failure mode, not evidence that training produces it.
- **Effective rank has several definitions.** The entropy form is used and
  stated; another gives other numbers.
- **Neither sensor measures whether a representation is useful.** A full-rank,
  high-variance embedding can be worthless. Passing this gate is not evidence of
  health; failing it is evidence of one specific sickness.
- **The continuity result is a property of this toy, this optimiser, this
  sweep.** A real embedding space may well be bimodal. n = 1 dataset, 5 seeds.

## Reproduce

```
python3 geometric-gate/run_gate.py          # ~6 min
python3 -m pytest geometric-gate/test_geometric_gate.py -q
```
