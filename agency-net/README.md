# The Agency Internet (AIPS) — a working reference layer

*What it is, what it solves that the normal internet cannot, and the results of
testing it on real open-source traffic. Scope is marked throughout: the code
here is real and tested; the router-firmware / telecom deployment is design.*

## The one-sentence version

The normal internet proves the *bytes* arrived intact and the *pipe* was private,
then hands the human the raw message and attests **nothing about its meaning**.
AIPS is the missing layer: as a message crosses the network, each node attaches a
**signed, non-suppressive verdict** about whether it is manipulation, and the
receiver can **cryptographically verify the whole path** — without any node ever
dropping or rewriting the content.

## What today's internet does — and the gap

| Concern | TCP/IP + TLS today | The gap |
|---|---|---|
| Did the bytes arrive intact? | ✅ checksums | — |
| Was the pipe private? | ✅ TLS | — |
| Is the *message* trying to manipulate the human? | ❌ nothing | the receiver is handed a scam and a genuine alert **identically** |
| Can the receiver prove what each hop concluded? | ❌ nothing above transport | an intermediary can rewrite meaning invisibly |
| May this agent take this action on my behalf? | ❌ no concept of who-may-do-what | an agent with the packet can do anything the packet allows |
| Is the service/dependency I'm talking to actually maintained? | ❌ a dead repo routes like a live one | no health signal reaches the receiver |

AIPS fills exactly those four empty rows, reusing the primitives this repo
already ships and tests (the gated NERE kernel, the SHA-256 wallet, the
delegation table, the capacity meter).

## The five layers (L1 is inherited, L2–L5 are the tested code here)

```
 L5  Capacity synthesis   receiver-side capacity meter (are you growing or being hollowed?)
 L4  Delegation control   default-deny, stake-capped, revocable grants — "OAuth of agency"
 L3  Trust attestation    the HOP ENVELOPE: a SHA-256 chain of each node's verdict
 L2  Cognitive audit      the gated kernel (enterprise-v1 gateways / consumer-v1 devices)
 L1  Shannon substrate    Wi-Fi / fiber / LTE — inherited, not reimplemented
```

The load-bearing new object is **L3, the hop envelope** (`aips.mjs`): a message
carries `content_sha256` and a chain of hop records, each
`hash = SHA-256(prev_hash + canonical(record) + content_sha256)`. Because the
content hash is folded into every link, both *in-flight payload mutation* and
*retroactive verdict rewriting* break the chain at the exact hop — and the
receiver detects it with `verifyPath()`.

## Results — tested on real open-source traffic

`node agency-net/field_test.mjs` (assertions: `aips.test.mjs`, **14/14**). All
benign inputs are real, live-fetched (the same registry corpora as the OSS field
trial); threats are injected and labeled; the τ_v cohort is a live response from
the deployed project-6q4gj GitHub API.

1. **Same scam, both networks.** TCP/IP delivers it raw. AIPS attaches a verdict
   at every hop and it **escalates down the path**: WARN at the enterprise
   gateways (p≈0.71), **BLOCK at the receiver's consumer-lexicon device**
   (p≈0.98) — the message meets its strongest judge exactly where it lands.
2. **Silence on real traffic — 281/281 (100%).** The network raises zero chips on
   real registry descriptions. A wire that cried wolf would be switched off; this
   one carries ordinary traffic invisibly. (Prose floor — see the field-trial
   caveats; live dialogue is still untested.)
3. **Threats surfaced in-band — 3/4.** Token-phish, fake advisory, and consensus
   pressure are all surfaced; the fourth (a reworded supply-chain PR) slips fast
   mode — the **documented evasive ceiling**, deep mode's job, not a silent
   failure of the design.
4. **Tamper located, which TCP/IP cannot do.** A relay that swaps the payload
   after attestation, or rewrites a past BLOCK to PASS, is caught at the exact
   hop. The bytes re-checksum fine and would arrive "valid" on the normal
   internet; AIPS breaks the chain.
5. **Agency boundaries enforced.** An agent's `publish` within its stake cap is
   allowed; over-cap and ungranted-destructive actions are denied by default.
   The normal internet routes all three identically.
6. **Network-health telemetry.** The live τ_v cohort flags the saturating-queue
   "zombie" dependencies (moment 88d, lodash 114d, request 251d) that a normal
   network delivers exactly like a healthy one (svelte 2.6d).

## What it's solving, in one line

The internet was built to move **bits** and it is superb at it. The agentic era's
scarce good is not bandwidth but **preserved human agency** — and that needs a
layer that makes manipulation *visible*, history *unforgeable*, and delegation
*bounded*, without ever becoming a censor. AIPS is that layer, non-suppressive by
construction (no node drops or mutates content; the verdict rides alongside and
release stays with the receiver).

## Honest scope

- **Real and tested (this directory):** the hop envelope and path verification,
  the multi-node relay, tamper detection, delegation enforcement, and the audit
  verdicts — all running on real data, 14/14 assertions, reusing primitives with
  100 JS + 86 Python assertions behind them.
- **Design, not built:** AIPS running inside Wi-Fi router firmware, "cognitive
  friction injection" at the transport level, and adoption as a ubiquitous
  standard. Those are architecture claims, plausible by analogy to OS/network
  history but empirically conditional on adoption — marked as such, not asserted.
- **Inherited caveats:** the 100% silence is on prose-like traffic; evasive
  coercion is fast mode's ceiling until on-device deep mode clears the sealed
  Stage-1 run.
