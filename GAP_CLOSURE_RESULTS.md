# Gap closure: one gap closed, one stays open, one prediction missed

*Answers "these were not committed and made reproducible." Pre-registered and
SHA-256 locked **before** the runner was written
(`cohort-audit/prereg/gapclosure_prereg.json`, canonical `f8a94c65…`), then run.
Reproduce: `python3 cohort-audit/gap_closure.py`. Full stack: `bash reproduce_all.sh`
→ **57/57**.*

---

## Headline

| Cohort claim | Before | After | Why |
|---|---|---|---|
| **Yeast 4825 — outcome coupling** | ⛔ gap | ✅ **CLOSED** | ORF-keyed essentiality labels **are** committed; the coupling reproduces offline |
| **GitHub 992** | ⛔ gap | ⛔ **still open** | the 992 rows were never committed; cannot be refetched within rate limits |
| **Digital swarm** | 🔶 sim | 🔶 **still a simulation** | but its substantive claim now has a *real-data* analogue that can fail |
| **G2 expanded cohort** | — | ❌ **prediction missed** | predicted N ≥ 35, reached **33**. Threshold not moved. |

**7 of 8 gates met. The one miss is recorded permanently and asserted in a test.**

## 1. The yeast gap was closable — the labels were already committed

The audit searched for a committed gene-essentiality artifact and reported
`label source found: False`. That is no longer true. The labels exist:

- `data/yeast/scer_essential_orfs.txt` — **1,055** systematic-ORF essential labels
- `data/yeast/yeast_interactome_DEG.csv` — 4,825 rows carrying `E_essential`

They were built from **raw DEG2001 (S. cerevisiae) → systematic ORFs via BioGRID**,
joined to the STRING v12 channel. Essentiality is wet-lab data; it is **never derived
from topology**, so the outcome is non-circular.

### What reproduces now (all four gates could have failed)

| Gate | Result |
|---|---|
| **Y1** labels join | N = **4,825**, essential = **1,055** ✅ |
| **Y2** channel intact | VIF(D_enc, D_dec) = **1.0026** ✅ |
| **Y3** quadratic not better | CV AUC linear **0.6663** > quadratic **0.5911** ✅ |
| **Y4** published 0.47 is an artifact | single-term quadratic CV AUC **0.5911** (*above* chance); multivariate `U+D+D²` **converged = False**, in-sample AUC **0.4275** ✅ |

**The Y4 number is the important one.** The published claim was "quadratic
anti-predictive, AUC ≈ 0.47." Under a *converged* fit the quadratic scores 0.59 —
above chance. The only way to reproduce a sub-chance value is the **non-converged**
multivariate fit, which returns **0.4275** — essentially the published 0.47. That
pins the published figure as a **separation artifact**, not a finding. The
qualitative conclusion the manuscript relies on (adding D² does not help) survives;
the specific number does not, and is now corrected in the record.

## 2. GitHub 992 — still open, and I am not pretending otherwise

No 992-row labelled artifact is committed (largest labelled JSON found: **22 rows**).
Refetching would need ~2 API calls per repo at 60 req/hr unauthenticated — roughly
**33 hours** — so it was not attempted. **The N=992 result must not be cited as
offline-reproducible from this repository.** The test asserts this gap can never be
silently closed.

## 3. The G2 miss — reported, not rescued

I pre-registered: the union of every committed real τ_v dataset would reach
**N ≥ 35 with ≥ 8 failures** and the direction would hold.

- Reached: **N = 33** (failed **9**, survived 24) — **missed the N threshold by 2**
- Direction: **held strongly** — median τ_v failed **45.4 d** vs survived **4.3 d**
- Failures rose from the audit's 4 → **9**, materially improving power

I did **not** move the threshold from 35 to 30. `test_gap_closure.py` asserts
`union_N == 33` and that `G2` remains in `missed_predictions`, so lowering the bar
after the fact breaks CI.

## 4. The swarm — a label, plus a falsifiable substitute

**S1** (swarm is a simulation) is a *provenance label and cannot fail* — it is
explicitly marked `falsifiable: false` and contributes zero evidence. The test
asserts it can never be counted as evidence.

**S2** carries the actual weight: the swarm's substantive claim (linear ≥ quadratic
on a dependency network) tested on a **real 434-package PyPI graph** — CV AUC
`U+D` = 0.590 vs `U+D+D²` = 0.590 (Δ +0.000). Quadratic adds nothing **on real
data**. That gate could have failed.

## 5. What changed in the audit itself

The audit's C2 gate originally passed by *detecting an absence* (`pass = not
labels_found`), so committing the labels made it **FAIL** — correct behaviour, and
the signal that the state had changed. It is now **state-aware** and honest in both
worlds:

- no labels committed → gap correctly declared → PASS
- labels committed **and** the coupling verified → gap closed → PASS
- **labels committed but coupling unverified → FAIL** (the dangerous case: a cohort
  quietly upgraded without the result holding)

Its stale narrative and hardcoded summary ("no essentiality labels committed", "these
four claims") were corrected; the ledger now computes the gap count instead of
asserting it. Provenance was re-locked: `2f638700…` → **`478547943d…`** (72 files).

## Reproduce

```
python3 cohort-audit/gap_closure.py     # the pre-registered protocol; exit 0 == reproduces
python3 cohort-audit/cohort_audit.py    # the updated audit ledger
bash reproduce_all.sh                   # 57/57 ALL GREEN
```

`exit 0` means **"reproduces as pre-registered, including gaps left open and
predictions missed"** — it does **not** mean every prediction held. One did not.

spec sha256 (canonical): `f8a94c655dc0ec5c9add082114dd7048a5d148827fd6e0cb33226461c3dbd03a`
provenance merkle root: `478547943d4403fa005b15c9451e228697925e054e370ebd5ce0e5959b7a567a`
