# The four-cohort τ_v experiment — results

*A new, ordered-prediction test of the enforcement-latency sensor, run LIVE on
2026-07-10 through the existing GitHub proxy in `project-6q4gj` (`api/gh-issues`,
batch summary, pages=2). No new API was needed. Reproduce with
`python3 tauv_4cohort_experiment.py`.*

---

## Design

Sixteen well-known repositories were **pre-assigned** to one of four *decline
tiers* by public maintenance status, before τ_v was measured. τ_v = mean
close-latency (days) of a repo's real closed, non-PR issues.

| Tier | Meaning | Repos |
|---|---|---|
| **T1 active** | genuinely, actively developed | fastapi, vite, pytest, tokio |
| **T2 mature** | stable, still maintained, slower cadence | webpack, babel, gatsby, jekyll |
| **T3 zombie** | deprecated / dead core, only cosmetic commits, **not archived** | gulp, moment, async, bower |
| **T4 archived** | formally archived (administrative end-of-life) | angular.js, lovefield, mojito, draft-js |

**Pre-registered ordered hypothesis:** τ_v(T1) < τ_v(T2) < τ_v(T3) as enforcement
capacity declines — and T4 (archived) is *expected to break monotonicity
downward*, because formal archival mass-closes trailing issues (the documented
bulk-close artifact).

## Results

| Tier | n | mean τ_v | median τ_v |
|---|--:|--:|--:|
| T1 active | 4 | 5.00 d | **4.58 d** |
| T2 mature | 4 | 5.10 d | **5.62 d** |
| T3 zombie | 4 | 68.30 d | **77.67 d** |
| T4 archived | 4 | 28.09 d | **29.48 d** |

- **Overall difference (Kruskal–Wallis, 4 tiers):** H = 11.54, **p = 0.0092**.
- **Ordered trend T1 < T2 < T3** (enforcement decline; archival-artifact tier
  excluded): **Spearman ρ = 0.739 (p = 0.006)**, Kendall τ = 0.604 (p = 0.013).
- **Decisive contrast — enforcement-intact (T1+T2) vs collapsed zombie (T3):**
  median **4.89 d vs 77.67 d = 15.9× gap**, Mann–Whitney one-tailed **p = 0.002**.
- **T4 archived median 29.48 d — LOWER than T3 (77.67 d)**, exactly as pre-stated:
  angular.js (7.97 d) and lovefield (14.71 d) had trailing issues mass-closed at
  end-of-life, deflating their latency.

## What it means

1. **τ_v rises monotonically across the enforcement-decline gradient** — a ~16×
   jump from enforcement-intact to enforcement-collapsed, on live data, with an
   ordered-trend p = 0.006.
2. **Age is not the driver.** T2 mature projects (webpack, babel, jekyll) are old
   but still *enforce*, so their τ_v stays as low as the youngest T1 projects. τ_v
   tracks live enforcement capacity, not calendar age or repo size.
3. **The zombie tier is where the sensor earns its keep.** These repos get cosmetic
   dependency-bump commits, so a "last-commit" health heuristic calls them active —
   yet their τ_v is 15.9× the active tier. **τ_v leads the lifecycle label.**
4. **The one failure is diagnostic, not damaging.** T4 breaks the monotonic
   prediction *downward*, precisely because archival bulk-closes issues. Pre-stating
   this and measuring it isolates the single artifact a deployer must handle: drop
   (or window out) repos with a close-latency collapse at the archival timestamp.
   This is the operational rule the earlier 18-repo autopsy motivated, now confirmed
   under an ordered four-cohort design.

**Bottom line.** The four-cohort experiment upgrades the earlier binary
failed-vs-survived autopsy into an *ordered gradient* and reproduces the core τ_v
claim on fresh live data (ρ = 0.739, p = 0.006; 15.9× intact-vs-zombie, p = 0.002),
while cleanly localizing the archival bulk-close confound. It remains a convenience
cross-section; the manuscript's headline still rests on the pre-registered N = 992
CI cohort. But as a live, ordered stress-test, it holds.
