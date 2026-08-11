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
