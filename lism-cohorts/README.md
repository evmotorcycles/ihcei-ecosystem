# LISM `E = U·D` — four-cohort cross-substrate meta-test (pre-registered)

One locked question, asked across four heterogeneous substrates:
**does the accelerating quadratic `E = U·D²` add anything over the linear law
`E = U·D` wherever a valid (channel-intact) test is possible — and does a
sequential multi-hop digital swarm inherit that linear coupling, or escape it?**

`D = D_enc · D_dec` — two multiplicative fidelity hops (encode × decode).

```
python3 lism-cohorts/meta_lism.py       # stdlib only, offline, $0
python3 -m pytest -q lism-cohorts/test_meta_lism.py
```

## The four cohorts

| | Substrate | N | Verdict | How this run checks it |
|---|---|--:|---|---|
| **A** | Yeast interactome (STRING v12) | 4825 | linear adequate; VIF 1.003 (channel intact) | attest committed refs; `repro/reproduce_yeast.py` recomputes VIF from raw STRING |
| **B** | GitHub repositories (pre-registered) | 992 | **QUADRATIC DISCONFIRMED**; linear AUC ~0.73, quad CV AUC ~0.59 | **live** re-hash of the prereg spec == archived CI hash `cac34f44…` |
| **C** | Knowledge / Stack Exchange (Barakah) | 793 | linear adequate; no curvature (LRT p~1); **effect weak** | attest committed `SE_BARAKAH_RESULTS.md`; `se_barakah_test.py` |
| **D** | Digital swarm (dependency tree) | 500 | **linear wins** R² 0.93>0.90; decay r=−0.887 (0.84→0.01 / 39 hops) | **live** re-simulation, seeded, stdlib |

**Meta-verdict:** linear `E = U·D` adequate in **4/4** channel-intact cohorts;
the accelerating quadratic gains nothing where a valid test was possible; the
multi-hop digital swarm **inherits** the law rather than escaping it.

## Two cohorts are recomputed *live* in this runner

- **Cohort D (swarm)** is re-simulated from a seed every run — `R²(E~U·D) > R²(E~(U·D)²)`
  and `corr(depth, D) < −0.5` are reproduced, not read from a summary.
- **Cohort B (GitHub)** has its pre-registration spec re-hashed from source; it must
  equal the archived CI hash `cac34f44…`, attesting the N=992 verdict.

The other two (yeast, knowledge) are attested from committed provenance, each with
its own live-recompute script that `reproduce_all.sh` already exercises
(`repro/test_reproduce.py` recomputes the yeast VIF and re-hashes the GitHub arm).

## The benefit of nulls and negative results

The runner **emits a negatives register verbatim from the locked spec.** These are
not failures to hide — they are what proves the harness is not grading its own
homework:

- **GitHub quadratic "AUC 0.41 / below chance"** was a numerical artifact of a
  non-converging fit; corrected to CV ~0.59, and the over-strong "anti-predictive"
  wording was **retracted**. The no-quadratic conclusion still stands.
- **D_gap curvature** fell *inside* the 1000-permutation null envelope (seed 42) →
  reported **inconclusive**, not spun either way.
- **Kubernetes D_gap sensor** null (p = 0.735) → reported as a null.
- **Clinical / contract / legislative** channels: collapsed VIF or empty failing
  region → reported **untestable**, never counted as support.
- **Validation Stage 1** (evasive coercion): fast-mode **null** (recall 0.25,
  Brier 0.30) → the deep on-device NPU model stays load-bearing and unproven.
- **Knowledge cohort effect is weak** (AUC ~0.58, newest-first time confound) — the
  *linear-vs-quadratic* verdict is what's claimed, not a strong predictor.

A correctly-reported null or an untestable channel does **not** turn the suite red.
Only a dishonest relabel or a silent post-hoc change would. That is the epistemic
firewall working — the same discipline the NYC-sidewalk reproduction demanded.

## Layer discipline

Everything above is **Layer-1** — a measured model-selection verdict. Interpretations
about Hinton's "digital swarms", AI scaling limits, or the physics of information
decay are **Layer-3** and are deliberately kept out of the locked decision rule.
