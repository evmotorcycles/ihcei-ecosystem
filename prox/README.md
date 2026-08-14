# PROX — a proximity layer for everything

**PROX turns any collection into a true metric space, on the CPU you already own,
with no model, no training data, no network and no vendor.**

It came out of the LMD telemetry in `physics-agency/lmd/`, but not in the way that
programme intended, and the difference is the point.

---

## 1. What the telemetry actually showed

The published sweep contracts a ring lattice and reports a log-log slope of
`-0.500000` at `R² = 1.000000`. Reproduced here in `tests/test_core.py`, the
measured distance is

```
d(0, N/2) = sqrt( k(N-k)/N ) · J^(-1/2) = 5 · J^(-1/2)      for N=100, k=50
```

to six decimal places. The fit is perfect because **it is not a fit**. Effective
resistance on a graph scales as `1/J` by construction and distance is its square
root, so the exponent could not have come out as anything but `-1/2`. The
repository's own `physics-agency/lmd/RED_TEAM.md` concedes exactly this: *"on a
discrete simulated graph the result is algebraically guaranteed."*

As physics, that guarantee is why the simulation cannot settle whether spacetime is
emergent — only hardware can. As **engineering**, that same guarantee is the most
valuable property the result has, and nobody was using it.

A trained embedding model gives you an *opinion* about whether two things are
related. Resistance geometry gives you a **theorem**. Theorems do not need GPUs,
do not drift between model versions, and can be audited.

---

## 2. The problem

For a machine to know that two things are related — two files, a symptom and a
diagnosis, a farmer's question and an extension leaflet — the industry's answer is
an embedding model. That means GPUs, gigabytes of weights, training corpora chosen
by whoever paid for the run, a network round trip, per-token fees, and a vendor who
can change the model underneath you.

**Relevance became something you rent.**

The consequences are not evenly distributed:

- A $40 Android phone cannot semantically search its own contents.
- A clinic cannot relate its own patient records without shipping them to a
  datacentre in another jurisdiction.
- A collection in Luganda, Quechua or Khmer is served worst, because the
  vocabulary was fixed by a training run that barely saw those languages.
- Every application rebuilds relevance separately. Nothing shares a coordinate
  system, so your files, mail and photos live in three unrelated universes.
- You cannot ask *why* two things were judged similar. There is no triangle
  inequality in a learned embedding space, and no audit trail.

Before the GUI, using a computer meant knowing command syntax, so computing was
rented from people who had memorised it. The GUI did not make computers more
powerful; it made an existing capability **universally addressable at near-zero
marginal cost**. Relevance is at the same juncture now.

---

## 3. The solution

Any relation you can *count*, PROX turns into a *distance*.

Build a coupling graph — items on one side, hashed character n-grams on the other,
plus whatever relations the application already knows (a link, a shared folder, a
reply, a co-purchase). Then compute effective resistance across it. Two items pull
together when many short paths run between them, so association emerges from
counting alone, with no semantic model anywhere in the pipeline.

The obstacle is that the telemetry's method — a dense pseudo-inverse — is O(N³)
time and O(N²) memory. Fine at N=100; impossible for the million items on a phone.
PROX removes it with the Spielman–Srivastava resistance sketch:

```
R_ij = (e_i - e_j)ᵀ A⁻¹ (e_i - e_j),     A = L + εI = CᵀC
     = ‖ C A⁻¹ (e_i - e_j) ‖²
```

Resistance is a *squared Euclidean norm*, so a Johnson–Lindenstrauss projection `Q`
preserves every pairwise distance, and `Z = Q C A⁻¹` gives every item a coordinate
vector in `k` dimensions where **ordinary Euclidean distance is the LMD proper
distance**. Building it costs `k` sparse solves instead of one dense inverse.

Measured, in `tests/test_core.py`:

| Property | Result |
|---|---|
| Triangle inequality, exact resistance | **0 violations** |
| Triangle inequality, compressed index | **0 violations** (it *is* a Euclidean space) |
| Sketch error vs dimension | falls as **1/√k**, to <3% at k=1024 |
| Same input → same index | **bit-identical** |
| The `-1/2` contraction law through compression | **exact to machine precision** |

That last row matters more than it looks. Scaling every coupling by `J` scales the
whole sketch by exactly `J^(-1/2)` with the *same* projection — so the telemetry's
contraction law survives compression and becomes a **user-facing dial** with a known
meaning, not an opaque hyper-parameter. Turn up "who I talk to" and the space
contracts along that relation by a factor you can predict.

### The interface: a PUI

The GUI gave everyone coordinates on a screen. PROX gives everyone coordinates on
their own information — a **Proximity User Interface**. Not a search box that
returns a list, but a persistent sense of *near* and *far*: what is close to what
you are doing now, one dial per kind of closeness, the same coordinate system across
every app on the device.

---

## 4. What it does not do

Measured, not hedged. These are asserted in the test suite so they cannot be
quietly forgotten.

**PROX is not a replacement for keyword search.** On known-item retrieval over real
prose it loses badly — Recall@10 of **0.15 against BM25's 0.85**, and no
configuration we swept fixed it. Effective resistance integrates over *all* paths,
which makes it a smoothing operator; known-item retrieval needs a sharpening one.

**PROX has no world knowledge.** "Cat" and "feline" share no character n-gram. A
trained model knows they are synonyms because someone paid to show it a billion
sentences. PROX derives association strictly from the structure of the collection
it is given. Real collections contain that structure in abundance; eight unrelated
sentences do not, and PROX will not pretend otherwise.

**Long documents drift toward the centre.** Effective resistance is degree-biased,
so long items appear as neighbours more often. Measured not to overwhelm topical
structure across a 32× length range, but it is real.

**Scale is demonstrated at 10³–10⁴ items, not millions.** Queries are fast at every
size tested (0.61–1.06 ms) and bytes-per-item falls steeply with corpus size
(14.3 KB → 4.0 KB), but **build time is not yet monotone**: 29 s at 500 items, 10 s
at 2,000, 101 s at 8,000. Fill-in in the sparse factorisation depends on graph
structure rather than size, and neither solver wins everywhere — the direct path is
6.7× faster at 30k nodes and 1.7× slower at 60k. A phone-scale
index is a design target, not a result. Fixing it needs a Laplacian-specific solver
and is the most valuable open task here — the mathematics does not obstruct it, the
current solver is simply the wrong one.

### So the architecture is a router, not a blend

Term matching and resistance geometry are near-perfect complements, and blending
them destroys both — measured, reciprocal rank fusion scored **worse than either**
on its own strong task. The routing signal is free: does term matching have any
evidence at all?

| Task | BM25 | PROX | **Router** |
|---|---|---|---|
| Known-item retrieval, real prose (R@10) | 0.8532 | 0.1468 | **0.8532** |
| Association across a total vocabulary gap (R@10) | 0.1042 | 0.9062 | **0.9062** |
| — same task, MRR | 0.1129 | 1.0000 | **1.0000** |

In the second task the query and its targets share **zero** vocabulary by
construction; every BM25 score is exactly `0.000000`, so term matching cannot rank
at all and lands on chance (0.1042). PROX reaches MRR **0.975 across 60 queries**
where the only route to the answer is a two-hop path through bridging documents.

**PROX answers the queries lexical search must decline** — a synonym, another
language, "find me things like this", an empty query box. That is not a smaller
claim than replacing search. It is a different and larger one, because those
queries are currently answerable only by renting a GPU.

---

## 5. Try it

```bash
pip install numpy scipy
python3 -m prox.cli index ~/Documents -o home.prox.npz
python3 -m prox.cli find home.prox.npz "mtoto ana homa"
python3 -m prox.cli near home.prox.npz notes/clinic.txt
```

```python
import prox
ix = prox.build(texts, ids=names)
ix.search("consulta médica")     # no language configuration anywhere
ix.neighbors(42)                 # 'more like this', no query at all
```

Zero-install browser build: open `demo/prox_console.html`. It never contacts a
server; the whole engine is a few hundred lines of dependency-free JavaScript.
Published and runnable at
<https://claude.ai/code/artifact/d0a2e336-4165-4572-b42d-eeed51d07d7a>.

Reproduce every number in this document:

```bash
python3 -m pytest tests/ -q          # 20 tests, ~2s
python3 bench/eval_bridge.py         # the association result
python3 bench/eval_real.py           # the honest loss to BM25
python3 bench/eval_router.py         # best of both
python3 bench/bench_scale.py         # cost
```

See `SPEC.md` for the format and algorithm, `ECONOMICS.md` for how it earns,
and `RESULTS.md` for the full measured record.

---

*Apache-2.0. The engine is free forever and always will be — that is the strategy,
not a concession. See ECONOMICS.md.*
