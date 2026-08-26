# STRUCTURAL AUDIT — PREREGISTRATION
STATUS: BLOCKED_ON_ACCESS     # the registered run fires only with an authenticated Search API
PILOT:  separate, n <= 2, labelled, no pooled verdicts

FILENAME NOTE. This is deliberately NOT called PREREGISTRATION.md. That name is
taken at this repository's root by a locked pre-registration from 2026-08-06
whose own text reads "Do not change". The protocol as received instructs writing
to that exact filename in the working directory, with no collision check. See
defect 6 in AUDIT_PROTOCOL_DEFECTS.md.

## HYPOTHESES -> GATES

Each gate names its quantity, its partition, and why the quantity bears on the
hypothesis. All four partitions were checked with plexus/gates.js before this
file was hashed: zero uncovered, zero contradictions.

H1  README claims diverge from dependency structure.
    quantity     median structural divergences per repo   (SLICE 5)
    supportedIf  median >= 1
    failsIf      median <  1
    relevance    If READMEs were faithful to structure the median would be 0.
                 A nonzero median means the README promises capability the
                 dependency tree does not back.

H2  Load-bearing dependencies are rotting.
    quantity     fraction of load-bearing deps abandoned OR single-maintainer
    supportedIf  fraction >= 0.20
    failsIf      fraction <  0.20
    relevance    If the things a project leans on were healthy this fraction
                 would be low. The failure condition is the exact complement of
                 the claim; the old [0.10, 0.20) gap is closed.

H3  Structure reveals risk that surface text does not.
    quantity     lockfile-resolved dependencies absent from manifest surface
    supportedIf  >= 1 hidden dep in >= 1 verified repo
    failsIf      0 hidden deps across all verified repos
    relevance    A lockfile carries structure the README and manifest text do
                 not. A dep in the resolved graph but not in the surface text is
                 a fact only structure exposes.

H4  Manifests list more than the code uses.
    quantity     median load-bearing fraction AT THE DEEPEST COMPUTED DEPTH
    supportedIf  fraction <  0.80
    failsIf      fraction >= 0.80
    relevance    If the manifest matched the code the fraction would be near 1.
    CONFOUND, named because it is not otherwise separable:
                 A low fraction has TWO possible causes -- the manifest
                 over-declares, or the import window is too shallow to see the
                 use. A thin entry point delegating to modules four levels down
                 produces a low fraction with a perfectly accurate manifest.
                 Nothing else in this protocol distinguishes them, so the depth
                 sweep below is a precondition on computing H4 at all, not a
                 second gate.

## DEFINITIONS, computable without cloning or executing

LOAD-BEARING       imported at depth <= 3 from the main entry point, computed
                   and REPORTED SEPARATELY at depths 1, 2 and 3.
                   Fallback: imported in >= 30% of source files, only where the
                   file list is obtainable via the Git Trees API, which supplies
                   the denominator the old wording lacked.
DECORATIVE         in the manifest, not load-bearing at depth 3.
ABANDONED          no release in 18 months AND < 2 active contributors in 12.
SINGLE-MAINTAINER  one contributor holds > 90% of commits in 24 months.
STRUCTURAL DIVERGENCE  a README capability with no supporting dep or module.

## GAP RULE

A classification that cannot be computed is recorded as "not computable" and the
run moves on. The gap is recorded, never filled, and never substituted.

DEPTH PRECONDITION on H4. If a repository's load-bearing fraction is still
rising by more than 0.10 between depth 2 and depth 3, the window is
demonstrably too shallow for that repository and its contribution to H4 is
recorded as NOT COMPUTABLE rather than as support. A fraction still climbing at
the edge of the window is evidence about the window, not about the manifest.

## SAMPLE (GATE 1)

30 repos: 10 web-framework by stars, 10 CLI-tool by stars, 10 utility-library
sampled at random from 50-500 stars. Each failure is recorded, none substituted:

  search 403 or rate-limit     -> STOP. The run is BLOCKED and recorded as such.
  no manifest in known format  -> record, skip, count as gap.
  no entry point               -> record, SLICE 4 returns "not computable".
  no Trees listing             -> record, fallback disabled for that repo.

Clone failure is not listed because slices 1-6 never clone.

## VERIFIER, non-executing

For one repository per tier (n = 3), fetch the lockfile (package-lock.json,
Cargo.lock, poetry.lock, go.sum) and compare it against the manifest. Count
resolved dependencies absent from the manifest surface. No lockfile: record as a
gap. This reads two files and runs no project code, and it is the direct
falsifier of the load-bearing classification.

## GATE-RELEVANCE CHECK, and its own limit

Before hashing, a reader who did not write the gate completes, for each pair:
"this gate bears on this hypothesis because [quantity] would change if
[hypothesis] were false." Those sentences are the `relevance` lines above.

The limit, stated because it is measurable and was measured: two readers who are
instances of the same model are not two origins. Pressed with this project's own
instrument, two such readers settle 0.250 each rather than 0.500 -- worth having
and worth a quarter. A relevance check that raises the odds is not a proof, and
the only reader whose disagreement is worth a half is one from a different
origin: a person, or a document that can be opened.

## PERMANENT LIMIT

This audit maps dependency manifests, lockfiles and GitHub metadata. It does not
read source for correctness, does not run tests, and does not judge quality. A
clean graph does not mean safe; a messy graph does not mean broken. The joints
are shown. The walking is yours.
