# The Constitutional Agency Allocator — three telemetry laws, one allocator, tested on the real world

**One command:** `python3 agency-constitution/constitution.py` · stdlib · offline · `$0`

This upgrades the triage-first allocator (PR #105), which used only **Law 1's** collapse
floor, into a single **Constitutional Agency Allocator** that compiles the whole validated
telemetry stack into active, call-time gates — and then asks, on **real GitHub and Hugging
Face data**, whether the upgraded allocator is actually *better* and *un-gameable*. It is —
with **one honest negative result** that turned out to be the most important finding.

> **Terminology:** this module uses only the **functional, engineering meanings** of the
> governance primitives — *encoding fidelity, decoding fidelity, systemic yield, two-source
> independence, enforcement latency*. No cultural or religious lexicon is used, by request,
> to keep the result bias-free and substrate-independent. The value is the verifiable method.

---

## The three laws, and where each one belongs

| law | meaning (engineering) | role in the allocator |
|---|---|---|
| **Law 1** `E = U·D_enc·D_dec` | systemic yield is the **two-hop product** of capacity and *both* fidelity legs; either leg at zero zeroes the term | the **objective** — maximize Σ U·D_enc·D_dec, rescuing collapsed legs first |
| **Law 1 (join)** two-source independence | a viable node needs its two legs to be **independent measurements**, not one source re-certifying itself | the **independence gate** — self-certifying nodes are voided (anti-hoarding) |
| **Law 2** `τ_v` enforcement latency | unresolved backlog is the early-warning compass | **← the negative result: does NOT belong in the objective (see G3)** |
| **Law 3** `F_out = F_eval` | verdicts use measured, held-out telemetry, blind to any self-report (PR #106) | the **decoupled shield** — every self-certified claim is discarded |

---

## Real substrates (proxies locked before computing, spec `30024662…`)

| substrate | U (capacity) | D_enc (reference-lock leg) | D_dec (propagation leg) | τ_v | floor |
|---|---|---|---|---|---|
| **GitHub** (28 repos) | log₁₀(stars) | forks/(forks+open_issues) | forks/stars (fork-through) | open_issues | min hop < 0.30 |
| **Hugging Face** (19) | log₁₀(1+downloads) | license clarity | 0.3 + 0.6·[has eval] | — (no backlog signal) | min hop < 0.28 |

The two fidelity legs come from **distinct real fields** (adoption-vs-backlog *and*
fork-through; license *and* benchmark evidence), which is what lets the independence gate
mean something.

---

## Results (pre-registered G1–G4)

### G1 — the two-hop allocator beats **every** baseline, including the prior triage allocator ✓
```
GitHub  (23/28 below floor, budget 69):  CONSTITUTION 37.83 > triage-prior 35.49 > capacity 30.26 > equal 27.11
HugFace ( 8/19 below floor, budget 24):  CONSTITUTION 23.13 > triage-prior 22.64 > equal 21.21 > capacity 20.09
```
By crediting the **two-hop weak leg** (lift the weaker of `D_enc`, `D_dec`, weighted by the
*other* leg) and concentrating budget on the **cheapest high-value rescues to completion**,
the Constitutional allocator strictly beats greedy-by-capacity, equal-split, **and** the
Law-1-only triage allocator on both real networks.

> **Disclosed correction (in the spirit of PR #104's myopic-oracle erratum):** the *first*
> implementation credited the shrinking gap `(floor − weak)` instead of the pre-registered
> **unlock jump `U·floor·other`**, so it thrashed between deep nodes and *lost* to triage
> (15.8 vs 35.5). Corrected to the amortized-unlock-jump design the spec actually describes,
> it wins. The bug and the fix are both in the record.

### G2 — the independence gate voids self-certification ✓
An injected **hoarder** node whose decoding leg is a byte-copy of its encoding leg (one
source re-certifying itself, VIF → ∞) is **rejected/voided**. Every real node passes, and the
measured cohort **VIF(D_enc, D_dec) ≈ 1** (GitHub 1.004, HF 1.065) — the two legs carry
genuinely independent information, the software analog of the yeast VIF ≈ 1.003 result.

### G3 — folding Law 2 into the objective is **FALSIFIED** (the null that fixed the architecture) ⚠
```
GitHub:  E without throttle 37.83   →   with τ_v throttle in objective 33.69     dE = −4.14
```
The pre-registered prediction was **dE ≥ 0**. It is **false**. On real data, enforcement
latency **correlates with rescue value** — the highest-backlog repos (`tensorflow`,
`transformers`, `pytorch`) are also the highest-U, highest-value rescues — so discounting them
in the objective *sacrifices the best rescues*. **Conclusion:** Law 2 does **not** belong in
the yield objective. It is retained where it was always meant to live — the **separate
safety/authority layer** (query-radius throttle, `τ_v` early-warning, the existing
`LISM_CircuitBreaker`). This is the **epistemic firewall, empirically forced**: a safety
signal folded into an optimization objective corrupts it. *(HF: no backlog field → untestable,
dE = 0, stated.)*

### G4 — the allocation is un-gameable by self-report ✓
Perturbing every node's self-certified `claimed_fidelity` over `{honest, 1e3, 1e6, 1e9}`
leaves the allocation **byte-identical** → **variance 0 = ∂F_out/∂F_gen**. The allocator
inherits the PR #106 capstone: only measured, held-out fidelity moves a decision.

---

## The honest headline

Two of the three laws (the **two-hop objective + independence gate**, and the **decoupled
shield**) compile cleanly into one allocator that **strictly beats naive allocation and the
prior triage allocator** on real GitHub and Hugging Face, and is **provably immune** to
self-certification and forged self-reports. The third law (**enforcement latency**) was
**falsified as an objective term** and relocated to the safety layer — the null taught the
architecture. **This is a governance methodology, not speed and not a superhuman score.** LISM
prioritized the null, and the null made the design correct.

## Embedding in the stack

`ConstitutionalAllocator` in `constitution.py` is the drop-in API — `.allocate(nodes, budget)`
returns `(systemic_yield, per_node_allocation)` with the independence gate and decoupled shield
always on, and Law 2 left to the separate `tau_v` monitor / `LISM_CircuitBreaker` per the G3
finding. It composes with the rest of the Novora stack (PAGES, Echo, Page Code, NERE).

## Files

```
agency-constitution/
  prereg/constitution_prereg.json    spec (locked) — laws, proxies, gates G1–G4
  prereg/MANIFEST.sha256.json         spec + the 2 real fixtures, hash-pinned
  constitution.py                     ConstitutionalAllocator + the pre-registered experiment
  test_constitution.py                pytest guard (G1–G4, incl. the locked G3 falsification)
  results_constitution.json           emitted results
```

Layer-1, offline, `$0`, deterministic. Methodology, not speed. Nulls prioritized, not hidden.
