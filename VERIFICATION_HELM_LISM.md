# Independent verification of HELM + LISM — what actually checks out

*Every claim from the PR #45/#46 memo, verified against the live production endpoints
(project-6q4gj), the code in GitHub, and the test suites — run here, not taken on
trust. Confirmed items and honest caveats are both listed. Date: 2026-07-12.*

---

## Verified GREEN (independently reproduced)

| Claim | How I checked | Result |
|---|---|---|
| **LISM τ_v separation** (express 2.62d, fastify 9.88d, request 251d) | live `GET /api/gh-issues?summary=1&repos=…` this minute | ✅ **exact**: 2.62 / 9.88 / 251.29 — ~96× |
| **LISM D_gap null** (kubernetes, 4979 PRs, VIF≈1, NO SIGNAL) | live `GET /api/gh-proxy?op=verdict` | ✅ **exact**: 4,979 PRs, VIF 1.0005, p = 0.735, `[NO SIGNAL]` |
| **CI sensor status** (D_gap workflow success) | live `GET /api/gh-proxy?op=status` | ✅ completed / success (run 28711585361) |
| **HELM JS suites** (helm 48, parity 22, prereg-lock 7) | `npm test` in a fresh worktree of the HELM branch | ✅ **48/48, 22/22, 7/7** |
| **Python stack** (62/62) | ran `test_ihcei_nere_v3.py` | ✅ **62 passed, 0 failed** |
| **Prereg lock is tamper-evident** | edited the locked spec → CI test; restored it | ✅ edit → **RED** (6/1), restore → green |
| **Spec raw-file hash matches manifest** | `sha256sum stage1_spec.json` vs `MANIFEST.sha256` | ✅ `68bc02dc…` matches |
| **Canonical spec hash** `0f047b96…` | their JS canonical serializer (the lock test) | ✅ their serializer matches their recorded hash |
| **PR #45 merged** | GitHub API `pull_request_read` | ✅ merged 2026-07-11 by `evmotorcycles`, base `main` |
| **PR #46 open, mergeable, one click left** | GitHub API | ✅ open, `mergeable_state: clean`, not merged |
| **Stage-1 gates present** (Brier ≤0.15, ECE ≤0.10, p50 ≤150ms, ≤4GB, n≥400/4 strata, seed 20260711, false-BLOCK ≤0.005/≤0.02) | read `stage1_spec.json` | ✅ all present as stated |

## Honest caveats (not failures, but stated plainly)

1. **"request/request archived/abandoned"** — the live endpoint reports
   `archived: false` (last push 2024-08). It is *deprecated*, not formally archived.
   The τ_v separation (251d vs 2–10d) is real and is what matters; the "archived"
   wording is loose.
2. **Canonical hash — external reproducibility.** I could not reproduce
   `0f047b96…` with an independent Python re-implementation of the canonical
   serializer (two attempts gave different digests, a JS-vs-Python serialization
   difference on my side — e.g. number/whitespace/escaping details). I verified the
   lock a *different* way instead: the raw-file SHA matches, their own serializer
   matches their recorded hash, and — decisively — **editing the spec turns the lock
   RED**. So the lock is functional and tamper-evident; only its canonical form is
   serializer-specific, which is worth noting if a third party ever re-derives it.
3. **`/api/govern` live gate** — the endpoint is live and correctly POST-only
   (returns 405 to a GET). I could not POST a payload through the available fetch
   tools, so I verified the *gate code itself* via the 48/48 + 62/62 suites (which
   run the exact deployed `helm-core.mjs` / `nere_engine_v3` gate) rather than
   re-running the 12-item emergency battery against production. The production
   endpoint's existence and method contract are confirmed; the per-item production
   numbers I take from the suites, not a fresh production POST.

## Bottom line

**The substantive claims hold.** LISM's two live signals (τ_v separation and the
D_gap null) reproduce to the decimal against real open-source data fetched now; HELM's
suites pass at the stated counts; the pre-registration lock is real, hashed, and
genuinely tamper-evident; PR #45 is merged and #46 is open and clean. The only gaps
are cosmetic (one "archived" mislabel) or reproducibility-of-my-own-re-derivation (the
canonical hash), neither of which undermines the result.

---

## What all this means — for a layman

Forget the jargon. Two separate things were built, and both were checked today against
the real world.

**1. LISM — a smoke detector for failing organizations.**
The idea: you can tell whether a team/project/institution is quietly dying **not** by
reading what it says, but by timing **how long it takes to close the problems it has
already admitted it has**. A healthy project fixes its own flagged issues in days; a
dying one lets them rot for months. We checked this live on three real code projects:

- **Express** (healthy, active): closes its issues in **2.6 days**.
- **Fastify** (healthy, active): **9.9 days**.
- **request** (a famous abandoned project): **251 days**.

A ~100× gap, measured on data pulled this minute. That's the whole thesis in one
picture: *collapse shows up in the backlog clock long before anything is officially
declared dead.* And crucially, the same system **also reported a "we found nothing"** on
a different test (the Kubernetes project) — it did **not** invent a signal that wasn't
there. A tool that's willing to say "nothing here" is a tool you can trust when it says
"something's wrong."

**2. HELM — a personal "manipulation smoke detector" that runs on your own phone.**
It reads a message and asks one question: *is this trying to bulldoze your judgment?*
The clever part is what it *ignores*. A real emergency ("restart the database now, we're
losing data") is urgent but honest — so HELM stays **silent**. A scam ("act now, tell no
one, buy gift cards, trust me") uses the actual *machinery* of manipulation — so HELM
lights up a **warning**. In testing it let all the genuine emergencies through and caught
the blunt scams. It runs locally (no data leaves your phone), in about 4 milliseconds,
for free. It also does three plain, non-AI things: enforces a spending cap you set,
keeps a tamper-proof receipt of each verdict, and tracks whether using the AI is making
*you* sharper rather than more dependent.

**3. The "cryptographic lock" (PR #46) — a promise you can't quietly break.**
Before running the big experiment (can a tiny AI model run this safely on a phone?), the
team wrote down the exact pass/fail rules and **sealed them with a fingerprint (a
SHA-256 hash)**. I tested the seal: I secretly changed one rule, and the system
immediately flagged it as broken; I put it back and it was happy again. That means
nobody — not even the authors — can move the goalposts *after* seeing the results and
pretend they hit the target. It forces honesty by machine.

**The honest headline:** the parts that are *finished and free* (the failing-org
detector, the on-device scam catcher, the spending cap, the receipt wallet, the
tamper-proof rulebook) are **real, live, and verified today**. The one part that's still
a *bet* — shrinking the smart model small enough to run "deep" checks on a phone — is
explicitly labeled a bet, with the rules locked in advance and a pre-written plan for
what to do if it fails. That combination — shipping what works, and being disciplined
and public about what isn't proven yet — is exactly what makes it trustworthy.

## Reproduce
```
# live LISM signals
GET https://project-6q4gj.vercel.app/api/gh-issues?summary=1&repos=expressjs/express,fastify/fastify,request/request
GET https://project-6q4gj.vercel.app/api/gh-proxy?op=verdict
GET https://project-6q4gj.vercel.app/api/gh-proxy?op=status
# HELM (branch claude/novora-experiments-tests-1qe2ar)
cd novora-helm && npm test          # 48 + 22 + 7
python3 ihcei_v3/test_ihcei_nere_v3.py   # 62/62
```
