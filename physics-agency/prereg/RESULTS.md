# Pre-registered results — the Telemetric Metric numerical validation

**Pre-registration was locked BEFORE the run.** The spec `telemetric_prereg.json`
(parameters, seeds, and pass thresholds) was fingerprinted under a canonical
SHA-256 and committed; the runner reads thresholds only from the frozen spec and
cannot change them.

```
locked spec SHA-256 : 011b7b53e9df4d12cc54e7689639209b82a282b3199b88f4d9ce481e6fdb7e3c
lock intact at run  : YES (spec unchanged since lock)
```

Reproduce the whole audited run:

```
node physics-agency/prereg/audit.mjs        # agency + attestation + epistemic audit
python3 physics-agency/prereg/run.py        # the locked run alone   (pytest: prereg 2/2)
```

## Outcome — PASS (3/3) against the locked thresholds

| ID | Pre-registered claim | Locked pass condition | Measured | Verdict |
|---|---|---|---|---|
| **H1** | `d=√(κ·τ_rt)` is a genuine metric | `triangle_violations == 0` | **0 / 8640** | PASS |
| **H2** | scaling `d ∝ 1/√coupling` | `|slope+0.5|<0.02 ∧ R²>0.999` | slope **−0.5000**, R²=**1.00000** | PASS |
| **H3** (primary) | discriminator: emergent moves, null frozen | `emergentΔ>0.05 ∧ nullΔ<1e-9` | emergent **0.9425**, null **0** | PASS |

**Symmetric null:** had any endpoint missed its locked threshold, this file would
report a NULL with no post-hoc adjustment. It did not; the result is a clean PASS.

## Provenance — audited on-device by the Novora stack ($0, no network)

| Stage | Tool | Result |
|---|---|---|
| Pre-registration lock | Echo `sha256(canonical)` | spec hash = manifest lock ✓ (tamper-evident) |
| Agency bounds | **Page Code** | runner may `write results.json` (**allow**) but `write telemetric_prereg.json` / `MANIFEST` (**deny**) — it cannot rewrite its own pre-registration |
| Attestation | **Echo Database** | prereg + results hash-chained, chain intact ✓, Merkle root published *(receipts regenerate each run — see `provenance.json` for the current IDs)* |
| Independent audit | **EI** | results-claim verdict **PASS** (p=0.14), release, ledger intact ✓ |
| Epistemic audit of the abstract | **NERE / PAGES** | score **1.0 Solid**, `METHODOLOGY_PRESENT`, attack **none**, cert `PGS-72D2F48D` |

Full machine-readable provenance: `physics-agency/prereg/provenance.json`.

## Scope (the firewall, restated)

This is a **Layer-1 numerical** validation of the equation's internal consistency
and the experiment's discriminating logic. The **physical experiment is proposed,
not performed.** The **Layer-3** claim — that physical spacetime is emergent — is
**neither claimed nor proven**; it is exactly what the proposed bench experiment
would test. What is established here is that the equation is well-posed, obeys its
predicted scaling, and yields a decisive discriminator — i.e., it is *ready to be
handed to a lab with the tools to prove or disprove it.*
