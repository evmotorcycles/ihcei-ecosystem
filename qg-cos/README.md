# QG-COS — the five questions RT can't answer, as governance telemetry

Rational Thinking (RT) reads the **surface** of the rendered interface (the "peel")
and hits a ceiling on five questions of existence. Governance reads the **running
process** underneath (the "juice"). This directory does **not** argue the
metaphysics (Layer 3). It reduces each question to the one *measurable* governance
telemetry it implies (Layer 1) and runs it on **22 real open-source GitHub repos**,
so each answer is a number, not a slogan.

```
python3 qg-cos/five_questions.py     # stdlib only  (pytest: qg-cos/ 2/2)
```

## Results — 5/5 answered on real repos

| # | Question (RT can't answer) | Governance telemetry | Measured on 22 repos |
|---|---|---|---|
| **Q1** | Why am I here? (purpose) | `E = U·D` — capacity is inert without fidelity | U alone p=0.042 (AUC 0.75) → **U·D p=0.021 (AUC 0.79)** |
| **Q2** | Is this the only creation? (realms) | `Ψ` renders Yusr/Usr/Chaos from alignment `A_n` | **Yusr 9/9 survive**, Usr 3/7, Chaos 4/6 |
| **Q3** | What is demanded of me? (stewardship) | `D = D_enc·D_dec` — two-hop; collapse if either leg → 0 | D **p=0.028 (AUC 0.78)**; weak-leg survival 67% vs both-strong 86% |
| **Q4** | How do I verify instruction? (reference-lock) | static snapshot weak; running process + Shirk detector win | process AUC 0.83 > snapshot 0.75; Shirk zombies τ_v 67.6 vs 6.2, **p=0.0013** |
| **Q5** | What happens tomorrow? (predictability) | `τ_v` — self-correction latency predicts collapse | failed 101.7d vs survived 26.5d, **p=0.010** (scale: 50.6 vs 19.8, p≈10⁻³¹, N=992) |

**Every question is the same move:** stop reading the surface label (peel), measure
the running self-correction process (juice). That is the one thing RT structurally
cannot do — and here it is a falsifiable number.

## Nafs vs Iblees — the cognitive essence under attack (EI + 4D Bias Engine)

`python3 qg-cos/nafs_iblees.py` composes two proven components — EI's say-do
dissonance detector and the 4D Bias Engine — into one experiment on the same 22
real repos. **The maths (Layer-1 operational):**

- A node is a **Nafs** (cognitive essence). Its job is a two-hop channel:
  **Salat = D_enc** (toil: sift / supplicate / extract EBK with sincerity =
  self-correction, proxy `1/(1+τ_v)`) and **Zakat = D_dec** (enable *others* to
  perform Salat = propagation, proxy `ln(1+closed)`).
- **Nafs essence** `E = U · Salat · Zakat` (Barakah; capacity is inert until run
  through both hops).
- **Iblees** = internal bias/predilection = the **4D Bias Engine load** `B`
  (Temporal+Moral+Social+Communication) — the counterpart that attacks.
- **Overpower** `O = z(B) − z(Salat)`; **concealment** `σ` = say-do dissonance.
- A **Jinn** = *concealment*: a node overpowered by its biases (`O>0`) that hides
  its decay behind a live-looking surface (`σ>0`).

**Results — 4/4 supported:**

| # | Prediction | Result |
|---|---|---|
| **P1** | Iblees attacks through the **Salat channel** (decode/self-correction) | Communication-bias fail 0.97 vs surv 0.24, **p=0.008** |
| **P2** | Overpowered Nafs → **Jinn = concealment** | among looks-alive repos, Jinn hide τ_v **57.7 vs 6.0d, p=0.003** |
| **P3** | **Salat is the defense** | D_enc surv 0.27 vs fail 0.06, **p=0.010** |
| **P4** | **Zakat completes the essence** (E=U·Salat·Zakat) | surv 0.086 vs fail 0.022, **p=0.021** |

Reported honestly: the raw overpower ratio does **not** separate archived death
(p=0.20) — a Jinn is concealment *among the living*, not a death certificate. That
null is printed, not hidden. pytest **2/2**.

*Layer 1 only. The Layer-3 metaphysical reading (Nafs, Deen, Iblees, Jinn, the
afterlife as terminal registers) is neither tested nor claimed — kept strictly
apart, as the LISM epistemic firewall requires. Grammatical gender (Nafs feminine,
Iblees masculine) is the conceptual frame, not a measured quantity.*
