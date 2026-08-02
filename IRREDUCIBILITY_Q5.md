# Q5 on a testbed where the answer isn't in doubt

**v1** `0de17fc489bbdad37ee2a8d7b5496fea85acd206f65753c4b9b8edbd781984f2` · **2/5**
**v2** `0cd701a45bb725c499f5313786d0e463e2986df4eb617c682aeb4388e66a1a84` · **5/6**

```bash
python3 -m pytest -q irreducible/test_irr.py     # ~5 min, real CA evolution
```

> The one gate that carries our own governance advice is the one that failed. Twice.

---

## Why a cellular automaton and not an institution

Q5 asks whether a system's future can be read off its present, or whether it has to be run.

On a real organisation that question is unanswerable. A null result means *"we found no
shortcut"*, which is not *"no shortcut exists"* — we may simply have looked badly, and no
amount of field data separates those.

**Rule 110 is proven Turing-complete.** For it, the answer is not in doubt: no general
shortcut to its state at step T can exist. Rules in Wolfram classes 1 and 2 are the
opposite — shortcuts demonstrably do exist. That gives a testbed where a null *means*
something, because it can be compared against a case where success is possible.

### The ablation is the whole design

*"Static prediction fails on the complex rules"* is worthless on its own — it could just
mean our regression is weak. So **P4 requires the same predictor, the same features and the
same pipeline to succeed on the simple rules.** The spec says in writing: if P4 fails, P3 is
uninformative regardless of its own outcome.

## v1 failed, and its own gates caught why

I hand-picked the simple rules: `[4, 108, 132, 160]`. **Rule 160 drives the centre cell to a
constant 0 by step 60**, so its AUC is **undefined — not low.** P4's pre-registered quantity
is the mean across *all four*, and that mean does not exist.

The mean over the surviving three is 0.9559. **It was not used.** P4 was recorded
**UNTESTABLE-HERE**, excluded from scoring, and *its binding consequence was still applied* —
so v1's P3 is reported **uninformative even though P3 itself was met.**

> Treating an ablation that could not be run as an ablation that passed is the immunising
> move. It was available and it was refused.

v1's P1 and P6 failed for the same single reason. Every other rule's shuffled-label control
sat inside `[0.40, 0.60]`.

## v2 changed the rules and nothing else

A **mechanical screen**: 74 published class-1/2 candidates → admit base rate in
`[0.20, 0.80]` → **take the four lowest numbers.** No discretion at any step.

It computed **base rate only**. Never AUC, never a fitted model — and base rate is the
admissibility criterion v1's own P2 declared *before any data*. Chosen: **1, 3, 5, 6.**
The screen rejects rule 160 (0.0) and rule 4 (0.1375, outside v1's own band).

**Not one threshold moved.** `irr.py` and `ca.py` are the same files for both runs; v2
differs only in which rules it names.

## The result

```
  static AUC, 4 SIMPLE rules     0.7656     bar 0.75        P4 MET
  static AUC, 4 COMPLEX rules    0.4940     ceiling 0.60    P3 MET
  shuffled-label control         all in [0.40, 0.60]        P6 MET
```

The same predictor that reaches **0.7656** on reducible rules sits at **chance** on the
irreducible ones. **Rule 110, proven Turing-complete: 0.4945.**

| rule | class | static AUC |
|---|---|---:|
| 1 | 2 | 0.9878 |
| 5 | 2 | 1.0000 |
| 3 | 2 | 0.5684 |
| 6 | 2 | 0.5062 |
| 30 | 3 | 0.5371 |
| 90 | 3 | 0.4564 |
| **110** | **4** | **0.4945** |
| 150 | 3 | 0.4881 |

## The gate that failed is the one that mattered

**P5** gave the predictor the first **30 steps of the actual trajectory** — the *"monitor
rather than forecast"* arm, the direct analogue of watching enforcement latency instead of
predicting from structure.

```
  partial-run AUC 0.4991  −  static AUC 0.4940  =  +0.0051      bar 0.10
```

**On computationally irreducible systems, partial observation does not rescue what static
structure cannot reach.** Watching half the run told the predictor essentially nothing about
the second half.

The complex arm is identical in v1 and v2, so **the null replicates to the digit**. The bar
was **not** lowered after v1 measured the same +0.0051.

> This is a null **against our own advice.** "Monitor τ_v rather than predict" has no
> support from this testbed. Where a system is genuinely irreducible, monitoring is not a
> cheaper substitute for running it — it is simply another thing that doesn't work.

## The caveat that matters most

The simple arm clears 0.75 **only because two of its four rules are near-perfect.** Rules 3
and 6 sit at **0.5684** and **0.5062** — near chance, despite both being **class 2**.

**Wolfram class does not determine static predictability.** The mean passes; the arm is not
homogeneous. Reported rather than smoothed over.

## DCM scores nothing here, by its own rule

Δ = V·I·C is an admissibility check for **concentrated or categorical** outcomes. AUC is
continuous and unbanded, so V and C sit near 1 by construction and **Δ cannot fail.**

A gate that cannot fail is not evidence, so **P7 is EXCLUDED rather than counted as a
pass.** That is a **scope limit on our own instrument**, and it retro-explains something:
every one of the five runs DCM has voided had an outcome landing on a small lattice — HELM
verdicts, banded scores, modal shares. On continuous outcomes DCM is silent.

## The gates

| Gate | Bar | v1 | v2 |
|---|---|---|---|
| P1 integrity + pre-flight | all AUCs finite | **FAIL** (160 undefined) | PASS |
| P2 outcome not degenerate | ≥6 of 8 in [0.20,0.80] | PASS | PASS |
| P3 static fails on complex | ≤ 0.60 | met but **UNINFORMATIVE** | **PASS** 0.4940 |
| P4 ablation: same predictor works | ≥ 0.75 | **UNTESTABLE-HERE** | **PASS** 0.7656 |
| **P5 monitoring beats predicting** | ≥ 0.10 | **FAIL** +0.0051 | **FAIL** +0.0051 |
| P6 shuffled control at chance | [0.40,0.60] | **FAIL** (160) | PASS |
| P7 DCM self-audit | — | EXCLUDED | EXCLUDED |
| P8 transfer to institutions | — | UNTESTABLE-HERE | UNTESTABLE-HERE |

## What this does and does not license

**Does:** there exists a class of systems where a static read of the present cannot
substitute for running the system; our predictor tells that class apart from the reducible
one; and partial observation does not close the gap.

**Does not:** that any institution is computationally irreducible. That τ_v is the right
thing to monitor. That "monitor rather than predict" is good advice for anyone.

> **A cellular automaton is not an institution.** P8 records this and no write-up may weaken
> it. Establishing transfer needs a demonstration that some real governance outcome is
> computationally irreducible, and nothing in this repository provides one.
