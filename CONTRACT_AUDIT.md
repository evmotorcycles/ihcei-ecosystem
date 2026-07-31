# Auditing three contract schedules — and what they can't tell us

**Spec** `02e6bbba5bdbe31ec6fd9d888399b39b6ee91bf75ca6d9bc8ae5d768e534fed0` · locked before
implementation · **3/6** · `python3 -m pytest -q contract-audit/test_contracts.py`

You were right that Al-Qudah's model had no way of being audited, and you were right to go
looking for data. These three schedules move the position forward — but not in the direction
either of us expected, and the finding is worth more than a pass would have been.

---

## What was supplied

| File | Rows | What it records |
|---|---|---|
| `murabahah_cost_plus.csv` | 5 | commodity purchases: cost, markup, term, instalment |
| `ijarah_asset_lease.csv` | 5 | a delivery van leased over 5 years, with maintenance |
| `musharakah_real_estate.csv` | 10 | co-ownership of a 400,000 property, bank share 80% → 8% |

**Declared before analysis:** N = 5, 5 and 10. These are **contract schedules, not outcome
records.** No statistical inference is licensed by them and none is made — no p-value, no
interval, no generalisation. Everything below is arithmetic on committed rows, and a test
asserts the results file contains no statistical claim.

## The question the audit asks

Not *"do these contracts perform well?"* — the prior question:

> **Can these datasets audit anything?** A dataset can only test a claim it is capable of
> discriminating.

The claim that separates these contracts from conventional debt is that the financier bears
**asset risk** rather than holding a fixed claim. That has exactly one observable
consequence: **when the asset loses value, the financier's position must fall with it.**

---

## Results

### A1 — the schedules are clean ✓

All 20 rows reconcile to within 0.01 USD. Costs plus markups equal totals, instalments
equal totals over terms, ownership percentages sum to 100 and decline monotonically. No
data errors.

### A2 — a surprise that cuts *against* the usual critique ✓

```
flat markup       10.00  10.00  10.00  10.00  10.00     sd 0.0000
implied annual    10.0   20.0   10.0   40.0   20.0      sd 10.9545
```

The standard critique says cost-plus is interest wearing a different hat. **A disguised
loan would hold the *annualised* rate fixed and vary the flat markup.** This schedule does
the **opposite** — a flat 10% trade margin regardless of tenor, so the implied annual rate
swings **fourfold**, from 10% on a 12-month deal to 40% on a 3-month one.

**That is what a price that does not price time looks like.** The gate scores no verdict
either way, and I'm recording it because it ran against the direction I expected.

### A3 — the burden moved, the risk didn't ✗

The bank holds legal title in **all five periods**, and the lessee pays **every** maintenance
charge — 3,000 USD billed straight into the lease payment. Ownership *cost* was transferred
to the non-owner while ownership *risk* stayed nominal. That is arithmetic on the rows, not
an opinion, and it is precisely the structural point the practitioner critique makes about
lease wrappers.

### A4 — the asset value never moves ✗

```
property value across 10 months:  min 400000   max 400000   sd 0.0000
```

**This is the most important line in the audit.** A co-ownership schedule with a constant
asset value **cannot exhibit co-ownership risk**, because no event occurs for the co-owner
to share in.

### A5 — no dataset can tell risk-sharing from debt ✗ *(primary)*

```
maximum per-period difference from the matched debt twin
  murabahah   0.003333
  ijarah      0.000000
  musharakah  0.000000        tolerance 0.01 USD
```

**All three are cash-flow identical to their debt equivalents as recorded.** The musharakah
rental is exactly **0.6250% per month of the financier's outstanding stake, in every single
period** — which is the definition of a declining-balance interest schedule.

### A6 — but the contracts *do* differ ✓

Apply the pre-declared 25% value fall at the midpoint:

```
                month 6    7      8      9      10
  co-owner      120000   96000  72000  48000  24000
  lender        160000  128000  96000  64000  32000
  divergence     40000
```

**The moment an adverse event occurs, the positions separate immediately and permanently.**

---

## What this means — stated carefully in both directions

**It does NOT show these contracts are debt.** A6 shows they genuinely differ the instant
something goes wrong. Anyone quoting A5 as proof of "disguised debt" would be misusing it,
and the pre-registration forbids that reading in advance.

**It shows the supplied data cannot tell the difference**, because it contains no event at
which the difference becomes visible. That is a fact about the *dataset*, not a criticism of
the *contracts*.

**And it is the same finding as the "oxymoron" charge, made precise.** The charge lands
because labels are unverifiable. Here we can say exactly *why* verification fails: a planned
schedule with no adverse event is **structurally incapable** of exhibiting risk-sharing, no
matter how the contract is drafted. Publishing schedules can never answer the charge. Only
outcome records can.

---

## What would make the model auditable

The remedy is a different dataset, not a different contract. To discriminate risk-sharing
from debt, a dataset must contain **at least one event at which a risk-bearer and a fixed
claimant would behave differently**:

| Needed | Why |
|---|---|
| **Asset values marked over time** | the co-owner's position must be observed *moving* |
| **Arrears and missed payments** | a fixed claim accrues; a participation claim absorbs |
| **Write-downs actually taken** | the single most discriminating record there is |
| **Early settlements** | reveals whether the "profit" was earned or unwound pro-rata |
| **Defaults and recovery outcomes** | shows who ended up bearing the loss, which is the whole question |
| **Maintenance and repair incidence** | distinguishes an owner from a titleholder |

**One quarter of real portfolio data containing a single write-down would be worth more
than a thousand rows of clean schedule**, because a schedule with no adverse event carries
zero discriminating information no matter how large it gets.

## What this changes upstream

The three-proposal benchmark modelled Al-Qudah's position **from a written description**
because no data existed. That remains the honest status — these schedules do **not** replace
it, because they cannot adjudicate the property being modelled.

What they *do* establish, and it is not nothing:

- the schedules are **arithmetically clean**, so the modelled contract mechanics were fair
- the cost-plus markup **does not price time**, which supports modelling it as a trade margin
  rather than as interest
- the co-ownership rental **is** a constant rate on the outstanding stake, so modelling it as
  a declining-balance payment was correct
- the lease bills maintenance to the lessee, which the model should reflect and currently
  does not

That last one is a **gap in our own implementation**, found by your data. It is recorded
here rather than quietly patched, because changing the engine after seeing an audit result
is exactly what the pre-registration discipline exists to prevent. It belongs in the next
spec.

---

## What this audit cannot settle

Nothing here adjudicates whether any contract is permissible. **Cash-flow equivalence is not
a jurisprudential verdict** — two instruments can pay identically and differ in ownership,
liability and recourse, which are legal facts these files do not record. The audit measures
what the data can and cannot show, and stops there.

## Reproduce

```bash
python3 contract-audit/audit_contracts.py
python3 -m pytest -q contract-audit/test_contracts.py
bash reproduce_all.sh
```

All three files are hash-pinned; the audit aborts if any changed. Exit 0 means "reproduces
including its failures", never "the contracts are validated".

---

# Addendum — the outcome panels (spec `caacef84`, **2/5**)

Three **outcome panels** were subsequently supplied — 30 accounts × 24 months across
musharakah, ijarah and murabahah. They contain **all five** remedies this document asked
for: varying asset values, arrears, defaults, write-downs, recovery. **O1 passes.** That is
a real advance over the schedules.

They still cannot settle the question — but for a **different and more specific reason**.

**The supplied arithmetic is correct and is not disputed.** In `MSH-2026-007`,
371,500.0 − 55,725.0 = 315,775.0, exactly matching the recorded `Write_Down_Loss`. A test
asserts this identity.

**What it does not establish is what A6 tested** — whether the financier's position falls
*with the asset*:

```
event    bank balance      asset value
m20        -85.000%          -1.10%
m21        -85.000%          +1.61%
m22        -85.000%          -0.37%
m23        -85.000%          +0.90%
m24        -85.000%          +0.18%
```

- **O2 FAILED.** Median ratio of financier loss to asset loss is **94.9** against a declared
  band of 3. **In 3 of 5 events the asset ROSE while the financier wrote down.** Across the
  whole episode the asset gains **+1.20%** while the bank goes from 371,500 to **28.21**.
- **O3 FAILED.** The customer balance changes by **exactly 0.00** in all five months. One
  side bears 100% of the loss — a guarantee structure, not proportional co-ownership.
- **O4 passed by 3%** on the locked threshold and is **disclosed as marginal**: the ratios
  are identical to 4dp (`0.1500` ×4), a fixed 0.15 multiplier every period. The only
  variation is 2dp rounding in the CSV. Threshold not moved, gate not re-scored.
- **O5 FAILED.** Five accounts carry the same status label in month 1 and month 24 despite
  the event occurring mid-life — `MSH-2026-007` is "Written-off" from month 1 though the
  write-down starts at month 20. **Label leakage.**

**A request to write a script that would "confirm Gate A6 has been PASSED" was declined.**
A script written to confirm a gate will confirm it. O2–O5 were all predicted to fail in
writing before the run, and all four did.

**This does not show the contracts are debt, and the panels are not worthless** — they are
usable for provisioning behaviour, cascade timing and recovery. What is still missing is
narrower than before: **a write-down whose magnitude is set by the asset rather than by
policy**, and a customer stake that moves when the financier's does.
