# Pre-registration — PLUMB language semantics + out-of-sample cohort run

**Status when written:** frozen BEFORE the out-of-sample run (P5–P7). Locked by
SHA-256 of this file; the hash is recorded in `plumb/prereg.lock.json` and
re-verified by `plumb/test_plumb.py`.

---

## Honest declaration of what is and is not pre-registered

Three classes of claim appear below. They are not equal and are not presented as
equal.

| Class | Claims | Status |
|---|---|---|
| **A. Language semantics** | P1–P4 | Genuinely pre-registered. Structural, deterministic, falsifiable by construction. |
| **B. Cohort A description** | D1–D2 | **NOT pre-registered.** Measured on the 22-repo Qwen/DeepSeek cohort *before* this file was written. Recorded as description, never as confirmation. |
| **C. Out-of-sample** | P5–P7 | Genuinely pre-registered. The program has never been run against this cohort. P6 is *informed* by cohort A — declared, not hidden. |

Anyone reading this should discount class B to zero as evidence. It is here so
the record is complete, not so it can be counted.

---

## A. Language semantics (pre-registered, falsifiable)

The claim under test is that Plumb's governance obligations live in the
**interpreter**, not in a style guide. Each prediction fails loudly if that is
false.

- **P1 — `blind` is physical, not advisory.**
  For a program declaring `blind "description"`, no evaluation path may observe
  the value of `description`. Test: inject a poisoned record whose `description`
  field contains a value that, if read, would change the verdict; the verdict
  must be identical to the same record with the field absent, and
  `audit.blind_values_stripped` must count the removal.
  *Falsified if* the verdict differs, or the field survives into evaluation.

- **P2 — non-independent legs HALT.**
  A program declaring `independent encode decode` whose two legs derive from the
  same source must return zero verdicts and a non-null `audit.halted`.
  *Falsified if* it emits verdicts, or merely warns.

- **P3 — there is no bare return.**
  Every emitted verdict carries `confidence`, `evidence` and `receipt` keys.
  There is no syntax in the grammar that produces an unqualified value.
  *Falsified if* any verdict lacks any of the three.

- **P4 — abstain is a result, not an error.**
  A record below the floor produces `verdict == "ABSTAIN"` with reasons, exit
  status 0, and no exception escaping `run()`.
  *Falsified if* abstention raises, or is reported as failure.

Additionally, receipts must be deterministic: the same program over the same
record yields the same receipt digest across runs.

---

## B. Cohort A — descriptive only, NOT a hypothesis test

Measured 2026-08-09 on `ei-dashboards/data/qwen_deepseek_frozen.json` (22 real
repos, 10 QwenLM + 12 deepseek-ai) with `plumb/examples/vendor.plumb`:

- **D1** VIF between the two legs = **1.2374** → independent, program proceeds.
- **D2** **3 SUPPORTED, 19 ABSTAINED.**

**Construct-validity note, stated before anyone can call it a win:** the high
abstain rate is a property of the `inverse` transform, not a governance finding.
`encode = 1/(1 + open_issues)` falls below the floor of 0.02 for any project
with more than 49 open issues, which is most serious projects. **This does not
mean 19 of 22 projects are bad.** It means this particular program is a blunt
instrument at that scale and abstains rather than guessing — which is the
designed behaviour, but is not evidence about the projects.

The floor of 0.02 was written into `vendor.plumb` **before** the first run and
is **not** being moved now that the abstain rate is known. Moving it would be
exactly the retuning this project exists to refuse.

---

## C. Out-of-sample run (pre-registered — NOT YET RUN)

Cohort B: `github-lism/data/github_cohort_frozen.json`, 28 real repositories,
different organisations, collected for a different study, carrying the same
three fields (`stars`, `open_issues`, `forks`).

The **byte-identical, unmodified** `plumb/examples/vendor.plumb` will be run
against it. No parameter will be changed for this cohort.

- **P5 — independence transfers.** VIF between the two legs on cohort B is
  finite and `< 5.0`, so the program proceeds rather than halting.
  *Falsified if* VIF ≥ 5.0 or infinite. A halt here would be a real negative
  result about the two-leg construct and will be reported as one.

- **P6 — abstention dominates (informed prediction).** Given the saturation
  described in D2, at least **50%** of cohort B records abstain.
  *Falsified if* fewer than 50% abstain. Declared as informed by cohort A.

- **P7 — no crash, no silent success.** The run exits 0 with a complete audit
  block, and the count of SUPPORTED plus ABSTAIN verdicts equals 28.
  *Falsified if* records are silently dropped.

Whatever P5–P7 return is recorded verbatim in `plumb/results_plumb.json` and
locked by `plumb/test_plumb.py`. **No gate in this file will be altered after
the result is seen.**

---

## Scope limits (binding)

1. Plumb is a **domain-specific rule language**, not a general-purpose
   programming language. It has no loops, no user-defined functions, no I/O.
2. Plumb checks **structure**, not **truth**. A program can be perfectly
   independent, fully blinded, fully receipted, and still encode a stupid rule.
   The language forces the obligations to be visible; it cannot make them wise.
3. Of the five governance questions, Plumb operationalises **three** (purpose,
   stewardship, reference-lock). **Questions 2 and 5 are not resolved here and
   are not resolved by this project.** They are outside what any software can
   check, and no part of this repository should be read as claiming otherwise.
