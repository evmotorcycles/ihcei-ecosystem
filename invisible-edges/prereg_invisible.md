# Pre-registration — invisible edges, the quotient pass, and two JEPA cards

Written and hashed **before the run**. 2026-09-15.

---

## Arm 1 — the question asked

> "If LINTEL trusts the explicit import statements but is blind to hidden
> dependencies like string dispatch or reflection, how should the pipeline flag
> these 'invisible edges' before the Laplacian matrix incorrectly zeroes out a
> cut vertex?"

The instinct behind the question is to **find** the hidden edges and put them in
the matrix. That is testable, and the first thing to test is whether static
analysis can tell a hidden dependency from a mention of a filename, because if
it cannot then adding them to the matrix replaces one wrong graph with another.

**The candidate detector.** Scan every source file for string literals and
comment text naming a real repository path, plus `importlib.import_module`,
`__import__`, `subprocess` invocations and `open()` on a repo path. Every hit is
a **candidate**, never an edge.

`where`: detector designed by me for this run, from the failure modes named in
the question. A different detector finds a different set.

| # | Prediction | Value |
|---|---|---|
| I1 | The repository contains at least 20 candidate invisible edges the import graph does not have | ≥ 20 |
| I2 | **Static analysis cannot separate a runtime dependency from a mention.** At least one candidate is a filename appearing in prose or a docstring with no runtime meaning | ≥ 1 false candidate |
| I3 | Adding all candidates **removes** at least one cut vertex the declared graph reported | ≥ 1 lost |
| I4 | Adding all candidates **creates** at least one cut vertex the declared graph did not report | ≥ 1 new |
| I5 | The two cut sets are therefore **not nested** — each holds a name the other lacks | not nested |
| I6 | The **name set** survives worse than under LINTEL's rewrites: strictly fewer than 27/27 survive | < 27 |

**I6 is the one that matters and the one I expect to be wrong about.** LINTEL's
certificate was that names are stable. If invisible edges break the names too,
the certificate is much narrower than it looked — stable under *how the code is
drawn*, unstable under *what the drawing leaves out*. If I6 misses and the names
hold, the certificate is stronger than I claimed.

**The answer this arm is designed to reach, whichever way it falls:** if I2
holds, the pipeline must **not** put candidates in the Laplacian. It should run
the readout twice — declared, and declared-plus-candidates — and report only the
cut vertices present in both, with the disputed ones named. That is LINTEL's own
method applied to a second transformation family, not a new mechanism.

## Arm 2 — the quotient pass

Proposed as the open item: statically detect indirection nodes (module body is
only re-exports; fan-out equals its re-export set), collapse them, and count
articulation on the quotient.

| # | Prediction | Value |
|---|---|---|
| Q1 | The quotient cut **count** is identical across the raw graph, +20 shims and +40 shims | all three equal |
| Q2 | The quotient graphs of those three are **isomorphic** as edge sets on the original names | identical |
| Q3 | The quotient is the **identity** on the un-shimmed graph, i.e. it collapses nothing that is not an indirection node | unchanged |
| Q4 | Merging a cut vertex into its sole importer **reduces** the count, so deflation is available too and the count is two-sided | count falls |

**Q1–Q2 are largely verification**: the quotient is built to undo exactly what
the shim did. They are here because if they fail, the collapse is wrong.

**Q3 is the real risk and I expect it to MISS.** This repository has genuine
one-in-one-out modules that are not shims. A quotient aggressive enough to erase
inserted indirection will also erase those, and then the quotient count is not a
repaired reading of the original graph — it is a reading of a different graph.
If Q3 misses, the quotient does **not** upgrade LINTEL to a trustworthy scalar,
and the shipped advice stays "trust the list, never the count".

## Arm 3 — what two JEPA cards say about collapse

`jepa-probe/` measured, and `geometric-gate/` corrected, that the stop-gradient
prevents representation collapse while the moving average contributes nothing in
that toy. The mechanism is one sentence of the paper (arXiv:2301.08243 §2).

Two **complete** model cards were fetched live from the Hugging Face connector on
2026-09-15 and frozen in `cards/`: `facebook/ijepa_vith14_1k` (3115 bytes) and
`facebook/vjepa2-vitl-fpc64-256` (3204 bytes). Both returned untruncated, so
unlike `pages-video/cards_frozen.json` these are whole cards.

| # | Prediction | Value |
|---|---|---|
| J1 | Neither card mentions representation **collapse** | absent from both |
| J2 | Neither card mentions **stop-gradient** or **exponential moving average** | absent from both |
| J3 | The I-JEPA card **does** state what it avoids doing — hand-crafted invariances, pixel-level detail | present |

**J1–J2 are not a criticism of the cards.** A model card is not a paper. The
finding, if it holds, is that the mechanism doing all the work is one sentence in
a paper and zero sentences in what a practitioner downloads — which is the same
"state what it cannot do in the same size type" rule this repository applies to
itself, observed elsewhere rather than asserted.

---

## Nulls, registered in advance

**NULL-I1.** The candidate detector is a lexical scan. It cannot resolve a
computed module name, a registry populated at import time, or a dependency
crossing a process boundary through data. Its recall is unknown and unknowable
from inside a static pass; only its **false positives** can be demonstrated.

**NULL-I2.** Adding candidates produces a graph nobody has claimed is correct.
It is a deliberately over-inclusive alternative, used to bound the readout, not
to replace it.

**NULL-I3.** A cut vertex is a routing fact, not a fault.

**NULL-Q1.** The quotient's definition of an indirection node is chosen. A module
that re-exports and *also* does one small thing is not caught, and a module that
happens to be one-in-one-out is caught whether or not it is indirection.

**NULL-J1.** Two cards. Nothing here characterises model cards in general, JEPA
implementations in general, or the practice of any organisation.

**NULL-J2.** The cards were fetched once, on one day. A card is a living file.

**NULL-GEN.** n = 1 repository throughout. The names-stable certificate was
measured on this graph and this rewrite family, and whether it holds elsewhere
is exactly as unmeasured as the count/names split was before N3 failed.

---

## What would falsify this

1. **I2 fails** — every candidate is a real runtime dependency, static analysis
   separates them cleanly, and they can safely go straight into the matrix.
2. **I6 fails** — the names survive invisible edges too, and LINTEL's
   certificate is broader than claimed.
3. **Q3 fails** — recorded as the quotient erasing real modules, which means it
   cannot be shipped as a repaired count.
