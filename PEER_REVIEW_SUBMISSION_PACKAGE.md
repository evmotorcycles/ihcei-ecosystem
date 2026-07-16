# LISM — Peer-Review Submission Package

*Everything an editor and referee need, in one place: target venue, a ready cover
letter, a submission-readiness checklist, the reviewer-defense matrix, the full
evidence inventory, and the plan for integrating the newest results into the
manuscript. Assembled to make acceptance a matter of judging the contribution, not
hunting for the parts.*

---

## 1. Target venue

- **Primary: *Nature Human Behaviour*.** Fit: multidisciplinary computational
  social science / complex-network theory / organizational behaviour; strong
  editorial preference for pre-registration, transparency, and constructive
  falsification (Mass Replication Initiative). LISM is a pre-registered,
  cross-substrate falsification with a deployable instrument — squarely in scope.
- **Secondary: *PNAS*** (Physical/Social Sciences interdisciplinary), or *Nature
  Communications* if a broader-scope home is preferred.
- **Format:** Article with a Registered-Report-style "Unlocking the Untested
  Domains" section (the four blueprints) as the forward program.

*Scope note for the editor:* this paper is not a clinical or molecular study
(those belong in *Nature Medicine* / *Neuroscience*); it is a structural result
about how human-agent coordination networks couple fidelity to viability. See
`LISM_AND_ALZHEIMERS.md` for the explicit layer separation that keeps the scope
claim safe.

## 2. Cover letter (ready to send)

> Dear Editor,
>
> We submit *"Information-Fidelity Coupling in Networks Is Linear, Not Quadratic:
> A Pre-Registered Cross-Domain Test, with Enforcement Latency as a Collapse
> Predictor"* for consideration at *Nature Human Behaviour*.
>
> A widespread intuition — that systemic viability couples to communication
> fidelity **quadratically**, so small fidelity losses compound into accelerating
> collapse — underwrites costly "zero-defect" policy across medicine, software,
> finance, and governance. It had never been tested under conditions that could
> falsify it. We pre-registered such a test (criterion SHA-256–locked before data)
> and ran it in every domain where an independent two-hop measurement exists. The
> quadratic is disconfirmed; a **linear law, E = U·D**, holds across three
> independent channel-intact substrates — a yeast interactome (N = 4,825,
> VIF = 1.003), a pre-registered GitHub cohort (N = 992, VIF = 1.02), and a live
> Stack Exchange network (N = 793, VIF = 1.08).
>
> From the same program we validate a cheap, deployable early-warning instrument —
> **enforcement latency τ_v** — which separates failed from surviving software
> repositories (50.6 d vs 19.8 d, p ≈ 10⁻³¹) and is computable from timestamps
> organizations already keep. We also **correct a prior artifact of our own** (a
> non-converged-fit "quadratic anti-predictive AUC"), and we report our
> disconfirmations and non-tests (52 convenience datasets, 0 eligible) as
> first-class results.
>
> The contribution is threefold: a corrected prior, a usable sensor, and — above
> all — a **reusable, anti-circular methodology** whose value we quantify directly
> (it cuts fabricated-law false discovery from 24% to 8% on a pure null, and from
> 100%/36% to 0% on collinear/sparse trap cohorts, while still recovering real
> effects). Every headline number recomputes from raw public data with pinned
> dependencies, checksums, and an independent referee report included.
>
> We believe this meets the journal's bar for rigor, transparency, and
> significance to the study of collective human systems. We have no competing
> interests and the work is not under consideration elsewhere.
>
> Sincerely, Labib Mago (Novora Research Initiative, Open Science Division)

## 3. Submission-readiness checklist

| Item | Status | Location |
|---|---|---|
| Main manuscript | ✅ revised | `LISM_manuscript_REVISED.md` |
| Significance statement (NHB-tuned) | ✅ | manuscript abstract + `CONTRIBUTIONS_FOR_REVIEW.md` |
| Pre-registration (locked criterion) | ✅ | `PREREGISTRATION*.md` |
| Independent referee report + responses | ✅ | `PEER_REVIEW.md` |
| Primary data reproducibility | ✅ | `build_yeast_cohort.py`, CI cohort, `REPRODUCIBILITY.md` |
| τ_v validation (locked + live) | ✅ | `TAUV_VALIDATION.md`, `nere_experiment/TAUV_4COHORT_RESULTS.md` |
| Methodology quantified (firewall MC) | ✅ NEW | `nere_experiment/METHODOLOGY_EXPERIMENT.md` |
| "Unlocking Untested Domains" (blueprints) | ✅ | `UNLOCKING_UNTESTED_DOMAINS.md` + `blueprint_conformance.py` |
| Reviewer-defense matrix | ✅ | Section 4 below |
| Deposit / DOI package | ✅ | `README_DEPOSIT.md`, `zenodo_metadata.json`, `CITATION.cff`, `SHA256SUMS.txt` |
| Data & code availability statement | ✅ | manuscript + this file §5 |
| Scope guard (medical/other layers) | ✅ NEW | `LISM_AND_ALZHEIMERS.md` |
| Yeast ORF-keyed labels + M5 CV re-report | ✅ RESOLVED | `data/yeast/scer_essential_orfs.txt`, `M5_CV_REREPORT.md` |
| Blueprint Stage-1 power analysis | ✅ NEW | `BLUEPRINT_POWER_RESULTS.md`, `blueprint_power_sim.py` |
| **Pending before submission** | ✅ none | (optional only: GITHUB_TOKEN for a fleet-scale τ_v figure) |

## 4. Reviewer-defense matrix

| Likely objection | Response | In-deposit evidence |
|---|---|---|
| "A null result — so what?" | Pre-registered, cross-domain, **constructive** (replaces the claim); corrects our own prior artifact (M5). | `PREREGISTRATION*.md`, `PEER_REVIEW.md` |
| "Only digital/biological; not general." | Three channel-intact substrates + one-hop legislation; high-stakes domains bounded honestly and given pre-specified, VIF-passing blueprints. | `UNLOCKING_UNTESTED_DOMAINS.md`, `blueprint_conformance.py` (7/7 pass, 2/2 broken rejected) |
| "Datasets cherry-picked / circular." | VIF channel-intact gate + non-circular measured outcomes; two independent searches show 0 eligible convenient datasets — no cherry-picking possible; the firewall's value is **measured**. | `THREE_DOMAIN_SWEEP_RESULTS.md`, `METHODOLOGY_EXPERIMENT.md` |
| "τ_v is just size/centrality/recency." | τ_v survives measured-only restriction and imputation biased against it; the new 4-cohort ordered test shows τ_v tracks **enforcement capacity, not age** (ρ = 0.739, p = 0.006; 15.9× intact-vs-zombie, p = 0.002), and localizes the one archival artifact. | `TAUV_4COHORT_RESULTS.md`, `tau_v_monitor/` |
| "Effect sizes modest (SE AUC ~0.6)." | Reported plainly; the *linear-vs-quadratic* verdict (the tested object) is robust to it; time-confound named. | manuscript, `SE_BARAKAH_RESULTS.md` |
| "Over-claims beyond its layer (e.g., medicine)." | Explicit layer separation: LISM instruments the coordination pipeline, not the biology; τ_v as a research-governance sensor, analogy labelled Layer-3. | `LISM_AND_ALZHEIMERS.md` |
| "Religious/interpretive framing undermines rigor." | Strictly firewalled: Layer 1 (tested) vs Layer 3 (interpretive prior, not dataset-adjudicated); empirical contribution stands without it. | `LISM_CONTRIBUTION.md` §5, `FLOOR_RETIREMENT.md` |
| "Is the methodology actually doing anything?" | Yes, and it's quantified: FDR 24→8% (null), 100→0% (collinear), 36→0% (separation), while recovering real linear (96%) and quadratic (53%). | `METHODOLOGY_EXPERIMENT.md`, `methodology_experiment.py` |

## 5. Evidence inventory (data & code availability)

**Validated cohorts (Layer-1):**
- Yeast interactome — N = 4,825, VIF = 1.003 — `build_yeast_cohort.py` (raw STRING v12/DEG/BioGRID).
- GitHub lifecycle — N = 992, VIF = 1.02, ΔAIC = −3.48 — archived CI run.
- Stack Overflow knowledge network — N = 793, VIF = 1.08.
- Legislation (one-hop, live) — directionally linear — `LEGISLATION_REAL_EXPERIMENT.md`.

**Sensor (τ_v):**
- Locked cohort: failed 50.6 d vs survived 19.8 d, p ≈ 10⁻³¹.
- Live 18-repo autopsy: `TAUV_VALIDATION.md` (naive-label confounds diagnosed).
- **New** ordered 4-cohort test: `TAUV_4COHORT_RESULTS.md` (ρ = 0.739, p = 0.006).
- Reference monitor: `tau_v_monitor/` (13 tests).

**Methodology (quantified):**
- Firewall Monte Carlo: `METHODOLOGY_EXPERIMENT.md` / `methodology_experiment.py`.
- NERE rhetorical firewall + stack suite (60/60): `nere_experiment/`.
- LISM × IHCEI integration (13/13): `lism_ihcei_integration.py`.

**Forward program:**
- Four Registered-Report blueprints + machine-checkable conformance test:
  `UNLOCKING_UNTESTED_DOMAINS.md`, `blueprint_conformance.py`.

All scripts are deterministic under stated seeds; live components use the existing
GitHub proxy in `project-6q4gj` (no additional API required).

## 6. Manuscript integration plan (where the new results go)

1. **Results → τ_v subsection:** add the ordered 4-cohort test (`TAUV_4COHORT_RESULTS.md`)
   as confirmatory live evidence that τ_v tracks enforcement capacity, not age;
   cite the archival bulk-close artifact as the pre-stated, localized confound.
2. **New "Methods as contribution" subsection:** fold in the firewall Monte Carlo
   (`METHODOLOGY_EXPERIMENT.md`) — the quantified answer to "does the discipline
   matter?" This is the strongest reviewer-facing asset; give it a figure.
3. **Discussion → "Unlocking the Untested Domains":** the four blueprints +
   conformance test, framed as Stage-1 Registered-Report templates.
4. **Scope paragraph:** import the layer separation from `LISM_AND_ALZHEIMERS.md`
   to pre-empt the over-claim objection.
5. **Data & Code Availability:** the inventory in §5 above.

---

*Recommendation: submit to *Nature Human Behaviour* once the yeast ORF-keyed label
file lands (the only ⏳ item). The optional GITHUB_TOKEN would upgrade the live τ_v
figure from 16–18 repos to a fleet-scale distribution, but is not required for
submission.*
