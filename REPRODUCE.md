# Reproduce everything — one command

**Run this from the repository root:**

```bash
bash reproduce_all.sh
```

No API keys. No network. Requires only `python3` (with `pytest`) and `node` (≥18).
Exit code `0` means every suite passed; non-zero prints which suite failed.

### Dependencies (one command)

```bash
pip install -r requirements.txt      # numpy pandas scipy statsmodels scikit-learn networkx pytest
```

Every heavy-dependency python test **skips gracefully** (never fails) if a library
is missing, so the stdlib-only arms reproduce on a bare interpreter. The node
suites need only `node ≥ 18` — no `npm install`.

> **Independent-reproducer note (addressing Jules's feedback).** The knowledge
> (Barakah / Stack Exchange) cohort previously required a *live* fetch through the
> Vercel SE proxy, so it could not be re-run offline. It now reproduces fully
> offline from a committed, deterministic fixture:
> `python3 repro/make_se_fixture.py && python3 se_barakah_test.py --json repro/data/se_fixture_barakah.json`
> (also run automatically by `repro/test_se_offline.py` inside `reproduce_all.sh`).
> The live `N=793` headline stays attested in `SE_BARAKAH_RESULTS.md`; the offline
> fixture reproduces the *verdict class* (channel-intact VIF≈1, LINEAR adequate on a
> no-D² ground truth) so the pipeline is not network-gated.

That single script runs **every test across the whole stack** — this is the
entrypoint any person, CI, or agent (Jules, Claude Code, etc.) should use. Latest
run: **23/23 suites green.**

## What it runs (by component)

| Component | Suite(s) | What it proves |
|---|---|---|
| **NERE / IHCEI** | `ihcei_v3/test_ihcei_nere_v3.py`, `test_deep_seam.py`, `test_four_d_bias.py`; `tests/test_tau_v_monitor.py` | probabilistic kernel + floor + corroboration gate; fast/deep parity; 4D bias engine; τ_v hazard monitor |
| **HELM** | `novora-helm/test/*.mjs` | on-device floor, scam armor, dark-pattern spotting, prereg lock, real-traffic contribution |
| **Page Code** | `page-code/pagecode.test.mjs` | stake-bounded permission table + change audit |
| **Echo Database** | `echo/echo.test.mjs`, `echo/scam_taxonomy.test.mjs` | append-only hash chain, Merkle proofs, tamper detection |
| **Agency Internet** | exercised in `page-code` + `russell-test` + `hinton-test` | bounded, revocable delegation grants |
| **Novora suite / PAGES** | `novora-suite/test/*.mjs` | 9-product screen schema + direction, PAGES grounding, keyless UI/backend endpoints |
| **EI** | `ei/ei.test.mjs` (17 checks on real GitHub data), `ei/ei_adversarial.test.mjs` (16 edge cases) | AUDIT · DELEGATE · DEVELOP · PROVE · HAZARD, non-suppressive, human-in-the-loop |
| **EI-LLM** | `ei-llm/ei-llm.test.mjs`, `ei-llm/field_test.mjs` | 8 verifier models, unit + field on the real 22-repo cohort |
| **Hinton's test** | `hinton-test/hinton_test.mjs` (+ `.test.mjs`) | Grand Canyon understanding test run through 8 tools (11/11) |
| **Russell's test** | `russell-test/russell_test.mjs` (+ `.test.mjs`) | Gorilla Problem: human stays sovereign as capability rises (7/7) |
| **EI + 8 models (Hinton & Russell)** | `ei-tests/ei_hinton_russell.mjs` (+ `.test.mjs`) | both tests run through the EI core and all 8 EI-LLM models, against a SHA-256-locked pre-registration (4/4) |
| **Benchmark-governance** | `benchmarks-governance/bench_governance.mjs` (+ `.test.mjs`) | does the stack *govern* a model attempting HLE / ARC-AGI / FrontierMath — flags hallucinations, bounds agency, sandboxes code loops (4/4, pre-registered). It does **not** score generation; it's a governance layer |
| **ADG / TQG / LISM / QG-COS** | `adg-tqg/`, `qg-cos/`, `repro/` | telemetry experiments on real repos + committed raw data |
| **Physics (Telemetric Metric)** | `physics-agency/` incl. pre-registered locked run | the equation, scaling, discriminator, 3D emergence, SHA-256-locked run |

## Run one component only

Everything is a plain `pytest` or `node --test` target — no custom runner needed:

```bash
node ei/ei.test.mjs                     # EI, 17 checks
node hinton-test/hinton_test.mjs        # Hinton test, 11/11
node russell-test/russell_test.mjs      # Russell test, 7/7
python3 -m pytest physics-agency/       # the physics suite
node --test novora-suite/test/*.mjs     # the Novora suite
```

## CI

`.github/workflows/reproduce.yml` runs `reproduce_all.sh` on every push and pull
request, so the "reproducible" claim is enforced, not asserted.

**Why this file exists:** the tests were previously spread across many directories
with no single entrypoint, so an external agent trying to reproduce them "could not
find anything." Now there is exactly one command.
