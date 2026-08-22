# The contract files are not ready, because there are none

Direct answer to "are the passage files containing the specific contract
specifications ready to be dropped into the PAGES ingestion script?"

**No.** Not "not yet formatted" — there is no contract data in this repository,
real or licensed, and four of the components the protocol names do not exist in
the form it assumes. Checked rather than recalled:

| Named in the protocol | What is actually here |
|---|---|
| contract datasets (Murābaḥah, conventional) | **none.** `financial-system/generate_mesh_datasets.py` calls `np.random.seed(42)` and `np.random.choice` — it synthesises banking rows. No contracts, real or licensed. |
| 2007–09 and 2020 financial stress data | **none.** No drawdown, contagion or stress series anywhere in the tree. |
| PAGES as a label-masking topological extractor | PAGES exists in `novora-suite/`, but it is a **grounding screener** that scores prose for methodology, `N=`, p-values. On the HF cohort it returned a uniform ~0.49 and the README says why: it scores card prose, and metadata has none. It does not extract contract topology. |
| `L_ΔU`, the Unearned Capacity Leverage Ratio, and its 0.15 threshold | **no definition anywhere.** The three `0.15` hits in the repository are a fidelity-decay constant in `gilt/prereg`, an AUC-gain gate in the same file, and a correlation cut in `swarm-lmd/swarm.py`. None of them is this quantity. |
| a NERE API for multi-agent financial simulation | `api/` holds `bill-text`, `calibrate`, `gh-issues`, `gh-proxy`, `gh-search`, `govern`. GitHub proxies and a bill parser. |

## What the protocol's own gates read when pressed

Run through `intercept.js`, the three quantitative gates:

```
F1  handles 2/5   ten settled 0/10   first check: ask where this came from
F2  handles 1/5   ten settled 2/10   first check: ask where this came from
F3  handles 1/5   ten settled 1/10   first check: ask where this came from
```

F1 settles none of the ten. (The "chemicals" and "safety" flags the interceptor
raised on F2 and F1 are false positives, from the words *concentration* and
*structural* — a limit of lexical matching already registered as NULL-L2.)

## Three things to change before any of it runs

**1. Every gate is written so it can only pass.** *"Definitively proving"*, *"the
surviving statistical verification suites"*, *"verify F4 to ensure the knife is
sharp"*, and — before a single result exists — *"hardcode the certified
structural equations into the Cairn engine"*. The manuscript has a title already.
`mask_preregistration.md` restates F1 to F4 so each has a losing side.

**2. The 0.15 threshold is the floor this project already retired.** A hard gate
on a quantity with no operable sensor is exactly `D ≥ D_min`, withdrawn here at
**p = 0.735** on an unseen cohort after the sensor read zero on 76.6% of records
(`FLOOR_RETIREMENT.md`). F2 does not need it: monotonicity is testable without
any threshold at all.

**3. Stage 1 strips the labels and Stage 4 puts them back.** Masking the
vocabulary out of the topology is the strongest idea in the protocol. Rendering
that same vocabulary into an ordinary person's browser extension undoes it, and
crosses the standing line that this terminology stays out of measurement code and
out of ordinary-person interfaces. The masker is built; the UI instruction is not.

## What was built instead

`mask.js` — Stage 1, the part that needs no data. It strips names to neutral
tokens, keeps the key with whoever runs the study rather than with the coder,
refuses a spec that arrives carrying its own classification, and refuses one that
does not declare whether it is real or synthetic.

Drop-in format, once real contracts exist:

```json
{ "id": "kebab-case-id", "serial": 1,
  "parts": ["…"], "links": [["a","b",1.0]],
  "sources": ["…"], "conclusion": "…",
  "provenance": { "kind": "real" | "synthetic", "where": "where this text came from" } }
```

No `classification` field. That is filled in after masking, by someone who cannot
see the key.
