# Results — is "single point of failure" a stable finding?

Run 2026-09-15 on this repository's **real** import graph: 442 files scanned,
**156 modules in the graph, 246 declared imports**, 10 pieces. Offline,
deterministic, no network, no keys.

Predictions locked in `prereg_lintel.md`, sha256
`87f7bc79f3b81ec6c61f66dbec84a7b8b02ad08907a9af8679823abbaed54189`.

**Five hit. Two missed. The second miss overturned the study's own thesis, in a
more useful direction than the thesis would have gone.**

---

## The finding

> **The count is not a measurement. The names are — under this transformation
> family, and not under every one.**

**Narrowed by a later measurement, recorded here rather than left standing.**
`invisible-edges/` applied a second transformation family — candidate undeclared
edges (string dispatch, registries, subprocess calls) — and **only 18 of 27
names survived**. So the certificate is: stable under *how the code is drawn*,
**not** stable under *what the drawing omits*. The advice below is unchanged for
the count; for the names, read the list twice and act on the agreed part.

A plain articulation-point reading flags **27 modules** as single points of
failure. Insert 40 re-export shims that change no behaviour and the count climbs
to **39**. Insert 60 and apply splits and merges, and it reaches **46** —
**1.7×**, with nothing about the system changed.

But across all of it, **every one of the original 27 names is still reported.**

So the practical advice inverts depending on which you use:

| | |
|---|---|
| **Do not** compare cut-vertex counts between projects, or against the same project last month | it partly measures how finely code is split into files |
| **Do** trust the list of modules, under rewrites | it survived 60 shims, 8 splits and 8 merges without losing one |
| **But** re-read it against candidate undeclared edges | 18/27 survived that too; the other 9 are disputed, not wrong (`invisible-edges/`) |

Any "architecture health score" built on a count of single points of failure is
measuring file-splitting style alongside fragility. Nothing in the reading
distinguishes the two, and the number is inflatable at will by whoever is being
measured.

---

## What was predicted, and what happened

| # | Prediction | Result |
|---|---|---|
| N1 | ≥ 5 cut vertices | **HIT** — 27 |
| N2 | A shim on a bridge becomes a cut vertex, every time | **HIT** — 67/67 |
| N3 | At least one raw cut vertex is an artefact | **MISS** — zero were |
| N4 | At least one survives every rewrite | **HIT** — all 27 |
| N5 | Splitting a cut vertex yields two | **MISS** — it yields one |
| N6 | The count rises monotonically with inserted shims | **HIT** — 27 → 39, 1.44× |
| N7 | Foster's total moves, so it cannot arbitrate | **HIT** |

### N2 — and the defect that made it look like a miss

The first run reported **31 of 67** and scored N2 a miss. That was a bug in my
harness, not a finding: `bridges()` returns its endpoints sorted, and
`insert_shim` removed the edge only in the stored direction, so for the other
**36** bridges the original edge survived beside the shim and left a parallel
route. 31 + 36 = 67 exactly. Fixed to match either orientation; the prediction
was not touched. `test_the_harness_defect_that_made_n2_look_like_a_miss`.

### N5 — a genuine miss, with the mechanism measured

Splitting a cut vertex `A` into `A#in → A#out` does **not** give two cut
vertices. Across all 14 eligible modules:

| | in-half only | out-half only | both | neither |
|---|---|---|---|---|
| count | **9** | 1 | 4 | 0 |

**The fan-in half inherits the cut status; the fan-out half usually does not.**
Articulation is about what routes *through* a module from its importers, so the
half carrying the importers keeps it. My prediction had the mechanism wrong.

### N3 — the miss that was better news than the hits

The study was built expecting reported single points of failure to be artefacts
of file layout. **Zero of 27 were.** They survived the four registered rewrites
and a far heavier regime applied together.

That is the opposite of the premise, and it is more useful: *count* and *names*
come apart, and only the count is unstable. This is visible only because the
prediction was written down first and missed.
`test_the_prediction_that_missed_and_was_better_news_than_the_hit`.

### N7 — Foster is conserved through every rewrite, and that is the problem

| | total | expected | conserved |
|---|---|---|---|
| raw | 146.0000 | 146.0 | True |
| after INSERT | 147.0000 | 147.0 | True |
| after SPLIT | 147.0000 | 147.0 | True |

It moves, and it is conserved every time, because `parts − pieces` is true of
*every* drawing. **A counting identity prefers no drawing over any other**, so it
cannot say which reading is right. Same property measured in `lmd-scaling/` and
`jepa-probe/`, third consequence.

---

## The rewrite family

Four rewrites, each preserving what-depends-on-what while changing how the code
is organised. `where`: chosen by me to mirror ordinary refactors.

| rewrite | the refactor it mirrors |
|---|---|
| **INSERT** `A→B` ⇒ `A→P→B` | a re-export shim or barrel file was added |
| **COLLAPSE** `A→P→B` ⇒ `A→B` | a facade was inlined |
| **SPLIT** `A` ⇒ `A#in→A#out` | a module was split in two |
| **MERGE** sole-importer pair ⇒ one node | two modules were merged |

`test_every_rewrite_preserves_reachability` pins that no original module loses
its reach. `COLLAPSE` and `MERGE` refuse inputs that do not qualify, rather than
silently doing something else.

---

## What this cannot do

- **A cut vertex is not a fault.** A shared kernel that everything routes through
  is usually correct. Survival makes a finding stable, not bad news.
- **"Behaviour-preserving" means reachability-preserving in the declared import
  graph.** It does **not** mean the refactor is safe. A re-export shim changes
  import time, circular-import behaviour and namespace contents — this session
  broke 41 tests exactly that way.
- **An edge exists only because somebody wrote an import.** Dependencies through
  a string, a registry, a subprocess, an HTTP call or reflection are invisible,
  and no rewrite here can reveal them.
- **The rewrite family is chosen, not derived.** A finding that survives these
  four may fail a fifth.
- **Nothing here measures whether any system actually broke.** Fragility is
  inferred from a drawing, never observed from an incident.
- **n = 1 repository, and it is this one.** A codebase with different module
  granularity gives different numbers — which is the point being made, and also
  why nothing here generalises.

## Reproduce

```
python3 lintel/run_lintel.py            # ~20s
python3 -m pytest lintel/test_lintel.py -q
```
