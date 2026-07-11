# IHCEI / NERE on real GitHub text — a real-world test that failed usefully

*How the shipped engine actually behaves on **real, external, human-authored text it
was never tuned on** — 217 benign items (this repo's PR prose + 159 live PyPI package
summaries), 6 legitimately-urgent honest bug reports, and 14 fresh coercive OSS
comments written for this test (not the tuning corpus). Reproduce:
`python3 nere_experiment/ihcei_realworld_test.py`. Baseline: the stack's own suite is
60/60 — but that is a spec test; this one could fail, and it did.*

---

## Why the 60/60 suite is not enough

`test_ihcei_nere_v3.py` passes 60/60, but its "benign" examples are **loaded with
explicit agency-preserving language** ("Options available: A (72%) or B (24%)…
decision authority remains with you"). Real developers don't write like that. So the
spec suite verifies NERE passes text *designed* to pass — construction-confirming. The
only way to know how it behaves in the wild is to feed it the wild.

## The results (real shipped NERE, fast mode, 5.3 ms/audit, $0.00)

| Axis (each can fail) | Result | Verdict |
|---|---|:--:|
| **Recall on fresh coercion** (14 held-out OSS comments, not the tuning set) | flagged **92.9%** (BLOCK/WARN); missed 1 groupthink phrasing | **PASS** — the signal generalizes |
| **HOLD false-positive on benign** (the *consequential* quarantine action) | **0.5%** (1/217) | **PASS (safe)** — the agency contract holds |
| **Advisory over-firing on benign** (NERE WARN / middleware notice) | NERE WARN **90.8%**; middleware `DELIVER_WITH_NOTICE` **96.8%** | **FAIL — alarm fatigue** |
| **Legitimate urgency** ("critical security bug… patch attached") | flagged **66.7%** | **CONCERN** — keys on urgency words |

Middleware action mix on 217 real benign items:
`DELIVER_WITH_NOTICE: 210, DELIVER: 6, HOLD: 1`.

## What actually happened (the honest read)

Two very different things, and conflating them would be the mistake:

1. **The dangerous action is safe.** HOLD (quarantine) requires a BLOCK-band posterior,
   and it fired on **0.5%** of real benign text. So IHCEI's core contract — *never
   wrongly block legitimate communication, keep agency with the human* — **holds up in
   the real world.** Nothing legitimate got quarantined, and genuine coercion was
   caught 93% of the time. That is the part worth deploying.

2. **The advisory layer is unusable as-shipped.** Neutral technical text —
   `"gh-issues batch summary mode"`, `"Screen-scraping library"` — contains neither
   coercive nor agency-preserving markers, so it lands at NERE's ~**0.48** no-evidence
   prior, which sits just inside the WARN band (≥0.40). Result: **97% of normal PRs
   would get a notice.** On a live GitHub repo that is textbook **alarm fatigue** —
   maintainers would mute it within a day. It even flags honest, evidence-based
   urgency ("critical security bug, patch attached") because it partly keys on surface
   words like *critical/immediately*.

**This is the gap a spec suite structurally cannot see, and it only shows up against
real text.** It is also fixable, and the fix is the framework's own machinery:

- **Raise the WARN threshold** (or lower NERE's neutral prior) so no-evidence text
  passes instead of warning. The BLOCK band is already well-placed (recall 93%,
  HOLD-FP 0.5%); only the advisory boundary is miscalibrated.
- **Seed the channel prior** on real benign telemetry before going live — exactly the
  `/v3/channel/update` step in the deployment guide. The `oss_default` prior is
  deliberately weak; real GitHub telemetry should dominate it fast and push neutral
  text to DELIVER.

## Bottom line

On real GitHub-style text, IHCEI's **safety contract passes** (0.5% wrongful HOLD,
93% coercion recall) but its **advisory calibration fails** (97% benign notice rate) —
a deployability blocker that the 60/60 suite masks. Reported as-is: the quarantine
engine is real-world-ready; the notice engine needs recalibration (raise WARN
threshold, seed the channel) before a live GitHub pilot. That is a finding, not a
green light — which is the point of testing against data that never knew the theory.

## Reproduce
```
python3 nere_experiment/ihcei_realworld_test.py
# corpora: realworld_corpus_github.json (real PR prose), realworld_corpus_pypi.json
# (159 live PyPI summaries); held-out coercive + urgent-honest sets are in the script.
```
