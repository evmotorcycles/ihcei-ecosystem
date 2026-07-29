# Sub-mesh pools: local pooling helps once, then stops

*Pre-registration `9091d056…`, locked and committed before any implementation existed.
Addresses the M3 failure from `SETTLEMENT_MESH.md`.*

```bash
bash reproduce_all.sh        # 70/70, clean checkout, offline, $0
```

**Result: 3 of 5 gates. Local pooling works — but by 17%, not 90%, and no operating zone
exists.**

---

## 1. The failure this addresses

The pure mesh lost the shared-shock replay **2,458 to 0** because a central balance sheet
pools every issuer's reserves and a mesh has none. Your proposed remedy — pool **locally**,
in *k*-neighbour clusters, so friction is absorbed without any single entity intermediating
the network — is the right shape of answer. So it was implemented **inside the same
settlement engine already built and attacked**, and driven by the **same committed 4,886
real shocks**.

Not by a formula. The published JAX cell computes `friction = exp(-0.15·(k−1))` and
`blast = k/total_nodes` and plots them; both outputs *are* those two expressions. That is
the sixth appearance of the tuned-formula pattern, and gate **S7** now enforces that only
`k` may differ across arms.

## 2. Measured

| k | failed | vs k=1 | blast radius |
|---:|---:|---:|---:|
| 1 | 2,430 | — | 0.0050 |
| **2** | **1,982** | **−18.4%** | 0.0100 |
| 5 | 1,991 | −18.1% | 0.0250 |
| 10 | 2,024 | −16.7% | 0.0500 |
| **20** | 2,024 | −16.7% | **0.1000** |
| 50 | 2,021 | −16.8% | 0.2500 |
| 200 | 2,046 | −15.8% | 1.0000 |

## 3. What held

- **S2 — local pooling does reduce friction.** Every cluster size beat the pure mesh.
- **S4 — 8,734 draws, zero violations.** No draw ever exceeded a pool's balance or drove
  one negative. The no-credit-creation rule holds operationally.
- **S1 — pooling conserves value exactly.** Unexplained drift `0.000000`; the gross change
  equals the exogenous withdrawals precisely.

## 4. What failed

### S5 — the published prediction was wrong on both halves

```
predicted:  >90% reduction   at blast radius ~0.02
measured:   16.7% reduction  at blast radius  0.1000
```

Five times the blast radius, one fifth of the benefit.

### S3 — no operating zone exists

No cluster size achieves **both** <50% of baseline failures **and** blast radius <0.10. The
two objectives are in direct tension and, at these parameters, nothing satisfies both.

## 5. The shape is the real finding

**Friction reduction is flat at 16–18% from k=2 to k=200.** A hundredfold increase in
cluster size buys *nothing* — and k=200 is slightly *worse* than k=2.

That is incompatible with `exp(-0.15·(k−1))`, which predicts monotonic decay toward zero.
The mechanism is visible in the design: **each member's draw is capped at a multiple of its
own contribution**, so a larger pool has proportionally more claimants and per-member
capacity is unchanged. Pooling helps once, by giving each node access to a buffer it did
not have. It does not help more.

**Consequence for the architecture:** the smallest useful cluster is the best one. k=2 —
bilateral mutual guarantee — captures essentially the entire available benefit at
**one twentieth** the blast radius of the proposed k=20. If local pooling is adopted, adopt
it small.

## 6. Disclosed harness fix

S1 initially failed on a value drift of 1.9 × 10⁴. That drift was the exogenous shock
withdrawing reserves **by design**, not an accounting leak — verified independently: gross
drift equals total withdrawals, unexplained drift is `0.000000`. The gate now measures
conservation across the *pooling* operations, which is what it was written to test.

**No fix converted a mechanism failure into a pass.** S3 and S5 failed before and after.

## 7. Honest status

Local pooling is a **real but small** improvement that does not close the gap to a
centralised book. The remaining options are: accept ~17% friction reduction with a small
blast radius, raise the draw cap (untested, and it moves toward credit creation — the thing
the architecture exists to prevent), or accept that a mesh trades routine liquidity for the
absence of a single point of collapse.

That trade is still **unmeasured** — no gate here or in `SETTLEMENT_MESH.md` tests
catastrophic centre failure. It remains the named next step.

---

*Reproduce: `bash reproduce_all.sh` → **70/70**. `exit 0` means "reproduces including its
failures", never "sub-mesh pooling works".*
