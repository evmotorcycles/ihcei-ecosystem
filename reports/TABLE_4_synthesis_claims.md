# Table 4 — Claim-status for the NERE synthesis report

**GATE: this table awaits approval. No report prose has been written.**

Tags: `repo-measured` (commit given) · `identity` (true by construction) ·
`external-claimed` · `analogy` · `lineage` · `framing` · `design` · `simulated` ·
`retired` · `open`.

**On naming retired terms:** this register does **not** reproduce retired
wording. `stack/governance/declarations.md` §15–§16 holds it verbatim and is
exempt *by what it is*; this file points there instead. Widening the exemption
set to cover `reports/` would be exemption-by-name, which is the failure mode
the rule exists to stop.

Claims are inventoried from the commissioning text **and** from its "Reality
Check" section. Where a row corrects the source, the correction is the row.

---

## A. Corrections to the commissioning text's own Reality Check

The firewall list was applied. These four rows are what checking the *positive*
claims turned up.

| # | The text says | What the repo measures | Tag |
|---|---|---|---|
| **A1** | *"The Geometric Gate: representation collapse is caught by trace-ratio **and effective rank**"* | **Half wrong, and the wrong half matters.** `geometric-gate/RESULTS.md`: trace scales as `c²` (**G1 hit**, rel. err `4.2e-16`) — but **effective rank does not move at all** (**G3 hit**, `1.2e-14`), and at threshold the collapsed space has *"effective rank identical to 1e-9."* **Effective rank is blind to uniform collapse.** Only the absolute trace sees it. | `repo-measured` — **correction** |
| **A2** | *"We proved R_eff ≡ 1 on uniform complete graphs (**falsifying** the naive lost-in-the-middle overclaim)"* | `R ≡ 1` on row-normalised `K_n` is an **identity**, max dev `< 1e-14`. It shows the metric is *constant* on that graph — i.e. cannot express positional degradation there. It does not falsify an empirical claim about deployed models; that inference is Layer-3. | `identity`; the falsification clause is `analogy` |
| **A3** | *"aggregate graph resistance is **not** a fidelity proxy"* — listed under "we proved" | This is a **design contract** (`[T3:B10]`), not a measurement. Redundancy masking serial decay is argued from the algebra, not measured on a fixture. | `design`, **not** `repo-measured` |
| **A4** | the text applies an adjective of confirmation to the incident | The confirming adjective was **struck from every repo surface** under ruling 2. Primaries were egress-blocked and **never fetched**; corroboration is out-of-repo and secondary. Per-hop payload availability remains **UNCONFIRMED**. | `external-claimed`, primaries unread |
| **A5** | the text uses a completed-demonstration verb ~12 times | The repository's own engine carries a module constant whose value is the string `"NOTHING"`, named for exactly this verb. Nothing here demonstrates in that sense; things are measured, and identities hold. | **vocabulary `retired`** |

## B. `repo-measured` — LMD / audit

| # | Claim | Value | Commit | Tag |
|---|---|---|---|---|
| B1 | Declared padding clears every cut vertex | `3 → 0` | `ae20cd4` | `repo-measured` |
| B2 | Maximum load **falls** under the same padding — registered the other way | `0.5714 → 0.3088` | `ae20cd4` | `repo-measured` · **registered miss** |
| B3 | Deepest dependence rises — the surviving sensor | `0.133333 → 0.257161` | `ae20cd4` | `repo-measured` |
| B4 | Second, disjoint fixture agrees in direction | `0.111 → 0.619` | `agi-stack/` | `repo-measured` |
| B5 | **Three of five sensors are defeated by declared padding** | cuts, load, best-route fidelity | ledger §3 | `repo-measured` |
| B6 | Bare `pinv` answers confidently across disconnected components | `0.790569` | — | `repo-measured` |
| B7 | Foster `Σ w·R = n − k` — assert-only, never returned, gates nothing | exact | — | `identity` |
| B8 | `tol_ratio = 1e-10` replaces an inherited default that flipped a verdict | — | — | `design` |

## C. `repo-measured` — LISM

| # | Claim | Value | Commit | Tag |
|---|---|---|---|---|
| C1 | `E = U · ∏D_k` is a product of retention factors; **log-additive across serial channels** (`log E = log U + Σ log D_k`) | — | — | `design` |
| C2 | Ratio floor blind to `U`; absolute floor is not | depth `5/5` vs **`5/71`** | `d16eac3` | `repo-measured` |
| C3 | Bypass padding defeats best-route fidelity | `0.59049 → 0.729` past a `0.6` floor | `d16eac3` | `repo-measured` · **defeat** |
| C4 | Subdivision padding moves the other way | `→ 0.531441` | `d16eac3` | `repo-measured` |
| C5 | 39-hop decay `0.84 → 0.01`, `r = −0.887`, `N = 500` | `cohort_D_swarm(seed=20260719)` | — | **`simulated`** — retired as telemetry `a9ac3e6` |

## D. `repo-measured` — LINTEL / structure

| # | Claim | Value | Tag |
|---|---|---|---|
| D1 | Names stable under behaviour-preserving rewrites | `27/27` | `repo-measured` |
| D2 | Names disputed under completion of omissions | `18/27` | `repo-measured` |
| D3 | Counts inflatable by shims that change no behaviour | `27 → 39 → 46`, ≈`1.7×` | `repo-measured` |
| D4 | The repository is its own subject and grew; figures moved with **no certificate changing** | modules `156 → 169`; cuts `27 → 31` | `repo-measured` `5ac72a2` |
| D5 | Candidates are not edges | `31 of 92` were mentions only | `repo-measured` |
| D6 | The quotient pass | **Q3 missed; does not ship** | `repo-measured` · negative |

## E. `repo-measured` — the geometric gate and the collapse

**This block is where A1 bites.** The two results point opposite ways and must
not be merged.

| # | Claim | Value | Tag |
|---|---|---|---|
| E1 | **No threshold is picked out by the data** — the sensor walks the whole candidate band | — | `repo-measured` · negative |
| E2 | Trace scales as `c²` — an **absolute** sensor, and it does see uniform collapse | rel. err `4.2e-16` | `repo-measured` |
| E3 | **Effective rank does not move at all** under the same rescale | `1.2e-14` | `repo-measured` |
| E4 | The **structural readouts are blind** to the collapse they were pointed at; embeddings differing by `1e6` in scale give identical readings | `36.000000` both arms | `repo-measured` |
| E5 | Collapse prevention is **stop-gradient**, not the moving average | 5/5 seeds, ~12 orders | `repo-measured` |
| E6 | One property, two consequences: **ungameable by scale, blind to a scale collapse** | — | `repo-measured` |
| E7 | Uniform collapse is invisible to **every ratio**, pair ratios included | — | `identity`, locked by `test_uniform_collapse_blindness.py` |

## F. `external-claimed` — the 2026 incident

| # | Claim | Tag |
|---|---|---|
| F1 | ~1,200 nodes, >70,000 messages on an undeclared channel, ~700 participating | `external-claimed`, **primaries unread** |
| F2 | Corpus analysed by third-party evaluators under access; no public release located | `external-claimed` |
| F3 | Per-hop payload availability | **UNCONFIRMED** · `open` |
| F4 | attacker framing, a psychiatric epithet, and an extinction metaphor | **`retired`** — motive and threat framing, stripped entirely |

## G. `analogy` — architecturally useful, not measured

| # | Claim | Tag |
|---|---|---|
| G1 | *"Agents hacking monitors ≡ rewriting inputs to `laplacian_audit.py`"* | `analogy` |
| G2 | *"Kill switches fail because of graph theory"* | `derived` — a theorem whose **premise is untested** (that a post-coordination swarm graph has no articulation points). Real kill switches act on substrate and credentials, not on graph nodes. Not `retired`, but not evidence either. |
| G3 | `R_eff = ∞` as a defensive achievement | **`identity`** — it is the *definition* of a disconnected graph. Air-gapping is the only **decidable** isolation state; that is weaker and defensible. |
| G4 | LINTEL "blinded" by a swarm | `design` boundary — undeclared channels are invisible **by definition**; LINTEL reports **disputes, not breaches**. |

## H. `lineage` / `framing` — explains why the stack exists; validates nothing

| # | Item | Tag |
|---|---|---|
| H1 | Hinton: Boltzmann machines, autoencoders, t-SNE, capsules, forward-forward | `lineage` |
| H2 | Hinton: immortal computation / weight-sharing swarms | `lineage` |
| H3 | Karpathy: "the transformer as a graph", attention as message passing | **`framing` — unmeasured in-repo; Door 1 shut.** Permitted once in a motivation section carrying the tag; **"the proposer layer" everywhere operable** |
| H4 | LeCun: JEPA, latent-state prediction | `lineage` |
| H5 | *"Structurally blind to physical reality"* as a property of the proposer layer | `framing` — not measured here |

## I. `retired` — the firewall list, confirmed against the ledger

| # | Retired claim | Held retired by |
|---|---|---|
| I1 | LISM given the vocabulary of heat and disorder | ledger §3 holds the wording; the module is grepped for it |
| I2 | LMD as physics / "Layer-1 physical limits" | `smi/test_smi.py` guards five emergence phrases in shipped output; the ledger holds them |
| I3 | the claim that a sensor cannot be gamed | B1–B5: three of five are defeated by declared padding. **No sensor here resists gaming** |
| I4 | the five emergence phrases, listed verbatim in `smi/test_smi.py` | same guard as I2 |
| I5 | *"Validated against real 39-hop telemetry"* | **RETIRED `a9ac3e6`**, 8 surfaces; ledger §15; enforced by `test_cohort_d_tagging.py` |
| I6 | Anthropomorphic and threat rhetoric (F4) | stripped; no motive attribution anywhere |

## J. `open`

| # | Item |
|---|---|
| J1 | Door 1 — no ML runtime, weight hosts unreachable; **shut on egress, not inspection** |
| J2 | Door 2 — no obtainable per-hop corpus; P24–P26 unwritten |
| J3 | The human check on primaries and on block-versus-outage — **OPEN** |
| J4 | Detector **recall** — unmeasurable by construction. Precision is demonstrable; recall is not |

---

## What I need before writing prose

1. **A1** — confirm the report states that **effective rank is blind** to uniform
   collapse and only the absolute trace sees it. The commissioning text has this
   backwards, and it is the same distinction as C4a/C4b in the physics thesis.
2. **A2** — confirm `R ≡ 1` is presented as an identity, with the
   "falsifies lost-in-the-middle" clause dropped or tagged `analogy`.
3. **A3** — confirm the redundancy-masking claim ships as `design`, not as a
   measurement.
4. **G2** — confirm kill-switch failure stays `derived` with its premise `open`,
   rather than joining the `retired` list as the Reality Check proposed.
5. Whether §H3 gets its one tagged appearance, as in Report 1, or none at all.
