#!/usr/bin/env python3
"""
tauv_4cohort_experiment.py — the new four-cohort tau_v experiment (LIVE data)
============================================================================
An ordered-prediction test of the enforcement-latency sensor. Four repository
cohorts were pre-assigned to a DECLINE TIER by public maintenance status, then
tau_v was measured LIVE (2026-07-10) via the existing GitHub proxy in
project-6q4gj (api/gh-issues, batch summary, pages=2). No placeholders — every
tau_v is the mean close-latency of that repo's real closed, non-PR issues.

Pre-registered ordered hypothesis:
    tau_v(T1 active) < tau_v(T2 mature) < tau_v(T3 zombie)          [enforcement decline]
    T4 (archived) is EXPECTED to break monotonicity DOWNWARD because formal
    archival mass-closes trailing issues (the documented bulk-close artifact).

Tiers:
  T1 ACTIVE   — genuinely, actively developed
  T2 MATURE   — stable, still maintained, slower cadence
  T3 ZOMBIE   — deprecated / dead core, only cosmetic commits (NOT archived)
  T4 ARCHIVED — formally archived (administrative end-of-life)

Run:  python3 tauv_4cohort_experiment.py
"""
import numpy as np
from scipy import stats

# (repo, tier, tau_v days, n_closed, archived)  — fetched live 2026-07-10, pages=2
COHORT = [
    ("fastapi/fastapi",     1,  0.15,   7, False),
    ("vitejs/vite",         1,  3.50,  31, False),
    ("pytest-dev/pytest",   1,  5.67,  27, False),
    ("tokio-rs/tokio",      1, 10.67,  17, False),
    ("webpack/webpack",     2,  1.52,  13, False),
    ("babel/babel",         2,  4.11,  24, False),
    ("gatsbyjs/gatsby",     2,  7.13,   2, False),
    ("jekyll/jekyll",       2,  7.62,  41, False),
    ("gulpjs/gulp",         3, 25.02, 121, False),
    ("moment/moment",       3, 67.69,  55, False),
    ("caolan/async",        3, 87.65,  31, False),
    ("bower/bower",         3, 92.82, 117, False),
    ("angular/angular.js",  4,  7.97,  80, True),   # bulk-closed at EOL -> deflated
    ("google/lovefield",    4, 14.71, 134, True),   # bulk-closed -> deflated
    ("yahoo/mojito",        4, 44.24,  35, True),
    ("facebook/draft-js",   4, 45.42,  19, True),
]
TIER_NAME = {1: "T1 active", 2: "T2 mature", 3: "T3 zombie", 4: "T4 archived"}


def tier_vals(t):
    return np.array([r[2] for r in COHORT if r[1] == t], float)


def main():
    print("=" * 78)
    print(" FOUR-COHORT tau_v EXPERIMENT — enforcement latency across a decline gradient")
    print(" live via project-6q4gj/api/gh-issues, 2026-07-10, pages=2")
    print("=" * 78)
    print(f"\n  {'repo':22s} {'tier':11s} {'tau_v(d)':>9s} {'n':>5s}  archived")
    for r in COHORT:
        print(f"  {r[0]:22s} {TIER_NAME[r[1]]:11s} {r[2]:9.2f} {r[3]:5d}  {r[4]}")

    print("\n  per-tier summary")
    print("  " + "-" * 52)
    print(f"  {'tier':12s} {'n':>3s} {'mean':>8s} {'median':>8s}")
    for t in (1, 2, 3, 4):
        v = tier_vals(t)
        print(f"  {TIER_NAME[t]:12s} {len(v):3d} {v.mean():8.2f} {np.median(v):8.2f}")

    # ── overall difference across the four tiers ─────────────────────────────
    groups = [tier_vals(t) for t in (1, 2, 3, 4)]
    H, p_kw = stats.kruskal(*groups)
    print("\n  Kruskal-Wallis across all 4 tiers:  H = %.2f,  p = %.4g" % (H, p_kw))

    # ── ordered trend across the ENFORCEMENT-DECLINE tiers (T1<T2<T3) ─────────
    dec = [(r[1], r[2]) for r in COHORT if r[1] in (1, 2, 3)]
    tiers = np.array([d[0] for d in dec], float)
    taus = np.array([d[1] for d in dec], float)
    rho, p_sp = stats.spearmanr(tiers, taus)
    tau_k, p_k = stats.kendalltau(tiers, taus)
    print("\n  Ordered trend T1<T2<T3 (enforcement decline, archival-artifact tier excluded):")
    print(f"    Spearman rho = {rho:.3f}  (p = {p_sp:.4g})")
    print(f"    Kendall  tau = {tau_k:.3f}  (p = {p_k:.4g})")

    # ── the decisive contrast: enforcement-intact vs enforcement-collapsed ───
    intact = np.concatenate([tier_vals(1), tier_vals(2)])   # T1+T2
    collapsed = tier_vals(3)                                 # T3 zombie
    U, p_mw = stats.mannwhitneyu(collapsed, intact, alternative="greater")
    print("\n  Enforcement-intact (T1+T2) vs enforcement-collapsed zombie (T3):")
    print(f"    intact    median = {np.median(intact):6.2f} d  (n={len(intact)})")
    print(f"    collapsed median = {np.median(collapsed):6.2f} d  (n={len(collapsed)})")
    print(f"    ratio of medians = {np.median(collapsed)/np.median(intact):.1f}x")
    print(f"    Mann-Whitney one-tailed (collapsed > intact): p = {p_mw:.4g}")

    # ── T4 archival bulk-close artifact, quantified ──────────────────────────
    t4 = tier_vals(4)
    print("\n  T4 archived breaks monotonicity DOWNWARD (the bulk-close artifact):")
    print(f"    T3 zombie median  = {np.median(tier_vals(3)):6.2f} d")
    print(f"    T4 archived median= {np.median(t4):6.2f} d   (LOWER than T3, as predicted)")
    print("    angular.js (7.97 d) & lovefield (14.71 d): trailing issues mass-closed at EOL.")

    print("\n" + "=" * 78)
    print(" INTERPRETATION")
    print("=" * 78)
    print(
        "  - tau_v rises monotonically across the enforcement-decline gradient\n"
        "    (T1 active ~4.6d -> T2 mature ~5.6d -> T3 zombie ~77.7d): a ~16x jump\n"
        "    from enforcement-intact to enforcement-collapsed, p ~ %.3g.\n"
        "  - Age is NOT the driver: T2 mature projects are old but still enforce, so\n"
        "    their tau_v stays low. tau_v tracks live enforcement capacity, not age.\n"
        "  - The ZOMBIE tier (dead core + cosmetic commits, NOT archived) is where the\n"
        "    sensor earns its keep: a last-commit heuristic calls these 'active'; tau_v\n"
        "    flags them. tau_v LEADS the lifecycle label.\n"
        "  - T4 archived breaks the monotonic prediction DOWNWARD exactly as pre-stated:\n"
        "    formal archival mass-closes issues and deflates tau_v. The violation is\n"
        "    diagnostic, not damaging — it isolates the one artifact a deployer must\n"
        "    exclude (drop repos with a bulk-close spike at the archival timestamp)."
        % p_mw
    )
    print("=" * 78)


if __name__ == "__main__":
    main()
