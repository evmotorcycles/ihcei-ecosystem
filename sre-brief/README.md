# Novora SRE Brief — validation

*The partnership brief (`Novora_SRE_Brief.pptx`, 8 slides) proposes enforcement
latency **τ_v** as a read-only, falsifiable early-warning signal for site
reliability. This harness tests the brief against the repository's real
artifacts — because a brief is only as good as its fidelity to the committed
science and the reproducibility of its instrument.*

`node sre-brief/validate_sre_brief.mjs` → **14/14**.

## What the brief claims, and how each claim is checked

| Slide | Claim | Test |
|---|---|---|
| 3 | τ_v: failed **50.6 d** vs survivors **19.8 d**, N=**992** (750/242), p≈**1e-31** | matches `REPRODUCIBILITY.md` CI-log table **and** `zenodo_metadata.json` deposit |
| 4 | Pre-registered D_gap **null p=0.735** on Kubernetes; VS Code was a dependabot artifact | archived verbatim in `FLOOR_RETIREMENT.md` / `LISM_CONTRIBUTION.md` |
| 4,7 | Spec **SHA-256-locked** before linkage | `govphys_quadratic_prereg_test.py` self-hash == archived `cac34f44…`; acceptance harness enforces the lock |
| 3 | "Responsiveness separates survivors from failures" | **reproduced on 15 real repos**: stale/abandoned mean τ_v **115.7 d** vs alive **15.2 d** |
| 5,8 | "Trajectory not threshold", "correlational not oracle", read-only shadow mode | the shipped `tau_v_monitor` carries these disclaimers verbatim and has no write path |

## Three pillars of the test

1. **Faithful to the archive** — every headline number on a slide is checked
   against the repo's locked record. A deck that inflated its own numbers would
   fail here; this one reports exactly what the CI log and the Zenodo deposit
   contain.
2. **Instrument reproduces on fresh data** — the brief's *direction* (higher τ_v
   in stale/abandoned repos) reproduces on the 15 real GitHub repos captured in
   this repo, using the same shipped monitor logic. The reproduced separation
   (7.6×) is even sharper than the paper's cohort (2.6×), on independent data.
   The say-do **Dissonance σ** (the LISM update) additionally surfaces the
   `lodash` "zombie" — fresh push, τ_v ≈ 114 d — that a naive last-commit scanner
   would rate healthy.
3. **The self-disproving discipline is real** — the SHA-256 pre-registration
   lock and the acceptance harness that refuses a tampered spec actually exist
   and run; slide 8's promise ("a discipline rigorous enough to disprove
   itself") is executable infrastructure, not a slogan.

## Honest scope

The raw 992-repository and STRING v12 datasets are rebuilt from public sources
over the network (`build_yeast_cohort.py`, the pre-registered GitHub fetch), so
their exact offline recomputation is out of scope here. This harness validates
that the brief **faithfully reports the archived confirmatory run** and that the
**same instrument reproduces its direction** on fresh real repositories — the
two things a reader most needs to trust before a 90-day shadow-mode pilot.
