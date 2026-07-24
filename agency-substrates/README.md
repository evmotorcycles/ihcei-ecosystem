# The triage-first agency methodology, tested on four real substrates

**One command:** `python3 agency-substrates/substrates.py` · stdlib · offline · `$0`

The AlphaAgency breakthrough is a **methodology**, not speed and not a superhuman score:
because agency is **multiplicative** (`E = U·∏Dᵢ`) with a `τ_v` collapse floor, the
structurally optimal governance move is **triage-first** — rescue below-floor nodes before
optimizing healthy ones. This asks whether that *active method* transfers to real data:
**GitHub, PubMed, Hugging Face, bioRxiv.** LISM prioritizes nulls, so the two honest limits
here are reported with the same force as the positives.

> **Framing:** OQM is invoked strictly as a **philosophy of governance** — the
> multiplicative-collapse → triage structure — not theology. The value is the verifiable,
> active method.

---

## Real nodes (proxies locked before computing)

| substrate | U (capacity) | D (fidelity) | floor |
|---|---|---|---|
| **PubMed** (8 fields) | log₁₀(papers) | integrity = 1 − retracted/total | D < 0.997 |
| **Hugging Face** (19) | log₁₀(1+downloads) | license clarity × eval evidence | min hop < 0.28 |
| **GitHub** (28) | log₁₀(stars) | forks / (forks + open issues) | D < 0.65 |
| **bioRxiv** (40) | n_authors | 1/(1 + τ_v/365) | — (all survivors) |

`value(node) = 0 if min(D) < floor (collapsed) else U·D_enc·D_dec`. Fidelities come from the
**frozen fixtures** — a node's self-reported popularity never enters the evaluation
(`F_out = F_eval`).

---

## Results (pre-registered T1–T4, spec `b7f6016e…`)

### Positives — the methodology transfers
```
HuggingFace (8/19 below floor):  triage 22.64  >  capacity 20.09  >  equal 21.21   → T2 PASS
GitHub      (2/28 below floor):  triage 111.51 >  capacity 109.62 >  equal 106.71  → T2 PASS
T1 (rescue-gain ≫ improve-gain) → PASS on both (and on PubMed)
```
On real Hugging Face and GitHub networks, the triage-first allocator recovers **strictly more
systemic agency** than greedy-by-capacity or equal-split — because unlocking a collapsed node
(`U·floor`) dwarfs improving a healthy one (`U·step`).

### `F_out = F_eval` on real data — T3 PASS
Ranking Hugging Face models by **downloads** (the self-report) differs from ranking by
**verified D** (license + eval), and **3 of the 5 most-downloaded models are below floor**
(e.g. `coqui/XTTS-v2` — hugely popular, ambiguous license). Trusting popularity would
misallocate; the deterministic evaluator ignores it.

### Two honest limits — reported with full force
- **PubMed → construct-untestable.** The integrity-D is so compressed near 1 that the floor
  (0.997) sits **above** the investment cap (0.99), so a below-floor field can **never** be
  rescued and all allocators **tie** (triage 36.11 = capacity 36.11). This is a proxy
  degeneracy — provable from the locked spec, disclosed here — **not** a triage failure. The
  literal pre-registered T2 did not hold on PubMed; that is stated, not retuned. *(An erratum
  in the same spirit as AlphaAgency's myopic-oracle disclosure.)*
- **bioRxiv → survivor-only null.** All 40 preprints are published survivors — **no collapsed
  nodes exist**, so triage is **not applicable**. Declared, not forced. LISM prioritizes nulls.

---

## The honest headline

The triage-first **methodology** — a structural consequence of `E = U·∏Dᵢ` + `τ_v` — beats
naive allocation on every real substrate where a rescue is *feasible* (Hugging Face, GitHub),
and it does so with a deterministic evaluator that can't be fooled by a node's self-reported
popularity. Where the proxy is degenerate (PubMed) or the data is survivor-only (bioRxiv), the
result is an honest limit, reported as such. **This is a verifiable active method, not speed
and not superhuman optimization** — exactly the distinction the DeepMind lesson draws.

## Files

```
agency-substrates/
  prereg/substrates_prereg.json     spec (locked) — node proxies + T1–T4
  prereg/MANIFEST.sha256.json        spec + the 4 referenced fixtures, hash-pinned
  substrates.py                      applies triage-first vs naive on real nodes
  test_substrates.py                 pytest guard (positives + both honest limits)
  results_substrates.json            emitted results
```

Layer-1, offline, `$0`. Methodology, not speed. Nulls prioritized, not hidden.
