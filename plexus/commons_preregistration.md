# Pre-registration — the structure commons

Written and hashed **before** `commons.js`, `library.js` or `test_commons.py`
were run even once. Every number below was worked out by hand from the graphs
defined here. The test suite's job is to disagree with me.

---

## What is being claimed

That a **structure** — parts, links, sources, a conclusion — can be contributed
to a commons, and that the same structure measured in one domain gives the same
answer in another, because the arithmetic never reads the labels.

If that is true, a library of structures is an asset a fork cannot copy: code
can be copied, a set of shapes people chose to give cannot.

If it is false — if two graphs with the same shape and different words give
different numbers — the whole idea is dead and this file says so first.

---

## What is NOT being claimed

Nothing here shows that a commons raises a valuation ceiling. That claim rests
on a **contribution rate** — the fraction of people who, having bought the
software, give a structure back. That number is **0 today**, because nothing has
shipped and nobody has contributed. It is not measurable in this repository by
any means, and no test below pretends otherwise. See NULL-1.

---

## Scope of the sources, stated plainly

The task named GitHub open-source projects and HuggingFace as the place to find
real problems. Two limits apply and neither is worked around:

1. This session's GitHub access is **scoped to two repositories**
   (`evmotorcycles/ihcei-ecosystem`, `evmotorcycles/govphys_pat`). Repository-wide
   or global code search is out of scope and is not used.
2. No paid API, no keys, no scraping.

So the seed structures are **not mined**. Each is either (a) a defect measured
inside this repository, with the file named, or (b) a publicly documented,
independently checkable property of a well-known open-source mechanism — a CSP
directive, `caches.addAll`'s atomicity, a single package registry, a model hub.
Every entry carries a `provenance.kind` of `measured-here` or `cited`, and the
tests refuse an entry that carries neither. A structure that came from a real
problem and a structure that came from my imagination must never be stored in
the same shape without a label separating them.

---

## The graphs (definitions, so the predictions are checkable)

Weights are 1.0 everywhere unless stated. `→` is an undirected link.

**A · sole-maintainer**
- `drawn`: parts {Maintainer, Review, Release signing, Security response, The project ships};
  links Maintainer→each activity, each activity→The project ships;
  sources = the three activities; conclusion = The project ships.
- `actual`: same graph, sources = {Maintainer}.
- `remedy`: add a second maintainer linked to all three activities;
  sources = {Maintainer, Second maintainer}.

**B · three-audits-one-threat-model** — same graph as A, every label different
(Threat model / Audit A / Audit B / Audit C / The system is secure).

**C · inline-only-under-csp** — same graph as A again
(CSP directive / three script files / The app runs).

**D · atomic-install-list**
- `drawn`: star — 12 assets each linked to *The app installs*; sources = the 12 assets.
- `actual`: chain — installs→asset 12→asset 11→…→asset 1; sources = {asset 1}.
- `remedy`: star again, but the fetch is per-asset and failure is tolerated.

**E · two-ways-into-the-vault**
- `drawn` and `actual`: {The data, The key, Password}; Password→key→data; sources = {Password}.
- `remedy`: add Recovery code→key; sources = {Password, Recovery code}.

**F · benchmark-contamination**
- `drawn`: {Eval A, Eval B, The model generalises}; both evals→conclusion; sources = both evals.
- `actual`: insert one shared corpus upstream of both; sources = {Shared corpus}.
- `remedy`: two separate corpora, one per eval; sources = both corpora.

**G · one-mirror-many-packages** — 40 packages, one registry. Same shape as A with 40 activities.

**H · model-weights-one-host** — 6 models, one hub. Same shape as A with 6 activities.

---

## Predictions

`deepest` = the largest FATHOM dependence over the sources.
`blind spot` = deepest(actual) − deepest(drawn).
`relief` = deepest(actual) − deepest(remedy).

| # | Prediction | Value |
|---|---|---|
| P1 | Foster's theorem holds for every structure in every slot | \|Σ bearing − (parts − pieces)\| < 1e-9 |
| P2 | A `drawn` — each of three activities | 0.333333 |
| P3 | A `actual` — the maintainer | 1.000000 |
| P4 | A blind spot | 0.666667 |
| P5 | A `remedy` — two maintainers | 0.250000 |
| P6 | **Transfer.** B and C return dependences identical to A, in all three slots, to within 1e-12, sharing no word with A or each other | identical |
| P7 | D `drawn` — each of 12 assets | 0.083333 |
| P8 | D `actual` — the chain | 1.000000, blind spot 0.916667 |
| P9 | D `actual` — every link bearing, and the count of parts whose removal breaks the graph | 1.000000; 11 parts |
| P10 | E `actual` / `remedy` — replicating the vault result already in the suite | 1.000000 / 0.250000 |
| P11 | F blind spot | 0.500000 |
| P12 | G `drawn` — each of 40 packages | 0.025000 |
| P13 | H `drawn` — each of 6 models | 0.166667 |
| P14 | Mean blind spot across all eight entries | 0.653125 |
| P15 | An entry carrying any key other than parts/links/sources/conclusion is refused with a **reason**, not an exception | refused |

P1–P14 test whether the code agrees with arithmetic I did by hand. They are
verification, not discovery, and are labelled as such. P6 and P15 are the only
two that could kill the idea rather than the implementation.

---

## Nulls, registered in advance

**NULL-1 — the one that matters.** Contribution rate is 0 and untestable here.
Nothing in this repository can show that a commons raises a ceiling from $1.44T.
The only evidence would be people contributing structures after buying the
software, and that requires shipping first. Any later claim that the commons is
working must cite a contribution count, not a measurement in this file.

**NULL-2.** The eight seed entries were written by one person in one sitting. A
library of eight is not a commons; it is a worked example. Calling it a commons
before an outside contribution arrives would be the same error as calling the
GPU ring sweep evidence.

**NULL-3 — a limit of the engine, expected to show up in D.** FATHOM's sources
are **disjunctive**: several sources support a conclusion in parallel, so more
sources always means less dependence on each. `caches.addAll` is
**conjunctive** — all twelve must succeed or none do. There is no conjunction
operator, so a conjunction has to be drawn as a chain. If D's numbers come out
as predicted, that is not a discovery about caching; it is a demonstration that
the naive drawing of a conjunction is wrong by 0.916667, and that the engine
cannot warn you about it.

---

## What would falsify the whole idea

1. **P6 fails.** Isomorphic graphs with different words give different numbers →
   transfer is a wording effect → a library of shapes is worthless.
2. **Nobody contributes.** If the software ships and fewer than 5% of buyers
   contribute a structure within 60 days, the fourth pillar is imaginary and the
   $1.44T ceiling stands. This gate is not testable here and is recorded so it
   cannot be quietly dropped later.
3. **The shapes do not recur.** If eight entries produce eight unrelated shapes,
   there is nothing to transfer and the library is a list, not a commons. Three
   of the eight are predicted isomorphic; if that is only true because I wrote
   them that way, the honest reading is that the recurrence is my doing and not
   the world's, and it must be re-tested against structures I did not write.

Gate 3 is the one I am most likely to fool myself on, so it is stated here
rather than after the numbers arrive.
