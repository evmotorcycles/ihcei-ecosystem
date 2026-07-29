# Referee report: the Colab "Hybrid Sovereign Mesh" run

*Pre-registration `9a3e4a3e…`, locked before the audit runner existed. All nine source
datasets are now committed and hash-pinned — the original run read files committed
nowhere, which by itself made it unreviewable.*

```bash
bash reproduce_all.sh        # 69/69, clean checkout, offline, $0
```

**Verdict: 7/14 gates. 4 REPRODUCED · 2 NOT REPRODUCED · 3 INVALID · 1 CIRCULAR.**

Six gates were declared **EXPECTED TO FAIL before the run**. A pass on any would have
withdrawn the criticism. None did.

---

## 1. What survived — and it matters

Where the Colab did straightforward counting, it was **exactly right**:

| Claim | Recomputed |
|---|---|
| 4,886 debits, 400 above the 30% threshold | ✅ exact |
| Meezan: n=11,248, U=238,959.66, breach 26.64%, E=104,378.76 | ✅ all four exact |
| Executive-order counts 112 / 132 / 907 / 1061 | ✅ exact |
| Hearing counts 3,567 / 8,245 / 11,404 / 15,738 | ✅ exact |

The provenance claim — *"these numbers are not hallucinations, they came from deterministic
pandas operations"* — is **true**. The arithmetic is honest. The problems are in what the
numbers were taken to *mean*.

## 2. The three INVALID findings

### A7 — the "Risk-Sharing" cohort contains **zero** risk-sharing contracts

```
Contract_Type in the file:   Murabaha 3,837 · Ijara 3,764 · Salam 3,647
Mudarabah: 0        Musharakah: 0
```

Murabaha is **cost-plus sale**, Ijara is **lease**, Salam is **forward purchase**. All three
are sale-based and debt-like in payoff. Risk-sharing in the sense the framework means —
profit-and-loss partnership — is *mudarabah* and *musharakah*, and **there are none**.

This is the deepest error, because it inverts the thesis: under **Harris Irfan's own
critique**, these three *are* the synthetic-debt wrappers. So the headline comparison was
**debt-like data against a tuned debt-like simulation**, labelled as risk-sharing beating debt.

### A8 — the comparison was rigged before any data was read

From the published source:

```python
capacity_u:      276355.69,  # Target Mean Capacity (U)
base_fidelity_d: 0.75,       # Tuned base fidelity for high Zombie Breach Rate
hops_params:     {...}       # Tuned hops distribution
```

…against a comparator arm using `BASE_FIDELITY_RISK_SHARING = 0.95`. **Two arms with
different fidelity constants cannot be compared.** The 97.45% vs 26.64% breach gap is the
0.75-vs-0.95 choice, restated.

The "Optimal Path Selection" block is likewise hardcoded — `optimal_u = 485448.89`,
`optimal_retained_d = 0.5773`, `TXN008250` — nothing is selected from data.

### A10 — the legislative fidelities are dimensionally impossible

Reported `D` values: **419,450 · 750,698 · 2,245,229 · 1,437,080**.

In `E = U·D`, `D` is a fidelity and must lie in **[0,1]**. These are a character count
multiplied by a hearing count. The resulting "yields" of up to **2.03 × 10⁹** have no units
and cannot be compared to anything.

## 3. The CIRCULAR finding

**A9 — the "Zombie Breach Rate" is a renamed percentile.**

`0.95^Risk_Score < 0.50` is algebraically `Risk_Score > ln(0.5)/ln(0.95) = 13.513`.

```
P(Risk_Score > 13.513) = 26.64%      reported "Zombie Breach Rate" = 26.64%
```

Identical. It carries no information beyond the input column. Separately, `Risk_Score`
ranges **0–100** and is used as a **hop exponent** — `0.95¹⁰⁰ = 0.0059`. A risk score is
not a path length.

## 4. What did not reproduce

- **A6 — `D_enc`:** recomputed `[88.46, 107.40, 98.36, 92.79]` against the claimed
  `[117.59, 91.05, 196.88, 91.31]`. Different values **and a different rank order** —
  Defense was claimed as by far the most specific (196.88) but recomputes to 98.36.
- **A3 — Kenya index:** recomputes to **12.23%**, not 11.24%. The denominator also counts
  every spreadsheet row (507 rows × 110 columns), not respondents.
- **Executive velocity:** Carter is reported at 71.25/yr and Nixon at 64.0/yr. Recomputed,
  Carter is **64.0** and Kennedy is **71.33** — the values appear shifted by one row.

## 5. The correction that reverses the political conclusion

**C6.** The Colab's `D_dec` was a **raw count** of hearings. Raw counts grow with domain
size, so:

```
spearman(capacity U, raw hearing count) = +1.00      ← perfect rank correlation
```

`E = U·D` was therefore approximately **U²**, and *"Govt Operations has the highest
realized yield"* reduces to *"Govt Operations is the biggest domain."* The finding was
circular.

Rebuilding `D_dec` as **hearings per enacted law** — an *intensity*, not a size — breaks it
(ρ = −0.80) and **reverses the substantive claim**:

| Domain | Rebuilt `D` ∈ [0,1] | Colab said |
|---|---|---|
| Banking & Finance | **0.9978** | "lowest baseline fidelity" |
| Macroeconomics | 0.8236 | "lowest baseline fidelity" |
| Defense & Security | 0.5434 | high specificity |
| Govt Operations | 0.3227 | highest yield |

Banking has the **highest** verification intensity per law, not the lowest. Corrected
`E = U·D`: Defense 492.9 > GovOps 342.4 > Banking 131.7 > Macro 92.2.

## 6. The 69-day latency was never computed — and is refuted

The Colab asserts "the ~70-day failure threshold" and "the 69-day failure state" repeatedly.
`public_laws.csv` carries `date_introduced` and `date_signed`, so it is directly measurable:

```
median days, introduction → signature
  Macroeconomics      171 d   (n=15)
  Banking & Finance   244 d   (n=69)
  Defense & Security  197 d   (n=91)
  Govt Operations     288 d   (n=404)
```

Every domain is **far above 69 days**. The asserted figure is refuted on these data.

**And this correction failed its own gate.** C4 required ≥100 dated laws per domain;
Macroeconomics has **15**. The latency measurement is underpowered for that domain, and
that is recorded as a failure rather than smoothed over.

## 7. What this review does *not* say

- It does **not** allege bad faith. Tuned baselines and loose proxies are ordinary
  early-stage modelling errors.
- It does **not** show Islamic finance is better or worse than conventional finance. These
  files cannot answer that — there are no risk-sharing contracts in them.
- It does **not** validate the Hybrid Sovereign Mesh or any political-decentralisation
  claim. On the corrected numbers, the political finding was circular and its direction
  reverses.

## 8. The one comparison that is fair

Holding transactions and fidelity **identical** and varying only payoff structure:

```
same 11,248 transactions, same fidelity input
  equity (90% proportional)  mean  -60,884.42 per contract
  debt   (8% markup, priority) mean -79,008.32 per contract
  difference                        +18,123.90   computed, not targeted
```

Equity beats debt — consistent with the independent N=992 stewardship result. **But this is
a statement about contract structure on debt-like data**, not evidence that risk-sharing
contracts perform better, because none are present.

---

*Reproduce: `bash reproduce_all.sh` → **68/68**. Datasets committed under
`data/colab-audit/` with a SHA-256 manifest. `exit 0` means "the review reproduces,
including the claims it refutes."*
