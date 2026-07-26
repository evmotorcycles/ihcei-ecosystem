# Status: nothing is falling apart — and here is exactly why 992 failed

*Written in response to: "it is as if things were not committed, everything is falling
apart." **It isn't.** A clean `git worktree` of HEAD reproduces **59/59 suites**, every
named system included. What changed is not the science — it is that an audit was added
which distinguishes "we have a conclusion" from "we committed the data." That audit
found a **packaging bug that has now bitten twice**, and this document fixes the class.*

```
bash reproduce_all.sh        # 59/59 ALL GREEN, from a clean checkout, offline, $0
```

---

## 1. Why GitHub 992 is not reproducible — settled by the logs you supplied

The CI logs for run **74994532125** answer this definitively. The relevant lines:

```
[fetch] 992 unique repositories
[save]  per-repo data -> govphys_quadratic_results.csv  (N=992)
N=992  fail=750  surv=242
VIF(D_enc,D_dec)=1.02  (gate <5.0)   r=+0.141
PRIMARY dAIC(quad-lin)=-3.48  perm z=+9.32
Third Law: tau_fail=50.61 tau_surv=19.76
VERDICT: QUADRATIC_DISCONFIRMED
```

Then the upload step:

```
Artifact name: govphys-quadratic-results
Uploaded bytes 59283
SHA256 digest of uploaded artifact zip is 43d7419141d7c9e774f71c001e269e52d46c71a1dca8abd50e6232e9e7f90a01
```

**So the science ran, correctly, and produced the data.** The analysis is real: 992
repositories fetched, 750 failed / 242 survived, VIF 1.02, quadratic disconfirmed,
τ_v 50.61 d vs 19.76 d.

### The actual cause — one line

`govphys_quadratic_results.csv` **is line 7 of `.gitignore`.**

So the per-repo rows were written to the CI runner's disk, uploaded as a 59 KB
artifact, and then **discarded** — the filename could never enter the repository. The
workflow-run artifact has since expired (the run now returns **404**), so those exact
rows are **unrecoverable**.

> **This is a packaging failure, not a scientific one.** Nobody faked anything; nobody
> ran it wrong. Evidence was produced and then thrown away by a `.gitignore` line.

**Does this weaken LISM? Narrowly, yes — honestly stated:** the N = 992 cohort cannot
be cited as offline-reproducible, so LISM's linear-coupling claim rests on the two
substrates that *are* committed (yeast + PyPI). It does **not** mean the 992 result was
wrong. **To close it:** re-run the pre-registered fetch and commit the CSV. That is the
whole remedy.

## 2. The same bug bit the yeast labels — and CI caught it

Identical failure mode, caught days earlier: `scer_essential_orfs.txt` sat on disk while
listed in `.gitignore`. Every *local* run passed; a clean checkout had nothing. My first
"gap closed" claim was **false**, CI failed it, and the audit's original finding was
**correct**. The labels are now genuinely committed (404 KB) and the gap is closed for
real.

## 3. The root-cause fix (new)

`cohort-audit/test_no_ignored_evidence.py` makes this class of bug impossible to repeat
silently:

- any gitignored `.csv`/`.json`/`.txt` must be a **declared gap** carrying a **reason
  and a remedy** — adding one is a deliberate, reviewable act;
- the yeast labels are asserted to be **git-tracked**, not merely present on disk
  (`git ls-files --error-unmatch`), which is precisely the check that would have caught
  the false closure immediately.

## 4. Full re-test — every system you named, from a clean checkout

All run from `git worktree add /tmp/verify HEAD` — nothing from a working directory.

| System | Suite | Result |
|---|---|:--:|
| **IHCEI / NERE kernel** | `ihcei_v3` kernel, fast/deep seam, 4D bias engine | ✅ 3/3 |
| **HELM** | core + parity + prereg lock + contribution | ✅ PASS |
| **Page Code** | permission table + change audit | ✅ PASS |
| **Echo (database / hash-chain)** | hash-chain + scam taxonomy | ✅ PASS |
| **Cross-stack (agency internet)** | integration + GitHub pilot | ✅ PASS |
| **Novora suite** | suite + screen + UI + backend | ✅ PASS |
| **Novora PAGES** | confidence / abstain (agency + security) | ✅ PASS |
| **EI** | whole contract on real GitHub data (17 checks) + adversarial | ✅ 2/2 |
| **EI-LLM** | 8-model unit suite + field harness (real 22-repo cohort) | ✅ 2/2 |
| **Gorilla Problem (Russell)** | control test | ✅ PASS |
| **Hinton "Grand Canyon"** | 8 tools | ✅ PASS |
| **EI + 8 models** | Hinton & Russell, pre-registered | ✅ PASS |
| **Digital swarms** | HF swarm E=U·D + revocation τ_v; stage-3 fidelity N ≥ 434 | ✅ 2/2 |
| **Deterministic F_out = F_eval** | generator/evaluator decoupling law | ✅ PASS |
| **Adversarial kernel** | ∂F_out/∂F_gen = 0 — rejects hallucinated gains | ✅ PASS |
| **Agency algorithm / methodology** | discovery, substrates, constitution | ✅ 3/3 |
| **LMD** | spacetime-verdict matrix + vs 4 emergent-spacetime theories | ✅ 2/2 |
| **Substrates: GitHub / HF / PubMed / bioRxiv** | agency-substrates, biomedical-agency, biorxiv/pubmed/github-lism | ✅ all |
| **Cohort audit + gap closure + evidence guard** | ledger, closure, root-cause guard | ✅ 3/3 |
| **Sovereign bank** | decoupled underwriting, 2/4 (B1 falsified) | ✅ locked |

**Total: 59/59 suites, 0 failures.**

## 5. What the audit actually changed (and why it looks like decay)

Nothing regressed. What was added is a **distinction** that did not exist before:

| Before | After |
|---|---|
| "we have four cohorts" | 2 backed by committed data · 1 unrecoverable gap · 2 simulations |
| "quadratic AUC 0.47, anti-predictive" | that figure is a **non-converged solver artifact** (in-sample 0.4275); converged quadratic = 0.591, still beaten by linear 0.666 |
| "popularity carries zero information" | **refuted** — stars discriminate default at AUC 0.74 on a non-circular outcome |

Losing claims that were never backed is not the framework weakening; it is the
framework **becoming checkable**. The two substrates that survived (yeast N = 4,825,
VIF 1.0026, linear 0.666 > quadratic 0.591; PyPI 434-package graph, quadratic Δ 0.000)
are independent, non-circular, and reproduce offline from committed data.

## 6. If you want 992 back

One command's worth of work, and it is worth doing:

1. Remove `govphys_quadratic_results.csv` from `.gitignore` (or write to `data/`).
2. Re-run the pre-registered fetch (`govphys_quadratic_prereg_test.py`, spec
   `cac34f44…`, needs a `GITHUB_TOKEN`; the original took ~47 minutes).
3. **Commit the CSV.** The evidence guard will then let the cohort be cited.

Until then the gap stays declared, with its cause and remedy attached wherever it is
quoted.

---

*Reproduce: `bash reproduce_all.sh` → 59/59. Provenance merkle root and every
pre-registration hash are committed; `exit 0` means "reproduces including its gaps,
nulls and missed predictions" — not "every claim held."*
