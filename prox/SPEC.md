# PROX/1 — format and algorithm

A PROX index is a coordinate system. It stores **positions, not content**: the
items' text cannot be reconstructed from it, which is what makes an index safe to
sync, share or publish when the underlying collection is not.

---

## 1. The coupling graph

Nodes are items `0 … n_items-1` followed by features `n_items … n_items+n_feats-1`,
plus one implicit **horizon** node coupled weakly to every other node.

Edges:

| Kind | Endpoints | Weight |
|---|---|---|
| item–feature | item `d`, feature `f` | `J_text · tf/(tf+k1) · idf(f)` |
| item–item | any two items | `J_class` for the relation's class |
| horizon | every node | `ε` (`reach`) |

`idf(f) = ln(1 + (N - df + 0.5)/(df + 0.5))`, `k1 = 1.2`.

**Features** are hashed character n-grams of sizes 3, 4 and 5 over the NFKC-folded,
lowercased, whitespace-collapsed text, padded with a leading and trailing space,
plus whole whitespace tokens prefixed with `\x00w`. The bucket is
`crc32(ngram, seed) mod n_buckets`. There is no vocabulary file and no language
parameter; every script decomposes identically.

**The horizon term is load-bearing.** Without it, resistance between disconnected
components is infinite and the Laplacian is singular. With it, `A = L + εI` is
positive definite, the solves are well-conditioned, and `ε` becomes a meaningful
control: large `ε` saturates distance locally, small `ε` lets association propagate
further. `reach → 0` recovers the ungrounded Laplacian of the LMD telemetry, and
`tests/test_core.py` verifies the bias shrinks monotonically toward it.

---

## 2. The embedding

Let `C` be the `(m + n) × n` matrix whose first `m` rows are `√w·(e_i − e_j)` for
each edge and whose last `n` rows are `√ε·e_i`. Then `A = CᵀC = L + εI` and

```
R_ij = (e_i − e_j)ᵀ A⁻¹ (e_i − e_j) = ‖ C A⁻¹ (e_i − e_j) ‖²
```

Resistance is a squared Euclidean norm, so for a random `±1/√k` Rademacher matrix
`Q` of shape `k × (m+n)`, the Johnson–Lindenstrauss lemma gives

```
Z = Q C A⁻¹        ⟹        R_ij ≈ ‖ z_i − z_j ‖²
```

`Z` is computed as `X = A⁻¹ (QC)ᵀ`, which is `k` sparse solves. `Q` is never
materialised: each of its `k` rows is generated from a seeded PRNG, multiplied
into `C`, and discarded.

**Guarantees.**

- `d(i,j) = ‖x_i − x_j‖` is a metric *exactly*, for any `k`, because it is
  literally a Euclidean distance. Approximation affects the values, never the
  axioms.
- Error falls as `1/√k` (measured: median 11.7% at k=16, 1.5% at k=1024).
- Scaling every coupling — including `ε` — by `J` scales `C` by `√J`, `A` by `J`,
  and `X` by exactly `J^(−1/2)`, with the same `Q`. The telemetry's contraction
  law is preserved to machine precision.
- Same inputs and seed produce a bit-identical index.

### Solver

`A` is sparse and symmetric positive definite. A direct factorisation is applied to
all `k` right-hand sides in one batched triangular solve; measured ~11× faster than
per-column conjugate gradients (0.46 s against 5.07 s at n≈17k, k=128). Fill-in is
the risk, and a memory failure falls back to Jacobi-preconditioned CG rather than
aborting. **Build time is not yet monotone in corpus size** — see `RESULTS.md`.

---

## 3. Query fold-in

A query is a virtual node coupled to features with weights `w_f`. Its exact row is

```
(Σ_f w_f + ε) z_q = Σ_f w_f z_f + b_q
```

where `b_q` is the query's own sketch row. PROX drops `b_q`:

```
z_q = ( Σ_f w_f z_f ) / ( Σ_f w_f + ε )
```

The dropped term is isotropic and contributes the same expected amount to
`‖z_q − z_j‖²` for every item `j`, so it cancels in ranking. Verified against exact
resistance computed with the query as a genuine graph node: fold-in reaches
Spearman ρ = 0.97 and **matches a full re-solve at every dimension**, so the
residual gap is the JL dimension, not the approximation.

Cost is `O(|query features| · k)` plus the scan — sub-millisecond, with no solve.

---

## 4. On-disk format

A compressed `.npz` archive:

| Key | Type | Meaning |
|---|---|---|
| `X_items` | float32 `(n_items, k)` | item coordinates |
| `X_feats` | float32 `(n_feats, k)` | feature coordinates, for fold-in |
| `buckets` | int64 `(n_feats,)` | sorted hash buckets, binary-searched at query time |
| `idf` | float32 `(n_feats,)` | inverse document frequency |
| `ids` | object `(n_items,)` | caller-supplied identifiers |
| `meta` | JSON string | format, `dim`, `reach`, `couplings`, counts, seed, feature-space config |

`meta.format` is `"PROX/1"`.

**Size.** Item coordinates cost `k × 4` bytes each. Feature coordinates dominate a
small index and are the reason a 109-document index costs ~690 KB/document, but
vocabulary grows sublinearly with corpus size while items grow linearly, so
bytes-per-item falls steeply with scale (measured: 14.3 KB/item at 500 items,
8.0 KB/item at 2000).

---

## 5. Conformance

An implementation is PROX/1-conformant if, for the same inputs and seed, it
produces distances within 1% of the reference and satisfies:

1. zero triangle-inequality violations,
2. sketch error decreasing as `1/√k`,
3. uniform coupling scaling by `J` contracting all distances by `J^(−1/2)` to
   within 0.01%,
4. an empty result — never a fabricated ranking — when a query shares no feature
   with the index.

`demo/prox_console.html` is a second independent implementation in dependency-free
JavaScript; it reproduces criterion 3 at **0.000% error** in-browser.
