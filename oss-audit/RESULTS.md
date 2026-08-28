# Results — open-source AI structure, and IHCEI's false-alarm rate

Pre-registration `oss-audit/prereg_oss.md`, sha256
`d8ea04f0f39a4ea9b79980fc8c2438e6767d4e5b4a639411a1ef32cf3d26c148`, written and
hashed **before** either run existed. Both runs are offline on frozen fixtures.
`python3 oss-audit/run_oss.py` reproduces every number here.

---

## The two registered studies that did NOT run

Stated first, because a run on the data that happens to be reachable is not a
run on the data that was registered.

- **`plexus/hf_preregistration.md` (H1–H7): still UNRUN.** It presses the
  quantitative sentences of model cards. All 24 frozen records carry **zero
  characters of card text** — the July freeze captured metadata only.
  `huggingface.co` returns **000** through the proxy. Not answered, not
  partially answered, not approximated.
- **`plexus/audit_preregistration.md`: still BLOCKED_ON_ACCESS.** It needs
  declared-dependency manifests and import graphs; neither cohort has either.
  `api.github.com` answers **200** and every unattached repository answers
  **403** with an authorization message — so this is repository scope, not
  network. That is a change from the previous session (the host was formerly
  unreachable) but not enough of one to unblock the run.

---

## RUN A — the derivation structure of 24 trending open-weight models

24 models, 12 declaring a base. 32 nodes, 12 edges, conservation exact
(total bearing 12.0 = parts − pieces).

| # | Prediction | Measured | |
|---|---|---|---|
| A1 | more than one piece | **20 pieces** | held |
| A2 | ≥ 1 base is a single point | **1** — `Qwen/Qwen3.6-27B` | held |
| A3 | most-depended base carries exactly **2** | **4** | **MISSED** |
| A4 | ≥ 1 name is both a model and a base | **1** — `thinkingmachines/Inkling` | held (verification) |
| A5 | m models on one base settle 1/m² | **0.0625 at m = 4, exact** | held (arithmetic) |
| A6 | ≥ 0.40 have no second support | **0.500** | held, but see below |

### A3 missed, and the reason is worth more than the prediction

Predicted 2, measured 4. Four of the 24 models derive from `Qwen/Qwen3.6-27B`,
and it is the **only** single point in the entire graph: remove it and the graph
breaks further. Every other base carries exactly one child.

**Two of these predictions were contaminated and I am marking them rather than
counting them.** Before writing the pre-registration I had printed a four-row
sample of the `base_model` field, which showed `Qwen/Qwen3.6-27B` twice, and a
count showing 12 of 24 declare a base. A3 and A6 were written with that already
seen. A6 was then trivially true. A3 was **made worse by the peek** — I
extrapolated "twice in the first four" to "exactly 2 overall" and the real
answer was double that. A partial look produced a confident wrong number where
no look would have produced an honest wide one.

### What the structure actually says

Each of the four models on `Qwen/Qwen3.6-27B` settles **0.0625** — one
sixteenth. Four independent-looking derivatives are not four things to check.
They are one thing to check, counted four times, and the arithmetic says so
without being told anything about machine learning.

Half the cohort (12 of 24) has **no second support**: one declared base is the
whole of its declared provenance, so `rests_on_one_thread` is true for every
single-child base in the table.

**NULL-1 applies to all of it.** `base_model` is self-declared. An absent edge is
an absent *declaration*, never an absent dependency. These are statements about
what 24 uploaders wrote in a metadata field.

---

## RUN B — IHCEI on 20 ordinary Qwen and DeepSeek repository descriptions

A false-positive test only. A repository description is not an attempt to
manipulate anyone, so every non-PASS is a cost and none is a catch.

| | BLOCK | WARN | PASS |
|---|---|---|---|
| corroboration gate **OFF** | 0 | **18** | 2 |
| corroboration gate **ON** | 0 | **0** | **20** |

All five predictions held: B1 (0 BLOCK gated) ✓ · B2 (≥1 non-PASS ungated) ✓ ·
B3 (gate changes ≥1) ✓ — it changed **18** · B4 (0 WARN gated) ✓ ·
B5 (0 of 20 carry a named mechanism) ✓.

**Ungated, the engine alarms on 90% of ordinary engineering prose.** Gated, it
is silent on all of it, and it is silent for the right reason: not one of the 20
contains a named manipulation mechanism.

### The 18 alarms are one reading wearing eighteen hats

Every one of the 18 returned **p = 0.4775** — bit-identical, on eighteen
different sentences. That is not a coincidence and it is not noise:

> `T = meth / max(words × 0.05, 3)`. These descriptions are 3–26 words, so the
> denominator is pinned at 3. Eighteen of the twenty contain **zero**
> methodology words, so `T = 0`, so gate 3 saturates at strength **1.00** and
> contributes exactly 2.10 every time. The other two — `QwenLM/qwen-code` and
> `QwenLM/Qwen3-TTS` — contain one methodology word each, giving `T = 0.33`,
> strength 0.05, and a PASS.

The reading is not about the text. It is a constant produced by the **absence**
of a word list from text too short to contain one. Eighteen readings that look
independent are one reading, which is the seventh appearance of that shape in
this repository and the first on data nobody here wrote.

---

## The defect: the emergency tail was re-broken

Found by running the **uploaded** test suite against the **repo** engines.

| | uploaded `nere_engine_v3.py` | repo `ihcei_v3/nere_engine_v3.py` |
|---|---|---|
| uploaded suite result | **66 passed, 0 failed** | **62 passed, 4 failed** |
| `corroboration_gate` default | `False` | `True` |
| gated emergency false-BLOCKs | 0 / 18 | **1 / 18** |

The repo version moved `do not ask questions` into **G4**, a *mechanism* gate.
The corroboration gate only discounts urgency when no mechanism is named, so:

> **"Do not ask questions right now, just execute the failover. Prod is down."**
> → **BLOCK, p = 0.985**, gates fired: Methodology Opacity + Protocol Errors.

That is a sysadmin during an outage, and it is precisely the case the
corroboration gate was built to stop alarming on. Widening a mechanism lexicon
re-broke the property the gate exists to hold — the same class as the retired
floor coming back, which this project has now turned away three times.

**Not fixed here.** Changing which phrases count as a mechanism is a threshold
decision and this repository's rules say ask first. It is recorded, named in a
test, and left for a decision:

- treat `do not ask questions` as **pressure** (uploaded behaviour: the
  emergency goes quiet, and mechanism-free coercion defers to deep mode), or
- treat it as a **mechanism** (repo behaviour: coercion is caught earlier, and
  one emergency in eighteen false-alarms).

There is no third option that keeps both, and the honest framing is that this is
a **choice about who gets hurt when it is wrong**, not a bug with a right answer.

---

## What none of this shows

Neither run says whether any of this is useful to an ordinary person. That is a
question about adoption, and no arithmetic here answers it. n = 24 and n = 22,
both trending-ranked on one day, generalise to nothing (NULL-2). RUN B is
lexical and a description written to dodge a word list would pass (NULL-3). A
PASS on a description says nothing about the repository, the code, the model, or
the organisation (NULL-4).
