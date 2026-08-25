# Working rules for this repository

Read before writing anything. These are not aspirations; most of them are
enforced by tests, and where they are, the test is named.

## Always

- **State what the tool cannot do, in the same size type as what it does.**
  `plexus/lens.js` holds each tool's refusal sentences and `test_gate.py`
  asserts every shipped page prints its own, verbatim, compared on collapsed
  whitespace. Edit a limit without editing the page and the build fails.
- **Lock predictions before running anything.** Write them, `sha256sum` the
  file, assert the hash in the test. There are 11 such files and 10 suites
  asserting them. A number produced before a prediction is a description.
- **Report the misses.** Four are recorded in the suite by name:
  `test_the_prediction_that_missed`, `test_the_two_predictions_that_failed`,
  `test_the_half_of_m5_that_missed`, and the truncated sixth decimal in
  `test_cohort.py`. Softening one costs more than the miss did.
- **Measure the structure; never hand-write the number.** Parts and links go in;
  bearings, single points and dependences come out of the tested engine.
- **Say where a reading came from.** Any hand-assigned link, prediction list or
  classification carries a `where` field. `test_metaphor.py` refuses one without.

## Ask first

- **Changing a locked pre-registration.** Never done silently. If a prediction
  needs to change, the honest move is a new file with a new hash and a record of
  why, not an edit.
- **Adding a threshold.** Every number that gates a decision needs a stated
  reason and an operable sensor. `FLOOR_RETIREMENT.md` records one retired at
  p = 0.735 because its sensor read zero on 76.6% of records.
- **Fusing two readouts into one score.** Structure, rhetoric, arithmetic and
  latency are different kinds of quantity. `test_gate.py` and `test_intercept.py`
  assert no combined field appears.
- **Shipping a claim about a real company, tariff, instrument or person.**
  `test_packs.py` greps the library for currency symbols and company suffixes.

## Never

- **Never imply the software understood the text.** It matches patterns. A
  party-inverted sentence returns a bit-identical readout, and
  `test_the_parties_can_be_inverted_and_the_readout_does_not_move` pins it. An
  engine that appeared to catch that would be claiming a comprehension it does
  not have.
- **Never put a grade on the first screen.** No `n/5`, no percentage of
  correctness, no colour that reads as safe or unsafe. The number a person holds
  is how many errands they have. `test_the_first_screen_carries_no_grade`.
- **Never render "nothing to check" as an error.** Empty is not false. A sincere,
  fluent, internally consistent text can yield nothing checkable, and that state
  gets no number at all -- `test_fog_returns_no_number_at_all`.
- **Never let a blank field become a zero.** A missing input makes its row vanish.
  `test_a_blank_field_stays_blank_and_never_becomes_zero` exists because a blank
  "amount paid" silently reading 0 would have reported a credit of -62084.
- **Never accuse.** The verdict says two numbers differ. It does not say
  overcharged, wrong, error, owe or fraud, and `test_packs.py` greps for those.
- **Never manufacture urgency, scarcity, social proof or price anchoring.** Every
  string must pass this project's own grounding engine.
- **Never write a literal NUL byte.** Use the escape `\u0000`. FIVE have now been
  committed here -- the fifth was in the line of this file that forbids it --
  and every one was caught by
  `test_the_shipped_page_carries_no_control_characters`.
- **Never rebuild a list inside a handler bound to one of its own children.**
  Mutate the row. Six occurrences so far.

## On the words

`check` is an imperative and an errand: *three things to check*. `checked`,
`verified`, `supported` are past participles and claim the errand was done. The
first is the whole vocabulary of this build; the last three are banned. Banning
both collapses the distinction the project turns on.
