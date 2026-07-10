# IHCEI's contribution to AI alignment

*What a probabilistic governance layer that sits between LLMs and AI
infrastructure adds to the alignment problem — stated concretely, scoped
honestly, and grounded in the shipped stack (60/60 tests) and its LISM physics
(13/13 integration tests). IHCEI is not a solution to alignment; it is a specific,
deployable piece of the defence-in-depth stack, and this document says exactly
which piece.*

---

## The one-paragraph version

Most alignment work tries to make a **model** safe from the inside (training,
RLHF, constitutional methods, interpretability). IHCEI takes the complementary
outside position: it governs the **messages that cross between** a model and a
human, or between two models, at runtime. Its single question per hop is not "is
this true?" but "**does this message preserve or erode the receiver's decision
authority?**" — answered as a posterior with a credible interval, never a
certainty, with content never mutated and release authority always left with a
human. That reframes a slice of alignment from *value-loading a model* to
*protecting human agency at the interface* — a target that is measurable,
auditable, and model-agnostic.

---

## 1. Agency preservation as an alignment objective

The hardest part of "aligned to human values" is that values are contested and
hard to specify. IHCEI sidesteps the specification problem for one important
sub-goal by optimizing a **procedural** target instead of a substantive one:
*keep the human able to decide.* It scores messages for the signatures that
**remove** agency — coercion, false urgency, authority-bypass ("just trust the
experts, don't verify"), manufactured consensus — and flags them, while leaving
genuinely informative content (including uncertainty) alone. This is corrigibility
seen from the message layer: an aligned interaction is one that keeps the human in
the loop and able to say no, and IHCEI measures exactly that (the NERE engine:
4/4 manipulative phrasings flagged, 4/4 disciplined passed, each flag carrying a
correction pathway rather than a silent block).

## 2. Independent, third-party auditing (no self-grading)

A model grading its own outputs for safety is a conflict of interest. IHCEI is an
**independent** layer: it audits the model's messages without being the model, so
its verdict is not entangled with the incentives that produced the content. In an
agentic world of many interacting models, this is the difference between "each
agent certifies itself" and "an auditor certifies the hop." IHCEI issues a
hash-chained **certificate** per hop, turning safety from an unverifiable claim
into an auditable record — the kind of artifact regulators, insurers, and incident
investigators can actually use.

## 3. Multi-agent alignment: governing the hops, not just the endpoints

As systems become agent-to-agent (LLM-A → LLM-B), the alignment surface moves from
single outputs to **inter-agent messages** — where coercion, prompt-injection, and
goal-hijacking propagate. IHCEI's `relay()` audits each inter-agent hop with the
same posterior contract and can HOLD a message (quarantine, never mutate) so a
manipulative instruction does not silently travel between agents. Its ledger raises
an **upstream alarm** when the HOLD rate climbs — a busy governance layer is a
symptom that the models feeding it are degrading. That is a fleet-level safety
signal you cannot get from inspecting one model in isolation.

## 4. Calibrated uncertainty instead of false confidence

A recurring alignment failure is **confident wrongness** — systems that assert
rather than hedge. IHCEI's verdicts live on a strict probabilistic floor
`[0.01, 0.99]`: **no endpoint can return certainty**, and a wide credible interval
*cannot* trigger a BLOCK (it downgrades to WARN). Uncertainty is encoded
structurally, so the layer refuses to over-read weak evidence. This is the honest
epistemics alignment needs, enforced by construction rather than by prompt.

## 5. What LISM adds — alignment grounded in a measured law, not tuned priors

Without LISM, IHCEI is well-engineered middleware with arbitrary thresholds. LISM
supplies the **physics** that makes its safety behaviour principled (see
`lism_ihcei_integration.py`, 13/13):

- **Linear coupling `E = U·D`** is IHCEI's essence math (the quadratic and the
  brittle hard `D_min` gate are retired) — so the layer does not over-penalize
  small fidelity losses, i.e. **fewer false alarms → less alarm fatigue**, itself
  an alignment property (an ignored safety layer is an unaligned one).
- **τ_v (enforcement latency)** is the failure-labelling function that **calibrates
  each channel's base rate from real data** — so IHCEI's priors are learned from the
  deploying organization's own telemetry, not guessed.
- **The four-pillar methodology** is the discipline IHCEI's floor **enforces** — it
  refuses to over-read a collapsed (VIF) or sparse (separation) signal, so the
  safety layer itself resists the false-signal failure mode that the methodology
  experiment showed cuts fabricated conclusions from 24–100% down to ~0–8%.

**In short: LISM makes IHCEI's safety verdicts empirically grounded, self-
calibrating, and disciplined against over-claiming — three properties an alignment
component must have to be trusted.**

---

## 6. Scope — what IHCEI does NOT claim (kept explicit)

- It does **not** make a model's internal objectives aligned; it governs the
  interface. Inner alignment, deception at the weights level, and capability
  control are out of scope.
- It does **not** decide truth; it flags agency-eroding communication. A false
  statement phrased respectfully can pass; that is by design — truth adjudication
  is a different layer.
- It is a **defence-in-depth** component, strongest in combination with training-
  time alignment and interpretability, not a replacement for them.
- Fast-mode pattern evidence is gameable; the durable product is the posterior
  math + calibration + the learning hook that retrains from labelled evasions.

## 7. Bottom line

IHCEI's contribution to alignment is a **deployable, independent, calibrated
agency-preservation layer for the message interface** — the place where
human-facing and agent-to-agent harms actually cross. It converts a slice of the
alignment problem from an unspecifiable values question into a **measurable
procedural one** (does this hop keep the receiver able to decide?), and LISM gives
that measurement an empirically grounded law, a self-calibrating sensor, and an
anti-over-claiming discipline. Not the whole of alignment — but a concrete,
auditable brick in the wall, shipping today.

*Layer note: Sections 1–6 are Layer-1 engineering claims tied to the shipped stack
and its tests. Any interpretive framing of "agency" as an ultimate value is Layer-3
and not adjudicated here.*
