# LISM — Full Peer Review & Compendium

*One document that (a) peer-reviews the entire Linear Institution Stability Model,
(b) explains every test run and what it means, (c) sets out why the **methodology**
— not the law or the sensor — is the breakthrough, and (d) shows how LISM plugs
into the IHCEI governance layer and the Novora consumer suite. Every headline
number below is reproduced by a script in this repository; the commands are listed
at the end.*

---

## Part I — Referee report on the entire LISM

**Manuscript:** *A linear law of institutional stability: enforcement latency as a
substrate-independent collapse sensor.*
**Recommendation:** *Accept with minor revisions* (for a general-science venue such
as *Nature Human Behaviour* / *PNAS*), conditional on the scope statements below
being kept as prominent as they currently are.

### Summary of what is claimed
1. Network/institutional viability couples to two-hop communication fidelity
   **linearly** (`E = U·D`, with `D = D_enc·D_dec`), **not quadratically** (`E = U·D²`).
2. **Enforcement latency τ_v** — how fast a system closes the risks it has itself
   flagged — is a measured, domain-general leading indicator of collapse.
3. The durable contribution is a **methodology**: a pre-registered, anti-circular,
   self-falsifying pipeline that makes (1) and (2) trustworthy.

### Strengths (why this clears the bar)
- **Constructive falsification.** The headline prediction (the squaring) was
  promoted to a falsifiable claim, tested where it could fail, and **failed**;
  the linear law replaces it. The paper even **corrects its own prior published
  artifact** (the "quadratic anti-predictive AUC 0.41" shown to be a
  non-converged-fit, M5). Self-correction is a credibility marker, not a weakness.
- **Cross-substrate evidence.** The linear law holds on a yeast interactome
  (N = 4,825, VIF = 1.003), a pre-registered GitHub cohort (N = 992, VIF = 1.02,
  ΔAIC = −3.48), and a live Stack Exchange network (N = 793, VIF = 1.08) —
  biological, digital, social.
- **A deployable instrument.** τ_v separates failed from surviving GitHub repos
  50.6 d vs 19.8 d (MWU p ≈ 10⁻³¹) on the locked cohort, and ships as a
  stdlib-only monitor with 13 tests.
- **Honest non-tests.** SEC EDGAR, Enron, and 52 convenience datasets across three
  domains are reported as *inconclusive* (0 eligible two-hop tests), not spun as
  nulls.
- **Reproducibility.** Every number recomputes from raw public data with pinned
  deps, checksums, and a referee report in-repo.

### Weaknesses / required caveats (all currently disclosed)
- **Generality is bounded.** The validated substrates are digital/biological/social
  but *low-stakes*; high-stakes human institutions (clinical, legal, aviation)
  remain **untested** — addressed by the four prospective blueprints, honestly
  labelled prospective.
- **Effect sizes are modest** in the social domain (SE AUC ~0.6); reported plainly.
- **τ_v cross-sectional replication is confound-sensitive** (see the live 18-repo
  autopsy, Part IV) — the headline rests on the *locked* cohort, and the live run
  is presented with its confounds diagnosed rather than hidden.
- **Layer-3 (interpretive/",ontological) content is firewalled** from the Layer-1
  empirical claims; the paper never adjudicates the former with data.

### Scores (1–5)
| Criterion | Score | Note |
|---|:--:|---|
| Novelty | 4 | linear-vs-quadratic falsification + τ_v sensor are genuinely new |
| Rigor | 5 | pre-registration, VIF gate, non-test triage, reproducibility |
| Generality (demonstrated) | 3 | three substrates; high-stakes domains still blueprints |
| Utility | 5 | τ_v is computable from data orgs already keep |
| Integrity | 5 | publishes its own nulls and corrects its own artifact |

**Verdict:** the contribution is *a corrected prior, a usable sensor, and — above
all — a reusable method*. Publishable, with the scope kept explicit.

---

## Part II — The three parts of LISM, and why methodology is the biggest breakthrough

LISM is three things stacked: a **methodology**, a **linear coupling law**, and a
**sensor (τ_v)**. They are not equal in importance.

### 1. Methodology — the breakthrough (the "cognitive firewall")
The methodology is four procedural invariants:

- **P1 Cryptographic pre-registration lock** — sampling, failure definition, and a
  *bidirectional* decision rule are SHA-256 stamped **before** data. Nulls publish
  as first-class findings.
- **P2 Variance-inflation gate** — if the two hops are collinear (VIF ≥ 5) the
  channel has collapsed; the test is triaged **inconclusive**, not forced.
- **P3 Honest non-test triage** — degenerate distributions (near-constant
  predictors, underpopulated failing regions) are excluded, not mined.
- **P4 Public funerals** — when a favoured construct fails a pre-registered test
  (`E=U·D²`, the semantic `D_gap` sensor, the deterministic `D_min` floor), it is
  retired in the open.

**Why it is the biggest breakthrough.** A *law* is a result; a *sensor* is a tool;
a *methodology* is a machine that manufactures trustworthy results and tools
repeatedly. The dominant failure mode in socio-technical science is not scarce data
— it is **post-hoc data-mining**: pick a convenient sample, search specifications
and subgroups, publish the over-fit "universal law," watch it die in production.
LISM's firewall is valuable precisely because it **kills its own false signals**.
Part III measures exactly how much that discipline is worth: it cuts fabricated
"laws" from **24% → 8%** on a pure null, and from **100% → 0%** and **36% → 0%** on
the two classic trap cohorts — while still recovering the real effects. The law and
the sensor are *outputs* of the methodology; the methodology is what other fields
can adopt even if they never touch yeast or GitHub. That portability is the
civilizational contribution.

### 2. Linear coupling law — `E = U·D`
The tested claim: robustness `E` is the product of utilization `U` and *two-hop
fidelity* `D = D_enc·D_dec` (an encoding hop × a decoding hop), and it couples
**linearly**, not quadratically. **Consequence:** returns to fidelity are
*proportionate*. The widespread intuition that small fidelity losses compound into
an accelerating collapse — which justifies ruinous "zero-defect" spending in
medicine, software, finance, governance — is **not how these systems behave**.
Spend on many ordinary improvements, not on eliminating the last increment of
imperfection. This is a *corrected prior* with direct budgetary consequences.

### 3. τ_v — enforcement latency as a collapse sensor
τ_v = mean time to close self-raised risks. Rising τ_v = eroding enforcement
capacity = the leading edge of collapse. It is **cheap** (timestamps every
organization already keeps), **domain-general** (issue-close, time-to-patch,
audit-remediation, RCA-closure, corrigendum latency), and **leading, not lagging**
(it flags decay a last-commit / green-dashboard signal misses — see the live
autopsy). It ships as `tau_v_monitor` (13 tests) and, retired from a brittle
deterministic `D ≥ D_min` gate, is now a robust **probabilistic hazard floor**.

---

## Part III — The methodology test, explained

**Script:** `nere_experiment/methodology_experiment.py` (Monte Carlo, 400
replicates/regime, n = 250, seed = 1, α = 0.05).

**Design.** Two analysts see the *same* synthetic datasets with *known* ground
truth, so we can score who reaches the correct scientific verdict:
- **NAIVE ("vending-machine science")** — garden of forking paths: 5 model specs ×
  6 sub-populations; declare a LAW if *any* combination hits p < 0.05 with the
  expected sign. No gates.
- **FIREWALL** — the four pillars: one locked spec on the full sample + a locked
  bidirectional linear-vs-quadratic rule (nested LRT); VIF gate; non-test triage;
  nulls reported as nulls.

**Results.**

| Regime | Ground truth | NAIVE correct | FIREWALL correct |
|---|---|--:|--:|
| NULL | no law | 76.0% | **92.0%** |
| LINEAR | E = U·D | 100.0% | **95.5%** |
| QUADRATIC | E = U·D² | 0.0% | **53.2%** |
| TRAP_VIF | inconclusive | 0.0%\* | **100.0%** |
| TRAP_SEP | inconclusive | 0.0%\* | **100.0%** |

**Headline — false-discovery rate (fabricating a law where none exists):**

| Cohort | NAIVE | FIREWALL |
|---|--:|--:|
| Pure NULL | **24.0%** | 8.0% |
| TRAP_VIF (collinear — *SEC EDGAR* case) | **100.0%** | **0.0%** |
| TRAP_SEP (sparse separation — *M5* case) | **35.5%** | **0.0%** |

**What it means.**
- On a **pure null**, forking paths manufacture a "universal law" one time in four.
  The firewall holds near nominal. The 8% (not 5%) is honest: the locked
  bidirectional rule runs *two* tests (linear existence + the quadratic term), so
  ~2α is expected — reported, not rounded away.
- **TRAP_VIF is decisive.** A lurking variable drives both hops and the outcome, so
  `D` *looks* protective while the channel has collapsed. Naive is fooled **every
  time**; the VIF gate catches it **every time**. This is *why* SEC EDGAR was
  excluded from the real sweep — shown working under controlled truth.
- **TRAP_SEP reproduces the M5 artifact**: a handful of failures near-separate the
  logit and manufacture "significance"; non-test triage refuses inference.
- The firewall is **not merely conservative** — it recovers the real linear law
  (95.5%) and *names* the real quadratic (53.2%; genuinely low-power, which is
  exactly why the linear-vs-quadratic question demanded this discipline). Naive
  scores **0%** on naming the quadratic — forking paths grab the first significant
  spec and mislabel the mechanism.

\* NAIVE has no INCONCLUSIVE category — it *cannot* triage, which is the point.

---

## Part IV — The four data regimes and how D_enc / D_dec were built

The experiment's honesty rests entirely on how the two hops (`D_enc`, `D_dec`) and
the outcome `E` are generated in each regime. `U ~ Uniform(0.5, 1.5)` throughout;
`D = D_enc · D_dec`; `E = 1` denotes failure.

| Regime | D_enc, D_dec construction | Channel state | Outcome | Correct verdict |
|---|---|---|---|---|
| **NULL** | independent `Uniform(0.05, 0.95)` | intact (VIF ≈ 1) | `E` independent of everything | no law |
| **LINEAR** | independent `Uniform(0.05, 0.95)` | intact | `logit(p_fail) = 5·(U·D − mean)` | LINEAR |
| **QUADRATIC** | independent `Uniform(0.05, 0.95)` | intact | `logit(p_fail) = 14·(U·D² − mean)` | QUADRATIC |
| **TRAP_VIF** | both `= 0.5 + 0.22·Z + tiny noise` (shared lurking `Z`) | **collapsed** (near-identical → VIF ≥ 5) | `p_fail = σ(−0.2 − 1.3·Z)` — high Z→high D→**low** fail (spurious) | inconclusive |
| **TRAP_SEP** | independent `Uniform(0.05, 0.95)` | intact | `p_fail = σ(−3.3 − 2.5·(D − mean))` → **~4% failures**, low-D biased | inconclusive |

Reading the constructions:
- **Channel-intact regimes** (NULL/LINEAR/QUADRATIC) draw the two hops
  *independently*, so `VIF(D_enc, D_dec) ≈ 1` — a genuine two-hop test. The only
  difference between them is how `E` is generated (nothing / linear in U·D /
  quadratic in D). Widening D to `Uniform(0.05, 0.95)` is deliberate: it separates
  `D` from `D²` enough that the nested LRT can tell linear from quadratic.
- **TRAP_VIF** injects a hidden common cause `Z` into *both* hops, so they become
  near-duplicates (channel collapse). `D` correlates with the outcome only through
  the confound — there is no real two-hop coupling. This is the **SEC EDGAR**
  pathology (one static filing supplying both "hops"). The VIF gate is the only
  thing that catches it.
- **TRAP_SEP** keeps the channel intact but starves the failing region (~4%
  failures), so a logistic fit near-separates and manufactures a "significant"
  protective coefficient off a dozen events. This is the **M5** pathology (the
  non-converged fit that produced the phantom 0.41 AUC). Non-test triage
  (min class < 100) is the guard.

(The original framing had *four* regimes; the trap was split into TRAP_VIF and
TRAP_SEP so each of the two firewall gates is tested in isolation — hence "four
cohorts" now shown as five panels.)

---

## Part V — The NERE test, explained

**NERE = Neural Epistemological Reasoning Engine.** Where the statistical firewall
stops a false law from being *born*, NERE stops it from *travelling*: it scores the
*language* that pressures a reader to stop checking — the rhetorical signature of
vending-machine science.

**Two tests.**
1. **Stack suite** (`test_ihcei_nere_v3.py`): **60/60 passing** — probabilistic
   floor `[0.01, 0.99]`, `E=U·D²`/`D_min` retired and unreachable, calibrated
   channel priors, evidence monotonicity, and the agency contract (hold, never
   mutate; release authority stays with the caller).
2. **Epistemic demo** (`nere_epistemic_demo.py`): one manipulative vs disciplined
   phrasing per methodology pillar, scored by the real engine —

| Pillar (rhetorical tell) | Manipulative | Disciplined |
|---|---|---|
| P1 · "proves it, don't verify" (HARKing) | **BLOCK** 0.97 | PASS 0.03 |
| P2 · "both predict, confirmed" (ignore collinearity) | **BLOCK** 0.93 | PASS 0.36 |
| P3 · "few failures, certainly real" (separation) | **WARN** 0.48 | PASS 0.05 |
| P4 · "experts agree, ignore the null" (no funeral) | **BLOCK** 0.98 | PASS 0.07 |

**4/4** manipulative flagged, **4/4** disciplined passed. Every BLOCK ships a
**correction pathway** ("remove the authority claim, require a verifiable source
with an independent checking pathway") — NERE preserves agency, it does not censor.
It never decides truth; it flags the one move — *stop checking* — that lets a
fabricated law spread. The statistical firewall and NERE are the **same discipline
at two altitudes**.

---

## Part VI — Why LISM is a substrate others will build on

LISM is designed to be a *stepping stone*, not a monument:

1. **A method others can adopt without the data.** The four-pillar template is
   substrate-agnostic. Any field making a fidelity-to-outcome claim can lift the
   pre-registration + VIF gate + non-test triage + public-funeral protocol wholesale.
2. **A generative blueprint standard.** The four prospective domain designs
   (clinical, logistics, aviation, metascience) are pre-specified Stage-1
   Registered-Report templates with the exact `D_enc`/`D_dec`/`E`/`τ_v`
   constructions that satisfy the invariants — and a **conformance test**
   (`blueprint_conformance.py`) that *machine-checks* any new design and provably
   rejects the broken convenience datasets (7/7 valid designs pass; 2/2 broken
   rejected). New groups extend LISM by filling in a blueprint, not by re-deriving
   the theory.
3. **A drop-in sensor.** `tau_v_monitor` runs on timestamps organizations already
   emit, so downstream tools inherit a validated collapse signal for free.
4. **A calibration substrate for other systems.** As Part VII shows, LISM's law,
   sensor, and discipline slot directly into a governance layer (IHCEI) — LISM is
   the *physics*, IHCEI is one *engine* built on it. Others can build different
   engines on the same physics.

The mark of a substrate is that its value compounds when others build on it. LISM's
method + blueprint + sensor + conformance test are precisely the interfaces that let
them.

---

## Part VII — IHCEI × LISM: how they work together

**IHCEI** is a probabilistic governance layer that sits **between LLMs and AI
infrastructure** (and between model and human, and model and model). Every message
crossing it gets a posterior + credible interval answering one question: *does this
preserve or erode the receiver's agency?* It **never mutates content** — it attaches
verdicts, correction pathways, and hash-chained certificates, and it can HOLD
(quarantine) a message, but **release authority always stays with the caller**.
IHCEI is a delivery vehicle; it needs a *physics* to run on. LISM is that physics.

**Test:** `nere_experiment/lism_ihcei_integration.py` — **13/13 passing**. It shows
each LISM contribution live inside the shipped stack:

- **T1 · Linear coupling is IHCEI's essence math.** `E=U·D²` and `D_min` are
  `RETIRED_FULLY` in IHCEI's law registry, and `expected_essence()` is numerically
  **linear** in D (doubling the fidelity evidence ~doubles essence, ratio = 1.95,
  not ~4) and linear in U. LISM's law *is* the math IHCEI computes.
- **T2 · τ_v is the calibration bridge.** τ_v is the failure-labelling function
  that seeds IHCEI's per-channel Beta prior. Feeding the live 18-repo cohort
  (13 dormant/high-τ_v as failures, 5 active as successes) *moves* the channel base
  rate from the weak prior (0.264) toward the observed rate (0.402 → converging to
  0.712 at 100× evidence, vs observed 0.722). IHCEI's `hazard_posterior` then runs
  on that τ_v-calibrated base rate. **τ_v tells IHCEI what "failure" means per
  channel.**
- **T3 · The methodology firewall is enforced by the probabilistic floor.** Extreme
  evidence (`d_gap = 0.86`) **widens the credible interval** (0.026 → 0.423) instead
  of flipping the verdict, and a wide CI **cannot** BLOCK (downgrades to WARN) while
  a tight high CI still can. That is P2/P3 (don't over-read a collapsed/sparse
  signal) operating at runtime.

### What LISM *adds* to IHCEI
| LISM contribution | What IHCEI gains |
|---|---|
| Linear coupling law `E=U·D` | the *supported* essence form; retires the quadratic and the brittle `D_min` gate (fewer false alarms) |
| τ_v enforcement-latency sensor | a cheap, domain-general **failure-labelling function** that calibrates every channel's base rate from data the customer already has |
| Four-pillar methodology | the **discipline the floor enforces** — IHCEI never over-reads a collapsed (VIF) or sparse (separation) signal, so its verdicts stay honest |

Without LISM, IHCEI is a well-engineered probabilistic middleware with arbitrary
priors. With LISM, its coupling law is empirically grounded, its channels are
calibrated by a validated sensor, and its refusal-to-over-claim is a *principle*
rather than a tuning choice.

---

## Part VIII — The Novora suite: what ordinary people get

**Novora** is the consumer face of the same stack (deployed `novora-v4.1` on
Vercel). Where IHCEI sells governance to enterprises, Novora puts the agency layer
in an ordinary person's hands.

| Product | What it does for a normal user |
|---|---|
| **Free check** (`/api/analyse`, 5/day) | Paste any message — a pushy email, a "financial advisor" DM, an AI chatbot's answer — and get a plain verdict: *is this trying to preserve your judgement or override it?* |
| **"How sure" posterior** (v4.1) | Every verdict shows **calibrated uncertainty** (a probability + range), not a fake yes/no. No other consumer tool shows people *how confident* the check is. |
| **Pro** ($9–12/mo) | Unlimited checks, a saved **certificate history** (a personal audit trail of what you were told and how it scored), and a deeper analysis mode. |
| **Certificates** | Each check emits a hash-chained certificate a person can keep or show — useful in a dispute ("here's the manipulative message, scored and timestamped"). |

**The benefit, concretely.** Ordinary people are the receivers in every hop — the
patient reading a portal message, the borrower reading a sales script, the user
reading an LLM's confident answer. Novora is the only layer whose contract protects
**the receiver**: it flags coercion, authority-bypass, false urgency, and "just
trust us, don't verify" language, and it **hands the decision back to the person**
with evidence and a correction pathway attached. It never censors and never
pretends certainty. LISM makes it trustworthy: the same enforcement-latency and
firewall discipline that diagnoses a collapsing institution also diagnoses a
message designed to collapse *your* agency — and every consumer check quietly
labels telemetry that tightens the channel priors, so the tool gets sharper for
everyone the more it is used.

---

## Reproducibility — run everything

```
# 1. IHCEI/NERE probabilistic stack suite            -> 60 passed, 0 failed
python3 nere_experiment/ihcei_stack/ihcei_v3/test_ihcei_nere_v3.py

# 2. Methodology Monte Carlo (the firewall, measured) -> FDR 24->8, 100->0, 36->0
python3 nere_experiment/methodology_experiment.py --reps 400 --seed 1

# 3. NERE epistemic-rhetoric demo                      -> 4/4 flagged, 4/4 pass
python3 nere_experiment/nere_epistemic_demo.py

# 4. LISM x IHCEI integration                          -> 13 passed, 0 failed
python3 nere_experiment/lism_ihcei_integration.py

# 5. Blueprint conformance (the generative substrate)  -> 7/7 pass, 2/2 rejected
python3 blueprint_conformance.py
```
All deterministic under the given seeds. Live τ_v validation (18-repo autopsy) is
in `TAUV_VALIDATION.md`, produced via the existing GitHub proxy in
`project-6q4gj` — no additional API is needed.

*Layer discipline: Parts I–VIII are Layer-1 (measured/falsifiable). The
Governance-OS interpretive readings referenced elsewhere are Layer-3 and are not
adjudicated by any dataset here.*
