# The same audit, applied to the three remaining cohorts — Yeast 4825, GitHub 992, digital swarm

**One command:** `python3 cohort-audit/cohort_audit.py` · stdlib · offline · `$0`

The knowledge-cohort audit (PR #111) did two things: it **retracted** a real-world claim (the
N=793 fixture is synthetic) and it **falsified** a pre-registered thesis. Consistency demands the
same audit be applied to the three cohorts that were never audited. This module does that.
It originally found **two more claims this repository could not substantiate offline**. Both have
since been closed by committing the underlying data — the history is kept below, because how a
gap closes matters as much as that it closed.

> **`exit 0` means "the audit reproduces, including its declared gaps" — not "all cohort claims
> are supported."**

---

## What the audit found

| cohort | status | detail |
|---|---|---|
| **Yeast 4825 — channel invariants** | ✅ **REAL, reproducible** | STRING v12 (taxon 4932), **4,825 proteins / 70,201 edges**, raw file committed and hash-verified. Measured **VIF = 1.0026**, reproducing the reported ≈1.003; collinear control rejected (VIF → ∞). |
| **Yeast 4825 — outcome coupling** | ✅ **CLOSED** | Essentiality labels now committed (1,055 essential ORFs). CV AUC linear 0.666 > quadratic 0.591. The published *quadratic AUC ≈ 0.47* reproduces **only** as a non-converged multivariate fit (in-sample 0.4275) — an artifact, and recorded as one. |
| **GitHub 992** | ✅ **CLOSED — real, reproducible** | The 992 rows are now committed at `cohort-audit/data/`. Independently re-analysed: 750 fail / 242 survive, VIF 1.0203, ΔAIC −3.48, **QUADRATIC DISCONFIRMED**. See the closure section below. |
| **GitHub τ_v (N=21)** | ✅ **REAL, but underpowered** | 21 real repos with real lifecycle labels — **4 failed / 17 survived**. |
| **Digital swarm** | 🔶 **SIMULATION, reproducible from seed** | `stage3_swarm.py` self-declares *"simulates the swarm"*; n_nodes=500 from a fixed seed. It reproduces exactly — but reproducing a simulation is a **code-correctness** check, not evidence about the world. |
| **Knowledge 793** | 🔶 **SIMULATION** | Already retracted in PR #111. |

**Current state: 0 cohort claims remain not offline-reproducible.** Two were closed by committing
the data they depended on. The swarm and the retracted knowledge cohort are still labelled
simulations, and reproducing a simulation is not evidence about the world.

---

## The one genuinely new empirical result

### C3 — enforcement latency does separate failed from surviving repositories (real labels)
```
failed   n=4   median τ_v = 121.7 days
survived n=17  median τ_v =   4.0 days
AUC(τ_v discriminating failed from survived) = 0.9559     (prediction was AUC > 0.5 → direction HOLDS)
```
Failing repositories take **~30× longer** to close their own issues. The direction is exactly as
predicted — **but with only 4 failures this is severely underpowered.** Even this strong-looking
AUC is **weak evidence**, and no p-value or confidence claim is manufactured from it. That caveat
is asserted in the test so it stays attached to the number.

---

## What this does and does not mean

**It does not disprove the LISM mathematics**, and it does not show the original yeast or GitHub
analyses were wrong — they may well have been run correctly against data that simply was never
committed to this repository. What it establishes is narrower and more important:

> **Precisely what this repository can substantiate offline** — which is the only thing a
> reproducibility claim can honestly rest on.

**Backed by committed real data:** the yeast channel-independence invariant (VIF ≈ 1.00 at
N=4,825), the real τ_v separation (N=21, underpowered), and the HF/bioRxiv/PubMed substrates.

**Both gaps are now closed the only way a gap can honestly close** — by committing the data they
depended on: the yeast essentiality labels keyed to ORFs, and the 992 labelled repository rows.
`test_cohort_audit.py` and `test_992.py` assert the closure conditions, so no cohort can be
silently upgraded on a flag alone.

---

## Gates (spec `96a33ebf…`, locked before running)

- **C1** yeast channel independence on real STRING v12 — **PASS** (VIF 1.0026, control rejected, raw hash matches)
- **C2** yeast outcome-coupling gap — **CLOSED**: essentiality labels committed; published AUC 0.47 recorded as a non-converged artifact
- **C3** τ_v separation, real labels, N=21 — **direction holds (AUC 0.956), declared underpowered**
- **C4** GitHub 992 gap — **CLOSED**: the 992-row artifact is committed and its summary recomputes from the raw rows
- **C5** swarm is a labelled simulation that reproduces from its seed — a **code-correctness** check, not evidence
- **C6** cross-cohort integrity ledger emitted and **derived from the data, never asserted** — the banner previously hardcoded a gap its own ledger had already closed

## The N=992 gap is now CLOSED — and here is the full sequence

This gap went through three states. All three are recorded, because the sequence
is the point.

| # | State | Why |
|---|---|---|
| 1 | **Reported closed** | `results_gapclosure.json` said the artifact was "found at `govphys_quadratic_results.csv`". |
| 2 | **Corrected to open** | That file was **gitignored and never committed**. True on one machine, false from a clean clone. |
| 3 | **Genuinely closed** | The CI artifact was deposited at `cohort-audit/data/`, **committed**, and independently re-analysed. |

State 2 was not pedantry: a result that only exists on the machine that produced
it is not a reproducible result, whatever the flag says.

**What closes it now** is not a flag. It is 992 rows in the repository, plus an
independent re-analysis that recomputes the verdict rather than reading it:

```
python3 cohort-audit/verify_992.py
```

| Quantity | Recomputed from rows | Published summary | |
|---|---|---|---|
| N total / failed / survived | 992 / 750 / 242 | 992 / 750 / 242 | match |
| Pearson r(D_enc, D_dec) | 0.1412 | 0.1412 | match |
| VIF (gate < 5) | **1.0203** | 1.0203 | match |
| AIC linear | 1088.215 | 1088.215 | match |
| AIC quadratic | 1091.698 | 1091.698 | match |
| ΔAIC (lin − quad) | **−3.483** | −3.483 | match |
| τ_v mean, failed / survived | 50.61 / 19.76 d | 50.61 / 19.76 d | match |
| **Verdict** | **QUADRATIC_DISCONFIRMED** | QUADRATIC_DISCONFIRMED | match |

The pre-registration lock holds: the spec SHA-256 printed by the CI run,
`cac34f44…01f7`, recomputes exactly from the docstring of the committed
`govphys_quadratic_prereg_test.py`. The run executed the design that is in this
repository, and the design was fixed before the first fetch.

### What this verdict does and does not say

- It says the **quadratic earned nothing**: ΔAIC ≤ 0 under a rule written before
  any data was seen, with the channel-intact gate (VIF 1.02 < 5) and the
  failing-region gate (750 ≥ 100) both **met, not waived**.
- It does **not** prove the linear law. "The quadratic added nothing here" is a
  narrower claim than "the linear relation is correct", and only the first is
  supported.
- The permutation z of ~9.2 is **not** evidence for the quadratic. It measures
  how far the observed ΔAIC sits from a permuted null; the observed ΔAIC is
  negative, so a large z here describes the null's tightness, not support.

### Two blemishes worth stating

1. The summary field is named `primary_dAIC_quad_minus_lin` but holds
   `AIC_lin − AIC_quad`. The value and the verdict follow the pre-registration
   correctly; **the label is backwards**, and anyone reading the JSON without the
   spec could invert the conclusion.
2. τ_v was imputed for **15.5%** of failed and **4.1%** of survived repositories.
   The imputation pulls failures toward the survivor value, so the τ_v separation
   is if anything **understated** — but a reader is entitled to know the fraction
   before trusting the gap.

## A correction that came before it: the gap-closure results were machine-dependent

`results_gapclosure.json` was at one point committed in a state reporting
**`G1_992_gap_closed: pass`**, with the detail *"992-row labelled artifact found at
`govphys_quadratic_results.csv`"*.

That file is **gitignored and has never been committed**. It is produced by
`govphys_quadratic_prereg_test.py`, which fetches live from the GitHub API. So the
result was true on the machine that generated it — and **not reproducible from a fresh
clone**, which is the only claim this repository is entitled to make.

Re-running `gap_closure.py` on a clean checkout produces the honest state, and that is
what is now committed:

> `G1_992_cannot_be_closed_offline` — no 992-row labelled artifact committed (largest
> labelled JSON/CSV = 22 rows); **GAP REMAINS OPEN** — the N=992 result must not be
> cited as offline-reproducible.

The expanded-cohort gate **G2** goes the same way: it reported `union N=1025` on that
machine and reports `union N=33` on a clean checkout, so **G2 now fails**, honestly.
The direction of the τ_v separation still holds at the smaller N; the sample size does
not support what was previously recorded.

Nothing was retuned to recover the pass. The failing state is the committed state,
which is what the README table above said all along — the JSON had drifted away from
it, not the other way round.

## Files

```
cohort-audit/
  prereg/cohort_prereg.json      spec (locked) — provenance findings declared BEFORE testing
  prereg/MANIFEST.sha256.json     spec + 4 committed fixtures, hash-pinned
  cohort_audit.py                 the audit runner
  gap_closure.py                  the follow-up gap-closure run
  test_cohort_audit.py            pytest guard — locks the GAPS as hard as the positives
  test_gap_closure.py             pytest guard for the gap-closure run
  results_audit.json              emitted results + the integrity ledger
  results_gapclosure.json         gap-closure results, from a CLEAN checkout only
```

Layer-1, offline, `$0`, deterministic. Methodology, not speed. **The gaps are the finding.**
