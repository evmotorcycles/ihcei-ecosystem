# Plexus

**See what a thing is made of, what is holding it up, and what it rests on.**

One file. Open it on a phone, a laptop, or a USB stick. No account, no server, no
network — it works with aeroplane mode on.

```
python3 plexus/build.py                 # writes app.html + the install files
python3 -m pytest -q plexus/            # 25 tests: browser vs Python, offline
node plexus/parity_dump.mjs             # what the browser engines answer
```

---

## Three questions, three tabs

| Tab | Asks | Engine |
|---|---|---|
| **Map** | How does it fit together? | LMD — distance is effective resistance on the dependency graph |
| **Holding it up** | Is there another way *round* this step? | SPAR — `w × R`, the chance a link is load-bearing |
| **Resting on** | Is there another way *in*? | FATHOM — remove each source and see what falls over |

The last two can disagree, and when they do it is worth reading both. That is
not a wrinkle; it is the finding that produced FATHOM in the first place —
route redundancy is not evidential independence, and it has the sign backwards.

---

## Installing

| | What you get | How |
|---|---|---|
| **Open the file** | the whole app, offline, every platform | double-click `app.html` |
| **Install to home screen** | an icon, its own window, no browser chrome | serve the folder over https, then "Add to Home Screen" / "Install" |

Installing needs the page **served** (https or localhost) because that is what
browsers require before registering a service worker. That is a browser rule and
no version of this app gets round it, so both paths are provided rather than one
being claimed to cover the other.

---

## Five things in the proposed design that were not built as specified

Each was tested before being rejected.

**1 · The client-side pseudo-inverse crashes on a broken graph.**
`L⁺ = (L + J/N)⁻¹ − J/N` holds only for a *connected* graph. With *k* pieces,
`L + J/N` has nullity `k − 1`, so the Gauss–Jordan step throws
`Matrix singular` — and a broken structure is exactly the case a person needs
the app to survive. Measured: the spec engine throws; the shipped engine returns
`Infinity` and reports `pieces = 2`.

**2 · The server-side version does not crash — it lies.**
`pinv` without a component check returns a *finite* distance between two things
with no path at all: `1.118` across a cut, against a genuine `1.732` inside one
piece. The unreachable pair reads as *nearer* than the reachable one.

**3 · A Flask backend breaks the one property worth having.**
`python app.py` and `localhost:5000` is not something an ordinary person
installs, and it puts their bill on a server. Everything here runs in the page.

**4 · Gradient-descent MDS from a random start is not reproducible.**
Every load would give a different picture, and it reintroduces the map-flipping
defect that classical MDS plus Procrustes alignment was built to remove.

**5 · `E = U·D` already means something else.**
In this repository `E = U·D` is a pre-registered law with `D = D_enc · D_dec`,
tested across four cohorts, where the quadratic was **disconfirmed**. Reusing
those letters for "urgency × distance to focus" would collide a tested result
with an invented heuristic. The useful readout is kept; the name is not.

Suggested links from shared labels are offered as **suggestions only** and never
feed a bearing or a sounding until a person confirms them. Two things sharing a
word are not thereby dependent on one another.

---

## Defects found by driving the built page

- **The two header controls shipped at 36px.** Under the 44px floor, in an app
  explicitly for every age. Caught by measuring every visible button in every
  tab, not by looking.
- **The layout drew as small as it could get away with.** `min(need, cap)` picks
  the smallest scale that separates the boxes when any scale up to `cap` is
  valid — the picture sat in a corner of an empty card at 55% width. Now `cap`.
  The same latent bug was in `smi/app_template.html`; fixed there too, where it
  changed no measured number because `cap` was already binding.
- **Literal NUL bytes in the source.** They worked. They also made `grep` call
  the file binary, and any formatter that strips control characters would
  silently turn the pair separator into the empty string — merging different
  pairs onto one key. Escaped, and a test now fails if one comes back.

---

## What it cannot tell you

Whether a step is *useful*, or whether a source is *true*. A required form that
changes no outcome still reads 100%, because removing it does break the chain.
And it only knows the parts you entered.

---

Files: `app_template.html` + `engines.js` + `build.py` → `app.html`,
`manifest.webmanifest`, `sw.js`, `icon.svg` · `parity_dump.mjs` ·
`test_plexus.py`.

---

## Shapes — the contributed-structure commons

`commons.html`. Eight shapes people have already run into, each stored twice:
the way it is usually described, and the dependencies actually there. The number
on each card is the distance between those two.

| Shape | As described | As it is | After the fix | Gap |
|---|---|---|---|---|
| One person, three jobs | 0.333 | 1.000 | 0.250 | **66.7%** |
| Three audits, one threat model | 0.333 | 1.000 | 0.250 | **66.7%** |
| Three script files, one policy directive | 0.333 | 1.000 | 0.250 | **66.7%** |
| Twelve assets, all or nothing | 0.083 | 1.000 | 0.083 | **91.7%** |
| A password is one way in | 1.000 | 1.000 | 0.250 | 0.0% |
| Two evaluations, one corpus | 0.500 | 1.000 | 0.500 | **50.0%** |
| Forty packages, one registry | 0.025 | 1.000 | 0.250 | **97.5%** |
| Six models, one hub | 0.167 | 1.000 | 0.250 | **83.3%** |

Every number is computed at load by `commons.js` from `library.js`; none is
typed into the page, and a test asserts the markup contains no figure at all.

**The first three rows share no word and measure identically, to 1e-12.** That
is the only reason a shape from someone else's field is worth anything in
yours, and it is the one test in `test_commons.py` marked THESIS: if it ever
fails, the library is a list of opinions and should be deleted.

**The pattern that fell out of it.** In the drawn slot, dependence is exactly
`1/n` for `n` supports contracted onto one conclusion, while the actual slot
reads 1.000 whenever there is a single hidden origin. So the gap is `1 − 1/n`:
*the more independent-looking things you list, the more reassuring the number
and the wider the error.* Noticed after the results arrived, not predicted, and
recorded as such.

### A structure is parts and links, and there is nowhere to put anything else

`validate()` refuses any key beyond `parts`, `links`, `sources`, `conclusion`.
Not because a fifth key must be personal data, but because a free-text box on a
shared record is where a name ends up — and then the commons is a database and
non-possession is a slogan. There is nothing to sanitise because there is
nowhere to put it. Every entry also carries `provenance.kind`, either
`measured-here` (a defect found in this repository, file named) or `cited` (a
documented mechanism anyone can check), and `licence: CC0-1.0`.

### Where these came from, and where they did not

The task named GitHub and HuggingFace as places to mine problems. Neither was
mined. This session's GitHub access is scoped to two repositories, so
repository-wide and global search were out of scope and unused, and there is no
paid API, no key and no scraping. Two entries were measured here; six cite
mechanisms whose behaviour anybody can verify from a specification or a lockfile.
Nothing claims a provenance it does not have.

### What none of it shows

That a commons raises a valuation ceiling. That claim rests on a contribution
rate, and `contributionRate()` is written so it **cannot return a number** while
there are no buyers — precisely so no later version can substitute a measurement
from this file for the one that matters. The gate, set before any of this ran:
**5% of buyers contribute a shape within 60 days of shipping.** Below that, the
fourth pillar was imaginary.

Eight shapes written by one person in one sitting is a worked example, not a
commons. Three of them share a shape; I wrote all three, so the recurrence is
evidence about me until a shape arrives from someone who never read this file.

Predictions were locked before anything ran:
`plexus/commons_preregistration.md`, sha256
`25e2df1112521cb353c5017429d51686dfeef53a48c74ab00ff1007f0d5885be`, asserted by
the suite so they cannot be edited after the fact.

---

## Mask and lens — the paradigm, as something that fails CI

Both are abstractions. The difference is what they do next.

| | **Mask** | **Lens** |
|---|---|---|
| The picture is | the destination | a handle |
| After it you | stay inside the product | leave and check something |
| Hidden | what is being collected, ranked, kept | little; the limits are printed |
| Example | "cloud", "folder", "For you" | "sole route", "no source named" |

Newton's cannonball and Einstein's falling lift were lenses: pictures that
existed to reach a measurement, and the measurement was allowed to kill them.
A manifesto saying so would cost nothing, so it is a file instead. `lens.js`
makes every tool register three things:

- **measures** — what it actually computes
- **cannot** — what it will not tell you, in the exact words its page must print
- **goCheck** — what a person does *next*, outside this software, with their own eyes

`register()` refuses a tool with no `cannot` ("what an oracle looks like") and a
tool with no `goCheck` ("nowhere to go, so its picture is a destination"). Then
`test_gate.py` asserts every shipped page prints its own limits and at least one
of its checks, compared on collapsed whitespace because that is what a reader
sees. Edit a limit in `lens.js` without editing the page and the build fails in
the same commit.

**Its own limit, which is registered too:** this checks that a refusal is
*printed*. It cannot check that a refusal is *true*, and no test here can.

---

## Agent Gate

`gate.html`. Say where an assistant may work in your plan, and where there is no
second way round. Three readouts, never added together.

| Readout | What it is | Measurable when |
|---|---|---|
| **Perimeter** | which links lie inside the boundary you drew, which cross out, and what they would reach | now — set arithmetic, nothing to tune |
| **No way round** | links with bearing 1.000: in every spanning tree, so there is no other path | now — Foster arithmetic |
| **Your own backlog** | is your time-to-close on flagged problems rising, against your own history | only with a history; otherwise it says so |

On the worked example: 2 links cross the boundary (reaching *the deposit* and
*the order ships*), exactly 1 step has no alternative, and the backlog reads
**not enough history** — which is what every fresh install reads, and is the
honest answer rather than a defect.

### What it is deliberately not built on

The design asked for was `∏Dᵢ < D_min`: each hop reports a fidelity, multiply
them, stop when the product drops below a floor. **This repository already
retired that gate, on its own data** (`FLOOR_RETIREMENT.md`):

- the sensor that would supply `D` reads zero on 89.8% and 83.7% of 3,685 pull
  requests — it fires on 23.4%, so the gate would be blind three times in four;
- the pre-registered confirmatory run on an unseen cohort of ~4,979 pull
  requests returned a **fully-powered null, p = 0.735**;
- the replacement — a hazard on enforcement latency — scored **AUC 0.898**
  against 0.828 for the deterministic floor.

So `gate.js` contains no `D_min` and no fidelity product. `retiredFloor()`
returns the record with those numbers in it, and a test asserts the name appears
exactly once in the file, on the line that says it is retired. Putting a
falsified floor back inside the one tool whose whole claim is that it prints its
limits would be the most complete way to disprove the claim.

The hazard is a JS port of `tau_v_monitor/core.py`, run against the Python over
eight synthetic histories — flat, rising, falling, noisy, a jump, a thin
history, a short one, and one with an open backlog — agreeing on status and
trend direction exactly and on every statistic to 1e-9. The port includes a
Taylor-series `erf` below |x| = 3, because the usual rational approximation has
a fractional error of 1.2e-7 and the Mann–Kendall *p* is an erfc: parity at
1e-9 would otherwise be measuring the approximation.

Predictions locked before anything ran: `plexus/gate_preregistration.md`, sha256
`543c29ee1050d354e63f7a2de02cc04dc1c1dcc5973e1af7b5bf35f25cfcb98a`.

### What it does not show

Nothing here shows an assistant gated this way is safer, cheaper or better.
Perimeter and sole routes are structure; the backlog is latency; whether anyone
acts on either is unmeasured and unmeasurable from inside the tool.

---

## Packs — the structure arrives already built

`packs.html`. The blank canvas is a defect: asking somebody holding a bill to
name six parts and draw five links before the software says anything is
homework, and the mask asks for one tap. Tap the kind of paper you are holding,
type the numbers off it, done.

| Pack | Numbers you type | Parts + links you would place by hand |
|---|---|---|
| A metered bill | 6 | 11 |
| A payslip | 5 | 11 |
| An invoice with tax | 3 | 8 |
| A deposit coming back | 5 | 11 |
| Splitting something | 2 | 5 |
| Paying in instalments | 4 | 13 |
| **All six** | **25** | **59** |

A test asserts `asks < parts + links` for every pack. If a pack is not less work
than drawing it by hand it has no reason to exist and should be deleted rather
than argued for.

### Two answers, never fused into one

**The arithmetic**, recomputed from scratch: either it matches or the difference
is named. **The structure**, separately: which steps have no second way round.
One green tick covering both would be the most reassuring thing the page could
show and the least true — a bill can be arithmetically perfect and rest entirely
on one meter reading nobody checked.

The worked case: reading 70 against 58, at 5032 a unit, plus 1700 standing
charge → 12 units, 60384, **62084**, and the printed total follows. Pay 65000
and 2916 carries forward.

### Two carried-forward figures, found by driving the page

Change the printed total to 63000 and a single "carried to next time" quietly
becomes 2000 — measured against what they *asked*, not against what the parts
*come to*. Both are real, they mean different things, and which one you are owed
depends on who is right about the 916, which the page cannot know. So both are
shown. They read the same whenever the bill matches and diverge by exactly the
amount in dispute when it does not.

### What is refused, and what is never invented

- A blank optional field makes its row **vanish**, never read 0. Software that
  turns a blank into a zero has invented a number, and inventing numbers is the
  thing this stack exists to catch.
- A missing required number is named, and everything downstream of it is absent.
- Dividing by zero is refused with a reason, never shown as infinity.
- `5,032` and `1 700` are accepted, because that is how the paper prints them.
- A pack with no declared assumptions is refused: the flat-rate assumption is
  the whole reason a stepped tariff will not match, and a person not told that
  will read the difference as an accusation.
- The verdict never says overcharged, wrong, error or owe. A test greps for those
  words. It knows two numbers differ; it does not know who is right about the
  tariff, the reading or the law.

### Why the rest-on reading is not run here

Every input to an arithmetic identity is required — units needs *both* meter
readings. That is a conjunction, and FATHOM's sources are disjunctive. It is the
same limit the Shapes library records as `atomic-install-list`. Run over a bill
it would report each meter reading at 0.0625, which is not unhelpful, it is
backwards. So packs run SPAR only, and the reason travels with the result as
data so a page cannot quietly stop printing it.

### No pack carries any real company's rates

Every seed pack is a general shape. A specific tariff nobody verified would be
worse than the blank canvas it replaces: a confidently wrong "what it should be"
arrives at the moment a person is least able to notice. Provider-specific packs
belong in the commons, from people holding the actual paper, with provenance
attached. A test greps `packlib.js` for currency symbols and company suffixes.

Predictions locked before anything ran: `plexus/packs_preregistration.md`, sha256
`bc23a73a33c9261eec98c95bf0cea85bcbaf8a7fa9385c073168e96d9835a2a4`.

**Registered null:** counting what a person types is not usability. Nothing here
measures whether somebody tired at the end of a long day finds this easy. That
needs people, and there are none in this repository.

---

## Press — the Lens algorithm

`press.html`. Paste what you were told. It presses out the things you could go
and check, and names the one to do first.

The logic is borrowed and the vocabulary is not: a pomegranate is peel, bitter
pith and seeds around the part you want, and you do not argue with the peel —
you press it, and what runs out is what you can use. Whatever does not run out
was never going to nourish anybody, however good the fruit looked. Truthfulness
is manner; truth is what survives the pressing. A test greps `press.html` for
the source's terminology and fails if any of it appears.

### What it measures

**How fast reality could contradict this, if reality disagrees.** Not whether it
is true, not how likely, not how good.

The consequence has to be said before anyone meets it as a bug:

> A completely fabricated claim carrying a named body, a year, a percentage and
> a stated method reads **maximum**. A careful, honest, vague statement reads
> **nothing**.

That is correct. The fabrication has staked something and can be destroyed with
one phone call. *“Industry experts generally agree that our meters are highly
accurate”* cannot be destroyed at all — which is why fog survives every argument
and specifics die. Pressing a well-made lie traps it inside its own structure;
pressing fog produces nothing, and the tool returns **no number** rather than a
low one.

A fabricated claim and a true one of the same shape return **identical numbers,
to 1e-12**, sharing no word. That is the test marked THESIS. If it ever fails,
the engine has begun guessing about the world and should be stopped rather than
improved.

### The finding: 1/m², exactly

Marks do not attach to the claim — they attach to the **origin** they are
attributed to, because a figure attributed to a report is worth nothing if the
report does not exist. That one modelling choice produces an exact law:

| Handles on one origin | Each one settles |
|---|---|
| 1 | 1.000 |
| 2 | 0.250 |
| 3 | 0.111 |
| 4 | 0.0625 |
| 5 | 0.040 |

**Five handles do not give you five ways to check.** They give you one way to
check, dressed as five, and each reads 0.040 *because* the graph is saying they
are not independent. The reassuring number is the warning. Split the same four
marks across two genuine origins and each rises to 0.125.

This is the fifth appearance of the shared-origin shape in this repository.

### The check to do first

Computed by removal, never by a rank anyone assigned: the part whose removal
leaves the rest in pieces. On a claim citing an unnamed audit that comes out as
*“Ask where this came from. Until something is named there is nothing to open.”*

### A prediction that missed, and the defect behind it

L4 predicted two single points with two origins. There are **three**: with two
origins hanging off it, the claim node is itself a cut vertex. The arithmetic
was right and the hand calculation was wrong — and it was not just a wrong
number, it was a defect. `firstCheck` took the first single point, so on any
two-origin claim the tool told the reader to go and open *“The claim stands”*.
The claim node is now excluded and `test_the_prediction_that_missed` pins both
the correction and the miss. The pre-registration was not edited.

Marks come from `cairn/ei_engine.js`, inlined rather than copied, so the page
cannot grow a private copy that drifts. It matches words and does not read: on
the worked example it misses the source entirely, because neither *authority*
nor *audit* is in the pattern it looks for. That is registered as a null, not
patched by widening a regex until it fires on everything — a person can add or
strike any mark with one tap.

Predictions locked before anything ran: `plexus/press_preregistration.md`, sha256
`a72e5d6950ae55db446479f40e472b288008068a7f0758ad6b3789c2bdfb48eb`.

---

## Lens or mask — auditing a picture, including our own

`metaphor.html`. Newton imagined light as tiny billiard balls. The picture
predicted the angle off a mirror, the bend into glass, and a perfectly sharp
shadow. **Two of those came back false** — light travels slower in water, not
faster, and it does bend round an edge. The picture died of its own predictions,
and that is exactly what made it a lens.

So one question is asked of any picture: **what does it predict that could come
back false, and who is able to make that prediction come true?**

| Class | Test | Count |
|---|---|---|
| **lens** | predicts at least one thing the presenter does **not** control | 5 |
| **self-referring** | predicts only things the presenter controls | 4 |
| **notation** | predicts nothing at all | 3 |

### The finding on MetaphorOS

All four audited metaphors — *a wider pipe means more bandwidth*, *stretch the
boundary to serve a million*, *snapping two bricks writes the integration*,
*water filling reservoirs pays out* — classify **self-referring**. They are not
vacuous: each really does predict something and each could come back false.
But every one could be made true again by the people who built it, editing their
own code. Nobody could have rescued Newton's particles that way.

**Self-referring is not an accusation of bad faith**, and every working
demonstration is one. It says only who holds the ability to make the prediction
come true. That is why a picture drawn over infrastructure a vendor operates
cannot do the job this stack needs a picture to do — and the Scale Slider is the
clearest case, because "stretch it and stop thinking about servers" is the cloud
metaphor with a new handle on it.

### Our own are in the same table

`sole-route`, `handles` and `what the bill should be` all classify **lens**, and
a test asserts it. If one had not, the standard would have been applied in one
direction only. One of the sole-route predictions — that the numbers add up to
parts minus pieces — is marked `presenterControls: true`, because it is a fact
about our arithmetic and not about the world. Marking it false would have been
the cheap way to inflate our own count.

### Same arithmetic as Press

A picture's predictions hang off the picture exactly as a claim's handles hang
off its origin — if the picture is wrong they all go together. So `press.js`'s
graph applies unchanged, and **1/m² reproduces exactly**: 1 → 1.000, 2 → 0.250,
3 → 0.111111.

### How to overturn any verdict on that page

Every prediction list is hand-written; the classing and arithmetic are not. State
a prediction that has been missed, add it, and the class changes. In particular:
if anyone can give a prediction of the pipe metaphor that its own builders could
**not** make true by editing their own code, M5 is wrong and the audit should be
withdrawn rather than defended.

Predictions locked before anything ran: `plexus/metaphor_preregistration.md`,
sha256 `c2588fcdbad5b7adf5ca022fc6b2b383d71549993abc08d8790cc79f906e0b33`.

**Registered null:** this measures pictures, not software. A tool built on a
self-referring picture can be excellent, and a tool built on a lens can be
useless. Nothing here says whether MetaphorOS would work, sell, or help anybody
— visual programming is forty years old and works.

---

## Qwen and DeepSeek — one test that could not run, and one that could

### The test that could not run

`hf_preregistration.md` (sha256 `ebe1366f…65adf87`) asked seven questions about
the text of real Qwen and DeepSeek model cards: how many quantitative sentences
press as checkable, how many marks each carries, how often the origin is
unnamed. **Not one of them has an answer.**

Two routes were tried, both closed here: the Hugging Face MCP tools returned
*requires approval* and no approval arrived, and the network policy answered
**403 to CONNECT for `huggingface.co:443`** — the proxy logged both refusals
itself. Every prediction in that file is about card text, so there is no partial
result and no substitute corpus.

**The pre-registration was not rewritten** into a question this environment can
answer. It stays locked and unedited; `HF_NULL.md` records the block and what it
would take to run it. Predictions edited after meeting the data are not
predictions.

### The test that could run

A separate, smaller question with its own pre-registration
(`cohort_preregistration.md`, sha256 `68682bef…5bf3d7aa`), about a file already
in this repository. `ei-dashboards/data/qwen_deepseek_frozen.json` holds 22 real
Qwen and DeepSeek projects, frozen 2026-08-06. Twenty-two projects reads as
twenty-two observations.

They are **two organisations**: deepseek-ai 12, QwenLM 10. Both are cut points.
Pressing each repository as a mark hanging off its publisher:

| | Each repository settles | A naive 1/22 implies |
|---|---|---|
| deepseek-ai (12) | **0.003499** | 0.045455 |
| QwenLM (10) | **0.004962** | 0.045455 |

An order of magnitude below what counting to twenty-two suggests. Sixth
appearance of this shape in this repository, and the first time it has been
pointed at a cohort we use ourselves rather than at somebody else's work.

**A pre-registered figure missed in its last digit.** C4 was written as
0.003498; the exact value is 262/143 arithmetic giving 0.0034987, so the
measured 0.003499 is right and the prediction was truncated where it should have
been rounded. Recorded in `test_cohort.py` rather than tidied away.

**What this does not say:** nothing about the quality of any repository or
either organisation, and nothing about the cohort's fitness for the use `plumb`
already makes of it — which is marked descriptive-only there for its own
separate reasons. Two labs publishing separately can still make genuinely
independent choices; the arithmetic reads the publishing structure and nothing
else.

**And the readout does not fit.** `press.js` was built for claims, so its
sentence here reads *"there are 22 things here you can go and do"* — true, and
beside the point. A test pins that, and the sentence is not used.

---

## Deploying it (Vercel)

`plexus/build.py` emits everything the deploy needs. From the repository root:

```bash
python3 plexus/make_icons.py     # only when the icon changes
python3 plexus/build.py          # index.html, manifest, sw.js, vercel.json
python3 -m pytest -q plexus/     # 32 tests, including the PWA files

cd plexus
npx vercel login                 # once
npx vercel link                  # once — creates .vercel/, answer "no" to a framework
npx vercel                       # preview deploy, prints a URL you can test
npx vercel --prod                # production
```

There is no build step to configure: it is a static directory. If Vercel asks
for a framework preset, choose **Other**; output directory `.`, build command
empty.

To check it before deploying, with the exact headers `vercel.json` declares:

```bash
python3 plexus/serve_with_headers.py plexus 8080
# then open http://localhost:8080 — localhost counts as a secure context,
# so the service worker registers there too
```

### Verified, not assumed

Driven in a real browser over a served origin with the deployed headers applied:

| Check | Result |
|---|---|
| secure context | `true` |
| service worker | `activated`, scope `/` |
| manifest parse errors | none |
| files cached on install | 7 of 7 |
| every declared icon fetches | `200` with the right content-type |
| network off, page reloaded | title `Plexus`, 4 examples, engine returns `2.000000` |

### The bug this caught

The first `vercel.json` had `default-src 'none'` with **no `connect-src`**. The
service worker `register()` call *succeeded*, the cache was *created*, and the
site would have shipped with **offline silently not working** — because
`caches.addAll()` during install is a same-origin fetch, the policy blocked it,
install rejected, and the registration was discarded. Every page-level check
still passed. Only cutting the network found it.

`connect-src 'self'` is therefore load-bearing, and a test now fails without it.

### Three things in the requested design that would not have worked

- **Data-URI icons in the manifest.** Chrome's install criteria want a fetchable
  icon of at least 192×192; a data URI is not reliably honoured.
- **SVG-only icons.** iOS does not read manifest icons for Add to Home Screen at
  all. It reads `<link rel="apple-touch-icon">`, and it does not accept SVG
  there — the installed icon on an iPhone would have been blank. Hence
  `icon-180.png`.
- **Long cache headers on the PWA assets.** An `immutable` `Cache-Control` on
  `sw.js` strands users on an old worker forever. The page, the worker and the
  manifest get `max-age=0, must-revalidate`; only the icons are immutable.

One more, found while rendering: `chrome --screenshot` captures before layout
settles on small viewports and writes a **blank** square with the correct
dimensions and a plausible file size. `make_icons.py` checks bytes as well as
dimensions for that reason.
