# Page Code — the blueprint half, and what it found on agent-built projects

Pre-registration `page-code/prereg_blueprint.md`, sha256
`bf47c93de29edd2cb030a23a370d04ec9e9b7e9a25132a221c6dadc36e2f1fc9`, locked
before any import graph was looked at. `python3 page-code/run_blueprint.py`
reproduces every number. Offline, deterministic, no network.

---

## What was added, and what was not touched

Page Code already audits what an agent **says** and what a diff **does** — a
corroboration gate on coercion, `dev-v1` lexicon, 22/22 in `pagecode.test.mjs`.
**That is unchanged.**

What it could not do was say what a project **is**. `blueprint.py` reads declared
`import` and `require` statements, builds the intra-project graph, and hands it
to `keel.survey`. The two halves are never combined: there is no field anywhere
that adds a structural reading to a rhetorical one.

```
understands_language = False
proves               = NOTHING
```

It reads import statements. It does not read code. **A module that everything
imports may be exactly right** — a shared kernel usually is. An edge exists only
because somebody wrote an import; anything reached through a string, a registry,
a subprocess or reflection is invisible.

---

## The readings

### This repository — 401 files, a real agent-built project

| | |
|---|---|
| files scanned | 401 |
| in the graph | **127** |
| **isolated** | **274** |
| edges | 197 |
| pieces | **9** |
| single points | **23** |
| busiest hub | `echo/echo.mjs`, imported by **22** |

### `ihcei_v3/` — the separately-authored stack

| | |
|---|---|
| files scanned | 26 · in graph **20** · isolated **6** |
| pieces | 2 · single points | **4** |
| busiest hub | `gt_probabilistic.py`, imported by **6** |

All five real predictions held: B1 (≥1 single point) · B2 (>1 piece) · B3
(isolated > joined) · B4 (hub fan-in ≥5) · B8 (the second stack has joints too).

**The hub count was cross-checked independently.** A separate regex run over
each of the 22 claimed importers confirmed **22 of 22**. `weir/weir.test.mjs`
appearing as a single point is also real: it is the only path to
`weir/upstream_fixture.mjs`, so removing it genuinely disconnects.

---

## Finding 1 — two thirds of what an agent writes stands alone

**274 of 401 files import nothing else in the project.**

This was registered as the prediction I least expected to hold, because it
bounds the reach of the whole service: *on a typical file there is nothing
structural to read.* An audit that only speaks when files are joined will be
silent on most of a codebase.

That is not a failure of the audit. It is a fact about the population being
sold to, and it belongs in the pitch rather than in a footnote after it.

## Finding 2 — the two projects are shaped oppositely, and that was not predicted

| | joined | isolated |
|---|---|---|
| this repository | 127 | **274** |
| `ihcei_v3/` | **20** | 6 |

Same extractor, same day, inverted shapes. One sprawling and mostly standalone,
one dense and tightly wired. Whatever "an agent-built project looks like" is, it
is **not one thing**, and any pricing or product claim resting on a typical
shape rests on something this data says does not exist.

## Finding 3 — the law lands on real code

22 modules import `echo/echo.mjs`. Each settles **1/484 = 0.002066…** — exactly
1/m². The count `counted_twice` would have given is **HALTED**, not reduced:
these are not 22 independent groundings, they are one, counted 22 times.

On `ihcei_v3`, 6 modules on `gt_probabilistic.py`, each settling **1/36**.

**NULL-B1 applies and is the point.** `spar/spar.py` being imported by 17 things
means the project has a shared measurement kernel. That is correct design. The
reading says *where the load is*; it is not permitted to say the load is
misplaced, and the suite greps the readings for judgement words.

---

## The defect: the auditor is inside the corpus it measures

The first version of the suite asserted `files_scanned == 401`. **Adding the
test file made it 402 and the assertion failed** — the audit walks the
repository it lives in, so writing a test for a count changes that count.

This is not fixable by excluding our own files: any customer who vendors the
tool into their repository has the same problem. The suite now asserts
**relationships**, which are stable, and never an absolute count.

Then the test written to record that defect **failed on itself**: it forbade the
string `files_scanned"] ==` and contained it. Fifth instance of that shape in
this repository — a rule tripping the search for violations of itself — and it
happened inside the test recording the fourth. The forbidden string is now built
rather than written.

---

## The revenue null, registered in advance

**Nothing in this run measures whether anybody would pay for it.** No
conversion, no willingness-to-pay, no adoption. A structural reading being
*correct* and a structural reading being *bought* are different propositions and
only the first is tested here.

Three things this run does say about the commercial case, none of them
flattering by construction:

1. **Reach is bounded by Finding 1.** If two thirds of files are isolated, the
   per-file value of a structural audit is zero for most files. The unit that
   has value is the *project*, not the file.
2. **There is no typical project** (Finding 2), so a fixed-price audit priced on
   an assumed shape is priced on an assumption this data contradicts.
3. **The strongest signal is still unreachable.** τ_v abstains for want of
   per-item timestamps, exactly as registered in `keel/prereg_keel.md`.

Two projects, both written under unusual discipline, is not a sample of
"millions of projects generated by Claude Code". That phrase is a market
description. This is n = 2.
