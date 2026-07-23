# OpenAlex LISM — citation concentration + reference-effort heavy tail (pre-registered before data)

**Run it (once real data is in):** `python3 openalex-lism/openalex_lism.py` · stdlib · offline · `$0`

OpenAlex is a fully **open, keyless** catalogue of ~250M scholarly works with the citation
graph attached. This experiment tests two **structural** LISM predictions on a real,
reproducible random sample of it — and honestly declares the coupling law untestable on a
single snapshot while flagging OpenAlex as the *most promising future two-hop substrate*.

The pre-registration was **locked before any data was seen** (spec
`175efac5f805f87989c249069b695b095d9a4c170bbc72205c7ed7f22df9233f`) — that is the whole
point of pre-registration, so the gates can't be reverse-fitted to the result.

---

## Why this is a scaffold (and how to complete it in one paste)

OpenAlex's API is **network-blocked from the analysis session** (the session's egress proxy
returns `403` on connect — the same wall that blocks Kaggle and BigQuery). But unlike those,
**OpenAlex needs no credential.** So the real data is a one-step, keyless fetch you run from
any browser and paste back. The runner **refuses to run** (exit 3) until real data is present
— it cannot fabricate.

**Fetch the reproducible fixed-seed sample** (same URL → same 50 works, every time):

```
https://api.openalex.org/works?sample=50&seed=42&per-page=50&select=id,display_name,cited_by_count,referenced_works_count,publication_year,primary_topic
```

Paste its JSON `results` array into `data/openalex_cohort_frozen.json`, set `frozen_at` and
`status:"REAL"`, re-hash into the manifest, and run. A **random** sample (not top-cited) is
used deliberately, so the heavy tail is a real property of the population, not a selection
artifact.

---

## What is pre-registered (gates fixed before data)

- **H1 — citation concentration.** Forward citations (`cited_by_count`, a D_dec / engagement
  proxy) are heavy-tailed — the classic bibliometric power law. *PASS if mean > median AND
  p90/median ≥ 2.0.*
- **H2 — reference effort.** The reference-list length (`referenced_works_count`, a D_enc
  encoding-effort proxy) is heavy-tailed. *PASS if mean > median AND p90/median ≥ 2.0.*
- **H3 — coupling UNTESTABLE (for now), and honestly the most promising substrate.** References
  (D_enc) and citations (D_dec) are *both* present here — closer to a real `E = U·D` two-hop
  than any prior cohort — but a single snapshot has no non-circular per-work **survival**
  outcome (E). So coupling is declared **untestable** here, exactly like the bioRxiv/PubMed/
  Kaggle/GitHub H3. A *longitudinal* OpenAlex pull (references → citations → 5-year citation
  survival) could someday give a genuine non-circular coupling trial — flagged as future work,
  not claimed.

## What this does and does not claim

- ✅ Tests the **structural signature** (citation + reference concentration) LISM predicts, on
  real OpenAlex data.
- ❌ Does **not** claim the `E = U·D` coupling (declared untestable on a snapshot).
- The validated LISM coupling cohorts remain yeast / GitHub-issue-τ_v / knowledge / swarm.

## Files

```
openalex-lism/
  prereg/openalex_prereg.json      pre-registration spec (locked BEFORE data)
  prereg/MANIFEST.sha256.json      spec hash locked; fixture hash pending real data
  data/openalex_cohort_frozen.json placeholder (UNFILLED until you paste the real sample)
  openalex_lism.py                 the runner (refuses to fabricate; stdlib, offline)
  README.md
```

Layer-1, offline, `$0`. Data source: OpenAlex (open, keyless; CC0).
