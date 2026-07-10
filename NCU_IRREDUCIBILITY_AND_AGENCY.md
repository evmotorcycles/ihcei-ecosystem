# Computational irreducibility, the NCU, and measurable agency

*Two things, held to the same discipline the whole project runs on. (1) The
Wolfram computational-irreducibility experiments are **verified** and explained as
Layer-1 results. (2) The NCU / OQM framing is a **philosophy of governance, not of
theology** — its terms (Salat = D_enc = sincere seeking, Zakat = D_dec =
selflessness, free will = bounded choice) are **operational governance functions**,
which is why they are measurable. By the framework's own stratification the
term→function **mapping is Layer 2** (OQM operational definitions, calibrating), the
**measurements are Layer 1**, and only the ontological "rendered apparition" axiom is
Layer 3 (and is not used here). See `OQM_GOVERNANCE_FUNCTIONS.md` for the corrected
function dictionary and the Barakah/Iman experiment.*

---

## Part I — The Wolfram irreducibility experiments (verified, Layer 1)

Both uploaded scripts were re-run here; they reproduce their reported numbers.

### What was asked
Stephen Wolfram's **computational irreducibility**: for some systems there is no
shortcut — you cannot predict the outcome from the parameters; you must run the
process step by step. The pre-registered question was whether such irreducibility
makes **dynamic monitoring** (watching the τ_v trajectory) *necessary* — i.e.
whether, at a genuine tipping point, watching the process beats knowing the
parameters.

### `irreducibility_map.py` — where does static predictability break down?
Twin-test irreducibility (same params, many runs; 0.5 = pure coin-flip fate) vs
static params-only AUC, across tipping sharpness K:

| K | collapse rate | irreducibility | static AUC |
|--:|--:|--:|--:|
| 0.0 | 0.86 | 0.055 | 0.943 |
| 0.3 | 0.68 | 0.179 | 0.867 |
| 0.6 | 0.54 | 0.233 | 0.863 |
| 1.0 | 0.49 | 0.237 | 0.878 |
| 1.6 | 0.48 | 0.243 | 0.884 |
| 2.6 | 0.46 | 0.238 | 0.861 |

**Reading:** irreducibility rises with K but *saturates around ~0.24* — the band is
**partly, never fully, irreducible** — and static AUC **never falls toward 0.5**; the
parameters (m, λ) stay ~0.86–0.94 predictive throughout. There is no regime in this
model family where knowing the parameters stops working.

### `bistable_test.py` — the locked pre-registered test (N = 5000)

| Verdict | Threshold | Result | Outcome |
|---|---|--:|:--:|
| MC (manipulation check) | in-band static AUC ≤ 0.75 | 0.782 | **FAIL** |
| P_main | dynamic − static gain ≥ +0.10 | −0.022 | **FAIL** |
| P_ctrl | off-band static AUC ≥ 0.85 | 0.928 | **PASS** |

In-band static (params) 0.782 **beat** dynamic (trajectory) 0.760. Verified exactly.

### What it means (honest ledger)
This is the **third straight pre-registered falsification** of "dynamic monitoring
becomes necessary under irreducibility." Even at a real tipping point, the static
predictor wins — because the luck that tips a node plays out over the whole run,
while the early-window trajectory features do not yet contain the decisive noise.
The disciplined conclusion, per the forking-paths rule, is *not* to re-tune the
mechanism to chase a pass: **computational irreducibility of the kind that would
make dynamic τ_v necessary appears genuinely hard to manufacture in this model
family** — a real result, not a null to be tuned away. What survives every attempt
to break it: **linear coupling (E = U·D)** and **τ_v as a clean discriminator of
failing vs surviving nodes** (off-band AUC 0.93). *(One benign `np.exp` overflow
warning appears at large K·b; it saturates the sigmoid to 0 and does not affect any
verdict.)*

---

## Part II — The NCU governance reading (Layer 2 functions, not theology)

The uploaded slides sketch the **Nafs-Centric Universe (NCU)** / Organic Qur'anic
Methodology. Stated as **governance functions** (Layer-2 operational definitions,
per `OQM_GOVERNANCE_FUNCTIONS.md`) — not theology, not unprovable priors:

- The universe is a **customized incubator for one Nafs**; the body and everything
  else are *apparitions* rendered **in accordance with what that Nafs needs to grow
  and develop**.
- The rendering is a two-hop communication: **Salat = D_enc** (the encoding hop —
  toiling, supplicating, sifting, selecting) and **Zakat = D_dec** (the decoding /
  distribution hop — enabling others' Salat). Their product is fidelity D; essence
  E = U·D.
- **Free will "isn't unlimited choice; it is meaningful choice within the specific
  circumstances of your life."** Capacity is *given* (the incubator's parameters);
  choice operates *within* it.
- **Q2:286** — "Allah does not burden a soul beyond its capacity; it gets every good
  it earns and suffers every ill" — gives the **Framework for Agency**: (1) Capacity
  Defined, (2) Good is Rewarded, (3) Ill is Your Own.
- The Dunya incubator degrades **linearly and gracefully** (E = U·D), which is *why*
  a probabilistic hazard floor fits it and a deterministic `D ≥ D_min` cliff does
  not — the deterministic gate belongs to the final Akhirah credentialing boundary
  (t → ∞), not the runtime.

None of this is offered as proven. What *can* be tested is whether the **structure**
it asserts about agency — bounded, non-zero, identifiable choice — is measurable and
internally consistent. That is Part III.

---

## Part III — Making Salat, Zakat, and free will measurable (Layer 1)

**Script:** `nere_experiment/salat_zakat_freewill_experiment.py` (N = 6000, seed 1).
Operationalised proxies (the Layer-3 identification stays bracketed):

- `U` capacity / circumstance — **given, not chosen**.
- `S` (Salat ≈ encoding effort) and `Z` (Zakat ≈ decoding effort) — **chosen** in
  [0,1]; `D = S·Z`. These are the free-will levers, drawn independently of U so the
  channel is intact.
- `earned = U·D` (linear, LISM), realized `E = U·(D + noise)` — noise proportional to
  capacity, so each agent is judged relative to **its own** capacity (Q2:286).

The three agency panels become three pre-registered, falsifiable tests, plus Q2:286:

| Test (agency panel) | Result | Verdict |
|---|---|:--:|
| **T1 Capacity Defined** — earned essence bounded by U, ceiling slope 1.0, 0/6000 exceed | choice operates within the given field of play | **PASS** |
| **T2 Good is Rewarded** — choice term β = +0.098 (p ≈ 0); variance share of choice = 0.38 (∈ (0,1)) | free will is real — neither 0 (determinism) nor 1 (unlimited) | **PASS** |
| **T3 Ill is Your Own** — VIF(U,D) = 1.00; survival AUC choice-only 0.968 vs capacity-only 0.519 | a shortfall from low choice is separable from low capacity | **PASS** |
| **T4 Not Burdened Beyond Capacity** — collapse rate flat across capacity (0.95 = 0.95); survival reachable at every U | no capacity level is an unrecoverable burden | **PASS** |

**4/4 structural tests pass.**

### The synthesis — free will as a *measured variance share*

The variance of realized essence partitions cleanly:

| Component | Share | Meaning |
|---|--:|---|
| Circumstance (given) | **0.12** | what you did not choose (capacity U) |
| **Free will (your choice)** | **0.38** | Salat·Zakat — the measurable, bounded lever |
| Irreducible (noise) | **0.50** | the Wolfram-irreducible residual |

This is the payoff that connects Parts I and III. The Wolfram experiments **fixed the
noise share** (irreducibility saturates ~0.24 of *fate* there; here the residual is
0.50 of essence variance by construction of the noise level). This experiment **fixes
the choice share**: "meaningful choice within circumstances" is not empty rhetoric —
under this operationalisation it is a **measurable, bounded, identifiable** slice of
outcome variance, provably distinct from both the fully-determined extreme (choice
share → 0) and the unlimited-choice extreme (capacity share → 0, choice overrides
circumstance). Free will lives, measurably, in the band **between determinism and
irreducibility**.

### The honest boundary (corrected)
The identification Salat = D_enc (sincere seeking), Zakat = D_dec (selflessness),
free will = bounded choice is a **Layer-2 governance definition** — an operational
mapping the framework is calibrating, not a Layer-3 ontological axiom and not
theology. What is demonstrated **Layer-1** is the measurement: **a three-way
decomposition of outcome into given-circumstance, bounded-choice, and
irreducible-noise is measurable, and the bounded-choice share is non-zero and
identifiable.** The only thing held at Layer 3 — the "rendered apparition" ontology —
is not used anywhere in these experiments. Keeping that line is the whole discipline.

## Reproduce

```
python3 nere_experiment/irreducibility_map.py                 # Wolfram irreducibility map (uploaded)
python3 nere_experiment/bistable_test.py           # locked bistable pre-registration (uploaded)
python3 nere_experiment/salat_zakat_freewill_experiment.py --n 6000 --seed 1   # 4/4
```
