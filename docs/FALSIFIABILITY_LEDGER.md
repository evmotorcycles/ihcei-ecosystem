# GT v18.0 Falsifiability Ledger

**Single source of truth for all empirical results.**
Updated after each completed test. Never retroactively edited.

---

## Coupling cohorts — descriptive question

**Pre-committed decision rule** (locked before any cohort ran):
- QUADRATIC SUPPORTED: ΔAIC > 10 AND permutation z > 3
- QUADRATIC DISCONFIRMED: ΔAIC ≤ 0
- INCONCLUSIVE: VIF ≥ 5, or 0 < ΔAIC ≤ 10

### Yeast interactome (N = 4,772)

| Field | Value |
|---|---|
| Domain | Protein-protein interaction network, yeast |
| N | 4,772 nodes |
| VIF | 1.003 (channel intact) |
| ΔAIC (lin − quad) | −48.2 |
| Permutation z | (strongly linear) |
| **Verdict** | **QUADRATIC DISCONFIRMED** |
| Date | 2025 |
| Notes | Clean channel, large N, decisive margin |

### GitHub repositories (N = 992) — pre-registered

| Field | Value |
|---|---|
| Domain | Open-source code repositories |
| N | 992 |
| VIF | 1.02 (channel intact) |
| ΔAIC (lin − quad) | −3.48 |
| Permutation z | — |
| **Verdict** | **QUADRATIC DISCONFIRMED** |
| Date | 2025 |
| Notes | Pre-registered; τ_v (enforcement latency) confirmed as robust predictor of repository failure (p ≈ 10⁻³¹). Reported separately — unaffected by AIC comparison. |

### Statutory domain — US Congressional Acts (N = 365)

| Field | Value |
|---|---|
| Domain | US public laws (104th–114th Congress, 1995–2015) |
| N | 365 usable (N_fail = 100, gate cleared) |
| D_enc | log1p(n_distinct_USC_sections_cited), normalized |
| D_dec | log1p(n_SCOTUS_cases + n_EOs per congress × policy topic), normalized |
| D_dec source | US Policy Agendas Project: Supreme Court Cases + Executive Orders datasets |
| VIF | 1.0021 (r = 0.0455, p = 0.39; channel intact) |
| AIC(M_lin) | 343.49 |
| AIC(M_quad) | 353.52 |
| ΔAIC (lin − quad) | −10.03 |
| Permutation z | −11.55 (p = 1.000) |
| Direction | Negative (artifact: citation count measures structural reach, not completeness; SCOTUS/EO density measures policy salience, not fidelity) |
| **Verdict** | **QUADRATIC DISCONFIRMED** |
| Date | June 2026 |
| Notes | First test with a real two-hop operand. D_dec measured from genuine downstream institutional engagement data (10,236 SCOTUS cases, 4,831 EOs). VIF gate passed legitimately. Direction artifacts noted — do not change the AIC verdict. Previous synthetic-data run (np.random.seed(42)) was a pipeline self-test, not a measurement; all prior references to "ΔAIC = −19.89 statutory" referred to that synthetic output and are superseded by this real run. |

---

## Pilot — prescriptive question

**Pre-registration:** `docs/PREREGISTRATION.md`
**SHA-256 (commit before window):** `ffe6bf32c31a00445984a1e1c55d2dba82150a530967df856e5fdd9a9ea21cfd`

**Pre-committed decision rule:**
- EARNS ENFORCEMENT: sensitivity ≥ 0.60 AND FPR ≤ 0.20 AND net benefit beats all baselines AND ROC-AUC lower 95% CI > 0.70
- DOES NOT EARN ENFORCEMENT: FPR > 0.20 at operating point OR no net-benefit lift OR AUC 95% CI includes 0.50
- INCONCLUSIVE: N_adverse < 50 OR kernel uncomputable on > 10% of items

| Field | Value |
|---|---|
| Channel | Not yet selected |
| EGS gate | Not yet run |
| D_floor calibration | Not yet run |
| Window | Not yet open |
| N_adverse accrued | 0 |
| **Status** | **UNTESTED** |

The pilot tests a different question from the coupling cohorts. The coupling disconfirmation does not answer whether enforcing the D-floor helps. Neither does it contradict the pilot hypothesis. The two tracks are firewalled by design.

---

## Excluded domains (documented reasons)

| Domain | Reason for exclusion |
|---|---|
| Enron emails | Single organisation; no per-unit outcome variable |
| SEC financial corpus | Degenerate predictors |
| AI/ZEGL domain | Circular — outcome zero by construction |
| Synthetic statutory run (seed=42) | np.random data; pipeline self-test only |

---

*Last updated: June 2026*