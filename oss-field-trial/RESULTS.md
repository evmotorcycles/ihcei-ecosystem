# OSS Field Trial — IHCEI/HELM on Real Open-Source Projects

**GT v18.2 · 2026-07-12 · reproduce: `node oss-field-trial/field_trial.mjs`**

The question this trial answers: as AI moves from recipe-checking into serious
projects, what do IHCEI (the enterprise gateway) and HELM (the on-device layer)
actually deliver on **real open-source project communication** — and does the
economics close? Every benign input is real and fetched live (provenance in the
fixtures); threats are injected and labeled; the health telemetry comes from the
deployed project-6q4gj GitHub API.

## 1 · Benefit: silence on real OSS traffic (n = 281 live registry texts)

Real package descriptions from npm and PyPI — how maintainers actually describe
their projects, the ambient traffic an auditor deployed on OSS sees all day:

| metric | gate OFF | gate ON |
|---|---|---|
| advisory notice rate | **87.9%** | **0.0%** |
| HOLD (quarantine) rate | 0.0% | 0.0% |
| ambiguous band p∈[0.30, 0.70] | **88.6%** | **0.0%** |
| HELM chips (on-device) | — | **0.0%** |
| mean audit latency | — | 1.47 ms |

The pre-gate row **independently reproduces the "~89% ambiguity trap" on fresh
data** (88.6% vs the 89% measured on the earlier communication-graph test).
The corroboration gate collapses it to zero on this traffic — technical prose
has pressure-shaped words ("must", "required", "critical") but no manipulation
mechanism, so the gate discounts it to silence.

## 2 · Benefit: real urgent maintainer warnings stay silent (7/7)

Real deprecation messages shipped in npm package metadata — apollo-server,
request, csurf, protractor, node-sass, tslint, left-pad. These are *genuine
urgent notices* ("end-of-life, stop using this, migrate now"): the
legitimate-urgency tail where a naive safety layer false-alarms. **Both engines
stay silent on all 7.** (Small n — the powered version of this claim is the
locked Stage-1 emergency corpus, n ≥ 400.)

## 3 · Benefit: threats injected into the same channel are caught

| threat | IHCEI (enterprise-v1) | HELM (consumer-v1) |
|---|---|---|
| supply-chain PR pressure ("core team agreed offline, skip CI, don't raise it") | WARN | WARN |
| npm token phish ("security team — don't tell anyone, send the token") | WARN | **BLOCK** |
| review bypass ("no time to review, too complex for you to verify") | WARN | WARN |
| manufactured consensus ("everyone agrees the dependency is safe") | **BLOCK** | **BLOCK** |
| typosquat ransom (gift-card fee) | PASS *(consumer mechanism — by design)* | **BLOCK** |
| fake security advisory ("authorities confirm, bypass your lockfile") | **BLOCK** | **BLOCK** |

**HELM recall 6/6; IHCEI 5/5 on enterprise-mechanism threats.** Silence in §1–2
costs nothing in protection: the same engines that ignore 281 real texts and 7
real urgent warnings catch every injected exploit, because the gate keys on
*mechanism*, not tone.

## 4 · Benefit: live project-health telemetry (deployed GitHub API)

Eight real repos, τ_v (issue-enforcement latency) computed server-side by the
deployed `gh-issues` endpoint from their actual issue timelines:

| repo | τ_v | true status |
|---|---|---|
| sveltejs/svelte | **2.61d** | active |
| expressjs/express | 2.80d | active |
| vitejs/vite | 5.43d | active |
| fastify/fastify | 9.88d | active |
| moment/moment | 88.46d | maintenance-mode |
| lodash/lodash | 114.41d | maintenance-mode (recent pushes!) |
| bower/bower | 121.67d | deprecated |
| request/request | **251.29d** | deprecated/unmaintained |

By **true maintenance status** the separation is clean: worst active 9.88d <
best non-active 88.46d (**9.0×**; svelte-vs-request is 96×). By a **naive
last-push label** the separation *breaks* — lodash pushes commits while its
issue queue runs at 114d — which independently replicates the documented
zombie-contamination failure of last-push health labels. τ_v measures
*enforcement*, and that is exactly what a serious project needs to know about
its dependencies. (n = 8 is illustrative telemetry; the powered claim is the
N = 992 pre-registered LISM cohort.)

## 5 · Financial viability — computed from the measured rates

Using the measured deep-mode cost of $0.003/message and the escalation rates
measured in §1 (a gateway must deep-check whatever fast mode cannot clear
confidently: the ambiguous band plus notices):

| architecture | cost per 1M messages | escalation |
|---|---|---|
| cloud deep-mode on everything | **$3,000** | 100% |
| gateway, fast + escalate, **pre-gate** | **$3,000** | ~100% (88.6% ambiguous + notices) |
| gateway, fast + escalate, **gate ON** | **~$0** | **0.0% measured** on this traffic |
| HELM on-device | **$0 marginal** | local by construction |

Three conclusions, stated with their limits:

1. **The gate, not deep mode, resolves the ambiguity trap on benign traffic.**
   Pre-gate, the 0.48-band forced ~100% escalation and the consumer economics
   were dead (the retired tollbooth model). Post-gate, *zero* of this real
   traffic needs a paid call. The $0-marginal free tier is genuinely free to
   serve **on this traffic profile**.
2. **Deep mode's cost scales with threat suspicion, not with volume.** Registry
   prose is calm; adversarial *conversations* (reworded coercion — the evasive
   class fast mode catches at only 0.125) are where deep mode earns its
   $0.003. That is a quality tail, not a volume tax — and its on-device
   replacement is exactly what the locked Stage-1 spec will test.
3. **The enterprise license prices against the counterfactual.** A $30k–$80k/yr
   self-hosted gateway breaks even against per-message cloud deep at 10M–26.7M
   deep checks/yr; pre-gate that was any org with ~10M messages/yr, post-gate
   the license buys *attestation* (signed SHA-256 certificates, lexicon-stamped
   hop envelopes, calibrated priors) rather than raw compute — which is the
   regulated-vertical value proposition anyway. The alarm-fatigue term is the
   hidden kill-switch: a layer that notices 87.9% of real traffic gets muted,
   and a muted layer's protection value is $0 regardless of price.

## Honest limits

- Registry descriptions are calmer than issue threads and incident channels;
  the 0.0% escalation number is a floor for prose-like traffic, not a universal
  constant. The locked pre-registration (emergency n ≥ 400, evasive n ≥ 300) is
  what turns these directional rates into powered claims.
- n = 7 real urgent warnings and n = 8 repos are live spot-checks that agree
  with the earlier powered results (emergency false-HOLD 0.50 → 0.00 on the
  44-item corpus; N = 992 τ_v study at p ≈ 10⁻³¹); they do not replace them.
- Threat recall here is on *blunt* injected threats; reworded (evasive)
  coercion remains fast mode's documented ceiling and deep mode's job.
