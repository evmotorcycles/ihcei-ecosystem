# Novora PAGES — provenance & attestation for generative media

*A generated podcast or video is a flat file: you can't pause a spoken sentence
and trace it to the source, and you can't tell if the audio was spliced. PAGES
binds a transcript to its sources so every spoken claim is falsifiable in one
tap, and any edit to the stream is detectable at the exact timestamp.*

## What it is

PAGES wraps a generated transcript (before it becomes audio/video) in two tested
structures, reusing the same primitives as the rest of the stack:

- **Temporal hop chain** — each segment `t` is hash-chained to `t-1` over its
  content + metadata (`hash_t = SHA-256(contentHash_t ‖ meta_t ‖ hash_{t-1})`).
  Editing a spoken claim or splicing the stream breaks the chain **at the exact
  timestamp**.
- **Tap-to-source (Merkle)** — the grounding passages form a Merkle tree; each
  segment carries an inclusion proof of its passage, so one tap shows the
  un-mutated source **and proves it's the one committed** in the published root.

Each segment is also audited two ways: **manipulation** (the NERE `consumer-v1`
gate, catching coercion inside synthesized speech) and **grounding** — fast mode
is on-device lexical alignment (word-overlap + fabricated-number detection);
deep mode is the **Gemini grounding hop** (`api/gemini-ground.js`), invoked only
on the ambiguous middle. Non-suppressive: verdicts ride alongside; the listener
decides.

## Results — tested on real open-source data

`node pages/field_test.mjs` (assertions: `pages.test.mjs` **14/14**). The
grounding sources are **real prose sentences from the Express.js README** (fetched
live); a generated "podcast" transcript is built over them with three grounded
segments, one hallucinated statistic, and one manipulation:

| time | grounded | p_align | verdict | spoken segment |
|---|---|---|---|---|
| 00:00 | ✅ | 0.909 | PASS | "create a package.json first using npm init" |
| 00:08 | ✅ | 0.980 | PASS | "Express does not force any specific ORM or template engine" |
| 00:15 | ✅ | 0.875 | PASS | "if you discover a security vulnerability, follow the security policies" |
| 00:23 | ❌ | **0.143** | PASS | "Express is **47%** faster than every framework" — *fabricated stat* |
| 00:30 | ❌ | 0.020 | **BLOCK** | "don't tell your team, wire the license fee now" — *manipulation* |

- **Grounding surfaces the hallucination:** the fabricated "47%" (a number in no
  source) drops to `p_align 0.143` — the classic media hallucination the listener
  would otherwise swallow whole.
- **Manipulation inside speech is caught** by the same NERE gate (00:30 → BLOCK).
- **Tap-to-source proves inclusion:** tapping 00:08 returns the un-mutated Express
  passage with a Merkle proof; a fabricated passage the author never wrote **fails
  inclusion** against the root.
- **Tamper-evidence:** flipping "follow" → "ignore" the security policies at 00:15
  makes `verify()` return **broken at 00:15 ("spoken text altered")**; splicing out
  a segment or rewriting a stored verdict is likewise caught. A normal `.mp3`/`.mp4`
  carries no such chain — the edit would play as authentic.

## The Gemini grounding hop (`api/gemini-ground.js`)

The deep-mode fidelity check runs in project-6q4gj on Vercel (where the Gemini
key and egress live). GET-testable:

```
GET /api/gemini-ground?health=1      -> { ok, keyConfigured, model }
GET /api/gemini-ground?test=1        -> runs a grounded + a hallucinated case live
GET /api/gemini-ground?source=…&claim=…  -> { grounded, p_alignment, reason }
```

It asks Gemini whether a CLAIM is fully supported by a SOURCE and returns a
calibrated `p_alignment`. Fast mode (on-device, `$0`) handles the clear cases;
this paid semantic hop resolves the ambiguous middle — the same fast/deep economics
as the rest of the stack.

## What PAGES solves

- **The black-box podcast:** every spoken claim is grounded-checked, so fabricated
  statistics are surfaced instead of trusted.
- **Deepfake / splice armor:** the hash chain makes any edit to the stream
  detectable at the timestamp; an un-attested stream is flagged as uncertified.
- **Provenance in one tap:** a claim traces to its exact source passage with a
  cryptographic inclusion proof — bringing academic rigor into the consumption flow.

## Honest scope

- **Real and tested:** the temporal hop chain, tap-to-source Merkle proofs,
  grounding audit (fast), manipulation audit, and tamper/splice detection — on
  real Express.js source data, 14/14.
- **Fast-mode grounding is lexical:** overlap + fabricated-number detection catches
  the common cases; genuine semantic paraphrase-vs-distortion is the Gemini hop's
  job, and reworded manipulation is the same fast-mode ceiling as elsewhere.
- **Not built here (design, per the memo):** spread-spectrum audio watermarking
  into real codecs, MPEG-4 timed-metadata muxing, and the player UI. PAGES here is
  the provenance/attestation *engine* and its contract, not a media muxer.
