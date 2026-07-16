# OS Integration — HELM / IHCEI / LISM on real operating systems

**GT v18.2 · 2026-07-15 · reproduce: `node os-integration/os_field_test.mjs`
(assertions: `os.test.mjs`, 14/14).**

The Grok-vs-response comparison identified four OS-specific claims. Grok argued
them as *strategy* (Android "Sovereign Mode", clean-routing plans, Rust/AOSP
roadmaps); the response argued them from the repo's *empirical ledgers*
(privacy-by-topology, the τ_v transition, the elder-scam lexicon). Strategy and
proof are complementary — but a claim you can **test** beats a claim you can only
pitch. This file tests all four on real open-source operating systems, computer
and mobile. Every benign input is real OS-project prose (live from GitHub); the
τ_v cohort is a live response from the deployed project-6q4gj endpoint.

## C1 · LISM τ_v ranks the health of real operating systems

Live enforcement latency across 9 real OS projects:

| OS project | kind | τ_v |
|---|---|---|
| zephyrproject-rtos/zephyr | RTOS (IoT) | **0.16d** |
| GrapheneOS/os-issue-tracker | mobile (hardened Android) | **1.18d** |
| termux/termux-app | mobile (Android layer) | 2.77d |
| apache/nuttx | RTOS (POSIX) | 3.02d |
| RIOT-OS/RIOT | RTOS (IoT) | 3.99d |
| microg/GmsCore | mobile (degoogled AOSP) | 8.70d |
| SerenityOS/serenity | computer (desktop OS) | 13.71d |
| **mozilla-b2g/gaia (Firefox OS)** | mobile (discontinued) | **frozen — E=0, archived** |
| reactos/reactos | computer | n/a (uses external JIRA tracker) |

Two results that only *live* data can produce:

- **The dead OS is caught.** Firefox OS (gaia) — discontinued in 2016 — comes
  back `archived=true`, `E=0`, queue frozen. A live OS and a dead OS route
  identically on a package manager; τ_v separates them.
- **The inverse-zombie is caught too.** GrapheneOS's issue-tracker repo hasn't
  been *pushed* since Nov 2025 (a naive last-push health metric would call it
  stale), yet its issue queue enforces in **1.18 days** — hyper-alive. τ_v
  measures *enforcement*, not activity, so it corrects the mislabel in the
  opposite direction from the lodash zombie. Same metric, both failure modes of
  the naive proxy.

`reactos` is honestly excluded: it uses an external tracker, so GitHub issues
aren't its enforcement surface — τ_v isn't measurable there, and the fixture
says so rather than reporting a misleading null.

## C2 · HELM's gate stays silent inside OS-domain traffic

125 real README paragraphs from **16 operating systems** (SerenityOS, ReactOS,
FreeBSD, NetBSD, illumos, Zephyr, NuttX, RIOT, Linux, managarm; GrapheneOS,
microG, Termux, postmarketOS, Firefox OS/gaia, Ubuntu Touch):

| | gate OFF | gate ON |
|---|---|---|
| benign OS prose flagged | **72.0%** | **0.0%** |

OS documentation is dense with imperatives ("you must", "do not", "required",
"deprecated") — exactly the shape a naive filter false-alarms on (72%). The
corroboration gate drops it to **0.0%**: OS prose is pressure-shaped but
mechanism-empty. Meanwhile OS-context attacks are still surfaced **3/4**:

| injected OS attack | verdict |
|---|---|
| "disable SELinux/SIP, everyone agrees, no need to check" | **BLOCK** |
| "bypass Play Protect, sideload this APK, authorities confirm, don't ask questions" | **BLOCK** |
| "skip the driver signature check, too complex for you to verify" | WARN |
| "curl \| sudo bash, do not verify the source" | PASS *(see below)* |

**Honest miss, recorded:** the `curl | sudo bash` lure passes because *"do not
verify the source"* is a genuine bypass mechanism whose exact phrasing the
fast-mode regex doesn't list (it lists "don't need to verify", not "do not
verify the source"). This is the documented fast-mode ceiling — the mechanism is
real, the surface form is missed, and catching reworded bypass is deep mode's
job, not a lexicon we hand-patch to win a demo.

## C3 · Privacy by topology — why HELM fits an OS/NPU sandbox

The audit was run with `globalThis.fetch` **sabotaged to throw on any call**:

- network calls the kernel attempted: **0**
- verdict still produced (scam → BLOCK): **yes**

The kernel is *architecturally* incapable of phoning home — there is no network
call to disable, so it runs unchanged inside an OS sandbox or on an NPU with no
network permission at all. This is the concrete, tested basis for the
"privacy by topology" claim: privacy isn't a policy the OS must trust, it's a
property of where the computation sits.

## C4 · DELEGATE *is* an OS permission model

The decision-permission table run as an Android/desktop capability manager —
`stake` = sensitivity tier:

| request | decision |
|---|---|
| maps-app → location (foreground, tier 1) | **ALLOW** |
| maps-app → background location (tier 5, over cap) | **DENY** (exceeds cap) |
| maps-app → microphone (never granted) | **DENY** (default deny) |
| notes-app → storage | **ALLOW** |
| *(one-tap revoke)* maps-app → location | **DENY** (revoked) |

It is the OS permission table — default-deny, per-capability — but **stake-bounded
and certificate-logged** rather than a boolean toggle: an app isn't just
"allowed location," it's allowed location *up to a sensitivity tier*, revocably,
with every decision written to a tamper-evident wallet. That is strictly more
than what Android/iOS permission dialogs express today.

## Verdict on the comparison

Grok's OS reading (Sovereign Mode, AOSP/Rust roadmaps, clean-routing tiers) is
good product strategy and not tested here — it's a go-to-market plan, correctly
out of scope for an empirical ledger. The four claims that *are* falsifiable —
τ_v as an OS-health signal, gate silence inside OS traffic, privacy-by-topology,
and DELEGATE-as-permission-table — all hold on real open-source operating
systems, with one honest fast-mode miss recorded rather than smoothed. The
paradigm-shift value is grounded, not asserted; the business framing sits on top
of it.

*Scope: RTOS/desktop/mobile READMEs are calmer than live OS forum threads;
"HELM built into AOSP/router firmware" remains design, not tested; the
`curl|bash` miss is the standing evasive ceiling until on-device deep mode
clears the sealed Stage-1 run.*
