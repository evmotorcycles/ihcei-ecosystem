# Pre-registration — is this an operating system, or a set of libraries?

**SHA-256 locked in `prereg.lock.json` before the tests were run.**

---

## The claim being tested

The proposal is that Cairn, Page Code, HELM, Trig, the nine Novora screens, the
governed learner and Plumb together constitute a **Governance OS** — a kernel for
agent-era computing, with the reasoning layers as headless drivers.

That is a structural claim about software, and structural claims about software
are testable. This module tests it, and expects several of the tests to fail.

## What actually makes something an operating system

Not "a collection of useful tools". Four properties, each of which is a
yes-or-no question about the code:

| | Property | The test |
|---|---|---|
| **1** | **Interposition** — it sits between a program and a resource, so the program cannot reach the resource without going through it | Can any component here *block* an action, or does it only return an opinion about one? |
| **2** | **Mandatory** — a program cannot opt out | Is there any path that reaches a resource without consulting the permission table? |
| **3** | **Composition** — the output of one part is the input of the next, with no manual translation | Does a permission decision flow into a record, and a record into a check, without a human gluing them? |
| **4** | **Degrades safely** — when metadata is missing it restricts rather than proceeds | On inputs with no evidence at all, does every component decline? |

An OS that only satisfies (3) and (4) is a **library**. That is not an insult;
most valuable software is a library. But the distinction decides what may
honestly be promised.

---

## Pre-registered predictions

- **O1 — interposition FAILS.** No component in this repository can prevent an
  action. Page Code returns `{decision, reason, rule}`; nothing consumes that
  return value at a point where the action could be stopped.
  *Falsified if* a component is found that actually blocks.

- **O2 — mandatory enforcement FAILS.** There is no hook, no syscall
  interception, no filesystem driver, no browser extension, no OS integration
  anywhere in this repository.
  *Falsified if* any such integration point exists.

- **O3 — composition PARTIALLY HOLDS.** A permission decision, a record entry
  and a claim check can be chained programmatically without human translation,
  but they do **not** share a common record type.
  *Gate:* chaining is demonstrated end to end in code; the schemas are compared
  and any mismatch is reported rather than smoothed over.

- **O4 — safe degradation HOLDS.** Given an input carrying no evidence, every
  component declines rather than emitting a confident value.
  *Falsified if* any component returns a displayable score on empty input.

- **O5 — the honest label.** Given O1–O4, the artefact is named for what it is.
  If interposition and mandatory enforcement both fail, the word "OS" is not
  used for it in the documentation, and a test enforces that.

**No gate will be altered after the results are seen.** If O1 or O2 unexpectedly
passes, that is a finding and the label changes accordingly.

---

## Why this matters more than it looks

An operating system's whole value is that a program *cannot* go around it. If a
permission table only advises, then an agent that ignores it is unaffected, and
the person relying on it is worse off than if they had no table — because they
believe they are protected.

The distinction is therefore not pedantry about vocabulary. **Calling a library
an OS transfers a guarantee to the user that the code does not provide.**
