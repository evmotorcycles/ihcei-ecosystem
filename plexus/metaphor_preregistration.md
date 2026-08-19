# Pre-registration — auditing a metaphor, including our own

Written and hashed **before** `metaphor.js`, `metaphorlib.js` or `test_metaphor.py`
were run once.

---

## What is being asked

MetaphorOS proposes that manipulating a visual metaphor *directly engineers the
underlying software*: a wider pipe is more bandwidth, stretching a boundary
allocates server clusters, snapping two shapes together writes an integration
layer.

The question is not whether that ships. Visual programming is forty years old
and works — Scratch, LabVIEW, Node-RED, Max/MSP, node graphs in every 3-D tool.
The question is the one this stack already enforces on itself: **after the
picture, is there somewhere to go?**

The closing example in the brief is the right test and it is Newton's. He
imagined light as tiny billiard balls, and that picture predicted reflection
angles, refraction, and *no bending around a sharp edge*. Two of those came back
**false** — light slows in water, and it does bend round edges. The corpuscle
metaphor was killed by its own predictions. **That is what makes it a lens.**

So the audit measures one thing: what does this picture predict that could come
back false, and **who is able to make that prediction come true?**

---

## Three classes, and the middle one is the finding

| Class | Test | Example |
|---|---|---|
| **notation** | predicts nothing at all | "cloud", "folder", "For you" |
| **self-referring** | predicts only things the presenter controls | "widen the pipe and bandwidth rises" |
| **lens** | predicts at least one thing the presenter does **not** control | corpuscles, the falling lift |

Notation is not a criticism. A legend on a map cannot be wrong and is still
worth having. **Self-referring is not an accusation of bad faith either** —
every demo is self-referring. It is a statement about *who can make the
prediction true*. If widening the pipe does not raise throughput, the people who
built the pipe can fix that by changing their own code. Nobody could fix
Newton's corpuscles by changing anything except the theory.

That is the whole difference, and it is why a metaphor over infrastructure a
vendor operates cannot do the work this stack needs a metaphor to do.

---

## The arithmetic

A metaphor's predictions hang off the metaphor itself, exactly as a claim's
handles hang off its origin in `press.js` — if the metaphor is wrong, all of its
predictions go together. So the same graph and the same engine apply, and the
same law should fall out: with `m` predictions on one origin, each settles
`1/m²`.

The list of predictions for each metaphor is **written by a person**. The
classification and the arithmetic over that list are not. Anyone who thinks a
prediction has been missed can add it, and the class will change — the audit
says exactly how to overturn itself.

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| M1 | m predictions on one origin: each settles 1/m²; every bearing 1.000; total m + 1 | exact |
| M1a | m = 1 | 1.000000 |
| M1b | m = 2 | 0.250000 |
| M1c | m = 3 | 0.111111 |
| M2 | A metaphor with no predictions returns **no number** and classifies `notation` | refused |
| M3 | A metaphor whose every prediction is presenter-controlled classifies `self-referring` — it still gets a number, because it really is refutable | self-referring |
| M4 | A metaphor with at least one prediction the presenter does not control classifies `lens` | lens |
| M5 | The four MetaphorOS metaphors audited (wider pipe, scale slider, snapping shapes, water-grid budgeting) all classify **self-referring** | 4 of 4 |
| M6 | "Cloud storage", "desktop and folders" and "For you" all classify **notation** | 3 of 3 |
| M7 | Newton's corpuscles classify `lens`, carry three predictions at 0.111111 each, and carry `killed: true` — a metaphor destroyed by its own prediction | lens, killed |
| M8 | **Every metaphor this stack ships classifies `lens`.** If one does not, that is special pleading and it must be given a real prediction or stop being called a lens | all |
| M9 | Class counts across the twelve audited | 5 lens, 4 self-referring, 3 notation |
| M10 | A declaration with no `predicts` field at all is refused with a reason, not an exception | refused |

M8 is the one that could embarrass us, and it is the reason our own metaphors
are in the same table as MetaphorOS's rather than in a section praising them.
M5 is the one that could be wrong: if anyone can state a prediction of the pipe
metaphor that its own builders could not make true by editing their own code,
the classification flips and this audit was mistaken.

---

## Nulls, registered in advance

**NULL-M1.** Nothing here shows MetaphorOS would not work, would not sell, or
would not help anybody. It very well might. The audit is about one claim —
that the metaphor *reveals* rather than covers — and that claim is separable
from whether the product is good.

**NULL-M2.** The prediction lists are hand-written. They are a Layer-3 reading
of each metaphor, and the arithmetic over them is Layer 1. Somebody who knows
optics better could improve Newton's list; somebody who has actually built a
visual programming environment could improve MetaphorOS's. The numbers would
move and the file says so.

**NULL-M3.** "Self-referring" says nothing about honesty or quality. Every
working demo is self-referring. It is a statement about who holds the ability to
make the prediction come true, and no more.

**NULL-M4.** This measures metaphors, not software. A tool built on a
self-referring metaphor can be excellent, and a tool built on a lens can be
useless.

---

## What would falsify this

1. **A genuine uncontrolled prediction for the pipe metaphor.** Then M5 is wrong
   and MetaphorOS's metaphors are lenses, and this audit should be withdrawn
   rather than defended.
2. **One of ours classifies self-referring.** Then the standard was being applied
   in one direction only, which is the failure this whole stack is arranged
   against, and it must be fixed in the same commit that finds it.
3. **The 1/m² law does not reproduce here.** Then metaphors and claims are not
   the same shape after all, and the reuse of `press.js`'s graph was wrong.
