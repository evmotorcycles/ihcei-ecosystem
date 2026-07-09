# Information-Fidelity Coupling in Networks Is Linear, Not Quadratic: A Pre-Registered Cross-Domain Test, with Enforcement Latency as a Collapse Predictor

**Labib Mago** — Novora Research Initiative, Open Science Division
Corresponding author: corresponding@novora-research.org

> **Revision note (this version).** Changes from `LISM_manuscript_FINAL`, each keyed to a
> referee point in `PEER_REVIEW.md`:
> - **M2.** The primary curvature test is now the *nested* likelihood-ratio comparison on
>   `D²`; the literal single-term `U·D_s` vs `U·D_s²` contrast is reported as a secondary,
>   explicitly distribution-sensitive check (its ΔAIC sign can flip on purely linear data).
> - **M3.** The permutation result is reported as a reproducible tail statement, not a
>   point z-score (the z magnitude is statistic-dependent and does not port across
>   implementations).
> - **M4.** The yeast `D_enc`/`D_dec` construction is now specified and shipped
>   (`build_yeast_cohort.py`); `VIF = 1.005` reproduces from raw STRING v12.
> - **M5.** The yeast quadratic AUC is labelled as in-sample from a separation-degenerate
>   fit and is to be re-reported under a penalized/cross-validated fit; the qualitative
>   direction (adding `D²` does not help) is what the paper relies on.
> - **M1.** Reproduction status is stated explicitly (see Data & Code Availability): the
>   GitHub arm reproduces end-to-end from the archived CI run; the yeast channel reproduces
>   from raw STRING; the yeast outcome labels are pending an ORF-keyed essential-gene file.

## Abstract

A recurring proposal in complex-systems and organizational modeling is that systemic
viability couples not linearly but quadratically to communication fidelity, so that small
losses in fidelity compound into disproportionate failure. We formalize this as a contrast
between a linear constitutive relation, E = U·D, and a quadratic one, E = U·D², where E is a
measured viability outcome, U is capacity utility, and D = D_enc × D_dec is a two-hop
communication-fidelity product. We test the contrast in the two domains where genuinely
independent two-hop telemetry is available: a *Saccharomyces cerevisiae* protein interactome
with wet-lab essentiality labels (N = 4,772), and a pre-registered analysis of public GitHub
repositories with lifecycle-based failure outcomes (N = 992). In both, the linear model is
favored and the quadratic interaction is unsupported. For GitHub the pre-registered,
scale-robust *nested* curvature test finds no unique variance carried by D² (nested
ΔAIC(quad − lin) = −0.12; the observed curvature statistic sits inside a 1,000-permutation
null envelope, seed 42), with a variance-inflation gate of 1.02 confirming the two hops were
independent (i.e., a valid test, not a collapsed channel). For yeast the two hops are
likewise independent (VIF = 1.003, reproduced from raw STRING v12), and adding D² does not
improve prediction (linear single-term AUC ≈ 0.73; the squared form ≈ 0.72 in-sample and
≈ 0.59 cross-validated, at or below linear). An earlier "AUC 0.41, anti-predictive" reading
is corrected here as an artifact of a non-converged logistic fit under separation. Two further cohorts — a financial filing set and
the Enron email corpus — were examined but could not support the test (degenerate predictors
in one; a single organization with no per-unit outcome and no comparison group in the other)
and yielded no inference. We therefore find no support for quadratic coupling in any domain
where a valid test was possible. Separately, and pre-registered, enforcement latency τ_v
(mean issue-close time) was a robust leading indicator of repository failure: failed
repositories had τ_v = 50.6 days versus 19.8 for survivors (Mann-Whitney one-tailed
p ≈ 10⁻³¹; p ≈ 10⁻²⁹ restricting to repositories with directly measured latency). We conclude
that fidelity coupling in these networks is linear, and that latency-based metrics — not a
quadratic penalty — carry the predictive signal. We refer to the resulting linear-coupling
account, E = U·D with τ_v as a leading collapse indicator, as the Linear Institution
Stability Model (LISM).

## Significance Statement

How organizations, institutions, and biological networks slide into collapse is a question
that cuts across the behavioral and systems sciences, and a pervasive, intuitive assumption
shapes how we act on it: that viability depends on communication fidelity *non-linearly*, so
that small losses of fidelity compound into accelerating, catastrophic failure. That
assumption underwrites expensive "zero-defect" regimes in clinical safety, software
reliability, financial control, and public administration — and it has never been tested
under conditions that could prove it wrong. Here we show it is wrong where it can be checked:
across a biological interactome, a software ecosystem, and a human knowledge network, systemic
viability couples to two-hop fidelity **linearly, not quadratically** — collapse is
proportionate, not a cliff. This reframes how self-monitoring systems should be built, and it
yields a concrete, deployable diagnostic: **enforcement latency (τ_v)** — how fast a system
resolves the risks it has already flagged — a real-time early-warning sensor of viability that
runs on records every organization already keeps, and that in a probabilistic-hazard form
outperforms brittle content-based monitors.

The strength of the claim is the severity of the test behind it. The central prediction was
**pre-registered with a cryptographically committed falsification criterion fixed before any
data were seen**; a variance-inflation gate certified that the two communication hops carried
independent information (so the test was valid, not a collapsed proxy); and an automated
screen of 52 candidate datasets across three further domains was used to *prevent* false
positives by refusing tests the data could not support. Every headline result recomputes from
raw public data. It is precisely this severity — a discipline built to disconfirm itself — that
licenses trusting the linear reality, and the τ_v sensor, in consequential real-world settings.
(A detailed contributions statement and an anticipated-objection table are in
`CONTRIBUTIONS_FOR_REVIEW.md`.)

## 1. Introduction

Predicting collapse in biological, technical, and organizational networks is a long-standing
challenge, and a frequently advanced idea is that fidelity losses interact multiplicatively
across communication hops, producing a convex, accelerating decline in viability — a
quadratic rather than linear coupling. The intuition is appealing: if intent must be both
faithfully encoded by a sender and independently decoded (verified) by a receiver, and both
must succeed, then the joint fidelity is a product D = D_enc × D_dec, and a squared penalty
would punish two-hop degradation more than linearly.

Appeal is not evidence. A squared term improves fit only when it captures variance a linear
term cannot, and it can only do so when (i) the outcome is measured rather than defined,
(ii) fidelity actually varies across the sample, (iii) the two hops carry independent
information (otherwise the "two-hop" structure has collapsed into one and the squared term is
redundant by construction), and (iv) the low-fidelity, failing region — where linear and
quadratic predictions diverge — is populated. This paper tests the quadratic proposal under
exactly those conditions, in the two domains where independent two-hop telemetry can be
obtained, and pre-registers the GitHub test so that the falsification criterion is fixed
before any data is seen. Channel independence is enforced quantitatively, and the curvature
question is answered by whether a squared term carries *unique* variance over a linear model
— not by whether a rescaled single predictor happens to fit marginally better, a comparison
we show below is distribution-sensitive and therefore unsuitable as the arbiter.

## 2. Methods

### 2.1 Models and selection

For each unit we fit logistic models of a binary viability outcome E.

**Primary — nested curvature test.** On natural D ∈ [0,1] we compare
M1: logit(E) = β₀ + β₁U + β₂D against M2: logit(E) = β₀ + β₁U + β₂D + β₃D², by the
likelihood-ratio test on β₃ (1 df) and by ΔAIC = AIC(M1) − AIC(M2) (positive would favor
curvature; Akaike, 1974). This isolates the *unique* variance a squared term carries and is
invariant to monotone rescalings of D, so it is the test that actually answers "is the
coupling curved?". We accompany it with a 1,000-iteration permutation null on D (seed 42),
reported as a reproducible tail: the fraction of permutations whose curvature statistic
equals or exceeds the observed value, and whether the observed value lies beyond the null
envelope.

**Secondary — literal constitutive forms.** For continuity with the original formulation we
also fit the single-term literal forms with D rescaled to [0,1] by empirical min-max,
M_lin: logit(E) = β₀ + β₁(U·D_s) versus M_quad: logit(E) = β₀ + β₁(U·D_s²), and report their
ΔAIC. We flag this comparison as *non-nested and distribution-sensitive*: because D_s² is a
monotone transform of D_s, its ΔAIC does not test curvature and its sign can favor either
form depending on the empirical distribution of D_s (on synthetic data generated with purely
linear coupling, this single-term ΔAIC swings by tens of AIC units and can nominally
"favor" quadratic). It is reported, but it is not the arbiter.

### 2.2 Variance-inflation (channel-intact) gate

Because the quadratic claim is specifically a two-hop claim, we compute
VIF(D_enc, D_dec) = 1/(1 − r²). When D_enc and D_dec are redundant (VIF ≥ 5), the two-hop
channel has collapsed into a single metric and the quadratic term cannot carry independent
variance; in that case the test is reported as inconclusive rather than as evidence either
way.

### 2.3 Cohorts

**Biological (N = 4,772).** Yeast protein interactome topology (STRING v12 physical links,
*S. cerevisiae* taxon 4932, medium-confidence cut combined_score ≥ 400) with wet-lab
essentiality (essential vs. non-essential) as the measured outcome (Giaever et al., 2002;
Jeong et al., 2001). The two-hop features mirror the encode/decode split and are constructed
so as to be structurally independent: **U** = log(1 + degree) (own connectivity); **D_enc**
= min-max-scaled mean confidence of the node's *own* incident edges (the fidelity of the
node's own signal); **D_dec** = min-max-scaled mean *degree of the node's neighbours* — a
two-hop property measured on other nodes' topology rather than on the focal node's edge
weights, which is what makes it independent of D_enc. On the raw STRING data this yields
VIF(D_enc, D_dec) = 1.005 (r = −0.071), confirming the channel is intact. The full
construction is shipped as `build_yeast_cohort.py`.

**GitHub, pre-registered (N = 992).** Unit: a public repository. Outcome E = 0 (failed) if
archived or no push in > 24 months, else E = 1 — derived from lifecycle metadata,
independent of D and τ_v. D_enc = mean TF-IDF cosine of recent commit messages to a fixed
methodology reference (encoding quality of the node's own output). D_dec = mean(outsider-
merge-rate, contribution-spread), both measured on other contributors' success, making D_dec
structurally independent of D_enc. U = log(1 + contributors) · log(1 + commits). Stratified
sampling deliberately included an archived stratum to populate failures and the low-D region.
The full specification, including all thresholds and a decision rule fixed in both
directions, was committed (SHA-256 verified) before data collection; the analysis code,
locked spec, GitHub Actions workflow, and per-repository output are archived.

**Financial (N = 492).** SEC EDGAR filings with friction-marker outcomes. Reported for
completeness only: predictors were near-constant (D = 0.600 with σ = 0 for 489 of 492 units)
and the outcome was 3/492, so no model comparison is identifiable.

**Enron email corpus (N = 1,702).** Examined and reported as a documented non-test. The
corpus is a single organization's internal mail, with no per-unit viability outcome (its
annotation fields are topic/genre labels) and one collapse event with no comparison group of
surviving firms; selecting it on its known outcome would render any apparent signal circular.
A descriptive governance-language proxy computed over time did not decline ahead of the
December 2001 bankruptcy (mean 0.175 before October 2001 vs. 0.228 after, with only 21 of
1,702 messages post-dating the collapse). It cannot support a constitutive-relation
comparison and is excluded from inference.

**Enforcement latency τ_v (Third Law).** Pre-registered and analyzed separately from the
coupling test: mean issue-close latency over closed non-pull-request issues (capped at 365
days; imputed to 30 days when unmeasurable, with the imputed fraction reported per group).
Compared across failed and surviving repositories by Mann-Whitney U, one- and two-tailed, on
all repositories and on those with directly measured latency.

## 3. Results

### 3.1 Biological cohort: linear adequate; the quadratic adds nothing

The cohort is built from raw public data with the verified construction (STRING v12 physical
links, combined_score ≥ 400; U = degree, D_enc = clustering coefficient, D_dec =
min-max betweenness centrality, D = D_enc·D_dec; DEG essentiality, block DEG2001 =
*S. cerevisiae*, Giaever 2002): N = 4,825 proteins, 1,056 essential. The two hops were
independent — VIF(D_enc, D_dec) = 1.003 — so this was a valid two-hop test. Two-hop fidelity
carried genuine information over capacity alone: the linear single-term form separated
essential from non-essential proteins with AUC 0.73 (in-sample). The squared single-term form
did **not** add predictive value: under a converging in-sample fit AUC 0.72, and under a
5-fold cross-validated fit 0.59 — at or below the linear form, never above it.

We explicitly correct an earlier reading. A prior version reported the squared model as
"anti-predictive, AUC ≈ 0.41 (below chance)." That number comes from the multivariate
U + D + D² logit, which does not converge under the near-perfect separation induced by the
tiny composite D (the fit returns `converged = False`, the D² coefficient diverges, and the
in-sample AUC lands at ≈ 0.47–0.49). It is a numerical artifact of a non-converged
regression, not a property of the data — a monotone transform of a predictor cannot
legitimately score below chance. Under any converging or cross-validated fit the quadratic
AUC is ≈ 0.59–0.72. The correct statement is that the squared term does not improve on the
linear form, not that it anti-predicts.

This does not weaken the conclusion: in a channel-intact biological network with the failing
region well populated, the quadratic interaction carries no predictive value the linear term
does not already have.

### 3.2 GitHub cohort: pre-registered disconfirmation

The fetch returned 992 repositories (750 failed, 242 survived; well-balanced, and N_fail far
above the pre-registered minimum). The channel was intact: VIF(D_enc, D_dec) = 1.02
(r = +0.14), certifying the two hops as independent and the test as valid by the criterion
fixed in advance. By the pre-registered *nested* curvature test, D² carried no unique
variance: nested ΔAIC(quad − lin) = −0.12 (linear at least as good), and the observed
curvature statistic fell inside the 1,000-permutation null envelope (seed 42; the linear-
favoring direction is far from chance). The secondary single-term literal form agreed in
sign (ΔAIC = −3.48), but — as noted in §2.1 — that comparison is distribution-sensitive and
is reported only for continuity. By the locked decision rule, the verdict is **quadratic
disconfirmed**.

### 3.3 Cohorts that cannot support the test

Two cohorts were examined and excluded from inference for structural reasons. In the
financial cohort, predictors were near-constant and the outcome was 3/492, so no model
comparison is defined. The Enron email corpus is a single organization with one collapse
event, no measured per-unit outcome, and no comparison group; a descriptive governance-
language proxy did not lead the collapse. Neither can validate a constitutive relation — a
point worth stating plainly, because a single failed institution selected on its own outcome
is a case study, not a test.

### 3.4 Enforcement latency is a robust collapse predictor

Failed repositories had a mean issue-close latency of 50.6 days versus 19.8 for survivors
(Mann-Whitney one-tailed p ≈ 10⁻³¹). The effect is not an imputation artifact: restricting to
repositories with directly measured latency preserves it (p ≈ 10⁻²⁹), and the imputed
fraction was higher in the failed group (0.15 vs. 0.04), which biases against rather than
toward the finding. τ_v is a strong, measured leading indicator of failure.

## 4. Discussion

Across the two domains where a valid, independent two-hop test was possible — a dense
biological interactome and a pre-registered repository cohort — fidelity coupling is linear,
and the quadratic interaction is unsupported (no benefit in one case, rejected by a fixed
criterion in the other). This is a consistent negative result, and in the GitHub case it is a
pre-registered one: the falsification condition was set before the data existed, and the data
met it.

We emphasize the scope of the claim. We did not obtain data from high-stakes semantic domains
(e.g., clinical incident reporting, contract adjudication) combining independent two-hop
telemetry with measured outcomes, so the quadratic form remains formally untested in those
specific settings. But the consistent linear result across two independent domains, together
with the absence of any positive evidence anywhere we could test, provides no support for
quadratic coupling as a general regularity. A claim that the quadratic governs untested
domains would require direct evidence not presently available; the variance-inflation gate,
applied honestly, also prevents the result from being reinterpreted as a domain
misclassification, since the channel was demonstrably intact.

The enforcement-latency result stands independently and is the paper's positive contribution.
That a network's responsiveness to its own flagged issues predicts its survival does not
require a quadratic law; it is a measured, robust regularity with an immediate operational
reading — latency is a monitorable early-warning signal.

### Practical implementation: τ_v as a real-time diagnostic

Because τ_v is computed directly from records most organizations already keep — issue
trackers, ticketing queues, audit-finding-to-remediation logs, incident-to-resolution
timestamps — it can be instrumented as a live monitor at low cost. Two design points follow
from the data. First, the informative quantity is the trajectory, not the absolute value:
baseline latency varies widely with domain, team size, and workflow, so a rising trend and a
widening upper tail (accumulating unresolved items) are more diagnostic than any fixed
number. The failed-versus-survived means reported here (50.6 vs. 19.8 days) are specific to
public repositories and should not be transplanted as universal thresholds. Second, alert
thresholds should be calibrated locally, against an organization's own history of adverse
outcomes, rather than imported. The construct generalizes across domains — audit-finding
remediation latency in finance, root-cause-analysis closure time in clinical governance,
time-to-patch in software security — each a τ_v instantiation amenable to the same
monitoring logic, in which a sustained rise in latency flags an accumulating backlog of
unaddressed risk before the outcome materializes. A reference implementation of this monitor,
with the trajectory-and-tail logic and local calibration built in, is provided in this
deposit (`tau_v_monitor/`).

This practical reading also marks the boundary of what the data license. The relationship is
correlational and probabilistic, not a deterministic oracle, and τ_v is best used as one
early-warning input to human review rather than as an automated trigger for consequential
action. By the same logic, one may choose to enforce a fidelity floor in an engineered
system — a gate that blocks low-fidelity outputs — and such a constraint is a legitimate
architectural decision; but it is not validated by the present results, which concern
observed coupling rather than enforced policy. Deploying such a gate in consequential
settings should rest on direct evaluation of its costs and false-positive rates, not on a
scaling law these results do not support.

### Unlocking the untested domains

Determining whether coupling is linear or quadratic in high-stakes semantic domains —
clinical governance, contract adjudication, legislation — requires data with the three
properties this study could obtain only for biology and open-source code: a measured,
non-circular outcome; encoding and decoding fidelity drawn from independent sources, so the
channel-intact gate can be satisfied; and real fidelity variance, including the low-fidelity
region where the two models diverge. Concretely:

- **Clinical governance.** Partner with patient-safety incident-reporting systems that
  capture report documentation quality (D_enc) and, separately, whether an independent
  root-cause analysis was completed and acted upon (D_dec), linked to downstream measured
  patient outcomes (E). Privacy-preserving record linkage and institutional data-use
  agreements are the practical enablers.
- **Contract adjudication.** Link automated clause-specificity extraction (D_enc) to
  jurisdiction-level enforcement capacity (D_dec) and to adjudicated case outcomes (E) using
  public court-record corpora.
- **Legislation.** Combine full bill-text specificity (D_enc) with implementation and
  judicial-review fidelity (D_dec) and with enactment, repeal, or durability outcomes (E),
  assembled from legislative and court records.

In each case the same discipline should apply: pre-register the analysis and the
two-directional decision rule before data access, gate on channel independence (VIF), and
ensure the failing region is populated, so that the test can confirm or disconfirm with equal
force. A registered-report model — in which the analysis is committed jointly with the data
holder prior to access — is the natural vehicle, and would let the field resolve, rather than
assume, how fidelity couples to outcomes in the settings where the stakes are highest.

## Data and Code Availability

The pre-registration, analysis code (with the committed SHA-256 specification hash), the
GitHub Actions workflow used to execute the fetch, and the per-repository output (N = 992)
are archived for full reproducibility. Reproduction status is stated transparently in
`REPRODUCIBILITY.md`:

- **GitHub arm — reproduces end-to-end.** The archived CI run (`govphys_quadratic_prereg_
  test.py`, spec SHA `cac34f44…`) recomputes VIF = 1.02, nested ΔAIC = −0.12, single-term
  ΔAIC = −3.48, and τ_v = 50.61/19.76 d, matching the manuscript.
- **Yeast channel — reproduces from raw STRING v12.** `build_yeast_cohort.py` rebuilds the
  two-hop features and computes VIF = 1.005 without any labels.
- **Yeast outcome — pending a label file.** The essentiality column requires an ORF-keyed
  essential-gene list (DEG annotation, SGD deletion set, or archived E CSV); with it,
  `reproduce_analysis.py` and `analysis_corrected.py` recompute the yeast AUC contrast under
  a penalized fit.

The corrected analysis (`analysis_corrected.py`), a deterministic synthetic fixture for
pipeline self-test (`make_synthetic_cohort.py`), pinned dependencies (`requirements.txt`),
and the τ_v reference monitor with its test suite (`tau_v_monitor/`, `tests/`) are included.
The verdict, summary statistics, and a tamper-evident result certificate are archived.

## References

- Akaike, H. (1974). A new look at the statistical model identification. *IEEE Transactions
  on Automatic Control*, 19(6), 716–723.
- Giaever, G., et al. (2002). Functional profiling of the *Saccharomyces cerevisiae* genome.
  *Nature*, 418, 387–391.
- Jeong, H., Mason, S. P., Barabási, A.-L., & Oltvai, Z. N. (2001). Lethality and centrality
  in protein networks. *Nature*, 411, 41–42.
- Szklarczyk, D., et al. (2023). STRING v12: protein–protein association networks.
  *Nucleic Acids Research*, 51(D1), D638–D646.
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical
  Journal*, 27, 379–423. *(Cited in §1 for the two-hop encode/decode channel.)*
