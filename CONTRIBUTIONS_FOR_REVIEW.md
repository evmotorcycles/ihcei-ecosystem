# LISM — Significance & Contributions (for peer review)

*Written for the reviewer's core question: "what does this contribute, and why
should it be published?" Every claim is anchored to evidence in this deposit and
scoped honestly, because over-claiming is what sinks a negative-result paper.*

---

## Significance statement (120 words)

A widespread intuition — that systemic viability couples to communication fidelity
*quadratically*, so small fidelity losses compound into accelerating collapse —
underwrites costly "zero-defect" policy across medicine, software, finance, and
governance. It had never been tested under conditions that could falsify it. We
pre-register such a test and run it in every domain where an independent two-hop
measurement is possible. The quadratic is disconfirmed; a **linear law, E = U·D**,
holds in three independent channel-intact domains. From the same program we
validate a cheap, deployable early-warning instrument — enforcement latency τ_v —
and a reusable protocol for testing coupling claims without circularity. The
contribution is a corrected prior, a usable sensor, and a method, each reproducible
from raw public data.

---

## Contribution 1 — A pre-registered falsification and a replacing law (primary)

- **What is new:** the first *pre-registered, two-directional* test of quadratic vs
  linear fidelity coupling, with the falsification criterion fixed (SHA-256 locked)
  before data. The strong hypothesis (the squaring, specifically) was promoted to a
  falsifiable prediction, tested, and **failed**; the **linear law E = U·D** is
  established in its place.
- **Evidence & generality:** consistent across three *independent* channel-intact
  domains — yeast interactome (N = 4,825, VIF = 1.003), pre-registered GitHub cohort
  (N = 992, VIF = 1.02, ΔAIC = −3.48), and a live Stack Exchange knowledge network
  (N = 793, VIF = 1.08) — plus a directionally linear one-hop legislation run.
- **Why it matters to a reviewer:** negative results are undervalued precisely
  because they are rarely done rigorously. This one is *pre-registered, cross-domain,
  and constructive* (it replaces the falsified claim with a validated one). It also
  **corrects its own prior published error** (the "quadratic anti-predictive AUC
  0.41" shown to be a non-converged-fit artifact), which is a marker of integrity,
  not weakness.

## Contribution 2 — A validated, deployable instrument (τ_v)

- **What is new:** enforcement latency τ_v — the time a system takes to close its
  own flagged risks — as a *measured, domain-general* leading indicator of collapse,
  and its reformulation from a brittle **deterministic fidelity gate** (`D ≥ D_min`)
  to a robust **probabilistic hazard floor**.
- **Evidence:** GitHub failed vs surviving repos 50.6 d vs 19.8 d, MWU p ≈ 10⁻³¹
  (10⁻²⁹ on directly-measured latency; imputation biased against the finding). The
  semantic sensor it replaces fires on only 23% of items and returned a
  fully-powered pre-registered null (p = 0.735); the τ_v/σ hazard model reaches
  AUC 0.898 vs 0.828.
- **Why it matters:** immediate, low-cost practical utility — computable from
  timestamps organisations already keep, transferable to clinical RCA-closure,
  audit-remediation, and time-to-patch. A reference implementation ships
  (`tau_v_monitor/`, 13 tests).

## Contribution 3 — A reusable, anti-circular protocol

- **What is new:** a testing discipline that makes coupling claims falsifiable
  without the circularity that plagues this literature: **pre-registration** with a
  two-directional rule, a **variance-inflation (channel-intact) gate** that refuses
  to over-read collapsed measurements, **honest non-test triage**, and **layer
  discipline** (Layer 1 falsifiable vs Layer 3 interpretive).
- **Evidence it works:** it forced the exclusion of degenerate cohorts (SEC EDGAR,
  Enron) and — demonstrated live here — flagged 52 convenient GitHub/Kaggle datasets
  across three domains as **0 eligible** two-hop tests, preventing a false positive.
- **Why it matters:** the protocol is portable to any field making
  fidelity-to-outcome claims; the framework earns trust by *publishing its own
  disconfirmations*.

## Contribution 4 — Full computational reproducibility

- Every headline number recomputes from raw public data (STRING, DEG, BioGRID for
  yeast; a locked CI run for GitHub; live Congress/Stack Exchange APIs), with pinned
  dependencies, checksums, an independent referee report, and a deterministic
  fixture for CI. This is the reproducibility bar reviewers increasingly require.

---

## Anticipated reviewer objections — and where each is answered

| Likely objection | Response (in-deposit) |
|---|---|
| "A null result — so what?" | Pre-registered, cross-domain, *constructive* (replaces the claim); corrects a prior artifact (M5). |
| "Only two domains; not general." | Now three channel-intact domains + a legislation one-hop; generality bounded honestly, extension route pre-registered. |
| "Datasets were cherry-picked / circular." | VIF channel-intact gate + non-circular measured outcomes; two independent searches show 0 eligible convenient datasets — no cherry-picking possible. |
| "τ_v is just centrality/size." | τ_v survives measured-only restriction and imputation biased against it; hazard model beats the semantic gate on unseen data. |
| "Effect sizes are modest (SE AUC ~0.6)." | Reported honestly; the *linear-vs-quadratic* verdict (the tested object) is robust to it; time-confound named. |
| "Religious framing undermines rigor." | Strictly firewalled: Layer 1 (tested) vs Layer 3 (interpretive prior, not dataset-adjudicated); the empirical contribution stands without it. |

## One-line positioning
LISM converts a popular but untested scaling intuition into a **falsified**
hypothesis, a **replacing linear law**, a **deployable early-warning sensor**, and a
**reusable protocol** — reproducibly, and with its own scope stated plainly.
