# Phase 5 — portable external-validity bundle

**STATUS: UNLOCKED. Every prediction in this file requires a networked runner.**

---

## What UNLOCKED means here, and why it is not a formality

This repository locks predictions by writing them, hashing the file with
`sha256sum`, and asserting the hash in a test. Eleven files are locked that way.
**This file is deliberately not one of them**, and nothing in this repository
asserts its hash.

A locked pre-registration is a promise that the predictions were fixed before
the numbers existed. That promise is only worth making where the numbers can be
produced. Both doors below are shut from this container — `DOOR1_STATUS.md` and
`DOOR2_STATUS.md` record the probes — so locking this text here would create a
third pre-registration that can never be scored, joining
`plexus/substrate_preregistration.md`. One of those is a recorded gap. Three
would be the house style.

**The locking is the runner's job.** A runner that passes a door's feasibility
gate copies that door's section verbatim into its own `prereg_*.md`, hashes it,
asserts the hash, and only then fetches anything. A run that fetches first and
locks afterwards has produced a description, not a result, and this bundle does
not cover it.

**The predictions are written out in full anyway**, because the point of a
portable bundle is that the thinking was done before the access existed. Writing
them later, with the data in hand, is the failure mode.

---

# DOOR 1 — trained attention

## 1. Feasibility gate

Run before anything else. All four must pass.

```bash
python3 -c "import torch, transformers, safetensors; print('runtime ok')"
curl -sS -o /dev/null -w '%{http_code}\n' https://huggingface.co/
curl -sS -o /dev/null -w '%{http_code}\n' https://cdn-lfs.huggingface.co/
python3 -c "
from transformers import AutoModel
m = AutoModel.from_pretrained('EleutherAI/pythia-70m', attn_implementation='eager')
print('weights ok', sum(p.numel() for p in m.parameters()))"
```

| gate | pass condition | measured in this container, 2026-09-17 |
|---|---|---|
| runtime present | imports succeed | **FAIL** — all three absent |
| hub reachable | `200` | **FAIL** — `000` |
| weight CDN reachable | `200` | **FAIL** — `000` |
| forward pass runnable | weights load and a forward pass returns attentions | **not reached** |

If any gate fails, record the failure with the same conditional wording used in
`DOOR1_STATUS.md` — *the verdict rests on container egress, not on inspection* —
and **write no pre-registration**. Do not substitute randomly-initialised
weights: an attention matrix from an untrained model is a synthetic fixture with
a misleading provenance, and must be labelled one.

## 2. Pre-registration text — P21, P22, P23 (UNLOCKED, requires networked runner)

The registered theme is **the sensors this project built may be inert on the
substrate it built them for.** All three predictions are written so that the
null is the interesting outcome. None is to be softened if it misses.

### P21 — the connectivity guard never fires on real attention

`stack/perception/` refuses a pair in two different pieces, because bare `pinv`
returns a confident finite `0.790569` across a void. Softmax attention is
strictly positive everywhere, so `C = A + Aᵀ` has no zero entries and the graph
is complete.

> **Predicted:** `pieces == 1` for every layer and every head of every model
> tested. The guard fires zero times.
>
> **Falsified by:** any layer/head yielding `pieces >= 2` at the declared
> tolerance.
>
> **If it holds**, the honest write-up is that a guard this repository spent a
> patch on is **inert on its intended substrate**, and its value is confined to
> the sparse graphs it was tested on. That is a null and it is reported as one.

### P22 — cut vertices never appear on real attention

> **Predicted:** `cuts == []` for every layer and every head, so the structural
> sensor in `stack/audit/` reads nothing on trained attention.
>
> **Falsified by:** any layer/head with a non-empty cut set.
>
> **Consequence if it holds:** on this substrate the OR-gate reduces to its
> fidelity arm alone, and §3 of the ledger — which records that padding already
> defeats the best-route arm — leaves only `ratio_worst` and deepest dependence
> live. Two of four sensors inert, one defeated.

### P23 — the ratio API is invariant to the three knobs that flipped the absolute reading

`lmd-scaling/RESULTS.md` recorded a published verdict flipping on three knobs:
dtype (float32 against float64), pinv library (numpy `rcond=1e-15` against jax
`max(M,N)·eps`), and Laplacian assembly (`L[i,i] += w` against
`diag(W.sum(1)) − W`). The ratio API exists because ratios should cancel that.

> **Predicted:** on a connected attention graph, the **ratio** of two token-pair
> distances moves by less than `1e-6` relative across all eight knob
> combinations, while the **absolute** distances move by more.
>
> **Why `1e-6`:** float32 machine epsilon is about `1.19e-7`; the bound is one
> order above it, which is the smallest threshold that is not just measuring
> rounding. Stated because `CLAUDE.md` requires every gating number to carry a
> reason and an operable sensor. The sensor is the eight-way sweep itself.
>
> **Falsified by:** any ratio moving more than `1e-6` relative, or by the
> absolute distances *also* staying inside it — the second case would mean the
> fixture was too easy to distinguish the two claims.

### Horizon, and the mandatory probe past it

Any trend claim over layer depth registers its range and **one probe past that
range, reported whichever way it falls** — the rule `geometric-gate/` and
`stack/perception/` both earned. The layer count of a single model is a ceiling
that cannot be exceeded from inside it, so the past-horizon probe for Door 1 is
**a second model of different depth**, declared before the first is run.

## 3. Data and provenance requirements

- **Model identity**: full repo id and the exact commit sha of the weights, not
  a branch name. `main` moves.
- **Tokenizer identity**: id and commit sha, recorded separately — a different
  tokenizer is a different graph on the same text.
- **Input text**: the exact strings, committed as a fixture, with a hash. A
  bearing is meaningless without the tokens it was read over.
- **Attention extraction**: `output_attentions=True` with an eager attention
  implementation. Fused kernels do not return the matrix, and a silently
  substituted implementation returning `None` must abort rather than fall back.
- **Symmetrization**: `C = A + Aᵀ`, pinned. Ledger §6c records that this is not
  free on an already-symmetric input; attention is not symmetric, so it applies
  normally here, and the reading is a ratio regardless.
- **`subject_hash`**: every certificate carries one over the audited edge list,
  per ledger §4b. The subject for an attention reading is the thresholded edge
  list at audit time, and the threshold is part of the subject.

## 4. Acceptance criteria

A Door 1 run counts only if all of these hold:

1. The feasibility gate passed **and its output is recorded in the run log.**
2. The pre-registration was copied verbatim, hashed, and the hash asserted in a
   test **before any weights were fetched.**
3. All three predictions are scored and reported **whichever way they fall**,
   with misses named in the suite the way the four existing ones are.
4. The past-horizon probe on a second model ran and is reported.
5. No reading is published as an absolute distance. Ratio or rank only.
6. Nothing in the write-up implies the model understood the text.

---

# DOOR 2 — per-hop swarm payloads

## 1. Feasibility gate

| gate | pass condition | measured in this container, 2026-09-17 |
|---|---|---|
| a per-hop message corpus is obtainable | a dataset or archive with **message payloads**, not metadata | **FAIL** — dataset search returned 0 results |
| the first-party disclosures are readable | pages fetch | **FAIL** — egress-blocked; not read directly |
| payload availability confirmed by a reader | a named person records what the disclosures say | **OPEN** — see ledger §8 |

Metadata alone does not open this door. Who talked to whom and when gives the
topology; `D_k` needs what was carried. The whole registered question is whether
those two diverge, so a topology-only corpus cannot answer it.

## 2. Pre-registration text — P24, P25, P26 (UNLOCKED, requires networked runner)

These are written here and **nowhere else**. `stack/swarm/test_sentry.py`
asserts by role that no `prereg_*.md` in that package locks any of them.

### P24 — serial fidelity trips before aggregate density collapse

> **Predicted:** computing `D_total = ∏ D_k` from per-hop payload similarity
> along the realised routes, the fidelity floor is breached at a **shallower
> hop depth** than the depth at which aggregate `R_eff` departs from its
> baseline. Fidelity is the earlier sensor.
>
> **Falsified by:** `R_eff` departing first, or the two moving together within
> the resolution of the corpus.
>
> **Direction is registered because a two-sided prediction here would be
> unfalsifiable.** If it misses, it misses.

### P25 — the real graph contains the bypass that defeats `ratio_best`

`stack/swarm/` measured that bypass padding lifts `ratio_best` from `0.59049`
to `0.729` on a synthetic chain, clearing a floor the unpadded chain breached.

> **Predicted:** the incident message graph contains at least one endpoint pair
> joined by a route strictly shorter in hops than the modal route between the
> same endpoints, so a `ratio_best` sentry would have read clean on traffic a
> `ratio_worst` sentry flagged.
>
> **Falsified by:** no such pair existing.
>
> **If it holds**, the synthetic defeat recorded in ledger §3 is not an artefact
> of a graph this project drew, and `ratio_best` must not ship as a lone reading
> anywhere.

### P26 — the structural sensor is inert on the real graph too

> **Predicted:** cut vertices on the 1,200-agent message graph number **zero**,
> as they did on the synthetic 40-agent ring with a 12-agent clique (`0 → 0`).
>
> **Falsified by:** any cut vertex.
>
> **Note on what this would and would not license:** a zero here says the
> drawing has no single routing point. It says nothing about motive, intent or
> decision-making by any agent or organisation, and the write-up may not drift
> into that.

## 3. Data and provenance requirements

- **Payloads, not metadata.** Per-hop message content, or a per-hop similarity
  already computed by a named method with that method recorded.
- **Route reconstruction**: how a "hop" was identified from the log, written
  down before the fidelities are computed. A different hop definition is a
  different `D_total`.
- **Access terms**: the corpus is reported as analysed by third-party
  evaluators under access rather than released. Any run states its access basis
  and whether redistribution is permitted. **If it is not, the derived
  readouts ship and the corpus does not.**
- **A `where` field** on every hand-assigned link or classification, per
  `CLAUDE.md`. `test_metaphor.py` refuses one without.
- **No claim about a real company or person** beyond the narrow verified public
  facts already quoted in `DOOR2_STATUS.md`. `test_packs.py` greps for company
  suffixes and currency symbols.

## 4. Acceptance criteria

1. The feasibility gate passed on **payload availability specifically**, and the
   evidence for that is recorded.
2. P24–P26 copied verbatim, hashed, asserted **before the corpus was touched.**
3. The hop definition was written down before any fidelity was computed.
4. All three scored and reported whichever way they fall.
5. Every readout carries a `subject_hash` over the edge list audited, and a
   date. Ledger §4b.
6. The write-up names the event as a topology observation and nothing more.

---

## Both doors: the standing instruction

**A network limitation must not harden into a finding.** Neither verdict in
`DOOR1_STATUS.md` nor `DOOR2_STATUS.md` rests on inspection; both rest on what
one container could reach on one day. The human check in ledger §8 is **OPEN**
and stays recorded as open until a named reader records an answer. If a runner
opens either door, the corresponding status file is wrong and is to be replaced,
not amended into agreement.
