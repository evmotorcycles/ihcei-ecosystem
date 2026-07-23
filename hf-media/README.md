# Novora PAGES governance — real Hugging Face video/audio generation cohort

**One command:** `node hf-media/run_media_governance.mjs` · offline · `$0` · no model download

This runs the **real Novora governance stack** — PAGES, HELM/EI, Echo, Page Code, Agency
Internet — over a frozen cohort of **19 real, most-liked open-source generative-media tools**
on the Hugging Face Hub (text-to-speech, text-to-audio, text-to-video, image-to-video). It
is pre-registered and SHA-256-locked *before* it runs.

Generative media is exactly where a listing-governance stack earns its keep: **voice
cloning** enables impersonation, **video generation** enables synthetic footage, and
licenses split three ways — permissive, non-commercial, and use-restricted (RAIL). This
experiment shows the stack producing **calibrated, tamper-evident telemetry** on those
distinctions — not a verdict that any tool is "good" or "bad."

---

## The cohort (real, then frozen)

Fetched live from the HF Hub through the MCP connector (authenticated user `Mago1234`,
filters `text-to-speech` / `text-to-audio` / `text-to-video`, sorted by likes), then
**frozen** to `data/hf_media_cohort_frozen.json` for offline reproducibility. Names you'll
recognize: `Kokoro-82M`, `coqui/XTTS-v2`, `Dia-1.6B`, `microsoft/VibeVoice-1.5B`,
`sesame/csm-1b`, `tencent/HunyuanVideo`, `Wan2.1-T2V-14B`, `stable-audio-open-1.0`,
`genmo/mochi-1-preview`, `AnimateDiff-Lightning`, and more. Each record carries `modality`,
`task`, `license`, `arxiv`, `eval_results`, `base_model`, and capability `flags` — all
transcribed verbatim from the live tag lists.

| artifact | SHA-256 |
|---|---|
| `prereg/hf_media_prereg.json` (spec) | `ee6195d3add8705df45be2ee936ca27e1331607e91e7f880111c79c6f9207922` |
| `data/hf_media_cohort_frozen.json` (fixture) | `3885e06905d1d067fc07b63fa3376464711835ac7c242d213dfaa252d46a5909` |

The runner re-verifies both hashes before scoring; if either drifts, it refuses to run.

---

## Locked decision rules (fixed before running)

- **License class.** `clear` = `apache-2.0`/`mit`; `non_commercial` = `cc-by-nc-4.0`;
  `use_restricted` = `creativeml-openrail-m` (RAIL); `ambiguous` = `other`/`null`.
- **Voice-cloning flag.** For audio tools, `voice-cloning` is treated as an
  *impersonation-relevant safety attribute to surface for review* — **not** a defect.
- **PAGES grounding signals.** mean of `[clear_license, arxiv, eval_results, base_model]`.
- **`media_flag`.** `FLAG` if voice-cloning **and not** clear license (impersonation under
  ambiguous/restricted terms); `REVIEW` if voice-cloning **or** non-clear license **or**
  preview; else `PASS`.
- **Page Code publish-allow.** allow **iff** clear license **and** grounding ≥ 0.5 **and**
  `media_flag ≠ FLAG`; else deny (needs human review).
- **Echo tamper.** flipping one byte of one record must change the Merkle root and locate
  the tampered record.

---

## Measured result (GREEN, honest)

```
N = 19   (10 audio / 9 video)

PAGES mean grounding ......... 0.490   ← uniformly low, and that's the honest finding
voice-cloning capable ........ 3 / 19  (16%) — surfaced for review
license  clear / non-comm / use-restricted / ambiguous  =  8 / 2 / 1 / 8
media_flag  PASS / REVIEW / FLAG  =  6 / 11 / 2
Page Code publish-allow ...... 4 / 19  (21%) — only permissive + grounded + non-FLAG

Echo: 19 records hash-chained; single-byte tamper CAUGHT and LOCATED; root restored ✓
Agency Internet: 3 real base_model lineage edges (revocable delegation)
```

**Two honest findings worth stating plainly:**

1. **PAGES does not discriminate here — and we report that, not hide it.** PAGES scores
   card *prose* for grounding (methodology, `N=`, metrics). Tag-level HF metadata has none
   of that, so every media card reads as "partially grounded" (~0.49). The discriminating
   signal comes from **HELM + Page Code**, not PAGES. A governance stack that pretended
   PAGES was doing the work here would be dishonest.
2. **Trending ≠ safe ≠ permissive.** 8 of 19 of the most-liked media tools carry
   ambiguous/`other`/`null` licenses; 3 are voice-cloning capable; only 4 clear the
   full publish gate. Two voice-cloning tools under ambiguous terms (`XTTS-v2`,
   `chatterbox`) are `FLAG`-ed for impersonation risk. One voice-cloning tool with a
   *permissive* license and a cited paper (`Qwen3-TTS`) is publish-allowed **but** carried
   as `REVIEW` — a calibrated middle, not a blanket ban.

---

## What this does and does not claim

- ✅ Governance/audit **telemetry** over generative-media card metadata, from the real stack.
- ❌ **Not** a claim that the stack improves generation quality, and **not** a safety verdict
  on any listed tool. The `voice-cloning` flag is surfaced as an attribute to review.
- ❌ **LMD and LISM's `E = U·D` are deliberately NOT applied** to this metadata — there is no
  measured spacetime observable and no independent per-tool viability outcome. Forcing them
  would be dishonest. Those laws are validated separately (`physics-agency/lmd`,
  `lism-cohorts`, `biorxiv-lism`). The `base_model` lineage is used only for the
  Agency-Internet revocation demo (no coupling claim).

## Files

```
hf-media/
  prereg/hf_media_prereg.json        pre-registration spec (locked)
  prereg/MANIFEST.sha256.json        spec + fixture hashes
  data/hf_media_cohort_frozen.json   19 real media tools (frozen)
  run_media_governance.mjs           the runner (real modules, offline)
  hf_media.test.mjs                  node:test guard
  results_media.json                 emitted results
```

Run the guard: `node --test hf-media/hf_media.test.mjs` · or the whole stack:
`bash reproduce_all.sh`. Layer-1 governance telemetry, offline, `$0`.
