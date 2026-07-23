# Run the Novora suite in Google Colab (copy-paste cells)

Two cells. Cell 1 runs the whole deterministic suite and prints a `RESULTS_SHA256`.
Cell 2 (optional) is your LMD GPU sweep. Then paste the hash back here for verification
against the pre-registered lock (`expected_results_sha256 = aebdd9b7…`).

---

## Cell 1 — the full reproduction suite (paste and run)

```python
# Fetch and run the self-contained Novora reproduction suite from the public repo.
import urllib.request
URL = "https://raw.githubusercontent.com/evmotorcycles/ihcei-ecosystem/main/colab-tests/colab_suite.py"
code = urllib.request.urlopen(URL).read().decode()
exec(compile(code, "colab_suite.py", "exec"))
_results, _digest = main()   # prints each test + RESULTS_SHA256
```

*(No network in your Colab? Just paste the entire contents of `colab_suite.py` into a
cell instead of fetching it, then call `main()`.)*

**Return this line for verification:**
```
RESULTS_SHA256 = <the hash Cell 1 printed>
```
If it equals `aebdd9b7723bf6c516283ebed15112f0227109ada7cb2e0bf9ced86464b56e51`, you have
independently reproduced the deterministic core of the stack.

---

## Cell 2 — the LMD GPU coupler sweep (your JAX notebook, kept)

```python
import jax, jax.numpy as jnp, numpy as np, matplotlib.pyplot as plt
print("JAX backend:", jax.default_backend(), jax.devices())

@jax.jit
def reconstruct(L):
    P = jnp.linalg.pinv(L); d = jnp.diag(P)
    R = d[:, None] + d[None, :] - 2.0 * P
    return jnp.sqrt(jnp.clip(R, a_min=0.0))

def ring(N, J):
    L = np.zeros((N, N))
    for i in range(N):
        L[i, i] = 2.0 * J
        L[i, (i + 1) % N] -= J; L[i, (i - 1) % N] -= J
    return jnp.array(L)

N = 100; Js = np.logspace(-1, 2, 15)
d = [float(reconstruct(ring(N, J))[0, N // 2]) for J in Js]
slope = np.polyfit(np.log10(Js), np.log10(d), 1)[0]
r2 = np.corrcoef(np.log10(Js), np.log10(d))[0, 1] ** 2
print(f"slope = {slope:.6f}   R^2 = {r2:.6f}")   # expect -0.500000 / 1.000000
assert np.isclose(slope, -0.5, atol=1e-4), "LMD signature not reproduced"
plt.loglog(Js, d, 'o-'); plt.xlabel("coupling J"); plt.ylabel("distance d(0,N/2)")
plt.title(f"LMD contraction (slope {slope:.4f})"); plt.grid(True, which="both", ls="--"); plt.show()
```

Expected: **slope −0.500000, R² 1.000000** — the algebraic LMD signature (you already
reproduced this; the raw distances differ in the ~5th decimal across CPU/GPU/BLAS, which is
harmless and excluded from the suite's hash).

---

## What each test checks

| Test | Component | Locked expectation |
|---|---|---|
| **T1** | LMD | slope −0.5, R² 1.0 (algebraic) |
| **T2** | LMD | 0 triangle violations / 100 graphs (it's a real metric) |
| **T3** | LISM | linear `E=U·D` beats quadratic (R² 0.96 > 0.93) |
| **T4** | swarm | multi-hop fidelity decays (corr −0.92) |
| **T5** | Echo | fixed Merkle root; one-byte tamper changes it |
| **T6** | τ_v | failed repos have higher enforcement latency; Mann-Whitney separates |
| **T7** | Hoffman | Fitness-Beats-Truth: fitness-tuned share → 1.0 |

HELM / PAGES / EI-LLM use JS-specific RNG and regex; they're verified in-repo with `node`
(`reproduce_all.sh`). A Python port of their governance logic is a future addition to this suite.
