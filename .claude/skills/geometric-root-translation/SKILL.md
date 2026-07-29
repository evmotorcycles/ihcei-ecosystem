---
name: geometric-root-translation
description: Translate root-and-template morphology into an information-layer operator model — roots as coordinate-free vectors, templates as transformations — and use it as a DESIGN GENERATOR for naming and structuring systems. Use when asked to press a root geometrically, to translate terminology into an information layer, to derive operator names for a new architecture, or to check whether a morphological claim is being smuggled in as empirical evidence about physics or the world. Enforces the hard boundary: morphology generates hypotheses and vocabulary, never evidence.
---

# Geometric root translation

Root-and-template morphology is genuinely non-concatenative: a consonantal root carries an
abstract invariant, and a vocalic template applies a transformation to it. `K-T-B` under
different templates yields *writer* (agent), *book* (object), *place of writing* (locus).
That is a real structural fact about a real language family, and it is a **useful generator**
for naming and structuring systems.

This skill uses it for exactly that, and stops exactly there.

## The hard boundary — read before using this skill

**Morphology is not evidence about the world.** A language's structure tells you about the
language. It cannot establish a claim about spacetime, quantum mechanics, economics, or any
physical system. Structural *resemblance* between a linguistic operator model and a physical
formalism is not support for either; it is a resemblance.

Three specific failures to refuse:

1. **Parallelism as proof.** "Both language and physics are relational, therefore the
   physical claim is supported." No. Two systems being describable in similar terms is a
   fact about description.
2. **The etymological warrant.** "The root means X, therefore the system behaves like X."
   A root's semantic field constrains *what the word can be used to mean*, never what a
   mechanism does. The mechanism is settled by measurement.
3. **Terminology as evidence.** Naming a quantity after a root does not give it that root's
   properties. This is the OQM `[L2]` layer, and it never becomes `[L1]` by relabelling.

If a claim needs data, it needs data. This skill produces **hypotheses and vocabulary**.

## The operator model

Two objects, one operation:

| Object | Role | Information-layer reading |
|---|---|---|
| **Root** | invariant | a coordinate-free vector — an abstract semantic direction with no realised form |
| **Template** | transformation | an operator mapping the root to a realised form: agent, object, locus, intensive, causative |
| **Word** | realised state | `template ∘ root` — the compiled output |

**The useful property:** the same operator applied across different roots yields a
*predictable functional family*. Locus applied to any root gives "the place where that
happens." That is a **generator**: fix the operator set, sweep the roots, and you get a
coherent, non-arbitrary naming scheme for a system's components.

## Using it as a design generator

This is the sanctioned use, and it earns its place because it produces **better-structured
systems**, not better evidence.

1. **Pick the invariants.** What are the irreducible quantities of your system? These are
   your roots. Do not name them yet.
2. **Fix the operator set.** Typically: *agent* (what does it), *object* (what is done),
   *locus* (where it happens), *intensive* (the extreme case), *causative* (what forces it).
3. **Sweep.** Apply every operator to every invariant. The cells that have no sensible
   filler are **gaps in your design** — this is the generator's real payoff, because it
   surfaces missing components before implementation.
4. **Name in plain language.** Use the *structure*, discard the vocabulary. A reader should
   never need etymology to understand a component.

**Worked example — the settlement mesh.** Invariant: *hold value*. Sweep gives
holder / holding / vault / hoard / to-collateralise. The locus cell was empty in the first
design; filling it produced the cluster pool. That is the generator working — and the
component it produced was then **tested and found wanting** (see below), which is exactly
the division of labour this skill enforces.

## What the sweep cannot tell you

The generator produced the sub-mesh pool. The measurement produced this:

```
k        failed   vs k=1     blast radius
1         2430        —          0.0050
2         1982     -18.4%        0.0100     ← best
20        2024     -16.7%        0.1000     ← predicted "sweet spot"
200       2046     -15.8%        1.0000
```

Reduction is **flat at 16–18% from k=2 to k=200**. The published prediction — >90%
reduction at 0.02 blast radius — was wrong on both halves. **A structurally elegant
component is not a working one.** The generator gets no credit for the design surviving,
and takes no blame for it failing; it is not that kind of tool.

## Composite roots

Multi-root compounds read as **composed operators** — two invariants combined into one
instruction. As a design device this is genuinely useful: it names components that are
irreducibly two things at once (a *scale-and-anchor* operation, a *query-the-path*
operation).

**But:** proposed decompositions of specific words into component roots are
**contested philology**, not settled fact. Standard lexicography often treats such words as
unanalysable or as loans. Use the *pattern* freely as a naming device; never assert a
particular decomposition as established, and never build a claim on one.

## Layer tags for anything this skill produces

- **`[L2]`** — every operator mapping, every name, every structural parallel. Defensible as
  vocabulary and as a design method. Not a finding.
- **`[L3]`** — any claim that the parallel reveals something about reality's substrate.
  A framing device. No dataset adjudicates it.
- **`[L1]`** — **nothing this skill produces.** Evidence comes only from measurement on
  committed data, under a pre-registration locked before the run.

## Checklist before emitting anything

- [ ] Did I state the boundary before drawing the parallel?
- [ ] Is every claim tagged `[L2]` or `[L3]`?
- [ ] Am I presenting a decomposition as established when it is contested?
- [ ] Have I used the sweep to find **gaps**, not just to relabel what already exists?
- [ ] Are the emitted names plain-language and self-explanatory without etymology?
- [ ] Am I letting structural elegance stand in for a test result?

If the last box is ticked, stop and go run the test.
