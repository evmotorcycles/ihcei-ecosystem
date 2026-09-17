# Commit 5 — serial-fidelity sentry. Results.

Run 2026-09-17. Pre-registration `prereg_sentry.md`, sha256
`9e45f3b272faff4389e1126e6c71034a955fd480a3e112eeed3702d18ec964df`, written and
hashed **before `lism_sentry.py` existed**. Reproduce with
`python3 stack/swarm/run_sentry.py`.

**15 of 15 predictions hit.** Read the next section before reading that as good
news.

---

## A clean sweep is a warning here, not a win

This repository records four misses by name and treats them as its most
valuable output. Fifteen from fifteen, on the first run, means one of two
things, and honesty requires saying which.

**Most of these predictions were derivable by hand, and that makes them weak
evidence.** `0.9^5 = 0.59049` is arithmetic. `0.9^6 = 0.531441` is arithmetic. A
ring of 12 has no cut vertex by a theorem, not by measurement. The absolute
floor's depth of 71 is `ln(0.0006)/ln(0.9)` rounded up. Predicting those
correctly demonstrates that I can multiply, not that the model is right.

What was **not** arithmetic was the direction of P11b, and that is the only
result here carrying real information.

**The suite that matters is therefore the one that can go red later**: the
relationships, the refusals, and the defeat recorded below. A prediction that
could not have failed is a description, and this write-up marks which ones those
were rather than banking them.

| prediction | genuinely at risk? |
|---|---|
| P10a — ratio is order-invariant | **no** — declared an identity in the prereg |
| P10b — exact ratios and the ratio-floor depths | **no** — hand-derivable |
| P10b — absolute floor at `U = 1000` gives depth **71** | **no** — hand-derivable |
| P11a — subdivision padding lowers the ratio | **no** — a longer product is smaller |
| P11b — bypass padding **raises** `ratio_best` | **YES** — depends on the route semantics being best-over-simple-paths, which was a design choice that could have gone the other way |
| P12a/P12b — the two sensors split | **partly** — the star's cut vertex is a theorem; that `0.81` clears a `0.6` floor while a 12-ring's `0.531441` does not is a real coincidence of the fixture, and a different floor would have collapsed the split |

---

## The finding that cost something: a third sensor falls to padding

`stack/audit/` had already measured declared padding defeating both structural
sensors: cut vertices `3 → 0`, maximum load `0.5714 → 0.3088`, both moving in
the attacker's favour. Only deepest dependence rose.

Serial fidelity, read on the best route, is **a third sensor the same attack
beats**:

| fixture | routes | `ratio_best` | trips at floor `0.6`? |
|---|---|---|---|
| 5-hop chain, `D = 0.9` | 1 | `0.59049` | **yes** |
| subdivision padding (relay inserted) | 1 | `0.531441` | **yes** — fell further |
| bypass padding (one edge skipping 3 hops) | 2 | `0.729` | **no** — **defeated** |

The attacker adds one declared edge and the sentry stops reporting. Nothing was
removed, no message changed, no hop got better; a shorter route simply became
available and `ratio_best` is the route an attacker picks.

**`ratio_worst` survived it** — `0.59049` on the original 5-hop path, still
tripping. That is why the module returns both and fuses neither, and why
`BYPASS_NOTE` says `ratio_best` must never be read alone.

Running tally of sensors against the declared-padding attack:

| sensor | verdict under padding |
|---|---|
| cut vertices | **defeated** (`3 → 0`) |
| maximum load | **defeated** (`0.5714 → 0.3088`) |
| serial fidelity, best route | **defeated** (`0.59049 → 0.729`) |
| serial fidelity, worst route | survives |
| deepest dependence | survives (`0.133 → 0.257`) |

Three of five. The two survivors are the two that are not shortest-path
readings, which is a pattern worth registering against before it is claimed.

## The floor form, measured

| floor | `U = 1` | `U = 1000` |
|---|---|---|
| ratio of `U`, `min_ratio = 0.6` | depth **5** | depth **5** |
| absolute, `min_E = 0.6` | depth **5** | depth **71** |

Identical hops, a factor of **14** in how deep the rot runs before anything
reports, purely because more entered the chain. `min_ratio` is a required
argument with no default; `absolute_floor_trip_depth` ships only so this table
can exist and nothing calls it.

## The OR-gate, earned

| fixture | cut vertices | `ratio_best` | structure trips | fidelity trips |
|---|---|---|---|---|
| 5-agent star | 1 (the hub) | `0.81` | **yes** | no |
| 12-agent ring | 0 (2-connected) | `0.531441` | no | **yes** |

Each sensor misses a fixture the other catches, so the OR is not decoration. The
caveat above stands: the split depends on the floor sitting between `0.531441`
and `0.81`, and a floor outside that band would have collapsed it. The gate is
earned **on these fixtures at this floor**, which is the most that was measured.

## What this says about the July 2026 incident

Nothing. Every number above describes a graph this project drew. No handoff
telemetry exists in this repository and none is reachable from this container —
`DOOR1_STATUS.md` and `DOOR2_STATUS.md` record both doors shut **on container
egress, not on inspection**. P24–P26 remain unwritten here; their text lives
unlocked in `phase5/runner_spec.md` for a runner that can pass the gate.
