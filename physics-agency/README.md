# Telemetry Machines — F=ma / E=mc² as a two-hop control channel

`python3 physics-agency/telemetry_machines.py` demonstrates, as a Layer-1
control-systems simulation, how **telemetry turns an abstract physical invariant
into a functioning machine**. Newton's `F=ma` and Einstein's `E=mc²` are
*open-loop* invariants — they assume instantaneous, frictionless transmission. A
real machine that exploits them (a Watt steam engine, a fission reactor) only
produces useful, bounded work once you wrap the raw capacity in a **telemetry
feedback loop** `D = D_enc · D_dec`.

> **Labels:** *Salat / Zakat* are the **Nafs**-specific names for the two hops (a
> cognitive essence toils, then enables others). A physical machine is not a Nafs,
> so here the hops keep their engineering names **D_enc / D_dec**. Same maths.

| Hop | Steam engine | Nuclear reactor |
|---|---|---|
| **D_enc** (sense/encode) | Watt centrifugal governor | ionization chamber / neutron-flux sensor |
| **D_dec** (act/decode) | throttle valve | boron/cadmium control rods |
| **τ_v** (telemetry latency) | linkage lag | sensor→rod actuation delay |

## Results — 4/4 verified

**A. The two-hop delivery law** `E = U · D_enc · D_dec`
- **V1** delivered work fits `U·D_enc·D_dec` exactly — **R²=1.00** (linear in each hop, multiplicative across the two).
- **V2** either hop → 0 collapses output: full **1.00**, blind sensor (D_enc→0) **0.02**, jammed valve (D_dec→0) **0.01**. Both hops are required.
- **V3** decay is a graceful **linear** slide, not a quadratic cliff: `R²(E~D)=1.00` beats `R²(E~D²)=0.73`.

**B. Telemetry makes it a machine** (feedback latency τ_v)
- **Open-loop** (no governor) → **DIVERGES** — the raw invariant flies apart / melts down.
- **Closed loop, low τ_v** (0–2 steps) → **stable** — a functioning machine.
- **V4** past a **critical τ_v ≈ 4** the delayed loop re-destabilizes (the control-theory delay margin).

```
python3 physics-agency/telemetry_machines.py   # 4/4  (pytest: physics-agency/ 4/4)
```

**Reading.** Raw capacity `U` (steam pressure, fissile mass) is inert or explosive
on its own. Useful work `E = U · D_enc · D_dec` appears only through *both*
telemetry hops, scales linearly, and decays gracefully — and it is the
low-latency feedback loop (`τ_v`) that turns the abstract invariant into a bounded,
functioning machine. **Layer-1 control theory only**; the "physics is *literally* a
communication channel" reading stays an explicitly-labelled Layer-3 prior.

---

## Emergent spacetime — distance from information alone (indirect stepping-stone)

`python3 physics-agency/emergent_spacetime.py` builds a network defined **only**
by an information-coupling matrix `W` — no coordinates, no positions — and
reconstructs a genuine distance metric from it via effective resistance /
Doyle-Snell commute times: `dx_ij = √R_ij`, `R_ij = L⁺_ii + L⁺_jj − 2L⁺_ij`.

**Results — 3/3:**
- **S1** `dx` is a real **metric** emergent from pure information: `dx_ii=0`, symmetric, **0/8640 triangle-inequality violations** across random chains.
- **S2** distance is a **function of information coupling**: scale coupling by `c` and every distance contracts exactly as `dx ∝ 1/√c` — space stretches and shrinks with the information, it is not a fixed stage.
- **S3 (indirect proof)** two networks with **identical nodes and identical total coupling "energy"** but different *structure* render **different geometries** (mean dx 1.39 vs 0.98) — so the geometry is fixed by the **information**, not the substrate or the energy.

**Firewall.** Layer 1 (proven here): on an information network, spatial distance is
an emergent, reconstructable function of the transition structure — not
fundamental. Layer 3 (**not** claimed): that physical spacetime is likewise a
projection of an information substrate. This is the indirect stepping-stone the
Hoffman/Wolfram picture points at, never a proof of the metaphysics.

```
python3 physics-agency/emergent_spacetime.py   # 3/3
```

---

## The Telemetric Metric — a new, falsifiable physics equation

`python3 physics-agency/telemetric_metric.py` proposes an equation and a theory
built on the **same** commute-time telemetry, and numerically validates both the
equation and the *experiment that would decide whether spacetime is fundamental*.

**The equation (Telemetric Metric / latency line element):**

```
    d(i,j)² = κ · τ_rt(i,j)          τ_rt = C_ij / ν = R_ij
```

Two things are *close* when a signal can round-trip between them fast (low latency
/ high correlation) and *far* when the round-trip is slow. `τ_rt` is the round-trip
information latency — the same latency family as LISM's `τ_v`, reduced to the
effective resistance `R_ij` of the correlation network. **Distance is the geometry
of latency.**

**The theory — Latency–Metric Duality (LMD):** geometry is not a fundamental
container; the metric is emergent bookkeeping of round-trip information latency
between the underlying degrees of freedom.

**Numerical validation — 3/3:**
- **T1** `d=√(κ·τ_rt)` is a genuine metric (0/8640 triangle violations).
- **T2** the predicted scaling holds exactly: `d ∝ 1/√coupling`, log-log slope **−0.5000**, R²=1.00000.
- **T3 (the discriminator)** change *only* the information coupling of two **fixed** sites: the emergent distance moves (Δ=0.94) while a fundamental-container null stays frozen (Δ=0). *This is the measurement that decides.*

**The proposed physical experiment.** A **tunable-coupling qubit lattice**
(superconducting / trapped-ion) or an **entangled optical-clock network**: hold two
probe sites at fixed physical positions, sweep the entanglement/coupling between
them, and measure their operational "distance" via correlation round-trip time
(Lieb-Robinson / commute time). *Fundamental spacetime* forbids a fixed pair's
distance from changing when only their coupling changes; *LMD* requires
`d ∝ 1/√coupling`. The sign and scaling of the response decide it.

**Firewall.** This script is Layer-1 numerics validating the equation's consistency
and the experiment's discriminating logic. The physical experiment is **proposed,
not performed**; the Layer-3 claim (physical spacetime is emergent) is neither
claimed nor proven — it is exactly what the proposed experiment would test.

```
python3 physics-agency/telemetric_metric.py    # 3/3  (pytest: physics-agency/ 10/10 total)
```
