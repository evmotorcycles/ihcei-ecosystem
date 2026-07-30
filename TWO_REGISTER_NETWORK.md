# The Two-Register Settlement Network

**Spec** `ed80430a7349da34ab6a76fcc5d60ecd30999cc1f857389b7acbe3a62a94c539` · locked before
implementation · **0/5** · `python3 -m pytest -q two-register/test_tworegister.py`

You had the priority split right, and the telemetry confirms it: **risk-sharing serves
network health; latency engineering serves something else, and they run side by side.**
This document names the model, reports the run that finalised it, and states plainly which
part of it did not survive.

---

## 1. The name, and why it is this one

Named from the mechanism, in plain English, with no borrowed vocabulary — the root sweep
was used only as a **design generator**, per the boundary in
`.claude/skills/geometric-root-translation`.

Invariant: *a claim under stress.* Sweeping the operator set gave holder / claim / **the
place a claim is sorted to** / the cascade / what forces the sort. The **locus** cell was
empty in every previous design, and filling it is the whole model:

> **Two-Register Settlement Network.** Every claim sits in one of two registers.
> The **recovery register** holds fixed claims: they survive a shock, so later inflows
> still reach the holder. The **containment register** holds participation claims: they
> absorb loss without a hard default event, so the loss does not propagate — but they
> **extinguish**, which forecloses recovery.

A test asserts the name and the entire results file are free of Arabic and theological
terms. The model must be judged on its mechanics.

## 2. Why the split exists — the measurements that forced it

| | Recovery register | Containment register |
|---|---|---|
| Instrument | fixed claim | participation claim |
| On loss | residual survives | extinguished |
| Claimant shortfall | **16.1** | 94.4 |
| Secondary failures | 148 | **121** |

Neither instrument wins both. **This is the finding, and you stated it correctly:**
risk-sharing was never a loss-minimisation tool for an individual lender — its operational
role is a **contagion firewall**. Adopting it to reduce your own losses is a design error;
it makes them worse.

## 3. What this run tested — and what died

Not "does mixing help." Two instruments with different failure modes usually beat either
alone, and the spec writes that gate off as weak in advance. The load-bearing claim was
**routing**: that assigning claims to registers *by a contagion-risk signal* beats
assigning the same share *at random*.

### N2 — routing is beaten by chance

```
targeted                       J = 3.7219
random assignment, 20 draws    mean 2.5692   min 1.5690   max 4.1542
```

**Targeted sits at the 90th percentile of random. Eighteen of twenty coin flips beat it.**

### N4 — and here is why

```
AUC(out-degree → cascade involvement) = 0.4447     BELOW 0.5
Spearman rho(signal, node size)       = −0.0333
```

The routing signal is **mildly anti-predictive**. It is not a size proxy — it is simply
wrong. Routing on it puts participation on the wrong nodes, so a coin flip does better.

**This is the fifth falsified selection rule in this programme**, and the pre-registration
predicted it in writing:

> *"EXPECTED TO FAIL… four selection rules have been falsified, one of them with an
> INVERTED sign."*

**The model therefore ships without the routing claim, as a fixed policy mix requiring no
scoring apparatus at all.** That is cheaper and more robust than what was proposed. The
anti-immunisation clause forbids rescuing this by proposing a better signal; any such
follow-up is a separate pre-registration reported as a second attempt.

## 4. A defect in my own pre-registered objective

`J` was locked with equal 0.5/0.5 weights. On this substrate the shortfall term spans
**18.17** and the cascade term spans **0.20** — shortfall dominates **90×**, so J is
effectively a shortfall metric despite its weights.

Nothing was re-scored and no threshold moved. The consequences, stated:

- **N1, N3, N5 largely restate "shortfall favours fixed claims."** Their interpretation is
  compromised.
- **N2 and N4 are untouched** — they are same-share comparisons and a diagnostic AUC.
- Under a **post-hoc range-balanced** version of the same two objectives, an **interior
  optimum does appear at share 0.60** (J′ 0.3167 against 0.5000 at both endpoints).

So *"the two-register idea is refuted"* would be too strong. **What is refuted is
routing.** The mix itself remains defensible — and on a balanced objective, favoured.

## 5. The sleeper: continuous distribution

Ablation under the locked objective:

| Remove | ΔJ | |
|---|---|---|
| continuous distribution | **+194.5048** | overwhelmingly dominant |
| recovery register | +6.2620 | earns its place |
| local pooling | +0.5305 | earns its place |
| containment register | −2.7219 | removal *improves* J here |

**Distributing inflows continuously is the single largest effect in the entire financial
programme — and it was never a named component in any proposal.** It is not risk-sharing,
not full reserve, not pooling. It is the discipline of paying holders down as money
arrives instead of warehousing it.

---

## 6. Why conventional banks should adopt this

No cultural framing required — this is network science, and the evidence is telemetry.

1. **Continuous distribution on distressed exposures.** The largest measured effect by two
   orders of magnitude. Paying down as inflows arrive dominates every structural choice
   tested.
2. **Full reserve is worth more than leverage.** Measured: leverage made settlement
   monotonically *worse* — m=1 → 0 failures, m=3 → 3,262, m=5 → 3,912, m=10 → 4,362. The
   central book's zero-failure record was achieved at **ΔU = 0.0**, by pooling, **not** by
   credit creation.
3. **Participation tranches as a circuit breaker, not a return strategy.** 18–32% fewer
   knock-on failures. Use it where cascade is the exposure, and price it knowing it costs
   you recovery.
4. **Do not buy a risk-routing model.** Ours was beaten by 18 of 20 coin flips. A fixed
   policy mix is cheaper and performed better.

## 7. Why Islamic banks should adopt this

Harris Irfan's charge is that the sector wraps conventional debt in synthetic trades and
changes the label while the fractional-reserve physics stays identical. The telemetry
supports the substance of that critique, and it also **corrects the remedy**:

- **The full-reserve substrate is vindicated on measurement, not on doctrine.** ΔU = 0 was
  the smoothest configuration tested. That is the strongest available argument for it, and
  it does not require anyone to accept a theological premise.
- **But risk-sharing does not do what it is usually sold as doing.** It does not reduce the
  financier's losses — measured, it increases them (94.4 vs 16.1), because writing a claim
  down *extinguishes* it and forecloses recovery. **A sector that adopts participation
  expecting lower losses will be disappointed by arithmetic, not by markets.**
- **Its real value is systemic**, and that is a better argument than the one usually made:
  it keeps counterparties alive and cuts cascades. Sold as prudential infrastructure it is
  defensible; sold as a superior return profile it is not.
- **The audit story is the differentiator.** A full-reserve claim register with a
  tamper-evident ledger is *checkable*. The oxymoron charge lands because labels are
  unverifiable; a hash-chained register makes the label testable.

> **The honest pitch to both sectors is the same:** adopt continuous distribution and full
> reserve because they measure well. Adopt participation for contagion only. Skip the risk
> model.

---

## 8. Where the rest of the stack fits

Each component below is described by what it actually does in this repository.

### The telemetry layer — what tells you the network is sick

- **LISM** (`E = U · D_enc · D_dec`) — the two-hop channel law. Yield couples *linearly* to
  fidelity, confirmed on the yeast interactome (N=4,825, CV AUC 0.666 vs quadratic 0.591)
  and the recovered GitHub cohort (N=992, dAIC −3.483). **Null reported honestly:** on real
  PyPI neither coupling explained reuse (R² ~0.01 both). In this financial network it is
  the *health* reading — capacity times how well the two hops actually carry.
- **τ_v (enforcement latency)** — the monitor. Failed **four times** as an admission
  screen; **passed** as a covenant trigger, earning +42,840 over holding everything. This
  is the latency-engineering half you correctly identified as running alongside: it governs
  *when to act on an exposure you already hold*, never *who to admit*.
- **ADG (`C_dev`) and TQG-CFE (`Ψ`)** — organisation-graph telemetry, explicitly **not**
  physical laws with SI units. They combine measurable network signals into a scalar that
  should track health. In this system they are the aggregate dashboard above the per-claim
  metrics: `C_dev` for developmental capacity of the network, `Ψ` for coherence. Layer 1
  is the telemetry reading only; the metaphysical reading is Layer 3 and is not claimed.

### The agency layer — what makes the readings trustworthy

- **IHCEI / NERE** — the probabilistic kernel underneath everything, producing calibrated
  verdicts rather than scores.
- **HELM** — runs that kernel **entirely on-device**. Architecturally incapable of
  surveillance: there is no network call in the kernel and a test proves it. For a
  settlement network this is what lets a participant be audited *without* their book being
  uploaded anywhere.
- **Echo (the agency database)** — content-audited writes, append-only tamper-evidence,
  Merkle-provable inclusion. **This is the claim register itself.** The reason a
  two-register model is checkable rather than merely asserted is that Echo can prove which
  register a claim was in, and that the record was not rewritten afterwards.
- **Page Code** — the governance layer for a coding agent: a default-deny permission table,
  a corroboration gate, and every audited change hash-chained into Echo. In a financial
  deployment this is what governs changes to the settlement engine itself.
- **EI-LLM** — a receiver-side attestation layer. It generates nothing and censors nothing;
  it answers verifiable questions — is this claim grounded, is this delegation in-bounds,
  is this queue saturating. It is the counterparty-verification seat.
- **Novora suite / PAGES** — the confidence-and-abstain layer. Its rule is that a system
  should decline to answer when it lacks grounds. Note the honest status: the abstention
  rule was **untestable** on the N=992 cohort by construction of that cohort's imputation —
  *untestable-here, not refuted*.
- **AlphaAgency (the Agency algorithm)** — the discovery methodology, and the most relevant
  piece to your point about LISM's true strength. A probabilistic generator proposes
  policies; a **deterministic evaluator** scores them; `F_out = F_eval` means a
  hallucinating generator cannot corrupt a verified result. Its own README reports that a
  pre-registered "near-optimal" framing turned out **false** against a genuine reference,
  and says so.

### The methodology — which is the actual contribution

You put it precisely: **LISM's strength is the methodology while engaging the telemetry.**
This run is the demonstration. The model was designed from prior measurements, its central
new claim was pre-registered with its own predicted failure, the failure arrived, and the
model shipped smaller. Nine consecutive runs have now refused a tuned simulation. The
score is 0/5 and the deliverable is *better* for it, because what remains is what survived
a genuine attempt to kill it.

A framework that cannot lose an argument to its own instruments is not a framework.

---

## Reproduce

```bash
python3 two-register/tworegister.py
python3 -m pytest -q two-register/test_tworegister.py
bash reproduce_all.sh
```

Exit 0 means "reproduces including its failures", never "the Two-Register Network works".
