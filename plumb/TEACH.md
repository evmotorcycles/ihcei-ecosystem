# Learning Plumb

**For everyone who builds software, and everyone who has to check it.**
No prior knowledge assumed. If you can read a recipe, you can read this.

---

## Part 1 — The idea, with no code at all

### A story about a school test

Imagine your teacher asks the class to mark their own homework.

Some people mark honestly. But the marks are now **unreliable** — not because
everyone cheated, but because you can no longer tell the honest marks from the
dishonest ones. The information you needed is gone.

Now imagine a different rule: **before marking, every name is covered up.** Now
nobody *can* mark their own work. You didn't need to trust anyone. You changed
what was possible.

That is the whole idea behind Plumb. Not "please be careful." **Make the careless
thing impossible.**

### What is a plumb line?

A plumb line is a piece of string with a weight on the end. Builders have used it
for thousands of years. Hold it up, and the string shows you *exactly* straight
down — because gravity pulls the weight, and gravity does not have opinions.

You can argue with a builder about whether a wall is straight. **You cannot argue
with the string.**

That is what we want from software that judges things: a check you cannot talk
your way around.

---

## Part 2 — The problem, shown in one example

Here is a small program in Python — the most popular programming language in the
world. It answers: *is this software project healthy?*

```python
def check_project(project):
    score = project["forks"] / project["stars"]
    if "best" in project["description"].lower():
        score = score + 0.5
    return round(score, 3)
```

Read line 4 slowly. It reads `description` — **the project's own description of
itself, written by the people who made it** — and adds half a point if they said
they were the best.

That is the school test with names uncovered.

Run it on a real project and it prints **`0.8`**.
Take out the self-description and the honest answer is **`0.3`**.

Now, three things worth noticing, because they are the whole reason Plumb exists:

1. **The program is not broken.** It runs. It has no bugs. Every tool that checks
   Python code for errors says it is fine.
2. **`0.8` looks exactly like a measurement.** It is a number with three decimal
   places. Nothing about it says "this was inflated by marketing copy."
3. **Nobody can tell.** Not the next programmer, not your boss, not an auditor —
   unless they read every line and happen to notice.

The number is confident, precise, wrong, and untraceable. That combination is the
problem.

---

## Part 3 — What Plumb does differently

Here is the same job written in Plumb:

```
plumb "is-this-project-healthy" {

  capacity  U    from field "stars"
  encode    Denc from field "open_issues" inverse
  decode    Ddec from ratio "forks"/"stars"

  floor 0.02

  blind "description"

  independent encode decode

  require evidence 4 of 5
  receipt
}
```

Let's read it line by line, like a recipe.

| Line | In plain words |
|---|---|
| `plumb "is-this-project-healthy"` | The name of the question you're asking. |
| `capacity U from field "stars"` | How **big** is it? Size on its own proves nothing — see below. |
| `encode ... "open_issues" inverse` | Can it take information **in**? `inverse` means *fewer is better*. |
| `decode ... ratio "forks"/"stars"` | Can information get back **out** and be used by someone else? |
| `floor 0.02` | Below this, don't answer at all. |
| `blind "description"` | **Delete** what it says about itself, before looking. |
| `independent encode decode` | The two checks must not be the same check twice. |
| `require evidence 4 of 5` | Need at least 4 of 5 pieces of evidence to say anything. |
| `receipt` | Keep a tamper-proof note of how this answer was reached. |

### The four rules that make it different

These are not suggestions in a style guide. **The program physically cannot break
them**, in the same way you cannot drive a car through a locked garage door by
being determined.

---

#### Rule 1 — You can never just return a number

In Python you can write `return 0.8` and stop. Plumb has no way to say that. Every
answer has to come with:

- **how sure** it is,
- **why** — the reasons,
- **what evidence** was there (like "4 of 5"),
- a **receipt** — a short code that proves this exact answer came from this exact
  input.

> **Why this matters:** a lonely number can't be argued with, because it has no
> reasons attached. An answer with its reasons attached can be checked, disputed,
> and corrected. Plumb never lets an answer travel without its reasons.

---

#### Rule 2 — `blind` really deletes things

This is the school-test rule, and it is the one people misunderstand most.

When you write `blind "description"`, Plumb does not "try to ignore" the
description, and does not "promise not to look." **It deletes it from the record
before the checking starts.**

By the time any calculation runs, that information does not exist. The program
could not cheat if it wanted to, because there is nothing there to cheat with.

And it goes one step further: the fact that the deletion happened is **written
into the receipt**. So an auditor doesn't have to trust that you used `blind` —
they can check the receipt and see it.

> **The difference in one sentence:** a rule says *don't look*; `blind` means
> *there is nothing to look at*.

---

#### Rule 3 — Two checks must actually be two checks

Say you're deciding whether to trust a restaurant, and you look at two things:

- its rating on a review site, and
- its rating on the same review site, again.

You looked twice. **You learned one thing.** But you feel twice as sure, which is
worse than useless — it is confidence you didn't earn.

`independent encode decode` tells Plumb to measure whether your two checks are
really carrying different information. If they are secretly the same, **the
program stops and refuses to answer.** It doesn't warn. It doesn't carry on with
a note in the corner. It stops.

There are **three** possible outcomes here, and the difference between the last
two matters enormously:

| Result | Meaning | What happens |
|---|---|---|
| `VERIFIED_INDEPENDENT` | Checked. They're genuinely different. | Carry on. |
| `DEPENDENT` | Checked. They're the same thing twice. | **Stop.** Answer nothing. |
| `UNVERIFIABLE` | **Couldn't check** — not enough data. | Carry on, but stamp every answer "not checked". |

**"I checked and it failed" and "I couldn't check" are different facts.** Treating
them as the same thing invents a finding out of a gap. (The first version of Plumb
made exactly this mistake. Its own test suite caught it. The fix is now locked by
a test so it can't come back.)

---

#### Rule 4 — "I don't know" is a real answer

Most software treats "no answer" as a crash. So programmers avoid it, and guess
instead — because guessing looks like working, and crashing looks like failing.

In Plumb, `ABSTAIN` is a **normal, successful result**. The program exits happily.
It just tells you it couldn't say, and why.

> **Why this matters:** if saying "I don't know" is expensive or embarrassing,
> people stop saying it. Plumb makes it as cheap and ordinary as answering, so it
> actually gets used.

---

## Part 4 — Why multiply?

Look again at the shape of the health score:

```
result  =  capacity  ×  encode  ×  decode
```

It **multiplies**. That is deliberate, and it is the difference between an honest
score and a flattering one.

If you *added* the three parts, a project could be enormous and completely broken,
and still score well — its huge size would carry the total.

Because they multiply, **if any one part is zero, the whole thing is zero.** A
project with a million stars that nobody can contribute to scores nothing. Size
alone buys you nothing.

Try it with real numbers:

| Stars (size) | Can take input? | Can give output? | Added | **Multiplied** |
|---|---|---|---|---|
| Huge (1.0) | none (0.0) | good (0.8) | 1.8 — looks great | **0.0** — honest |
| Medium (0.5) | good (0.6) | good (0.6) | 1.7 — looks similar | **0.18** — clearly better |

The added column can't tell those two apart. The multiplied column can.

---

## Part 5 — For programmers: how you actually use it

### Where Plumb fits

**Plumb is a domain-specific language, not a general-purpose one.** No loops, no
user-defined functions, no I/O, no arithmetic beyond the declared operators.
Calling it "a new programming language" in the sense of Python or Rust would be an
overclaim, and the source file says so in its own docstring.

You will not write an application in Plumb. You write **the rule that decides
something**, in a form an auditor can read in thirty seconds and a court could
read in five minutes.

Think of it like SQL: nobody writes a whole app in SQL, but the moment your data
questions matter, you want them in SQL rather than buried in loops.

### The realistic workflow

```bash
# 1. Write the rule
$EDITOR rules/vendor.plumb

# 2. Lock it BEFORE you run it against real data
sha256sum rules/vendor.plumb > rules/vendor.lock

# 3. Run it
python3 plumb/plumb.py rules/vendor.plumb data.json --key repos

# 4. Anyone can re-run step 3 and get the same answer
```

Step 2 is the part people skip and shouldn't. Locking the rule *before* you see
results is what stops you from quietly nudging a threshold afterwards to get the
answer you wanted. If you change the file later, the hash changes, and everybody
can see it changed.

### Reading the output

```
program   : vendor-fitness
records   : 28   floor 0.02
blind     : ['description', 'topics']  (0 values physically removed)
two legs  : VIF 1.0041  VERIFIED_INDEPENDENT
verdicts  : 10 supported, 18 abstained (abstaining is a result, not an error)
```

Read that last line carefully. **18 out of 28 abstained.** That is not a failure —
the tool refused to guess 18 times. In most systems those 18 would have been
confident numbers, and you'd never have known which ones to distrust.

And note the honesty on line 3: *0 values physically removed*. It says `blind` was
declared, and that **nothing was actually there to remove** in this dataset. That
distinction is the difference between "blinding worked" and "blinding had nothing
to do", and it refuses to let you confuse them.

### If you're staying in Python

You don't have to adopt a new language to get the same four obligations.
`plumb/governance.py` provides them as ordinary Python decorators:

```python
from governance import verdict, blind, evidence, support, abstain

@verdict                      # rule 1: no bare returns allowed
@blind("self_description")    # rule 2: physically delete it
@evidence(3, of=4)            # rule 4's threshold
def assess(record, signals=None):
    if "self_description" in record:
        raise AssertionError("unreachable — the field was already deleted")
    reuse = record["forks"] / record["stars"]
    if reuse < 0.02:
        return abstain(f"reuse ratio {reuse:.3f} is below the floor")
    return support(round(reuse, 3), "measured from forks and stars")
```

If somebody later edits that function to `return 0.9`, it doesn't silently do the
wrong thing — **it raises an error immediately.**

Run `python3 plumb/governance.py` to watch the same input score `0.8` the ordinary
way and `0.300` the governed way.

> **Honest note:** this does *not* "transform Python". Python is not modifiable and
> nothing here changes it. What it does is make the obligations enforced *at
> runtime*, so a function that skips them raises instead of quietly returning a
> number. That is the real difference from a linter or a code-review checklist:
> neither of those can stop a running program.

---

## Part 6 — For auditors: what to actually check

If you are reviewing someone else's Plumb rule, here is the checklist, in order of
how often it catches something real.

**1. Is the rule file hash-locked, and was it locked before the run?**
If the lock file is newer than the results, the rule could have been tuned to fit.
This is the single most common way a good process goes bad.

**2. What is in `blind` — and was there anything there to blind?**
Check the output line `(N values physically removed)`. If it says `0`, the
blinding did nothing *on this data*. That may be perfectly fine — but it means
this run is not evidence that blinding works.

**3. Are the two legs genuinely different measurements?**
Look at the VIF number. Under 5 is the gate. But also read what the two legs
actually *are*: two different numbers computed from the same underlying source can
still pass a statistical check while being the same fact in disguise.

**4. What fraction abstained, and why?**
A very high abstain rate usually means the rule is mis-scaled rather than the
world being bad. In our own published run, 64% abstained — and that turned out to
be a property of the `1/(1+backlog)` formula flattening out for large projects,
**not** evidence that those projects were bad. We reported it that way. So should
you.

**5. Does the floor look like it was chosen before or after?**
A floor of `0.02` is a decision. Ask when it was made. A floor that happens to sit
just below the interesting result is a floor that was probably moved.

**6. Do the receipts actually verify?**
Re-run the program on the same data. The receipts should be identical. If they
aren't, something non-deterministic is in the pipeline and none of the above holds.

---

## Part 7 — The honest limits

This section exists because a tool that hides its limits gets trusted once,
wrongly, and then abandoned.

**Plumb checks structure. It does not check truth.**
A rule can be perfectly blinded, perfectly independent, fully receipted — and
still be a stupid rule. Plumb forces the obligations to be *visible*. It cannot
supply judgement, and nothing here should be read as claiming it can.

**A passing rule is not a good rule.**
"This program obeyed all four obligations" is a statement about the program, not
about the world.

**The receipts are tamper-evident, not tamper-proof.**
They do not prevent anyone editing history. They make editing history *visible*.
Those are different guarantees and the difference matters.

**It cannot check what data you chose to feed it.**
Blinding one field says nothing about the ten fields you didn't blind, or the rows
you didn't include.

**Of the five governance questions, Plumb addresses three.**
Purpose, stewardship, and reference-lock become `capacity × encode × decode`,
`independent`, and `blind`. **Questions two and five are not resolved here, and
are not resolved anywhere in this repository.** They are outside what any software
can check. Naming that boundary is part of the work, not a gap in it.

---

## Part 8 — Try it in five minutes

```bash
git clone <this repo> && cd ihcei-ecosystem

# the worked before/after — 0.8 vs 0.300
python3 plumb/governance.py

# a real rule over 28 real software projects
python3 plumb/plumb.py plumb/examples/vendor.plumb \
        github-lism/data/github_cohort_frozen.json --key repos

# the negative control: both checks read the same column.
# it HALTS and refuses to answer. exit code 3.
python3 plumb/plumb.py plumb/examples/collapsed.plumb \
        ei-dashboards/data/qwen_deepseek_frozen.json --key repos

# the 41 tests that hold all of the above in place
python3 -m pytest -q plumb/
```

### Your first rule

Copy `plumb/examples/vendor.plumb`, change the field names to match your data, and
run it. Then deliberately break it — point `encode` and `decode` at the same
column — and watch it halt. **Seeing a tool refuse to answer is the fastest way to
understand what it is for.**

---

## One-page summary

| | Ordinary code | Plumb |
|---|---|---|
| Return a bare number | allowed | **impossible** |
| Ignore a field | by convention | **deleted before evaluation** |
| Two identical checks | runs fine, sounds confident | **halts** |
| Say "I don't know" | usually a crash | **a normal result** |
| Prove how an answer arose | read the source and hope | **receipt, checkable** |
| Change the rule after seeing results | invisible | **hash changes, visible** |
| Decide whether a rule is *wise* | your job | **still your job** |

The last row is not a weakness. It is the only honest place to draw the line.
