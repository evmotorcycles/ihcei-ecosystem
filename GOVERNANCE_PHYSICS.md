# Governance Physics: the crossover, run properly — and what it cost

*Two new skills (`rational-thinking-framework`, `governance-framework`), one
pre-registered experiment (`6a7877db…`), and two results that went **against** the
framework — one of them against a gate I wrote myself.*

```bash
bash reproduce_all.sh        # 68/68, clean checkout, offline, $0
```

---

## 1. The two containers, as reusable skills

You asked for the frameworks to be saved for reference. They are, as two skills that
invoke each other:

| Skill | Job |
|---|---|
| `rational-thinking-framework` | State the RT reading of a field **at full strength**, and run the RT-side firewall |
| `governance-framework` | Run the four-step crossover, and assign one of **three verdicts** |

**The crossover protocol.** State the RT reading → identify the channel → **re-derive, do
not re-label** → **produce a discriminating prediction**. Step 4 is not optional; a
crossover that skips it is renaming.

**The three verdicts.** Every reframe must be assigned exactly one:

| Verdict | Meaning | May claim |
|---|---|---|
| **Rival theory** | changes a prediction | must be tested; may be *wrong* |
| **Interpretation** | empirically equivalent | coherence only — **never** the field's predictive credit |
| **Category error** | contradicts a measurement or a no-go theorem | withdraw or repair |

**Most reframes are interpretations, and saying so is not a defeat.** Reframing is a real
scientific move — thermodynamics → information theory, mechanics → variational principles
— but each of those paid for itself in *new derivations*, not new vocabulary. That is the bar.

## 2. The crossover on quantum physics — verdict by claim

| Claim | Verdict |
|---|---|
| Spacetime is emergent / a rendered interface | **`[L3]` interpretation.** Emergent-spacetime programmes are live research, but nothing here adjudicates it. |
| The wave function is a generative probability space | **Interpretation.** Empirically equivalent restatement; earns coherence, not confirmation. |
| Observation is a rendering optimisation | **Interpretation, and strained.** Decoherence recovers measurement statistics with *no* observer. Any reading that makes rendering depend on a mind must confront that, not bypass it. |
| Bell violation ⇒ "the evaluator cannot be lied to" | **Overreach.** Device-independent certification is real but narrow — specific cryptographic tasks under loophole-free conditions. It does not generalise to arbitrary self-reports. |
| **Entanglement ⇒ τ_rt = 0 ⇒ d = 0** | **CATEGORY ERROR — and now measured.** |

### The category error, tested rather than argued

The entanglement claim is checkable **inside the framework's own formalism**, no physics
required. In LMD, `τ_rt` is realised as **commute time / effective resistance** — a
round-**trip transport** quantity. So the claim reduces to: *maximal correlation forces
commute time to zero.*

That is gate **GP5**, pre-registered so the framework could lose. On **1,262 maximally
coupled real pairs** in the PyPI graph:

```
minimum emergent distance = 0.200115      mean = 0.614069
pairs with d = 0:  ZERO
```

**Refuted on its own terms.** Correlation is not transport latency — which is precisely
why **no-signalling** holds in physics: perfect correlation transmits **zero bits**. The
"they sit at the same coordinate on the CPU" reading inverts the very theorem it appeals to.

## 3. The result that cost me two of my own gates

GP3 asked whether the coupling→distance scaling exponent matches the framework's sharp
prediction of **−0.5000**. It returned:

```
fitted slope = -0.5000      R² = 1.00000000
```

**That is too perfect to be data**, and it is: it is an **algebraic identity**.

```
W → sW  ⟹  L → sL  ⟹  L⁺ → L⁺/s  ⟹  R → R/s  ⟹  d = √R → d/√s
so  log d = −0.5·log s + const     EXACTLY, for EVERY graph
```

Controls with no relation to the substrates confirm it — a **random graph** and a **path
graph** both return −0.5000 with R² = 1.00000000.

So GP3 and GP6 **passed as pre-registered, and are not evidence.** Under this repository's
own rule — *a test that cannot fail is not evidence* — both are excluded from the
evidential score.

> **This also corrects a claim already committed here.** `physics-agency/lmd` reports the
> same −0.5000 slope on seeded graphs as a *verified prediction of Latency-Metric
> Duality*. It is not one. Any definition of the form `d = √(κ·τ)` with `τ` homogeneous of
> degree −1 in the coupling produces it automatically. That README now carries the
> correction, and a test enforces it.

## 4. What actually survives — 4/4 evidential gates, about **graphs**

| Gate | Result |
|---|---|
| **GP1** metric emerges on a real graph | 0 violations in 300,000 triples; symmetry err 2.9e-15 |
| **GP2** not merely degree relabelled | ρ(d, 1/√(dᵢdⱼ)) = **+0.8686** — clears the 0.90 gate by only **0.03** |
| **GP4** survives a degree-preserving null | real 1.113106 vs null 1.050101 ± 0.008475, **z = +7.43** |
| **GP5** maximal coupling ⇏ zero distance | min d = 0.200115, **zero** pairs at d = 0 |

GP2 is the one to watch: the emergent geometry is **substantially** degree. A test pins
that margin between 0.80 and 0.90 so it cannot quietly be reported as "independent of
capacity."

**GP7** (excluded, cannot fail) asserts that no Layer-3 term — *rendered, headset,
conscious, observer, spacetime, simulation* — appears in any scored gate. None does. **The
physics interpretation acquires no empirical support here, and none is claimed.**

## 5. So what did the crossover actually buy?

Applied to **scripture**, the crossover produced operational definitions that *generate
falsifiable tests* — a genuine success of the method, independent of whether any given
test passed.

Applied to **finance**, it produced four falsifications and one 4/5 — and the
falsifications came from the method working.

Applied to **physics**, it has so far produced **one narrow `[L1]` result about graphs**,
**several interpretations**, and **one category error that the experiment caught**.

That is a real answer to your question — *"by looking at quantum physics through
governance we will be able to answer the questions we were unable to answer"*. On this
evidence: **not yet, and not this way.** The container change is a legitimate move, but it
buys new answers only where it produces new *derivations*. Here it produced a redescription
plus one inference that measurement refutes.

The framework's credibility does not come from the physics being right. It comes from the
physics being **checkable**, and from what happened when it was checked.

---

*Reproduce: `bash reproduce_all.sh` → **67/67**. Pre-registration `6a7877db` committed
before the runner existed. `exit 0` means "reproduces including its failures and its
downgrades" — never "Governance Physics is validated."*
