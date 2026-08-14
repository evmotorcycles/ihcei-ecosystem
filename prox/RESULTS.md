# Measured results

Every number here was produced by the scripts in this directory on the machine
described below. Failures are reported at the same weight as successes; where a
claim is not demonstrated, it says so.

**Environment.** 4 CPU cores, 16 GB RAM, Linux, Python 3.11, numpy 2.4.6,
scipy 1.17.1. **No GPU, no network, no downloaded model.** JAX is not required.

---

## 1. What the source telemetry established

`tests/test_core.py::test_reproduces_the_ring_telemetry_closed_form`

The published sweep contracts a 100-node ring and reports slope `-0.500000`,
`R² = 1.000000`. Reproduced through the telemetry's own code path — a dense
pseudo-inverse of the ungrounded Laplacian — against the closed form
`d = sqrt(k(N−k)/N) · J^(−1/2)`:

| J | published d(0,50) | closed form | agreement |
|---|---|---|---|
| 0.1000 | 15.811416 | 15.811388 | 6 s.f. |
| 1.1788 | 4.605395 | 4.605277 | 5 s.f. |
| 100.0000 | 0.499995 | 0.500000 | 5 s.f. |

`R² = 1.000000` exactly because **this is an identity being evaluated, not a fit
succeeding**. Effective resistance scales as `1/J` by construction; distance is its
square root; the exponent could not have been anything but `−1/2`. The repository's
own `physics-agency/lmd/RED_TEAM.md` concedes the point.

That is a dead end for physics and the whole opportunity for engineering.

---

## 2. Guarantees that survive compression

`tests/test_core.py` — 8 tests, ~1.1 s.

| Property | Result |
|---|---|
| Triangle inequality, exact resistance (250 nodes, 2.6M triples) | **0 violations** |
| Triangle inequality, compressed index | **0 violations** |
| Identity, symmetry, separation | hold to 1e-12 |
| Determinism (same seed → same index) | **bit-identical** |
| Grounding bias as `reach → 0` | monotone, <1e-4 |

Zero violations in the compressed index is not luck. The sketch **is** a Euclidean
space, so the axioms hold for any `k`; approximation moves the values, never the
guarantees. This is the property no learned embedding has.

### Sketch accuracy follows the JL rate

Median relative error against exact resistance, 250-node random graph:

| dim k | 16 | 64 | 256 | 1024 |
|---|---|---|---|---|
| median error | 11.68% | 5.82% | 2.87% | 1.48% |
| p95 error | 33.4% | 17.1% | 8.3% | 4.3% |

Error halves as `k` quadruples — exactly `O(1/√k)`, as Johnson–Lindenstrauss
predicts.

### The contraction law survives compression exactly

Scaling every coupling (including the horizon term) by `J` scales `C` by `√J`, `A`
by `J`, and the sketch by exactly `J^(−1/2)` — with the *same* projection.
Measured over 15 couplings spanning three decades on a random graph:

```
slope = -0.500000000   (|error| < 1e-9)      R² = 1.000000000
```

The independent JavaScript implementation reproduces it in-browser at **0.000%
error** across J = 0.1 … 100. This is why coupling is a dial with a predictable
meaning rather than an opaque hyper-parameter.

---

## 3. Association across a total vocabulary gap

`bench/eval_bridge.py` — 12 queries × 5 seeds = 60 queries, dim=256.

Each topic owns two disjoint vocabularies sharing no words and no character
n-grams. Queries are drawn from vocabulary A; targets are documents written purely
in vocabulary B. The only route between them is a two-hop path through bridging
documents. Candidates are restricted to B-documents, because a topic's own A- and
bridge-documents legitimately outrank the targets and would make the measurement
meaningless.

| method | Recall@10 | MRR | nDCG@10 |
|---|---|---|---|
| chance | 0.1104 | 0.2030 | 0.0959 |
| BM25 | 0.1042 | 0.1129 | 0.0958 |
| **PROX** | **0.8875** | **0.9750** | **0.9038** |

**Max BM25 score over the entire candidate pool: `0.000000`.** The vocabulary gap
is total, so term matching cannot rank at all and lands on chance by construction,
not by misconfiguration.

PROX is 8× chance. Quality rises with dimension as theory requires — MRR 0.667 at
k=64, 1.000 at k=256 — confirming the effect is the geometry, not an artefact.

---

## 4. Where PROX loses, and by how much

`bench/eval_real.py` — 109 real markdown documents from this repository, 45,908
words. Known-item retrieval: first half of each document indexed, second half is
the query.

| method | Recall@10 | MRR | build | query |
|---|---|---|---|---|
| **BM25** | **0.8532** | **0.6208** | 0.02 s | 1.34 ms |
| PROX | 0.1468 | 0.0575 | 10.26 s | 2.08 ms |

**PROX loses by 5.8× on recall.** This is not a tuning failure. Swept across
`min_df` ∈ {1,3,5,10}, `dim` ∈ {256,1024,2048} and n-gram sets, Recall@10 never
exceeded 0.15:

| min_df | dim | features | R@10 |
|---|---|---|---|
| 1 | 256 | 73,855 | 0.1468 |
| 3 | 256 | 34,167 | 0.1009 |
| 5 | 1024 | 23,191 | 0.1193 |
| 3 | 2048 | 34,167 | 0.1284 |

The cause is structural: effective resistance integrates over **all** paths, making
it a smoothing operator, while known-item retrieval needs a sharpening one. No
amount of tuning converts one into the other.

### Blending makes it worse

Reciprocal rank fusion of the two rankings, measured on both tasks:

| task | BM25 | PROX | RRF blend |
|---|---|---|---|
| known-item (R@10) | 0.8532 | 0.1009 | 0.3394 |
| association (R@10) | 0.1042 | 0.9062 | 0.7812 |

**The blend is worse than the better method on both tasks.** Averaging a sharp
signal with a smooth one discards both.

### Routing recovers everything

`bench/eval_router.py`. The routing signal is free — does term matching produce any
evidence at all?

| task | BM25 | PROX | **router** |
|---|---|---|---|
| known-item, real prose (R@10) | 0.8532 | 0.1468 | **0.8532** |
| association, vocabulary gap (R@10) | 0.1042 | 0.9062 | **0.9062** |
| association (MRR) | 0.1129 | 1.0000 | **1.0000** |

The router chose BM25 109/109 times on prose and PROX 12/12 times on the gap task.
**PROX does not replace lexical search; it answers the queries lexical search must
decline.**

---

## 5. Other measured limits

**No world knowledge.** "Cat" and "feline" share no character n-gram. PROX derives
association strictly from structure present in the collection given to it; on
disjoint sentences there is none, and it does not manufacture any. Asserted in
`tests/test_index.py::test_prox_does_not_invent_world_knowledge`.

**Degree bias.** Effective resistance favours high-degree nodes, so long documents
drift toward the centre of the space and appear as neighbours more often. Measured
across a 32× length range, topical accuracy still held at 48/48; degree
normalisation was tested and changed nothing, so the bias is mild but real.

**Structure is a precondition.** On a corpus where topic structure is genuinely
present, same-topic nearest-neighbour accuracy was 8/8 and 48/48. On eight
unconnected sentences it is undefined, and the honest answer is that PROX is the
wrong tool.

---

## 6. Cost

`bench/bench_scale.py`, dim=128, min_df=3, Zipf-distributed synthetic corpora.

| items | features | build s | index MB | **bytes/item** | query ms |
|---|---|---|---|---|---|
| 500 | 13,097 | 29.06 | 7.2 | 14,342 | 0.61 |
| 2,000 | 28,522 | 10.03 | 16.1 | 8,042 | 0.78 |
| 8,000 | 52,423 | 101.14 | 31.8 | **3,972** | 1.06 |

**Query latency is the strong result**: sub-millisecond to single-digit
milliseconds, on a CPU, with no inference. Fold-in is `O(|query features| × k)`
with no solve.

**Bytes per item falls steeply**, 14.3 KB → 4.0 KB, exactly as Heaps' law predicts:
feature coordinates dominate a small index but vocabulary grows sublinearly while
items grow linearly. The asymptote is `dim × 4` = 512 B/item.

### The unresolved problem: build time is not monotone

29.1 s at 500 items, 10.0 s at 2,000, 101 s at 8,000. The cause is fill-in in the
sparse direct factorisation: hub features (common n-grams touching many documents)
make fill-in depend on graph *structure* rather than on size, and the 500-item
anomaly reproduced across runs, so it is not warm-up.

There is no single best solver. Measured head-to-head:

| nodes | direct (batched factorisation) | iterative (Jacobi CG) |
|---|---|---|
| 30,522 | **8.3 s** | 55.8 s |
| 60,423 | 167.0 s | **99.5 s** |

The ordering reverses between them, so `prox/core.py` now switches at 40,000 nodes.
That one-line change cut the 8,000-item build from **167 s to 101 s (1.65×)** with
no change to output. It relieves the symptom without curing it: the crossover was
found by measurement, not derived, and it will move with corpus shape.

**So the honest statement of scale is this.** PROX is demonstrated at 10³–10⁴
items, where it builds in seconds to minutes and queries in milliseconds. **The
"millions of items on a phone" figure is a design target, not a measured result.**
Reaching it needs a Laplacian-specific solver — algebraic multigrid or a
combinatorial preconditioner — which is the single most valuable open engineering
task in this repository. Nothing in the mathematics obstructs it; the current
solver simply is not the right one.

---

## 7. Reproducing

```bash
pip install numpy scipy pytest
python3 -m pytest tests/ -q        # 20 tests, ~2 s
python3 bench/eval_bridge.py       # §3
python3 bench/eval_real.py         # §4
python3 bench/eval_router.py       # §4
python3 bench/bench_scale.py       # §6  (slow: ~4 min)
open demo/prox_console.html        # §2, in-browser, no network
```

Verified in headless Chromium: the browser build indexes 15 multilingual documents
in **189 ms**, retrieves correctly in Swahili, Arabic, English and source code, and
reproduces the coupling law at 0.000% error, with zero console errors and zero
network requests.
