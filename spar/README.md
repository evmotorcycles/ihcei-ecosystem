# SPAR — what is holding this up

A spar is the member that carries the load. Everything else on a rig is fittings.

For any process, SPAR says which links are spars, using one number that nobody
chose:

```
bearing = weight × effective resistance
        = P(this link appears in a random spanning tree)
        = how often this link is the thing holding the structure together
```

```
python3 spar/spar.py                    # the demo, with tables
python3 spar/build_app.py               # writes spar/app.html — offline, phone-first
python3 -m pytest -q spar/test_spar.py
```

Offline, on-device, `$0`, no keys, no network. The engine is `smi/lmd.py`, which
`smi/test_parity.py` checks against its browser port over fourteen graphs — so
the page in your hand and the arithmetic under test are the same arithmetic.

---

## Why this is not a score

Every "criticality score" in every dashboard is a formula somebody chose, with
weights somebody tuned, that somebody else can argue with. This is not that.

**1 · Conserved.** Foster's theorem: the bearings of every link sum to exactly
`n − k`, where `n` is the number of parts and `k` the number of separate pieces.
Not normalised to sum to something — it comes out that way.

| structure | total | parts − pieces | error |
|---|---|---|---|
| triangle | 2.000000000000 | 3 − 1 | `0.0e+00` |
| K5 | 4.000000000000 | 5 − 1 | `4.4e-16` |
| weighted mix | 4.000000000000 | 5 − 1 | `8.9e-16` |
| two pieces | 4.000000000000 | 6 − 2 | `8.9e-16` |

**2 · Parameter-free.** Nothing to tune. Two people running it on the same
structure get the same numbers.

**3 · Ungameable by scale.** Multiply every weight by anything and not one
bearing moves — `w → Jw` and `R → R/J`, so `w·R` is untouched. Measured at
`4.4e-16` over a 10⁹ range of factors. Insisting that everything you touch is
very important changes nothing.

**4 · Obfuscation is arithmetic, not allegation.** The total *is* `n − k`, so
adding steps raises it. A complaints process that carried `6.00` and now carries
`8.00` for the same outcome has had two steps' worth of structure added, and the
number says so without anyone having to accuse anyone.

---

## The claim is checked against counting, not against a textbook

`bearing = P(link is in a random spanning tree)` is the whole product, so
`test_spar.py` enumerates **every spanning tree** of each small graph, weighted,
and compares. The two computations share no code.

```
weighted 4-node graph, 3 spanning trees
  link 0-1 (w=3.0) :  w·R = 0.882352941   counting trees = 0.882352941
  link 1-2 (w=0.5) :  w·R = 0.294117647   counting trees = 0.294117647
  link 0-2 (w=2.0) :  w·R = 0.823529412   counting trees = 0.823529412
  link 2-3 (w=7.0) :  w·R = 1.000000000   counting trees = 1.000000000
```

---

## A null, found while building this, and kept

The tempting next claim is that this measures whether a conclusion is genuinely
**corroborated**. It does not. It gets the sign backwards:

| structure | highest link | links with no alternative |
|---|---|---|
| A and B share one origin — **not** independent | 0.75 | 0 of 4 |
| A and B have separate sources — **independent** | 1.00 | 4 of 4 |

The genuinely independent structure reads as the *more fragile* one. Independent
sources form a tree; a shared origin closes a cycle; and this measures cycles.
**Route redundancy is not evidential independence.**

An earlier version of `spar.py` asserted the opposite in its own docstring, and a
third demo in the app was built on it. Both are gone. The null is pinned by
`test_route_redundancy_is_NOT_evidential_independence` so nobody re-derives it.

---

## The limitation, stated plainly

On a pure **tree** every link is a bridge and every bearing is exactly `1.000`.
SPAR cannot rank the steps of a tree, and any tool claiming to would be inventing
the ranking.

That reading is not a failure to say something. It says: *no step in this
structure has an alternative route; every one is a single point of failure; and
nothing here is checked against anything else.* For a bill or a benefits
decision, that is the finding.

**SPAR is informative about ranking exactly where redundancy exists, and about
fragility everywhere.**

A link's bearing cannot answer "does all of this pass through one part" —
`single_points()` answers that separately, by taking each part out and counting
the pieces left behind, rather than by a formula that could be argued with.

---

## What it does not tell you

Whether a step is *useful*. A required form that changes no outcome still reads
`100%`, because removing it does break the chain. That is a true statement about
the structure and a claim about nothing else.

It also has no acquisition layer. Every structure here is hand-entered. Turning
a real bill, contract or process into a weighted graph is a separate problem and
it is not solved in this directory.

---

Files: `spar.py` (engine, guards, demo) · `test_spar.py` (36 tests, incl.
brute-force spanning-tree enumeration) · `app_template.html` + `build_app.py` →
`app.html` (offline, phone-first).
