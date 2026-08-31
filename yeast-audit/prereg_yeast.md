# Pre-registration — does the yeast interactome have zero cut vertices?

Written and hashed **before the graph was built or measured**. 2026-08-29.

## The claim under test

A pasted audit reports, for a 4,825-node yeast interactome:

> `Sole-Route Single Points of Failure (Cut Vertices): 0`
> `N = 4825 nodes, E = 15400 edges`

and concludes this "mathematically validates Dr. Denis Noble's cardiac
pacemaker experiments".

Two things are checkable here without any biology, and one is not checkable at
all. `yeast-interactome-audit.py` does not exist in this repository; the real
STRING v12 physical-links file for *S. cerevisiae* does, committed at
`repro/data/4932.protein.physical.links.v12.0.csv.gz`, sha256 `5993baac…`.

## Predictions

| # | Prediction | Value |
|---|---|---|
| Y1 | The real interactome has **many** cut vertices, not zero | ≥ 100 |
| Y2 | The edge count is **70,201**, not 15,400 | 70,201 |
| Y3 | The graph is in **more than one** piece | ≥ 2 |
| Y4 | The largest component still contains cut vertices | ≥ 1 |

**Y1 is the one that matters.** A real protein network has peripheral proteins
attached by a single interaction; every one of those makes its neighbour a cut
vertex. Zero would require 2-connectivity everywhere, which no biological
network of this size has.

## The category error, stated as an argument and NOT as a measurement

Even if the count were zero it would not validate Noble, and a large count does
not refute him. A **cut vertex is a fact about connectivity**: remove the node
and the graph falls into pieces. Noble's pacemaker result is about **functional
redundancy**: remove 80% of a current and the cell still keeps time, because it
re-routes *dynamically*, not because the interaction graph stayed connected.

A protein can be a cut vertex and non-essential. A protein can be deeply
embedded and lethal to lose. Graph connectivity and functional essentiality are
different quantities, and this repository's own rule is that different
quantities are never fused. **The instrument in the pasted audit does not
measure the thing its conclusion is about**, and no number it returns would fix
that. This paragraph is Layer 3 reasoning, not a result.

## Nulls

**NULL-Y1.** STRING physical links at `combined_score >= 400` is one threshold
on one database. A different cut gives a different graph and different counts.
**NULL-Y2.** Cut vertices say nothing about whether a knockout is survivable.
**NULL-Y3.** Nothing here tests Noble's experiment, which needs cells.
