# Final Validation — the full Novora stack, one matrix

**GT v18.2 · 2026-07-13 · every row re-run for this document; live rows verified
against production project-6q4gj the same morning.**

This consolidates the finalized testing across the four layers — the NERE
kernel, the IHCEI gateway, HELM and its apps, and the live deployment — plus the
locked instruments that govern what may be claimed next.

## The matrix

| Layer | Suite / check | Result |
|---|---|---|
| **NERE kernel (Python)** | `ihcei_v3/test_ihcei_nere_v3.py` — floor, bands, gates, corroboration gate both-sides, learning hooks | **62/62** |
| | `ihcei_v3/test_deep_seam.py` — fast/deep extractor seam, identical posterior math | **11/11** |
| | `tests/test_tau_v_monitor.py` — τ_v hazard monitor | **13/13** |
| **IHCEI gateway (JS)** | corpus validation (gate ON): emergency false-HOLD **0.000**, clean FP **0.000**, blunt recall 0.900 | pass |
| | handler smoke: SHA-256 certificate reproduces from canonical payload; tampering any field changes it; `mechanism_lexicon: enterprise-v1` stamped | pass |
| **HELM (JS)** | `test/helm.test.mjs` — floor, silence-default, emergency-safety, scam armor, dark patterns, no-network, 4 primitives | **48/48** |
| | `test/parity.test.mjs` — cross-engine gate + lexicon-stamp parity | **22/22** |
| | `test/prereg.lock.test.mjs` — Stage-1 spec hash matches manifest (tamper turns CI red) | **7/7** |
| | `test/contribution.test.mjs` — real project traffic, threats, live τ_v, governed automation | **23/23** |
| **Novora apps** | extension kernel byte-identical to `src/helm-core.mjs`; `popup.js` parses; MV3 manifest valid; demo page imports the same kernel | in sync |
| **Field trials** | `oss-field-trial/field_trial.mjs` — 281 live registry texts: notices 87.9%→**0.0%**, deprecations silent 7/7, threats 6/6, τ_v cohort 9–96× | pass |
| | `oss-field-trial/issues_followup.mjs` — 306 real README paragraphs: gate-ON floor **0.0%**; labeled Brier OFF 0.205 → ON **0.074**, HELM 0.082 | pass |
| | `oss-field-trial/tier2_calibration_test.py` — federation null: LLRs ×4–7, evasive recall **0.125 → 0.125**, safety held | pass (null confirmed) |
| **Locked instruments** | `prereg/stage1_spec.json` — canonical SHA-256 `0f047b96…` matches `MANIFEST.sha256` | locked |
| | `prereg/acceptance_harness.mjs` — refuses tampered spec; dry run returns **Claim A = NULL** under the fast stand-in (the null path works) | verified |
| **Live production (project-6q4gj, 2026-07-13)** | `GET /api/calibrate?mode=fast` — all 12 legitimate emergencies **PASS** in production, values matching local to 4 decimals | verified live |
| | `GET /api/gh-proxy?op=status` — real GitHub Actions telemetry (D_gap sensor run: completed/success) | verified live |
| | `GET /api/gh-issues?…&summary=1` — live τ_v: express **2.72d** vs request **251.29d** (92×) | verified live |

**Totals: 100 JS assertions + 86 Python assertions + 2 field trials + 1
pre-registered-instrument dry run + 3 live production endpoints — all green.**

## What is closed vs. what is open

**Closed (tested, shipped, live):** the probabilistic kernel with the epistemic
floor; the corroboration gate in all three engines with versioned, stamped
mechanism lexicons; SHA-256 tamper-evident certificates end-to-end (gateway
responses and the HELM wallet); the four HELM primitives on-device with zero
network calls; the alarm-fatigue result on real traffic; the τ_v live
instrument; the CI-enforced pre-registration lock and its grading harness.

**Open (priced in advance, not claimed):** on-device deep mode. Two independent
runs now bound it — fast mode catches 0.125 of evasive coercion, and federated
LLR calibration moves that by exactly zero — so the 1–3B distillation bet is
confirmed **load-bearing** for the evasive tail, and the only path to claiming
it is the one-shot sealed run against `stage1_spec.json`. The three powered
corpora (evasive ≥ 300, emergency ≥ 400 × four strata, consumer-scam ≥ 300)
remain to be authored and frozen into the manifest.
