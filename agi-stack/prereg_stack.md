# Pre-registration — can the Laplacian be gamed, and what does LISM do in the stack?

Written and hashed **before the run**. 2026-09-14.

---

## The claim under test

A proposed three-layer architecture (LLM symbolic · JEPA perceptual · LMD
epistemological) states:

> "The Novora architecture is un-gameable because it relies on mathematics, not
> preferences. **You cannot trick the Laplacian Matrix.** No matter how
> eloquently the LLM phrases an argument, if the logical path relies on a single
> unverified assumption, the Effective Resistance will spike, and the Cut Vertex
> will be exposed."

In the same architecture, **the LLM proposes the edges**. The audited layer is
the layer that supplies the input. That is the thing to test.

The engine's own standing null already says what I expect: *absence of an edge
is absence of a declaration*. If that is true, then presence of an edge is
presence of a declaration too, and a declaration is exactly what an adversary
controls.

## Arm 1 — gaming the topology

Start from a real audited graph: three cited passages routing through one
declared method to one conclusion (`order-invariance/`, locked 9c9872e4). It has
**one cut vertex** and each passage settles **1/9**.

The adversary adds edges only. It invents no new evidence, changes no wording,
and removes nothing. It simply **declares more links** between things already in
the graph.

| # | Prediction | Value |
|---|---|---|
| G1 | Adding edges alone removes **every** cut vertex | 0 cut vertices |
| G2 | It takes **at most 3** added edges to do it | ≤ 3 |
| G3 | After padding, the deepest dependence **falls** — the argument reads *more* robust while resting on exactly the same evidence | falls |
| G4 | Total bearing **rises** with padding, so a "more connected" reading looks stronger | rises |
| G5 | Requiring every edge to carry a `where` makes the padding **refusable**, because the invented edges have no source to name | all padding refused |

**G1–G4 are the attack. G5 is the only defence I expect to work, and it is not a
mathematical defence** — it moves the trust from the matrix to whoever writes
the `where`. If G5 holds, the honest statement is that the Laplacian cannot be
tricked *about a graph*, and can be trivially tricked *about an argument*,
because the graph is a claim.

## Arm 2 — LISM through the proposed stack

The architecture is a chain: LLM → JEPA → edge proposer → LMD → synthesis. LISM
measures what survives a chain of hops, `E = U · ∏ Dᵢ`.

| # | Prediction | Value |
|---|---|---|
| L1 | With four hops at Dᵢ = 0.9, **E < 0.66** | < 0.66 |
| L2 | Across depths 1–12 at fixed Dᵢ, `E` is **monotone decreasing** and never rises | monotone |
| L3 | To keep E ≥ 0.5 at 4 hops, each hop needs **Dᵢ ≥ 0.84** | ≥ 0.84 |
| L4 | The retired hard floor `D ≥ D_min` is **still marked RETIRED_FULLY** and does not reappear as a gate in anything written here | retired |

**L1–L3 are arithmetic and are listed as verification, not discovery.** The
point of computing them is that they set a floor on what any such stack can
promise: a four-layer pipeline whose layers are each 90% faithful delivers
roughly two thirds of its input fidelity, and no amount of architecture diagram
changes that.

**L4 is the one that matters.** `FLOOR_RETIREMENT.md` retired a hard fidelity
gate at a fully-powered null, p = 0.735. An architecture that re-introduces a
stop-below-a-number rule as an *empirical* claim resurrects it. As a **declared
preference** it is a different object and is allowed — the distinction this
repository has now had to make four times.

---

## Nulls, registered in advance

**NULL-G1.** The attack requires the adversary to control edge proposals. In an
architecture where a human draws the graph, or where edges come from a source
outside the audited layer, it does not apply. The finding is about the proposed
architecture, not about LMD.

**NULL-G2.** "Reads more robust" is a statement about the numbers, not about the
argument. Padding does not make an argument better and nothing here says it does.

**NULL-G3.** G5 is not a proof that provenance-checking works. It shows that a
field can be made mandatory. Whether the `where` a person writes is true is
exactly what no test in this repository can check.

**NULL-L1.** `Dᵢ` values here are chosen, not measured. Nothing in this run
estimates the real fidelity of an LLM hop, a JEPA hop, or a human hop. The
arithmetic is exact; its inputs are illustrative.

**NULL-L2.** n = 1 graph for the attack. A different topology may resist padding
differently, and no claim is made about graphs in general.

---

## What would falsify this

1. **G1 fails** — padding cannot remove the cut vertices, and the topology has a
   resistance to declaration-level attack that I did not expect.
2. **G5 fails** — provenance-requirement does not stop the padding, and there is
   no cheap defence at all.
3. **L2 fails** — the hop product is not monotone, which would mean the LISM
   form is wrong.
