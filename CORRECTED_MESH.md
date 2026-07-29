# The surgical correction — built from the telemetry, and what it cost

**Spec** `dca3694c5610c5225ef23e4ad26041be3fc831e80bd0fe6eb98bd791acfe0fb3` · locked before
implementation · **3/6** · `python3 -m pytest -q corrected-mesh/test_corrected.py`

The instruction was right: don't burn down the infrastructure, isolate the failure points
and correct only those. So the telemetry — not the doctrine — decided what to keep.

| | Decision | Evidence |
|---|---|---|
| **KEEP** | balance-sheet pooling | a central book at `ΔU = 0.0` cleared every routine debit with **zero** settlement failures (`bf5a27f0` C1) |
| **CUT** | fractional credit creation | leverage made settlement monotonically **worse**: m=1 → 0, m=3 → 3,262, m=5 → 3,912, m=10 → 4,362 (`bf5a27f0` C2) |
| **CUT** | the single point | tested below, F5 |
| **CUT** | deferred consequence | the latency covenant, tested below, F6 |
| **ADD** | participation notes | the untested piece — **this is what the run was for** |

---

## A bias in every previous run, corrected here

Every experiment in this programme so far replayed only the **4,886 Debit rows**. The
committed dataset also holds **5,114 Credit rows**.

A downside-only sequence structurally **cannot** show an upside-sharing mechanism. Every
previous test of risk-sharing was therefore biased *against* it. This run replays both —
**10,000 events in recorded order, identically in every arm**. Declared before any result
was seen, and it makes the test fairer to the proposal, not harsher.

## The trap the spec named in advance

A fixed obligation that cannot be paid is a **settlement failure**. A participation claim
that cannot be paid is written down and recorded as **nothing**.

Scoring equity on failure *counts* would hand it a near-perfect result by construction —
a test that cannot fail. So every primary gate is scored on

```
CLAIMANT VALUE SHORTFALL  =  value promised  −  value delivered
```

defined identically for a debt claim and an equity claim, and not improvable by
relabelling.

---

## The headline result, and why it must not be banked

```
claimant value shortfall
  corrected (equity, k=2)      94.4      primary 156   secondary 121
  fixed debt (k=2)          2,465.0      primary 224   secondary 190
  central full-reserve book 2,184.4      primary   0   secondary   0
```

A **96.2% reduction**, and the corrected arm beating the central book by 23×. Those
numbers are too good, and the too-perfect rule says to look for the mechanism before
celebrating.

The equity arm also distributed **50% of every credit inflow** to holders. That is
**prepayment**, and a debt issuer can do it too. Holding the distribution policy fixed:

| | prepay ON | prepay OFF |
|---|---|---|
| **equity** | 94.4 | 4,059.3 |
| **fixed debt** | **16.1** | **2,465.0** |

**In both columns equity is worse than debt.** The entire gain belongs to the discipline of
distributing inflows continuously, which is orthogonal to whether a claim is fixed or
variable.

**The mechanism is legible.** Writing a claim down **extinguishes** it — the holder can
never be made whole from later inflows. A residual debt survives and stays recoverable.
Loss absorption is not free; it forecloses recovery.

The same applies to F4: the central comparator was not given prepayment. Granted the same
discipline it scores **1,105.7** and is **ahead** of the corrected arm. That gate compares
distribution policies, not topologies.

**No threshold was moved and no gate was re-scored.** F2 and F4 pass as written; the
confounds are recorded in the source, the results JSON and the tests.

---

## What survived the control — the real finding

**F3 holds in both columns.**

```
secondary (knock-on) failures
  prepay ON     equity 121  vs  debt 148     18.2% fewer
  prepay OFF    equity 129  vs  debt 190     32.1% fewer
```

**Participation is a contagion control, not a loss reducer.** Absorbing a loss without
triggering a hard default event genuinely stops it propagating — it does not make the loss
smaller. The pre-registration named this exact outcome in advance as the interesting one:

> *"If F3 passes while F2 fails, the finding is that equity is a CONTAGION control, not a
> loss reducer — which would be a precise and useful result."*

Note the honest qualifier: the effect **weakens to 18.2% once prepayment is present**,
below this gate's own 30% bar. Participation and prepayment partly substitute for each
other.

---

## What failed

### F5 — the 1/K quarantine claim is refuted

The proposal states single-point dependency drops to `1/K ≈ 0.0100` and failure is
"strictly quarantined within that cluster."

- **Arithmetic:** at n=200 and k=20 there are **10 clusters**, so `1/K = 0.10`, not 0.0100.
  The quoted figure conflates cluster *count* with cluster *size*.
- **Measurement:** the fraction of the network whose delivered value is impaired is
  **0.9350** — **9.3× the claimed quarantine**.

Damage is not confined to a cluster. This is the third independent refutation of the
quarantine claim, after the flat sub-mesh curve and the tail-risk run.

### F6 — participation is worse than dead weight

Ablation, with prepayment held **ON** so it isolates participation itself:

| Remove | Δ claimant shortfall | |
|---|---|---|
| full reserve | **+8,093.1** | earns its place by a wide margin |
| equity participation | **−78.3** | **removing it IMPROVED the outcome** |
| local pooling | +191.6 | earns its place |
| latency covenant | +125.9 | earns its place |

Three of the four components are justified. The fourth — the architecture's headline
innovation — is worse than dead weight on this metric.

### F1 — the invariant, and an honest failure

The **corrected arm holds full reserve exactly**: 0 violations, unbacked claims 0.0. The
**fixed-debt comparator** violates it 11 times, because after a shortfall its residual
claim survives with no reserve behind it — which is what an unbacked debt *is*.

The gate says "in every arm," so it **fails as written**. The reason is a property of debt,
not a bug in the build, and the gate was not rewritten to say otherwise.

---

## The design the six runs now support

Not the one the proposal specified.

| Component | Verdict |
|---|---|
| Full reserve | **strongly supported** — largest single effect measured (+8,093.1) |
| Balance-sheet pooling | **supported** — the telemetry vindicated it and it is kept |
| Continuous distribution of inflows | **supported, and it is the sleeper** — the single largest driver of the headline, and it was not in the proposal as a named component |
| Latency covenant | **supported** (+125.9) |
| Local k-neighbour pools | **supported but small** (+191.6); k=2 captures it, k≥5 adds nothing |
| Participation / loss-sharing | **for loss reduction: worse than dead weight.** For contagion control: **genuine**, 18–32% fewer knock-on failures |
| 1/K quarantine | **refuted**, 0.9350 measured against 0.10 claimed |

**The actionable reading.** If you want less value lost by claimants, mandate continuous
distribution of inflows and hold full reserve. If you want less *contagion*, use
participation. These are different objectives and the same instrument does not serve both —
adopting participation to reduce losses makes losses worse.

## Anti-immunisation

The F2/F4 confound and the F6 result may **not** be rescued by asserting that
participation's benefit is qualitative, that the event sequence is unrepresentative, or
that the real world differs. The spec forbade those moves before the run. Equally, the F3
pass must not be widened from "contagion control" into "risk-sharing works" — the spec
forbade that too.

## Reproduce

```bash
python3 corrected-mesh/corrected.py
python3 -m pytest -q corrected-mesh/test_corrected.py
bash reproduce_all.sh
```

Exit 0 means "reproduces including its failures", never "the corrected architecture works".
