# Cross-stack integration — the whole agency stack on one real dataset

*Every other suite in this repo tests one engine in isolation. This one takes a
**single body of real open-source data** and runs it through the **entire
pipeline**, asserting the pieces actually compose. If a seam is loose, an
assertion here breaks.*

## The real data

- **35 live packages** pulled from the public **npm + PyPI** registries
  (`fetch_live_corpus.mjs` → `fixtures/live_registry_corpus.json`). Both
  registries are on the sandbox no-proxy allow-list, so this is a genuine live
  fetch — maintainer-written descriptions and README openers, not a replay.
  Re-run the fetcher to refresh; it stamps a new `fetched_at`.
- **22 real GitHub repos** across three τ_v cohorts already captured in this repo
  (`os-integration/`, `novora-helm/`, `oss-field-trial/` fixtures) — real
  issue-close latencies computed server-side from each project's actual issue
  timeline.

## What it runs — `node cross-stack/integration.test.mjs` (26/26)

| stage | engine | on the real data |
|---|---|---|
| A | **LISM** | τ_v + say-do **Dissonance (σ)** on the GitHub cohorts |
| B | **HELM / NERE** | manipulation gate: 0% false alarm on 35 real blurbs; fires on injected scam |
| C | **Echo** | whole corpus ingested as audited, hash-chained records; tamper located; Merkle proof |
| D | **Page Code** | real release/docs diffs pass; self-generated force-push & secret-exfil caught |
| E | **PAGES** | release-notes "podcast" over real README passages; fabricated stat flagged; splice located |
| F | **AIPS** | a real blurb relayed across agency nodes; in-flight mutation & rewritten hop caught |

`node cross-stack/field_report.mjs` prints the same run as a readable report.

## Headline results (real data)

**LISM — Dissonance (σ) reads the network's say-do gap.** σ standardizes, *within
each cohort*, a project's **SAY** (declared vitality = push recency) against its
**DO** (enacted responsiveness = `-log(1+τ_v)`). It is a *coherence* signal, not a
quality score:

| repo | τ_v (days) | push age | σ | read |
|---|---|---|---|---|
| lodash/lodash | 114.4 | 13 d | **+1.47** | **ZOMBIE** — fresh push, but risk rots ~4 months |
| SerenityOS/serenity | 13.7 | 1 d | **+1.97** | **ZOMBIE** — busiest push, slowest closer in its cohort |
| GrapheneOS/os-issue-tracker | 1.18 | 236 d | **−3.31** | **INVERSE-ZOMBIE** — looks stale, fastest responder |
| zephyrproject-rtos/zephyr | 0.16 | 1 d | −1.24 | INVERSE-ZOMBIE — alive *and* responsive |
| request/request | 251.3 | 701 d | −0.06 | coherent — honestly deprecated (say≈do), **not** alarmed |

`lodash` scores ZOMBIE in **both** independent web snapshots — the signal is
stable across two live fetches, not a fluke of one pull.

**The rest of the stack, same data.** HELM stays silent on **0/35** real blurbs
and BLOCKs the same prose the instant a scam (mechanism + pressure) is injected
(`p=0.97`). Echo ingests all 36 records (35 PASS + 1 recorded scam), verifies
clean, and locates an insider's verdict-rewrite at the exact record. Page Code
passes real release diffs and BLOCKs a force-push-to-main / secret-exfil. PAGES
grounds a real README sentence (`p_align 0.98`), drops a fabricated "73% faster"
stat to `0.02`, BLOCKs coercion inside the speech, and locates a splice at
`00:08`. AIPS attests every hop and catches an in-flight payload mutation.

## Honest scope

- **σ is correlational**, calibrated locally (z-scored within a cohort), and is
  *one input to human review* — the same discipline the `tau_v_monitor` package
  enforces. It flags **incoherence between posture and behaviour**, not "bad": an
  honestly-dead repo reads ≈0 on purpose.
- The **Third-Law direction check** (`failed τ_v > survived τ_v`) only returns a
  verdict when a cohort carries a labeled *failed* class with issue signal;
  archived repos here have empty queues (no latency signal), so it reports null
  rather than inventing a comparison. That is recorded, not hidden.
- Fast-mode grounding (PAGES stage E) is lexical overlap + fabricated-number
  detection; genuine semantic paraphrase-vs-distortion is the job of an optional
  pluggable deep grounder (PAGES' `ground` hook). Everything else here is on-device, `$0`, no
  network beyond the one-time registry fetch.
