# Pre-registration — pressing real Qwen and DeepSeek model cards

Written and hashed **before** any card was fetched. Nothing from Hugging Face
had been looked at when this file was locked.

---

## What is being tested, and what is not

The Lens algorithm (`plexus/press.js`) has only ever been run on synthetic marks
and two hand-written example sentences. This is its first run against real
artefacts nobody here wrote: the model cards of Qwen and DeepSeek releases.

**This does not evaluate any model.** Nothing here says whether Qwen or DeepSeek
is good, whether a benchmark figure is correct, or whether anyone has done
anything wrong. It asks one question of the sentences on a card: *if a reader
wanted to check this, what could they go and do, and who would they have to ask?*

---

## Two things already in this repository that constrain this

1. `plumb/PREREG.md` marks the existing 22-repo Qwen/DeepSeek cohort as
   **descriptive only**. This run does not touch that cohort and does not
   inherit or refresh its status. It is a separate, newly frozen sample.
2. `qg-cos/five_questions.py` already carries the same pressing frame this stack
   uses — reading the process underneath rather than the rendered surface. Its
   Q3 rests on the two-hop fidelity product that `FLOOR_RETIREMENT.md` retired
   at p = 0.735; nothing in this run depends on Q3.

---

## Procedure, fixed in advance

1. Fetch the model cards for the Qwen and DeepSeek text-generation models
   returned by the Hub search, up to ten of each, by downloads.
2. **Freeze** the fetched text verbatim into `plexus/hf_cards_frozen.json` with a
   SHA-256 and the date, so every later run is offline and reproducible.
3. For each card, take its **quantitative sentences**: those containing at least
   one digit and at least 40 characters, capped at 40 per card, in document
   order. These are the candidate claims.
4. Run `cairn/ei_engine.js` over each sentence for marks, take the first detected
   source span as the origin, and press the result with `press.js`.

Everything after step 2 is deterministic and runs with no network.

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| H1 | Share of quantitative sentences that press as **checkable** (at least one mark) | ≥ 0.80 |
| H2 | The most common number of marks on a quantitative sentence is **2 or 3**, not 5 | 2 or 3 |
| H3 | Share of pressed sentences whose origin is **unnamed** — a figure with nothing behind it that a reader could open | ≥ 0.60 |
| H4 | At least **one** card, somewhere in the sample, carries a source span pointing at something a third party holds (an arXiv id, a DOI, a link) | ≥ 1 |
| H5 | Share of sentences where the `source` mark fires at all | ≤ 0.35 |
| H6 | The 1/m² law reproduces on real text exactly as on synthetic marks | exact |
| H7 | Across the whole sample, the single most common `firstCheck` instruction is **"Ask where this came from"** | most common |

H1, H2, H3, H5 and H7 are the ones that could come back wrong. H6 is
verification — it is arithmetic and cannot come out otherwise; it is listed so
that a reader does not mistake it for a discovery.

H4 is deliberately a prediction **against** the interesting result. If no card in
the sample points at anything a third party holds, the finding is starker — and
I would rather have predicted the boring outcome and been beaten by the data
than predicted the striking one and been flattered by it.

---

## What I expect to find, stated so it can be wrong

That model cards are **dense in figures and thin in origins**: many numbers,
stated precisely, with the evaluation that produced them being the authors' own,
and no named third party a reader could go to instead. That is the shape the
Shapes library already records as `benchmark-contamination`, and if it appears
here it appears in real artefacts rather than in an example I wrote.

If instead most cards name independent leaderboards or third-party evaluations
with links, H3 and H5 fail, the expectation was wrong, and it must be reported
that way.

---

## Nulls, registered in advance

**NULL-H1.** This measures cards, not models. A model with a thin card can be
excellent and a model with a thorough card can be poor.

**NULL-H2.** A high mark count is not accuracy and an unnamed origin is not
dishonesty. Publishing a number you measured yourself is normal, expected, and
how nearly all of this field works. The reading says only what a reader would
have to do to check it, and who they would have to ask.

**NULL-H3.** Mark detection is lexical, from `cairn/ei_engine.js`. It matches
words. On a benchmark table it will read numbers it does not understand and will
miss sources named in ways its patterns do not cover. Registered already as
NULL-L2 in `press_preregistration.md` and no less true here.

**NULL-H4.** Sentence splitting on a markdown card is crude. Tables, code blocks
and lists will be cut in places no reader would cut them. The sample is what a
naive reader's eye would land on, not a curated set of claims.

**NULL-H5.** Ten of each is a small sample chosen by download count on one day.
It is not representative of open-weight releases generally and no inference to
that population is made.

---

## What would falsify this

1. **H3 and H5 both fail** — cards mostly do name third-party origins. Then the
   expectation above was wrong and the `benchmark-contamination` shape does not
   describe this corner of the world.
2. **H1 fails badly** — most quantitative sentences produce no marks. Then the
   lexical detector is not fit for this kind of text and the run says nothing
   about cards, only about the detector.
3. **Any card's numbers move between two offline runs.** Then the freeze is not a
   freeze and every figure here is unreproducible.
