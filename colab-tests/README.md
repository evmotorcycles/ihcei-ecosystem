# colab-tests — run elsewhere, verify here

A **cryptographic reproduction protocol** for the Novora / IHCEI stack. You (or anyone —
a reviewer, a partner, a lab) run a self-contained script in Google Colab; it prints a
`RESULTS_SHA256`; that hash is checked against a **pre-registered lock**. A match is
independent proof the deterministic core reproduces; a mismatch localises the divergence.

```bash
python3 colab-tests/colab_suite.py                 # run the suite (prints RESULTS_SHA256)
python3 colab-tests/verify_colab.py <hash-or-json> # check a returned result against the lock
python3 -m pytest -q colab-tests/test_colab.py     # the repo reproduces its own locked hash
```

- **Locked expectation:** `expected_results_sha256 = aebdd9b7723bf6c516283ebed15112f0227109ada7cb2e0bf9ced86464b56e51`
  (spec `591b99ef…`, in `prereg/`).
- **Colab cells:** `COLAB_NOTEBOOK.md`.

## How it stays honest across machines

The hash covers only **environment-stable** quantities:

- **Algebraically exact** — the LMD slope (−0.5) and R² (1.0) are graph-Laplacian identities,
  identical on any hardware. (Your Colab already returned `-0.500000 / 1.000000`.)
- **Integer counts** — e.g. 0 triangle-inequality violations.
- **Bit-exact pure-Python + hashlib** — LISM OLS, swarm decay, the Echo Merkle root, the τ_v
  Mann-Whitney U, and Hoffman FBT all use the standard-library Mersenne-Twister RNG and IEEE-754
  arithmetic, so they're identical across CPython everywhere.

Raw LMD **distances** carry harmless ~5th-decimal float noise across CPU/GPU/BLAS (your Colab:
`15.811416`; a numpy CPU: `15.811388`), so they are **displayed but excluded from the hash** —
otherwise a faithful run would falsely mismatch.

## The seven tests

| Test | Component(s) | What it proves |
|---|---|---|
| **T1** | LMD | ring-lattice coupler sweep → slope −0.5, R² 1.0 (emergent-distance signature) |
| **T2** | LMD | effective-resistance distance obeys the triangle inequality (a real metric) |
| **T3** | LISM | `E = U·D` linear beats quadratic on a seeded cohort |
| **T4** | swarm | multi-hop fidelity decays with depth |
| **T5** | Echo Database | hash-chain Merkle root is fixed; a one-record tamper changes it |
| **T6** | τ_v (IHCEI/NERE hazard monitor) | failed repos have higher enforcement latency; MWU separates |
| **T7** | Hoffman / EI | Fitness-Beats-Truth reproduced under selection |

## Honest scope

This suite covers the **deterministic, Python-portable core** (LMD, LISM, swarm, Echo Merkle,
τ_v, Hoffman). **HELM, PAGES, Page Code, Agency Internet, and the EI-LLM verifiers** use
JS-specific RNG and regex; they are verified in-repo with `node` via `reproduce_all.sh`, and a
Python port of their governance logic is a documented future addition here. We do **not** claim
this single suite covers every module — only the portable, cryptographically-checkable core.
