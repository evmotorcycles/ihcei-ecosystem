# Governance computer science vs RT computer science

**RT = "rational-truthfulness" computing.** Software built to be *correct* and to
*report honestly*. It is the tradition almost all software belongs to, and it is a
genuine achievement — type systems, tests, formal methods, code review.

**Governance computing** asks a different question. Not *"is this program
truthful?"* but *"can this program's answer be checked by someone who does not
trust the program, the author, or me?"*

That is not a higher standard of care. It is a different **location** for the
guarantee.

---

## The one-sentence difference

> RT puts the guarantee in the **author's discipline**.
> Governance puts the guarantee in the **structure of the program**, where it
> survives the author leaving, forgetting, being rushed, or being motivated.

Everything else in this document is an elaboration of that sentence.

---

## Why "truthful" is not enough — a worked case

This function is truthful. It reports exactly what it computed. It has no bugs,
passes type checking, and any reviewer would call it clean.

```python
def check_project(project):
    score = project["forks"] / project["stars"]
    if "best" in project["description"].lower():
        score += 0.5
    return round(score, 3)
```

It returns **`0.8`**. The honest answer is **`0.3`**.

The inflation came from `description` — the project's own account of itself. The
program consulted the thing it was judging, about itself, and folded that into the
verdict.

Notice what did **not** fail:

- Not correctness. It computed what it was told to compute.
- Not honesty. It reported its result faithfully.
- Not testing. Any test asserting `check_project(x) == 0.8` passes.
- Not review. A reviewer would have to *notice* line 4 and *object* to it.

**RT has no vocabulary for what went wrong here**, because nothing RT measures went
wrong. The failure is that a verdict consulted its own subject — and "don't do
that" is advice, not a mechanism.

This is why the distinction is not academic. `0.8` and `0.3` are different
decisions about where money goes.

---

## The three questions governance answers that RT cannot

RT can establish that a program does what it says. It cannot, on its own, answer
these three — because each is a question about **the relationship between the
judge and the judged**, not about the code's correctness.

### Q1 — Purpose: what is this system *for*, such that we could tell if it failed?

**Why RT can't answer it.** A correct program optimises whatever objective it was
given. Correctness is silent on whether that objective was the right one, and
silent on whether "big" was quietly substituted for "working".

**The governance answer:** make purpose a *shape*, not a label.

```
E = capacity × encode × decode
```

The terms **multiply**. If any one is zero, the result is zero. A system with
enormous reach and no working channel scores nothing — reach alone cannot carry
the total.

Had these been *added*, size would dominate and a huge broken thing would outrank
a modest working one. The multiplication is the claim: **capacity is not
achievement.** And because it is arithmetic rather than a mission statement, it
is checkable by someone who has never met you.

*What this doesn't do:* it does not tell you the objective is worth pursuing. It
makes an inflated one visible.

---

### Q3 — Stewardship: who is checking, and are they actually independent?

**Why RT can't answer it.** Two tests can both pass while testing the same thing.
Two reviewers can both approve while sharing an assumption. Nothing in the code
records whether your evidence sources were genuinely separate — and the *feeling*
of confirmation is identical either way.

**The governance answer:** measure independence, and act on the measurement.

```
independent encode decode        # legs must carry different information
```

Measured by variance inflation, with three outcomes — and the third is the one
that matters most:

| Outcome | Meaning | Behaviour |
|---|---|---|
| `VERIFIED_INDEPENDENT` | measured, genuinely different | proceed, stamp each verdict |
| `DEPENDENT` | measured, the same information twice | **halt**, emit nothing |
| `UNVERIFIABLE` | too little data to measure | proceed, stamp `independence_checked = false` |

`UNVERIFIABLE` is not `DEPENDENT`. **"I checked and it failed" is a finding.
"I couldn't check" is an absence of evidence.** Collapsing them manufactures a
result out of a gap — which is the failure mode this whole discipline exists to
refuse.

*Provenance:* the first implementation collapsed exactly these two states and
halted on both. Its own test suite caught it. The fix is locked by a regression
test named after the mistake.

*What this doesn't do:* statistical independence is not conceptual independence.
Two numbers derived from one underlying source can pass the check and still be the
same fact wearing two hats.

---

### Q4 — Reference-lock: what is the answer measured *against*?

**Why RT can't answer it.** A program can read anything in scope. Nothing stops an
evaluator consulting the thing it is evaluating — that was the `0.8` above. RT can
verify the read happened correctly; it cannot object that the read should not have
happened.

**The governance answer:** remove the field from the record before evaluation
begins.

```
blind "description"
```

Not "ignore it." Not "don't weight it." **Delete it.** By the time any calculation
runs, the field does not exist. The evaluator could not cheat if it wanted to.

Then one step further: the deletion is committed to **inside the receipt digest**.
An auditor doesn't have to trust that you applied blinding — they verify it from
the receipt.

This is the plumb line. Gravity has no opinion about your wall. A deleted field
has no opinion about your verdict.

*What this doesn't do:* blinding one field says nothing about the ten you didn't
blind, or the rows you didn't include.

---

### And the two we do not claim

**Q2 and Q5 are not resolved here, and are not resolved anywhere in this
repository.** They are outside what any software can check.

A stack claiming five out of five would be telling you something it cannot know.
Naming the boundary is part of the work — and it is also the test of whether the
first three claims are worth anything. A framework that answers every question it
poses has usually chosen its questions to fit its answers.

---

## Where Plumb sits

Plumb is the **executable form** of those three answers. Not a description of
governance computing — an interpreter that cannot produce a verdict which skips
the obligations.

| Question | Plumb construct | If violated |
|---|---|---|
| Q1 purpose | `capacity × encode × decode` | zero anywhere → zero result |
| Q3 stewardship | `independent encode decode` | **program halts**, zero verdicts |
| Q4 reference-lock | `blind "field"` | field deleted; deletion in the receipt |
| (all three) | no bare return | `GovernanceError` at runtime |
| (all three) | `abstain` is a result | exits 0, with reasons |

The move Plumb makes is small and specific: **it relocates these from the review
checklist into the grammar.** A checklist item can be skipped by a tired person on
a Friday. A grammar cannot be.

**Plumb is a domain-specific rule language, not a general-purpose one.** No loops,
no user-defined functions, no I/O. You will not write an application in it. You
write the rule that decides something, in a form an auditor reads in thirty
seconds.

And `governance.py` does **not** "transform Python" — Python is not modifiable.
It makes the same obligations enforced at runtime, so a function that skips them
raises instead of quietly returning a number. That is the real difference from a
linter: a linter cannot stop a running program.

---

## Side by side

| | RT computing | Governance computing |
|---|---|---|
| Central question | Is it correct and honestly reported? | Can a stranger check it without trusting us? |
| Guarantee lives in | the author's discipline | the structure of the program |
| Wrong answers caught by | tests, types, review | **structure** — the wrong shape won't run |
| "Ignore this field" | a convention, sometimes a comment | the field is **deleted** |
| Two identical checks | run fine, feel twice as sure | **halt** |
| Confidence | a number the program chose | a number **compared against something it never saw** |
| "I don't know" | usually an exception | a normal, successful result |
| Changing the rule after results | invisible | hash changes, **visible** |
| Failure it prevents | incorrect computation | **uncheckable computation** |
| Failure it cannot prevent | a wise-looking bad objective | **the same** |

That last row is not symmetry for the sake of it. Neither tradition can tell you
your rule is wise. Governance computing only guarantees that when your rule is
unwise, **somebody outside can see it** — instead of receiving a number with three
decimal places and no way in.

---

## What this is not

**Not a claim that RT computing is wrong.** Correctness is a prerequisite, not a
rival. A governed program that computes the wrong thing is still wrong. Everything
here sits *on top of* ordinary correctness.

**Not a claim to detect bad intent.** Every mechanism described here is equally
effective against an honest mistake and a deliberate one, which is precisely why
it doesn't need to tell them apart.

**Not a claim that structure implies safety.** A fully blinded, fully independent,
fully receipted rule can still be a foolish rule. These constructs make the
obligations visible. They do not supply judgement.

**Not a claim of completeness.** Three of five questions. The other two stay open,
and are stated as open wherever this work is published.

**Not a valuation claim.** Nothing here supports a statement about market size or
company worth. Those depend on markets, capital and timing that no repository can
measure, and any figure would be invented.

---

## Verify it rather than believe it

```bash
python3 plumb/governance.py          # 0.8 the RT way, 0.300 the governed way
python3 -m pytest -q plumb/          # 41 tests holding the four obligations
bash reproduce_all.sh                # the whole stack, offline, no keys
```

The pre-registrations in this repository are SHA-256 locked **before** their runs
and re-verified by the test suite, so editing one after seeing results fails the
build. Nulls, halts and our own failed calibration gate are reported at full
strength.

That last item is the honest test of whether any of this is real: we ran a
calibration check on our own confidence scores, set the limit at 0.15 beforehand,
measured **0.3727**, failed — and did not move the limit. It is printed on the
front page of the tool ordinary people use.

A framework that has never published its own failure has not yet been tested.
