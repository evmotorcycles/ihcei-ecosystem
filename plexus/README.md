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
