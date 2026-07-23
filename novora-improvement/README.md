# Novora stack self-assessment → one shipped improvement

**Run it:** `node --test novora-improvement/pages_confidence.test.mjs` · offline · `$0`

The Novora governance stack exists for **agency and security, not speed.** So when we
turned the stack's own tests on itself, the thing worth fixing wasn't throughput — it was
a **calibration/honesty** flaw. This module documents the self-assessment and ships one
concrete, pre-registered improvement.

---

## The finding

Across this session's real-data runs (HF models, HF media, GitHub, the Kaggle scaffold),
**PAGES emitted a precise-looking grounding score (~0.35–0.49) even when the text had no
gradable signal at all.** `screen('pages', 'ok thanks')` returned ~0.35 — indistinguishable
from a genuinely middling but *real* grounding judgement.

For a tool whose job is protecting the reader's agency, that's the wrong failure mode:
- **Agency:** a false-precise number invites the reader to trust a judgement that was never made.
- **Security:** on adversarially-empty or trivial input, false confidence is exactly the gap an attacker wants.

## The fix (shipped in `novora-suite/engine/fastmode.mjs`)

PAGES now computes a **`signal`** count (methodology cues + hollow cues + hard numbers) and a
**`confidence`** ∈ {low, medium, high}. When there is **no** gradable signal it **abstains**:

```
screen('pages', 'ok thanks')
  → { verdict: 'Insufficient Evidence', confidence: 'low',
      insufficient_evidence: true, flags: ['INSUFFICIENT_SIGNAL','ABSTAIN'], score: 0.35 }

screen('pages', 'Phase 3 RCT, N=44,165, 95% CI, pre-registered, DOI cited.')
  → { verdict: 'Solid', confidence: 'high', score: 1.0 }        // unchanged

screen('pages', '…task text-to-speech. license mit. No methodology paper is cited.')
  → { verdict: 'Partially Grounded', confidence: 'medium', score: 0.49 }   // unchanged
```

A numeric score is still returned (so downstream aggregation never sees `NaN`), and **no
score on gradable text changes** — `hf-media`, `hf-cohort`, and the suite distributions are
identical. The abstain fires *only* at zero signal.

## Pre-registered acceptance (all green)

| criterion | result |
|---|---|
| abstains on zero-signal text (`''`, `ok thanks`, emoji) | ✅ Insufficient Evidence / low |
| signal-rich claim stays high-confidence, still outscores hollow | ✅ direction preserved |
| real card/prose keeps its ~0.49 graded band (no abstain) | ✅ unchanged |
| full `reproduce_all.sh` stays green | ✅ |

## Honest backlog (documented in `prereg/improvement_prereg.json`, NOT claimed as done)

- Extend the same `confidence` field to HELM/EI on short metadata.
- Per-domain calibration corpora (PAGES/HELM read prose grounding; tag metadata lacks it).
- Surface Page Code deny-**reasons** in the client so a denial is legible to the user.

These are real, unfixed opportunities — logged as backlog, not results.

## Files

```
novora-improvement/
  prereg/improvement_prereg.json   the finding, the fix, the locked acceptance
  pages_confidence.test.mjs        the proof (abstain + no-regression)
  README.md
```
