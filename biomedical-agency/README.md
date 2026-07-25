# OQM as a case study: the four telemetry laws on real biomedical substrates

**One command:** `python3 biomedical-agency/biomedical_oqm.py` · stdlib · offline · `$0`

> ## ⚠ Epistemic firewall — read first
> **This is a methodology demonstration, not a clinical result.** The **measured layer**
> (Layer-1) is ordinary, checkable telemetry on real data: a protein-interaction network's
> collinearity, a bibliometric retraction distribution, a preprint publication-latency
> distribution, and a software-network allocation. The **biomedical mapping** (Layer-3) —
> *disease as a communication / routing failure* — is an **interpretive overlay** drawn from
> OQM used **strictly as a case study in governance logic**. **Nothing here diagnoses, treats,
> prevents, or cures any disease. It is not medical advice and makes no clinical claim.** The
> two layers are reported separately and stay separate.

This takes the **Organic Qurʾānic Methodology purely as a case study**, extracts its
**substrate-independent logic** (using only functional/engineering meanings — no cultural or
religious lexicon), and asks a single question: do the **four telemetry laws** that already
described software, physics-analog, and bibliometric substrates also describe **real
biological-network, clinical-bibliometric, and biomedical-software telemetry**? On four real,
frozen substrates — they do, with the honest limits stated.

---

## The extracted logic (no lexicon — just the functions)

| law | function | biomedical overlay (interpretation only) |
|---|---|---|
| **Law 1** two-hop yield + independence | `E = U·D_enc·D_dec`; legs must be independent (VIF ≈ 1) | non-redundant **dual-pathway** synergy vs redundant capacity |
| **Law 2** enforcement latency `τ_v` | latency of a system's self-correction loop | rising `τ_v` = slower self-correction = accumulating collapse risk |
| **Law 3** say-do dissonance `σ` | gap between surface claim and underlying data | **integrity early-warning** on a research field |
| **Law 4** triage under collapse | rescue below-floor nodes first | prioritize failing **medical-software** nodes to block cascade |

---

## Results — pre-registered B1–B4 (spec `7022c33b…`), all substrates real & frozen

### B1 — Law 1 independence, on the **real yeast interactome** ✓
STRING v12, *S. cerevisiae* (taxon 4932), **N = 4,825 proteins / 70,201 interactions**.
`U` = degree, `D_enc` = clustering coefficient, `D_dec` = min-max betweenness.
```
measured VIF(D_enc, D_dec) = 1.0026   (< 1.10 → the two fidelity hops are INDEPENDENT)
collinear control (D_dec := D_enc)    → VIF = ∞ → REJECTED
```
The two hops carry **genuinely independent** information (reproducing the known VIF ≈ 1.003),
so the two-hop product `E = U·D_enc·D_dec` is a **valid, non-degenerate** model on a real
biological network. *Overlay:* independent hops model a non-redundant dual-pathway (candidate
synergy); collinear hops are redundant. *Scope:* this tests **channel integrity only**, not a
drug-combination outcome — no essential-gene labels are committed.

### B2 — Law 3 integrity dissonance, on **real PubMed** ✓
8 real MeSH clinical fields, **12,690 retractions**.
```
most-retracted field 'Neoplasms' holds 50.7% of all retractions (uniform would be 12.5%) → concentrated
dissonance flag (rate > 2× median 0.00123) fires for: Anesthesia, Stem Cells, Neoplasms
```
The hidden retraction burden is **heavily concentrated**, and the dissonance detector fires on
the high-rate fields. *Overlay:* a field-level integrity early-warning. *Scope:* a bibliometric
signal — **not** a claim about any specific paper.

### B3 — Law 2 enforcement latency, on **real bioRxiv** ✓ (with an honest limit)
40 real preprints; `τ_v` = days from preprint to publication.
```
median 219 d · mean 358.4 d · p90 856 d · p90/p50 = 3.90 → heavy-tailed
```
The self-correction latency is **heavy-tailed** (mean ≫ median). *Honest limit:* the cohort is
**survivor-only** (all 40 were published), so a failed-vs-survivor separation is **not testable
here** — the tail is descriptive of the latency distribution, stated not overclaimed. *Overlay:*
rising `τ_v` = slower self-correction = accumulating collapse risk.

### B4 — Law 4 triage, on **real biomedical software** ✓ (small-N)
The 8 real bioinformatics-domain GitHub repos (7 below floor), allocated by the Constitutional
allocator (PR #107).
```
E: constitution 10.36 | capacity 7.97 | equal 7.80 | triage-prior 10.37   (N=8 caveat)
```
The triage allocator **beats naive allocation** (and effectively ties the prior triage allocator
at this tiny N). *Overlay:* prioritize below-floor medical-software nodes to prevent cascade
failure in a healthcare IT stack. *Scope:* N = 8 — a small-cohort demonstration, stated as such.

---

## The honest headline

The **same four telemetry laws** describe real **yeast-interactome**, **clinical-bibliometric**,
**preprint-latency**, and **biomedical-software** telemetry — the independence of two biological
fidelity hops (VIF ≈ 1.00), the concentration of a hidden integrity burden, the heavy tail of a
self-correction latency, and the triage advantage under multiplicative collapse. Where the data
cannot support a stronger claim (bioRxiv survivor-only; GitHub-biomed N = 8), that is said plainly.
**The value is the substrate-independent method and the firewall around it — not speed, not a
superhuman score, and emphatically not a clinical claim.**

## Files

```
biomedical-agency/
  prereg/biomed_prereg.json          spec (locked) — extracted logic + gates B1–B4 + firewall
  prereg/MANIFEST.sha256.json         spec + 4 real fixtures, hash-pinned
  build_yeast_features.py             REAL STRING v12 → frozen per-node feature table (needs networkx; ~85 s)
  data/yeast_channel_frozen.json      derived fixture (U, D_enc, D_dec per protein) + raw-STRING hash
  biomedical_oqm.py                   the stdlib runner (B1–B4)
  test_biomedical.py                  pytest guard (reads the frozen fixture; stdlib, fast)
  results_biomedical.json             emitted results
```

Layer-1 telemetry, offline, `$0`, deterministic. Methodology, not speed; nulls and limits
prioritized, not hidden. **Not a clinical result. Not medical advice.**
