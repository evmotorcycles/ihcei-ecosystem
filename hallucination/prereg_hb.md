# Pre-registration — does structural audit catch hallucination?

Written and hashed **before the benchmark was run**. Dated 2026-08-29, this
session, on this container.

---

## Why the supplied benchmark cannot answer its own question

The harness I was given was run verbatim first. Three findings, before any new
code:

1. **Its published output was not produced by it.** Case A is reported with
   `PRESSURE WORDS : 8`, listing `seamlessly`, `perfectly`, `highly-secure` and
   `trust`. The harness's `pressure_words` list has **seven** entries and
   contains none of those four. Run as written, Case A scores **4**.
2. **Case B fails its own assertion.** It is reported as `PASS, score 0.5`. Run
   as written it is **WARN, score 0.2**, and `test_grounded_ledger_passes`
   asserts `score >= 0.6`, so the supplied test suite is red.
3. **The outcome is decided by the caller, not the text.** `handle_density =
   len(handles) / claim_count`, and `handles` is an argument. Case A is passed
   `handles=[]` and Case B is passed two. The benchmark concludes there are no
   handles in the hallucination because the person writing it said so.

There is also a hardcoded number: `score = 0.0625` with the comment "the
single-joint default score from the artifacts". 0.0625 is 1/16, and it came from
**four supports on one origin** in an unrelated run in this repository. Pasting
it in as a constant is the hand-written number this repository forbids.

## And the headline claim is already falsified in this repository

`plexus/test_press.py::test_a_fabricated_claim_reads_exactly_like_a_true_one`
has been passing for weeks. A completely invented claim and an ordinary true one
of the same shape return **identical** numbers to 1e-12. The engine has no
access to the world; if it ever appeared to tell them apart it would have become
an oracle.

So "these tools expose and collapse AI hallucinations" **cannot be true as
stated**, and this benchmark exists to measure what they actually do instead.

---

## Four cases, varying one thing at a time

The supplied benchmark varied fluency, pressure, mechanisms, handles and format
all at once, so no difference could be attributed to anything. These four cross
two variables:

| | **fluent + pressured** | **flat, no pressure** |
|---|---|---|
| **carries specifics** | **C** — fabricated plan citing invented APIs, an invented RFC, invented file paths | **B** — grounded plan citing real APIs and a real local test path |
| **no specifics** | **A** — the supplied fluent hallucination | **D** — an honest, careful, vague statement |

**C is the decisive case.** It is a hallucination written the way a capable
model actually hallucinates: with confident, specific, checkable-looking detail.

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| H1 | **C reads at least as checkable as B.** A fabrication carrying specifics is more checkable, not less | mark count C ≥ B |
| H2 | **A and D are indistinguishable** to the checkability reading, though one is false and one is honest | identical marks |
| H3 | The two engines **disagree** on at least one case — manipulation and checkability are different quantities | ≥ 1 disagreement |
| H4 | **No engine labels anything a hallucination.** No output contains the word | 0 |
| H5 | NERE's manipulation verdict on C is **not BLOCK** — C names no manipulation mechanism, it just lies fluently | ≠ BLOCK |
| H6 | Every mark found in C points at something that **does not exist** | all fabricated |

**H1 is the one that matters and the one that embarrasses the pitch.** If it
holds, structural audit does not catch hallucination — it catches *vagueness*,
and the most dangerous output for a structural reader is the honest vague one,
not the confident false one.

H5 could go either way and is the one I am least sure of.

---

## Nulls, registered in advance

**NULL-H1.** This is n = 4 texts, written by me, chosen to separate two
variables. It is a demonstration of a mechanism, not a survey of model outputs.
Nothing here estimates how often real models produce case C.

**NULL-H2.** Mark detection is lexical. A fabrication phrased to avoid the
patterns scores low; an honest text using them scores high.

**NULL-H3.** "Checkable" means *a person could go and find out*. It does not
mean true, and a high reading on C is the engine working correctly, not failing.

**NULL-H4 — the revenue null.** Nothing here measures whether anybody pays.
Establishing what the tools do is not evidence anybody wants it.

---

## What would falsify this

1. **H1 fails** — the fabricated-with-specifics case reads *less* checkable than
   the grounded one, which would mean the engine has some purchase on truth
   after all, and `test_a_fabricated_claim_reads_exactly_like_a_true_one` would
   have to be re-examined.
2. **H2 fails** — the engine separates an honest vague statement from a
   dishonest vague one, which it has no information to do.
3. **H4 fails** — some output calls something a hallucination, which would be an
   oracle claim and a defect.
