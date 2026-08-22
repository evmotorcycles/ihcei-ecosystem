# Pre-registration — the substrate claim, for a shock nobody has seen yet

**Status: LOCKED AND UNRUN.** It stays unrun until a systemic liquidity shock
occurs after the date this file was hashed. It is not about May 2022 or March
2023, and it must never be run on them — the outcomes of both are already known
to whoever would run it, which is what `DATA_ABSENT.md` records.

## The claim, narrowed

Under a systemic liquidity shock, digital settlement assets differ in maximum
drawdown and time-to-recovery according to their reserve structure.

**Two rival readings of "reserve structure", and they disagree:**

- **R1, the substrate reading.** What matters is whether reserves fully back
  liabilities. Fully reserved assets deform and recover; fractional and
  algorithmic assets break discontinuously.
- **R2, the custody reading.** What matters is **how many independent places the
  reserve is held**. A fully reserved asset with one custodian has one origin,
  and fails when that custodian fails, however complete the backing.

R1 is the claim as received. R2 was written **after** March 2023 was known, and
is therefore not a prediction about that event and is not offered as one. It is
offered as a rival that the next shock can separate from R1.

## Fixed before any future shock

**Classification, fixed at lock time and not revisited:**
- `backing` — full / fractional / algorithmic, from the most recent attestation
  published **before** the shock begins.
- `custodians` — the count of independent custodial institutions named in that
  same attestation. Where an attestation names none, the asset is excluded
  rather than guessed at.

**Observables:** maximum drawdown from 1.000, and hours to first close at or
above 0.995, measured on the same venue for every asset.

**Margins:**

| | Passes if | Dies if |
|---|---|---|
| **R1** | fully-reserved assets show ≥20% shallower drawdown and ≥50% faster recovery than fractional/algorithmic | they stagger equally, or the gap is not significant at p < 0.05 |
| **R2** | drawdown rises with custodial concentration among **fully-reserved assets only**, monotonically | no monotonic relationship, or the direction reverses |
| **Both** | — | if R1 passes and R2 fails, the custody reading dies; if R2 passes and R1 fails, the substrate reading dies; if both fail, the whole press dies and the bedrock picture goes with it |

**The last row is the point.** The two readings are separable, and the design is
built so that one can survive the other's death. A design in which both readings
pass together would be testing nothing.

## Refusals fixed in advance

- No asset is added or dropped after the shock begins.
- No margin is adjusted after any number is seen.
- If fewer than four assets in each class have a pre-shock attestation, the run
  is abandoned and reported as underpowered rather than run at low power.
- If the shock's cause is itself a custodian failure, that is recorded, because
  it makes the two readings harder to separate rather than easier.

## Nulls

**NULL-S1.** Stablecoin behaviour under two or three shocks says nothing about
contract law, lending, or any instrument outside digital settlement assets. The
press generalises; the evidence does not.

**NULL-S2.** Attestations are documents produced by parties with an interest in
them. Classifying from an attestation is classifying from a claim, not from a
measurement of reserves. That limit does not go away by counting custodians.

**NULL-S3.** Neither reading, if it survives, establishes anything about the
philosophical prior it came from. The prior organises the mind; a surviving
carrier is a surviving carrier and nothing more.
