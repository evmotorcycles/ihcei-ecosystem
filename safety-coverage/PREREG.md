# Pre-registration — how often the safety warning fires when it should

**SHA-256 locked in `prereg.lock.json` BEFORE the lexicon was changed and BEFORE
the sealed set was scored.** Re-verified by `test_coverage.py`.

---

## The defect this is about

Cairn shows a warning when a claim touches a domain where being *well-written*
and being *safe* are different things — health, chemicals, money, law, physical
safety. It is the single most consequential thing on the screen, because it is
the moment the tool tells a person to stop trusting it.

A spot check on ten realistic health texts found **7 with no warning at all**,
including an infectious-disease outbreak report mentioning deaths.

The lexicon fires on *clinical* vocabulary — dose, mg, patient, diagnosis,
therapy — and misses **infectious disease, outbreaks, mortality, oncology and
vaccination** entirely. That is most of the health information ordinary people
actually forward to each other.

---

## Why this needs a pre-registration at all

The obvious move is to add the missing words until the ten examples pass. That
produces a lexicon tuned to ten sentences and a coverage number that means
nothing.

So the corpus is split before anything is changed:

| Set | N | Used for |
|---|---|---|
| **DEV** | 40 | May be inspected. The lexicon may be written against these. |
| **SEALED** | 40 | **Not inspected while editing the lexicon.** Scored once, at the end. |
| **CONTROL** | 30 | Texts that must **not** trigger a warning. Guards against fixing coverage by flagging everything. |

Assignment is deterministic: `sha256(text)` first hex digit — `0-7` → DEV,
`8-f` → SEALED. No shuffle, no seed to re-roll, and anyone can recompute which
set a sentence landed in.

---

## Pre-registered predictions

- **S1 — the baseline is bad.** On the SEALED set, the *current* lexicon misses
  **more than 40%** of texts that should warn.
  *Falsified if* it misses 40% or fewer, in which case the spot check was
  unrepresentative and this whole module is unnecessary.

- **S2 — the revised lexicon transfers.** After revision written against DEV
  only, the SEALED miss rate falls **below 20%**.
  *Falsified if* it stays at or above 20% — meaning the revision memorised DEV
  and did not generalise, which is the failure this split exists to detect.

- **S3 — precision does not collapse.** On the CONTROL set, **at most 10%** of
  texts that should not warn do warn.
  *Falsified if* more than 10% false-fire. A warning that appears on everything
  is a warning nobody reads, and buying recall with precision is not a fix.

- **S4 — the improvement is not an artefact of the split.** Baseline and revised
  miss rates are reported for DEV and SEALED **separately**. If SEALED is much
  worse than DEV, the gap is reported as overfitting rather than smoothed into a
  single average.

**No threshold above will be altered after the results are seen.** If S2 fails,
the revision is reported as insufficient and the miss rate stands as measured.

---

## What this does not claim

1. **A warning is not a safety assessment.** Firing means "this touches a domain
   where structure is not safety". It says nothing about whether the content is
   correct or dangerous.
2. **A lexicon is not comprehension.** This is word matching. It will miss any
   phrasing nobody thought of, and the sealed miss rate is a floor on that, not
   a ceiling.
3. **Coverage on a written corpus is not coverage in the world.** The corpus was
   written by one author for this test. Real user text will differ, and a real
   evaluation needs text people actually pasted.
4. **This does not make Cairn safe to rely on for health decisions.** It makes
   the tool more likely to say so. Those are different things.
