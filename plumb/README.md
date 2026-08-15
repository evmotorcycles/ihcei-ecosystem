# PLUMB — a governance rule language, and the same obligations inside Python

> A plumb line finds true vertical using a force you cannot argue with.

Two artefacts live here:

| File | What it is |
|---|---|
| `plumb.py` | **Plumb** — a small declarative language whose interpreter cannot emit an unqualified answer. |
| `governance.py` | The same four obligations as decorators, for people who are staying in Python. |

Run them:

```bash
python3 plumb/plumb.py plumb/examples/vendor.plumb ei-dashboards/data/qwen_deepseek_frozen.json --key repos
python3 plumb/governance.py            # worked RT-vs-Governance comparison
python3 plumb/run_plumb.py             # regenerates results_plumb.json
python3 -m pytest -q plumb/            # 41 guard tests
```

---

## What problem this is actually solving

An RT language optimises for *truthfulness*: it lets you write correct code, and
trusts you to have been careful. Nothing in Python stops this:

```python
def assess(record):
    score = record["forks"] / record["stars"]
    if "best" in record["self_description"].lower():
        score += 0.5
    return round(score, 3)          # -> 0.8
```

That function is syntactically perfect, passes type checking, and is **wrong in a
way no compiler can see**. It consults the subject's own description of itself,
then returns a bare number with no confidence, no reasons, and no record of how
it was produced. Downstream, `0.8` is indistinguishable from a measurement.

The governed version returns `0.300` — the real ratio — and it is not a matter of
the author remembering to be careful. `self_description` is **deleted from the
record before the function body runs**.

```
RT Python      : 0.8   <- bare number, blurb-inflated, no receipt
Governance     : SUPPORTED (confidence 0.300) — reuse ratio 0.300 clears the floor
  evidence     : 3/4
  receipt      : e84826fbfd782559
  blinded      : ('self_description',) — removed before the body ran
```

That gap — `0.8` versus `0.300` — is the whole thesis, and it is reproducible by
running `python3 plumb/governance.py`.

---

## The four obligations

Both artefacts enforce the same four things. None of them is advice.

**1. No bare return.** There is no syntax for an unqualified answer. A governed
Python function returning `0.9` raises `GovernanceError`; a Plumb program has no
grammar production that yields a naked value. Every answer carries confidence,
the reasons behind it, the evidence count, and a receipt.

**2. `blind` is physical.** Declared fields are *deleted* from the record before
evaluation begins. The evaluator cannot read them because they are not there —
not because a policy says it shouldn't. The removal is committed to inside the
receipt digest, so an auditor can verify blinding happened rather than trusting
that the decorator was applied.

**3. Independence is checked, in three states.** Two evidence legs must carry
different information. Measured by VIF, with a distinction that matters:

| State | Meaning | Behaviour |
|---|---|---|
| `VERIFIED_INDEPENDENT` | VIF < 5 | proceed, stamp each verdict |
| `DEPENDENT` | VIF ≥ 5 or infinite | **HALT** — emit zero verdicts |
| `UNVERIFIABLE` | fewer than 3 records | proceed, stamp `independence_checked=False` |

`UNVERIFIABLE` is not `DEPENDENT`. Reporting "not independent" when you mean "I
could not tell" manufactures a finding out of an absence. The first version of
this interpreter collapsed the two and halted on single records; the test suite
caught it and `test_P2_unverifiable_is_not_the_same_as_dependent` now locks the
fix.

**4. Abstain is a result.** Below the floor, the program returns `ABSTAIN` with
reasons and exit status 0. It is a return value, never a raise — abstaining has
to be as cheap and ordinary as answering, or code quietly stops doing it.

---

## Mapping to the governance questions

Three of the five questions are operationalised here:

- **Q1, purpose** → `capacity × encode × decode`. Capacity alone is inert: a
  project with a hundred thousand stars and no working channel scores zero,
  because the terms multiply.
- **Q3, stewardship** → `independent`, the two-hop requirement.
- **Q4, reference-lock** → `blind`, the decoupled shield.

**Questions 2 and 5 are not resolved here, and are not resolved anywhere in this
repository.** They are outside what any software can check. Naming that boundary
is part of the work, not a gap in it.

---

## Results

Pre-registration locked by SHA-256 in `prereg.lock.json` **before** the
out-of-sample run. Full detail in `PREREG.md`; machine-readable in
`results_plumb.json`.

### Out-of-sample (pre-registered, cohort B: 28 real GitHub repositories)

The byte-identical `vendor.plumb` was run against a cohort collected for a
different study, with no parameter changed.

| Prediction | Gate | Measured | Result |
|---|---|---|---|
| P5 independence transfers | VIF finite and < 5.0 | **1.0041** | HOLDS |
| P6 abstention dominates | ≥ 50% abstain | **64.3%** (18/28) | HOLDS |
| P7 no silent drop | supported + abstained = 28 | **28** | HOLDS |

### Negative control

`collapsed.plumb` reads both legs from the same column. It **halts** with
VIF `inf` and emits zero verdicts, exit code 3. In an RT language that program
runs fine and prints a confident number twice.

### Three things that must not be read as wins

1. **`blind` stripped 0 values on cohort B.** That cohort has no `description`
   or `topics` columns at all. The blinding did not fail — there was nothing to
   blind. P1 is therefore tested on cohort A and on a synthetic poisoned record,
   never on cohort B.
2. **The high abstain rate is a property of the transform, not a finding about
   the projects.** `encode = 1/(1 + open_issues)` falls below the 0.02 floor for
   any project with more than 49 open issues, which is most serious projects.
   This does **not** mean those projects are bad. The floor was written before
   the first run and **was not moved** once the abstain rate was known.
3. **Cohort A's numbers are descriptive only.** They were measured before
   `PREREG.md` existed and carry no confirmatory weight. They are recorded so the
   record is complete, not so they can be counted.

---

## Scope limits (binding, and tested)

1. **Plumb is a domain-specific rule language, not a general-purpose programming
   language.** No loops, no user-defined functions, no I/O. Calling it "a new
   programming language" in the sense of Python or Rust would be an overclaim.
2. **`governance.py` does not "transform Python".** Python is not modifiable and
   nothing here changes it. What it does is make the obligations enforced at
   runtime, so a function that skips them raises instead of quietly returning a
   number. The difference from a linter or a review checklist is that neither of
   those can stop a running program.
3. **Both check structure, not truth.** A program can be perfectly independent,
   fully blinded, fully receipted — and still encode a foolish rule. These
   constructs force the obligations to be visible. They do not supply judgement.
4. **The ledger is tamper-evident, not tamper-proof.** It does not prevent
   editing; it makes editing visible.

Each of these is locked by a test, so weakening the code without also weakening
the stated limits fails the suite.
