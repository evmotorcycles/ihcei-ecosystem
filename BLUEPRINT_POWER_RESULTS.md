# The four blueprint cohorts — Stage-1 power results

*The four prospective LISM cohorts (Clinical Governance, International Logistics,
Civil Aviation, Metascience) already pass the **structural** conformance test
(`blueprint_conformance.py`: channel-independent, non-circular, populated failing
region). This is the **statistical** test a Registered-Report reviewer asks next:
at the planned sample size, can each cohort actually distinguish a linear coupling
from a quadratic one — and will it falsely "find" curvature when the truth is
linear? Reproduce with `python3 blueprint_power_sim.py --reps 300 --seed 1`.*

---

## Method

For each cohort's planned (N, base failure rate), simulate a two-hop design with
**independent** hops (`D = D_enc · D_dec`, channel intact) and outcome
`logit P(fail) = a + b1·z(U·D) + b2·z(U·D²)` (predictors standardized). Fit the
nested pair `M1: E~z(U·D)` vs `M2: +z(U·D²)`, test the D² term (LRT, df = 1,
α = 0.05), and sweep the true quadratic effect `b2`:
`b2 = 0` gives the **Type-I** rate; `b2 > 0` gives **power**. `b1 = 0.6` throughout.

## Results

| Cohort | N | fail % | Type-I (b2=0) | power @ b2=0.45 | power @ b2=0.60 | MDES (80%) | linear-detect |
|---|--:|--:|--:|--:|--:|--:|--:|
| Clinical Governance | 2000 | 25% | 0.04 | 0.72 | 0.90 | **0.52** | 1.00 |
| International Logistics | 2000 | 20% | 0.04 | 0.72 | 0.89 | **0.52** | 1.00 |
| Civil Aviation | 1500 | 20% | 0.07 | 0.56 | 0.80 | **0.60** | 1.00 |
| Metascience (Reg. Reports) | 1000 | 20% | 0.05 | 0.41 | 0.66 | **0.79** | 1.00 |

*MDES = minimum detectable quadratic effect (log-odds per SD) at 80% power.
linear-detect = power to detect the linear coupling itself (existence test).*

## What it means

1. **No hallucinated curvature (Type-I control).** When the truth is linear
   (`b2 = 0`), every cohort's "quadratic found" rate sits at ~α (0.04–0.07). The
   nested LRT does not manufacture a squaring — the same discipline the methodology
   experiment demonstrated, now confirmed **at the planned N**. This is the guard
   that lets a *null on D²* be read as genuine support for linearity rather than
   low power.
2. **All four are strongly powered for the existence test.** Power to detect the
   linear coupling is **1.00** in every cohort — a real `E = U·D` signal will not be
   missed at these sample sizes.
3. **Curvature resolution differs by N — and that is the Stage-1 lock.**
   Clinical & Logistics (N = 2000) resolve the smallest curvature (MDES ≈ 0.52);
   Aviation (N = 1500) is adequate for moderate curvature (MDES ≈ 0.60);
   **Metascience (N = 1000) is the weakest (MDES ≈ 0.79)** — it can only
   distinguish a *large* quadratic effect. This is exactly the kind of honest limit
   a Registered Report must state up front.
4. **The pre-registration rule this implies.** For any cohort whose *hypothesized*
   curvature is below its MDES, the protocol must commit to a **larger N** before
   data — not reinterpret an underpowered null as confirmation of linearity post
   hoc. Metascience should either scale to N ≈ 1,600–2,000 or narrow its claim to
   "no *large* quadratic effect."

## Bottom line

The four blueprints are **structurally valid** (conformance test) *and*, at their
planned sizes, **statistically honest**: Type-I is controlled, the linear law is
fully powered, and the quadratic-discrimination limits are quantified per cohort.
These MDES values are the numbers to SHA-256–lock in each Stage-1 Registered
Report. Metascience is flagged for an N increase — surfaced by the simulation, not
by a reviewer.
