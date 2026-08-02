# CRM — the Cognitive Reference Model

**Novora open-source initiative · model three**

**Spec** `558f6fa11302867b7fd1dfc0254e45ad8a54544b74d1c2893d63c20ff1248787` · locked before
the runner existed · **4/6** ·
[Artifact](https://claude.ai/code/artifact/32cbabaa-69ab-4933-8a04-a95f6bdd85ad)

```bash
python3 -m pytest -q cognitive-reference/test_crm.py
```

> **CRM did not earn its existence on this run.** It is reported anyway, in full.

---

## Why LISM could not do this alone

LISM carries a **single fidelity term**. That is not an oversight — it is reference-neutral
by construction, measuring how much signal survives a channel rather than what the signal is
supposed to be faithful *to*.

In a perceptual system that is exactly the missing degree of freedom: an agent can be highly
faithful to **payoff** while being unfaithful to the **world**, and LISM has nowhere to write
that down. So CRM splits the term:

```
D_W = |rank corr( g(x), x    )|     fidelity to the WORLD
D_F = |rank corr( g(x), f(x) )|     fidelity to the PAYOFF
```

Both are computed from the perceptual map and the world **only**. Neither reads the agent's
realised payoff — a test scans the source of both functions to enforce it.

## The result CRM was built to risk

```
mean held-out |error|, 5-fold CV, 2,000 agents

  CRM two-reference    0.06611
  D_F alone            0.06641     ← 0.0003 apart
  LISM U·D_enc·D_dec   0.06915     ← X5 rival
  single fidelity      0.07725
  D_W alone            0.09513
```

**X5 FAILED.** CRM beat LISM's own two-hop form by **0.00304** against a locked bar of 0.005.
The pre-registration had already written down what that means:

> *"If LISM's existing form predicts this cognitive outcome as well as a purpose-built
> two-reference model, then CRM adds vocabulary and no power, and the honest conclusion is to
> keep LISM and drop CRM."*

**And a harsher number that was not pre-registered.** `D_F` alone scores 0.06641 against the
two-reference model's 0.06611 — a gain of **0.0003**. The locked X3 compared CRM against the
*mean* of the two fidelities, which is a weaker rival than the better single one. Against the
best single reference, two references buy almost nothing. Reported because leaving it out
would flatter the model.

## The one thing that looked like a discovery

The discriminating prediction was a **sign flip** on a swept knob:

```
correlation(D_W, D_F) by payoff monotonicity m

  m = 0.00   −0.646     non-monotone payoff: the references pull apart
  m = 0.25   −0.177
  m = 0.50   +0.236
  m = 0.75   +0.957
  m = 1.00   +1.000     monotone payoff: the references coincide
```

**X4 passed — and trips the too-perfect rule.** Two values exceed the locked 0.95 flag. The
reading is **degeneracy, not leakage**: when payoff is strictly increasing in the world state,
the two references *are* the same ordering, so the correlation is forced to 1. Half (b) was
disclosed as near-definitional **before** the run for exactly this reason. **Only the negative
correlation at m = 0.00 carries information.**

## I mis-specified the self-audit — and the binding fires anyway

The spec routed CRM through DCM's self-audit, with power to void the run. It said to band
realised payoff at its median. But DCM's `C` factor is *distinct outcome values ÷ n* — so
binarising a continuous outcome forces **C = 2/2000 = 0.001 by construction.** The gate could
not pass whatever the data did.

```
Δ = V 0.5000 × I 0.9600 × C 0.0010 = 0.0005     against a floor of 0.20
```

> **X6 was not met, so X3, X4 and X5 are UNINFORMATIVE.**

On the unbanded payoff `C` would be **1.0000** — 2,000 distinct values across 2,000 agents.
That is a **diagnosis of my error, not a substitute verdict.** The gate is not re-scored and
the spec is not edited. **Honouring a binding rule only when it is convenient is precisely the
immunisation move the rule exists to stop**, so every result above — including the one that
looks like a discovery — is reported as uninformative.

### Second consecutive self-inflicted un-passable gate

In `6cb42dcd` the cognitive arm **could not fail** because noise was averaged away. Here the
self-audit **could not pass** because the outcome was binarised. Different errors, same class:
**a threshold written without checking the quantity could reach it.** That is a pattern about
this programme's spec-writing and it is recorded as one, not as two unlucky accidents.

The fix did work where it was aimed: **X2 passed** — the populated-failing-region gate added
specifically to catch the earlier error, with payoff IQR 0.1815 against a floor of 0.02.

## The gates

| Gate | Locked bar | Measured | |
|---|---|---|---|
| X1 integrity + earlier flaw fixed | noise on the outcome, not averaged | 2,000 agents | PASS |
| X2 failing region populated | payoff IQR ≥ 0.02 | 0.1815 | PASS |
| X3 two references beat one | gain ≥ 0.005 | +0.01114 | PASS |
| X4 dissociation is directional | neg at m=0, non-neg at m=1 | −0.646 → +1.000 | PASS\* |
| **X5 CRM beats LISM** | gain ≥ 0.005 | **+0.00304** | **FAIL** |
| **X6 DCM self-audit** | Δ ≥ 0.20 | **0.0005** | **FAIL** |
| X7 anything about people | — | — | UNTESTABLE-HERE |
| X8 governance layer | — | HELM: PASS | EXCLUDED |

\* passes and trips the too-perfect flag; see above.

## What each tool actually did

Declared in the spec **before** the run, so the toolchain could not be presented afterwards as
doing more than it did.

| Tool | Role | Could it change a verdict? |
|---|---|---|
| **LISM** | Supplied the **rival** in X5 — the incumbent CRM had to beat. It held. | **Yes — and it did** |
| **DCM** | Supplied X6, the **self-audit with power to void the run**. | **Yes — and it did** |
| **Claude Code** | Wrote the spec and locked it by SHA-256 *before the runner existed*, then implemented against it. The hash makes the order verifiable rather than asserted. | no |
| **IHCEI** | The repository substrate — reproduce harness, provenance Merkle lock, pre-registration convention. Carries the run; measures nothing in it. | no |
| **HELM / NERE** | Audited the **prose** of the results file for manipulative or unsupported framing. Returned PASS, p(manipulative) 0.143. | no |
| **Novora Suite** | Nine-product consumer kernel; screens the layman-facing write-up. | no |
| **Page Code** | Audits whether the repository change sits inside the declared permission table. | no |

**Only two of seven could change a verdict, and both ruled against the new model.** A
governance verdict on prose is not evidence about agents — saying so in the specification, in
advance, is what stops a large toolchain looking like it was doing scientific work it wasn't.

## What this says about people

**Nothing, and that is not a figure of speech.** Four Hugging Face searches for human
behavioural trial data — memory recall, judgment, calibration, decision trials — returned only
text and multiple-choice QA corpora. **No human trial dataset was reachable** (X7,
UNTESTABLE-HERE). Every agent is simulated.

The substrate is Hoffman's published Fitness-Beats-Truth setting, which makes the world and
payoffs principled — but it is **a simulation, not a derivation.** A simulation can show a
decomposition is *useful inside a model* and say nothing about whether it is *true of minds*.

## Where that leaves model three

CRM is better than LISM on this task — by 0.003 against a bar of 0.005, and by 0.0003 against
the best single reference. The spec said what to do in that case: **keep LISM.**

And by the binding rule I am not entitled even to that conclusion. **The honest status of CRM
is untested, not refuted.** The next step is not to defend it but to **re-register** it, with:

1. a self-audit that can actually pass — `C` computed on the unbanded outcome;
2. a rival comparison against the **best single reference**, not the mean of the two;
3. and, if it is ever to say anything about cognition, trial-level human data with an
   experimentally decoupled world-versus-payoff structure.

**Model three does not join the stack on this evidence.** That is the mechanism working.
