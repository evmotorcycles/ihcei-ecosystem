# Cairn — an Epistemological Interface

**Open it:** `cairn/cairn.html` — double-click. No server, no install, no account, no network.

---

## The name

A **cairn** is a stack of stones marking a trail. It works because:

- it is built **stone by stone by everyone who came before** — cumulative, public evidence;
- you trust it **because you can see it**, not because someone told you to;
- and when there is **no cairn**, you immediately know you are off-trail.

That is abstention, verifiability and accumulated evidence in a single image — which is
exactly what an Epistemological Interface is for. The verification engine inside is called
**Assay** (an assay measures what a sample actually contains, ignoring its label).

---

## The four models

| model | who it's for | what it does |
|---|---|---|
| **Cairn Flint** | everyone, free | Instant and **fully on-device**. Nothing leaves your machine. Everyday questions, private by construction. |
| **Cairn Slate** | students, professionals | The balanced default. Everyday work, study, drafting — with evidence shown on every answer. |
| **Cairn Granite** | researchers, corporations | Deep verification. Cross-checks sources **against each other**, not just against itself. |
| **Cairn Quartz** | governments, regulated sectors | Audit and compliance. Sealed receipts, retention rules, **sovereign deployment** inside your own jurisdiction. |

Named for stone, because a cairn is built from it — and because each is harder and slower
than the last, which is exactly the trade you are making.

---

## What an EI is, and how it differs from an AI assistant

Both take a question and return text. **What they optimise for is opposite.**

| | an AI assistant | **Cairn (an EI)** |
|---|---|---|
| **Optimises for** | an answer that *sounds* helpful | an answer you can *check* |
| **Confidence is** | a writing style | a **measurement**, shown as a value |
| **When evidence is thin** | writes something plausible anyway | **abstains, and names what's missing** |
| **When it refuses** | policy ("I can't help with that") | evidence ("there isn't enough here") |
| **Reputation of a source** | often treated as a quality signal | **weighted zero**, by construction |
| **You verify it by** | trusting the vendor | **re-checking the receipt yourself, offline** |
| **Its goal for you** | keep you engaged | leave you **able to decide without it** |

The core difference in one line:

> **An AI assistant tries to give you the best answer. An EI tries to give you an accurate
> picture of how much any answer can be trusted — including its own.**

That makes it a worse toy and a better instrument. You would not want Cairn to write you a
poem. You would want it before signing a contract, submitting a thesis, approving a
supplier, or publishing a national statistic.

**What it is not:** Cairn is not a fact-checker that pronounces "true" or "false", and it is
not an oracle. It measures **how much checkable support a claim actually has** and shows you
the gap. Most real claims land in the middle, and saying so is the product.

---

## The interface

Deliberately familiar — anyone who has used a chat assistant can use Cairn immediately.

- **New chat / Chat** — ask anything; every answer carries its evidence panel
- **Projects** — sources, rules and receipts kept together so a team shares one evidence base
- **Artifacts** — documents and dashboards Cairn built, each carrying the evidence behind it
- **Connectors** — where Cairn is allowed to look; **read-only by default**
- **Page Code** — the permission table; **default-deny**, and only you can widen it
- **Customize** — how careful it is and how much it shows *(you can hide detail; you cannot make it pretend)*
- **Design** — appearance, language, accessibility

Every answer shows: **confidence** (measured, not styled), **what I checked** (with failures
as visible as passes), and a **receipt** you can re-verify later.

---

## Verified running in a real browser

Driven headlessly over the Chrome DevTools Protocol — not a mock-up:

```
TITLE     : Cairn — the Epistemological Interface
MODELS    : Cairn Flint | Cairn Slate | Cairn Granite | Cairn Quartz
NAV ITEMS : Chat · Projects · Artifacts · Connectors · Page Code · Customize · Design

--- vague input "is it good" ---
ABSTAINED : true
CONFIDENCE: insufficient

--- evidence-rich input (figures + method + date + scope) ---
CONFIDENCE: moderate
CHECKED   : — No source is named | ✓ Contains specific figures | ✓ Says how it was measured
            | ✓ Anchored to a date or period | — Scope is not stated
RECEIPT   : e127e2a99d606169 · 3/5 evidence signals · re-checkable offline

MODEL SWITCH -> Cairn Quartz / badge: sovereign · sealed
PAGE CODE : 6 rules; default row = (anything not listed) · any · deny · default
```

Note the second result: the input was **good but not perfect**, and Cairn said so —
crediting the figures, method and date while flagging the missing source and scope. It
neither rubber-stamped nor dismissed it. That middle register is the whole point.

Screenshots: `screen_chat.png`, `screen_models.png`, `screen_pagecode.png`.

## Honest scope

`cairn.html` is a **working demonstration of the interface and its behaviour** — the
abstention logic, evidence scoring, permission table and receipts are real and run
on-device. It is **not** wired to a language model; it demonstrates the surface people
actually use and the guarantees that surface makes. The verification machinery it reflects
(`adversarial-kernel/`, `agency-constitution/`, `echo/`, `page-code/`) is separately tested
in this repository.

## Files

```
cairn/
  cairn.html          the GUI — open it directly
  CONSTITUTION.md     the ten articles, each externally testable
  README.md           this file
  screen_*.png        captured from a real headless Chrome session
```

---

## The Python engine, wired to the browser

```
python3 cairn/ei_server.py     # starts the engine on 127.0.0.1:8765
# then open cairn/cairn.html — the header badge flips to "engine: python"
```

`ei_llm.py` is the engine (pure stdlib, importable, testable). `ei_server.py` serves it
locally — bound to `127.0.0.1` only, so nothing it sees leaves the machine. If the server
isn't running, the GUI falls back to its built-in on-device logic and says so in the badge.

## Hinton's Grand Canyon test, run against an EI

Hinton told a chatbot *"I saw the Grand Canyon flying to Chicago."* It attached the
participle to the object, objected that the canyon can't fly, was corrected, and said *"Oh,
I see. I misunderstood you."* His argument: you can't **mis**understand without attempting
to understand.

**Cairn answers differently, and that is the point.** The sentence is a participial
attachment ambiguity — the text alone does not determine which reading was meant. So it
declines to commit:

```
verdict   : AMBIGUOUS      committed answer: None
 (A) attaches to subject   plausible=True   I was flying to Chicago, and I saw the Grand Canyon
 (B) attaches to object    plausible=False  I saw the Grand Canyon, and the Grand Canyon was flying
asks      : Which did you mean — were you flying, or was the Grand Canyon flying?
receipt   : b74961f0c896fb43
```

Then the correction turn (`"No, it was me flying to Chicago."`) produces:

```
receipt 81c9375bb5b92782 · revises b74961f0c896fb43
```

**An assistant says "I misunderstood" and the prior state is gone. An EI keeps both states
linked**, so the revision can be inspected later by someone who trusts neither party.

### The anti-overclaim control — the only informative gate

Give it a structurally identical sentence where **both** readings are perfectly sensible —
*"I photographed the woman walking to the station."* — and it flags that too. **That proves
it is doing syntactic pattern matching, not comprehension.** It does not know what a canyon
is; it knows what a participle is attached to. The plausibility check reads a hand-written
list of 15 landform nouns.

**So this does not refute Hinton, and does not claim EI understands anything.** Hinton's
argument concerns whether a system builds a semantic model; this experiment does not engage
that question. What it shows is narrower and checkable: **on underdetermined text an EI
declines and asks where an assistant commits and later apologises — and the EI's revision
leaves an audit trail.** A claim about failure modes and accountability, not intelligence.

Reproduce: `python3 cairn/hinton_test.py` · guard: `python3 -m pytest cairn/test_ei_llm.py`
Verified in a live browser: `screen_hinton.png`.


---

## v1.1 — what the field audits changed

Real usage surfaced three problems. All three are fixed, and the fixes are locked in
`test_ei_llm.py`.

### 1. Definitions no longer look like failures *(the big one)*

Pasting *"Epistemology is the study of knowledge"* used to return a red **0/5
INSUFFICIENT_EVIDENCE**. That is a correct engine looking broken — the text was never
auditable in the first place. Cairn now **routes the claim before scoring it**:

| input | routed as | shown as |
|---|---|---|
| *"Revenue rose 14% in Q3, per the annual report"* | EMPIRICAL | audited normally |
| *"Epistemology is the study of knowledge"* | CONCEPTUAL | **out of scope, no score** |
| *"I think green tea is great"* | OPINION | **out of scope, no score** |
| *"What is inflation?"* | QUESTION | **out of scope**, offers to audit an answer |

Out-of-scope renders in **neutral grey with no number at all** — because a score people
read as a grade is a grade. The receipt line reads `no score — nothing to measure`.

### 2. Structure is never mistaken for safety

An audit gave an un-emulsified glycolic-acid serum **3/5** — it was well-specified *and*
chemically unstable. A user could read that as "mostly fine". Cairn now detects
**domain risk** (chemistry, medical, legal, financial, safety-critical) and says so:

> **I checked the wording, not the subject matter.** This touches **medical/health**. A
> well-formed claim here can still be wrong or unsafe — a specialist has to review the
> content itself. My score says nothing about that.

### 3. Every uncertain result carries a next move

Low or out-of-scope results now list **what would settle it** as clickable prompts, so the
user leaves with an action rather than anxiety.

### Onboarding teaches the boundary *first*

A four-step overlay runs before the first audit, and step two is the empirical/conceptual
line side by side — the distinction that caused the 0/5 confusion. Re-openable any time
with `?`.

### Navigation

`Ctrl/Cmd-K` command palette (13 entries: jump to any panel, switch model, new chat),
`?` for help, a working mobile drawer under 820px, and keyboard navigation throughout.

---

## The compute question, measured

*"Won't an EI need as much compute as an LLM?"* — for the deterministic tier, no, and this
is measured rather than asserted:

```
20,000 audits in 1.475s  ->  73.7 microseconds each
13,563 audits/sec/core   ->  CPU only, no GPU, no model weights, no network
```

**Honest caveat:** that is the *deterministic* tier — regex, a lexicon and arithmetic. The
moment an LLM is used for semantic parsing, its compute cost is inherited in full. The
architecture that stays cheap is **deterministic-first, escalate rarely**: route and score
every claim for microseconds, and spend model compute only on the minority that needs it.
Cairn is cheap because most claims never reach a model — not because auditing is magic.
