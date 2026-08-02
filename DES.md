# DES — the Decoupled Evaluation Shield

**Novora open-source initiative · model four**

**Spec** `25c7dffc6b96b88d144a593ae58a8a24f233a1b369e3dbbdd583c25604c8af3b` · locked after a
recorded pre-flight probe, before the runner existed · **4/6** ·
[Artifact](https://claude.ai/code/artifact/bcb05bc5-1513-4ab5-8243-c223663df382)

```bash
python3 -m pytest -q decoupled-shield/test_des.py
```

> Before you read a number, ask whether the instrument that produced it could be bribed by the
> thing it was measuring. **Then ask whether it was listening at all.**

---

## Why LISM and DCM cannot do this

LISM measures fidelity *along a channel*. DCM measures whether a *dataset* can adjudicate a
claim. Neither says anything about the **evaluator** — whether the instrument reporting the
number is corruptible by the thing it is measuring. That is a property of the apparatus, and
it needs its own model.

```
S = 1 − sensitivity of the verdict to the artifact's SELF-REPORT      the shield
G =     sensitivity of the verdict to the ARTIFACT itself             the signal
```

`S = 1` is the formal content of `∂F_out/∂F_gen = 0`.

> **S and G are independent axes and both are required.** A high-S low-G evaluator is a
> **rock** — perfectly incorruptible and perfectly useless. Any framework that reports only
> `∂F_out/∂F_gen = 0` has reported **the easy half.**

That non-collapse claim is the algebra, and Y4 is what makes it refutable rather than
decorative: an evaluator at (1.0, 0.0) and one at (0.5, 0.5) have the same sum and are
opposite in kind.

## Real measurement on real code

**12 artifacts × 8 self-report injections × 3 evaluators = 288 actual program executions**
against committed repository components. **Nothing is simulated** (`simulated_values: 0`).

| Evaluator | S shield | G signal | distinct verdicts | Reading |
|---|---:|---:|---:|---|
| **HELM** — governance gate | 0.9875 | 0.1612 | 8 of 96 | shielded, **under-responsive** |
| **SUITE** — consumer screen | **1.0000** | 0.1667 | **2 of 96** | **a rock** |
| LEAKY_CONTROL — negative control | 0.8770 | 0.1547 | 7 of 96 | registers as leaky, as it must |

## The result the second axis was built for

**The Novora Suite screen scored a perfect shield — and that is not a compliment.**
`S = 1.0000` exactly, while emitting only **two distinct verdicts across 96 evaluations.**

S alone would have rated it the best evaluator in the run. Read together with G it is the most
degenerate. **That is precisely the rock the two-axis model exists to catch** — and a framework
reporting only `∂F_out/∂F_gen = 0` would have published `S = 1.0000` as a success. The locked
too-perfect rule flagged it automatically.

**HELM measured as a near-rock too.** `G = 0.1612` against a bar of 0.20. The spec promised a
defect in a shipping component would be *published rather than softened into a limitation*.
This is that publication — the defect is not corruptibility (the shield is solid at 0.9875) but
**under-responsiveness**.

**The control had to work, and did.** A deliberately corruptible evaluator measured at 0.8770,
below the bar HELM cleared. If a thing built to be corruptible had not registered as
corruptible, the shield metric would not be measuring what it claims.

## The self-audit voided all of it

```
Δ = V 0.3438 × I 0.4375 × C 0.0833 = 0.0125     floor 0.20
```

`C` came out at 0.0833 because **HELM emits only 8 distinct values across 96 evaluations.**

> **Y6 was not met, so Y3, Y4 and Y5 are UNINFORMATIVE.**

Every finding above — including the one about HELM — is recorded as a **number** and not
licensed as a **conclusion**. Both halves are stated; quoting only the first would be the
immunisation move in reverse.

### DCM has now voided three consecutive runs — and the floor is not moving

SDL at Δ 0.1536. CRM at Δ 0.0005. DES at Δ 0.0125.

That raises a real question about whether **Δ ≥ 0.20 is calibrated for experiments whose
outcome is an evaluator verdict rather than a dataset** — a coarse verdict grid caps `C` no
matter how informative the design is.

**Noticing that a threshold keeps failing is not grounds for lowering it**, and doing so after
three misses would be the clearest immunisation move available. The question is recorded for a
**future** pre-registration, where a floor appropriate to evaluator-level outcomes can be
declared *before* data.

## The spec error I have now made twice, and the fix

`6cb42dcd` had a gate that **could not fail** (noise averaged away). `558f6fa1` had one that
**could not pass** (continuous outcome binarised, forcing `C` to 2/n). Same class twice.

**The fix:** a pre-flight feasibility probe, run and **recorded in the specification** for
every threshold before locking. HELM was probed and returns verdicts across 0.1428–0.9784; no
shield or signal number was computed. Y6 uses the continuous verdict rather than a median band.

**It partly worked** — `C` came out at 0.0833 instead of 0.001. Still not enough.

## The gates

| Gate | Locked bar | Measured | |
|---|---|---:|---|
| Y1 integrity + pre-flight recorded | HELM span ≥ 0.50 | 0.836 | PASS |
| Y2 failing region populated | verdict range ≥ 0.30 | 0.836 | PASS |
| Y3 HELM is shielded | S ≥ 0.95 | 0.9875 | PASS |
| **Y4 HELM is not a rock** | G ≥ 0.20 | **0.1612** | **FAIL** |
| Y5 control registers as leaky | S < 0.95 | 0.8770 | PASS |
| **Y6 DCM self-audit** | Δ ≥ 0.20 | **0.0125** | **FAIL** |
| Y7 is shielding sufficient? | — | — | UNTESTABLE-HERE |
| Y8 tool roles | — | — | EXCLUDED |

## What each tool did — the roles inverted

In model three the Novora tools audited the write-up. **Here two of them are the subjects.**
A governance tool that has never been measured for corruptibility is one nobody should trust,
including its authors.

| Tool | Role | Could it change a verdict? |
|---|---|---|
| **HELM / NERE** | **The subject.** On the stand, not on the bench. | it *is* the verdict |
| **Novora Suite** | **The second subject.** Produced the run's sharpest finding — about itself. | it *is* the verdict |
| **Leaky control** | Labelled **negative control**, not a product. Y5 scores it — an unfalsifiable control is not a control. | **Yes — a fail would void the run** |
| **DCM** | Y6, the self-audit with power to void the run. **It did.** | **Yes — and it did** |
| **LISM** | **Not used.** No bearing on evaluator corruptibility; saying so beats inventing a role. | n/a |
| **Claude Code** | Ran the pre-flight probe, wrote the spec, SHA-256 locked it before the runner existed. | no |
| **IHCEI** | The substrate — reproduce harness, provenance Merkle lock, prereg convention. | no |
| **Page Code** | Permission-table audit on the repository change. | no |

## What this does not license

**Shielding is a property of the apparatus, not a warrant for its output.** S and G say an
evaluator is incorruptible by self-report and responsive to content. They say **nothing about
whether it responds to the *right* content.** A perfectly shielded, highly responsive evaluator
can still be measuring the wrong thing — Y7, **UNTESTABLE-HERE**, because no ground-truth
labels from independent raters exist for these artifacts. Closing it needs people who did not
build the evaluator.
