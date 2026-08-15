# Pre-registration — testable textual claims in the OQM channel model

**Locked by SHA-256 in `text-channel/prereg.lock.json` BEFORE the test statistics
in Section C were computed.** The lock is re-verified by `test_text_channel.py`.

---

## 0. What this study is, and what it refuses to be

The task that produced this module was phrased as: *"prove that the Quran is a
governance manual and communication channel."*

**A design that sets out to prove a conclusion is not a test.** It has no state in
which it returns "no". So the request has been converted into the only form that
can carry evidence: **specific textual claims, stated in advance, that could come
back negative.**

Three boundaries bind everything below, and they are not modest framing — they are
the load-bearing limits of what any dataset can do here.

**Boundary 1 — the category boundary.**
Datasets 2–4 of the proposed design (yeast interactomes, software repositories,
knowledge networks, agent swarms, institutional registries) measure **networks**.
Whatever they show is a fact about networks. **No measurement of a protein
interactome can license a claim about the status, authorship or purpose of a
text.** That inference is a category error, and it is the single largest weakness
in the design as proposed. Confirming `E = U·D` in yeast a thousand times over
says exactly nothing about any book.

**Boundary 2 — the direction boundary.**
Even a *perfect* result on every test below would license only: "this text
exhibits statistical structure consistent with a directed-transmission
distinction." It would **not** license "therefore it is a governance manual",
because many texts exhibit lexical structure, and structure is not purpose.
Structure is evidence about a text; purpose is a claim about an author.

**Boundary 3 — the terminology boundary.**
Per standing instruction, the interpretive vocabulary of the source framework is
kept out of the hypotheses. The Arabic text is used **as data**, because the
orthographic claims are claims about Arabic script and cannot be tested without
it. The hypotheses are stated in functional terms only. Layer-1 (what was
measured) never mixes with Layer-3 (what it might mean).

---

## A. Corpus

| | |
|---|---|
| Source | Tanzil Uthmani text, distributed inside the `pyquran` PyPI package |
| File | `text-channel/data/quran-uthmani.xml` (1,522,037 bytes) |
| Integrity | MD5 `6aae945d556a1b28cfe682c0ea5ab518`, matching the publisher's own `quran-uthmani-md5.txt` shipped alongside it |
| Structure | 114 sections, 6,236 verses, verified on parse |

The corpus is **committed**, so every number below recomputes from a clean clone
with no network. This is the standard the N=992 cohort had to meet, and it applies
here identically.

---

## B. Claim 1 — the orthographic partition · **DESCRIPTIVE ONLY, NOT A TEST**

The proposed design claims that instances of the preposition-plus-noun form
`b-s-m` split into two channels — one written without the connecting *alif*
(claimed: worldly, unfiltered) and one written with it (claimed: purified,
elevated).

**This was counted before this file was written, so it carries no confirmatory
weight and is recorded as description.** The counts are:

| Form | Count | Locations |
|---|---|---|
| alif-omitted `بِسْمِ` | **3** | 1:1, 11:41, 27:30 |
| alif-retained `بِٱسْمِ` | **4** | 56:74, 56:96, 69:52, 96:1 |

**Finding, stated in advance of any interpretation: N = 7 total.**

A partition of seven items into a 3/4 split cannot be statistically distinguished
from any other narrative partition of seven items. There is no test with power
here — not because the claim is false, but because **seven data points cannot
support an inference about two semantic channels.** Any story told over these
seven will fit, including contradictory stories.

Two locations are also worth recording because the proposed design named only five
of the seven: **11:41 is alif-omitted** and **69:52 is alif-retained**. A claim
about a 7-item partition that omits 2 of the 7 items has not yet been checked
against its own data.

**Pre-registered position: Claim 1 is UNTESTABLE at this N and is reported as
untestable.** No amount of interpretation changes the sample size. If the claim is
to become testable it needs an independent, pre-declared coding of what "worldly"
and "purified" predict — applied by coders blind to the orthography — and even
then N=7 caps the achievable evidence at anecdote.

---

## C. Claim 2 — directed transmission vs unmarked arrival · **GENUINE TEST**

This is the one claim in the proposed design with enough data to be falsifiable.

### The claim, in functional terms
Two arrival-verb families are said to differ in function: family **A** (root
`j-y-'`) is claimed to mark **directed delivery of a specified payload to a
specified audience**; family **B** (root `'-t-y`, Form I) is claimed to mark
**unmarked arrival or appearance** without a payload.

If true, verses containing family A should co-occur with payload vocabulary at a
**higher rate** than verses containing family B.

### Surface forms (declared before computing anything)

- **Family A** — `جَآء`, `جَاء`, `جِئ`, `يَجِيء`, `تَجِيء`, `نَجِيء`
- **Family B, Form I only** — `أَتَىٰ`, `أَتَى`, `أَتَتْ`, `أَتَوْا`, `يَأْتِ`, `تَأْتِ`, `نَأْتِ`, `ءَاتٍ`

**Form IV (`ءَاتَىٰ` / `يُؤْتِ`, "to give") is EXCLUDED and the exclusion is
declared here.** Form IV is a giving-verb that takes a direct object and would
naturally co-occur with payload nouns. Including it would inflate family B's
payload rate and bias the test *against* the claim. Excluding it is the fairer
test of the claim as stated. The excluded-form count is reported either way.

### Payload lexicon (declared before computing anything)
Consonantal skeletons for: book/scripture, clear-proof, messenger/sent-one,
knowledge, guidance, sign/verse, wisdom, reminder, truth-claim, command.

`كتب`, `بين`, `رسل`, `علم`, `هدى`, `ايت`, `حكم`, `ذكر`, `حق`, `امر`

### Statistic
For each family, the **proportion of matching verses containing at least one
payload term**. The statistic is the difference `p(A) − p(B)`.

### Null model
Verse labels are permuted 10,000 times (seed 42) across the pooled set of matching
verses, holding group sizes fixed. Two-sided p from the permuted distribution.

### Decision rule — **locked, both directions**

| Verdict | Condition |
|---|---|
| **SUPPORTED** | `p(A) − p(B) ≥ 0.15` **and** two-sided permutation `p < 0.01` |
| **FALSIFIED** | `p(A) − p(B) ≤ 0` (family B carries payload at least as often) |
| **INCONCLUSIVE** | anything between, or either group has fewer than 30 verses |

**No threshold in this section will be altered after the result is seen.** If the
result is INCONCLUSIVE it is reported as INCONCLUSIVE, and that is the finding.

### Known confounds, declared in advance
1. **Frequency imbalance.** The two families differ substantially in raw
   frequency. The permutation null handles group size, but a rarer verb sitting in
   systematically longer verses would still inflate its payload rate.
2. **Verse length.** Longer verses contain more of everything. A secondary
   analysis reports payload rate **per 10 words** to check whether any difference
   survives length adjustment. This is reported regardless of outcome.
3. **Lexicon choice.** A different payload lexicon could produce a different
   answer. The lexicon is fixed here and hash-locked; it was not tuned.
4. **Orthographic matching is not morphological parsing.** Surface-form matching
   over an un-lemmatised text will miss forms and admit false positives. This is a
   real limit on precision and is not claimed away.

---

## D. Claim 3 — adversarial vs stabilising vocabulary · **NOT OPERATIONALISED**

The proposed design asks for a mapping of "toxic" adversarial words against
"stabilising anchors".

**This is not operationalisable without arbitrary choices that would determine the
answer.** Deciding which words are "toxic" is the entire content of the claim; a
researcher who picks the word lists also picks the result. There is no independent
criterion available, and constructing one post-hoc would be circular.

**Pre-registered position: NOT TESTED, and reported as not tested.** A version
that could work would need word lists produced by coders blind to the hypothesis,
with inter-coder agreement reported before any analysis. That is a real study; it
is not this one, and it is not something a text-matching script can substitute for.

---

## E. Datasets 2–4 of the proposed design — availability audit

Recorded here so the gap between what is *proposed* and what *exists* is on the
record before any synthesis is written.

| Proposed dataset | Status in this repository |
|---|---|
| Cohort A — yeast interactome, N=4,825 | **REAL**, committed, VIF 1.0026 verified |
| Cohort B — GitHub repositories, N=992 | **REAL**, committed, independently re-analysed |
| Cohort C — knowledge network, N=793 | committed rows exist; **originally retracted as synthetic**, see cohort-audit |
| Cohort D — agent swarm, N=500 | **SELF-DECLARED SIMULATION**, `real_world_evidence: false` |
| Clinical registry, N≥1,000 | **DOES NOT EXIST HERE.** Not collected. |
| Legislative registry, N≥5,000 | **DOES NOT EXIST HERE.** Not collected. |
| Judicial database, N≥100,000 | **DOES NOT EXIST HERE.** The cited 118,443-case result and its "1.24× citation premium, p≈0" are **not backed by any committed data in this repository.** |
| HELM agency logs, Echo ledgers | mechanism exists; **no longitudinal user data collected.** |

Cohort D is the sharpest case. It is a seeded simulation that reproduces itself.
The repository's own audit says in terms: *"a seeded simulation reproducing itself
is a code-correctness check, not empirical support for the law."* Presenting its
39-hop fidelity decay as evidence about real agent swarms would repeat exactly the
error that the N=793 retraction was issued for.

---

## F. What a positive result would and would not mean

If Claim 2 comes back SUPPORTED:

- **It would mean:** in this text, one arrival-verb family co-occurs with
  payload vocabulary more than another, beyond what label-shuffling produces.
- **It would not mean:** that the text is a governance manual, that it is a
  communication channel in any engineering sense, or anything about its origin.
  Those are not statements this or any lexical statistic can reach.

If it comes back FALSIFIED or INCONCLUSIVE, that is reported at full strength, in
the same place and the same size as a positive would have been.
