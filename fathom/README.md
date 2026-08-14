# FATHOM — how deep does this actually go?

To fathom is to drop a line and find the depth rather than judge it from the
surface. FATHOM answers the one question SPAR provably cannot:

> **If any single source turned out to be wrong, how much would be left?**

```
python3 fathom/fathom.py
python3 -m pytest -q fathom/test_fathom.py
```

Offline, on-device, `$0`, no keys. Same engine as SMI and SPAR.

---

## Why it exists

Building SPAR turned up a null. Route redundancy is **not** evidential
independence, and it has the sign backwards:

| structure | SPAR (route redundancy) | FATHOM (sounding by removal) |
|---|---|---|
| two accounts, one shared origin — *not independent* | 0.75, looks robust | **100%** — rests on one thread |
| two accounts, separate sources — *independent* | 1.00, looks fragile | **50%** — survives losing either |

Independent sources form a tree; a shared origin closes a cycle; SPAR measures
cycles. That null is pinned in `spar/README.md`. The gap it left is what this
fills — **by removal**, because removal is the only method that has held up
anywhere in this stack.

---

## What is measured

Sources are the places support enters from. Contract them all into one ground and
the conclusion's support is the effective **conductance** to that ground:

```
support        = 1 / R(conclusion, ground)
dependence(s)  = 1 − support without s / support with all
```

Contraction is the whole move. It stops asking *“is there another way round this
link”* and starts asking *“is there another way **in**”*.

```
Two accounts that trace to ONE origin
  lose Common origin        100.0%   <- carries it alone
  sounding                  100.0%    0.0% of the support would remain

Two accounts with SEPARATE sources
  lose Source 2              50.0%
  lose Source 1              50.0%
  sounding                   50.0%   50.0% of the support would remain

A study and a blog post
  lose Main study            97.8%
  lose A blog post            2.2%
  sounding                   97.8%    2.2% of the support would remain
```

Properties, all tested:

- **k equal independent sources each carry exactly 1/k**, to `1e-9`.
- **Scale-invariant.** Multiply every link by anything; no dependence moves.
  Dependence is a ratio of conductances, so the factor cancels.
- **Depth is not independence.** Relaying one account through five hands still
  reads as one thread — the padding earns nothing.
- **A source with no path to the conclusion adds nothing.** Listing it does not
  make it support anything.
- **Strength is respected.** One real study plus one blog post reads `97.8% /
  2.2%`, not “two sources”.

---

## The boundary, stated twice because it matters

FATHOM measures **the structure you described**. Two sources entered as separate
are treated as separate — so if they secretly share an origin and you did not say
so, FATHOM will report robustness that is not there.

It also says nothing about whether any source is *true*. It measures what would
be left if one turned out not to be.

---

## One wording fix worth recording

The summary line originally said *“survives losing any one”* whenever the deepest
dependence was below the threshold. That is true at 97.8% dependence and
thoroughly misleading. The fix was to print **what remains** as a number rather
than to add a second threshold — a tunable would have been the easier change and
the wrong one.

---

Files: `fathom.py` (engine, guards, demo) · `test_fathom.py` (14 tests) ·
`results_fathom.json`.
