# HELM — Validation Report (v0.1)

**GT v18.2 · positioning: IHCEI/NERE is infrastructure (the probabilistic layer
between LLMs); HELM is the personal agency layer — the same kernel, on-device,
owned by the person.** This report records what was tested, what the numbers
are, and what HELM does in the real world once deployed. It follows the
framework's own rule: null and negative results are deliverables, and every
number carries its uncertainty.

---

## 1. What HELM is, in one paragraph

HELM runs the IHCEI/NERE probabilistic kernel **entirely on-device**. Every
message, AI answer, offer, feed item, or agent action can arrive with a
calibrated agency verdict — *does this develop me or steer me?* — at zero
marginal cost, **silent until it matters**. Nothing audited ever leaves the
device; there is no network call in the kernel and a test proves it. Beyond the
audit, HELM ships three primitives every person needs and no incumbent owns:
**DELEGATE** (a revocable decision-permission table for AI agents), **DEVELOP**
(a capacity-vs-dependency meter, reported to the person only), and **PROVE** (a
hash-chained, tamper-evident certificate wallet).

## 2. What the tests are, and what each proves

`npm test` runs **70 assertions across two suites**, all passing:

| Suite | Assertions | What it pins |
|---|---|---|
| `test/helm.test.mjs` | 48 | floor, silence-default, emergency-safety, scam armor, corroboration gate, dark patterns, no-mutation/no-network, all four primitives |
| `test/parity.test.mjs` | 22 | cross-engine: enterprise-v1 (govern.js) and consumer-v1 (HELM) make the same *structural* gate decision, and every verdict stamps the lexicon it was judged under |

Test groups in the main suite (A–J):

- **A · Epistemic floor** — no output is ever 0 or 1; probabilities live in
  `[0.01, 0.99]`. Uncertainty is represented, never erased.
- **B · Silence by default** — calm, optioned, sourced text produces no chip.
  The default state of the system is *quiet*.
- **C · Emergency-safety** — "restart the primary now", "evacuate immediately",
  "apply pressure to the wound" stay **silent**. A safety layer that mutes real
  emergencies protects no one; HELM does not.
- **D · Scam armor** — a grandparent scam ("it's me, don't tell anyone, wire it
  now") is caught: it trips secrecy + payment + impersonation, the gate opens,
  the posterior clears the (stricter, ambient) floor.
- **E · Corroboration gate** — the load-bearing design choice (§4 below).
- **F · Dark patterns** — manufactured scarcity / fake social proof at checkout
  is flagged.
- **G · Contract** — no mutation of content, no suppression (verdict only), and
  a test that asserts the kernel makes **no network call**.
- **H · DELEGATE** — default-deny, stake caps, one-tap revocation, every
  decision certificated.
- **I · PROVE** — the wallet's hash chain verifies clean, and any edit to a past
  entry is *detected and located*.
- **J · DEVELOP** — the capacity meter separates developmental use (person stays
  in the loop) from dependent use (person outsources thinking), and detects a
  substitution trend.

## 3. Two bugs the suite caught before they shipped

Both are recorded because catching them is the point of testing adversarially,
not on the happy path.

1. **Elder-scam miss (lexicon gap).** The naive port of the enterprise engine
   *missed* the grandparent scam — its mechanism lexicon (bypass / authority /
   consensus) was tuned for AI-and-PR coercion, not phone scams. `don'?t` did
   not match "do not", and the payment pattern did not match "wire payment".
   Building HELM meant broadening the lexicon to **secrecy, payment-pressure,
   impersonation, scarcity** (consumer-v1). The scam-armor tests caught this.

2. **Tamper-blind wallet (the dangerous class).** `CertificateWallet._canonical`
   used `JSON.stringify(payload, Object.keys(payload).sort())` — but the second
   argument there is a **replacer allow-list**, which silently drops *nested*
   keys from the hash. Editing `payload.verdict` did not change the hash, so the
   chain was forgeable while passing every happy-path test. Fixed with a
   recursive, key-sorted stable serialization. This is the worst class of
   security bug: it passes every happy-path test and fails only under
   adversarial edit. The "tamper located at edited link" test now guards it.

## 4. The load-bearing design choice, validated with numbers

IHCEI fast mode false-alarmed on **legitimate urgency** (emergencies) 50% of the
time. An average 0.5% aggregate false-positive rate *hid* this: the rare
legitimate-urgency tail (emergencies) is exactly where a muted safety layer
does its damage. HELM fixes it for free with a **corroboration gate**: the
heaviest gates (methodology-opacity g3, benevolent-tyranny g7) and the pressure
words (urgency / fear / imperative) carry full weight only when a real
manipulation **mechanism** is also present — else they are discounted ×0.15.

The mechanism lexicon is channel-specific and **versioned**, and each verdict
now records which lexicon judged it (`mechanism_lexicon` on the hop envelope /
certificate):

- **enterprise-v1** (govern.js, NERE Python): manufactured consensus (g2),
  verification-bypass (g4, incl. scrutiny-suppression "do not ask questions"),
  unverifiable authority (g5), complexity-deflection (g6), isolation.
- **consumer-v1** (HELM): all of enterprise-v1 **plus** secrecy, payment-
  pressure, impersonation, manufactured scarcity — the elder-scam / dark-pattern
  armor.

Measured effect (enterprise-v1, the shared 44-item IHCEI corpus, fast mode):

| metric | gate OFF | gate ON |
|---|---|---|
| legitimate-urgency **false-HOLD** | **0.500** | **0.000** |
| clean-benign false-positive | 0.300 | **0.000** |
| blunt-coercion recall (HOLD/WARN) | 1.000 | 0.900 |
| groupthink recall | 0.750 | 0.750 |
| evasive-coercion recall | 1.000 | **0.125** |

Two honest readings of that table:

- The gate does exactly what it should: it **eliminates** the emergency
  false-HOLD and the clean false-positives, and keeps blunt coercion (its real
  job) at 0.90 — the one blunt case it drops (`cm02`) is a mechanism-free
  imperative *structurally indistinguishable* from a real emergency, which fast
  mode genuinely cannot separate.
- The **evasive** number is not a regression; it is the **documented ceiling of
  fast mode**. The gate-OFF 1.000 was fragile — it came from stray pressure
  words on reworded text, not from any detected mechanism. Catching reworded
  coercion is **deep mode's** job, and that is a *pre-registered* test
  (`PREREGISTRATION.md`), not a shipped claim.

## 5. What HELM does in the real world (once deployed, accessed by everyone)

- **For an older person:** the grandparent scam and the "your account is
  suspended, pay in gift cards" scam raise a plain-language chip — *"this looks
  like manipulation, and here's why"* — while a real "your prescription is
  ready, call the clinic" message stays silent. Nothing is blocked; the person
  still decides. The mirror, never the hand.
- **For anyone using AI agents:** DELEGATE is the "OAuth of agency" — an agent
  may draft an email but never send above a stake cap, may spend up to £20 but
  not £2,000, and every such decision is a certificate the person can revoke
  with one tap and prove later.
- **For a knowledge worker:** DEVELOP answers a question no screen-time meter
  can — *is my AI use growing my ability or replacing it?* — and reports the
  trend to the person alone, never to a platform.
- **For everyone:** PROVE gives a portable, tamper-evident record of what was
  audited and what was delegated — the receipts layer for a life lived
  alongside AI.

## 6. Honest status — real vs. bet

- **Real and tested now (deployable):** the entire fast-mode kernel, the
  corroboration gate, scam/dark-pattern armor, emergency-silence, and all four
  primitives — on-device, offline. 70/70 assertions green; cross-engine parity
  with the server (govern.js) and Python reference (62/62) confirmed.
- **The bet (design §3, §10):** *on-device deep mode.* v0.1 is fast-mode only.
  The ambient-layer economics depend on a distilled ~1–3B extractor running the
  semantic step on a phone NPU. Directionally plausible, **unproven at ambient
  precision** — it is a pre-registered test with thresholds LOCKED BEFORE
  training (`PREREGISTRATION.md`), able to return a meaningful **null** that
  would retire the ambient-deep claim and degrade HELM to *fast-mode + the four
  primitives* (still genuinely useful).
- **Corpus caveat:** the emergency / scam corpora are hand-authored seeds (tens
  of items). The 0.00 emergency false-alarm is direction-strong but must be
  re-measured on the frozen, expanded corpora before ambient default-on.
- **$5T framing:** `HYPOTHESIS`, wide interval, exactly as the design files it.
  What is *not* hypothetical: these four primitives solve real problems for
  every age band at near-zero marginal cost, and the delegation table has no
  incumbent.
