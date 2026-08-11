# Weir — the gate an agent has to cross

**A weir is a low barrier built across a stream.** Water cannot go round it, and
because everything crosses in one place, a weir is also how you *measure* the
flow. That is the whole design: nothing passes unmeasured, and some things do
not pass at all.

```
node weir/weir.mjs --key weir/key.example.json --upstream http://localhost:3000 --port 8080
```

---

## The problem it solves, and why the other tools could not

Everything else in this project **returns an opinion about an action**. Cairn
says a claim is thin. The valet key screen says a path would be refused. The
dashcam records that something happened.

None of them can stop anything. A structural test of the whole stack found
exactly that: no component can block, and no hook exists that a program cannot
bypass. The honest label was **a library, not an operating system** — and the
danger of an advisory layer is that a person believes they are protected when
they are not.

**Weir refuses.** A denied request is answered `403` at the gate and is *never
forwarded*. The upstream server does not see it, because the bytes are never
sent. That is the difference between a warning and a wall.

| | The tools | Weir |
|---|---|---|
| On a bad request | reports it | **refuses it** |
| Upstream sees the request | yes | **no** |
| Can be ignored | yes, silently | only by not routing through it |
| What it produces | a verdict | a verdict **and a refusal** |

---

## What it actually does, in order

1. **Decides.** Default deny; a refusal beats a permission written above it; the
   most specific permission wins; read permission never implies write. Same
   three rules the valet key screen displays — enforced here instead of shown.
2. **Refuses, or forwards.** A refusal ends at the gate. Nothing downstream is
   contacted, so nothing downstream can leak.
3. **Screens what crosses.** Content coming back is checked, and the result rides
   on the response headers: `x-weir-check`, `x-weir-evidence`, and
   `x-weir-careful` when it touches health, money, law, chemicals or safety.
4. **Seals it.** Every crossing — refusals included — is written to a chain where
   editing an old entry breaks every seal after it.

### Budgets

A rule may carry a `budget`: *five changes to drafts, then ask me again*. The
sixth write is refused. This is the part people actually want from a valet key
and almost never get from a permissions dialog.

---

## The guard — where Cairn stops being a library

Everywhere else in this project, Cairn **returns a verdict** and something
downstream may or may not act on it — which is to say, nothing has to. A rule
carrying `require` makes the verdict the *predicate of a refusal*:

```json
{ "path": "briefings/**", "plain": "read briefings, but only ones that carry their evidence",
  "allow": true, "write": false, "require": "SUPPORTED" }
```

A briefing that names its study, its figure and its date is delivered. A bare
assertion is fetched, assayed, found to be `INSUFFICIENT_EVIDENCE`, and **not
handed over** — `403`, `x-weir: withheld`, and the response carries the question
that would fix it instead of the content that failed.

> ⚠️ **This is a weaker guarantee than a refusal, and the two must not be blurred.**
> A refused *request* never reaches upstream. Withheld *content* was already
> fetched — upstream saw the request. What is guaranteed is only that the bytes
> did not reach the client. The response says `fetched_but_not_delivered: true`
> so a reader cannot mistake one for the other, and a test asserts it.

### Three states, because two would lie

The independence check elsewhere in this project refuses to collapse *checked
and failed* into *could not check*. A gate must not either, or an unreadable
payload silently becomes a pass.

| `x-weir-guard` | meaning | what happens |
|---|---|---|
| `MET` | reached the required bar | delivered |
| `NOT_MET` | checked, fell short | withheld |
| `UNCHECKABLE` | nothing could be assayed | **the key decides** |

`UNCHECKABLE` defaults to withholding, because a gate fails closed. A key may
say `"on_uncheckable": "pass"` — and the response still carries
`x-weir-guard: UNCHECKABLE`. The distinction is never lost, only acted on
differently.

---

## The stop card — what a refusal looks like to a person

```
python3 weir/build_stop.py && open weir/stop.html
```

Abstaining is one of two normal outcomes, so on a phone it has to *look* like
one. The trap is in the name: design to an **empty tray** and you will build
absence — dead space, a centred line, a spinner that stopped — which is exactly
what a crash looks like, so a person reads the more familiar of the two.

The card is therefore not empty. It is a **returned parcel with a slip on it**:
you get your thing back, plus a note saying what was missing. What separates a
stop from a crash is not the absence of an answer but the **presence of the
work** that led to not giving one — words read, checks run, checks met, the
time, and a fingerprint. A crashed app cannot produce a number or a hash.

`weir/test_stop.py` turns that from a design opinion into an assertion. It
drives the page in headless Chromium and fails if:

- a stop and an answer have different silhouettes (both must be
  `strip · head · counts · reasons · next · acts · foot`)
- the stop card contains any crash vocabulary — *error*, *failed*, *oops*,
  *try again*, *something went wrong*
- the strip is painted a reddish colour, or the page even defines an error-red token
- the card lacks its counts, its time or its fingerprint
- any next step points at the app (*retry*, *reload*) instead of at the claim
- the input was cleared
- the page overflows sideways at 390 px

---

## The honest boundary

> **Weir is real interposition for traffic that routes through it. It is not
> mandatory in the operating-system sense.**

Nothing here stops a program from opening its own socket and ignoring the proxy.
Making it unbypassable requires the layer below: a network namespace with no
other route out, a container, a firewall rule, or OS-level enforcement. Those are
real and standard, and **they are not in this repository.**

So the accurate claim is narrow and worth stating precisely:

- ✅ For an agent configured to use this proxy, refusals are enforced, not advised.
- ✅ Refused requests provably never reach upstream — the test asserts the
  upstream log is empty.
- ❌ An agent that chooses not to use the proxy is entirely unaffected.
- ❌ This is not a sandbox, and it cannot contain a hostile program.

If you deploy it, put it where the agent has no other route — otherwise you have
rebuilt an advisory layer with extra steps.

---

## Known rough edges, disclosed rather than discovered

**Screening is noisy on machine-readable payloads.** The content check was built
for prose. Passing a JSON dataset through it trips patterns on incidental words —
the frozen GitHub cohort raises a legal flag because the records contain the word
"license". The flag is real; the inference a reader might draw from it is not.
Treat `x-weir-careful` as meaningful on documents and noise on data.

**Only the first 4 KB of a response is screened.** A warning at the top of a long
document does not mean the rest was examined.

**Paths are matched as strings.** Normalisation, symlinks and encoding tricks are
not handled. Against an adversary who controls the path, this is not enough.

---

## Tested against real data

The fixture serves the actual frozen cohorts used elsewhere in this project —
22 real GitHub repositories and 24 real Hugging Face models — plus files that
must never be readable.

```
node --test weir/weir.test.mjs
```

The suite asserts, among other things:

- four different refused paths, and an **empty upstream log**
- a refusal body that does not contain the protected content
- the real cohorts arriving intact through an allowed path
- a `PUT` to a read-only rule refused, and not forwarded
- a five-change budget producing `[200,200,200,200,200,403,403]`
- an outbreak report carrying its health warning through the gate
- editing a past crossing breaking the seal chain
- a bare assertion withheld by the guard, with the failing text absent from the
  refusal body — and the response admitting upstream did see the request
- an unreadable payload reported as `UNCHECKABLE`, never as a failed check
