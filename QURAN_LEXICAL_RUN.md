# yahūd and naṣārā: label or descriptor?

**Spec** `708ac80e3b14096c0eee90df0eae918596c565d78f005541c06b5dd1111fb6aa` · **5/6** ·
[Artifact](https://claude.ai/code/artifact/67107d23-c3b8-4c3f-9c11-92a923ee7b0f)

```bash
python3 -m pytest -q quran/test_qlex.py
```

Dataset: 6,236 ayahs, committed at `data/quran/The_Quran_Dataset.csv`
(sha256 `7312b6b220e192ba9ebd02c0c4221ba76c35c69fcea18ae9d306ee20413fcb41`).

## Two limits, stated as gates rather than footnotes

- **V8 — it does not establish what the words mean.** Many ordinary ethnonyms are
  historically deverbal in every language. A pass is *consistent with* a descriptor reading
  and does not select it. `UNTESTABLE-HERE`
- **V9 — it is not a claim about any living community.** The units of analysis are Arabic
  word-forms in one text. `OUT OF SCOPE BY CONSTRUCTION`

## Why "shares a root with a verb" was not the test

`عَاد` (ʿĀd, the tribe, 26 ayahs) is surface-identical to `عَادَ` *ʿāda* "he returned"
(root ʿ-W-D, 2:275) **and** to `عَاد` *ʿādin* "transgressor" (root ʿ-D-W, 2:173). A
shared-letters test would call a proper noun deverbal.

**The test used instead:** does the text *designate the group* with a finite verb — a
relative clause "those who [verb]" or a vocative "O you who [verb]"? A proper noun cannot be
conjugated to name its own bearers.

## Result

| | noun | named by a finite verb |
|---|---:|---:|
| **yahūd** | 8 | **10** — incl. vocative *yā ayyuhā alladhīna hādū* (62:6) |
| **naṣārā** | 14 | **0** |
| 7 control proper nouns | — | **0** (Firʿawn, Thamūd, ʿĀd, Isrāʾīl, Majūs, Rūm, Quraysh) |

The verbal designation of *yahūd* is **commoner than the noun**. The ablation held 7/7, so
the behaviour discriminates.

## V4 failed, and it is the sharpest part

The pre-registered prediction was that *naṣārā* is never verbally designated. Two hits came
back: **8:72 and 8:74**, `وَالَّذِينَ آوَوا وَنَصَرُوا` — "those who sheltered and helped."

Those name the **Anṣār**, a *different group*. The matcher cannot resolve referents, so the
gate is **scored failed as measured** — a gate is not re-scored after the fact.

The substance is sharper than a pass: the root supplies **82** finite verbs and *anṣār* **11**
times, so the machinery for a "those who did X" designation is present and used — just never
for the *naṣārā*.

> **A single claim covering both words is not supported.** Stating them together would hide
> the asymmetry that is the actual result.

## Two specific claims, both hold

- **M-L-L verbal usage is confined to 2:282** — three finite tokens, none elsewhere in 6,236 ayahs.
- **2:120 uses a singular `مِلَّتَهُمْ` while naming both groups.**

## Where the difficulty actually was

Not statistics — spelling. The dagger alif (U+0670) is a long vowel and must become an alif;
a dagger alif *after* alif-maqsura is that letter's own vowel and is not an extra letter; and
combining marks must be stripped by Unicode category, because a hand-written range missed
U+064B–U+0652 and silently corrupted every count in the first attempt.

**Admitted weakness:** V2's threshold (≥ 5) was set after the count of 10 was seen during
normalisation, so the primary is a *weak* pre-registration. V3 and V4 were not, and they
carry the run.
