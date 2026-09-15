# Pre-registration — the NERE pipeline, before it is wired

Written and hashed **before the module runs**. 2026-09-15.

---

## What is being built

A composite path from a hand-drawn, provenance-tagged argument graph to the
three structural readouts this repository already computes. Four stages:

1. `DependencyTracingExtractor` — **not a language model.** It builds and
   validates a graph someone else drew. It cannot read a document, cannot find
   an edge, and refuses any edge that does not name its provenance.
2. `JEPASemanticFilter` — a **seam that abstains**. No benchmarked latent-energy
   model exists in this repository, so the filter returns ABSTAIN on every call
   and no number leaves it.
3. `LMDTelemetryEngine` — the existing engines (`spar`, `fathom`, `smi`),
   wrapped, not reimplemented.
4. `EpistemicFirewall` — layering rules over provenance and structure.

## The two drawings of one document

The uploaded study (N182) already has a locked reading in
`order-invariance/prereg_order.md` (sha `9c9872e4…`): three cited passages route
through **one** declared method to a conclusion. Five parts.

A second drawing separates the metaphor from the method, giving six parts:
three passages → the metaphor → the method → the conclusion.

`where`: both drawings are hand-made from the uploaded PDF. The first is the
locked one; the second is recorded here as an **alternative reading**, not as a
correction of it. `NULL-N2` of the locked file already says a different modelling
decision gives a different number, and this is that case, measured.

---

## Predictions

### Arm 1 — the two drawings

| # | Prediction | Value |
|---|---|---|
| E1 | The locked 5-part drawing gives Foster total **4.0** and **one** cut vertex, the method | 4.0, 1 cut |
| E2 | The 6-part drawing gives Foster total **5.0** and **two** cut vertices, the metaphor and the method | 5.0, 2 cuts |
| E3 | Effective resistance from a passage to the conclusion in the 6-part drawing is **3.0** | 3.0 |

**E1–E3 are verification, not discovery.** Foster's theorem fixes the total at
parts − pieces, and the cut vertices of a chain are its interior nodes. They are
here so that the wrapper is shown to be reading the same engines, and because a
pipeline that could not reproduce them would be wired wrong.

### Arm 2 — the seam that abstains

| # | Prediction | Value |
|---|---|---|
| E4 | The semantic filter abstains on **every** call, including on a graph where every edge is literal | always ABSTAIN |
| E5 | **No number leaves the seam**: the verdict's energy field is `None` in every case | `energy is None` |
| E6 | A pipeline run carries the abstention line into its report, rather than dropping it | line present |

### Arm 3 — the firewall

| # | Prediction | Value |
|---|---|---|
| E7 | An edge with no provenance tag is **refused**, not defaulted to a tag | raises |
| E8 | Both N182 drawings classify as **Layer 3**, because each carries at least one interpretive edge | Layer 3, both |
| E9 | A graph whose every edge is `literal` classifies as **Layer 1** | Layer 1 |
| E10 | No field anywhere in the report combines a structural quantity with a provenance quantity | no fused field |

**On E8/E9 — the rule and its reason.** A Layer-1 claim is one the document
states. One inferred edge on the path means the reader supplied part of the
chain, so the claim is not lexical. That is categorical, not a tuned number:
the sensor is the provenance tag the drawer must write, and there is no
threshold to choose.

**No Provenance Fragility Index is registered.** A 30%-of-edges downgrade was
proposed. It has no stated reason and no sensor beyond the ratio itself, and
`FLOOR_RETIREMENT.md` records a gate retired at p = 0.735 for exactly that.
The ratio is **reported**; it gates nothing.

### Arm 4 — the padding attack, and the one declared fusion

Take the 6-part drawing and add edges only — no new parts, no new evidence.

| # | Prediction | Value |
|---|---|---|
| E11 | Adding edges alone clears **every** cut vertex | 0 cuts |
| E12 | It takes **at most 4** added edges | ≤ 4 |
| E13 | The measured Foster total is **unchanged at 5.0** — immune, by parts − pieces | 5.0 |
| E14 | The deepest dependence **rises** under padding, moving against the attacker | rises |

**E14 is the one I could be wrong about.** In `agi-stack/` the same attack raised
dependence from 0.111 to 0.619 on a different graph. Whether it rises here is
not settled by that.

**The declared fusion.** One rule in this module combines two readouts, by
explicit decision rather than by default: the padding tripwire fires when the
cut count **falls** and the deepest dependence **rises** in the same comparison.

*Reason:* neither half is evidence on its own. Cuts fall whenever anyone adds a
link, including honestly. Dependence rises for many reasons. The conjunction is
narrow because clearing a bottleneck while making the argument rest **harder** on
one thing is the signature of declaring links rather than finding them.

*It is recorded as a fusion, not hidden as a score.* It emits a named boolean
with both source readouts beside it, and both remain separately readable. It
produces no number and does not change any layer.

---

## Nulls, registered in advance

**NULL-E1 — the drawing is the claim.** Every number here is a reading of a graph
a person drew. The two N182 drawings differ only in whether the metaphor is its
own node, and they give different telemetry. Nothing in this module can say which
drawing is right.

**NULL-E2.** The extractor extracts nothing. It is a validator with a name
inherited from the specification it implements, and that name overstates it.
No language model runs in this module and no text is parsed.

**NULL-E3.** The provenance tag is written by whoever draws the graph. Whether
an edge marked `literal` really is stated in the document is exactly what no
test here can check.

**NULL-E4.** The abstaining seam is not evidence that a semantic layer would
help. It is a hole with a defined shape.

**NULL-E5.** Layer 1 / Layer 3 are labels about where a claim came from, not
about whether it is true. A Layer-1 claim can be false and a Layer-3 claim can
be correct.

**NULL-E6.** n = 1 document, 2 drawings. Nothing generalises.

---

## What would falsify this

1. **E11 fails** — padding cannot clear the cut vertices on this graph.
2. **E14 fails** — dependence falls or holds under padding, so the declared
   conjunction would never fire and the tripwire is inert.
3. **E10 fails** — a fused field reaches the report, and the orthogonality rule
   is not actually enforced by the code.
