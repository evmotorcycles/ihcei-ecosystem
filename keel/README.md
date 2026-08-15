# Keel — a governance kernel

**A keel is the part of a boat you never see.** It does not power the boat, steer
it, or choose where it goes. It removes *one* degree of freedom: the sideways
one. Without a keel you go where the wind pushes you. With one you go where you
are pointed. *On an even keel* is already ordinary speech for this.

That is the whole relationship to Windows, macOS, Android, HarmonyOS and Linux.
They are the hull, the engine and the cargo hold, and they are good at it. Keel
is added underneath. **It competes with none of them, because it answers a
different question.**

```
A traditional kernel asks:   MAY this program do this?
Keel asks:                   are there GROUNDS to do this?
```

Those are orthogonal, which is why holding both matters. A hallucinated
instruction with valid permissions executes perfectly on every operating system
in the world. **The permission was never the thing that was wrong.**

| | Traditional kernel | Keel |
|---|---|---|
| Manages | processor, memory, devices, files | actions and the grounds for them |
| Asks | may this program do this? | is there enough behind this to act on? |
| Default | **do it** unless something objects | **do not** unless there are grounds |
| On a fabrication with valid permissions | executes it perfectly | holds it, and says what is missing |
| On missing data | an error, or a guess | abstaining is a normal result |
| Produces | bytes, frames, syscall returns | a decision, a reason, and a sealed record |
| Blind to | whether the content is grounded | whether anything is *true* |

---

## Install

```
bash keel/install.sh          # puts `keel` in ~/.local/bin
keel key                      # what an assistant is allowed to do
keel check "a claim"          # what it is made of, and what would settle it
keel run actions.json         # put a list of actions through the kernel
```

**A single file that needs nothing but node:** `keel/dist/keel.cjs` (34 KB), with
`keel.cmd` for Windows and `keel` for macOS/Linux.

**A real standalone binary** — no node installed at all:

```
python3 keel/build_exe.py --binary
```

That was built and run here: a 124 MB Linux binary answering `env -i ./keel check`
with an empty environment. The same two commands on Windows produce `keel.exe`.

> Two things are **not** done for you and cannot be. The injection step needs one
> npm package (`postject`), and shipping a `.exe` to other people needs a
> code-signing certificate — without one, Windows SmartScreen warns every person
> who downloads it. The binary is ~124 MB because it contains a whole copy of
> node, so it is deliberately **not committed** to this repository. What the
> build script will never do is produce a file called `keel.exe` that is really
> a shell script.

There is also a browser console — no install at all:
**[`keel/console.html`](console.html)**, three engines on one page, offline.

---

## The one entry point

Every action goes through `admit()`. There is no second path, no fast path and no
privileged caller. Six stages run in a fixed order, and **every stage can only
refuse — not one of them can grant.** Passing means nothing stopped you.

```
   1  NAME     an action must say what it is        nothing anonymous moves
   2  KEY      default deny                          you list what IS allowed
   3  BUDGET   a permission may be finite            five changes, then ask
   4  ASSAY    measure the evidence behind it        three states, never two
   5  BAR      policy may demand a standard          below it, withhold
   6  SEAL     write it to a chain that cannot be quietly edited
```

```js
keel.admit({ verb: "write", target: "posts/finding.md",
             content: "The new process is much better and everyone should switch." })

// { admitted: false, outcome: "HELD", stage: "BAR", tier: "BATCH",
//   why: "this rule acts only on SUPPORTED material; what arrived was
//         INSUFFICIENT_EVIDENCE (0 of 5 kinds of support)",
//   next: "Add a source, a figure, a date, a method or a scope…",
//   seal: "6f3a…" }
```

Every traditional operating system would have written that file.

### Three states, never two

`UNCHECKABLE` is not `NOT_MET`. Collapsing *could not check* into *checked and
failed* turns an unreadable payload into a silent pass; collapsing it the other
way turns an honest gap into a fabricated verdict. A policy chooses what happens
on `UNCHECKABLE`, and the stamp says `UNCHECKABLE` either way.

### Three tiers, so it does not nag

A slip for every action is not protection: somebody who has dismissed forty
slips dismisses the forty-first without reading it. That is how **Allow** became
a reflex on every other system.

| tier | when | what the person sees |
|---|---|---|
| `LEDGER` | admitted | nothing — sealed, always inspectable |
| `BATCH` | held for want of evidence | one line at the end: *"47 done · 3 held for missing a source"* |
| `STOP` | a boundary crossed, or high-stakes content | immediately, on its own |

Thirty ordinary reads produce **zero interruptions** and thirty sealed entries.
Reaching for `.ssh` produces exactly one. A held *health* claim is promoted out
of the batch — being well-formed is not the same as being safe.

---

## Checked from outside itself

`keel/audit.py` is Python on purpose. An auditor written in the kernel's own
language, importing the kernel's own code, agrees with the kernel about any
mistake they both make. It reads only the ledger and re-derives every seal.

| obligation | the tamper that makes it fail |
|---|---|
| every decision recorded | an unnamed outcome |
| chain intact | editing entry 3; deleting entry 5 |
| admissions name their rule | blanking one rule |
| refusals give a reason | blanking one reason |
| escalation follows the rule | downgrading a `STOP` to `LEDGER` |
| counts carry their handles | emptying one `missing` list |

Six checks that hold on a clean run and **fail on a tampered one**. A check that
cannot fail is decoration.

### A pre-registered null

`keel/run.plumb` asks, in Plumb, whether a run was *governed* or merely *logged*
— `E = U × D_in × D_out`. **It halts on every keel ledger, and that halt is the
result.** `sealed/attempted` is exactly 1.000 on every run, because a ledger
records everything that reaches it: *a record cannot contain its own omissions.*
The substitute leg correlates at r = 1.000. Plumb refuses to report one
measurement twice and call it corroboration.

Full write-up, including the four tempting workarounds that were rejected:
**[`NULL.md`](NULL.md)**.

---

## What this is not

**It is not a kernel in the operating-system sense**, and calling it one without
this paragraph would be a lie. It does not schedule, allocate memory, drive
hardware or isolate processes — and **nothing forces a program to come through
it.**

That is not a guess. The structural check now *demonstrates* it: it stands the
gate up, watches a forbidden request get refused with the upstream log empty,
and then opens its own socket straight to the far side and reads the protected
bytes. One line of ordinary code.

```
O1 interposition      PASSES   (behaviourally — a refused request never arrives)
O2 mandatory routing  FAILS    (behaviourally — a program went round it and won)
```

Making it unavoidable is a job for the layer underneath: a container, a network
namespace with no other exit, a platform that will only call out through this.
**That is real, standard, and not in this repository.** A gate you can walk
around is a gate you should not rely on alone — and the honest label stays
*a gate that works only where it is the only route.*

**And none of it knows whether anything is true.** It checks whether a claim can
be checked. A well-written falsehood carrying all five kinds of support is
admitted, on purpose — and hands over the exact words that settle it in five
seconds.
