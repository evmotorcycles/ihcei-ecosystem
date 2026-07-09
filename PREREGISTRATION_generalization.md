# Pre-Registration — LISM Generalization: Stage 1 Registered Report Protocol

**Goal.** Transition the Linear Institution Stability Model (LISM) from two
completed two-hop tests (yeast interactome; pre-registered GitHub cohort) to a
generalized, substrate-independent theory of institutional survival, by testing
the linear-vs-quadratic constitutive relation in **three high-stakes semantic
domains**: (1) clinical governance, (2) contract adjudication, (3) legislation.

**Status.** Locked specification template. For each domain, instantiate this
protocol, freeze the operational definitions and thresholds, and commit the
SHA-256 printed by the analysis harness **before any outcome-linked data is
accessed**. Confirm, disconfirm, and inconclusive are all reportable.

**Why a template, not a run.** The datasets that satisfy the invariants below do
not exist as convenient downloads (a Kaggle/portal sweep returns non-tests — see
§6). Each domain requires a data-holder partnership; this protocol is what is
committed *jointly with the holder prior to access*, per the Registered Report
model.

---

## 1. Hypotheses (identical across domains; only operationalization changes)

- **H0 (linear):** systemic viability couples linearly to two-hop fidelity,
  `E = U · D`, with `D = D_enc · D_dec`.
- **H1 (quadratic):** viability couples quadratically, `E = U · D²` — a convex,
  accelerating penalty on two-hop fidelity loss.

The pre-registered test discriminates H0 from H1 **only where a valid two-hop
channel exists** (see the three invariants, §2).

## 2. The three hard invariants (eligibility gates — checked before inference)

A dataset is **eligible** for a coupling verdict only if all three hold. Any
failure ⇒ the domain is reported as a **documented non-test**, never a null.

| # | Invariant | Operational check | Fails like |
|---|---|---|---|
| I1 | **Genuine channel independence** | `D_enc` and `D_dec` drawn from *different data sources / actors*; `VIF(D_enc, D_dec) = 1/(1−r²) < 5` | Enron (one hop by construction); the ~468k-bill legislative corpus (placeholder D_dec) |
| I2 | **Populated failing region** | real fidelity variance incl. the low-`D` region; `σ(D) > 0`, and ≥ 10% of units in the bottom `D` quartile; outcome not degenerate (`N_fail ≥ 100`) | SEC EDGAR (D = 0.600, σ = 0; 3/492 outcome) |
| I3 | **Measured, non-circular outcome** | `E` empirically observed downstream, not defined by the communication protocol itself | any outcome derived from the same text that produced `D` |

These are the same firewalls that forced the exclusion of the SEC EDGAR and
Enron cohorts from the original paper; here they are pre-committed gates.

## 3. Per-domain operationalization (independent sources are mandatory)

### 3.1 Clinical governance (patient safety → outcomes)
- **D_enc** — documentation quality/thoroughness of patient-safety incident
  reports (e.g., structured completeness score of the incident narrative).
  *Source A:* the incident-reporting system.
- **D_dec** — whether an **independent** root-cause analysis (RCA) was completed
  and its corrective actions verified as implemented. *Source B:* the
  quality/safety RCA registry — a different system and different actors than
  the reporters. (This independence is what satisfies I1.)
- **E** — downstream, objectively measured patient outcome on the linked care
  pathway (e.g., 30-day mortality, readmission, harm-event recurrence).
  *Source C:* the clinical outcomes / EHR record.
- **U** — unit capacity (caseload, staffing-adjusted throughput).
- **Unit:** one incident-linked care episode.
- **Privacy:** privacy-preserving record linkage (hashed/tokenized identifiers),
  a data-use agreement, HIPAA Safe-Harbor or Expert-Determination de-identification;
  **no PHI enters the model** — analysis runs on de-identified derived features only.

### 3.2 Contract adjudication (legal enforcement)
- **D_enc** — clause specificity / structural precision extracted from raw
  contract text by a semantic parser (defined terms, obligations, remedies,
  cross-references per clause). *Source A:* the contract corpus.
- **D_dec** — jurisdiction-level enforcement capacity / judicial reliability
  (court throughput, reversal rates, enforcement-index) — measured on the
  **courts**, not the contract. *Source B:* judiciary statistics. (Satisfies I1.)
- **E** — adjudicated outcome: contractual intent sustained vs. breached/nullified.
  *Source C:* case dispositions.
- **U** — matter capacity (contract value / complexity, party resources).
- **Unit:** one adjudicated contract dispute.

### 3.3 Legislation (governance & policy durability)
- **D_enc** — full-text specificity / statutory clarity of enacted bills
  (the specificity features already implemented in `legislation_coupling_test.py`:
  defined-term, cross-reference, numeric-threshold, mandate densities).
  *Source A:* the statute text (Congress.gov).
- **D_dec** — downstream **administrative implementation fidelity** (rulemaking
  completion, agency compliance) **and** judicial-review alignment — measured on
  agencies/courts. *Source B:* the Federal Register / regulations.gov / court
  dockets. This is the hop the earlier ~468k-bill "dead-channel" test lacked;
  supplying it non-degenerately is the crux (I1).
- **E** — long-term durability: enactment, amendment, repeal, or statutory
  survival over a fixed horizon. *Source C:* legislative + court records.
- **U** — scope/capacity (appropriation size, affected population).
- **Unit:** one enacted statute.

## 4. Models & analysis (inherits the M2/M3 corrections)

- **PRIMARY — nested curvature test.** On natural `D ∈ [0,1]`:
  `M1: logit(E)=β₀+β₁U+β₂D` vs `M2: +β₃D²`; likelihood-ratio test on `β₃`
  (1 df) and `ΔAIC = AIC(M1) − AIC(M2)`. This isolates the unique variance a
  squared term carries and is scale-robust. Fit with a **penalized (Firth/L2)**
  logistic to avoid the separation artifact that produced the spurious "AUC 0.41"
  in the yeast arm.
- **SECONDARY — literal forms** `U·D_s` vs `U·D_s²` (min-max `D`), reported as
  *distribution-sensitive* and non-arbitral.
- **Permutation null** — 1,000 permutations of `D` (seed fixed in the frozen
  spec), reported as a **reproducible tail** (fraction ≥ observed; beyond-envelope
  flag), not a point z.
- **Channel gate** — `VIF(D_enc, D_dec)` reported first; `≥ 5 ⇒ INCONCLUSIVE`.
- **τ_v (Third Law), reported separately** — the domain's enforcement-latency
  analogue (RCA-closure time; remediation lag; time-to-implementation) vs `E`,
  Mann-Whitney one- and two-tailed, imputed fraction reported per group.

## 5. Power analysis & decision rule (locked before access)

- **Power.** Simulation-based: under an assumed linear DGP and under a quadratic
  DGP with a plausible curvature effect size (β₃ giving a 0.05 AUC gap), compute
  the N at which the nested LRT achieves 0.80 power at α = 0.05. Require the
  eligible sample to meet that N with `N_fail ≥ 100` (I2). Record the power curve
  in the frozen spec.
- **Two-directional verdict (thresholds locked):**

| Verdict | Condition |
|---|---|
| **QUADRATIC SUPPORTED** | eligible (I1–I3) **and** nested `ΔAIC > 10` **and** permutation tail p < 0.001 **and** β₃ > 0 (convex) |
| **QUADRATIC DISCONFIRMED** | eligible **and** nested `ΔAIC ≤ 0` (linear at least as good) |
| **INCONCLUSIVE** | any invariant fails, or `0 < ΔAIC ≤ 10`, or underpowered |

Note the **sign requirement**: the yeast arm showed significant but *negative*
(saturating) curvature — the opposite of the accelerating penalty — so "supported"
requires β₃ **> 0**, not merely significant.

## 6. Dataset eligibility rubric (the screen, before any locking)

Applied to every candidate dataset (`kaggle_dataset_screen.py` operationalizes this):

1. Does it contain **two fidelity signals from independent sources/actors**? (else I1 fails)
2. Is the outcome **measured downstream**, not derived from the same text as `D_enc`? (else I3 fails)
3. Is there **real low-fidelity variance** and `N_fail ≥ 100`? (else I2 fails)
4. Can the two hops be **linked at the unit level** (record linkage feasible)?

A "no" on 1–3 ⇒ **non-test**, reported as such. Convenient public datasets
(Kaggle, open portals) almost always fail #1 or #2 — they are single-source or
their "outcome" is protocol-defined. This is expected and is itself informative.

## 7. Registered Report Stage 1 structure & locking

1. Freeze this instantiated protocol (definitions, thresholds, power, seed).
2. Run `sha256sum PREREGISTRATION_generalization.<domain>.md` and commit the hash
   in the same commit, **before** any outcome-linked access.
3. Obtain in-principle acceptance (IPA) from the data holder / journal on the
   Stage 1 plan.
4. Access data, run the frozen harness, report Stage 2 exactly as specified —
   including inconclusive and disconfirming outcomes, with equal prominence.

## 8. Ethics & governance

- Clinical: IRB/REC approval, HIPAA-compliant de-identification, DUA, minimum-
  necessary derived features, no re-identification attempts, secure enclave
  analysis. The model never sees PHI.
- Legal/legislative: public records; respect court-record access terms and any
  jurisdictional restrictions.
- All three: results are correlational and probabilistic — one input to human
  governance review, never an automated trigger for consequential action.

---

*This protocol inherits every correction from the completed arms: nested
curvature as primary (M2), reproducible permutation tail (M3), penalized fits
under separation (M5), and the VIF channel-intact gate. It is the disciplined
bridge from "linear in two domains" to "linear as a regularity of institutional
survival" — earned test by test, not assumed.*
