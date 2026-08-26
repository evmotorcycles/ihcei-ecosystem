# The dependency-audit protocol: three blockers and five defects

Written before anything was hashed, because that is the only moment these can
be fixed. After `PREREGISTRATION.md` is locked, a defect in it is permanent by
design — which is the point of locking, and the reason the check has to happen
now.

## It cannot run here. Three reasons, checked rather than assumed

| | |
|---|---|
| `gh` CLI | **absent** |
| GitHub search API, unauthenticated | **403.** The spec says "unauthenticated is fine for 30 repos". It is not, from here. |
| Repository scope | This session is scoped to **two** repositories. Searching GitHub for 30 arbitrary repos across three topics is precisely the thing that scope forbids. |

The third is not a technical limit and no token fixes it. GATE 1 asks for 30
repositories chosen by stars across three topics; two are reachable, and they
are not a sample of anything.

## Five defects in the protocol itself

### 1 · H2 and GATE 3 leave a gap, and it is the middle of the range

H2 claims **≥ 20%**. GATE 3 fails H2 at **< 10%**. A measured 15% neither
supports nor fails it.

Measured by `gates.js`: **the uncovered range is [0.10, 0.20), 9.995% of the
outcome space** — and it is the region a real result is most likely to land in.
That gap is where a decision gets made after the data arrives, wearing a locked
file's authority.

**Fix:** make `failsIf` the complement of `supportsIf` — `< 0.20`. Checked:
partitions cleanly, zero uncovered.

### 2 · GATE 2 points the wrong way

> "If the median load-bearing fraction < 40%, H1 is weakened: most dependencies
> are decorative and the README may be closer to the truth than expected."

The load-bearing fraction measures **manifest against code**. H1 is about
**README against structure**. A low fraction says the manifest overstates what
the code uses — which is itself a divergence, and says nothing whatever about
the README. The inference does not follow from the measurement, and if anything
runs the other way.

GATE 4 already tests H1 properly by counting divergences. GATE 2 should either
be attached to a hypothesis about manifests, or dropped.

### 3 · SLICE 4 cannot implement its own definition

LOAD-BEARING requires either a critical-path traversal from the entry point, or
the fallback "imported in ≥ 30% of source files". SLICE 4 fetches **only the
entry point file** and parses its imports. So the traversal never happens and
the fallback has no denominator. What it actually computes is depth-1 imports
from one file, which is a third thing the definition does not describe.

**Fix:** either state the definition as depth-1-from-entry-point and accept the
narrowness, or fetch the source tree. The current wording promises the second
and delivers the first.

### 4 · GATE 1 references an operation the spec forbids

> "Do not substitute a repository if it fails to **clone**."

SLICES 1–5 are explicitly API-only and never clone. The failure mode the gate
guards against cannot occur, and the failures that *will* occur — 403, no
manifest, missing entry point — have no stated handling.

### 5 · Layer 2 contradicts Layer 3, on the safety-relevant line

Layer 2, external signals: *"Run the project's test suite if one exists."*
Layer 3, CLAUDE.md: *"Do not execute any code from the audited repos."*

Running a test suite **is** executing the repository's code, and the proposal is
to do it for three repositories chosen by star count and never read. Arbitrary
code from unvetted sources, executed to check an audit that explicitly does not
read source for correctness.

**Fix:** drop the test-run, or replace it with a build-tool dependency listing
(`npm ls`, `pipdeptree`, `cargo tree`) which answers the actual question — does
the manifest match the resolved graph — without executing project code. That is
also a better test of the load-bearing classification than a test suite ever
was, and it is the falsifier the protocol's own "Where this breaks" section asks
for.

## What is right, and should not be lost in the fixing

The permanent-limit paragraph, stated before any data and repeated at the end.
"Do not substitute a repository — the gap is data." The refusal to score or rank
anything. The instruction to record failures rather than fill gaps with
plausible text. The second critic told not to soften. Those are the parts most
protocols do not have, and they are the reason the five defects above are worth
fixing rather than the protocol worth discarding.
