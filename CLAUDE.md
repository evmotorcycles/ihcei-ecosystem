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

## Earned by failures in this repository

- **Register a horizon, then probe past it.** Any monotonicity or trend claim
  states the range it was measured over, and **one probe past that range is
  mandatory and reported whichever way it falls**. `geometric-gate/` found an
  empty band that finer sampling filled; `stack/perception/` hit 3.112x inside
  its registered range and reversed one doubling past it. Both would have
  shipped a confident wrong number. `test_the_growth_reverses_one_sample_past_the_registered_range`.
- **A lexical check needs a two-sided decoy.** Collapse whitespace before
  matching; exclude path separators as well as word characters at the
  boundaries; carry one string the check must NOT fire on and one it MUST; and
  scope the claim to precision -- a static text check can demonstrate its false
  positives and can never claim recall. `"ema"` matched inside `"semantically"`;
  `\busr\b` fired inside `/usr/local`. Thirteen times in one session a check
  has matched the sentence forbidding the thing it checks for, including the
  write-up of the eleventh.
- **Exempt by role, never by name.** A file that must quote what it forbids --
  the ledger, a `prereg_*.md`, a `test_*.py`, a `RESULTS.md` -- is exempt by
  what it is. A hand-listed allowlist needs a new entry per module and grows
  silently. Shipped module code is never exempt, and a decoy asserts it.
- **A rule broken fourteen times is a mechanism, not a reminder.** The lexical
  rule above now lives in `stack/governance/matcher.py` and is the only
  available implementation: `forbid()` collapses whitespace itself so a caller
  never holds the raw text, and `scan()` takes both decoys and `min_seen` as
  **required keyword arguments** so a one-sided check cannot be written and a
  walk that read nothing cannot report clean. Two more instances arrived
  immediately and are kept as cases -- the fifteenth was the matcher's own
  docstring, flagged by the first scan ever run, fixed by neutralising the
  example and **not** by exempting the file; the sixteenth was a test grepping
  its own source for a deleted function's name, fixed by reading the parse tree
  instead of matching text. `test_matcher.py`.
- **An identity check never ships labelled as evidence.** A wrapper that
  imports its engine cannot drift from it, so it carries no regression against
  it at all -- not even one annotated as a tautology, because a reader skimming
  a green suite counts it. A vendored copy carries the opposite obligation: a
  frozen fixture snapshot external to both. Pick one, record which, take the
  consequence. `declarations.md` §4c.
- **A certificate names its subject, not only its group.** `27 -> 31` cut
  vertices and `18 -> 23` stable names happened with no certificate changing,
  because a certificate said what it held *under* and never what it held
  *about*. Every one now carries `(readout, invariance_group, subject_hash,
  date)`, two certificates over different subjects refuse to combine, and
  legacy ones are marked rather than back-dated. Tests assert relationships --
  `stable == declared & completed`, `lost | gained == declared ^ completed` --
  never frozen counts, and a tolerance band on a ratio is a frozen count in
  disguise.
- **Probe the container before writing a prediction against it.** Both Phase 5
  doors are shut on **egress, not on inspection**: no ML runtime and no
  reachable weight host for Door 1, no obtainable per-hop corpus for Door 2. No
  pre-registration was written against either. The text exists unlocked in
  `phase5/runner_spec.md` for a runner that can pass the gate, and the human
  check stays recorded **OPEN** -- a network limitation must not harden into a
  finding.

## On the words

`check` is an imperative and an errand: *three things to check*. `checked`,
`verified`, `supported` are past participles and claim the errand was done. The
first is the whole vocabulary of this build; the last three are banned. Banning
both collapses the distinction the project turns on.
