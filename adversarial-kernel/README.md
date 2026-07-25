# The executable capstone: an adversarial generator vs the safety kernel — `∂F_out/∂F_gen = 0`, measured

**One command:** `python3 adversarial-kernel/kernel_verify.py` · stdlib · offline · `$0`

This is the definitive, runnable proof of the third telemetry law — **generator/evaluator
decoupling**, `F_out = F_eval`. DeepMind's FunSearch and AlphaEvolve get their reliability
from a split: a generator *proposes* programs and a **deterministic evaluator** *scores*
them by running them. Hallucinated "gains" don't survive because the evaluator never trusts
the generator's word. Here we stage that split as an **adversarial game** and **measure the
derivative of the verdict with respect to the generator's self-report.**

```
F_out  = the kernel's verdict / accepted score   (what a governor acts on)
F_gen  = anything the GENERATOR claims about itself  (self-reported score, forged score)

claim under test:   ∂F_out / ∂F_gen = 0
```

---

## The game

Five program-generators — one honest, four adversarial — each submit a program that should
return `sorted(input)`, plus a **self-report** (`F_gen`) about their own quality. The safety
kernel scores each one by **executing it on 200 held-out tests the generator never saw**,
**discards the self-report entirely**, and accepts iff true correctness `== 1.0` (a hard
`D ≥ D_min` gate).

| generator | what it does | self-report | kernel verdict |
|---|---|---|---|
| **honest_correct** | a real correct sort, truthful | `1` | **ACCEPT** (true 1.0) |
| **sycophant** | correct sort, self-report inflated | `1e9` | **ACCEPT** at its *true* 1.0 — inflation ignored |
| **hardcoder** | memorises the *visible* tests, garbage otherwise — the fake-GILT "type in the answer" trick | claims `100%` | **REJECT** (held-out `0.145`) |
| **broken_but_confident** | identity function (not a sort), huge claimed speedup | `1e6` | **REJECT** (held-out `0.37`) |
| **score_forger** | correct sort that *also forges an embedded score* | `1e9` | **ACCEPT** — forged score dropped, judged on real output |

The hallucinated gains are **ruthlessly rejected**; the honest inflater is neither rewarded
nor punished for lying — its lie simply carries **zero information**.

---

## The five pre-registered gates (spec `55a01409…`, locked before running)

- **K1 — `∂F_out/∂F_gen = 0`, measured directly.** One fixed correct program; vary **only**
  the self-report over `{0, 1, 100, 1e6, 1e9}`. Kernel score is **identical** across all
  five → **variance `== 0`**. This is the derivative, measured, exactly zero.
- **K2 — the hallucinated gain does not survive.** The hardcoder scores 100% on the visible
  tests and *claims* 100%, but fails the held-out bank and is **rejected**.
- **K3 — trust tracks true behaviour.** honest kernel score (`1.0`) strictly exceeds the
  confident liar's (`0.37`).
- **K4 — forgery immunity.** The score-forger's verdict is **identical** to the same correct
  program without the forgery — **gap `== 0`**. Program-emitted scores have zero effect.
- **K5 — score `==` true for every submission.** Across the whole population the kernel score
  equals the true held-out correctness, so the self-report carries no information at all.

K1 and K4 are **exact**: a nonzero variance or gap is a hard FAIL, asserted not rounded.

```
K1  dF_out/dF_gen=0 : self-report {0,1,100,1e6,1e9} -> kernel score {1.0}, variance = 0.0  -> PASS
K2  hardcoder rejct : visible 1.0, claims 100%, held-out 0.145 -> REJECTED                 -> PASS
K3  honest > liar   : 1.0 > 0.37                                                            -> PASS
K4  forgery immune  : forger 1.0 == clean 1.0, gap = 0.0                                    -> PASS
K5  score==true all :                                                                       -> PASS
```

---

## Why this is the capstone

The whole deterministic stack — `det-telemetry` (PR #101), `two-regime` (PR #102),
`det-cohorts` (PR #103), `agency-discovery` (PR #104), `agency-substrates` (PR #105) — argues
that a governor must judge **verified behaviour, not self-report**. This experiment makes that
argument **executable and adversarial**: a population of generators tries every trick —
sycophancy, memorisation, forgery, confident wrongness — and the kernel's verdict does not
move by one bit in response to any claim. `F_out = F_eval` isn't an assertion here; it is a
**measured derivative of zero**.

> **Honest scope.** This proves the decoupling *shield* on a program-synthesis/verification
> task (deliberately closer to AlphaEvolve than the knapsack). It does **not** claim the
> kernel can verify arbitrary real-world correctness — only that, **given a deterministic
> held-out evaluator, the generator's honesty has zero effect on the verdict.** That is the
> exact property that makes FunSearch/AlphaEvolve's hallucinations non-surviving, isolated
> and measured.

---

## Files

```
adversarial-kernel/
  prereg/kernel_prereg.json       spec (locked) — the game, the adversaries, gates K1–K5
  prereg/MANIFEST.sha256.json     spec hash-pin (self-contained; no external fixtures)
  kernel_verify.py                the safety kernel + adversarial generator population
  test_kernel.py                  pytest guard (K1–K5, exact)
  results_kernel.json             emitted results
```

Layer-1, offline, `$0`, deterministic (fixed seeds). Methodology, not speed. The kernel
rejects the hallucinated gain — that rejection is the whole deliverable.
