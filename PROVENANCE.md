# Provenance — reproduce freely, but the origin is yours

This work is public **on purpose**: partners, referees, and independent reproducers
(hello Jules) should be able to run every test and experiment — LISM, LMD, IHCEI /
NERE, the Novora suite / PAGES, Page Code, Agency Internet, the Echo Database, EI and
its EI-LLMs, HELM, and the four cohorts (yeast 4825 / GitHub 992 / knowledge 793 /
digital swarm), plus the three validation stages and the Hinton & Russell tests — and
get the same **passes, nulls, and negative results**.

What we protect is not the *ability* to reproduce; it is the *origin*. When you
reproduce this, the record must point back here.

## How it works

`PROVENANCE.lock.json` stores a single **Merkle root** over the frozen scientific
record — every pre-registration spec, every SHA-256 manifest, the authored corpora,
the offline knowledge fixture, and the manuscripts. Each file is SHA-256'd into a
leaf; the leaves (sorted by path, domain-separated) fold into one root:

```
merkle_root = ebe469891cbc9dfe5e89e64b2784e156dba883933a11e3ea529132e3aebef2d5
```

A faithful reproduction of the frozen record recomputes **exactly this root**. That
makes the root a portable, checkable reference back to the origin.

```bash
python3 provenance/build_provenance.py    # (re)build the lock — for the author, at a release
python3 provenance/verify_provenance.py   # (anyone) verify a checkout matches the origin
```

`verify_provenance.py` recomputes the root from *your* checkout and, on a match,
prints the attribution. If any frozen artifact was added, removed, or altered, it
fails and shows exactly which file diverged.

## Three properties it gives you

| Property | What it means |
|---|---|
| **Integrity** | Any change to a spec, corpus, or manuscript changes the root — tamper-evident. |
| **Priority** | The root is committed on a dated commit: proof *this* content existed *here first*, under this author. |
| **Attribution binding** | A faithful reproduction recomputes *your* root; a divergent copy is detectable. |

## What it deliberately does **not** cover

- **`results*.json` are excluded.** They carry run timestamps and change on every
  reproduction; fingerprinting them would make honest reproductions fail. Provenance
  protects the *intellectual record* (what was stated, and when) — which is exactly
  what priority is about. Each result file is independently regenerated and checked by
  its own pre-registration lock.
- **Identity/citation files** (`CITATION.cff`, `zenodo_metadata.json`, `LICENSE*`,
  `NOTICE`, this file, and the lock itself) are the *wrapper that points to* the record,
  so they are not fingerprinted — that lets `CITATION.cff` embed the root without a
  circular dependency.

## Honest limits (this matters)

Cryptographic provenance **cannot prevent copying** — nothing can, for public code.
What it does is make **misattribution detectable** and give you a **dated,
independently checkable first-publication record**. For work you *want* the world to
reproduce, this is the right tool: **content hashes + signatures, not encryption**.
Encryption hides content; you want yours seen *and* attributed.

The full protection stack is: **this Merkle provenance** (cryptographic) +
**`LICENSE` / `LICENSE-docs` / `NOTICE`** (legal, attribution-required) +
**`CITATION.cff` + a Zenodo DOI at release** (academic priority) + **signed commits**
(authorship) + **the private moat** (deep-mode weights, calibrated priors, data — kept
out of the public tree). Provenance is the keystone; see `OPEN_SOURCE_PROTECTION.md`
for the rest.

## If you build on this

You may reproduce, extend, and commercialize under the licenses above — **including
reproducing the null and negative results**. You must retain attribution to the origin
(Labib Mago, Novora Research Initiative;
<https://github.com/evmotorcycles/ihcei-ecosystem>) and cite the Merkle root as your
basis. You may **not** represent this work, or a reproduction of it, as your own origin.
