# Novora, explained for everyone — what we built, what we tested, what came back

*Every number below is a real measurement from a real experiment in this
repository. Nothing here is a projection. Where a claim is philosophical rather
than measured, it is labelled **Layer 3 (interpretation)** and kept strictly
apart from **Layer 1 (measured)** — the same discipline the LISM manuscript uses.*

---

## The one-sentence idea

Today's AI race optimizes for **speed** — how fast a machine can write text or
code. Novora bets that once machine intelligence is cheap and everywhere, speed
stops being scarce. What becomes scarce is **trust**: keeping a human in charge,
knowing what a model *doesn't* know, and being able to *prove* what happened.
Novora builds the layer that does that — a **verifier that never censors**, only
measures, records, and hands the final decision back to the person.

Think of it as the **seatbelt and dashboard** for AI, not a faster engine.

---

## The technologies, in plain words

| Name | In one sentence | What it really is |
|---|---|---|
| **LISM** | A law for when organizations quietly rot. | *Linear Institution Stability Model.* Networks fail on a slow slide, not a cliff; the early-warning gauge is **enforcement latency τ_v** — how long a problem sits unfixed. |
| **IHCEI** | The gatekeeper that checks claims before they reach you. | An **epistemological** gateway (about *knowledge*, not morality): does this claim hold up? It never mutes — it calibrates. |
| **NERE** | The tiny engine inside the gatekeeper. | The on-device kernel that scores manipulation/uncertainty with a strict "floor" so it stays silent unless there's a real mechanism, not just urgent words. |
| **HELM** | The consumer-facing guard on your device. | Runs NERE locally, zero network, with four protective primitives (scam armor, dark-pattern spotting, capacity meter, tamper-proof wallet). |
| **EI** | The unifying idea: intelligence that *knows what it doesn't know*. | *Epistemological Intelligence.* Composes five proven primitives — **Audit, Delegate, Develop, Prove, Hazard** — into one non-suppressive contract. |
| **EI LLM** | Eight verifier models in two families. | A receiver-side attestation layer: **Veridian** (deep audit) + **Apex** (on-device edge). It checks generators; it doesn't compete with them. |
| **Echo Database** | A ledger you can't secretly edit. | Append-only, hash-chained, Merkle-provable storage: every decision leaves a tamper-evident receipt. |
| **Page Code** | An "OAuth of agency" for coding agents. | A stake-bounded permission table: an AI agent may edit `src/**` but is physically blocked from force-push, secrets, or payments without a human. |
| **Agency Internet** | The protocol for machines negotiating on your behalf. | The addressing/permission fabric so autonomous agents transact with bounded, revocable authority. |
| **Novora PAGES** | Provenance welded into media. | Every second of generated audio/video is bound to its source under a hash chain; a splice or deepfake breaks the chain at the exact spot. |
| **Novora suite** | The 9-product app. | The shipped `$0`, keyless, on-device product surface that screens content and actions. |
| **SRE** | The reliability compass for AI swarms. | *Site-Reliability.* Watches τ_v and throttles an agent swarm the moment its fix-queue saturates. |
| **ADG / TQG-CFE** | Telemetry for a network's health and how it "renders" its world. | Organization-graph equations (like `E=U·D`, **not** physics with SI units): `C_dev` = network development; `Ψ` = whether a node experiences ease, hardship, or chaos. |

---

## What we tested, and exactly what came back

### 1. LISM — the rot law (the scientific anchor)
- **The gauge works.** Across **N=992** real institutions, organizations that
  later failed had a fix-latency of **τ_v = 50.6 days** vs **19.8 days** for
  survivors — separated at **p ≈ 10⁻³¹**. A slow fix-queue is the tell.
- **It's the *process*, not the *words*.** A static keyword sensor (`D_gap`) that
  read surface text was a **complete null (p ≈ 0.735)**. The sensor that tracked
  the *running* self-correction rate (`τ_v`) succeeded at **p ≈ 10⁻³¹**.
- **Independently reproduced.** A biological analog — a yeast protein network of
  **N=4825** nodes — reproduces the same two-hop structure with collinearity
  **VIF = 1.003** (the encode and decode channels are genuinely independent).
- **Reproducible from committed raw data** with stdlib-only code (`repro/`).

### 2. IHCEI + NERE — the gatekeeper and its kernel
- **62/62** NERE kernel tests (floor, bands, gates, corroboration, learning).
- **11/11** fast/deep seam tests — the free on-device path and the paid deep path
  compute *identical* posterior math.
- On real traffic the gate produced **0.000 false-holds on emergencies** and
  **0.000 false-positives on clean text**, at 0.90 recall on blunt manipulation.

### 3. HELM — the on-device guard
- **48/48** core tests + **22/22** cross-engine parity + **7/7** pre-registration
  lock + **23/23** real-traffic contribution tests.
- **Alarm fatigue solved on real data:** across **281 live registry texts**,
  routine notices firing dropped from **87.9% → 0.0%**; 7/7 deprecations stayed
  silent; 6/6 real threats still caught.
- On **306 real README paragraphs**, calibration error (Brier) improved from
  **0.205 → 0.074** with the gate on.

### 4. EI — the unifying layer
- **17/17** tests: composes Audit, Delegate, Develop, Prove, Hazard into one
  contract where **release always stays with the human** and every decision is
  attested. Non-suppressive by construction.

### 5. EI LLM — the eight verifier models *(new this round)*
- **17/17 field checks on real GitHub data**, plus **9/9** unit tests.
- **Veridian SENTRY** on 22 real repos: threw the throttle, flagged **4 zombie
  queues** (loud-alive but rotting), and confirmed survivors close issues far
  faster (**26.5 vs 101.7 days**).
- **Apex PAGE CODE**: allowed an in-scope edit but **denied force-push and secret
  edits** — every action written to a hash-chained ledger.
- **Veridian PAGES**: localised a deep-faked media frame to the **exact second**.
- **Veridian CHARTER**: flagged a **circular citation loop**; passed a doc anchored
  to a real primary source.
- **Apex SHIELD**: alarmed on a scam (*"wire the money now, don't tell anyone"*,
  p=0.98) but stayed **silent on benign urgency** (*"restart the server now"*).
- **Apex ASCENT**: injected friction only when the human stopped verifying.
- **Veridian VITALIS**: refused to write a prescription to the record until a
  physician audited the evidence.
- **Apex SCALE**: turned one authoritative answer into 3 paths with calibrated
  odds that sum to 1.

### 6. Echo, Page Code, Agency Internet, Novora PAGES, Novora suite
- **Echo**: append-only hash chain verifies intact; editing any past field is
  detected and located.
- **Page Code**: default-deny permission table; force-push/keys/payments blocked;
  SHA-256 ledger of agent actions.
- **Novora PAGES**: tamper anywhere in a media stream breaks the provenance chain
  at the exact coordinate; "tap-to-source" returns the un-mutated grounding passage.
- **Novora suite**: 9 products screen content on-device at **`$0` marginal cost,
  zero network** — verified live in production (project-6q4gj): all 12 legitimate
  emergencies PASS; live τ_v read express **2.72d** vs a stalled repo **251.3d** (92×).

### 7. SRE — the swarm compass
- The τ_v hazard monitor (**13/13** tests) throttles automation the instant a
  queue's latency drifts above its own baseline — bounding an AI swarm's output
  to the human team's real corrective capacity.

### 8. ADG / TQG-CFE — network health & "rendering"
- **ADG `C_dev`** (network development from pure graph topology): survivors
  **3.19 vs 1.18**, **p = 0.025, AUC 0.78**.
- **TQG `A_n`** (alignment): **p = 0.018, AUC 0.80**.
- **Two-hop fidelity `D`**: **p = 0.028, AUC 0.78**.
- **Ψ rendering**: **Yusr (ease) 9/9 survive**; the **Chaos** class cleanly isolates
  the deceptive repos (archived-but-fast) that a naive check mislabels.
- **Shirk detector** (say-do gap): flags "zombie" repos — fresh-looking but
  rotting — at **p = 0.0013**.

**Grand tally:** 100+ JavaScript assertions, 86+ Python assertions, multiple live
field trials, and three live production endpoints — all green, all reproducible.

---

## Why the universe being "computational" is a *testable* claim here

Two thinkers frame this:
- **Stephen Wolfram** — reality at its base isn't matter; it's a network of simple
  rules being rewritten step by step. Matter is an *emergent* pattern of information.
- **Donald Hoffman** — what we perceive isn't the truth of the world; it's a
  *fitness interface* (a "headset"), shaped by evolution to keep us alive, not to
  show reality.

These are usually *philosophy*. Novora's contribution is to turn three of their
claims into **numbers measured on real networks** (**4/4 supported**, 22 repos):

| Claim | Plain meaning | What we measured |
|---|---|---|
| **Substrate independence** (Wolfram) | Institutions survive on *information*, not physical mass | `C_dev` from pure graph topology predicts survival — **p=0.033** — with no funding/headcount inputs |
| **Computational irreducibility** (Wolfram) | No shortcut predicts a complex system; you must *run it* | The frozen snapshot is dominated (**AUC 0.75**) by the running-process sensor (**AUC 0.83**); at scale the static sensor is a full null (p≈0.735) while the process holds (p≈10⁻³¹) |
| **The interface renders** (Hoffman) | Perception is a fitness dial, not truth | Alignment `A_n` renders ease/hardship/chaos and tracks survival — **p=0.018, AUC 0.80** |
| **Why the interface *survives*** (Hoffman's FBT gap) | Fitness-beats-truth says *why it's chosen*, not *why it lasts* | Decay is **linear, not a cliff** (adjusted R² prefers the linear fit) — the buffer that lets a world-blind interface coast on raw utility |

**Layer 3 (interpretation):** if institutions, biology, and perception all obey
the same information-decay law, that is consistent with a reality whose base is
computation rather than matter. **Layer 1 (measured):** the four numbers above.
We claim only Layer 1; the cosmological reading stays an explicitly-labelled analogy.

---

## How this helps human civilization — with the data

1. **Stops institutional collapse before the cliff.** τ_v is a cheap, live gauge
   (p≈10⁻³¹, N=992) that gives months of warning — for companies, agencies, open
   infrastructure — because the decay is a *slow slide*, not a sudden failure.

2. **Makes AI swarms safe to deploy at scale.** SENTRY/SRE bound a swarm's speed
   to a human team's *real* review capacity (survivors close in 26.5d vs 101.7d
   for the rotting). Autonomy without runaway cascades.

3. **Kills alarm fatigue — the reason people mute safety.** On 281 real texts,
   false alarms fell **87.9% → 0.0%** while real threats were still caught 6/6.
   A guard people don't switch off is the only guard that protects anyone.

4. **Keeps humans in the driver's seat.** Page Code, VITALIS, and SCALE make the
   AI a calibrated *copilot*: it can act within bounds, but force-push, prescriptions,
   and high-stakes choices need a human who *audited the evidence* — with a
   tamper-proof receipt each time.

5. **Fights deepfakes and hallucinated citations structurally.** PAGES localises a
   tamper to the exact second; CHARTER flags circular "prestige-trap" citations.
   Trust becomes *verifiable*, not assumed.

6. **Protects cognition itself.** ASCENT detects when a person is outsourcing their
   thinking and adds friction — so AI in education *grows* capability instead of
   hollowing it.

7. **Costs `$0` at the edge, harvests no data.** The Apex family runs on-device,
   ≤4GB, zero network — sidestepping the cloud "billing trap" and keeping privacy
   by physical topology.

8. **Refuses to lie to itself.** Every headline is pre-registered under a SHA-256
   lock; if a model fails the sealed threshold, the system reports the **null**
   honestly (as LISM's `D_gap` and federation nulls show it already has).

---

## Reproduce any of it

```bash
node ei-llm/field_test.mjs                       # EI LLM — 17/17, real GitHub cohort
node --test ei-llm/ei-llm.test.mjs               # EI LLM — 9/9 unit
python3 adg-tqg/experiment_enriched.py           # ADG/TQG — 4/4 governance-telemetry
python3 adg-tqg/experiment_wolfram_hoffman.py    # Wolfram + Hoffman — 4/4
python3 repro/reproduce_tauv.py                  # LISM τ_v law from committed raw data
python3 repro/reproduce_yeast.py                 # yeast VIF=1.003 from committed STRING v12
```

*Two layers, never mixed. Layer 1 is everything with a p-value. Layer 3 is the
interpretation, always labelled. Novora only claims Layer 1.*
