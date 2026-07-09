# Pre-Registration — Barakah / Knowledge-Propagation Extension (Stack Exchange)

**Purpose.** First attempted EXTENSION of the LISM linear-coupling law beyond the
two completed cohorts (yeast, GitHub), in the knowledge-propagation domain the
Governance framework's own operationalization of Barakah points to. Unlike the
clinical/contract/legislative domains — where the independent second hop is not in
any off-the-shelf dataset — Stack Exchange has three *different actors* per unit
(asker, answerers, downstream readers), so the two hops and the outcome are
plausibly separable and publicly measurable.

**Status.** Locked template. Commit the SHA-256 of `se_barakah_test.py` before the
fetch; do not edit definitions/thresholds after data is seen.

## Unit & variables (from SE question metadata via `api/se-search.js`)
- **Unit:** one question thread.
- **U (capacity):** `log(1 + asker reputation)`.
- **D_enc (sincere seeking / query fidelity):** min-max of clipped positive
  question `score` — the community's judgment of the ASKER's encoding. Source A: the
  question.
- **D_dec (selflessness / onward transmission):** min-max of `answer_count` — the
  community's onward transmission, measured on ANSWERERS (different actors). Source B.
- **D:** `D_enc · D_dec`.
- **E (Barakah / downstream reuse):** top-tercile `view_count` = 1 — compounding
  downstream consumption, measured and non-circular w.r.t. whether it was answered.

## The three invariants (eligibility gates)
- **I1 channel independence:** `VIF(D_enc, D_dec) < 5`. D_enc is on the asker, D_dec
  on the answerers → plausibly independent; **verified on the data, not assumed.**
- **I2 populated failing region:** `>= 100` threads in each of E=1 and E=0.
- **I3 non-circular outcome:** downstream reuse (views), distinct from the text and
  from the answering process.

## Analysis (inherits the corrections)
- **PRIMARY:** nested curvature LRT — `M1: logit(E)=b0+b1 U+b2 D` vs `M2:+b3 D²`;
  report `ΔAIC` and the LRT p on `b3`; penalized-safe under separation.
- Single-term literal AUC (linear `U·D_s` vs quad `U·D_s²`) reported as secondary.
- **Sign requirement:** "quadratic supported" needs `b3 > 0` (convex/accelerating),
  since the yeast arm showed the opposite (saturating) sign.

## Two-directional decision rule (locked)
| Verdict | Condition |
|---|---|
| **LINEAR (extends LISM)** | eligible **and** `ΔAIC ≤ 0` or LRT `p ≥ 0.05` |
| **QUADRATIC SUPPORTED** | eligible **and** `ΔAIC > 10` **and** LRT `p < 0.001` **and** `b3 > 0` |
| **INCONCLUSIVE** | `VIF ≥ 5` (channel collapse), or `I2` unmet |

A **LINEAR** verdict would be the first genuine extension of the linear essence law
to a third, socially-generated domain. **INCONCLUSIVE** (likely if question quality
and answer volume co-move) is honestly reportable and itself informative: even the
Barakah domain resists clean off-the-shelf two-hop instrumentation.

## Run
```
# fetch via the deployed proxy (SE API is blocked from the sandbox):
curl "https://project-6q4gj.vercel.app/api/se-search?site=stackoverflow&tag=python&pages=3" > se.json
python se_barakah_test.py --json se.json
```
