# The OQM Lexical Screen — an instrument that can say no

**Spec** `8257dfcca40d0be024bac323e45137eba27277200243b3c1a7893d6f08349204` · **4/5** ·
[Artifact](https://claude.ai/code/artifact/d32c34a8-ab4b-4407-831e-21f399b8e94c)

```bash
python3 -m pytest -q quran/test_oqm_screen.py
```

Not another reading. A **reusable screen** for questions of the shape *"is this word a label
or an act?"* — applied uniformly to a whole vocabulary, with a decision boundary fixed before
any term was scored, and required by its own gate to be capable of disagreeing with the
framework that built it.

## Built from the test that worked

| Candidate | Calibration result | |
|---|---|---|
| **Designation** — does the text name a group with a finite verb? | 7 of 7 control proper nouns scored **zero** | **kept** |
| **VIF on word counts** | **99.8%** of random unrelated pairs cleared its bar — separated nothing | **discarded** |

## Calibrated at both ends

```
  negative controls  Firʿawn, Thamūd, ʿĀd, Isrāʾīl, Majūs, Rūm, Quraysh     all 0
  positive controls  kafarū 171 · ʿamilū 58 · ẓalamū 33                     all ≥ 20
  separation                                                                33
```

Boundary fixed in advance: **< 5 = LABEL**, **5–19 = AMBIGUOUS**, **≥ 20 = ACTION**.

## The vocabulary

| Term | Designations | Class |
|---|---:|---|
| āmanū / muʾmin | **268** | ACTION |
| ittaqaw / muttaqīn | 27 | ACTION |
| hādū / yahūd | 10 | ambiguous |
| ashrakū / mushrikūn | 9 | ambiguous |
| ṣabarū / ṣābirūn | 6 | ambiguous |
| naṣārā | 2 | **LABEL** |
| nāfaqū / munāfiqūn | 2 | **LABEL** |
| aslamū / muslim | 1 | **LABEL** |
| ḥawāriyyūn | 0 | **LABEL** |
| ṣābiʾīn | — | **UNTESTABLE** |

**X6 passed:** five of ten come back LABEL, including **muslim** and **munāfiqūn**. A gate
was written specifically to catch a screen that certifies everything its author hoped for. Had
it returned zero LABELs, the verdict would have been *"this screen is broken"* — not
*"the framework is confirmed"*.

## X1 failed, and that produced a scope condition

**ṣābiʾīn cannot be screened at all** — its root supplies no attested finite verb. That is
**untestable-here, not label**. *Naṣārā* and *ḥawāriyyūn* score zero *despite* their roots
having verbs (82 finite tokens for N-Ṣ-R). The screen now carries a stated precondition:
**the root must supply an attested finite verb.**

## Three defects, all caught by the calibrators

1. **The clitic stripper ate a first radical.** `كفروا` begins with *kāf*, also the "like/as"
   proclitic — *kafarū* became *farū* and scored **3** instead of **171**.
2. **The ḥawāriyyūn forms missed the attested `يُحَاوِرُهُۥ`.**
3. **`وَعَمِلُوا۟` carries the conjunction inside the token** — *ʿamilū* scored **8** instead of
   **58**. Fixed with a **uniform proclitic rule applied to every term and every control**.

Each fix changed the instrument. **None changed a threshold.**

## What an ACTION classification does not buy

It does not vindicate a reading — it establishes that the text uses a verbal group-designation,
a far smaller fact. It says nothing about meaning (many ordinary group-names are historically
deverbal in every language), and nothing about any living community.
