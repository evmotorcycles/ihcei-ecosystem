# The alarm on `D` — diagnosed, and it was a definition

**Spec** `b6a262ead56e56b532a3578185c6d505df45fbc9c58a5ba5864108bb194c53d8` · locked before
the primary quantity was computed · **4/4**

```bash
python3 -m pytest -q construct/test_con.py
```

## The alarm as it stood

ρ(U, D) = **+0.5695** on real PyPI and **−0.4702** on the real GitHub cohort. Two committed
substrates disagreeing on the *sign* — taken to mean `D` is an unstable construct and every
fidelity claim rests on sand.

## The proposed fix is BLOCKED, not refuted

Demand-normalising `D_dec` by inbound load is not computable: the committed GitHub cohort has
no inbound issue or PR counts. **No proxy was substituted.** The mechanism may well be right.

But a prediction of it had already failed before the lock. Queue congestion is a *decode-side*
story, so the flip should sit in `D_dec`. **Both hops flip:**

```
              PyPI      GitHub
ρ(U, D_enc)  +0.5869   −0.2415
ρ(U, D_dec)  +0.3496   −0.5154
```

Computed before the spec was written, recorded in it as pre-flight observations, scored by
nothing.

## The two definitions share a name and nothing else

```
PyPI    D_enc = 1.0 / (1.0 + months_since_release / 12.0)      ← a recency decay
GitHub  D_enc = TF-IDF cosine of commit messages to a reference  ← a text-similarity score
```

## The result is exact, not approximate

```
  ρ(U_versions, months_since_release)  =  −0.5869
  ρ(U_versions, D_enc)                 =  +0.5869
```

**The same number, sign-flipped — necessarily.** `D_enc` is strictly decreasing in months and
Spearman is rank-based, so `ρ(U, D_enc) = −ρ(U, months)` *identically*.

> PyPI's "fidelity correlation" is the statement that packages with more releases have
> released more recently, restated. It carries **zero independent information about fidelity.**

A timing-free fidelity column (pin clarity) gives **+0.3496** against the timing-based
**+0.5869** — the 0.20 drop the discriminating gate required.

**And the count-to-intensity remedy makes it worse.** Versions *per month of age* drives ρ to
**+0.9418**, because that is even more directly a function of recency. The usual fix is a
tautology here.

## What this settles, and what it does not

**Settles:** one of the two data points the alarm rested on is disqualified. With PyPI's
number gone there is no longer a *contradiction between substrates* — there is one substrate
with a negative correlation, and one whose `D` was measuring release timing.

**Does not settle:** the GitHub negative correlation, which no gate here touches and which
stands exactly as it was. **`D` is not repaired.** `E = U·D_enc·D_dec` is **not** restored to
universal standing.

**The alarm should be restated, not retired:** not *"D is unstable across substrates"* but
*"D is a family of substrate-specific formulas, and at least one member was measuring
release timing."* The remedy is a rule about what may be compared — not a transformation
applied to either.

## An open consequence, flagged not claimed

Several PyPI-based results in this repository use the same `D_enc`. Whether those readings
change has **not** been re-run here, and no claim is made about them either way.

| Gate | Bar | Measured | |
|---|---|---:|---|
| N1 integrity | 540 / 866 rows | exact | PASS |
| **N2 the PyPI correlation is construction-induced** | \|ρ(U, months)\| ≥ 0.50 | **0.5869** | **PASS** |
| N3 the declared identity | — | −1.0000 | EXCLUDED |
| **N4 a timing-free column breaks it** | drop ≥ 0.20 | 0.2373 | **PASS** |
| N5 count-vs-intensity disclosed | — | +0.9418 | EXCLUDED |
| N6 permutation control | ≤ 0.10 both | 0.0843 / 0.0648 | PASS |
| N7 demand normalisation | — | — | **BLOCKED** |
| N8 cross-substrate repair | — | — | UNTESTABLE-HERE |
