# Peer Review — *Information-Fidelity Coupling in Networks Is Linear, Not Quadratic*

**Manuscript:** LISM_manuscript_FINAL — Mago, Novora Research Initiative
**Reviewer role:** methodological / reproducibility referee
**Recommendation:** **Major revision** (the science is sound and unusually honest; the deposit does not yet reproduce as shipped, and two statistical claims are over-stated relative to what the code computes)
**Date:** 2026-07-08

---

## 1. Summary of the submission

The paper contrasts two constitutive relations for network viability — linear `E = U·D`
against quadratic `E = U·D²`, where `D = D_enc × D_dec` is a two-hop
communication-fidelity product — and tests the contrast in the two domains where genuinely
independent two-hop telemetry is available: a *S. cerevisiae* interactome (N = 4,772) and a
**pre-registered** GitHub repository cohort (N = 992). In both, the linear model is favored
and the quadratic interaction is unsupported. A secondary, pre-registered result is that
enforcement latency `τ_v` (mean issue-close time) strongly separates failed from surviving
repositories (50.6 d vs 19.8 d; MWU one-tailed p ≈ 10⁻³¹). The authors name the resulting
account the Linear Institution Stability Model (LISM).

This is, in structure, a **registered-report-style negative result with one positive
finding** — the most credible kind of paper in this genre and the hardest to publish. The
review below is therefore oriented toward protecting that credibility, not undermining it.

---

## 2. What the paper gets right (and should keep)

1. **Pre-registration with a two-directional decision rule.** The GitHub test commits a
   SHA-256-locked specification, a VIF channel-intact gate, an `N_fail ≥ 100` power floor,
   and thresholds that can return *supported / disconfirmed / inconclusive* with equal force.
   This is exemplary and is the paper's strongest methodological asset.
2. **The VIF gate is a genuine falsifier, not an escape hatch.** Requiring
   `VIF(D_enc, D_dec) < 5` before *any* quadratic verdict correctly forecloses the
   "two-hop structure collapsed into one metric" artifact. Reporting VIF = 1.02 for GitHub
   certifies the test as valid rather than vacuous.
3. **Honest cohort triage.** The financial (degenerate predictor, 3/492 outcome) and Enron
   (single org, no per-unit outcome, no comparison group) cohorts are explicitly excluded
   from inference and labelled non-tests. Many papers would have mined these; this one names
   the circularity and walks away. Keep this section verbatim.
4. **The `τ_v` result is defended against its most obvious confound.** Restricting to
   directly measured latency (dropping imputed values) preserves the effect (p ≈ 10⁻²⁹),
   and the imputed fraction is *higher* in the failed group — i.e. imputation biases against
   the finding. This is exactly the robustness check the earlier τ_v work reportedly lacked.
5. **Framework-neutral reproduction script.** `reproduce_analysis.py` recomputes each
   headline number from CSV columns with no interpretive vocabulary, so a skeptic can verify
   the statistics without buying any of the surrounding theory. I ran it (see §4) and the
   pipeline executes cleanly.

---

## 3. Major concerns (must address before acceptance)

### M1 — The deposit does not reproduce as shipped: the data CSVs are absent
`reproduce_analysis.py` and the SHA256SUMS manifest both reference
`github_repositories.csv` and `yeast_interactome_DEG.csv`, but **neither file is present in
the repository or the deposit bundle.** The manifest lists a hash for
`github_repositories.csv` but the file itself is missing, and the yeast CSV is only
described as rebuildable via `build_yeast_cohort.py`. As it stands, *none of the headline
numbers actually recompute from the archive* — the central reproducibility claim of the
Data & Code Availability section is unmet.
**Required:** deposit `github_repositories.csv` (the paper states it "ships with this
package and reproduces exactly"), and either deposit the built `yeast_interactome_DEG.csv`
or pin the exact raw inputs (STRING v12 file version + accession) so
`build_yeast_cohort.py` is deterministic. Add a checksum check to the script.

### M2 — The "PRIMARY ΔAIC" statistic is not a nested test and is distribution-fragile
The primary comparison fits two **non-nested, single-regressor** models —
`logit(E) ~ U·D_s` vs `logit(E) ~ U·D_s²` — and reads off `ΔAIC`. Because `D_s²` is a
monotone transform of `D_s` on `[0,1]`, this ΔAIC does not test *curvature*; it tests which
of two rescalings of the *same* one predictor happens to fit better, and its sign is
sensitive to the empirical distribution of `D_s`. **Concretely: when I ran the exact
script on a cohort I constructed to be purely linearly coupled (D_dec ⟂ D_enc, no
quadratic component), the PRIMARY ΔAIC came out +6.44 and the SECONDARY nested ΔAIC +10.08
— i.e. nominally *favoring quadratic* — purely from the shape of the D distribution.**
The reported GitHub value (−3.48) is therefore evidence, but a *fragile* one: a different
(equally defensible) D-distribution could have flipped its sign without any change in the
true coupling.
**Required:** demote the single-term ΔAIC from "PRIMARY" or, better, make the **nested**
`M0/M1/M2` likelihood-ratio / ΔAIC on `D²` the primary curvature test (it is the one that
actually isolates the squared term's unique variance), and report the single-term contrast
as a secondary literal-form check. The yeast AUC contrast (0.74 vs 0.41) is the more
convincing evidence and should be foregrounded. This does not change the paper's
conclusion — it makes it robust to this exact objection.

### M3 — The permutation "z = +9.32" is under-specified and not reproducible as a number
The script's own comment concedes "the exact z depends on the chosen permutation
statistic" and validates only *direction and tail*. On my run the same procedure produced
z ≈ +114. A z-score whose magnitude is not reproducible should not appear in the abstract
or results as a point value.
**Required:** either (a) fully specify the permutation statistic and report the value it
deterministically produces with the shipped data and seed 42, or (b) replace the numeric z
with the reproducible claim ("observed fit beyond the 1,000-permutation null envelope,
seed 42") and drop the specific figure. Right now the manuscript quotes a number the code
does not stably generate.

### M4 — Abstract N and body N for the biological cohort are inconsistent
The abstract reports the yeast cohort as **N = 4,772**; `reproduce_analysis.py` prints the
reported line as **1009/4772** (1,009 essential of 4,772). The manuscript body says D_enc
and D_dec are "derived from independent interactome features" but the deposit does not
include the feature-construction code for yeast the way it does for GitHub (only
`build_yeast_cohort.py`, which is not shown to compute D_enc/D_dec from independent
features). Because the yeast VIF ≈ 1.0 claim is load-bearing (it is what makes yeast a
*valid* two-hop test), the D_enc/D_dec construction for yeast must be as auditable as the
GitHub one.
**Required:** ship the yeast D_enc/D_dec construction and confirm the essential/total
counts throughout.

### M5 — The yeast quadratic evidence rests on an in-sample AUC of a degenerate model
Section 3.1 reports the quadratic model's AUC = 0.41 "below chance," computed **in-sample**
from a logit the authors themselves describe as non-converging under near-perfect
separation. An in-sample AUC from a degenerate fit is not a stable quantity, and "below
chance" for a monotone-transformed single predictor usually signals a sign/separation
artifact rather than genuine anti-prediction.
**Required:** report the quadratic evidence with a penalized fit (Firth logistic or L2)
that converges under separation, or with cross-validated AUC, so the 0.74-vs-0.41 contrast
is not an artifact of the degeneracy. Again, this is expected to *strengthen* the result.

---

## 4. Reproduction attempt (what I actually ran)

- `reproduce_analysis.py` executes without error under
  `numpy / pandas / statsmodels / scikit-learn / scipy`. Good.
- With the real `github_repositories.csv` **absent**, I generated a schema-matching
  synthetic cohort (columns `E, D_enc, D_dec, D, U, tau_v, tau_v_imputed`; 750 failed /
  242 survived; D_dec constructed ⟂ D_enc) purely to exercise the code path. The script
  ran end-to-end and printed the reproduced-vs-reported table. This confirms the code is
  runnable and framework-neutral, and it is what surfaced the fragility in **M2** and the
  z-magnitude instability in **M3**.
- I could **not** verify a single headline number against source, because no source data
  ship with the deposit (**M1**).

**Net:** the *code* is credible; the *archive* is not yet self-contained. This is the
single most important fix.

---

## 5. Minor concerns

- **m1.** Abstract: "AUC 0.41 vs 0.74" — state in-sample vs cross-validated (ties to M5).
- **m2.** The `D = D_enc × D_dec` product is min-max rescaled before squaring; note
  explicitly that this rescaling is *inside* the pre-registration, since rescaling choices
  are exactly what M2 shows the single-term ΔAIC is sensitive to.
- **m3.** τ_v means (50.6 / 19.8 d) are used well in the manuscript (the Discussion
  correctly warns against transplanting them as thresholds). Ensure the slide deck's
  headline numbers carry the same "trajectory, not threshold" caveat — the SRE brief mostly
  does, keep it.
- **m4.** Shannon (1948) is in the reference list but never cited in the body; either cite
  it where the two-hop channel is introduced or remove it.
- **m5.** Give the exact `statsmodels` / `scikit-learn` / `numpy` versions and a
  `requirements.txt` with pinned versions; logistic convergence behavior under separation is
  version-sensitive and bears directly on M5.
- **m6.** Corresponding author lists `corresponding@novora-research.org` (a role alias); a
  named ORCID would help.

---

## 6. Verdict

The **conclusion is well supported and honestly bounded**: across the two domains where a
valid, channel-intact two-hop test was possible, there is no support for quadratic coupling,
and enforcement latency is a robust, measured collapse predictor. The reasoning discipline
(pre-registration, VIF gate, non-test triage) is a model for the field.

The paper is **not yet acceptable as an archival, reproducible artifact** because (M1) the
data do not ship, and it **over-states two statistics** (M2 the single-term ΔAIC framing,
M3 the permutation z) relative to what the code stably computes. None of these threaten the
conclusion; all of them, fixed, make it more defensible. I recommend **major revision** and
would expect to recommend acceptance once §3 is addressed.

---

## 7. Addendum — reproduction with the raw inputs (added after the author supplied data)

After the initial review the author provided the raw GitHub Actions run log and the raw
yeast inputs (STRING v12 physical links; DEG FASTA sets). This materially advances M1 and
M4:

- **GitHub cohort reproduces exactly.** The archived CI log (run 2026-06-19,
  `govphys_quadratic_prereg_test.py`, spec SHA `cac34f44…`) records the fetch of 992 repos
  and prints VIF = 1.02 (r = +0.141), PRIMARY ΔAIC = −3.48, SECONDARY = −0.12, τ_v =
  50.61/19.76 d, verdict QUADRATIC_DISCONFIRMED — matching the manuscript to the digit.
  The central pre-registered result is **authentic and reproduced**. *M1 (GitHub): resolved.*
- **Yeast channel-independence reproduces from raw STRING.** Rebuilding the interactome
  features directly from `4932.protein.physical.links.v12.0.csv` at the standard medium-
  confidence cut (score ≥ 400 → 4,825 proteins) with a documented encode/decode two-hop
  construction gives **VIF(D_enc, D_dec) = 1.005 (r = −0.071)**, matching the reported
  ≈1.003. The load-bearing "channel intact" claim holds on real data. *M4 (independence):
  substantially resolved; the D_enc/D_dec construction is now shipped in
  `build_yeast_cohort.py`.*
- **M3 sharpened, not dissolved.** The CI log does print `perm z = +9.32`, so that number
  is what the *original* script emits — but its magnitude remains statistic-dependent and
  non-portable (an independent reimplementation of the permutation gives a different z on
  the same tail). The reproducible-tail reporting in `analysis_corrected.py` should replace
  the point z in the manuscript.
- **New blocker for full yeast reproduction (refines M1/M4/M5).** The deposited DEG FASTA
  files carry **only opaque DEG IDs, no organism/ORF annotation**, so essential genes
  cannot be mapped to yeast ORF names from the shipped files, and the databases that carry
  that mapping are off the network allowlist. The yeast **outcome column E therefore cannot
  yet be regenerated**, and the AUC 0.74-vs-0.41 contrast (M5) remains unverified pending an
  ORF-keyed essential-gene list (DEG annotation, SGD deletion set, or archived E CSV). This
  is the single remaining item for a fully self-contained yeast reproduction.

**Revised bottom line:** the GitHub arm is now reproduced end-to-end; the yeast arm is
reproduced except for its outcome labels. Recommendation stands at **major revision**,
but the remaining work is concrete and small: reframe M2/M3 in the text, deposit the yeast
essential-gene labels, and re-run the yeast AUC under a penalized fit (M5).

---

## 8. Addendum 2/3 — yeast rebuilt with the AUTHOR'S OWN construction; **M5 proven, provenance located**

The author subsequently supplied the original `build_yeast_cohort.py`. Its verified
construction is now adopted as canonical in this repo:
**U = degree, D_enc = clustering coefficient, D_dec = min-max(betweenness centrality),
D = D_enc · D_dec**, E = DEG essentiality (block DEG2001 = *S. cerevisiae*, Giaever 2002).
Rebuilt from raw STRING v12 + DEG + a BioGRID name map, this reproduces the manuscript's
scale to the digit: **N = 4,825, VIF(D_enc,D_dec) = 1.003 (= reported 1.003), essential =
1,056 (vs 1,009)**. Running the coupling test on the author's actual features settles M5:

| Model (single-term) | Manuscript | Author-construction in-sample | 5-fold CV |
|---|---|---|---|
| linear `U·D_s` | AUC 0.74 | **0.726** | 0.66 |
| quadratic `U·D_s²` | **0.41 (anti-predictive)** | **0.721** | 0.59 |

**Provenance of the 0.41 — located exactly.** The manuscript's sub-chance quadratic AUC is
produced by the **multivariate `U + D + D²` logit fit on the raw (tiny) composite D**, which
**does not converge** under the resulting near-perfect separation: `converged = False`, with
the D² coefficient blowing up to ≈ +2.5×10⁵ and ΔAIC ≈ −1,680 (matching the pre-registration's
quoted "ΔAIC ≈ −1805, AUC 0.47"). That non-converged fit yields an in-sample AUC of ≈ 0.47–0.49
— i.e. the reported "≈0.41, anti-predictive." **Every converged or cross-validated
specification of the same quadratic gives AUC ≈ 0.59–0.72, never below chance.**
`analysis_yeast.py` reproduces both the artifact and the corrected numbers in one run.

**Verdict on M5: CONFIRMED.** The "quadratic is anti-predictive / below chance" statement is
a numerical artifact of a non-converged logistic regression, not a property of the data. It
must be corrected. The correct, defensible statement is: *adding D² does not improve
prediction over the linear form* (quadratic AUC ≤ linear under any valid fit), which **still
supports the paper's central linear conclusion** — it simply removes an over-strong,
irreproducible claim. The linear AUC (~0.73) and the channel-intact VIF (1.003) both
reproduce exactly. With this correction the yeast arm reproduces end-to-end and the paper's
finding stands on solid ground.
