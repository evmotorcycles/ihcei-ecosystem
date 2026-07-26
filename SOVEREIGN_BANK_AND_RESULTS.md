# Where the results leave LISM — and a banking design, rigorously tested

*Four things: (1) what the new results mean for LISM and its four cohorts, (2) why the
Knowledge Exchange actually failed, (3) a banking architecture built on that diagnosis,
(4) a **pre-registered test of that architecture on real GitHub projects — which came
back 2/4, with my central prediction falsified.** Every number below re-run, offline,
`$0`.*

---

## 1. Where the four cohorts leave LISM

| Cohort | Status | What it does / doesn't support |
|---|---|---|
| **Yeast 4,825** | ✅ real, gap closed | Channel intact (VIF 1.0026); CV AUC **linear 0.666 > quadratic 0.591**. Coupling is linear. **Load-bearing.** |
| **PyPI 434-package graph** | ✅ real | Quadratic adds **Δ 0.000**. Independent confirmation on a technical substrate. **Load-bearing.** |
| **GitHub 992** | ⛔ not reproducible | Rows never committed. **Cannot be cited.** |
| **Knowledge 793** | 🔶 synthetic | Retracted as real-world; estimator control only. **Zero evidence.** |
| **Digital swarm** | 🔶 simulation | A seeded sim reproducing itself. **Zero evidence.** |

**The honest position:** LISM's linear coupling law now rests on **two** independent,
non-circular, offline-reproducible substrates — one biological (survival), one technical
(dependency structure). That is a narrower but far firmer base than the four-cohort
story, because the two that carried no evidence have been labelled and the one that
can't be reproduced has been excluded.

Also corrected: the published **"quadratic anti-predictive, AUC ≈ 0.47"** is a
non-converged solver artifact (in-sample 0.4275, `converged = False`). Under a converged
fit the quadratic scores 0.591 — above chance, still beaten by linear. *The conclusion
survives; the number is retired.*

## 2. Why the Knowledge Exchange failed — the actual diagnosis

The pre-registered claim was that fidelity-adjusted capacity would out-predict raw
status at explaining knowledge yield. It failed badly:

| Real substrate | ρ status alone | ρ fidelity-adjusted |
|---|--:|--:|
| Hugging Face · likes → downloads (N=19) | **+0.4035** | +0.0123 |
| GitHub · stars → forks (N=28) | **+0.8763** | +0.5140 |

**The failure was a construct conflation, not a measurement error.** The only available
yield proxies — *downloads* and *forks* — are themselves popularity measures. So the
test asked "does popularity predict popularity?" and the answer was of course yes. The
fidelity legs measured *trustworthiness*, a different axis. **The thesis conflated reach
with quality.**

The fix is not a better fidelity metric. It is a **non-circular outcome**. Which is
exactly what the banking test below uses.

## 3. The banking design (architecture — labelled, not evidence)

The design follows from the diagnosis: if you cannot read quality off prestige, an
underwriter must measure **behaviour** instead of **standing**.

| Layer | Rule | Status |
|---|---|---|
| **Reserve** | 100% full reserve. No credit creation from nothing. Riba = unearned capacity inflation (`ΔU > 0` while `D → 0`). | architecture |
| **Contract — home** | Diminishing co-ownership: joint purchase, rent on the financier's share only, share buyback, **loss shared in proportion to equity**. No repossession-with-yield-intact. | architecture |
| **Contract — SME** | Profit-participating notes tied to a *specific cash-flowing asset*. Investor absorbs capital loss; operator loses labour. No fixed guaranteed return. | architecture |
| **Evaluator** | **Ignore self-reported standing. Score on measured enforcement latency τ_v** — how fast the applicant actually clears its own open obligations. | **TESTED BELOW** |

Only the evaluator layer is testable without a bank. The reserve and contract layers
are **design, not findings**, and are labelled as such. That distinction is the whole
point of the discipline.

## 4. The test — pre-registered, and it did not go my way

**Spec locked before the data was fetched and before the runner was written:**
`fbe085fcf4cc2a7f5b3bf386a7e81f1542cda6f6f826996ca75ef41162f0d62a`

**Design.** Two underwriters compete on the *same* 27 real GitHub repositories.
Outcome = **default** (archived, or no push in >730 days) — derived from lifecycle
**only**, never from stars/forks/downloads, so it is non-circular. This is the corrected
form of the Knowledge-Exchange question.

- **Conventional (status-based):** fund the most-starred. "Prestige = safe."
- **Sovereign (decoupled):** ignore stars entirely; fund the lowest enforcement latency.

**Cohort:** N = 27, 6 defaults. Median τ_v **34.4 d (default)** vs **4.8 d (performing)**.
Median stars **16,120 (default)** vs **36,803 (performing)**.

### Results — 2 of 4 gates met

| Gate | Result | |
|---|---|:--:|
| **B1** τ_v beats stars at discrimination | AUC τ_v **0.7143** vs stars **0.7381** | ❌ **FAILED** |
| **B2** popularity is near-chance | AUC stars **0.7381**, outside the locked band [0.30, 0.70] | ❌ **FAILED** |
| **B3** decoupled book defaults less | conventional **15.4%** vs sovereign **7.7%** | ✅ passed |
| **B4** genuinely two different axes | spearman(stars, τ_v) = **−0.30** | ✅ passed |

### What this actually means — read carefully

**My central prediction was wrong, and a popular claim is refuted.**

- **"Popularity carries zero information about trustworthiness" is false** on this
  cohort. With a *non-circular* outcome, stars discriminated default at **AUC 0.74** —
  slightly *better* than enforcement latency (0.71). Prestige is not noise. Big projects
  do survive more often, and any framing that says otherwise is overstated. **That
  correction stands even though it cuts against the design I was testing.**
- **What survived is narrower and more specific.** The two signals are genuinely
  different axes (ρ = −0.30), and the *funded book* built on latency defaulted at
  **half the rate** of the prestige book (7.7% vs 15.4%). Prestige-based funding
  concentrates into large, famous, *dead* projects — angular.js (58k stars) and
  node-v0.x-archive (34k stars) are both archived and both would be funded by a
  star-ranking lender.
- **So the defensible claim is about portfolio construction, not ranking power.**
  Decoupled underwriting is justified here because of *who it funds*, not because
  latency is a better ranker. That is a materially weaker claim than the one I
  pre-registered, and it is the one I am making.

**A known confound, named but not used as a rescue.** Archival bulk-close deflates τ_v
for archived repos (angular.js closes at 7.97 d *because* its issues were mass-closed at
sunset), which actively penalises τ_v in this test. I documented this artifact
previously. It is a real limitation — but I am **not** using it to overturn the B1/B2
failures. The gates failed; that is recorded.

**Declared limits (locked in advance):** N = 27 with 6 defaults is **underpowered** — no
p-value or confidence claim is manufactured. Repository abandonment is an *analogue* of
credit default, not credit data. This tests the **evaluator layer only**.

## Reproduce

```bash
python3 sovereign-bank/underwriting_test.py     # 2/4 gates; prints both failures
python3 -m pytest sovereign-bank/test_bank.py   # asserts the failures stay failures
python3 cohort-audit/gap_closure.py             # yeast closed, 992 open, G2 miss
bash reproduce_all.sh                           # whole stack
```

`test_bank.py` asserts `auc_stars > auc_tau_v` and that both failed gates remain in
`gates_not_met`. If anyone later widens the band or flips the comparison to turn this
into a clean win, **the build breaks.**

---

*The design is not vindicated by this test — it is narrowed by it. That is what a test
that can fail is for.*
