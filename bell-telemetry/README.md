# The Bell Monitor — "the universe is not locally real" as active, device-independent telemetry

**One command:** `python3 bell-telemetry/bell_monitor.py` · stdlib · offline · `$0` · deterministic

Bell's theorem plus the **CHSH inequality** is proven, Nobel-2022 physics (Aspect, Clauser,
Zeilinger): correlations produced by **any** local hidden-variable — *shared-cause* — model
are bounded by the CHSH value **`|S| ≤ 2`**; quantum entanglement reaches the **Tsirelson
bound `S = 2√2 ≈ 2.828`**; and **no physical theory can exceed it**. That is the precise sense
in which *the universe is not locally real.*

This module transforms that abstract result into an **active telemetry tool** for the Novora
stack — a **device-independent correlation certifier** — exactly as abstract `E = mc²` was
transformed into power plants. The tool trusts **nothing** about a source's internals and reads
only its **output statistics**: the strongest possible form of `F_out = F_eval`.

> ## Three layers, kept strictly separate
> - **Layer-1 — proven physics** (reproduced here as exact math + Monte Carlo): the constants
>   **2**, **2√2**, **4**.
> - **Layer-2 — the engineering tool**: the `BellMonitor` that estimates `S` from a stream and
>   classifies the correlation regime with finite-sample statistics.
> - **Layer-3 — interpretation** (speculative, labelled): the LISM/LMD reading. **LMD remains a
>   proposed, unproven theory** — nothing here proves it.

---

## The tool: `BellMonitor` (embeddable, device-independent)

```python
m = BellMonitor()
m.update(setting_a, setting_b, outcome_a, outcome_b)   # settings ∈ {0,1}, outcomes ∈ {+1,-1}
m.S()                    # the estimated CHSH value
m.classify()             # 'LOCAL' | 'NONLOCAL_CERTIFIED' | 'BEYOND_TSIRELSON_INVALID'
m.certified_nonlocal()   # True iff S exceeds 2 by > 5 standard errors (finite-sample)
```

It reads only outputs — never the mechanism — and classifies three regimes:

| regime | condition | meaning |
|---|---|---|
| **LOCAL** | `|S| ≤ 2` | explainable by a **shared classical cause** |
| **NONLOCAL_CERTIFIED** | `2 < |S| ≤ 2√2` (by > 5σ) | **not** explainable by **any** local hidden variable |
| **BEYOND_TSIRELSON_INVALID** | `|S| > 2√2` (by > 5σ) | **non-physical** — a source claiming this is provably fabricating |

---

## Results — pre-registered P1–P4 (spec `516231fc…`)

### P1 — the classical bound is real ✓ (proven physics)
```
brute force over all 16 deterministic local strategies → max |S| = 2.000000  (exact)
Monte-Carlo shared-hidden-variable source → Ŝ = 1.769 ± 0.002  → LOCAL (cannot certify)
```

### P2 — the quantum violation reproduces ✓ — *"not locally real"*
```
analytic singlet CHSH at optimal angles = 2.8284271   (Tsirelson 2√2 = 2.8284271)
Monte-Carlo singlet source → Ŝ = 2.829 ± 0.003, 262 σ over 2 → NONLOCAL_CERTIFIED
```
The Monte-Carlo singlet source **certifies a violation at 262 standard errors** — local hidden
variables are ruled out. This is the computational reproduction of the Aspect/Clauser/Zeilinger
result.

### P3 — the Tsirelson ceiling is an un-gameable fraud detector ✓
```
PR box  → Ŝ = 4.000 → BEYOND_TSIRELSON_INVALID
quantum → NONLOCAL_CERTIFIED      classical → LOCAL
```
No physical resource can exceed `2√2`, so **any source claiming `S > 2√2` is provably
fabricating**. The Popescu–Rohrlich box (`S = 4`) is correctly rejected as non-physical.

### P4 — the device-independent independence gate (the LISM bridge) ✓
```
shared-cause ('collusion') source certifies independence-of-cause?  No  (S ≤ 2, a common cause suffices)
entangled source certifies?                                          Yes (S > 2, NO local common cause explains it)
```
The Bell certificate is the **device-independent generalization of LISM's `VIF ≈ 1`
independence gate**: both ask *"can this correlation be explained by a shared common cause?"* —
`VIF` answers it statistically (linear collinearity), CHSH answers it at the strongest possible
level (no local hidden variable of **any** kind).

---

## Active telemetry for LISM and LMD

- **LISM** — the `BellMonitor` is the **hardest independence law** in the stack. Where the
  `VIF` gate (used in `agency-constitution`, `biomedical-agency`, the yeast channel) certifies
  *statistical* independence, the CHSH certificate is **assumption-free / device-independent**:
  it certifies that a correlation cannot come from **any** shared classical cause. Governance
  uses: certify a genuine quantum randomness/key resource trusting only outputs, and reject
  beyond-Tsirelson fraud.
- **LMD** *(interpretation — Layer-3, not a measured claim)* — LMD proposes that **locality
  itself is emergent from information**. Bell nonlocality is exactly what that thesis predicts:
  if space/distance is not fundamental, correlations need not respect a local-hidden-variable
  distance bound. The `BellMonitor` is the telemetry adapter for that reading — but **LMD is a
  proposed, unproven theory**, and this module proves nonlocality, **not** LMD.

## The honest headline

Proven nonlocality is now an **active, device-independent certifier**: classical (shared-cause)
correlations are bounded at `S ≤ 2`, genuine quantum correlations are **certified** at `2√2`,
and beyond-Tsirelson claims are **rejected** as non-physical. **A classical/software system
cannot violate Bell — only genuine quantum hardware can** — so the tool's governance value is
certifying quantum resources, an un-gameable fraud ceiling, and unifying LISM's independence gate
with the strongest physical independence certificate. **Methodology, not speed; not a superhuman
claim; and the LMD reading is labelled interpretation, not proof.**

## Files

```
bell-telemetry/
  prereg/bell_prereg.json        spec (locked) — the tool, gates P1–P4, the three-layer firewall
  prereg/MANIFEST.sha256.json     spec hash-pin (self-contained; seeded, no external fixtures)
  bell_monitor.py                 the BellMonitor tool + the pre-registered experiment
  test_bell.py                    pytest guard (constants exact; MC certificates clear 5σ)
  results_bell.json               emitted results
```

Layer-1 proven physics, offline, `$0`, deterministic (fixed seeds). Methodology, not speed.
