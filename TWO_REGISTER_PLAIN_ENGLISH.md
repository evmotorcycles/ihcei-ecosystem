# The Two-Register Settlement Network — explained without the jargon

**Spec** `ed80430a` · locked before implementation · **0/5** · full technical write-up in
`TWO_REGISTER_NETWORK.md`

This document is for someone who is not a quantitative analyst. It explains what the model
does, walks through an ordinary business transaction, and says honestly what it offers a
bank — including what it does *not* offer.

---

## Part 1 — What the headline actually means

Here is the technical summary, then the same thing in English.

> *Prereg ed80430a · 0/5. Two registers. One of them stopped being routable. Routing
> refuted, signal AUC 0.4447, 5th falsified selection rule, predicted to fail in advance.*

**In English:**

We built a lending system with two settings, and we thought we had a clever way to decide
which setting each borrower should get. **We tested the clever part against flipping a
coin. The coin won 18 times out of 20.** So we deleted the clever part and shipped the
system without it.

The score `0/5` means every one of the five things we said we'd check came back negative.
We wrote down *in advance* that we expected the main one to fail, and it did.

Some other phrases decoded:

| Jargon | English |
|---|---|
| **Pre-registered** | We wrote down what would count as success **before** running the test, and locked the file with a tamper-proof fingerprint, so we couldn't quietly move the goalposts afterwards. |
| **AUC 0.4447** | A score for "how well does this predictor work?" 0.5 means useless — a coin flip. **Below 0.5 means it points the wrong way.** Ours was below. |
| **Selection rule** | Any rule of the form "pick the good ones using this signal." We've now tried five. All five failed. |
| **Claimant value shortfall** | Money someone was promised, minus money they actually received. |
| **Secondary failure / cascade** | Business B fails *because* business A failed first. The domino effect. |
| **Full reserve (ΔU = 0)** | The lender lends money that actually exists. Nothing is created out of nothing. |
| **0/5 is the deliverable** | We're publishing the failure. That's the point — see Part 5. |

---

## Part 2 — The model in one picture

Every loan sits in one of **two registers**. A register is just a list — which list your
loan is on decides what happens when things go wrong.

| | **Recovery register** | **Containment register** |
|---|---|---|
| What it is | A normal fixed claim | A share-in-the-outcome claim |
| Bad month | You still owe it | It gets written down |
| Are you "in default"? | Eventually yes | **No — there is no default event** |
| Good year later | The lender gets paid | **The written-off part is gone forever** |
| Protects | **the lender** | **everyone downstream of you** |

**Neither one is better. They protect different people.** That is the whole model.

And running underneath both, the piece that turned out to matter most:

> **Continuous distribution.** You don't pay on the 1st of the month. You pay a share of
> every payment *as it arrives*.

---

## Part 3 — An ordinary transaction, step by step

> ⚠️ **This example is an illustration, not a measurement.** The numbers are made up to
> show how the mechanism works. The measured evidence is in Part 4 and comes from 10,000
> real recorded transactions. We keep these strictly separate.

**Sam runs a small print shop.** He needs **£20,000** for a new machine. His shop normally
takes about **£8,000 a month**.

### Step 1 — Where the money comes from

Under a conventional loan, the bank creates most of that £20,000 as a new deposit when it
writes the loan. Under this model it comes from savers' money that already exists —
**full reserve**. Nothing is invented.

*Why it matters:* when we tested creating money against not creating it, creating it made
settlement **worse, every time** — the more leverage, the more failed payments. That's a
measurement, not a principle.

### Step 2 — A normal week

| Day | What happens |
|---|---|
| Monday | Sam invoices a customer **£3,000** |
| Wednesday | The customer pays |
| Wednesday, same hour | **£1,500 goes straight to the funder. £1,500 stays with Sam.** |

There is no monthly due date. There is no "did the direct debit clear?" **The payment is a
share of what actually came in.**

### Step 3 — A bad quarter

Sam's biggest client leaves. Revenue drops from £8,000 to **£2,000** a month.

- **Old way:** Sam owes his fixed £X on the 1st regardless. He can't pay. He is now in
  **default** — his credit is damaged, penalties start, and he stops paying his paper
  supplier and his part-time staff to cover the bank.
- **This model:** £2,000 comes in, so **£1,000 goes to the funder**. That's it. Sam has
  paid exactly what he was supposed to pay. **He is not in default. He was never late.**

This is the single most important thing in the system, and it is almost boring: *most small
businesses don't fail because they're unprofitable. They fail because a fixed payment date
met a variable income.* Continuous distribution deletes that mismatch.

### Step 4 — A real loss

Now something worse. A flood destroys stock; **£6,000 is genuinely gone** and is never
coming back.

**If Sam's loan is in the RECOVERY register:**
- Sam still owes the £6,000. It stays on the books.
- Two years later he's trading well again, and it gets paid off.
- **The funder gets almost everything back.**
- But Sam carried that debt through his whole recovery — and if his supplier was depending
  on him, that supplier felt it too.

**If Sam's loan is in the CONTAINMENT register:**
- The £6,000 is **written down**. Gone.
- Sam is clear immediately. He keeps trading and **keeps paying his paper supplier and his
  staff** — so they don't fail either.
- **The funder never sees that £6,000 again** — not even if Sam has a record year in 2028.
  Writing a claim down *extinguishes* it.

### Step 5 — So who decides which register Sam goes in?

**Not an algorithm.** We built one and tested it. It lost to a coin flip 18 times out of 20,
because our risk signal turned out to point slightly the *wrong* way.

So it's a **policy decision made in advance and applied uniformly** — for example, *"all
trade credit to suppliers in our food-distribution chain goes in containment; all equipment
finance goes in recovery."* Simple, cheap, and it performed better than our clever version.

---

## Part 4 — The evidence

From **10,000 real recorded transactions**, both money in and money out, replayed through
the same settlement engine with only one thing changed at a time.

### What we measured

| Finding | Numbers |
|---|---|
| **Paying as money arrives beats everything else** | Removing it was **30× worse** than removing any other single feature |
| **Lending money that exists beats lending money you create** | 0 failed settlements at full reserve; 3,262 → 3,912 → 4,362 as leverage rose |
| **Write-downs protect the network, not the lender** | Lender loses **~6× more** (94.4 vs 16.1); **18–32% fewer** businesses dragged down |
| **Our risk-routing model was useless** | Beaten by 18 of 20 random assignments |

### Two things we got wrong and are publishing anyway

1. **Our own scoring formula was broken.** We combined two goals with "equal 50/50
   weights," but on this data one term was **90× larger** than the other, so the formula was
   really only measuring one of them. We did **not** rewrite it after the fact. We reported
   the result as scored and flagged that three of the five gates are compromised by it.
2. **We overstated one finding and corrected it.** We first wrote that the smart routing
   lost to *every* random draw. It lost to 18 of 20. Two were worse. The corrected claim is
   the one that stands.

---

## Part 5 — What this offers a bank, honestly

### The parts you can use tomorrow

1. **Pay-as-you-collect on distressed exposures.** This needs no new infrastructure, no
   blockchain, no new legal form. It was the biggest measured effect in the entire
   programme by two orders of magnitude, and it is mostly a change to *collection timing*.
2. **Full reserve in the settlement layer.** Not as ideology — as the configuration that
   produced the fewest failed settlements in testing.
3. **Write-down tranches as a circuit breaker.** Use them where a customer's failure would
   take out three of your other customers. Price them knowing they cost *you* recovery.
4. **A tamper-evident claim register**, so "which register was this loan in?" is provable
   rather than asserted.

### The parts you should not buy

- **A risk-routing model.** Ours failed. Be sceptical of anyone selling one who hasn't
  tested it against random assignment at the same allocation share.
- **Risk-sharing as a way to lose less money.** It isn't. It measurably loses you *more*.

### What we did *not* achieve

Being straight about this, because it is the most commercially relevant fact here:

> **We never beat a conventional central clearing book on routine friction.** A single
> full-reserve central book posted **zero** failed settlements against our decentralised
> mesh's 2,548. We tested whether the mesh repays that cost during a crisis, across
> eighteen different crisis scenarios. **It never did.**

So this is **not** a replacement for a clearing house, and anyone claiming otherwise is not
reading our own numbers. It is a set of **four specific, separately-testable practices**
that improved measurable outcomes, plus one honest warning about the practice everyone
expects to be the star.

---

## Part 6 — Why the sectors should care

### Conventional banks

Nothing here requires any cultural or religious framing. It's network science: pay as you
collect, don't lend what you haven't got, use write-downs surgically where contagion is the
real exposure, and don't buy a scoring model that hasn't been tested against chance.

### Islamic banks

The long-standing charge — from insiders like Harris Irfan — is that the sector wraps
conventional debt in a different label while the underlying mechanics stay identical. Two
things follow from our measurements:

- **The full-reserve requirement is vindicated by measurement, not doctrine.** It was
  simply the best-performing configuration we tested. That is a much stronger argument, and
  it requires no one to share your premises.
- **But risk-sharing does not lower your losses — it raises them.** Measured: 94.4 against
  16.1. A sector adopting participation while expecting better returns will be disappointed
  by arithmetic, not by markets. **Its genuine value is systemic**: it keeps counterparties
  alive. Sold as prudential infrastructure, it is defensible. Sold as a superior return
  profile, it is not.
- **The audit trail is the real differentiator.** The "oxymoron" charge lands because labels
  are unverifiable. A tamper-evident register makes the label *checkable*.

---

## Part 7 — Why we're publishing a failure

A model that only ever produces confirmations hasn't been tested.

We designed this from earlier measurements, wrote down in advance what would prove the new
idea wrong, ran it, watched the new idea fail exactly as predicted, and shipped the system
**smaller** than we'd planned. Nine times in a row now we've declined to write a simulation
whose output would have been decided by its own formula.

What's left is what survived a real attempt to kill it. That is the only kind of finding
worth putting in front of a risk committee.

---

## Reproduce it yourself

```bash
python3 two-register/tworegister.py
python3 -m pytest -q two-register/test_tworegister.py
bash reproduce_all.sh          # 73/73
```

Exit code 0 means *"this reproduces, including its failures"* — never *"the model works."*
