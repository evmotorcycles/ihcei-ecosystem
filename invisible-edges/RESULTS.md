# Results — invisible edges, the quotient, and two JEPA cards

Run 2026-09-15 on this repository's real import graph: **156 modules, 246
declared imports, 27 cut vertices**. Offline and deterministic; the Hugging Face
fetch was an attested manual step and every run here is against `cards/`.

Predictions locked in `prereg_invisible.md`, sha256
`1f3455944c51ef2f306bf2d50041e046438a8077ee2124c34c716b5d9f23edc9`.

**Nine hit. One missed — Q3, and it is the reason the quotient does not ship.**

---

## The answer to the question asked

> *How should the pipeline flag invisible edges before the Laplacian
> incorrectly zeroes out a cut vertex?*

**It should not put them in the Laplacian at all.** Run the readout twice —
declared, and declared-plus-candidates — and report the intersection, naming the
disputed ones. That is LINTEL's own method applied to a second transformation
family, not a new mechanism.

The reason is measured, not argued. A candidate detector found **92** places a
module names another module that the import graph does not link. **31 of them
sit only in comments or docstrings.** A filename in prose is lexically identical
to a filename in a `subprocess` call, so the detector can demonstrate its own
false positives and can say **nothing whatever about its recall**. Putting
candidates straight into the matrix would replace one wrong graph with another.

| | modules | edges | cut vertices |
|---|---|---|---|
| declared | 156 | 246 | **27** |
| declared + 92 candidates | 156 | 338 | **22** |

Adding them **removes 9** cut vertices and **creates 4**. The two readings are
not nested — each holds names the other lacks. **18 of 27 names survive both.**

## The correction this forces to LINTEL

Last commit's certificate was *"the count is inflatable, the names are stable"*.
That was measured under one invariance group and it does not extend:

| invariance group | what happens to the names |
|---|---|
| behaviour-preserving rewrites of the drawing (shims, splits, merges) | **27/27 survive** |
| what the drawing leaves out (candidate invisible edges) | **18/27 survive** |

**I6 hit, and it narrows the product.** The names are stable under *how the code
is drawn*. They are **not** stable under *what the drawing omits*. Those are
different transformation families and only the first was measured in `lintel/`.
The shipped claim has to say which one it is.

The nine names that did not survive are not thereby wrong — a candidate edge is
not a real edge either. They are **disputed**, and the honest readout names them
as disputed rather than picking a side.

---

## Arm 2 — the quotient pass: Q3 MISSED, and that settles it

| shims inserted | cut vertices | quotient cut vertices | nodes collapsed |
|---|---|---|---|
| 0 | 27 | **26** | 2 |
| 20 | 32 | **26** | 22 |
| 40 | 42 | **26** | 42 |

**Q1 and Q2 hit**: the quotient count is identical across all three, and so are
the quotient edge sets. The raw count moved 27 → 32 → 42 and the quotient did
not move at all. As a deflator of inserted indirection, it works exactly as
proposed.

**Q3 missed, as the pre-registration expected it to.** The quotient is *not* the
identity on the un-shimmed graph: it collapsed **2 real modules**,
`plexus/metaphor.js` and `plexus/press.js`, which are genuinely one-in one-out
and are not indirection at all. So the quotient's 26 is not a repaired reading
of the original graph — it is a correct reading of a **different** graph, one
with real modules deleted.

**Q4 hit**: merging a cut vertex into its sole importer takes 27 → 26. So the
count is two-sided — inflatable by shims, deflatable by merges.

**Therefore the quotient does not upgrade LINTEL to a trustworthy scalar, and
the shipped advice is unchanged: trust the list, never the count.** The open
item is closed, in the negative.

---

## Arm 3 — two JEPA cards, fetched live

Both returned **complete**, not truncated: `facebook/ijepa_vith14_1k` (3115
bytes) and `facebook/vjepa2-vitl-fpc64-256` (3204 bytes).

| | mentions collapse | names the mechanism |
|---|---|---|
| I-JEPA (arXiv:2301.08243) | **no** | **no** |
| V-JEPA 2 | **no** | **no** |

**J1 and J2 hit. This is not a criticism of the cards** — a model card is not a
paper, and **J3 hit**: the I-JEPA card does state what it avoids doing
("hand-crafted data transformations", "pixel-level details"). It is not a card
that says nothing.

The observation is narrower and it lands on this repository as much as on
anyone: the mechanism `jepa-probe/` measured, and `geometric-gate/` corrected to
the stop-gradient specifically, is **one sentence of the paper's section 2 and
zero sentences of what a practitioner downloads**. Same "state what it cannot do
in the same size type" rule this project applies to itself, observed elsewhere
rather than asserted.

### The instrument defect that made J2 look like a miss

J2 first read **MISS** on the I-JEPA card. The term `"ema"` was matched as a
substring, and it occurs inside **"semantically"** — ordinary English in a card
about semantic representations. The acronym needs word boundaries; the phrases
do not. Fixed, and kept as
`test_the_instrument_defect_that_made_j2_look_like_a_miss`.

That is the **second instrument defect in two turns**, after the
bridge-direction bug in `lintel/`. Both had the same shape: a lexical test that
fired on something that looked like the thing it was looking for.

---

## What this cannot do

- **The detector's recall is unknown and unknowable from a static pass.** It can
  demonstrate its false positives; it cannot demonstrate what it missed. A
  computed module name, a registry filled at import time, or a dependency
  crossing a process boundary through a data file leaves no mark it can read.
- **The widened graph is not a correct graph.** It is deliberately
  over-inclusive, used to bound the reading, not to replace it.
- **A cut vertex is a routing fact, not a fault.**
- **The quotient's definition of an indirection node is chosen.** One-in one-out
  catches real modules with that shape and misses a module that re-exports *and*
  does one small thing.
- **Two cards, fetched once, on one day.** Nothing here characterises model
  cards in general, JEPA implementations in general, or any organisation's
  practice. A card is a living file.
- **n = 1 repository throughout.** Whether the names-stable certificate holds on
  any other graph is exactly as unmeasured as the count/names split was before
  N3 failed last commit.

## Reproduce

```
python3 invisible-edges/run_invisible.py        # ~25s
python3 -m pytest invisible-edges/test_invisible.py -q
```
