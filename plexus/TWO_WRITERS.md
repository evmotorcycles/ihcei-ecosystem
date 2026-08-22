# On a second strategist, and on write access

## Is a second one necessary?

**Not for capability.** Cowork and Claude Code run the same underlying model.
There is no reasoning this project needs that one can do and the other cannot.
The differences are packaging: where the files are, what the session can reach,
whether it survives a closed laptop.

Two corrections to the comparison as it is usually stated, because they change
the answer for *this* project specifically:

1. **"Claude Code runs locally with unrestricted folder access" does not apply
   here.** This work happens in Claude Code on the web — a sandboxed cloud
   container, cloned fresh, reclaimed on idle. The local-machine advantages are
   real for a laptop install and absent from how this repository is actually
   being built.
2. **Some of the listed commands are not ones I can confirm.** `/compact` is
   real. I would not build a workflow on `/re` or `/goal` without checking them
   against current documentation, and neither would I assert they do not exist.

## But it is valuable, and the reason is not capability

The most useful moments in this project have all been disagreements. The
Constitutional AI correction was one — a premise about training-time method
being mistaken for user-facing friction, which was carrying a whole design
decision. Measuring the five-to-ten mapping was another, and it corrected the
correction: the count was 2, or 5, or 6, depending on who assigned the links.

Neither surfaced from one voice agreeing with itself.

## The limit, measured by this project's own instrument

Two strategists that are both the same model are **not two origins**. They hang
off one, and on any question where the training is the source of the error they
will make it together. That is the shape recorded in the Shapes library as
`shared-origin`, and pressing it gives the same arithmetic as everywhere else:
two marks on one origin settle **0.250 each**, not 0.500. The second opinion is
worth having and it is worth a quarter, not a half.

Real independence comes from a different origin: a person who holds the actual
paper, a published document that can be opened, a measurement. Not a second
instance of the same weights.

## Write access: no, or a separate branch

**Read access is fine and useful.** The repository is on GitHub; there is nothing
to protect from a reader, and a second strategist reading the locked files is
exactly the check that has been valuable.

**Two writers on this branch is a specific, concrete hazard.** There are
currently **11 locked pre-registrations** and **10 test files asserting their
hashes**. The entire discipline of this project rests on those files never being
edited after they are hashed.

Two agents writing the same branch produces one of two outcomes, and both are
bad:

- a pre-registration is edited, the hash test fails, and somebody "fixes" the
  test to match the new hash — which silently converts a prediction into a
  retrodiction, the exact failure everything here is arranged against;
- a merge resolves in favour of whichever agent pushed last, and a locked file
  changes without either of them noticing.

Neither requires bad intent. Both are the ordinary result of two writers and no
coordination.

**So:** a second strategist reads, argues, and proposes. Changes land on one
branch, written by one writer, and the hash tests are what catch it if that ever
stops being true.
