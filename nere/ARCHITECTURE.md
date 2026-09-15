# NERE — architecture and ingestion protocol

v1.0.0. Predictions locked in `prereg_nere.md`, sha256
`81a0c16b22a81c9d89df8c3153d9cfacc98e7ec5889a292b90f124828b45248c`.

**Infrastructure, not a product.** Per `LAYERS.md`, NERE has no interface and an
ordinary person should never encounter the name. `test_layers.py` fails if a page
appears presenting it as a tool someone operates, and `test_nere_ships_no_interface`
fails if any markup lands in this directory.

---

## What this is

A path from a hand-drawn, provenance-tagged argument graph to the three
structural readouts this repository already computes. It separates **drawing a
claim** from **reading its structure**, so that the reading can be wrong about
the drawing without being wrong about itself.

## What this is not, in the same size type

- **It does not read documents.** No language model runs here. Nothing is parsed
  and no edge is ever found. `DependencyTracingExtractor` is a **validator** with
  a name inherited from the specification it implements, and that name overstates
  it. Every part and link is supplied by whoever draws the graph.
- **The semantic layer abstains.** There is no benchmarked latent-energy model in
  this repository, so the effective path is **extractor → LMD**. `JEPASemanticFilter`
  scores nothing, admits nothing and rejects nothing, and no number leaves it.
- **It does not say whether a claim is true.** Layer 1 and Layer 3 describe where
  a chain came from. A Layer-1 claim can be false; a Layer-3 claim can be correct.
- **It measures nothing itself.** `spar`, `fathom` and `smi` do the measuring and
  carry their own suites. This is a wrapper.
- **It cannot tell whether a provenance tag is honest.** Whether an edge marked
  `literal` really is stated in the document is written by the drawer, and no test
  here can check it.

---

## The three paradigms

They audit different things. They do not compete, and **they are not all present**.

| Layer | Architecture | Space | Objective | Status here |
|---|---|---|---|---|
| Symbolic | LLM | discrete tokens | cross-entropy `P(x_t+1 \| x_1..t)` | **Not in this module.** A person draws the graph. |
| Semantic | JEPA | continuous latent | energy `F(x,y)` | **Seam only. Abstains on every call.** |
| Structural | LMD | graph Laplacian | spectral, `L⁺` | **Present.** Parameter-free: no training, no loss, no weights. |

The structural layer is the only one that runs. That is worth stating plainly,
because a three-row table invites the reading that three things are working.

---

## The pipeline

### 1. Validation — the airlock that refuses

Every **part** names a type (`evidence`, `method`, `conclusion`). Every **link**
names a `provenance` and a `where`. There are no defaults: an untagged link is
**refused**, because assuming `literal` would let an inferred step read as a
stated one.

| Provenance | Meaning |
|---|---|
| `literal` | the document states this link in so many words |
| `interpretive` | the reader inferred it from the document |
| `imported` | the reader brought it from outside the document |

A drawing with parts but no links raises — that is an empty result, not a zero.

### 2. The semantic seam — ABSTAIN as a value

```python
def evaluate_edges(self, g) -> SemanticVerdict:
    return SemanticVerdict.abstain("no benchmarked JEPA model in repo")
```

`ABSTAIN` is a value the firewall **consumes**, not an exception it swallows. The
type refuses to carry an energy while abstaining, so a later edit cannot quietly
fill the box. Every run prints `semantic layer: ABSTAIN (no benchmarked model)`,
and the pipeline **raises** if the seam ever starts scoring without the contract
being updated with it.

### 3. Structural telemetry — three readouts, never fused

`mesh_metric` walks the adjacency rather than asking `pinv` whether a path exists,
so an unreachable pair returns **no reading at all** instead of a small confident
number.

| Readout | From | What it answers |
|---|---|---|
| Total bearing | `spar.bearings` | conserved at parts − pieces, exactly (Foster) |
| Cut parts | `spar.single_points` | which single parts break the drawing |
| Deepest dependence | `fathom.sound` | what the conclusion rests on hardest |
| Effective resistance | `smi.mesh_metric` | latency from evidence to conclusion |

### 4. The firewall

**The layering rule is categorical, not a tuned fraction:** Layer 1 requires
**every** edge on the chain to be `literal`. One inferred edge means the reader
supplied part of the chain, so the claim is not lexical. The sensor is the
provenance tag; there is no threshold to choose.

**No Provenance Fragility Index is registered.** A 30%-of-edges downgrade was
proposed. It gates nothing here: it has no stated reason and no sensor beyond the
ratio itself, and `FLOOR_RETIREMENT.md` records a gate retired at p = 0.735 for
exactly that failure. The ratio **is reported**, beside the layer it does not
decide. `test_the_thirty_percent_gate_was_not_added` proves this behaviourally —
a drawing at ratio 0.1, below any such gate, still reads Layer 3.

---

## The one declared fusion

Everything else stays orthogonal. **One rule combines two readouts, by explicit
decision, and is labelled a fusion in its own output.**

The **padding tripwire** fires when, in the same comparison, the cut count
**falls** and the deepest dependence **rises**.

*Reason:* neither half is evidence alone. Cuts fall whenever anyone adds a link,
honestly included. Dependence rises for many reasons. Clearing a bottleneck while
the argument comes to rest **harder** on one thing is the signature of declaring
links rather than finding them.

It emits a named boolean with both source readouts beside it, produces **no
number**, and **changes no layer**.

---

## Measured: two drawings of one document

The uploaded study has a locked reading in `order-invariance/prereg_order.md`
(sha `9c9872e4…`): three passages route through **one** declared method. A second
drawing separates the metaphor from the method. Both are defensible; they are
**not** corrections of each other.

| | locked, 5 parts | alternative, 6 parts |
|---|---|---|
| Total bearing / expected | 4.0000 / 4.0 | 5.0000 / 5.0 |
| Cut parts | the method | the metaphor **and** the method |
| R_eff evidence → conclusion | 2.0 | 3.0 |
| Layer | 3 (motivating) | 3 (motivating) |

**The drawing dictates the telemetry.** `NULL-N2` of the locked file already said
so — *"a correct reading of a wrong picture"* — and this is that case, measured.
Nothing in this module can say which drawing is right.

## Measured: the padding attack

Four added edges on the 6-part drawing. No new parts, no new evidence, nothing
removed — the adversary only **declares more links** between things already there.

| Readout | before | after | |
|---|---|---|---|
| Cut parts | 2 | **0** | **gamed** |
| Total bearing | 5.0000 | 5.0000 | **immune**, by parts − pieces |
| Deepest dependence | 0.066667 | **0.449275** | **moved against the attacker** |

**The attack defeats one readout of three.** That is the case for not fusing them,
measured rather than asserted — and it is why the tripwire is a conjunction.

---

## Repository constraints

- **No fused scores** except the one declared above, which labels itself.
- **float64 enforced.** `smi/lmd.py:60` sets `jax_enable_x64=True`. At float32 the
  n=100 ring reads −0.500003 and noise arrives as signal.
- **Assemble the Laplacian as `diag(W.sum(1)) − W`**, not by accumulating into the
  diagonal edge by edge. `lmd-scaling/RESULTS.md` measures a case where assembly
  order alone flips a published PASS to FAIL at n=100.
- **Identity, not result.** A global scalar sweep `L = J·L₀` giving a −0.5 slope is
  an algebraic identity of the pseudo-inverse. `smi/PREREG.md` says so first.

## A caution this module cannot remove

Most predictions in `prereg_nere.md` are **specification, not discovery**: E4–E10
describe code written in the same commit to satisfy them, and E1–E3 and E13 are
fixed by Foster's theorem. **Only E14 could have gone either way.** A suite that
passes because it tests its own specification has shown that the code does what it
says — not that what it says is worth doing.

## Reproduce

```
python3 nere/run_nere.py
python3 -m pytest nere/test_nere.py -q
```
