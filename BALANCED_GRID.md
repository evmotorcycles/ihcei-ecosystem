# The balanced grid — the fix we promised, and it didn't work

**Spec** `5576e524581f405ed2cec785664ed6b7704ffaa5c692058b7a9c93f87337f543` · locked after a
**bracketed** pre-flight, before any of the 20 artifacts was evaluated · **4/7**

```bash
python3 -m pytest -q balanced-grid/test_bg.py
```

> I told you this gap was "fully closable" and that it would convert Q4 from unlicensed to
> licensed. **That was wrong**, and it was wrong in the direction of optimism.

---

## What was promised

HELM v2's self-audit failed at Δ = 0.1256. Its disclosure **D9** diagnosed the cause as a
defect in the *grid*, not the engine: only 1 of 8 self-report slots was "none", so the
incidence term `I` was pinned at 0.4375 and Δ could not reach the floor. D9 committed to a
specific fix, in writing, before this run existed:

> *"Balance the grouping — equal numbers of self-report-present and self-report-absent
> cells — and declare that design BEFORE data. That is an experiment-design fix, not a
> floor change."*

This is that fix. 20 artifacts no engine had ever seen. 10 self-reports split 5/5 by a
semantic rule written before any evaluation. **Floor left at 0.20.**

## The line I had to stay on the right side of

Rebalancing a grid *specifically so that a failed audit passes* is one short step from
gaming it. The distinction I held to, declared in the spec itself:

- **Moving the floor** after failing it → immunisation. Never.
- **Repairing a design defect that made a declared standard unreachable** → legitimate,
  but only under three conditions, all checkable in the locked document.

**Condition 2 was the dangerous one.** Adding four *neutral* self-reports would raise a
naive aggregate shield score `S` by dilution alone — buying the primary gate with the audit
fix. Two defences were declared in advance:

- The primary shield became **`S_HARD`**, computed *only* over the 5 self-certifying
  reports. Dilution cannot touch it.
- Gate **W4 fails the run if `S_HARD` comes in materially *above*** the held-out 0.9843. A
  gate that only trips on improvement is the only kind that catches a design change buying
  its own primary.

**Condition 3** needed the gate to still be able to fail. The pre-flight probe ran the
balanced grid over two *already-burned* artifact sets and **bracketed the threshold**:

```
burned DES texts          Δ = 0.1067   below the floor
burned HELM v2 texts      Δ = 0.3000   above the floor
```

Same grid, opposite verdicts. Balancing does not by itself buy a pass. `S` and `G` were
deliberately **not** probed, and the 20 new artifacts were not touched.

## The fix worked on the term it targeted. The audit failed anyway.

```
                 HELM v2 grid    balanced grid
  I                  0.4375   →     1.0000     exactly as designed
  V                  0.5625   →     0.4000     fell
  C                  0.5104   →     0.2650     fell
  Δ                  0.1256   →     0.1060     floor 0.20, UNCHANGED
```

`I` went to exactly 1.0 — which is **not a discovery**. The 5/5 split forces it
arithmetically. It is a **design constant**, flagged as such by the too-perfect rule, and
Δ on this grid is really a test of `V × C`.

**The D9 diagnosis was incomplete.** Fixing `I` was necessary and nowhere near sufficient.

**Fifth consecutive void** — SDL 0.1536 · CRM 0.0005 · DES 0.0125 · HELM v2 0.1256 ·
balanced grid 0.1060. The floor did not move this time either.

## The more interesting failure

**W2 failed.** The verdict range across the 20 artifacts with no self-report was **0.1199**
for v1 and **0.1882** for v2, against a 0.30 bar. *The engines barely separate these texts
at all.* W3 then failed on both axes: `S_HARD` 0.9072 against 0.95, `G` 0.1842 against 0.20.

Three failures, one cause.

## The real result of this run is post-hoc

**15 of the 20 artifacts return the identical baseline verdict `0.1428` — under *both*
engines.**

| | Spearman vs declared manipulativeness | Spearman vs **word count** |
|---|---:|---:|
| HELM v1 | **+0.0445** | **−0.4831** |
| HELM v2 | **+0.0388** | **−0.4774** |

Mean verdict by the band declared in the spec:

```
                       v1        v2
  factual            0.1298    0.1276
  hedged             0.1272    0.1240
  mildly pressuring  0.1428    0.1428
  strongly manip.    0.1277    0.1347     ← lower than "mildly pressuring"
```

Flat, and **mis-ordered**. The single most manipulative text scores *below* the single most
factual one, on both engines.

### It is not v2's density weighting

v1 gives −0.4831 against word count; v2 gives −0.4774. **The same number.** The length
effect lives in the gate and regex structure both engines share, not in v2's division by
word count. **Replacing v2 would change nothing.**

### What it suggests about our earlier numbers

On the DES set and the HELM v2 held-out set, the manipulative texts were also the **short**
texts. Length and manipulativeness were confounded. This spec deliberately broke that
confound — the 2-word *"Act now."* sits in the most manipulative band while three 30-word
texts sit in the factual band — **and the signal disappeared.**

That is consistent with `G = 0.2980` having measured **length** rather than
**manipulation**. Consistent with — not proof of.

### DCM voided the run for exactly the right reason

Δ failed because the verdicts are concentrated. They are concentrated because the engine
does not discriminate the gradient. **The void and the finding are the same fact seen
twice.** The self-audit did not obscure the result; it detected it.

## The limit, and it is serious

**The band labels are mine.** Written into the spec by the same author who maintains the
engines' test suites. They are **not** independent rater labels, so **W8 stays
UNTESTABLE-HERE and HELM is not refuted here.**

What carries the weight is the *direction*: author labels are biased **toward** agreeing
with the author's own engine, and the correlation still came out at zero. A positive result
from these labels would have been worth little. A null from them is harder to dismiss.

## The gates

| Gate | Locked bar | Measured | |
|---|---|---:|---|
| W1 integrity + bracketed pre-flight | 600 evals, probe in spec | 600 | PASS |
| **W2 failing region populated** | range ≥ 0.30 both engines | **0.1199 / 0.1882** | **FAIL** |
| **W3 v2 clears both axes (`S_HARD`)** | ≥ 0.95 and ≥ 0.20 | **0.9072 / 0.1842** | **FAIL** |
| W4 balancing didn't flatter the shield | `S_HARD` ≤ 0.9943 | 0.9072 | PASS |
| W5 v1 responsiveness replicates | \|G − 0.2980\| ≤ 0.10 | 0.2070 | PASS |
| W6 control still leaky | `S_HARD` < 0.95 | 0.4110 | PASS |
| **W7 DCM self-audit** | Δ ≥ 0.20 | **0.1060** | **FAIL** |
| W8 right content? | — | — | UNTESTABLE-HERE |
| W9 tool roles | — | — | EXCLUDED |

**W7 not met → W2 through W6 are UNINFORMATIVE**, including the three that passed.

## Where this leaves Q4

Q4 (reference-lock: *can something verify without being corrupted by what it verifies?*)
is **not** licensed by this run, and is in a **worse** position than before it.

Before: two numbers, `S` and `G`, computable on any evaluator, with a rock detectable by
the second. After: the `G` side of that pair may have been measuring text length on every
set we ever ran it on, and we cannot yet tell.

**What would actually close it** is not another grid. It is **manipulativeness labels from
raters who did not build the engine**, on texts where length and manipulativeness are
decorrelated by design. Until then `G` is a number whose referent is unknown.

## What is not claimed

HELM is not refuted. This is one 20-text set, scored against author-supplied labels, in a
run its own self-audit declared uninformative. The claim is narrower, and it is about our
**measurements** rather than about the engine:

> The shield-and-signal numbers reported for HELM in DES and in HELM v2 were measured on
> sets where length and manipulativeness were confounded, and no run so far has separated
> them.

**v1 remains the shipping engine.** Nothing here is a reason to replace it — and nothing
here is a reason to trust its `G` score either.
