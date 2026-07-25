# The Cohort Ledger — what this repository can actually prove

*Every empirical claim LISM rests on, audited cohort by cohort, pre-registered and
SHA-256 locked before running. One gap closed, one still open, two "cohorts" that are
simulations, one thesis falsified, and one published number corrected. Everything
below reproduces offline, `$0`, no API keys.*

```
bash reproduce_all.sh          # 57/57 ALL GREEN
```

---

## The ledger at a glance

| Cohort claim | Status | The number |
|---|---|---|
| **Yeast 4825 — channel invariants** | ✅ **REAL** | STRING v12, 4,825 proteins / 70,201 edges, **VIF = 1.0026** |
| **Yeast 4825 — outcome coupling** | ✅ **REAL — gap CLOSED** | 1,055 essential ORFs; **CV AUC linear 0.666 > quadratic 0.591** |
| **GitHub 992** | ⛔ **STILL A GAP** | rows never committed; largest labelled artifact = **22 rows** |
| **GitHub τ_v union** | ✅ **REAL** (underpowered) | **N = 33** (9 failed); median τ_v **45.4 d** vs **4.3 d** |
| **Knowledge 793** | 🔶 **SIMULATION** (retracted) | fixture declares `synthetic: true`, seed 20260720 |
| **Digital swarm** | 🔶 **SIMULATION** | source self-declares "simulates the swarm", 500 nodes, fixed seed |

**Two claims are backed by real committed data. One gap remains genuinely open. Two
"cohorts" are simulations and are labelled as such — they contribute zero real-world
evidence.**

---

## 1. Yeast 4825 — the gap is now CLOSED, and a published number is corrected

### What was missing
The audit reported *"no gene-essentiality labels are committed anywhere"*, so the
outcome-coupling claim could not be reproduced. **That is no longer true.** The labels
are committed:

- `data/yeast/scer_essential_orfs.txt` — **1,055** systematic-ORF essential labels
- `data/yeast/yeast_interactome_DEG.csv` — 4,825 rows carrying `E_essential`

Built from **raw DEG2001 (S. cerevisiae) → systematic ORFs via BioGRID**, joined to
the STRING v12 channel. Essentiality is **wet-lab data, never derived from topology** —
so the outcome is non-circular.

### What reproduces (four gates, all could have failed)

| Gate | Result |
|---|---|
| **Y1** labels join to the channel | N = **4,825**, essential = **1,055** ✅ |
| **Y2** channel intact | **VIF = 1.0026** (r = −0.0513) ✅ |
| **Y3** quadratic does not beat linear | CV AUC **0.6663** vs **0.5911** ✅ |
| **Y4** the published 0.47 is an artifact | see below ✅ |

### ⚠️ Correction: the "quadratic AUC ≈ 0.47, anti-predictive" figure is an artifact

This number is still being repeated in LISM narratives. It does not survive scrutiny:

- Under a **converged** single-term fit, the quadratic scores **CV AUC 0.5911** —
  *above* chance, not anti-predictive.
- The only way to reproduce a sub-chance value is the **non-converged** multivariate
  `U + D + D²` fit: `converged = False`, in-sample AUC = **0.4275** ≈ the published 0.47.

**So "AUC 0.47" is a separation-degenerate fitting artifact, not a finding.** The
qualitative conclusion LISM actually relies on — *adding D² does not improve
prediction* — **survives** (0.591 < 0.666). The specific number does not, and quoting
it as evidence of "anti-predictive" behaviour should stop.

## 2. GitHub 992 — still open, and not being fudged

No 992-row labelled artifact is committed anywhere. The largest labelled JSON in the
repository holds **22 rows**. Refetching 992 repositories needs roughly two API calls
each at 60 requests/hour unauthenticated — about **33 hours** — so it was not
attempted.

> **The N = 992 result (750 fail / 242 survive, AUC ≈ 0.73) must NOT be cited as
> offline-reproducible from this repository.**

This does **not** mean the original analysis was wrong. It may well have been run
correctly against data that was simply never committed. It means this repository
cannot substantiate it, which is the only thing a reproducibility claim can rest on.
`test_gap_closure.py` asserts the gap so it can never be silently closed.

### What *is* real: the τ_v union cohort — and a prediction I missed
Unioning every committed real τ_v dataset gives **N = 33** (9 failed, 24 survived),
median τ_v **45.4 d failed vs 4.3 d survived** — direction holds, and failures rose
from the audit's 4 → **9**.

**But I pre-registered N ≥ 35 and reached 33. That prediction is MISSED.** I did not
move the threshold to 30. The test asserts `union_N == 33` and that `G2` stays in
`missed_predictions`, so rescuing it later breaks CI.

## 3. Knowledge 793 — retracted as real, and the thesis falsified

Two separate things happened here, and they must not be conflated.

**The retraction.** The committed N = 793 "knowledge cohort" fixture is **synthetic** —
its own provenance says `synthetic: true, seed: 20260720`. Any narrative citing it as a
real Stack Exchange measurement (*"Cohort C, VIF 1.08, AUC 0.58"*) is **not supported**
by this repository. It is used only as a **labelled estimator control**, and it does its
job: it correctly recovers independent hops at **VIF = 1.0032**. Zero real-world
evidence.

**The falsification (K1).** The pre-registered claim — that fidelity-adjusted capacity
would out-predict raw status at explaining knowledge yield — was tested on four **real**
substrates and **failed badly**:

| substrate | ρ status alone | ρ fidelity-adjusted |
|---|--:|--:|
| Hugging Face · likes → downloads (N=19) | **+0.4035** | +0.0123 |
| GitHub · stars → forks (N=28) | **+0.8763** | +0.5140 |

*Diagnosis, not a rescue:* the only available yield proxies — downloads and forks — are
themselves popularity measures. Popularity predicts popularity. The fidelity legs
measure **trustworthiness**, a different axis. The thesis conflated reach with quality.

**What survived is sharper than the original claim:**
- **K3 confirmed** — capacity does not buy fidelity (PubMed ρ = +0.19, N=8; bioRxiv ρ = −0.09, N=40).
- **K4 confirmed** — prestige ordering ≠ verified ordering; all 5 of GitHub's most-starred repos sit below the fidelity floor.
- **K2 partial FAIL, not papered over** — GitHub VIF **1.1741** exceeds the pre-registered **1.10** gate (still far under the standard 5.0). **Threshold not moved.**

**The corrected conclusion:** it is *not* that fidelity predicts reach — it plainly
doesn't. It is that **reach and trustworthiness are separate, measurably different
orderings**. That is precisely why an evaluator must measure fidelity *separately*
instead of inferring it from popularity — now motivated by a falsification rather than
an assumption.

## 4. Digital swarm — a label, plus a falsifiable substitute

The swarm source self-declares *"simulates the swarm"* (500 nodes, fixed seed). **A
seeded simulation reproducing itself is a code-correctness check, not evidence.** In
the test suite this gate is explicitly marked `falsifiable: false`, and an assertion
prevents it from ever being counted as support.

The swarm's *substantive* claim — linear ≥ quadratic on a dependency network — was
therefore tested on something that can fail: a **real 434-package PyPI dependency
graph**. Result: CV AUC `U+D` = **0.590** vs `U+D+D²` = **0.590** (Δ +0.000). The
quadratic adds nothing **on real data**.

---

## What this does and does not mean for LISM

**It does not disprove the LISM mathematics.** Nor does it suggest the original yeast
or GitHub analyses were run incorrectly — they may have been run correctly against data
never committed here.

**What now stands on committed, reproducible data:**
- the yeast channel is genuinely intact (VIF ≈ 1.00) — the two-hop test is valid;
- the yeast **outcome coupling** reproduces, and the quadratic adds nothing;
- on a real dependency graph, the quadratic again adds nothing;
- τ_v separates failing from surviving repositories in the right direction (N = 33, underpowered).

**What does not:**
- the **N = 992** cohort (rows never committed);
- any real-world reading of the **N = 793** knowledge cohort (synthetic);
- the swarm as evidence (simulation);
- the **"quadratic AUC 0.47"** figure (non-converged artifact).

**The precise, defensible statement** — replacing "robustly validated across Yeast
N=4,825 and repository-lifecycle N=992" — is:

> The linear form is supported on the yeast interactome (N = 4,825, channel VIF 1.0026,
> CV AUC linear 0.666 > quadratic 0.591) and on a real 434-package dependency graph
> (quadratic Δ = 0.000), with a directionally consistent but underpowered τ_v cohort
> (N = 33). The N = 992 repository cohort is not offline-reproducible from this
> repository and is not cited as support.

---

## Reproduce everything yourself

```bash
python3 cohort-audit/cohort_audit.py       # the ledger: gaps + simulations
python3 cohort-audit/gap_closure.py        # yeast CLOSED, 992 open, G2 miss recorded
python3 knowledge-breakthroughs/knowledge.py   # the falsification, on real substrates
python3 repro/reproduce_yeast.py           # VIF from raw STRING v12, no network
python3 repro/verify_github_ci.py          # attests the archived 992 CI run
bash reproduce_all.sh                      # 57/57 ALL GREEN
```

**`exit 0` means "reproduces as pre-registered, INCLUDING gaps left open, nulls, and
predictions missed."** It does **not** mean every claim held. Several did not — and the
tests assert those failures so they cannot later be flipped into wins.

### Locks

| Item | SHA-256 |
|---|---|
| gap-closure spec (canonical) | `f8a94c655dc0ec5c9add082114dd7048a5d148827fd6e0cb33226461c3dbd03a` |
| provenance merkle root | `478547943d4403fa005b15c9451e228697925e054e370ebd5ce0e5959b7a567a` |

Pre-registered and locked **before** the runners were written, so a runner cannot be
tuned to produce its own predictions. Offline, `$0`, deterministic.

*Novora Research Initiative — methodology, not speed. Finding the gap is the result.*
