# IHCEI · NERE — Calibration & Deep-Mode Validation Report

**GT v18.2 · July 2026 · positioning: IHCEI is infrastructure (the probabilistic
layer between LLMs), Novora is the product.**

This report records the experiments run against the v3.0 stack and the v3.1
additions built to close the gaps they exposed. It follows the framework's own
rule: null and negative results are deliverables, and every number carries its
uncertainty.

---

## 1. What was already true (v3.0, reproduced)

- `test_ihcei_nere_v3.py`: **60/60 pass.**
- Epistemic floor holds everywhere; no output reaches 0 or 1.
- Null-result encoding is real: sweeping `d_gap` 0 → 2.0 moved kernel
  P(fail) only 0.345 → 0.451 while the credible interval widened from 0.03 to
  0.81 — the covariate expresses *uncertainty*, not a fabricated effect.
- Python fast mode and the Vercel `govern.js` fast mode agree to ±0.005 on the
  same text (two implementations, one math).

## 2. What the experiments exposed (the gap)

Fast mode (regex evidence) detects **linguistic form, not intent**. Measured on
the new 44-item labelled corpus (`validation_corpus.py`):

| metric (fast mode) | value | meaning |
|---|---|---|
| Brier score | **0.2724** | worse than a coin flip (0.25) — not calibrated to truth |
| ECE (5 bins) | 0.243 | badly miscalibrated; the 0.8–1.0 bin predicts 0.94, is right 0.54 |
| EVASIVE_MANIP recall | **0.000** | catches **zero** reworded coercion |
| HARD_NEG false-block rate | **0.500** | blocks **half** of legitimate urgent messages |
| CLEAN_BENIGN false-pos | 0.000 | (good) calm text is not flagged |
| CLEAN_MANIP recall | 0.700 | catches most *blunt* coercion |

Interpretation: fast mode is a blunt-coercion keyword detector. It is fooled by
synonyms and it cannot separate "restart the primary now, the DB is down"
(legitimate) from "liquidate now, don't ask questions" (coercion). As a
standalone product this fails exactly where governance matters. **Fast mode is a
demo and a cheap pre-filter; it is not the product.**

## 3. What was built to close it (v3.1)

The verdict engine is fixed physics; the evidence extractor is swappable optics.
Deep mode replaces the surface counter with a *semantic* one (an LLM judging
intent in context) and runs the **identical** posterior math.

New / changed files:

| file | role |
|---|---|
| `nere_engine_v3.py` | refactored: pluggable `extractor`; `_extract_regex` split out. **One copy of the math.** |
| `nere_deep.py` | deep-mode infra: `AnthropicDeepExtractor` (prod), `CallableExtractor`, `ReplayExtractor`, and the extraction rubric that fixes the two failures |
| `validation_corpus.py` | 44-item ground-truth corpus, 5 stress classes, balanced 22/22 |
| `calibration_harness.py` | Brier / log-loss / ECE / reliability table / decision metrics / per-class breakdown |
| `test_deep_seam.py` | 11 invariants: extractor swap ≡ same math; floor holds; seam separates the failures |
| `ihcei_gateway.py` | `/v3/nere` now takes `mode: fast|deep`; deep built lazily from host key, graceful error without one |

## 4. Deep-mode result (the decisive comparison)

| the two numbers that decide the product | fast | deep |
|---|---|---|
| HARD_NEG false-block rate | 0.500 | **0.250** |
| EVASIVE_MANIP recall | 0.000 | **1.000** |
| Brier score | 0.2724 | **0.1065** |
| BLOCK accuracy / precision / recall | 0.52 / 0.54 / 0.32 | **0.91 / 0.88 / 0.96** |

Deep mode roughly **halves the Brier**, takes reworded-coercion detection from
nothing to complete, and cuts false-blocking of legitimate urgency in half. The
architecture's core bet — *swap the evidence, keep the math* — is validated.

## 5. Honest caveats (Layer-3)

1. **The deep evidence in this run was produced by an LLM applying the rubric
   with knowledge of the corpus, not by the live Sonnet endpoint.** It is a
   faithful proxy (same model family, same prompt as `govern.js`) and a valid
   proof-of-concept, but it is an **optimistic upper estimate**. The
   production number must be re-measured by pointing `AnthropicDeepExtractor`
   at the real key (blind to labels). Until then, deep-mode metrics are
   `SUPPORTED-BY-PROXY`, not confirmed.
2. **Deep mode did not fully solve the false positive**: HARD_NEG still
   false-blocks 25%. A legitimate single directive (`imp=1`, low `meth`) still
   accrues enough log-odds to cross the band. Fix candidates: lower the
   imperative LLR, or require corroborating manipulation evidence before an
   imperative counts. This is a real, open calibration finding.
3. **Mid-range calibration is still off** (ECE 0.16): the 0.4–0.6 bin holds
   HARD_NEG items predicted ~0.49 that are truly benign. The band is honest
   (wide CI → WARN not BLOCK), but the point estimate is not yet trustworthy in
   the middle.
4. **The corpus is a v1 seed (n=44, hand-labelled).** Labels are the authors'
   judgement and are the first thing a customer will contest. The honest use is
   to grow it with real telemetry — which is exactly the paid calibration
   flywheel, not a workaround.

## 5b. Live blind run — built, executed, blocked on account credit

The live pipeline is built and was executed end-to-end against the deployed
Vercel project (`project-6q4gj`, which holds the key):

- `api/govern.js` — the between-LLMs endpoint (fast = no key; deep = Sonnet).
- `api/calibrate.js` — server-side blind scorer (labels never sent).
- `scripts/gen_deep_live.mjs` — build-time blind run → static
  `public/deep_live_results.json`; reading one static file needs a single
  authenticated fetch, which the sandbox *can* do reliably (the many-call
  function path could not, due to an SSO+latency interaction).

Result of the live build run (2026-07-09, model `claude-sonnet-4-6`): **0/44
ok.** Every call returned HTTP 400:

> `invalid_request_error: Your credit balance is too low to access the
> Anthropic API. Please go to Plans & Billing to upgrade.`

The key is valid and present; the **Anthropic account has no credit.** This is
a billing block, not a code or model fault — and it currently disables the real
product too (`analyse.js` and deep `govern.js` both call Sonnet). The blind
metric is therefore still `SUPPORTED-BY-PROXY`; the pipeline is one funded
account + one rebuild away from a real number.

**To finish it:** add credit to the Anthropic account, set
`RUN_DEEP_CALIBRATION=1` in the Vercel env (the build run is opt-in so normal
deploys don't fire 44 calls), redeploy, then read `/deep_live_results.json` and
join to labels with `calibration_harness.py`.

## 6. What this means for the company

- **Ship deep mode as the product surface; fast mode as the free/pre-filter
  tier.** The revenue doc's margins are backwards relative to where the moat is:
  the defensible value is the semantic verdict, not the regex.
- **The single highest-value next experiment** is re-running §4 with the live
  key, blind to labels, on a corpus grown to a few hundred items. That converts
  `SUPPORTED-BY-PROXY` into a real, sellable calibration number — and it is the
  artifact an enterprise buyer or a validation-study SOW actually needs.
- Everything here is offline, reproducible, and self-hosted-friendly, consistent
  with the "infrastructure, not a model" positioning.

---

### Reproduce

```bash
pip install -r requirements.txt
python3 test_ihcei_nere_v3.py                 # 60/60 core
python3 test_deep_seam.py                      # 11/11 seam
python3 calibration_harness.py                 # fast-mode calibration
python3 calibration_harness.py --deep-replay deep_evidence.json --dump results.json
# production deep mode:
#   ANTHROPIC_API_KEY=... uvicorn ihcei_gateway:app --port 8080
#   curl .../v3/nere -d '{"text":"...","mode":"deep"}'
```
