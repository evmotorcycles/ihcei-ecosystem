# What ordinary people actually use these for

Four tools, four jobs. This document answers three questions honestly: what is
each one *for*, how does a person actually use it, and what would bring them
back. It also answers a fourth question nobody usually asks out loud — **where
each tool stops being useful** — because a tool that oversells itself gets used
once.

---

## A note on the valuation framing

The brief for this work asked how each tool reaches a trillion-dollar valuation.
I can't answer that, and I'm not going to pretend to. Valuations depend on
markets, competition, capital, distribution and timing — none of which is
visible from inside a repository, and none of which I can measure. Any number I
gave you would be invented.

What I *can* do is the part that is actually checkable: name the specific job
each tool does, the moment a person reaches for it, and the honest reason they
would or wouldn't come back. That is the real input to any valuation, and it is
the only part of the question I can answer without making things up.

One structural observation, offered as a caution rather than a forecast: **the
retention model here is genuinely harder than a chatbot's.** A chatbot is
retained by dependence — you come back because you can't do the thing yourself.
These tools are designed to leave you *more* able to judge without them. That is
the right design and it is a harder business. The honest source of repeat use is
not dependence but **frequency of the underlying event**: new claims arrive
constantly, new apps ask for access constantly, records need adding constantly.
The tool doesn't need you to need it. It needs the world to keep generating the
situation.

---

## 1. Check a claim — *Cairn EI*

### The job
You were told something and you don't know whether to act on it. Not "is this
true" — nobody can hand you that. The job is: **what would I need to check, and
what is missing right now?**

### When a person actually reaches for it
- An AI gave a confident answer with no source, and it matters enough to verify.
- A relative forwards a health claim about a supplement or a diet.
- A tradesperson, a salesperson or a landlord makes a specific factual assertion.
- A news headline states a statistic and you want to know whether the number is
  attached to anything.
- A student is deciding whether a source is usable in an essay.
- A manager gets a one-line claim in a slide deck and has to sign off on it.

### What using it looks like
Paste the sentence. Press one button. You get back:
- which of five checkable things are present — source, numbers, method, date, scope;
- **what to ask for next**, phrased as a request you can send verbatim;
- a warning if the topic is one where being well-written and being safe are
  different things (chemicals, health, money, law, anything load-bearing).

Thirty seconds, no account, nothing leaves the device.

### Where it stops
It does not know whether the claim is true. A well-sourced lie scores well. It
does not understand language — the ambiguity check is pattern matching and the
plausibility check reads a hand-written list of fifteen landform nouns. It is a
*missing-evidence detector*, not a fact-checker, and calling it one would be the
overclaim that makes people stop trusting it.

### Why someone comes back
Because the situation recurs weekly and the output is a **script for the next
message**, not a verdict. "Can you tell me where that figure comes from?" is
useful every time, and gets easier to send when a tool wrote it for you. The
repeat use is the asking, not the scoring.

---

## 2. Decide what an app may touch — *Page Code*

### The job
Something wants access to your files — an AI assistant, a browser extension, a
contractor's tool. The job is: **say what it may have, once, in plain words, and
have everything else refused without you having to think of it.**

### When a person actually reaches for it
- Installing an AI assistant that asks for access to a whole drive.
- Letting a bookkeeper's tool at the accounts folder but nothing else.
- Giving a contractor access to one project directory for six weeks.
- Any moment where the only options offered are "allow everything" or "don't
  use the thing".

### What using it looks like
A short list in ordinary language: *read anything in projects*, *change drafts,
five times then ask again*, *never touch payroll*. Then a box where you type any
file and see immediately whether it would be allowed, and which rule decided.

The important part is the last line of the table: **everything else — refused.**
You never have to predict the bad request. You only have to describe the good
ones.

Two rules that make it safe rather than merely tidy, both enforced in the code:
a refusal always beats a permission, so a broad "allow" can never shadow a
narrow "deny"; and among permissions the most specific rule wins, so the limit
you see is the limit that applies.

### Where it stops
It stops an app reaching what it was never granted. It does **not** stop an app
misusing what you *did* grant, and it cannot tell you whether the app is
trustworthy. Grant the smallest thing that does the job.

### Why someone comes back
Every new tool is a new grant, and grants need revisiting when the job ends. The
returning moment isn't "let me check my permissions" — nobody does that. It's
"I'm installing something new", and that happens constantly.

---

## 3. Keep a record nobody can quietly edit — *HELM*

### The job
You need to be able to show later what was agreed and when — to a landlord, an
insurer, a client, a committee, or yourself in six months. The job is: **a log
where changing an old line is visible.**

### When a person actually reaches for it
- Building work: quotes, deposits, dates, changes to scope.
- A dispute with a landlord or a service provider.
- Care notes shared between family members looking after a relative.
- A community group or a small charity recording decisions and who took them.
- Anyone keeping a lab notebook, a maintenance log, or a handover record.

### What using it looks like
Type what happened, press add. Each entry gets a seal that includes the entry
before it. Change an old line and every seal after it visibly breaks — the page
shows you exactly which entry was altered. There is a button that does this on
purpose, so you can watch it work before you trust it.

### Where it stops
It makes tampering **visible**, not impossible. It says nothing about whether an
entry was true when it was written — someone can still write a lie; they just
can't rewrite it later without it showing. It is also not a legal instrument on
its own.

### Why someone comes back
Because a record is only worth having if it's continuous, and a gap is a hole in
the thing you'll rely on. The habit is the product. This is the one tool here
whose value genuinely compounds with use.

---

## 4. See whether confidence matches reality — *CI*

### The job
Everything else on your screen states confidence. Almost nothing tells you
whether that confidence has ever been checked. The job is: **compare what a tool
claims against an independent measure it never saw.**

### When a person actually reaches for it
Honestly — rarely, and not on their own initiative. This is not a daily tool for
most people. It matters when someone is deciding whether to trust a system at
all: a procurement decision, a school choosing software, a regulator, a
journalist, or a person who has just been burned by a confident wrong answer.

### What using it looks like
You read one number and one sentence. In our own case: we set a limit of 0.15
before running, measured **0.3727**, and failed. The bars show the tool was
consistently *less* confident than reality warranted, and the page says so on its
face rather than in a footnote.

### Where it stops
It measures calibration on one cohort, of twenty-two projects, on one definition
of ground truth. It is not a general safety certificate.

### Why someone comes back
They mostly don't, and I'd rather say that than invent a retention story. Its
real function is **trust transfer**: it is the page you show someone when they
ask why they should believe the other three. A tool that publishes its own
failure is making a claim about itself that a marketing page cannot make.

---

## How the four fit together

They are the same discipline applied at four points:

| | The question | The tool |
|---|---|---|
| Before you act on information | what's missing from this? | Check a claim |
| Before you grant access | what exactly am I handing over? | Page Code |
| After something happens | can this record be quietly changed? | HELM |
| Before you trust the tools themselves | has their confidence been checked? | CI |

The common thread is that each one **replaces a feeling with something
checkable** — and each one tells you where it stops. That last part is not
modesty. A tool that hides its limits gets trusted once, wrongly, and then
abandoned. A tool that states them gets used correctly for years.

---

## What we are not claiming

- Not that any of this makes a claim true.
- Not that structural soundness means safety — the app says so on every result
  that touches health, chemicals, money or law.
- Not that our own confidence scores are well calibrated. They are not; we
  measured it, failed, published the number, and did not move the limit.
- Not any valuation, market size, or growth figure. Those are not measurable
  from here.
