# The cohorts of every telemetry law — probabilistic and deterministic

**One command:** `python3 deterministic-cohorts/det_cohorts.py` · stdlib · offline · `$0`

`E = U·D` earned trust because it was tested on real cohorts — yeast, GitHub, knowledge,
swarm. The **deterministic** laws deserve the same. This states the evidence base of every
telemetry law in the stack, and grounds the threshold law `D ≥ D_min` on four real substrates.

---

## The evidence base of each law

### `E = U·D` — linear, **probabilistic** (the *Duniya* incubator regime)
The tolerant, noisy channel where nodes have runway (`τ_v`) to self-correct.
- **yeast interactome** N = 4,825 (VIF 1.003) · **GitHub cohort** N = 992 · **knowledge / StackExchange** N = 793 · **digital swarm** (N ≥ 434)
- `τ_v` enforcement-latency: GitHub issue-close · bioRxiv publication latency · PubMed retraction-burden concentration

### `D ≥ D_min` — threshold, **deterministic** (the *Aakhirah* terminal gate)
The hard gate applied to a completed ledger once time is integrated out — a candidate clears
the bar or it doesn't. **This module's cohorts** (all real binary gates):

| substrate | deterministic gate | counts | survival s |
|---|---|---|---|
| **GitHub** | CI + review → merge | 18,631 merged / 4,270 unmerged | **0.789** (0.72–0.84) |
| **PubMed** | integrity → not retracted | 7,804,691 papers / 12,690 retracted | **0.99837** |
| **HuggingFace** | reports benchmark eval evidence | 1 / 19 models | **0.053** |
| **bioRxiv** | journal publication | 40 published, no control | **survivor-only → untestable** |

### `F_out = F_eval` — decoupling, **deterministic** (generator / evaluator)
Output fidelity = the evaluator's, independent of the generator's honesty.
- the knapsack **FunSearch sim** (D1–D5: honest 400 = lying 400, gap 0)
- the **`reproduce_all` catch-record** — it rejected a synthetic Kaggle CSV, a fabricated GILT
  script, and an OpenAlex-null spin (real, dated evidence in git history)

---

## Results (pre-registered, spec `bf336fa2…`)

```
DG1 gates are binary/deterministic (integer pass/fail counts)   → PASS
DG2 every measurable gate is a genuine filter (0<s<1)           → PASS
DG3 D_min is a real bar (survival spread 19.0× ≥ 3)             → PASS
    strict HF eval-gate 0.053 … lax-failure PubMed 0.99837
DG4 bioRxiv publication pass-rate DECLARED UNTESTABLE           → PASS
```

**The key finding — `D_min` is real and gate-specific, not a universal constant.** The four
gates survive at wildly different rates (0.05 → 0.998, a 19× spread) precisely because each
sets its bar in a different place: HuggingFace almost never demands benchmark evidence, GitHub
merges most reviewed PRs, PubMed retracts only a tiny fraction. Each is nonetheless a **binary,
deterministic** gate — pass or fail, no smooth score.

**bioRxiv stays honest.** The frozen cohort is publication *survivors* only — there is no
unpublished control group — so the publication-gate pass-rate is **untestable**, exactly like
the `E = U·D` coupling was on bioRxiv. Declared, not spun.

---

## The two-regime frame (Layer-3, kept separate from the measurements)

> Two corrections honored from the OQM/GT framing: it is **Duniya** (an earlier "Dune" was a
> hallucination), and **Barakah (E) is probabilistic** — the Duniya/linear regime, `laʿalla` =
> expectation-without-certainty — *not* deterministic. The deterministic regime is the
> **terminal selection gate** `D ≥ D_min` (Aakhirah), with `D = D_enc · D_dec` (Ṣalāt · Zakāt),
> two independent hops that multiply.

- **Duniya (incubator):** `E = U·D`, tolerant, noise-forgiving, `τ_v` runway for self-correction.
- **Aakhirah (terminal):** `D ≥ D_min`, a hard deterministic gate on the completed ledger.

These are interpretive labels for *why* two regimes exist; the numbers above are the Layer-1
measurements and stand on their own.

## Files

```
deterministic-cohorts/
  prereg/det_cohorts_prereg.json    spec (locked) + the full cohort table + corrections
  prereg/MANIFEST.sha256.json       spec + the 4 referenced fixtures, hash-pinned
  det_cohorts.py                    reads the frozen fixtures; computes binary-gate survival
  test_det_cohorts.py               pytest guard (DG1–DG4 + fixture pinning)
  results_det_cohorts.json          emitted results
```

Layer-1, offline, `$0`. The deterministic laws now have their cohorts, just like `E = U·D`.
