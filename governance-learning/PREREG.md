# Pre-registration — the Governance Learning Algorithm (GLA)

**SHA-256 locked in `prereg.lock.json` BEFORE the model was fitted.** Re-verified
by `test_gla.py`.

---

## What is being built

An ordinary learner fits parameters to minimise a loss and then **returns a
number**. Nothing in it records what it was allowed to see, whether its evidence
was independent, or when it is outside the region it learned from.

A **governance learning algorithm** is an ordinary learner with the four Plumb
obligations moved from the surrounding process into the algorithm itself:

| Obligation | In the learner |
|---|---|
| No bare return | `predict()` returns a Verdict — confidence, evidence, receipt — never a float |
| `blind` is physical | blinded columns are **deleted from the matrix** before fitting *and* before inference |
| Independence is checked | feature legs must pass a VIF gate or the fit **halts** |
| Abstain is a result | outside the learned support, it returns ABSTAIN rather than extrapolating |

Two further obligations exist only because this thing *learns*, and they have no
counterpart in a one-shot rule:

| Obligation | Why learning needs it |
|---|---|
| **Sealed test set** | the split is fixed by a hash of the row id, not by a shuffle we could re-roll until it flattered us |
| **No self-training** | the learner may never fit on its own outputs — `∂F_out/∂F_gen = 0`. A model that learns from its own predictions manufactures confidence from nothing |

---

## Data

`cohort-audit/data/govphys_quadratic_results.csv` — 992 real repositories,
committed, already independently re-analysed elsewhere in this repository.

- **Outcome `E`**: 1 = survived, 0 = failed. Measured from lifecycle metadata only.
- **Features offered**: `U` (capacity), `D_enc`, `D_dec`.
- **Blinded**: `stars` and `archived`.
  `archived` is a **direct component of the outcome definition** — leaving it in
  would let the model read the answer. `stars` is the capacity proxy already
  present as `U`. Both are deleted before fitting, not down-weighted.
- **Split**: deterministic. `sha256(repo_name)` → hex; test set is the ~30% whose
  first hex digit is in `{0,1,2,3,4}`. No shuffling, no seed to re-roll.

---

## Pre-registered predictions

- **L1 — the learner declines.** On the sealed test set it returns ABSTAIN for at
  least **10%** of rows. *Falsified if* it answers everything: a learner that never
  declines has not learned where its support ends.

- **L2 — selective prediction pays.** Accuracy on the rows it **did** answer is
  **strictly greater** than accuracy on all rows scored blindly.
  *Falsified if* answering everything is as good — in which case abstention is
  costing coverage and buying nothing, and that is worth knowing.

- **L3 — blinding is physical.** Adding an adversarial column that perfectly
  encodes the outcome, then blinding it, produces a **bit-identical** model to one
  trained without the column at all. *Falsified if* any parameter differs.

- **L4 — the independence gate halts.** A feature set whose two legs are the same
  column produces **zero predictions** and a halt reason. *Falsified if* it warns
  and proceeds.

- **L5 — no bare return exists.** Every output carries confidence, evidence and a
  receipt. *Falsified if* any path returns a float.

- **L6 — self-training is refused.** Attempting to fit on the learner's own
  predicted labels raises. *Falsified if* it silently accepts them.

- **L7 — calibration is reported, not assumed.** Expected calibration error on the
  answered rows is measured and printed **whatever it is**. There is no gate on
  it: this is a measurement, and a bad number is published at the same size as a
  good one.

**No threshold above will be altered after the results are seen.**

---

## What this is not

1. **Not a claim to be a good predictor.** The gates test *governance properties*,
   not predictive power. A perfectly governed learner can be useless, and L7 exists
   to make that visible rather than deniable.
2. **Not a general ML framework.** One binary outcome, three features, a logistic
   fit in pure Python. The obligations are the contribution; the model is the
   smallest thing that can carry them.
3. **Not fairness-tested.** Blinding a column is not fairness. A blinded feature
   can be reconstructed from correlated ones, and nothing here checks for that.
4. **Not a replacement for the analysis it learns from.** The 992-row verdict was
   established by a pre-registered statistical test, not by this model.
