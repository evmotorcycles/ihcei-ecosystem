# A ledger cannot contain its own omissions

**Result: the two-leg fidelity model does not apply to a keel ledger. Reported
as a null rather than worked around.**

## What was tried

`keel/run.plumb` asks whether a run was *governed* or merely *logged*, using the
same shape used everywhere else in this project:

```
E = U × D_in × D_out
```

- `U` — how much happened (actions in the ledger)
- `D_in` — did it all come through the kernel? (`sealed / attempted`)
- `D_out` — can a person disagree with the decisions? (`reasoned / actions`)

A product, so that a busy run with either leg at zero scores zero. Both legs are
required to be independent, or the program halts rather than reporting one
number twice and calling it corroboration.

## What happened

Over a 28-run cohort produced by the real kernel:

| leg | min | max | variance |
|---|---|---|---|
| `sealed / attempted` | 1.000 | 1.000 | **0.00000** |
| `named / attempted` | 0.538 | 1.000 | 0.01062 |
| `checkable / actions` | 0.538 | 1.000 | 0.01062 |

**The inbound leg is a constant.** Every entry that reaches the ledger is
sealed, so `sealed/attempted` is 1.000 by construction. It is not that the
kernel scores well on it — the quantity carries no information at all.

Substituting a leg that does vary (`named/attempted`) fails differently:

```
correlation r = 1.000     VIF = 1.5 × 10¹⁵     (the gate is VIF < 5.0)
```

An action that arrives named is exactly the action that gets a rule. The two
legs are one measurement wearing two names, and Plumb halts:

```
the two legs are not independent (VIF infinite) — a program whose encode and
decode carry the same information is rejected
```

## Why this is the right answer and not a bug

A ledger is a record of what came through. **It cannot record what did not.**
Asking a keel ledger whether everything came through the kernel is asking a
record to testify about its own gaps, and there is no arrangement of its columns
that answers it. The information is not there to be extracted.

This is the same limit the structural check reports from a different direction —
mandatory routing FAILS, nothing forces a program to come through the gate — now
measured a second time, independently, and reaching the same place.

## What was NOT done

The tempting moves were all available and all rejected:

- **Drop the `independent` clause.** The program would print a confident number.
  The number would be one measurement reported twice.
- **Lower the floor until something passes.** Retuning a gate after seeing the
  result is the failure this project exists to catch.
- **Pick a third pair of columns and keep going until VIF < 5.** That is fishing.
  The pre-registered pair is the pair.

`run.plumb` is kept exactly as first written, halt and all.

## What still works

The **structural** obligations in `keel/audit.py` are unaffected, and they
discriminate — each is paired with a tamper test that makes it fail:

| obligation | caught by |
|---|---|
| every decision recorded | an unnamed outcome |
| chain intact | editing entry 3; deleting entry 5 |
| admissions name their rule | blanking one rule |
| refusals give a reason | blanking one reason |
| escalation follows the rule | downgrading a STOP to LEDGER |
| counts carry their handles | emptying one `missing` list |

Six checks that hold on a clean run and fail on a tampered one. That is a real
audit. What it is not, and now cannot claim to be, is evidence that nothing
bypassed the kernel.
