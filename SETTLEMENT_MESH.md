# The Reciprocal Settlement Mesh — built from scratch, then attacked

*Pre-registration `a5f49a6e…`, locked and committed before any implementation existed.
All terms are plain English by directive: the logic is kept, the vocabulary is not.*

```bash
bash reproduce_all.sh        # 70/70, clean checkout, offline, $0
```

**Result: 2 of 5 scored gates. The mesh lost where it matters most — and that is the
finding.**

---

## 1. Why build from scratch

You were right, and the referee report proved it: the legacy datasets are evidence of the
**contradiction**, not of risk-sharing. The cohort labelled "Risk-Sharing" contained only
cost-plus sale, lease and forward purchase — **zero** profit-and-loss partnerships. Mining
those files further can only reproduce size-bias and rigged comparisons.

So the architecture is specified from first principles and tested by methods that don't
require it to already exist.

## 2. First, a refusal

The JAX cell isn't a test:

```python
simulate_medina_mesh:   D_enc = D_dec = 0.95          # constant
simulate_firaun_node:   D = exp(-0.005 * U)           # the collapse IS this
                        tau = 4.8 + (U/120)**2.5      # the breach IS this
```

No data enters. The verdict is fixed by the two function bodies. This is the **fifth**
appearance of the tuned-baseline pattern, and gate **M7** now enforces structurally that
**no architecture-specific constant may differ between arms** — the exact gate that cell
would fail.

## 3. What can honestly be established before deployment

Not empirical support — that needs a deployed system. What *is* available:

| Method | What it yields |
|---|---|
| **Invariants** | theorems that hold under every admissible operation |
| **Adversarial attack** | the attacker wins or doesn't; the designer doesn't decide |
| **Shared-shock replay** | both arms, identical real inputs, no tuning |
| **Ablation** | which parts carry weight, and which are dead |

The shock source is **4,886 real recorded debits** from the committed banking dataset —
recorded history, replayed in order, identical for both arms.

## 4. What held

- **M1 — the full-reserve invariant.** 200,000 randomised operations (issue / net /
  settle) including deliberate over-issuance attempts: **zero** states where pledged
  exceeded reserves. A theorem about the mechanism, not an observation about the world.
- **M2 — all six attacks blocked**, zero false positives on 50 honest issuances:
  issue-without-reserve · double-pledge · forged attestation · collusion with *k*−1
  verifiers · self-reported reserves · cycling through intermediaries.

## 5. What failed — and these are real

### M3 — pooling beats the mesh at routine shock absorption

```
identical 4,886-shock sequence · identical parameters · no per-arm constants
  mesh failed settlements:  2,458
  centralised:                  0
```

A centralised balance sheet **holds every issuer's reserves** and can meet obligations no
individual node could. The mesh has no pool, and it **genuinely loses this contest**. This
is the single most important thing to know before building.

### M4 — contagion is worse, not better

2.95 counterparties impaired per node failure, against 0.00 centralised.

### M5 — the verifier quorum is dead weight

```
component removed        failed settlements    delta
multilateral_netting            2,493           +35   ✓ earns its place
verifier_quorum                 2,458            +0   ✗ DEAD WEIGHT
latency_covenant                2,551           +93   ✓ earns its place
```

Removing the quorum changes settlement outcomes by **exactly zero**, while costing **3.20
independent verifications per claim**. The full-reserve check at issuance already catches
everything the quorum was meant to catch. It is named, not quietly retained.

## 6. Three harness defects — found, fixed, disclosed

1. The cycle attack was a disjunction whose second term was an *honest, fully-backed*
   issuance by a different solvent node — it "succeeded" for reasons unrelated to the attack.
2. The contagion metric compared obligations to reserves **after** `settle()` had already
   written them down, returning 0.00 for both arms and measuring nothing.
3. The terminology scan was scanning the file that **defines** the banned-term list.

Fixing a broken measurement is not moving a threshold. **No fix converted a mechanism
failure into a pass** — M3, M4 and M5 failed before the fixes and fail after them.

## 7. The limitation the locked metric cannot see

Recorded as a **post-hoc, never as a gate**:

```
share of all obligations resting on ONE entity
  mesh      0.0086
  central   1.0000
```

M3 counts **routine** failed settlements, and pooling wins that contest. But **no locked
gate tests catastrophic centre failure** — the failure mode pooling creates. The mesh
appears to trade *frequent small failures* for *no single point of collapse*, and the
pre-registered metrics only measure the first half of that trade.

**That is not a result.** No test of it was pre-registered, so it is not claimed. Building
it is the named next step.

## 8. Honest status of the design

| Established | Not established |
|---|---|
| Reserve invariant holds under every operation tried | That it is legally permissible |
| Six named attacks blocked, no false positives | That it is economically viable or liquid |
| Netting and the latency covenant carry weight | That it beats existing institutions |
| The quorum does not, and costs 3.2 verifications/claim | **Anything at all about the world** |

No such system has been deployed. Simulating a design is not evidence about reality, and
this document does not claim otherwise.

**What the evidence says right now: a peer-to-peer mesh without pooling absorbs routine
shocks worse than a central balance sheet.** If the design is to proceed, that is the
problem to solve — and the honest next step is the catastrophic-failure test that would
show whether the trade is worth making.

---

*Reproduce: `bash reproduce_all.sh` → **69/69**. Pre-registration `a5f49a6e` committed
before the implementation. `exit 0` means "reproduces including its failures", never
"the mesh works".*
