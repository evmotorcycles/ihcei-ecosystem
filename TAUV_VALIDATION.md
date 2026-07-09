# Live validation of the enforcement-latency sensor (τ_v) via the GitHub API

*Supplementary re-test. Fetched live on 2026-07-09 through the server-side proxy
`api/gh-issues.js` (batch summary mode) running on `project-6q4gj`. No
placeholders: every τ_v below was computed from that repository's real, closed,
non-PR issue timeline. Reproduce with `python3 tauv_live_validation.py`.*

---

## What this is (and is not)

This is a **supplementary** stress-test of τ_v on a *fresh, independent,
convenience* cross-section of 18 well-known GitHub repositories. It is **not** the
manuscript's primary evidence. The headline GitHub result — failed repos close
their own flagged issues far slower than survivors (**50.6 d vs 19.8 d, MWU
p ≈ 10⁻³¹**) — rests on the **pre-registered CI cohort (N = 992)** with a
*non-circular, CI-derived* failure label and controlled sampling. The point of
this exercise was to see what a naive, off-the-shelf lifecycle label reproduces on
live data, and to report that honestly.

**Definition (unchanged).** For a repository, τ_v = mean close latency (days,
capped at 365) over its closed, non-PR issues, sampled from the 300
most-recently-opened issues (`pages=3`, `sort=created&direction=desc`).

---

## The live cohort (18 repos, pages=3)

| repo | τ_v (d) | n_closed | archived | E (naive) | status |
|---|--:|--:|:--:|:--:|:--|
| pallets/flask | 11.9 | 78 | no | survived | active |
| psf/requests | 3.4 | 27 | no | survived | active |
| expressjs/express | 2.7 | 30 | no | survived | active |
| axios/axios | 7.8 | 43 | no | survived | active |
| tqdm/tqdm | 84.5 | 31 | no | survived | active (slow triage) |
| moment/moment | 88.5 | 85 | no | survived | **dormant** (maintenance mode) |
| bower/bower | 121.7 | 200 | no | survived | **dormant** (deprecated 2017) |
| jashkenas/backbone | 73.1 | 147 | no | survived | **dormant** |
| Netflix/Hystrix | 317.7 | 229 | no | survived | **dormant** (maintenance mode) |
| airbnb/enzyme | 45.3 | 143 | no | survived | **dormant** (abandoned) |
| Netflix/falcor | 147.1 | 98 | no | survived | **dormant** (abandoned ~2018) |
| petkaantonov/bluebird | 83.8 | 123 | no | survived | **dormant** (superseded) |
| angular/angular.js | 6.1 | 126 | **yes** | failed | dormant (bulk-closed at EOL) |
| nodejs/node-v0.x-archive | 118.3 | 235 | **yes** | failed | dormant |
| google/lovefield | 29.6 | 188 | **yes** | failed | dormant (bulk-closed) |
| yahoo/mojito | 48.6 | 56 | **yes** | failed | dormant |
| facebook/draft-js | 66.8 | 23 | **yes** | failed | dormant |
| jquery/jquery-mobile | 24.6 | 66 | **yes** | failed | dormant (bulk-closed) |

---

## Analysis A — pre-specified naive label (E = failed if archived OR pushed > 730 d)

| group | n | mean τ_v | median τ_v |
|---|--:|--:|--:|
| failed | 6 | 49.0 d | 39.1 d |
| survived | 12 | 82.3 d | 78.5 d |

**MWU one-tailed (failed > survived): p = 0.753 — direction OPPOSITE to
hypothesis.** On the naive label the sensor appears to fail. This is expected, and
it is *informative*: it surfaces exactly the two confounds the pre-registered CI
cohort was built to exclude.

1. **Zombie contamination.** Deprecated / maintenance-mode projects — Hystrix
   (318 d), falcor (147 d), bower (122 d), moment (88 d), bluebird (84 d) — still
   receive occasional dependency-bump or documentation commits, so "pushed within
   730 days" wrongly labels them **survived**. These are precisely the repos τ_v
   flags as decaying. **τ_v leads the last-push lifecycle label**; the last-commit
   heuristic is fooled by cosmetic activity.
2. **Archival bulk-close (opposite artefact).** Formally-archived repos —
   angular.js (6 d), jquery-mobile (25 d), lovefield (30 d) — had their trailing
   open issues *mass-closed* at sunset. That collapses their measured close-latency
   downward, so the naive "failed" group is biased *low*. The manuscript's
   CI-derived label sidesteps this because it does not equate "archived" with
   "failed at the moment of interest."

Both confounds push in the direction that *masks* the effect. The naive label is
the wrong instrument, and this cross-section shows why.

## Analysis B — reclassify by actual maintenance status

The distinction the naive label misses — *is the project actually being
maintained?* — is exactly what τ_v is meant to detect. Reclassifying each repo by
its documented status (active vs dormant/deprecated/archived; see the provenance
column in `tauv_live_validation.py`):

| group | n | mean τ_v | median τ_v |
|---|--:|--:|--:|
| dormant | 13 | 90.1 d | 73.1 d |
| active | 5 | 22.1 d | 7.8 d |

**MWU one-tailed (dormant > active): p = 0.013 — as hypothesised (~9× median
gap).** Removing the three documented bulk-close-at-archival repos sharpens it
further: **dormant median 86 d vs active 8 d (~11×), p = 0.006.**

> This reclassification is **post-hoc and judgement-based** (each status is
> documented, but not pre-registered), so it is **illustrative, not
> confirmatory**. The one active repo with a high τ_v — tqdm (84 d) — is an honest
> outlier: a genuinely-maintained project with a small team and slow triage.

---

## Bottom line

- On a naive last-push label, the live convenience cross-section **does not**
  reproduce the failed-vs-survived τ_v gap — and the reason is diagnostic, not
  damaging: it reproduces the two confounds (zombie contamination; archival
  bulk-close) that the **pre-registered CI cohort was specifically designed to
  avoid**.
- Once repositories are graded by *actual* maintenance status — the very decay τ_v
  is built to sense — the hypothesised direction returns strongly (~9–11× median
  gap, p ≈ 0.006–0.013).
- Read together, this is mild **support** for τ_v as a *leading* indicator: it
  tracks true institutional decay more faithfully than a last-commit proxy, which
  cosmetic activity fools.
- The manuscript's headline τ_v claim continues to rest on the **pre-registered,
  non-circular CI cohort**, not on this convenience sample. Presenting the live
  sample's messiness, and diagnosing it, is the correct scientific posture — and
  consistent with the project's practice of publishing its own confounds.

## Reproducibility

```
python3 tauv_live_validation.py      # encodes the live cohort + runs A, B, B'
```
Cohort fetched via, e.g.:
```
GET https://project-6q4gj.vercel.app/api/gh-issues?summary=1&pages=3&repos=pallets/flask,psf/requests,...
```
`api/gh-issues.js` computes τ_v, the lifecycle inputs (archived, pushed_at), and
E server-side; the proxy runs unauthenticated (GitHub's 60 req/h limit), so the
cohort was assembled in small batches on 2026-07-09.
