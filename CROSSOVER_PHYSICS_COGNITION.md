# The RT → Governance crossover, run on quantum physics and cognitive psychology

**Spec** `6cb42dcd0147fce58eb63f16761ae0b7e98c63099b45af1f9d4d2965dd63e4b8` · locked before
any fit · **5/9**

```bash
python3 -m pytest -q crossover/test_crossover.py
```

Two theories, named and pre-registered:

| | | |
|---|---|---|
| **T2O** | Two-Hop Objectivity | quantum arm — a **derivation** from standard QM |
| **T2R** | Two-Hop Retention | cognitive arm — a **simulation** |

---

## First: what "governance, not theology" can and cannot mean here

You're right that the five questions are governance questions. But the honest version of
that claim is narrower than it looks, and stating the narrow version is what makes it
testable:

> **Each of the five admits an operational reading that names a measurable quantity.**
> That is what makes a question *governance-tractable*.

That is a **Layer 2** claim — it is about tractability, not about what the questions
ultimately mean, and it is not evidence that any particular reading is correct. Writing down
an operational reading is not answering a question.

| Question | Operational reading | Named quantity | Tested here? |
|---|---|---|---|
| **Q1** Purpose | what does the system convert capacity into, at what yield | `E = U·D` | measured elsewhere |
| **Q2** Realms | is there a terminal register scoring trajectories | selection floor `D ≥ D_min` | **no** |
| **Q3** Stewardship | one act, or a **two-hop channel** | `D_enc · D_dec` vs a single term | **yes — and it lost** |
| **Q4** Reference-lock | does fidelity need a single locked frame | degradation under multiple frames | **no** |
| **Q5** Failure | can outcomes be shortcut, or must they be monitored | `τ_v`, irreducibility | **no** |

**Four of the five were not put at risk by this run.** Only Q3 was — and it failed.

## Second: the crossover protocol, including step 4

The protocol is four steps, and **step 4 is not optional** — a crossover that skips it is
renaming, not reframing. Every reframe gets exactly one of three verdicts: **rival theory**
(changes a prediction), **interpretation** (empirically equivalent), or **category error**
(contradicts a theorem).

---

# Arm 1 — Quantum physics · T2O

## Step 1 — the RT reading, at full strength

Decoherence theory: a system coupled to an environment loses coherence in the pointer basis;
**measurement statistics are recovered with no conscious observer**. Settled, not in dispute.

**Quantum Darwinism** (Zurek) adds the part that matters: the environment is not a monolithic
sink. It stores **redundant copies** of pointer-basis information, and observers access only
**fragments**. Objectivity is explained by many fragments carrying the same record.

**This already distinguishes total system–environment correlation from fragment-limited
observer access.** Any governance reframe that "discovers" this has rediscovered an existing
theory and has to say so.

## Step 2 — the channel

| | |
|---|---|
| **U** | `H(S)`, pointer entropy available to be made objective |
| **D_enc** | `1 − |Γ|`, total decoherence factor — set by the **coupling** |
| **D_dec** | `m/N`, fraction of environment accessed — set by the **observer** |

Two different knobs. That's what makes a two-hop claim testable rather than a relabelling.

## Step 3 — re-derive, don't re-label

The **partial-information plateau** is recovered exactly. `I(S:F)` reaches full `H(S) = 1.0000`
bit by fragment fraction 0.5 and is monotone in fragment size. This is a closed-form
consequence of the Schrödinger equation for the standard pure-dephasing spin-star — **not a
mechanism chosen here.** Nothing generates the plateau; the plateau is a theorem.

## The result — Q3 failed decisively, and the spec predicted it

```
median absolute error against exact I(S:F),  95 points, N = 20

  single-hop      U · D_enc                   0.0028 bits   ← wins
  two-hop linear  U · D_enc · D_dec           0.5495 bits   ~195× worse
  quadratic       U · (D_enc · D_dec)²        0.7709 bits
```

**The second hop is not merely dead weight. Including it makes the prediction dramatically
worse.**

The locked spec recorded Q3 as at genuine risk and gave the reason in writing: *"the
partial-information plateau means a form linear in fragment fraction must undershoot… I
expect the two-hop linear form to LOSE this gate."* It did.

**Q2 passed, and that pass is hollow.** The linear form beat the quadratic by 0.22 bits, so
the gate is met. Both are useless next to the single-hop form. A gate can be met by beating a
worse rival, and that is what happened.

### My prediction about *where* it would fail was wrong

I said the linear form would fail in the saturation region, at large fragments. It fails
worst at **small** fragments — mean error **0.6787** at the smallest fraction against
**0.3434** at the largest.

The reason is redundancy: **one qubit in twenty already carries nearly all the classical
information**, so the exact curve is already at the plateau while the linear form is still
predicting one twentieth of it. Direction right, location wrong. Recorded, not repaired.

### What this costs LISM — and it is a real cost

> **The two-hop product form assumes the decode hop is *scarce*** — that accessing more of
> the channel buys proportionally more yield. **Where records are redundantly copied, it is
> not scarce**, and the product form is wrong by two orders of magnitude.

`E = U · D_enc · D_dec` now carries a stated domain limit: **do not apply it to channels
whose records are redundantly replicated.** This does not reverse the substrates where it was
measured — yeast, GitHub, the financial cohort — which are not obviously redundant in this
sense. It marks a **boundary**, discovered by carrying the form into a new field and having
it fail.

## Verdict — declared *before* the run

**INTERPRETATION, not rival theory.**

The channel identification *is* quantum Darwinism. It changes no prediction of physics.
Declaring this in advance is what stopped a good numerical fit being presented afterwards as
a physical discovery.

There is something modest to take from it: a reframe that lands on an existing, well-tested
theory is a **validity check on the method** — the vocabulary mapped onto real structure
instead of inventing new structure. Modest, and reported as modest.

**Hard constraint respected:** decoherence is not observation. Nothing here makes any outcome
depend on a mind, and no signalling or zero-latency claim appears anywhere.

## The experiment a physics lab would run

**Protocol.** Prepare a system qubit dephased by an engineered *N*-subsystem environment —
trapped-ion chain, photonic multi-mode, or NV centre with a controlled nuclear-spin bath.
**Hold the total decoherence factor |Γ| fixed while redistributing the per-subsystem
overlaps:** configuration A concentrates the record in few strongly-coupled subsystems,
configuration B spreads it thinly across many.

**Measure.** Reconstruct `I(S:F)` against fragment size tomographically; extract redundancy
`R_δ`.

**What it settles.** Whether accessible information at fixed total decoherence depends on how
the record is distributed, and which functional form in `(D_enc, D_dec)` tracks it.

**What it does not settle.** Nothing about governance, institutions, or the five questions. It
is a physics measurement and stays one.

**Honest note:** this is close to experiments already performed on quantum Darwinism in
photonic and NV systems. It's the experiment this arm *implies*, not an unprecedented one.

---

# Arm 2 — Cognitive psychology · T2R

## Step 1 — the RT reading, at full strength

Encoding, storage, retrieval. The testing effect and spacing effect are robust and replicated.
**Bjork's New Theory of Disuse already posits two factors** — storage strength and retrieval
strength. A two-factor reading of memory is **not new and is not claimed as new here.**

What is actually at issue is narrower: do the two combine **multiplicatively**, so one at zero
cannot be compensated, or **additively**, so they trade off?

## Step 4 — the discriminating prediction

**The multiplicative form forbids what the additive form permits:** with one factor at or near
zero, retention must go to zero regardless of the other. An additive account predicts a
non-zero floor at `w·U`. That corner of the design space is a real experimental design.

## The result — the arm could not fail, and that is my error

**Recovery was 1.0000 in all 36 configurations across all 200 replicates.**

The locked design applies noise per participant and then **averages over the cell**, so
effective noise on a cell mean is the stated sd ÷ √n — about **0.0045** at the lowest setting.
The two accounts differ by far more than that at every design point. Nothing could fail.

- **C2 failed** — no populated failing region.
- **C3 "passed" at 1.0000** and **C4 "failed" at a gap of exactly zero.** **Neither is
  informative.** A test that cannot fail is not evidence.

**Whose error:** mine. The noise levels were specified without accounting for averaging. The
spec is not edited and the gates are not re-scored.

### One sentence of my own spec is withdrawn

The spec said a C5 miss would be *"a real result against DCM."* **It is not, and that sentence
is withdrawn.**

With recovery identically 1.0 there is no variation for Δ to predict, so the AUC is
**undefined**, not low. C5 scores as not met because the locked rule says so — but its status
is **UNTESTABLE-HERE, not REFUTED**. **Nothing in this run is evidence for or against DCM.**

**What the next spec must do:** specify noise on the cell mean directly, or raise it enough
that averaged noise is comparable to the gap between the accounts — and re-register before
running.

## Verdict

**INTERPRETATION.** The accounts separated everywhere in the tested design space, so the
reframe added no design guidance. That verdict was assigned by the gate rule declared in
advance — and it rests on a mis-specified noise model, so even the interpretation verdict is
weakly supported here.

---

## What this run may and may not be quoted for

**May:** that a specific functional form does or does not track an exactly computable quantum
quantity; that a specific design can or cannot separate two accounts of retention under
stated noise.

**May not:** that physics confirms a governance reading. That anything was learned about human
memory, the testing effect or the spacing effect. That the five questions have been answered.
That a reframe which recovers an existing theory has discovered something.

**Root analysis supports no number here.** It produced the vocabulary and the hypothesis. It
adjudicates no gate, appears in no computation, and a test scans the source to enforce that.

## Reproduce

```bash
python3 crossover/crossover.py
python3 -m pytest -q crossover/test_crossover.py
bash reproduce_all.sh
```

Exit 0 means **"reproduces including its failures"** — and this run has four of them, one of
which is a refutation of the programme's own central functional form in a new domain.
