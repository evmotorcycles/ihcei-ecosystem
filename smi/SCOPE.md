# Scope amendment — LMD is computational telemetry

**Amends the framing of `PREREG.md`. Changes no prediction, no gate, and no
number.** The pre-registration stays hash-locked and unedited; this file records
what changed in the *language*, and why, so the two can be read together.

## What changed

The original write-up repeatedly said things like *"this is not evidence that
space is emergent"* and *"no result here is evidence about the nature of
space."* That was answering a question nobody asked. By denying a physical claim
four times over, it implied one had been made.

**None was.** LMD here is **computational telemetry on an information layer**:
measurement of a dependency graph inside a running system. It is a construction
for building interfaces — SMI is the first — and the name is a name.

| | |
|---|---|
| **What is measured** | a dependency graph between live elements in software |
| **What `J` is** | how strongly one element's value determines another's |
| **What `d` is** | how far apart two elements should sit, given those dependencies |
| **What it is not** | a statement about matter, spacetime, or physical distance |

## What did not change

Every prediction, every gate, and every result in `PREREG.md` stands exactly as
locked. `prereg.lock.json` still verifies. In particular:

**H0 is still an identity.** `pinv(J·L₀) = J⁻¹·pinv(L₀)` is a fact about the
pseudo-inverse, and moving the subject matter from physics to software does not
touch it. The log–log slope is −0.500000 with R² 1.000000 on a ring, a path, a
star and a random graph, and it would be on any graph anyone ever passes it. A
measurement that cannot come out otherwise is not a verification of anything, in
any domain.

## The part that improves under the correct scope

Framed as physics, the identity was an embarrassment to be disclaimed. Framed as
telemetry for an interface, **it is a property worth having on purpose**:

> Scaling every coupling by the same factor rescales every distance and changes
> nothing else. So a global tension control is a **zoom**, not a semantic
> control. It cannot reorder elements, cannot change what is near what, and
> cannot alter a single value. It is safe to expose to a user.

That is the useful reading, and it is why the sweep is kept and labelled
`INVARIANT (BY CONSTRUCTION)` rather than deleted. It earns its place twice: as
a design guarantee, and as a smoke test that fails the moment `pinv`, the
Laplacian, or the clipping breaks.

What carries actual information in this engine is **topology** and **local**
coupling — which is exactly what H4 measures, and H4 can fail.

## The claim, stated once, in the form it should be made

> A layout derived from a dependency graph cannot drift out of step with the
> dependencies. Change what depends on what, and the picture changes, because
> the picture *is* the dependency structure rather than a drawing of it.

That is a software property. It is testable, it is the reason to build this, and
it needs no physics behind it.
