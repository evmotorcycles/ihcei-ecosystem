# Testable textual claims — what a dataset can and cannot settle

**One command:** `python3 text-channel/text_channel.py` · stdlib · offline · `$0`

---

## The task, and what had to change about it

The request was: *"using datasets, prove that the Quran is a governance manual and
communication channel."*

**A design that sets out to prove a conclusion is not a test.** It has no state in
which it returns "no". So the request was converted into the only form that can
carry evidence — specific claims, stated and hash-locked in advance, that could
come back negative. Three did. One came back positive, and it is weaker than it
looks.

---

## Results

| Claim | Verdict | Why |
|---|---|---|
| **1. Orthographic partition** | **UNTESTABLE** | N = 7 total instances |
| **2. Directed transmission vs unmarked arrival** | **SUPPORTED, marginally** | diff 0.1534 vs a 0.15 gate; p = 0.0001 |
| **3. Adversarial vs stabilising vocabulary** | **NOT OPERATIONALISED** | choosing the word lists chooses the answer |

---

## Claim 1 — the orthographic partition is untestable, and that is the finding

The claim is that the preposition-plus-noun form `b-s-m` splits into two channels,
one written without the connecting *alif* and one with it.

It does split. Here is every instance in the text:

| Form | N | Locations |
|---|---|---|
| alif-omitted | **3** | 1:1, 11:41, 27:30 |
| alif-retained | **4** | 56:74, 56:96, 69:52, 96:1 |

**Total N = 7.**

A 3/4 split of seven items cannot be statistically distinguished from any other
narrative partition of seven items. Any story told over these seven will fit —
including contradictory ones. This is a statement about **sample size**, not about
whether the claim is true. The claim may well be right; there is simply no way to
find out from seven data points.

**One thing the run surfaced that the proposal had not:** the proposal named five
of the seven instances. It did not mention **11:41** (alif-omitted) or **69:52**
(alif-retained). A claim about a seven-item partition that leaves out two of the
seven has not yet been checked against its own data.

To make this testable you would need an independent, pre-declared coding of what
each channel predicts, applied by coders blind to the orthography. Even then,
N = 7 caps the achievable evidence at anecdote.

---

## Claim 2 — the one real test, and its fine print

Two arrival-verb families are said to differ: family **A** marks directed delivery
of a specified payload; family **B** (Form I) marks unmarked arrival. If so, A
should co-occur with payload vocabulary more often than B.

Payload lexicon and verb forms were **declared and hash-locked before the
statistic was computed**.

```
family A verses            355   mean length 17.77 words
family B verses (Form I)   280   mean length 17.14 words
Form IV (the giving-verb)  247 verses EXCLUDED, declared in advance
both-family verses         24 dropped as ambiguous

payload rate A             0.5606
payload rate B             0.4071
difference (A − B)         0.1534
permutation p (two-sided)  0.0001      10,000 shuffles, seed 42
length-adjusted per 10 wds A 0.4865  vs  B 0.2917

GATE (locked in advance)   SUPPORTED if diff ≥ 0.15 and p < 0.01
VERDICT                    SUPPORTED
margin over the gate       +0.0034
```

### Read the margin before you read the verdict

The verdict was decided by **0.0034**. Had the pre-registered effect-size gate
been 0.16 instead of 0.15, this would read INCONCLUSIVE. The gate was **not**
moved — but a result that turns on the third decimal place is not a clean win, and
presenting it as one would be the exact failure this project exists to refuse.

### We tried to break it — leave-one-out on the payload lexicon

Post-hoc, not pre-registered. Legitimate precisely because it can only *weaken*
the result: it is an attempt to break our own finding, not to rescue it.

| Term dropped | Difference | p | Still clears the gate? |
|---|---|---|---|
| book/scripture | +0.1600 | 0.0000 | yes |
| clear-proof | +0.1309 | 0.0012 | **no** |
| messenger | +0.1426 | 0.0006 | **no** |
| knowledge | +0.1614 | 0.0000 | yes |
| guidance | +0.1534 | 0.0001 | yes |
| sign/verse | +0.1497 | 0.0002 | **no** |
| wisdom | +0.1613 | 0.0000 | yes |
| reminder | +0.1467 | 0.0002 | **no** |
| truth-claim | +0.1384 | 0.0005 | **no** |
| command | +0.1726 | 0.0000 | yes |

**Removing any one of 5 of the 10 payload terms drops it below the gate.**

> **Honest summary: the direction is robust, the magnitude is marginal.**
> Family A leads in all ten variants, every p ≤ 0.0012 — so *something* is there
> and it is not noise. But the SUPPORTED label depends on the exact ten words we
> chose, and a reasonable researcher choosing nine of them would have written
> INCONCLUSIVE.

The length confound was checked, not assumed away: the two groups are within
0.63 words of each other on average, and the difference survives per-word
adjustment.

### What this result licenses

- **It shows:** in this text, one arrival-verb family co-occurs with payload
  vocabulary more than another, beyond what label-shuffling produces.
- **It does not show:** that the text is a governance manual, that it is a
  communication channel in any engineering sense, or anything about its origin.
  Those are not statements a lexical co-occurrence statistic can reach.

---

## Claim 3 — not operationalised, and why that is the honest answer

The proposal asks for a map of "toxic" adversarial words against "stabilising
anchors".

**Deciding which words are toxic *is* the claim.** A researcher who picks the word
lists picks the result, and there is no independent criterion available here to
pick them with. Building one after seeing the text would be circular.

Reported as **not tested**. A version that could work needs word lists produced by
coders blind to the hypothesis, with inter-coder agreement reported before any
analysis. That is a real study. A text-matching script is not a substitute for it.

---

## The boundary that matters most

The proposed design draws on four datasets, three of which measure **networks** —
yeast interactomes, software repositories, agent swarms, institutional registries.

> **No measurement of a protein interactome can license a claim about the status,
> authorship or purpose of a text.**

Confirming `E = U·D` in yeast a thousand times over says exactly nothing about any
book. This is a category error, and it is the largest weakness in the design as
proposed. The network results in this repository are real and they are good; they
are simply about networks.

Even the *textual* result above only reaches structure. **Structure is evidence
about a text; purpose is a claim about an author.** No dataset crosses that gap.

---

## Availability audit — proposed vs what exists

Recorded before any synthesis, so the gap is on the record.

| Proposed dataset | Status here |
|---|---|
| Cohort A — yeast interactome, N=4,825 | **REAL**, committed, VIF 1.0026 |
| Cohort B — GitHub repositories, N=992 | **REAL**, committed, independently re-analysed |
| Cohort C — knowledge network, N=793 | rows committed; **originally retracted as synthetic** |
| Cohort D — agent swarm, N=500 | **SELF-DECLARED SIMULATION**, `real_world_evidence: false` |
| Clinical registry, N≥1,000 | **does not exist here** |
| Legislative registry, N≥5,000 | **does not exist here** |
| Judicial database, N≥100,000 | **does not exist here.** The cited 118,443-case result and its "1.24× citation premium, p≈0" are **not backed by any committed data in this repository** |
| HELM agency logs | mechanism exists; **no longitudinal user data collected** |

Cohort D is the sharpest case. The 39-hop fidelity decay from 0.84 to 0.01 is
frequently cited as showing something about real agent swarms. It is a **seeded
simulation**. The repository's own audit says it in terms: *a seeded simulation
reproducing itself is a code-correctness check, not empirical support for the
law.* Citing it as evidence about real systems would repeat precisely the error
the N=793 retraction was issued for.

---

## Provenance

| | |
|---|---|
| Corpus | Tanzil Uthmani text, from the `pyquran` PyPI package |
| Integrity | MD5 `6aae945d…ab518`, matching the publisher's own checksum file shipped beside it |
| Shape | 114 sections, 6,236 verses, verified on parse |
| Committed | yes — every number recomputes from a clean clone, no network |

The corpus is committed for the same reason the N=992 rows had to be: a result
that exists only on the machine that produced it is not a reproducible result.

---

## Method limits, stated rather than discovered later

1. **Surface-form matching is not morphological parsing.** Matching over
   un-lemmatised text misses forms and admits false positives. This limits
   precision and is not claimed away.
2. **The lexicon is a choice.** A different payload list gives a different answer,
   as the leave-one-out table shows directly.
3. **Co-occurrence is not semantics.** Two words in one verse is not evidence that
   one governs the other.
4. **One text, one translation-free analysis.** There is no comparison corpus, so
   nothing here says whether this pattern is unusual among texts of this kind.
   That absence is a real limit on interpretation: *no control corpus was
   analysed.*

Limit 4 is the one that most constrains the result. Establishing that a pattern is
**distinctive** requires showing that comparable texts lack it. That study has not
been run.

---

## Reproduce

```bash
python3 text-channel/text_channel.py           # the full pre-registered run
python3 -m pytest -q text-channel/             # 16 guards, including the fragility
```

The guards lock the untestable and not-operationalised verdicts as hard as the
positive one. Nulls are results here, and they are held in place by tests so they
cannot quietly disappear from a later summary.
