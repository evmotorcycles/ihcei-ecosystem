# The same audit, applied to the three remaining cohorts — Yeast 4825, GitHub 992, digital swarm

**One command:** `python3 cohort-audit/cohort_audit.py` · stdlib · offline · `$0`

The knowledge-cohort audit (PR #111) did two things: it **retracted** a real-world claim (the
N=793 fixture is synthetic) and it **falsified** a pre-registered thesis. Consistency demands the
same audit be applied to the three cohorts that were never audited. This module does that — and
finds **two more claims that this repository cannot substantiate offline**.

> **`exit 0` means "the audit reproduces, including its declared gaps" — not "all cohort claims
> are supported."**

---

## What the audit found

| cohort | status | detail |
|---|---|---|
| **Yeast 4825 — channel invariants** | ✅ **REAL, reproducible** | STRING v12 (taxon 4932), **4,825 proteins / 70,201 edges**, raw file committed and hash-verified. Measured **VIF = 1.0026**, reproducing the reported ≈1.003; collinear control rejected (VIF → ∞). |
| **Yeast 4825 — outcome coupling** | ⛔ **NOT offline-reproducible** | **No gene-essentiality labels are committed anywhere** (no DEG file, no ORF map). The reported *ΔAIC ≈ −1805 / quadratic AUC ≈ 0.47* **cannot be reproduced here.** |
| **GitHub 992** | ⛔ **NOT offline-reproducible** | **The 992 rows were never committed** — `lism-cohorts/results_meta.json` stores only a spec *hash*. The reported *N=992, 750 fail / 242 survive, linear AUC ≈ 0.73* is not backed by committed data. |
| **GitHub τ_v (N=21)** | ✅ **REAL, but underpowered** | 21 real repos with real lifecycle labels — **4 failed / 17 survived**. |
| **Digital swarm** | 🔶 **SIMULATION** | `stage3_swarm.py` self-declares *"simulates the swarm"*; n_nodes=500 from a fixed seed. **Zero real-world evidence.** |
| **Knowledge 793** | 🔶 **SIMULATION** | Already retracted in PR #111. |

**Two cohort claims are not offline-reproducible; two "cohorts" are simulations.**

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

**Not backed:** the yeast outcome-coupling result, and the entire N=992 GitHub cohort.

**To close these gaps** the underlying data must be committed: a yeast essentiality label file
keyed to ORFs, and the 992 labelled repository rows. Until then the status stays as recorded —
`test_cohort_audit.py` asserts each gap, so no cohort can be silently upgraded.

---

## Gates (spec `96a33ebf…`, locked before running)

- **C1** yeast channel independence on real STRING v12 — **PASS** (VIF 1.0026, control rejected, raw hash matches)
- **C2** yeast outcome-coupling gap — **PASS by correctly detecting the absence** of essentiality labels
- **C3** τ_v separation, real labels, N=21 — **direction holds (AUC 0.956), declared underpowered**
- **C4** GitHub 992 gap — **PASS by correctly detecting** that no 992-row artifact is committed
- **C5** swarm is a labelled simulation that reproduces from its seed — a **code-correctness** check, not evidence
- **C6** cross-cohort integrity ledger emitted, with **≥1 not-reproducible cohort** (the audit does not whitewash itself)

## A correction: the gap-closure results were machine-dependent

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
