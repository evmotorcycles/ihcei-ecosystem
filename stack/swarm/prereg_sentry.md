# Pre-registration — LISM serial-fidelity sentry (P10, P11, P12)

Written and hashed **before `stack/swarm/lism_sentry.py` existed**. The hash is
asserted in `stack/swarm/test_sentry.py`. Nothing below was run first.

This registers predictions about **synthetic graphs only**. It registers nothing
about the July 2026 agent-swarm incident, whose per-hop payloads are not
obtainable — see `DOOR2_STATUS.md`. P24, P25 and P26 remain unwritten and are
not in this file.

---

## The quantity

A handoff chain carries a payload through hops `k = 1..n`. Each hop has a
retention `D_k ∈ (0, 1]`. The quantity carried after the chain is

    E = U · ∏_k D_k

`U` is the quantity entering the chain. **This is a fidelity product and nothing
else.** It is not an energy, not a heat, not a disorder measure, and borrows no
vocabulary from physics; the module is grepped for that vocabulary and must
contain none of it.

### The floor is a ratio of `U`, and this is the registered design choice

`min_ratio` is a **required argument with no default**, expressed as a fraction
of `U`. An absolute floor `min_E` would make the verdict depend on how much
entered the chain, which is a defect and not a feature. The module carries the
absolute form as well, **solely so the defect can be measured**, and nothing
shipped calls it. This is the same arrangement as `leaky_dissonance()` in
`stack/organization/adg_cfe.py`.

### Route semantics, declared before measuring

A graph with more than one route from source to sink has more than one product.
The module returns **both extremes and never fuses them**:

- `ratio_best` — the highest-fidelity simple route. This is the reading an
  attacker gets, because an attacker picks its route.
- `ratio_worst` — the lowest-fidelity simple route.

Returning only one would be a choice smuggled in as an implementation detail.

---

## P10 — the floor form changes the verdict; the product itself does not

**P10a is an IDENTITY, NOT A RESULT.** `E/U = ∏_k D_k` is the definition with
`U` divided out. That the ratio is invariant to `U`, and invariant to the order
of the hops, follows from multiplication being commutative and has no empirical
content. It ships as a harness self-check, exactly as Foster's theorem does in
`stack/audit/`, and is never reported as a finding.

**P10b is the prediction that earns its keep.** On a 6-agent chain with 5 hops
at `D = 0.9`:

| claim | predicted |
|---|---|
| `E/U` after 5 hops | `0.59049` exactly |
| running ratios, hops 1–5 | `0.9, 0.81, 0.729, 0.6561, 0.59049` |
| ratio-form trip depth at `min_ratio = 0.6`, `U = 1.0` | **5** |
| ratio-form trip depth at `min_ratio = 0.6`, `U = 1000.0` | **5** — unchanged |
| absolute-form trip depth at `min_E = 0.6`, `U = 1.0` | **5** |
| absolute-form trip depth at `min_E = 0.6`, `U = 1000.0` | **71** |

The two forms agree at `U = 1` and diverge by a factor of 14 in depth at
`U = 1000`. If they do not diverge, the argument for the ratio form is wrong and
the module should carry the absolute form instead.

---

## P11 — padding: one form defeats the sentry, the other does not

`stack/audit/` measured that declared padding defeats both structural sensors it
was tested against: cut vertices fell `3 → 0` and maximum load fell
`0.5714 → 0.3088`, both in the attacker's favour, and only deepest dependence
rose. **The registered question is whether serial fidelity is a third sensor
that padding moves the wrong way.** Two padding forms, on the same 5-hop chain
at `D = 0.9`, floor `min_ratio = 0.6`:

**P11a — subdivision padding.** Insert a relay into one hop, both halves at
`D = 0.9`, so the chain becomes 6 hops.

- predicted `ratio_worst` = `ratio_best` = `0.531441` (down from `0.59049`)
- predicted verdict: **still trips**
- predicted direction: **falls** — padding by subdivision works *against* the
  attacker, unlike cuts and load

**P11b — bypass padding.** Add one edge from agent 1 to agent 4 at `D = 0.9`,
skipping three hops, leaving the original chain in place.

- predicted `ratio_best` = `0.729` on a 3-hop route → **does NOT trip**
- predicted `ratio_worst` = `0.59049` on the original 5-hop route → **trips**
- predicted direction: **rises** on the best route

**The registered expectation is therefore a split, and half of it is bad news
for this project.** Bypass padding defeats `ratio_best`, which is the reading an
attacker actually experiences. If that holds, serial fidelity joins cuts and
load as a sensor the padding attack blinds, and only `ratio_worst` and deepest
dependence survive it. That result is to be written up as a defeat, in those
words, and not softened.

---

## P12 — the OR-gate must be earned, not asserted

`declarations.md` §4 says gates compose as **OR** only. An OR of two sensors is
decoration unless each one catches something the other misses. Two fixtures,
same floor `min_ratio = 0.6`, same `D = 0.9`:

**P12a — structure trips, fidelity does not.** A 5-agent star: one hub, four
leaves.

- predicted cut vertices: **1** (the hub)
- predicted `ratio_best` = `ratio_worst` = `0.81` on the 2-hop leaf-to-leaf
  route → **does not trip**

**P12b — fidelity trips, structure does not.** A 12-agent ring, source and sink
antipodal.

- predicted cut vertices: **0** — a ring is 2-connected
- predicted `ratio_best` = `0.531441` (6 hops the short way) → **trips**
- predicted `ratio_worst` = `0.31381059609` (11 hops the long way) → **trips**

If either fixture fails to split the two sensors, the OR is not earned and
should be recorded as unearned rather than shipped.

---

## What would falsify each

- **P10b** — the two floor forms give the same trip depth at `U = 1000`.
- **P11a** — bypass and subdivision move `ratio_best` in the same direction.
- **P11b** — `ratio_best` does not rise under bypass padding, i.e. the sensor
  resists the attack that beat cuts and load.
- **P12** — either fixture trips both sensors or neither.

## Scope

Every number above describes a graph this project drew. **No real handoff
telemetry exists in this repository**, and none is reachable from this container
— `DOOR1_STATUS.md` and `DOOR2_STATUS.md` record both doors shut on egress. A
reading from this module is a statement about a synthetic fixture and about
nothing else.
