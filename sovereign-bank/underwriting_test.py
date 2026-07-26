#!/usr/bin/env python3
"""
underwriting_test.py — does behaviour price default better than prestige?
========================================================================
The corrected form of the falsified Knowledge-Exchange question.

K1 failed because its yield proxies (downloads, forks) were THEMSELVES popularity
measures, so popularity trivially predicted popularity. Here the outcome is held
NON-CIRCULAR: default is derived from lifecycle only (archived / no push in >730d),
never from stars, forks or downloads.

Two underwriters compete on the SAME real repositories:
  CONVENTIONAL (status-based)  — score by popularity (stars). Fund the most-starred.
  SOVEREIGN   (decoupled)      — ignore stars entirely; score by enforcement latency
                                 tau_v. This is F_out = F_eval: underwrite measured
                                 behaviour, not self-reported standing.

Pre-registered in prereg/bank_prereg.json, canonical sha256 fbe085fc..., LOCKED
before the data was fetched and before this runner was written.

Data: fetched live 2026-07-25 via the project-6q4gj gh-issues proxy (stars, tau_v and
lifecycle in the same call). Sampling frame: the previously-committed tau_v cohorts,
assembled in earlier sessions for lifecycle diversity. Stars were NEVER a sampling
criterion — which matters, because stars are the predictor under test.

Run:  python3 sovereign-bank/underwriting_test.py
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCKED = "fbe085fcf4cc2a7f5b3bf386a7e81f1542cda6f6f826996ca75ef41162f0d62a"

# (repo, stargazers, tau_v_days, default)  default: 1 = archived or no push >730d
COHORT = [
    ("request/request",            25530, 209.33, 0),
    ("bower/bower",                14916,  92.82, 0),
    ("lodash/lodash",              61258,  30.59, 0),
    ("moment/moment",              47937,  67.69, 0),
    ("jashkenas/underscore",       27341,  31.87, 0),
    ("facebook/create-react-app", 103302,   5.19, 0),
    ("gulpjs/gulp",                32958,  25.02, 0),
    ("SerenityOS/serenity",        33658,  17.77, 0),
    ("pallets/flask",              72014,   0.63, 0),
    ("fastify/fastify",            36803,  16.15, 0),
    ("microg/GmsCore",             14013,   3.95, 0),
    ("vitejs/vite",                82089,   2.03, 0),
    ("RIOT-OS/RIOT",                5765,   3.43, 0),
    ("psf/requests",               54175,   0.25, 0),
    ("sveltejs/svelte",            87678,   4.09, 0),
    ("apache/nuttx",                3964,   3.97, 0),
    ("termux/termux-app",          58127,   3.33, 0),
    ("expressjs/express",          69246,   4.76, 0),
    ("gohugoio/hugo",              89174,   2.17, 0),
    ("zephyrproject-rtos/zephyr",  15990,   0.17, 0),
    ("Netflix/Hystrix",            24477, 319.14, 0),   # maintenance-mode but not yet stale
    ("angular/angular.js",         58572,   7.97, 1),   # archived; issues bulk-closed at EOL
    ("google/lovefield",            6769,  14.71, 1),
    ("yahoo/mojito",                1560,  44.24, 1),
    ("facebook/draft-js",          22626,  45.42, 1),
    ("jquery/jquery-mobile",        9613,  24.57, 1),
    ("nodejs/node-v0.x-archive",   34297,  70.51, 1),
]


def auc(scores, labels):
    """P(score(default) > score(survivor)), ties = 0.5. Pure stdlib."""
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return float("nan")
    wins = sum((1.0 if a > b else 0.5 if a == b else 0.0) for a in pos for b in neg)
    return wins / (len(pos) * len(neg))


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def median(v):
    v = sorted(v); n = len(v)
    return float("nan") if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)


def main():
    lock = open(os.path.join(HERE, "prereg", "BANK.sha256")).read()
    print("=" * 84)
    print(" SOVEREIGN-BANK UNDERWRITING TEST — behaviour vs prestige, on real repositories")
    print(" " + [l for l in lock.splitlines() if "canonical" in l][0].strip())
    print("=" * 84)

    stars = [r[1] for r in COHORT]
    tau = [r[2] for r in COHORT]
    default = [r[3] for r in COHORT]
    nd, ns = sum(default), len(default) - sum(default)
    print(f"\n cohort: N={len(COHORT)}  defaults={nd}  performing={ns}")
    print(f" median tau_v   default={median([t for t,d in zip(tau,default) if d]):7.2f} d   "
          f"performing={median([t for t,d in zip(tau,default) if not d]):7.2f} d")
    print(f" median stars   default={median([s for s,d in zip(stars,default) if d]):7.0f}     "
          f"performing={median([s for s,d in zip(stars,default) if not d]):7.0f}")

    results, failed = [], []
    def gate(name, ok, detail):
        (results if True else results).append({"gate": name, "pass": bool(ok), "detail": detail})
        if not ok:
            failed.append(name)
        print(f"\n  {'PASS' if ok else 'FAIL'} {name}\n        {detail}")

    # B1 / B2 — discrimination. Conventional scores default risk as LOW stars.
    auc_tau = auc(tau, default)                    # high tau_v -> predict default
    auc_star = auc([-s for s in stars], default)   # low stars  -> predict default
    gate("B1_tauv_beats_stars", auc_tau > auc_star,
         f"AUC(tau_v -> default) = {auc_tau:.4f}   vs   AUC(low-stars -> default) = {auc_star:.4f}")
    gate("B2_popularity_is_near_chance", 0.30 <= auc_star <= 0.70,
         f"AUC(stars) = {auc_star:.4f} (pre-registered near-chance band [0.30, 0.70])")

    # B3 — portfolio default rates. Each underwriter funds the half it prefers.
    half = len(COHORT) // 2
    conv_book = sorted(COHORT, key=lambda r: -r[1])[:half]   # most-starred
    sov_book = sorted(COHORT, key=lambda r: r[2])[:half]     # lowest enforcement latency
    conv_rate = sum(r[3] for r in conv_book) / len(conv_book)
    sov_rate = sum(r[3] for r in sov_book) / len(sov_book)
    gate("B3_portfolio_default_rate", sov_rate < conv_rate,
         f"loan book of {half}: conventional (top stars) defaults {conv_rate:.1%}  |  "
         f"sovereign (low tau_v) defaults {sov_rate:.1%}")

    # B4 — are they even different axes?
    rho = spearman(stars, tau)
    gate("B4_two_axes_not_collinear", abs(rho) < 0.50,
         f"spearman(stars, tau_v) = {rho:+.4f}  -> popularity and enforcement latency are "
         f"{'independent orderings' if abs(rho) < 0.5 else 'the same signal restated'}")

    print("\n" + "=" * 84)
    print(f" RESULT: {len(results)-len(failed)}/{len(results)} pre-registered gates met")
    if failed:
        print(f" GATES NOT MET: {failed}")
        print(" Reported as-is. No threshold was moved and no gate was dropped after seeing"
              "\n the numbers; the misses are asserted in the test suite.")
    print("\n LIMITS (declared in the locked spec, before any data):")
    print("   - N=27 with 6 defaults: UNDERPOWERED. No p-value or confidence claim is made.")
    print("   - repository abandonment is an ANALOGUE of credit default, not credit data.")
    print("   - this tests the EVALUATOR layer only; full-reserve and risk-sharing contract")
    print("     structure is architecture, not evidence, and is labelled as such.")
    print("=" * 84)

    json.dump({"spec_sha256_canonical": LOCKED, "N": len(COHORT), "defaults": nd,
               "auc_tau_v": round(auc_tau, 4), "auc_stars": round(auc_star, 4),
               "portfolio": {"conventional_default_rate": round(conv_rate, 4),
                             "sovereign_default_rate": round(sov_rate, 4)},
               "spearman_stars_tauv": round(rho, 4),
               "gates": results, "gates_not_met": failed},
              open(os.path.join(HERE, "results_bank.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
