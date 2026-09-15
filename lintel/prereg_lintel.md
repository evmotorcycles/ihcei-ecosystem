# Pre-registration — is "single point of failure" a stable finding?

Written and hashed **before the run**. 2026-09-15.

---

## The problem this is for

Every dependency-graph tool reports articulation points and calls them single
points of failure. `page-code/blueprint.py` does it here. The number gets put on
dashboards, compared between projects, and tracked over time.

This session measured something that makes all of that suspect. In
`agi-stack/`, adding edges that introduce no new evidence cleared **every** cut
vertex. That was built as an attack. **It also happens by accident, constantly**:
a barrel file, a re-export shim, a facade, a module split in two during a
refactor. None of those change what the system depends on. All of them change
the drawing.

So the question is not "what are the single points of failure". It is **"which
of the reported single points of failure survive a change that alters no
behaviour"**.

## The rewrite family

Four rewrites, each preserving *what depends on what* while changing how the
code is organised. `where`: chosen by me to mirror ordinary refactors; they are
a declared modelling decision and a different family gives a different answer.

| | rewrite | the refactor it mirrors |
|---|---|---|
| **INSERT** | edge `A→B` becomes `A→P→B` | somebody added a re-export shim or barrel file |
| **COLLAPSE** | a one-in one-out node `P` is removed, `A→P→B` becomes `A→B` | somebody inlined a facade |
| **SPLIT** | node `A` becomes `A₁→A₂`, in-edges to `A₁`, out-edges from `A₂` | somebody split a module in two |
| **MERGE** | `A→B` where `B` has only `A` importing it, merged into one node | somebody merged two modules |

Reachability between original modules is preserved by all four. A finding about
fragility that does not survive them was a finding about file layout.

## The subject

The real Python and JavaScript import graph of this repository, read by
`page-code/blueprint.py`: **155 modules in the graph, 245 edges**, 440 files
scanned. Not synthetic.

---

## Predictions

| # | Prediction | Value |
|---|---|---|
| N1 | The raw graph has at least 5 cut vertices | ≥ 5 |
| N2 | INSERT on a **bridge** edge creates a new cut vertex — the inserted shim itself — in **every** case | 100% |
| N3 | At least one raw cut vertex **fails** to survive some behaviour-preserving rewrite | ≥ 1 artefact |
| N4 | At least one raw cut vertex survives **every** rewrite | ≥ 1 robust |
| N5 | SPLIT of a cut vertex that has both in- and out-edges yields **two** cut vertices where there was one | count rises by 1 |
| N6 | Cut-vertex **count** rises monotonically with the number of inserted shims, so the metric is inflatable at will with no behaviour change | monotone rising |
| N7 | Foster's total changes under INSERT and SPLIT, because the node count changes, so it **cannot arbitrate** which reading is right | total moves |

**N4 is the one that decides whether this is a tool or a demolition.** If nothing
survives, the honest report is that cut-vertex analysis has no stable content on
this graph and the right move is to stop reporting it — not to ship a instrument
that always says "nothing". If some survive, the survival set is the readout.

**N6 is the finding with the widest reach.** If a count can be doubled by
inserting shims that change nothing, then that count is not comparable between
two projects, or between one project and itself last month. Any "architecture
health" number built on it is partly measuring file-splitting style.

---

## Nulls, registered in advance

**NULL-N1 — a cut vertex is not a fault.** A shared kernel that everything routes
through is usually correct. `blueprint.py` already says this. Survival makes a
finding stable; it does not make it bad news.

**NULL-N2.** An edge exists only because somebody wrote an import. Dependencies
through a string, a plugin registry, a subprocess, an HTTP call or reflection are
invisible, and no rewrite here can reveal them. Absence of an edge is absence of
a declaration.

**NULL-N3.** The rewrite family is chosen, not derived. It mirrors refactors I
have seen; it is not a complete account of behaviour-preserving change, and a
finding that survives these four may fail a fifth.

**NULL-N4.** "Behaviour-preserving" here means reachability-preserving in the
declared import graph. It does **not** mean the refactor is safe, correct, or
free of runtime consequences. A re-export shim can change import time, circular
import behaviour and namespace contents — this session broke 41 tests that way.

**NULL-N5.** n = 1 repository, and it is this one. A codebase with different
module granularity will give different numbers, which is precisely the point
being made and also the reason nothing here generalises.

**NULL-N6.** Nothing here measures whether anybody's system actually broke.
Fragility is inferred from a drawing, not observed from an incident.

---

## What would falsify this

1. **N4 fails** — no cut vertex survives, and the reading has no stable content.
2. **N6 fails** — the count does not move under inserted shims, so the metric is
   robust after all and this study's premise is wrong.
3. **N2 fails** — inserting a shim on a bridge does not create a cut vertex, and
   my account of why indirection corrupts the reading is wrong.
