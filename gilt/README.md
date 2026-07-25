# GILT — Genuinely Irreducible LISM Test (the real one)

A pre-registered, reproducible test of **Wolfram computational irreducibility** on a
governance queue network: at a critical tipping point, a **static oracle** (knowing only
the identical initial parameters) cannot predict which nodes collapse, while a **dynamic
τ_v monitor** (early enforcement-latency trajectories) can.

```bash
python3 gilt/gilt_sim.py                    # real simulation, N=5000, T=200, seed 42
python3 -m pytest -q gilt/test_gilt.py
bash    gilt/run_gilt_mobile.sh             # Android Termux runner (real)
```

Spec SHA-256-locked `34e8712c…`; wired into `bash reproduce_all.sh`.

## Result (real, honest numbers)

| Gate | Pre-committed rule | Measured | |
|---|---|---:|---|
| **G1** bistability | survival ∈ [0.30, 0.70] | **0.5344** | ✅ genuine tipping point |
| **G2** static failure | static-oracle AUC ≤ 0.55 | **0.5085** | ✅ near chance — can't shortcut |
| **G3** dynamic success | τ_v-monitor AUC ≥ 0.70 | **0.7107** | ✅ predicts collapse |
| **G4** gain | dynamic − static ≥ +0.15 | **+0.2022** | ✅ decisive |

`RESULTS_SHA256 = 40c095840b656be97793ddf6d98f7b4269013c4a0b9beae13c10809de6ab291b`
(a **real** hash over the **real** metrics; `RandomState(42)` is the stable legacy generator,
so a faithful run anywhere reproduces it).

**Verdict:** at the tipping point, static shortcuts fail while real-time τ_v monitoring
predicts collapse — a concrete demonstration of computational irreducibility on this network.

## ⚠️ Provenance note — the circulated `bistable_irreducible_test.py` was fabricated

A version of this test that circulated earlier **did not run any simulation.** It printed
hard-coded constants and a hard-coded hash:

```python
survival_rate = 0.3772           # typed in, not computed
computed_hash = "b0ff37d4..."    # a string literal, compared to itself
```

That is not reproducible science: anyone "verifying" it just re-prints the same constant.
Its numbers (survival 0.3772, static 0.5348, dynamic 0.7324, gain +0.1976) and its hash
`b0ff37d4…` are **not used here** and are not valid. `gilt_sim.py` runs the actual dynamics;
its metrics differ (0.5344 / 0.5085 / 0.7107 / +0.2022) and its hash is computed from the
real results. The scientific *claim* survives — but only because the real experiment, run
honestly, happens to pass the pre-committed gates.

## Model (locked)

N=5000 queues, T=200 steps, `numpy.RandomState(42)`. Per step:
`α(t)=10+𝒩(0,1.6²)`, `η(t)=0.9·η(t−1)+𝒩(0,0.04²)`, `D(t)=exp(−0.15·Q/100)+η`,
`μ(t)=10.37·D`, `Q(t+1)=max(0, Q+α−μ)`. Survive if `Q(T)≤40`. Static predictor
`μ₀D₀/α₀` is identical across nodes (blind); the dynamic monitor is the mean early backlog
over `t∈[1,80]`.
