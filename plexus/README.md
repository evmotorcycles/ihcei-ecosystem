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
