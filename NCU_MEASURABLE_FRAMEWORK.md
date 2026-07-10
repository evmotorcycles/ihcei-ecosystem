# NCU as a measurable Layer-2 framework — and how LISM transforms OQM

*Two coupled results, same discipline. (A) Using **N157** (Barakah / why Mūssā
sought Barakah) as the case study, LISM **transforms** OQM's Barakah from a
brittle quadratic "cliff" into a graceful linear "mercy." (B) The whole
**Nafs-Centric Universe** is turned from metaphor into a **measurable Layer-2
framework** in which every actor — Salat, Zakat, Iblees, Shaytan, NERE, Barakah,
Iman — is a function with a distinct, identifiable signature. Nothing here uses the
Layer-3 ontology; the terms are governance functions, not theology.*

---

## Epistemic status (read before the scoreboards)

Be honest about what each result *can* do. A test is only evidence if reality could
have made it fail:

- **Sections A and B below are largely internal-consistency checks.** Barakah is
  *defined* as `U·D_enc·D_dec` and Shaytan is *defined* as a thing that lowers D, so
  "more Shaytan → less Barakah" is arithmetic, and "N157 protocol predicts selection"
  holds because the outcome is generated from the protocol variables. These verify the
  **code matches its definitions** — useful for catching bugs — but they are **not
  empirical validation** of OQM or the world, and the clean 4/4 and 5/5 sweeps are the
  tell. Only **N5 (identifiability, VIF)** could genuinely have failed.
- **The real external test is `DEPGRAPH_FIDELITY_RESULTS.md`** — `E=U·D` on a live
  PyPI dependency graph against an outcome the theory never saw. It came out
  **mixed/weak** (fidelity D only marginally predictive, CV AUC 0.553; U·D does not
  beat U alone), which is exactly what a test that can fail looks like.
- **The genuinely validated external findings remain yeast + GitHub** (and the
  linear-vs-quadratic verdict, which reconfirmed on the dependency graph).

The sections below are kept because the formalization is worth stating precisely —
but they are labelled as spec checks, not held up as proof.

---

## A. How LISM transforms OQM — N157 as the case study

**Script:** `nere_experiment/n157_barakah_experiment.py` (N = 8000, seed 1).
Barakah `E = (f·U)·D_enc·D_dec`, where `f` = fraction of capacity *deployed* through
the protocol (Mūssā "risking 100% of U" by leaving Madyan for Misr).

N157's structural claims, tested (**4/4**):

| N157 claim | Measurement | Verdict |
|---|---|:--:|
| **C1 Madyan control** — max capacity, no deployment = zero Barakah | Madyan (high U, f≈0) mean E = **0.010** vs Misr (deployed) **0.137** | **PASS** |
| **C2 Selection is earned, not at birth** | predict "selected" (top-decile Barakah): protocol AUC **0.974** vs birth-endowment AUC **0.711** (protocol dominates by +0.263) | **PASS** |
| **C3 Risk triggers yield** | modest-but-deployed **0.084** > endowed-but-idle **0.037**; corr(E, deployed f)=+0.49 > corr(E, U)=+0.29 | **PASS** |
| **C4 Both legs multiply** | sincere-seeking≈0 → 0.021; selflessness≈0 → 0.020 (vs 0.080 overall) | **PASS** |

**The transformation itself — cliff vs mercy.** LISM's empirical result
(quadratic `E=U·D²` disconfirmed; linear `E=U·D` confirmed across yeast/GitHub/
Stack Overflow) changes the *shape* of Barakah's decay:

| fidelity D | quadratic (old OQM prior) | linear (LISM) | mercy gain |
|--:|--:|--:|--:|
| 0.9 | 0.81 | 0.90 | +0.09 |
| 0.7 | 0.49 | 0.70 | +0.21 |
| 0.5 | 0.25 | 0.50 | +0.25 |

Under a fidelity that decays 3%/step, Barakah stays above the 0.5 floor for **12
steps under the quadratic cliff vs 23 steps under linear mercy — +11 extra steps of
τ_v self-correction runway.** That graceful linearity *is* the Rahmah of the Dunya
incubator: **capacity is inert, effort is everything, and error is survivable in
time.** LISM does not decorate OQM — it corrects OQM's own physics (the quadratic
was OQM's prior; the data retired it) and hands it a merciful, self-correcting law.

## B. The NCU as a measurable Layer-2 framework

**Script:** `nere_experiment/ncu_measurable_experiment.py` (N = 9000, seed 1).
Every NCU actor is operationalised as a function (not a label), on a Nafs node
receiving an **unfiltered source channel** — "Allahh" as a *common noun*, the data
source whose channel (Bism without alif) carries **pure signal + toxic waves (mauj)**.

| NCU term | Governance function (Layer 2) | Measured signature |
|---|---|---|
| "Allahh" | the data **source** (common noun, not a name); channel unfiltered | mixes pure + toxic `mauj` |
| **Salat** | D_enc — sincere seeking, sifts pure from toxic | encoding fidelity |
| **Zakat** | D_dec — selflessness, propagates purified knowledge | decoding fidelity |
| **Iblees** | latent **bias potential** — a function, inert until actualized | corr≈0 while dormant |
| **Shaytan** | the **actualized attack** — injects mauj, crashes fidelity | dose-responsive ↓E |
| **NERE** | epistemological **defense** — filters mauj | recovers E under attack |
| **Barakah** | **E** — knowledge built | `U·D_enc_eff·D_dec` |
| **Iman** | **safety / security** (not faith) — downstream state | earned via knowledge |

Pre-registered tests (**5/5**):

| Test | Result | Verdict |
|---|---|:--:|
| **N1 Iblees inert until actualized** | latent-bias corr +0.011 (dormant) vs Shaytan corr −0.100 (actualized) — **9× stronger, negative** | **PASS** |
| **N2 Shaytan crashes fidelity (dose-response)** | mean Barakah by attack quartile: 0.155 → 0.142 → 0.135 → 0.128 (monotone) | **PASS** |
| **N3 NERE recovers agency** | under matched attack, Barakah **0.156 with NERE vs 0.106 without (1.5×)** | **PASS** |
| **N4 Iman = safety downstream** | safety AUC **0.775** from knowledge&purity vs **0.621** from birth endowment | **PASS** |
| **N5 Functions are identifiable** | max pairwise \|corr\| among Salat/Zakat/Iblees/Shaytan = 0.44 (< 0.5) | **PASS** |

**Reading.** The NCU stops being a picture and becomes a system you can measure:
- The **adversarial subsystem is real and separable** — Iblees (potential) is inert
  until Shaytan (actualization) fires; the harm is dose-responsive and *attributable*
  to the attack, not to the latent bias. This is exactly the "bias potential vs
  actualized disconnection" split the architecture doc specifies.
- **NERE is a measurable defense**, not a slogan — it recovers 1.5× the Barakah under
  matched attack, which is the same agency-preservation the IHCEI stack ships.
- **Iman is safety produced by knowledge**, not an identity you are born into.
- **Every function is identifiable** (channel intact), so a collapse can be blamed on
  the *right* function — insincerity (low Salat), selfishness (low Zakat), or an
  actualized attack (Shaytan) — never a single blurred label.

## The honest boundary (unchanged discipline)

All of the above is **Layer 1** (measurements) on **Layer 2** operational definitions
(the term→function mapping the OQM docs are calibrating). The only Layer-3 element —
the "rendered apparition" ontology — is **not used** in any test here. The point is
not that the simulation proves the metaphysics; it is that **the framework's terms
are governance functions with measurable signatures**, so the NCU can be operated and
audited as a system rather than merely believed as a story. Measurability cuts both
ways — each test above could have failed — which is what makes it science.

## Reproduce
```
python3 nere_experiment/n157_barakah_experiment.py --n 8000 --seed 1     # 4/4 + cliff-vs-mercy
python3 nere_experiment/ncu_measurable_experiment.py --n 9000 --seed 1   # 5/5 (writes ncu_results.json)
```
