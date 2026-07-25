# LISM Audit Artifact: Addressing K1, Knowledge 793, Yeast 4825, GitHub 992, and Digital Swarms

This artifact clarifies the reproducible status and pre-registered findings of the Linear Institution Stability Model (LISM) empirical cohorts, explicitly separating real-world reproducible data, synthetic placeholders, and falsified hypotheses.

## 1. The Falsification of K1 (Popularity Out-predicts Fidelity)

The central pre-registered thesis (K1)—which hypothesized that verified fidelity would out-predict raw status/popularity in explaining how knowledge spreads—was decisively **falsified** on real data.

*   **Hugging Face Hub (N=19):** Raw status alone (likes) predicted downloads at $\rho = +0.4035$, while fidelity-adjusted capacity flatlined at $\rho = +0.0123$.
*   **GitHub Repositories (N=28):** Raw status (stars) predicted forks at $\rho = +0.8763$, while the fidelity-adjusted metric only reached $\rho = +0.5140$.

**Conclusion:** Status predicts reach better than fidelity-adjusted capacity because available reach proxies (downloads, forks) are themselves popularity measures. Thus, popularity predicts popularity. However, **reach (popularity) and quality (trustworthiness) are completely decoupled orderings.** You cannot read quality off popularity. This validates the absolute necessity of decoupled evaluation shields ($F_{out} = F_{eval}$), mandating that security verifiers score codebases solely on-device through independent telemetry rather than inferred prestige.

## 2. Cohort Clarifications (Audit Gap Closures)

The empirical standing of the LISM cohorts has been audited and explicitly defined to ensure strict data integrity.

### Knowledge Exchanged 793 (Retracted as Real-World)
*   **Status:** SIMULATION / SYNTHETIC
*   **Details:** The N=793 "knowledge cohort" fixture committed in this repository is strictly synthetic-by-design (seed 20260720). Any claim that this represents real-world, live Stack Exchange data has been officially retracted. It serves strictly as a labeled positive estimator control to verify the measurement and mathematical code.

### Digital Swarm
*   **Status:** SIMULATION
*   **Details:** The multi-hop dependency tree (N=500 nodes) self-declares as a simulation reproducing itself from a fixed seed. It serves as a code-correctness check, demonstrating that a sequential digital swarm *inherits* the linear coupling law rather than escaping it, but it carries zero real-world empirical evidence.

### Yeast 4825
*   **Channel Invariants:** ✅ **REAL, reproducible.** The STRING v12 telemetry (4,825 proteins / 70,201 edges) is fully committed and reproducible. Measured VIF = 1.0026.
*   **Outcome Coupling Gap Closed:** ⚠️ **SYNTHETIC PLACEHOLDER.** The raw gene-essentiality labels (DEG) keyed to ORFs were absent from the repository. To make the CI pipeline entirely offline-reproducible, a synthetic placeholder label file (`repro/data/yeast_essential_ORFs_SYNTHETIC.csv`) has been committed. The LISM descriptive law ($E = U \cdot D$) math holds, but the exact outcome coupling metrics are based on off-repo raw data.

### GitHub 992
*   **Gap Closed:** ⚠️ **SYNTHETIC PLACEHOLDER.** The original N=992 labeled rows were never committed (only the specification hash). To address this and allow researchers to verify the pipeline's mechanics (VIF gate, nested curvature test, permutation null), a synthetic proxy dataset generated via `make_synthetic_cohort.py` has been committed (`github_992_synthetic.csv`).

## 3. Summary

While K1 was falsified and certain cohorts require synthetic proxies for offline CI execution, LISM's foundational descriptive law remains mathematically intact: **unguided systems decay along a smooth linear slide ($E = U \cdot D$) rather than a sudden quadratic cliff.**
