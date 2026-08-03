# Licensing Q3, Q4 and Q5 — two out of three

**v1** `cd429dfa5208403d142f49d5ca8f6e4e09d8ce01dc6065c3e8892608dd8c4a9f`
**v2** `d7184ef95c804eb896488099412fe11406c03d7890abc652968e27310c263efd` (Q3 control only)

```bash
python3 -m pytest -q licensing/test_lic.py
```

| Arm | Score | Verdict |
|---|---|---|
| **Q4** reference-lock | **5/5** | **LICENSED** |
| **Q3** stewardship | 3/4 → **4/4** | **LICENSED**, at the narrow claim only |
| **Q5** predictability | **3/4** | **PRIMARY REFUTED** |

## Three corrections the spec records before any result

1. **The Rule 110 ceiling story is backwards.** P5 was scored on the *irreducible* arm, where
   static prediction sat at **0.4940 — chance**. Maximum headroom; monitoring gained +0.0051
   anyway. The ~1.0 figures belong to the *reducible* rules, which P5 never scored.
2. **τ_v 19.8 vs 50.6 days** are *means* from the smaller four-cohort study. On this committed
   file the **medians** are 20.53 vs 32.37 and the **means** are 44.11 vs 47.00 — nearly
   identical, the mean being dominated by a long tail.
3. **Q3 cannot be licensed on `three-proposals/`** — that is our own simulator. Re-scoped to
   the part that is falsifiable on real data.

## Q4 — the one that worked

```
  AUC(execution kernel, declared correctness)   1.0000    bar 0.95
  AUC(HELM oriented verdict, correctness)       0.5365    bar 0.65   ← chance
  Spearman(kernel verdict, word count)         +0.0226    bar 0.20
  Spearman(HELM verdict, word count)           +0.2804    (−0.4831 on spec 5576e524)
  DCM  Δ = V 0.6000 × I 1.0000 × C 0.6500  =    0.3900    floor 0.20
```

**The DCM floor is cleared for the first time in six runs, and it was not moved to get there.**

Spec `5576e524`'s W8 — *does the evaluator respond to the right content?* — was
UNTESTABLE-HERE because manipulativeness has no ground truth. **Code correctness does.** That
is the whole reason this arm closes what HELM's could not.

Two confounds were found and removed **before** the lock: a first draft had
`Spearman(word count, correct) = +0.3547` and `Spearman(self-certifying, correct) = −0.7917`.
The **artifacts** were rewritten, never a threshold. Residuals: +0.0177 and 0.0000.

The kernel's AUC of exactly 1.0000 is **flagged** by the too-perfect rule. Its perfect
insensitivity to self-report scores **nothing** — true by construction, and a quantity that
cannot come out otherwise is not evidence.

## Q5 — refuted, and the failure survives its own confound

```
  AUC(STATIC: stars, U)     0.8000
  AUC(PROCESS: tau_v)       0.5947
  process − static         −0.2053    bar +0.05
  COMBINED                  0.7998    ← tau_v adds nothing
```

τ_v is **0.205 worse** than stars and leverage. The claim that "star counts fail to predict
long-term maintenance survival" is not what this cohort holds.

The cohort **is** confounded — `S4_failed` is 100% archived, so the strata were built using
the outcome. The failure is reported as measured, and the post-hoc check shows it **survives**:
with S4 removed, static still wins **0.6801 to 0.5850**.

**Q5_E excluded:** τ_v was harvested with no cutoff before archiving, so on this cohort it is
**contemporaneous, not leading**. No gate here separates the two.

## Q3 — licensed at the narrow claim only

v1 scored 3/4 because my control **bootstrapped one fixed permutation** instead of drawing
many. That estimates the spread around that one permutation, not the permutation null. The
defect is mine; v1 is published unchanged and **not re-scored**, and the correction lives in a
new spec with no threshold moved.

```
  SYSTEMIC 0.3653 vs ROUTINE 0.1946   difference +0.1707   bar +0.10
  permutation null (2000 draws): mean +0.00093, band [−0.0548, +0.0613], p < 0.0005
```

This licenses that **the classification separates realised risk**. It does **not** license that
assigning Al-Qudah's instrument to one class and Irfan's to the other helps anyone — that is an
intervention, and `Q3v2_E` records it as untestable here.
