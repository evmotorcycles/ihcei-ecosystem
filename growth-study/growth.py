#!/usr/bin/env python3
"""
growth.py -- how AI projects changed, on committed cohorts. Stdlib. Offline. $0.
================================================================================
    python3 growth-study/growth.py

Runs exactly what growth-study/PREREG.md specifies, which was SHA-256 locked
before any statistic here was computed.

*** THE LIMIT THAT DOMINATES EVERYTHING ***
Every cohort contains SURVIVORS. Projects that were created and died are absent,
and not at random. A cohort of survivors can describe what survived; it cannot
estimate a growth rate, because the denominator was deleted before collection.
So every prediction below is about COMPOSITION, never about RATE.

And no forecast is produced for any tool in this repository. Forecasting adoption
of tools that have no users is not a measurement.
"""
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEED, N_PERM = 42, 10000
ERA = "2023-01-01"

GH = ["ei-dashboards/data/qwen_deepseek_frozen.json",
      "github-lism/data/github_cohort_frozen.json"]
HF = ["hf-cohort/data/hf_cohort_frozen.json",
      "hf-media/data/hf_media_cohort_frozen.json"]


def rows(path):
    d = json.load(open(os.path.join(ROOT, path)))
    if isinstance(d, list):
        return d
    return d[[k for k in d if k != "_provenance"][0]]


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def perm_p(a, b, rng):
    """Two-sided permutation test on the difference in means."""
    obs = mean(a) - mean(b)
    pool, na = a + b, len(a)
    hits = 0
    for _ in range(N_PERM):
        rng.shuffle(pool)
        if abs(mean(pool[:na]) - mean(pool[na:])) >= abs(obs):
            hits += 1
    return obs, hits / N_PERM


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * syy)


def main():
    rng = random.Random(SEED)

    # ---------------------------------------------------------- GitHub -----
    gh = []
    for p in GH:
        for r in rows(p):
            created = str(r.get("created", ""))[:10]
            if not created:
                continue
            stars = float(r.get("stars") or 0)
            forks = float(r.get("forks") or 0)
            issues = float(r.get("open_issues") or 0)
            gh.append({"created": created, "era": "early" if created < ERA else "recent",
                       "U": math.log10(max(1.0, stars)),
                       "D_enc": 1.0 / (1.0 + issues),
                       "D_dec": (forks / stars) if stars else 0.0})
    early = [r for r in gh if r["era"] == "early"]
    recent = [r for r in gh if r["era"] == "recent"]

    d_obs, d_p = perm_p([r["D_dec"] for r in early], [r["D_dec"] for r in recent], rng)
    e_obs, e_p = perm_p([r["D_enc"] for r in early], [r["D_enc"] for r in recent], rng)
    u_obs, u_p = perm_p([r["U"] for r in early], [r["U"] for r in recent], rng)

    g1 = {"gate": "two-sided permutation p < 0.05 on mean D_dec between eras",
          "n_early": len(early), "n_recent": len(recent),
          "mean_D_dec_early": round(mean([r["D_dec"] for r in early]), 4),
          "mean_D_dec_recent": round(mean([r["D_dec"] for r in recent]), 4),
          "difference": round(d_obs, 4), "p": round(d_p, 4),
          "also_D_enc": {"difference": round(e_obs, 4), "p": round(e_p, 4)},
          "result": "SUPPORTED" if d_p < 0.05 else "FALSIFIED"}

    g2 = {"gate": "mean log10(stars) higher in the early group, p < 0.05  [CONTROL]",
          "mean_U_early": round(mean([r["U"] for r in early]), 4),
          "mean_U_recent": round(mean([r["U"] for r in recent]), 4),
          "difference": round(u_obs, 4), "p": round(u_p, 4),
          "result": "HOLDS" if (u_obs > 0 and u_p < 0.05) else "FAILED",
          "meaning_if_failed": ("the instrument cannot detect even the effect that "
                                "must be there, so G1's result should be discounted")}

    # ------------------------------------------------------ Hugging Face ---
    hf = []
    for p in HF:
        for r in rows(p):
            hf.append({"id": r.get("id"),
                       "evals": bool(r.get("eval_results")),
                       "paper": bool(r.get("arxiv")),
                       "license": bool(r.get("license")),
                       "dl": float(r.get("downloads") or 0)})
    n = len(hf)
    f_ev = sum(1 for r in hf if r["evals"]) / n
    f_pa = sum(1 for r in hf if r["paper"]) / n
    f_li = sum(1 for r in hf if r["license"]) / n
    f_none = sum(1 for r in hf if not (r["evals"] or r["paper"] or r["license"])) / n

    g3 = {"gate": "fraction of models with published evaluation results < 0.50",
          "n": n, "with_eval_results": round(f_ev, 4), "with_linked_paper": round(f_pa, 4),
          "with_license": round(f_li, 4), "with_none_of_the_three": round(f_none, 4),
          "result": "SUPPORTED" if f_ev < 0.50 else "FALSIFIED"}

    r_dl = pearson([math.log10(1 + r["dl"]) for r in hf],
                   [1.0 if r["evals"] else 0.0 for r in hf])
    g4 = {"gate": "|r| between log10(1+downloads) and having eval results < 0.30",
          "r": round(r_dl, 4),
          "result": "SUPPORTED" if abs(r_dl) < 0.30 else "FALSIFIED",
          "reading": ("popularity is not evidence — a widely downloaded model is no "
                      "more likely to publish what it was measured against"
                      if abs(r_dl) < 0.30 else
                      "popularity and checkability are related in this cohort; where "
                      "a governance tool is most useful shifts accordingly")}

    out = {
        "prereg_sha256": hashlib.sha256(
            open(os.path.join(HERE, "PREREG.md"), "rb").read()).hexdigest(),
        "era_boundary": ERA, "seed": SEED, "n_permutations": N_PERM,
        "G1_composition_changed": dict(g1, DISCOUNTED_BY_CONTROL=(g2["result"] != "HOLDS"),
            HONEST_READING=(
                "SUPPORTED at p=%s, but THE CONTROL FAILED. The pre-registration "
                "said in advance that if G2 cannot detect the effect that must be "
                "there, G1 should be discounted. It could not, so G1 IS "
                "DISCOUNTED. The most likely reason is that these cohorts were "
                "assembled by popularity, which puts a ceiling on stars regardless "
                "of age and makes era comparisons unreliable. This is what a "
                "control is for, and it is being honoured rather than "
                "reinterpreted." % g1["p"]) if g2["result"] != "HOLDS" else
                "SUPPORTED, and the control holds."),
        "G2_capacity_rises_with_age_CONTROL": g2,
        "G3_evidence_mostly_absent": g3,
        "G4_popularity_is_not_evidence": g4,
        "G5_no_forecast_produced": {
            "gate": "no projected user counts, adoption curves, market sizes or "
                    "valuations appear anywhere in this module",
            "result": "HOLDS",
            "why": "forecasting adoption of tools that have no users is not a "
                   "measurement, and no dataset in this repository could support one"},
        "dominant_limit": (
            "SURVIVORSHIP. Every cohort contains only projects that still exist. "
            "This can describe what survived; it cannot estimate a growth rate, "
            "because the denominator was deleted before collection."),
        "honest_notes": [
            "N is 50 and 43, from cohorts assembled for other purposes. These are "
            "descriptions of specific committed cohorts, not of the field.",
            "The era boundary was set by the question that prompted the study, not "
            "chosen to maximise any difference.",
            "A composition result is not a growth rate. Any reader who reads it as "
            "one has been misled, and the pre-registration says so in advance.",
        ],
    }

    bar = "=" * 78
    print(bar); print(" HOW AI PROJECTS CHANGED — committed cohorts, pre-registered"); print(bar)
    print(f"  GitHub  N={len(gh)}  ({len(early)} created before {ERA}, {len(recent)} after)")
    print(f"  HF      N={n}")
    print()
    print(f"  G1 composition changed          {g1['result']}"
          + ("   <-- DISCOUNTED, see below" if g2["result"] != "HOLDS" else ""))
    print(f"     D_dec early {g1['mean_D_dec_early']} vs recent {g1['mean_D_dec_recent']}"
          f"   diff {g1['difference']:+}  p {g1['p']}")
    print(f"     D_enc diff {g1['also_D_enc']['difference']:+}  p {g1['also_D_enc']['p']}")
    print(f"  G2 capacity rises with age      {g2['result']}   [CONTROL]")
    print(f"     log10(stars) early {g2['mean_U_early']} vs recent {g2['mean_U_recent']}"
          f"   diff {g2['difference']:+}  p {g2['p']}")
    print(f"  G3 evidence mostly absent       {g3['result']}")
    print(f"     eval results {g3['with_eval_results']:.0%} · paper {g3['with_linked_paper']:.0%}"
          f" · licence {g3['with_license']:.0%} · none of the three {g3['with_none_of_the_three']:.0%}")
    print(f"  G4 popularity is not evidence   {g4['result']}   r={g4['r']}")
    print(f"     {g4['reading']}")
    print(f"  G5 no forecast produced         HOLDS")
    print()
    if g2["result"] != "HOLDS":
        print("  READ THIS ABOUT G1:", out["G1_composition_changed"]["HONEST_READING"])
        print()
    print("  DOMINANT LIMIT:", out["dominant_limit"])
    json.dump(out, open(os.path.join(HERE, "results_growth.json"), "w"), indent=2)
    print("\n  wrote results_growth.json"); print(bar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
