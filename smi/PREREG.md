# SMI / LMD — pre-registration

Written and hashed **before** the harness was run. Everything below is a
commitment, including the two predictions that say a specified behaviour is
wrong.

## What is being built

The **Synaptic Mesh Interface**: a layout engine where on-screen elements are
nodes in a dependency graph and their positions are not authored but *derived*.
Distance between two elements is the effective resistance between them:

```
L⁺ = pinv(L)
R_ij = L⁺_ii + L⁺_jj − 2·L⁺_ij
d_ij = √R_ij
```

Elements that depend strongly on each other are pulled close; elements with only
a weak path between them drift apart. Nothing about the picture is authored.

## H0 — THE −0.5 SLOPE IS AN IDENTITY, NOT A RESULT

**Predicted before running: the sweep cannot fail.**

For a scalar J > 0, `pinv(J·L₀) = J⁻¹·pinv(L₀)`. Therefore `R_ij(J) = R_ij(1)/J`
and `d_ij = √R_ij ∝ J^(−1/2)` **exactly**, for every pair, on every graph, at
every N. The log–log slope is −0.5 and R² is 1.000000 by construction.

So the sweep is **not** evidence that "space is emergent". It is a correctness
check on the implementation: it fails if `pinv` breaks, if the Laplacian is
built asymmetrically, or if the clip is wrong.

- **Prediction H0a:** slope = −0.5 ± 1e-4, R² ≥ 0.999999 on a ring, N = 100.
- **Prediction H0b:** the same slope on a path, a star, a dense random graph and
  a sparse random graph — because topology is irrelevant to it.
- **It is reported as `IDENTITY (CONTROL)`, never as `PASS`.**

## H1 — uniform coupling changes scale, never shape  *(falsifiable)*

If every edge is scaled by the same J, the normalised distance matrix
`D / max(D)` is unchanged. A GUI can therefore zoom without reordering anything.

- **Predicted:** max element-wise change in `D/max(D)` < 1e-4 across
  J ∈ [10⁻¹, 10²] at float64.
- **Fails if:** any element moves more than that.

## H2 — a disconnected mesh does NOT report infinite distance  *(falsifiable)*

The specification says broken links yield infinite distance. **Predicted: it
does not.** `pinv` of a disconnected Laplacian returns finite, meaningless
numbers across components.

- **Predicted:** for a ring cut into two arcs, `d(i,j)` between components is
  finite and < 1e3.
- **Consequence if confirmed:** components must be detected explicitly, and the
  engine must return `inf` itself. Shipping the specified behaviour would render
  unrelated elements as *near neighbours*.

## H3 — J → 0 collapses distance to zero, not to infinity  *(falsifiable)*

**Predicted: the specified "low coupling ⇒ infinite distance ⇒ visual rot" is
inverted at the limit.** With all weights zero, L = 0, pinv(0) = 0, so d = 0.

- **Predicted:** `d(0, N/2) → 0` as J → 0, and exactly 0.0 at J = 0.
- **Consequence if confirmed:** a totally broken mesh would render identically to
  a perfectly coupled one — maximum contraction. The compositor must special-case
  it rather than trusting the metric.

## H4 — a local pull moves near nodes more than far ones  *(falsifiable)*

Raising J on a single edge is not a global rescale, so H1 does not apply.

- **Predicted:** the change in distance from the pulled node falls monotonically
  with graph hop-distance from that edge, over ≥ 90% of adjacent hop pairs.
- **Fails if:** the response is flat, non-monotone, or global.

## Gates fixed now

| quantity | gate |
|---|---|
| H0 slope | −0.5 ± 1e-4 |
| H0 R² | ≥ 0.999999 |
| H1 shape drift | < 1e-4 |
| H2 cross-component distance | finite, < 1e3 |
| H3 d at J=0 | == 0.0 |
| H4 monotone fraction | ≥ 0.90 |

Precision: float64 (`jax.config.update("jax_enable_x64", True)`). At float32 the
ring N=100 slope reads −0.500003, which is noise, not signal.

## What this is not

The engine computes effective resistance on a graph. It says nothing about
physics, and "Latency-Metric Duality" here is a name for the construction, not a
claim about spacetime. No result in this module is evidence about the nature of
space.
