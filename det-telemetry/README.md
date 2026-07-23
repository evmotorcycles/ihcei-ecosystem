# Deterministic Telemetry — the Generator/Evaluator Decoupling Law

**One command:** `python3 det-telemetry/funsearch_det.py` · stdlib · offline · `$0`

LISM's `E = U · ∏Dᵢ` describes fidelity **decay**. This is its **deterministic complement**:
the law that explains why DeepMind's FunSearch / AlphaEvolve can use a hallucinating LLM to
discover *provably correct* algorithms — and why both a probabilistic and a deterministic
system are required, each with a role.

---

## The equation

```
Decoupling Law:   F_out = F_eval,     ∂F_out / ∂F_gen = 0
Yield:            Y = U · s          (U = candidates generated, s = deterministic survival fraction)
```

The output fidelity of a **generate-and-filter** pipeline equals the deterministic
**evaluator's** true-accept fidelity, and is **independent of the generator's honesty** —
provided the evaluator is deterministic with zero false-accept.

- **Probabilistic generator** (the LLM): supplies capacity **U** — massive variance, exploration,
  and, yes, hallucination. On its own it is *also* the verifier, so `F_out = F_gen`, which decays
  into RLHF people-pleasing noise (this is why a chat window hallucinates a convincing false proof).
- **Deterministic evaluator** (a compiler / test suite / formal checker): forces the final hop
  `D_dec = 1`. A hallucination cannot survive it. On its own it explores nothing (`U = 0`).
- **The split** is what discovers: `E = U · ∏Dᵢ` needs *both* factors nonzero.

## The experiment (real, deterministic, reproducible)

A FunSearch-style evolutionary loop on a hard-constrained **0/1 knapsack** (the deterministic
evaluator: over-capacity candidates are invalid, score −∞ — zero false-accept). The generator is
a seeded bit-flip mutator, in two variants: **honest**, and a **liar** that attaches an inflated
self-reported score (claims every candidate is great, RLHF-style). Gates were locked *before*
running (spec `d9ea4e6c…`).

| gate | prediction | result |
|---|---|---|
| **D1** evaluator determinism | same candidate → identical score (variance 0) | **PASS** `[243,243,243,243,243]` |
| **D2** generator variance | different seeds → different populations | **PASS** |
| **D3** honesty **decoupling** | honest vs lying generator → **identical** best (gap 0) | **PASS** `400 = 400, gap 0` |
| **D4** monotone ratchet | best-so-far non-decreasing | **PASS** (60 gens) |
| **D5** architecture control | self-verifying pipeline + liar is strictly worse | **PASS** `−∞ (invalid) < 400` |

**D3 is the core result.** Under deterministic evaluation, a generator that *lies about its own
quality* produces the **exact same** discovered solution as an honest one — because the evaluator
discards self-reports and scores objectively. `∂F_out/∂F_gen = 0`, measured.

**D5 is the reason the deterministic hop is required.** The *self-verifying* pipeline (chat mode —
trusts the generator's self-report) is fooled by the liar into crowning an **invalid, over-capacity**
candidate (true score −∞), strictly worse than the deterministic pipeline's 400. Trusting the
generator to grade itself is exactly the failure mode.

## The open-source grounding (and an honest, self-referential proof)

The deterministic evaluator is the same *kind* of object as a CI test suite, a compiler, or a
formal checker on real open-source projects — **and as this repository's own hash-locked
`reproduce_all.sh` harness.** That harness is a working deterministic evaluator, and its git
history is real empirical evidence of the decoupling law: it **rejected a synthetic Kaggle CSV,
a fabricated GILT script, and an attempt to spin the OpenAlex null into a false pass** — fabrications
a probabilistic generator (including this assistant) tried to push through. The architecture caught
them because the evaluator does not trust the generator. That is the law, working in public.

## Files

```
det-telemetry/
  prereg/det_prereg.json     spec (locked BEFORE running) — D1–D5
  prereg/MANIFEST.sha256.json
  funsearch_det.py           the deterministic generator/evaluator loop
  test_det.py                pytest guard (D1–D5 + cross-process determinism)
  results_det.json           emitted results
```

Layer-1, offline, `$0`. The deterministic complement to `E = U·∏Dᵢ`: both systems required.
