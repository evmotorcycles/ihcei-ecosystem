# Two-Register Network v2 — finalised, and corrected by its own test

**Spec** `f14596f111c9378ae33c3ffa1e490a535086205692269bebeb8652215b8bb5cd` · locked before
implementation · **3/5** · `python3 -m pytest -q tworegister-v2/test_v2.py`

You proposed three improvements. **One was confirmed, one was corrected, and the third
turned out to be the whole model.** This document reports all three as measured, gives the
configuration a bank should actually deploy, and walks Sam's loan through it.

---

## 1. What the run says about your three improvements

| Your proposal | Verdict | Evidence |
|---|---|---|
| **① Adopt Al-Qudah's contracts as the recovery primitive** | **Corrected — it made our model worse** | v2 71.0 vs v1 51.8, losing on **0 of 5 seeds** |
| **② Re-centre the headline on flow, not contract architecture** | **Confirmed, strongly** | **50.9×**, re-measured on the new composition |
| **③ Confine participation to contagion control** | **Confirmed, and it goes further** | the mix adds nothing at all — pick an endpoint |

### ① The correction, and why the reasoning was still sound

Your inference was reasonable: in the three-proposal run Al-Qudah's arm scored **88.5**
against our **96.7**, so importing his contracts should help. **It doesn't.**

```
at containment share 0.25, identical conditions
  v2  co-ownership recovery   71.0
  v1  fixed claims            51.8      ← better
  and v2 loses on 5 of 5 seeds
```

**His 88.5 came from being *pure*, not from the contract primitive being better inside a
mix.** At share 0.0 the architecture *is* his model, and that is where the number came
from. Drop his contracts into a mixed register and they underperform plain fixed claims.

The right conclusion is not *"adopt his contracts into our architecture."* It is
**"his architecture, unmixed, is the best configuration tested."** Which is a stronger form
of your own instruction that his model is not being replaced.

## 2. The sweep, and why it cannot be rigged

At containment share **0.0 this architecture is Al-Qudah's arm**; at **1.0 it is Irfan's
arm**. The sweep interpolates between two *named positions* — so any advantage we claim has
to appear as an interior point beating both of its own endpoints.

```
containment    shortfall   secondary
      0.00         36.1         121     ← Al-Qudah arm
      0.10         46.2         119
      0.25         71.0         119
      0.40         77.0         119
      0.60        107.8         109
      0.80        138.7         108
      1.00        167.6         101     ← Irfan arm
```

**V2 failed.** Across the entire range cascades fall only **121 → 101 (16.5%)** while
shortfall rises **36.1 → 167.6 (4.6×)**. No interior share delivers a 15% cascade reduction
inside a 25% shortfall budget. **The mix adds nothing over picking an endpoint.**

That is your improvement ③ taken to its conclusion: participation is not just *confined* to
contagion control — on this substrate, blending it in at all is a bad trade unless cascade
is the thing you are buying.

## 3. The seed-robustness check this programme had never run

Every result in this repository up to now rested on **one seed**. That is not good enough
for peer review, so v2 swept five.

```
seed        shortfall @ 0.25
20260801           71.0
20260802           63.8
20260803           69.9
20260804           34.7
20260805           61.9
                   mean 60.2   sd 13.2   CV 0.220
```

> **Single-seed results in this repository carry roughly ±22% variation.** Every
> single-seed finding elsewhere here should be read with that band attached.

**And V5's pass is partly vacuous, disclosed rather than banked.** The gate had two
criteria. The CV criterion carries information and passed. The modal-share criterion —
"the best interior share is stable across seeds" — is satisfied only because *no seed has
one*, so "None appears 5/5" tests nothing. A test that cannot fail is not evidence, including
when it is mine and it passed.

**This is why V4's failure was re-run across all five seeds** before being reported: a
single-seed comparison on a quantity with 22% noise is not a finding. It lost on all five.

---

## 4. The configuration to deploy

Not the one v2 proposed. The one the measurement supports:

| Layer | Setting | Why |
|---|---|---|
| **Substrate** | 100% full reserve, `ΔU = 0` | identical contracts cost **1.99×** more on a fractional substrate |
| **Payment timing** | **continuous distribution** — pay as you collect | **50.9×** effect, the largest in the programme |
| **Routine claims** | Al-Qudah asset-backed / diminishing co-ownership, **unmixed** | best configuration tested (36.1) |
| **Participation** | **only** where cascade is the actual exposure | buys ~16% cascade at 4.6× shortfall — a bad trade unless cascade is what you want |
| **Register routing** | **none** — fixed policy, no scoring model | routing lost to 18 of 20 coin flips |

**The two-register split is a second-order refinement.** Continuous distribution is the
model. That is your improvement ② and it survived every attempt to knock it down.

---

## 5. Sam's print shop gets his loan

> **Illustration, not measurement.** Numbers invented to show the mechanism. Evidence is
> §2–3, from 10,000 committed real events.

Sam needs **£20,000** for an industrial printer. Shop takes ~**£8,000/month**.

**Step 1 — the money exists.** The £20,000 comes from pooled savings that already exist.
Nothing is created at a keyboard. *(Full reserve — the substrate that measured 1.99× better
with contracts held fixed.)*

**Step 2 — the bank buys the printer with him.** Not a loan at interest: joint purchase.
Sam puts in **£6,000 (30%)**, the bank **£14,000 (70%)**, and the bank holds real title to
its share. *(Al-Qudah's diminishing co-ownership — the best-scoring configuration tested.)*

**Step 3 — he pays as he collects.** Monday he invoices £3,000. Wednesday the customer
pays — and that hour, **£1,500 goes to the bank**, buying out a slice of its ownership;
£1,500 stays with Sam. **No monthly due date exists.** *(Continuous distribution — 50.9×.)*

**Step 4 — the bad quarter.** His biggest client leaves; revenue drops to £2,000/month. He
passes through **£1,000**. That is the whole obligation. **He is not in default. He was
never late.** Under a fixed monthly schedule he would have missed a payment and stopped
paying his paper supplier to cover the bank.

**Step 5 — the flood.** £6,000 of stock destroyed. The bank owns 70% of the asset, so it
**carries its 70% of the asset loss** — that is what holding title means. Sam keeps his
performing share, keeps trading, keeps paying his supplier.

**Step 6 — when participation gets used.** Sam's shop is not a systemic node. If instead he
were the sole packaging supplier to eleven other businesses, *then* a participation tranche
would be worth its cost — you would be **buying cascade protection and paying ~4.6× in
recovery for it, knowingly.** For an ordinary print shop, you don't.

---

## 6. What each sector gets

### Conventional banks

Nothing here needs a cultural frame. **Pay as you collect** — the largest measured effect,
and mostly a change to collection timing rather than new infrastructure. **Don't lend what
you haven't got.** **Use participation only where contagion is the real exposure**, priced
knowing it costs recovery. **Don't buy a risk-routing model.**

### Islamic banks

- **Al-Qudah's contracts are vindicated on measurement** — best configuration tested, at
  36.1. Not "halal enough": **best**, on settlement outcomes, with no theological premise
  required for the claim.
- **The substrate is the whole problem, and now it has a number.** Identical contracts cost
  **1.99×** more fractional than full-reserve. The label was never the issue.
- **Risk-sharing does not lower your losses — it raises them 4.6×.** Sold as prudential
  infrastructure it is defensible. Sold as a superior return profile it is not.
- **Al-Qudah's model is not replaced.** At share 0.0 the architecture *is* his model, and
  the test says that is where to sit. What v2 adds is the payment-timing rule and the
  audit register — not a replacement contract set.

---

## 7. Where the stack sits, and how LISM is extended

### The Novora stack, in this network

- **Echo** — **the claim register itself.** Append-only, hash-chained, Merkle-provable. It
  is what makes "which register was this claim in, and was it altered?" *checkable*. The
  oxymoron charge lands because labels are unverifiable; this is the answer to it.
- **HELM / IHCEI / NERE** — the kernel runs **on-device**, no network call, with a test
  proving it. A participant can be audited **without their book leaving the premises**.
- **EI-LLM** — receiver-side attestation: generates nothing, censors nothing, answers
  verifiable questions. The counterparty-verification seat.
- **Page Code** — default-deny permissions over any agent that can change the settlement
  engine, every change hash-chained into Echo.
- **AlphaAgency** — `F_out = F_eval`: a deterministic evaluator decides, so a hallucinating
  generator cannot corrupt a verified result. That is why these numbers survive.
- **PAGES** — confidence-and-abstain. Honest status: **untestable** on N=992 by construction
  of that cohort — untestable-here, not refuted.

### How LISM is extended by this work

LISM was `E = U · D_enc · D_dec` — a **two-hop channel**: acquisition fidelity times
distribution fidelity, coupling linearly. Two extensions came out of this programme, and
both were forced by measurement rather than chosen:

1. **`D_dec` has a timing dimension, and it dominates.** LISM treated distribution fidelity
   as *how well* value propagates. The measurement says **when** it propagates is worth
   ~50× more than any structural choice about the channel. Distribution is not just a
   coefficient — **it is a rate**, and the rate is where the effect lives.
2. **The two hops have different failure modes, and they are not interchangeable.**
   Recovery protects the *holder*; containment protects the *network*. LISM's product form
   already implied that either hop at zero collapses the result; what is new is that
   **optimising one actively costs the other** — 16% cascade for 4.6× shortfall — so the
   product cannot be maximised by improving both independently.

**Al-Qudah's model extends LISM in a third way**, and this is the part that surprised us:
his amortising co-ownership makes `D_dec` **structural rather than discretionary** — value
returns continuously because the contract is *built* that way, not because a policy says
so. That is a stronger implementation of the same insight than ours, and the measurement
says so at 36.1 against our 71.0.

---

## 8. Layer discipline, stated once more

The Organic Qur'anic Methodology is **governance philosophy, and Layer 3 — philosophically
prior**. It supplies the abstract logic used to *generate* theories and engineer systems.
It supplied the stock-versus-flow reading that turned out to point at the largest effect in
the system before we measured it.

**It did not supply the evidence, and it cannot.** Everything in §2–3 came from a settlement
engine. Everything in §5 is an illustration. Nothing here adjudicates a jurisprudential
question — a better settlement outcome is not a ruling, and this document does not offer one.

**And the boundary held in the direction that costs us something:** the methodology
generated v2's design, and the telemetry rejected two of its three claims. That is the
division of labour working.

---

## Reproduce

```bash
python3 tworegister-v2/v2.py
python3 -m pytest -q tworegister-v2/test_v2.py
bash reproduce_all.sh
```

**For a reviewer:** the spec hash is computed over the canonical JSON of the pre-registration
and verified by the runner before any measurement; the event source is hash-pinned against a
committed manifest and the run aborts if it changed; all gates, thresholds and seeds are in
the spec and none was altered after the run. Exit 0 means "reproduces including its
failures", never "v2 works".
