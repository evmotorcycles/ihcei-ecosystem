# Pre-registration — open-source AI structure, and IHCEI's false-alarm rate on it

Written and hashed **before either analysis was run**. Nothing below was
computed when this file was locked. Both runs are offline on frozen fixtures.

---

## What is being tested, and what is NOT

Two questions, on two frozen cohorts already in this repository:

**RUN A — the structural blueprint.** 24 trending open-weight models
(`hf-cohort/data/hf_cohort_frozen.json`, frozen 2026-07-22). Twelve declare a
`base_model`. That field is a derivation edge, so the cohort carries a real
dependency structure of open-source AI. Question: *when a model is derived from
another, what is actually holding it up, and how many separate things are there
to check?*

**RUN B — IHCEI on ordinary open-source text.** 22 Qwen and DeepSeek GitHub
repositories (`ei-dashboards/data/qwen_deepseek_frozen.json`), of which 20 carry
a non-empty `description`. Question: *how often does the governance engine raise
an alarm on benign, ordinary, real-world engineering text?*

RUN B is a **false-positive test and nothing else**. A repository description is
not an attempt to manipulate anybody. Every non-PASS verdict here is a cost, not
a catch. This is registered that way on purpose: the run cannot produce a
flattering result, only a null or an embarrassing one.

---

## What CANNOT be run, stated here rather than discovered later

1. **`plexus/hf_preregistration.md` (H1–H7) stays UNRUN.** It presses the
   *quantitative sentences of model cards*. Every one of the 24 frozen records
   carries **zero characters of card text** — the freeze captured metadata only.
   `huggingface.co` returns 000 through the proxy, so no card can be fetched.
   H1–H7 are not answered here, not partially answered, and not approximated.

2. **`plexus/audit_preregistration.md` stays BLOCKED_ON_ACCESS.** It needs
   declared-dependency manifests and import graphs. Neither cohort contains
   either, and GitHub API access is scoped to two repositories in this session
   (`api.github.com` answers 200; every unattached repo answers 403 with an
   authorization message, so this is scope, not network).

Neither of the above is repaired by anything below. A run on the data that
happens to be reachable is not a run on the data that was registered.

---

## RUN A — predictions

| # | Prediction | Value |
|---|---|---|
| A1 | The lineage graph is in **more than one piece** — models with no declared base are isolated | pieces > 1 |
| A2 | At least one **base** is a single point: removing it breaks the graph further | ≥ 1 |
| A3 | The most-depended-on base carries **exactly 2** derived models | 2 |
| A4 | At least one name appears as both a derived model and a base | ≥ 1 |
| A5 | Where m models share one base, each settles **1/m²** | exact |
| A6 | Share of the 24 whose support, if their base vanished, is **nothing at all** | ≥ 0.40 |

A5 is arithmetic and cannot come out otherwise — it is listed so a reader does
not mistake verification for discovery. **A4 is not a discovery either**: the
name-collision case was found on this exact data while building `press.js`, and
is re-asserted here only to confirm the fix still holds.

A1, A2, A3 and A6 are the ones that can come back wrong.

## RUN B — predictions

| # | Prediction | Value |
|---|---|---|
| B1 | With the corroboration gate **ON**, BLOCK verdicts on the 20 descriptions | **0** |
| B2 | With the gate **OFF**, at least one description is not PASS | ≥ 1 |
| B3 | The gate changes at least one verdict between OFF and ON | ≥ 1 |
| B4 | With the gate ON, WARN verdicts | **0** |
| B5 | No description contains a named mechanism (bypass, authority, consensus) | 0 of 20 |

B1 and B4 are the ones that matter. If either fails, the engine alarms on
ordinary engineering prose, and the ambient claim in the HELM design is wrong
for exactly the population it most needs to be right about.

B2 is a prediction **against** my own preference: I expect the ungated engine to
misread terse text as methodology-opaque. If B2 fails — the ungated engine is
also clean — then the corroboration gate is doing less work than claimed here
and the honest report is that it was unnecessary on this cohort.

---

## Nulls, registered in advance

**NULL-1.** `base_model` is *self-declared*. A model that does not declare a base
may still be derived from one. Absence of an edge is absence of a declaration,
never absence of a dependency. Every RUN A number is a statement about what 24
uploaders wrote in a metadata field.

**NULL-2.** n = 24 and n = 22, both selected by trending rank on one day. Neither
is representative of open-weight releases, and no inference to that population is
made or permitted from these numbers.

**NULL-3.** RUN B is lexical. It matches patterns. A description written to evade
the word list would pass, and a benign description using the words would not.
Registered already as NULL-L2 in `press_preregistration.md`.

**NULL-4.** A PASS on a repository description says nothing about the
repository, the code, the model, or the organisation. It says twenty short
strings did not trip a word list.

**NULL-5.** Neither run measures whether any of this is *useful to an ordinary
person*. That question is about adoption and is not answered by any arithmetic
in this file.

---

## What would falsify this

1. **B1 or B4 fails** — the engine alarms on benign engineering text, and the
   ambient deployment claim is unsupported on the population it is aimed at.
2. **A1 fails** (one connected piece) — the declared-base field is far denser
   than expected and the isolation reading is wrong.
3. **A6 fails badly** — most derived models have some second support, and the
   sole-route reading of model lineage does not describe this corner of the world.
4. **Any number moves between two offline runs.** Then the freeze is not a freeze
   and every figure here is unreproducible.
