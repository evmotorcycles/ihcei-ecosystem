# Pre-registration — Packs, and the friction claim made arithmetic

Written and hashed **before** `packs.js`, `packlib.js` or `test_packs.py` were
run once.

---

## The problem being solved

A person with a bill in their hand should not have to name six parts and draw
five links before the software tells them anything. That is the blank-canvas
defect, and it is fatal: the mask asks for one tap, and a tired person at the end
of a long day will take the one tap every time.

So the structure arrives already built. A pack is a shape somebody else worked
out, with the numbers left empty. The person types the numbers off their own
paper and gets two answers.

---

## Two answers, never one

This is the part that must not be got wrong, and it is the same firewall the
rest of this stack already runs on.

**Arithmetic.** Does the printed total follow from the numbers you typed?
Recomputed from scratch, exactly, and the result is either "it matches" or a
named difference. Deterministic, no model, no judgement.

**Structure.** What does the answer rest on, and is there a second way to any of
it? Foster arithmetic, the same engine as everywhere else.

A single green light fusing the two would be the most saleable thing a pack
could produce and the least honest. A bill can be arithmetically perfect and
rest entirely on one meter reading nobody checked. A bill can have a difference
of zero and a tariff nobody agreed to. `difference == 0` means **the printed
total follows from what you typed**, and it means nothing else.

---

## Why the structure reading here is about single points, not redundancy

Every input to an arithmetic identity is **required**. Units used needs both
meter readings; the total needs the rate *and* the fee. That is a conjunction.

FATHOM's sources are **disjunctive** — more sources always means less rests on
each — which is exactly the limit already recorded in the Shapes library as
`atomic-install-list`, where a twelve-asset conjunction drawn as a star
understates by 0.917. Running source-dropping over a bill would report the two
meter readings at 0.0625 each, which is not merely unhelpful, it is backwards.

So packs report **SPAR** — which links are sole routes and which parts break the
graph when removed — and deliberately do **not** run the source-dropping
readout. The reason is printed on the page rather than left in a file.

---

## The seed packs

Six, all jurisdiction-neutral and currency-neutral. Numbers only, no symbols.

1. **A metered bill** — reading now, reading last time, price per unit, fixed
   charge, the printed total, and optionally what was paid.
2. **A payslip** — gross, tax, pension, other deductions, the printed net.
3. **An invoice with tax** — subtotal, tax percent, the printed total.
4. **A deposit returned** — deposit, up to three deductions, the printed return.
5. **Splitting a bill** — total, number of people.
6. **Paying in instalments** — cash price, deposit, instalment, how many.

---

## Predictions

The metered-bill figures are the worked case that prompted this: reading now 70,
reading last time 58, price per unit 5032, fixed charge 1700, printed total
62084, paid 65000.

| # | Prediction | Value |
|---|---|---|
| K1 | Metered bill: units, cost of units, what it should be, difference | 12, 60384, 62084, 0 |
| K2 | With 65000 paid: carried to next time | 2916 |
| K3 | With the printed total changed to 63000: difference, and wording that names it without asserting fault | 916 |
| K4 | Metered bill structure: parts, links, every bearing, total bearing | 6, 5, 1.000 each, 5.000 = 6 − 1 |
| K5 | Metered bill single points | exactly `Units used` and `What the bill should be` |
| K6 | Leaving the optional "what you paid" empty: the carried-forward row is **absent, not zero** | absent |
| K7 | Dividing by zero | refused with a reason, never NaN or Infinity |
| K8 | An expression naming a key that does not exist | refused |
| K9 | A derivation that depends on itself | refused |
| K10 | **The friction claim.** For every pack, the count of numbers a person types is strictly less than the parts plus links they would otherwise place by hand | asks < parts + links, all six |
| K11 | A pack that declares no assumptions is refused | refused |
| K12 | Invoice: subtotal 1200 at 18 percent | tax 216, total 1416 |
| K13 | Instalments: cash 900, deposit 100, instalment 80, twelve of them | paid 1060, extra 160 |
| K14 | Payslip: gross 4200, tax 630, pension 210, other 0, printed net 3360 | deductions 840, net 3360, difference 0 |
| K15 | Deposit: 1500 held, deductions 200, 75 and 0, printed return 1225 | taken 275, should return 1225, difference 0 |

K10 is the one that could kill the whole idea: if a pack is not less work than
building the thing by hand, it has no reason to exist. K6 is the one that could
make the tool dangerous rather than merely useless — a missing input that
silently becomes zero is software inventing a number, which is precisely the
failure a mask commits.

---

## Nulls, registered in advance

**NULL-K1 — the honest limit of the friction claim.** Counting the numbers a
person types is not usability. It does not measure whether somebody tired, at
the end of a long day, with a child asking for something, actually finds this
easy. That would need people, and there are none here. "Fewer things to type" is
a proxy and is reported as one.

**NULL-K2 — no pack carries any real provider's rates.** Every seed pack is a
general shape. Shipping a named company's tariff that I cannot verify would be
worse than a blank canvas: a confidently wrong "what it should be" is exactly
the failure this whole paradigm is arranged against. Provider-specific packs are
a job for the commons, from people who hold the actual paper, with provenance
attached.

**NULL-K3 — a flat rate will not match a stepped tariff.** Many real utilities
charge in bands. The metered-bill pack assumes one price for every unit and says
so in its own assumptions. Against a banded tariff the difference will be
non-zero, and that is information about the shape of the tariff rather than an
accusation against anybody.

**NULL-K4 — what a difference of zero does not mean.** It does not mean the rate
is fair, the reading is right, the charge is lawful, or that the money is owed.
It means the printed total follows from the numbers you typed. Anything more is
the reader's own work, and the pack says where to go and do it.

---

## What would falsify this

1. **K10 fails on any pack.** That pack is more work than doing it by hand and
   should be deleted rather than defended.
2. **A missing input becomes a number.** The tool invented a value; that is the
   mask failure committed by the tool built to name it.
3. **A pack ships a specific provider's rates.** Then the software is asserting
   something about the world it cannot check, inside the one place a person is
   least able to notice.
