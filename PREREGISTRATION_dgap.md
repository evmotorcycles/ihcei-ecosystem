# Pre-registration — NERE D_gap Sensor, Spec v3.1

**Registered spec SHA-256 (of the docstring in `dgap_actions_sensor_v3.py`):**

    7a74ea544c3e40e4ce81fe1490273e07e9f74458a8d73de465c9bec9a8e17a46

The hash is COMPUTED at runtime from the module docstring, never asserted.
Any file whose docstring does not hash to the value above is not the
registered specification, whatever it claims.

**Discovery sample (exploratory, already observed):** microsoft/vscode,
closed-PR pages 1-39, fetched 2026-07-04. Human-only exploratory result:
coef +2.12, 95% CI [-0.21, 4.46], p = 0.074. Pooled result (Spec v2,
hash ded09320...): coef +1.97, p = 0.0012, partially carried by a
dependabot lexical artifact.

**Confirmatory sample (registered, unseen at registration):**
kubernetes/kubernetes closed PRs, or microsoft/vscode pages >= 51.

**Primary decision rule (human cohort only):** Logit(E==0 ~ const + D_gap),
within-cohort MinMax scaling, VIF < 5.0 gate, power floor N >= 500 with
>= 50 failures. VALIDATED iff p < 0.05 AND coef > 0. All outcomes reported.
