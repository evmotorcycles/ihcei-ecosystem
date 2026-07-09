# Barakah / Knowledge-Propagation Extension — Result (live Stack Exchange)

**Date:** 2026-07-09 · **Source:** live Stack Overflow via `api/se-search.js`
(Vercel `project-6q4gj`) · **Harness:** `se_barakah_test.py` ·
**Spec:** `PREREGISTRATION_barakah_knowledge.md`.

This is the **first genuine extension of the LISM linear essence law beyond the two
completed cohorts (yeast, GitHub)** — into the socially-generated
knowledge-propagation domain the framework's own operationalization of Barakah
points to (D_enc = sincere seeking / query fidelity; D_dec = selflessness / onward
transmission; E = Barakah = downstream compounding reuse).

## Why this domain is testable where the other three were not
Stack Exchange has **three different actors per unit** — the asker (encoding), the
answerers (decoding/propagation), and downstream readers (reuse) — so the two hops
and the outcome are drawn from independent sources. That is exactly the channel
independence (I1) that clinical, contract, and legislative datasets lacked.

## Cohorts and result

| Cohort | N | VIF(D_enc,D_dec) | E=1 / E=0 | linear AUC | quad AUC | nested verdict |
|---|--:|--:|--:|--:|--:|---|
| SO `python` | 400 | 1.12 (r=+0.32) | 134 / 266 | 0.575 | 0.586 | **no curvature** (ΔAIC −1.8, p=0.67) |
| SO `javascript` | 400 | 1.20 (r=+0.41) | 135 / 265 | 0.617 | 0.624 | no curvature |
| **pooled** | 793 | 1.08 (r=+0.28) | 267 / 526 | 0.593 | 0.602 | **no curvature** (LRT p≈1) |

**Verdict: LINEAR adequate — consistent with LISM.** The two hops are independent
(VIF ≈ 1.1, so a *valid* two-hop test), the failing region is populated
(≥ 100 per cell), and adding `D²` improves prediction in neither cohort. As in the
yeast arm, the `D²` term hits separation and its point ΔAIC is unstable, so the
verdict rests on the non-significant likelihood-ratio test and the linear-vs-quad
AUC contrast — both saying the squared term adds nothing.

## Honest scope
- **The effect is weak** (AUC ≈ 0.58–0.62): two-hop fidelity only weakly predicts
  downstream reuse here. Part of this is a **time confound** — the proxy fetches
  newest-first questions, whose `view_count` has had little time to accumulate. A
  stronger test would use activity-aged or vote-sorted threads. The
  *linear-vs-quadratic* verdict (the object of the test) is nonetheless robust.
- This is one domain and two tags; it is a **first extension**, not a closed case.
  It does what the three high-stakes domains could not: pass the invariants and
  return a verdict — and that verdict is linear, not the accelerating quadratic.

## Standing of the linear law after this run
Empirically linear in **three** channel-intact settings now — a dense biological
interactome, a pre-registered software-repository cohort, and a socially-generated
knowledge network — plus directionally linear in the one-hop legislation run. No
positive evidence for the accelerating quadratic anywhere a valid test was possible.

## Reproduce
```
curl "https://project-6q4gj.vercel.app/api/se-search?site=stackoverflow&tag=python&pages=4" > se.json
python se_barakah_test.py --json se.json
```
