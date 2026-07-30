# Three proposals for Islamic banking, put on the same engine

**Spec** `0b2328c54836ec5281c54e4c1ff0afdb6a779172a51975ed5703d020a13c6402` · locked before
implementation · **4/5** · `python3 -m pytest -q three-proposals/test_three.py`

Three named positions disagree about what Islamic banking should be. The disagreement is
usually conducted in jurisprudence. Here it is conducted in **settlement outcomes**, on one
engine, with one committed 10,000-event sequence, and one metric applied identically to
every arm.

---

## 1. The arms

| Arm | Position | Mechanics as implemented |
|---|---|---|
| `irfan` | Abandon fractional-reserve banking; full-reserve participation notes | 100% full reserve; every claim absorbs loss proportionally and **extinguishes**, no default event |
| `alqudah_m3` | Work within real regulatory constraints using asset-backed contracts and diminishing co-ownership | Claims amortise on schedule; the institution's ownership share absorbs a **proportion** of loss, remainder survives — on the **fractional substrate** the position accepts as reality |
| `alqudah_m1` | **required control** | The *same contracts* at full reserve — separates the contract design from the substrate |
| `tworegister` | Ours | Full reserve, fixed 25/75 containment/recovery mix, **no routing model** (routing was refuted at `ed80430a`) |

## 2. The design decision that made this a fair test

Continuous distribution of inflows measured **+194.5** in the previous run — two orders of
magnitude above any structural component, and **larger than anything the three positions
dispute**. It is a named part of *our* proposal and not of the other two.

Handing it to our arm alone would have guaranteed our arm wins, on a mechanism the
doctrinal argument is not even about. So it was made an **independent factor**: every arm
runs both ways, and the architecture gates are scored with it **off everywhere**. Declared
in the spec before any result was seen.

## 3. Results

```
distribution OFF          shortfall   secondary   unbacked
  irfan                      4103.2         135        0.0
  alqudah_m3                 6621.6         616     1585.9
  alqudah_m1                 3321.2         166        0.0
  tworegister                2983.7         177        0.0

distribution ON
  irfan                       128.3         123        0.0
  alqudah_m3                  237.0         672      930.6
  alqudah_m1                   88.5         142        0.0
  tworegister                  96.7         151        0.0
```

### B4 failed — and it is the finding

```
spread between best and worst arm, on shortfall
  distribution OFF     3637.8
  distribution ON       148.5      →  4.1% retained
```

**A payment-timing rule that none of the three positions argues about dominates the dispute
between them.** Switch on continuous distribution and 96% of the three-way difference
disappears. The spec predicted this failure in writing and made it the primary gate for
exactly this reason.

This is uncomfortable for all three positions. It is *most* uncomfortable for ours, because
we are the ones who named the mechanism and still framed the architecture as the headline.

### And our own arm loses once distribution is on

With distribution enabled, **`alqudah_m1` scores 88.5 against our 96.7**. Our B2 win exists
only in the distribution-off comparison, and it is modest there too — 2,983.7 against the
same contracts at full reserve on 3,321.2. Reported, not omitted.

### What passed

- **B1 — the substrate difference is real, not nominal.** The fractional arm carries
  **1,585.9** of unbacked claims; all three full-reserve arms carry exactly **0.0**.
- **B3 — full extinguishment stops cascade best, on someone else's architecture.** Irfan's
  all-participation arm records the **fewest** secondary failures (135). The
  contagion-control finding from our earlier run **generalises beyond our own design** —
  which is the first time it has been tested outside it.
- **B5 — the practitioner critique is correct on measurement.** Identical contracts score
  **6,621.6 at m=3 against 3,321.2 at m=1** — a **1.99×** penalty attributable to the
  substrate alone, with contract design held fixed. **The label was never the problem. The
  substrate was.**

## 4. What each position gets right, on measurement

| | Vindicated | Corrected |
|---|---|---|
| **Irfan** | The substrate critique (B5, 1.99×) and full extinguishment as the best cascade control (B3) | All-participation is **not** the best on claimant shortfall — 4,103.2 against 3,321.2 for co-ownership at full reserve. Extinguishing forecloses recovery. |
| **Al-Qudah** | The contract design is sound — **at full reserve it wins outright** once distribution is on (88.5, best of all four) | The constraint being accepted is the expensive part. The same contracts cost **2× more** on the fractional substrate. Necessity is real, but it is not free, and now it has a number. |
| **Two-Register** | Best on shortfall with distribution off | Wins narrowly, and **loses once distribution is on**. The register split is worth far less than the payment-timing rule we found by accident. |

## 5. What this cannot settle

**Nothing here adjudicates a jurisprudential question.** An arm scoring better on settlement
outcomes is not thereby permissible; an arm scoring worse is not thereby impermissible. The
spec says this and it is repeated here because the temptation to convert a settlement result
into a ruling is exactly the error the layer discipline exists to prevent.

What the test measures is what these architectures **do** under a recorded event sequence.
That is a real and useful thing to know, and it is all that is on offer.

---

## 6. The 2:275 / 2:276 reading

Run under `.claude/skills/oqm-methodology`. **Everything in this section is `[L2]`** — a
reading, derived by a stated method. None of it is evidence, and the numbers above do not
become scriptural support by being placed next to it.

### The lexicon, fixed before use

Per the lexicon rule (103:3, *"toiled in accordance with the proper lexicon"*), each term
gets one operational sense held constant:

| Term | Operational sense used throughout |
|---|---|
| **ribā** | capacity inflation without matching fidelity work: `ΔU > 0` while `D → 0` |
| **al-bay'** | an exchange whose value passes through as it is realised |
| **ṣadaqah** | outward pass-through that keeps a counterparty solvent |
| **yamḥaq** | progressive erasure of a stock |
| **yurbī** | compounding growth of a flow |

### The pressing

**As-Ṣidq** (the surface report): 2:275 contrasts two categories of transaction and forbids
one. **Al-Ḥaqq** (the operational layer): the two categories differ in *when value moves*.

- A **fixed unbacked claim** takes its return on a schedule detached from whether the
  underlying produced anything. Value is warehoused and extracted on a date.
- An **exchange** moves value **as it is realised**.

That is not a moral distinction in the pressing — it is a **timing** distinction, and timing
is the thing this programme measured at +194.5.

### Where the alignment is real, and where it stops

The reading and the measurement agree on one specific point, and it is worth stating
precisely because the temptation is to claim more:

> **2:276 sets a stock against a flow.** *Yamḥaq* acts on a stock — something accumulated
> gets erased. *Yurbī* acts on a flow — something passing through compounds. The measured
> result has the same shape: **warehousing inflows and paying on a schedule was the single
> most destructive configuration tested; passing them through as they arrived was the single
> most protective.**

**This is a structural correspondence, not a proof.** The measurement did not test a
scriptural claim and could not have. What it did was find, independently, that the
stock/flow distinction is where the largest effect in the system lives — and that is worth
saying out loud without inflating it.

### Why current practice sits badly with this reading

Not because of the labels. **Because of the substrate — and now that has a number.**

The synthetic-debt wrapper reproduces exactly the configuration the pressing identifies:
value taken on a schedule rather than as realised, on a substrate carrying **1,585.9** of
unbacked claims. Changing the contract's name while keeping both features changes the
As-Ṣidq and leaves the Al-Ḥaqq untouched — which is precisely the failure mode the pressing
protocol exists to detect, and precisely what B5 measured at **1.99×**.

**And the reading cuts against us too.** If the operative distinction is stock-versus-flow,
then our two-register split is a **second-order** refinement of something the reading
already had, and B4 says so: 4.1% retained. The reading was ahead of our architecture, and
our architecture spent its effort in the wrong place.

### The audit boundary

`ṣadaqah` is read here as outward pass-through. That is defensible within the root's
attested field. It is **not** a derivation that the measured 18–32% cascade reduction is
what the term denotes — the number came from a settlement engine, the term came from a
lexicon, and the fact that they point the same way is a **correspondence a reader may find
suggestive and must not treat as support.**

---

## Reproduce

```bash
python3 three-proposals/three.py
python3 -m pytest -q three-proposals/test_three.py
bash reproduce_all.sh
```

Exit 0 means "reproduces including its failures", never "one of these proposals is correct".
