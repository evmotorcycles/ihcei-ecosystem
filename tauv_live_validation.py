#!/usr/bin/env python3
"""
tauv_live_validation.py
=======================
Thorough, LIVE validation of the enforcement-latency sensor (tau_v) on a fresh,
independent set of GitHub repositories, fetched via api/gh-issues.js (batch
summary mode) on 2026-07-09. No placeholders: every tau_v below was computed
server-side from that repo's real, closed, non-PR issue timeline
(tau_v = mean close latency in days, capped at 365; sort=created desc, pages=3,
i.e. up to the 300 most-recently-opened issues).

This is a SUPPLEMENTARY re-test, not the manuscript's primary evidence. The
headline GitHub finding (failed 50.6 d vs surviving 19.8 d, MWU p ~ 1e-31) rests
on the PRE-REGISTERED CI cohort (N = 992) with a non-circular, CI-derived failure
label. The purpose here is to stress-test tau_v on a convenience cross-section and
report — honestly — what a naive off-the-shelf lifecycle label does and does not
reproduce.

Two analyses:
  A. Pre-specified naive label:  E = 0 (failed) if archived OR pushed > 730 d ago,
     else E = 1 (survived).  MWU one-tailed (failed tau_v > survived tau_v).
  B. Diagnostic health reclassification (POST-HOC, judgement-based, documented):
     'active' = genuinely maintained as of 2026; 'dormant' = publicly
     deprecated / maintenance-only / archived. This is exactly the distinction
     tau_v is meant to detect, and the naive last-push label cannot.
"""
import numpy as np
from scipy.stats import mannwhitneyu

# --- Live cohort, fetched 2026-07-09 via project-6q4gj/api/gh-issues (pages=3) ---
# fields: repo, tau_v (days), n_closed, archived, pushed_at, E_naive (1=surv,0=fail),
#         status ('active' | 'dormant'), status_basis (public evidence for status)
COHORT = [
    # ---- naive-survived (E=1): NOT archived AND pushed within 730 days ----
    ("pallets/flask",            11.92,  78, False, "2026", 1, "active",  "actively developed; frequent releases"),
    ("psf/requests",              3.38,  27, False, "2026", 1, "active",  "maintained; security/bugfix releases"),
    ("expressjs/express",         2.71,  30, False, "2026", 1, "active",  "Express 5 line under active development"),
    ("axios/axios",               7.80,  43, False, "2026", 1, "active",  "actively developed"),
    ("tqdm/tqdm",                84.46,  31, False, "2026", 1, "active",  "maintained; small team, slow triage"),
    ("moment/moment",            88.46,  85, False, "2024", 1, "dormant", "maintenance mode since 2020; project itself recommends alternatives"),
    ("bower/bower",             121.67, 200, False, "2024", 1, "dormant", "deprecated 2017; repo touched only for docs"),
    ("jashkenas/backbone",       73.10, 147, False, "2026", 1, "dormant", "dormant; no feature development for years"),
    ("Netflix/Hystrix",         317.68, 229, False, "2025", 1, "dormant", "officially in maintenance mode since ~2018; not accepting features"),
    ("airbnb/enzyme",            45.29, 143, False, "2025", 1, "dormant", "effectively abandoned; no React 18 support"),
    ("Netflix/falcor",          147.10,  98, False, "2025", 1, "dormant", "abandoned ~2018; only sporadic housekeeping commits"),
    ("petkaantonov/bluebird",    83.85, 123, False, "2024", 1, "dormant", "superseded by native promises; dormant"),
    # ---- naive-failed (E=0): archived == true ----
    ("angular/angular.js",        6.12, 126, True,  "2024", 0, "dormant", "AngularJS end-of-life; issues MASS-CLOSED at sunset (bulk-close artifact)"),
    ("nodejs/node-v0.x-archive", 118.29, 235, True, "2024", 0, "dormant", "archived legacy Node line"),
    ("google/lovefield",         29.57, 188, True,  "2021", 0, "dormant", "archived 2021; some trailing issues bulk-closed"),
    ("yahoo/mojito",             48.58,  56, True,  "2016", 0, "dormant", "archived 2016"),
    ("facebook/draft-js",        66.79,  23, True,  "2023", 0, "dormant", "archived 2023"),
    ("jquery/jquery-mobile",     24.57,  66, True,  "2021", 0, "dormant", "archived 2021; trailing issues bulk-closed"),
]


def mwu_greater(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    try:
        _, p = mannwhitneyu(a, b, alternative="greater")
    except Exception:
        p = float("nan")
    return p


def summarize(name, group_true, group_false, label_true, label_false):
    """group_true is the hypothesised-HIGHER group (failed / dormant)."""
    t = np.array([r[1] for r in group_true], float)
    f = np.array([r[1] for r in group_false], float)
    p = mwu_greater(t, f)
    print(f"\n{name}")
    print("-" * len(name))
    print(f"  {label_true:9s} (n={len(t):2d}): mean tau_v = {t.mean():6.1f} d   median = {np.median(t):6.1f} d")
    print(f"  {label_false:9s} (n={len(f):2d}): mean tau_v = {f.mean():6.1f} d   median = {np.median(f):6.1f} d")
    if f.mean() > 0:
        print(f"  ratio of means  {label_true}/{label_false} = {t.mean()/f.mean():.2f}x")
    print(f"  ratio of medians                = {np.median(t)/max(np.median(f),1e-9):.2f}x")
    print(f"  MWU one-tailed ({label_true} > {label_false}): p = {p:.4g}")
    direction = "as hypothesised" if np.median(t) > np.median(f) else "OPPOSITE to hypothesis"
    print(f"  -> direction: {direction}")
    return p


def main():
    print("=" * 74)
    print("tau_v LIVE validation on a fresh GitHub cross-section  (fetched 2026-07-09)")
    print("=" * 74)
    print(f"repos: {len(COHORT)}   (pages=3, tau_v = mean close latency, cap 365 d)")
    print("\n  repo                       tau_v    n_closed  archived  E_naive  status")
    for r in COHORT:
        print(f"  {r[0]:26s} {r[1]:6.1f}   {r[2]:6d}      {str(r[3]):5s}    {r[5]}       {r[6]}")

    # --- Analysis A: pre-specified naive lifecycle label ---
    naive_fail = [r for r in COHORT if r[5] == 0]
    naive_surv = [r for r in COHORT if r[5] == 1]
    pA = summarize("A. Pre-specified naive label  (E = failed if archived OR pushed >730 d)",
                   naive_fail, naive_surv, "failed", "survived")

    # --- Analysis B: health reclassification (post-hoc, documented) ---
    dormant = [r for r in COHORT if r[6] == "dormant"]
    active = [r for r in COHORT if r[6] == "active"]
    pB = summarize("B. Health reclassification  (dormant/deprecated vs actively-maintained)",
                   dormant, active, "dormant", "active")

    # --- Analysis B': drop the documented archival bulk-close artifacts ---
    ARTIFACT = {"angular/angular.js", "jquery/jquery-mobile", "google/lovefield"}
    dormant2 = [r for r in dormant if r[0] not in ARTIFACT]
    pB2 = summarize("B'. Health reclassification, excluding documented bulk-close-at-archival repos",
                    dormant2, active, "dormant", "active")

    print("\n" + "=" * 74)
    print("INTERPRETATION")
    print("=" * 74)
    print(textwrap())


def textwrap():
    return (
        "A. The naive last-push lifecycle label does NOT reproduce the pre-registered\n"
        "   finding: mislabelled 'survivors' carry the HIGHEST tau_v. This is expected\n"
        "   and informative — two confounds the pre-registered CI cohort was designed\n"
        "   to avoid are visible here:\n"
        "     (1) Zombie contamination. Deprecated/maintenance-mode projects (Hystrix\n"
        "         317 d, falcor 147 d, bower 122 d, moment 88 d, bluebird 84 d) get\n"
        "         stray dependency-bump/doc commits, so 'pushed within 730 d' wrongly\n"
        "         labels them 'survived'. tau_v flags them as decaying; the last-push\n"
        "         heuristic does not. tau_v LEADS the crude lifecycle label.\n"
        "     (2) Archival bulk-close. Formally-archived repos (angular.js 6 d,\n"
        "         jquery-mobile 25 d, lovefield 30 d) had trailing issues mass-closed\n"
        "         at sunset, deflating tau_v downward — the opposite artefact.\n"
        "B/B'. Reclassifying by ACTUAL maintenance status — precisely the decay tau_v\n"
        "   is meant to detect — recovers a strong directional signal: dormant median\n"
        "   ~73 d vs active median ~8 d (~9x), and cleaner still once the documented\n"
        "   bulk-close repos are removed. This is post-hoc and judgement-based (each\n"
        "   status is documented above), so it is illustrative, not confirmatory.\n"
        "BOTTOM LINE: the live convenience cross-section neither cleanly confirms nor\n"
        "   refutes on the naive label; it reproduces the known confounds and shows\n"
        "   tau_v tracking true institutional decay better than a last-commit proxy.\n"
        "   The manuscript's headline tau_v result stands on the PRE-REGISTERED CI\n"
        "   cohort (non-circular failure label, controlled sampling), not this sample."
    )


if __name__ == "__main__":
    main()
